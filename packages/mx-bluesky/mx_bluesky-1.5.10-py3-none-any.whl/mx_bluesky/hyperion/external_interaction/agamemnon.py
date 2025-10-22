import dataclasses
import json
import os
import re
import traceback
from collections.abc import Sequence
from enum import StrEnum
from os import path
from typing import Any, TypeVar

import requests
from deepdiff.diff import DeepDiff
from dodal.utils import get_beamline_name
from jsonschema import ValidationError
from pydantic_extra_types.semantic_version import SemanticVersion

from mx_bluesky.common.parameters.components import (
    PARAMETER_VERSION,
    MxBlueskyParameters,
    WithVisit,
)
from mx_bluesky.common.parameters.constants import (
    GridscanParamConstants,
)
from mx_bluesky.common.utils.log import LOGGER
from mx_bluesky.common.utils.utils import convert_angstrom_to_eV
from mx_bluesky.hyperion.parameters.components import Wait
from mx_bluesky.hyperion.parameters.load_centre_collect import LoadCentreCollect

T = TypeVar("T", bound=WithVisit)
MULTIPIN_PREFIX = "multipin"
MULTIPIN_FORMAT_DESC = "Expected multipin format is multipin_{number_of_wells}x{well_size}+{distance_between_tip_and_first_well}"
MULTIPIN_REGEX = rf"^{MULTIPIN_PREFIX}_(\d+)x(\d+(?:\.\d+)?)\+(\d+(?:\.\d+)?)$"
MX_GENERAL_ROOT_REGEX = r"^/dls/(?P<beamline>[^/]+)/data/[^/]*/(?P<visit>[^/]+)(?:/|$)"


class _InstructionType(StrEnum):
    WAIT = "wait"
    COLLECT = "collect"


@dataclasses.dataclass
class _PinType:
    expected_number_of_crystals: int
    single_well_width_um: float
    tip_to_first_well_um: float = 0

    @property
    def full_width(self) -> float:
        """This is the "width" of the area where there may be samples.

        From a pin perspective this is along the length of the pin but we use width here as
        we mount the sample at 90 deg to the optical camera.

        We calculate the full width by adding all the gaps between wells then assuming
        there is a buffer of {tip_to_first_well_um} either side too. In reality the
        calculation does not need to be very exact as long as we get a width that's good
        enough to use for optical centring and XRC grid size.
        """
        return (self.expected_number_of_crystals - 1) * self.single_well_width_um + (
            2 * self.tip_to_first_well_um
        )


class _SinglePin(_PinType):
    def __init__(self):
        super().__init__(1, GridscanParamConstants.WIDTH_UM)

    @property
    def full_width(self) -> float:
        return self.single_well_width_um


def create_parameters_from_agamemnon() -> Sequence[MxBlueskyParameters]:
    """Fetch the next instruction from agamemnon and convert it into one or more
    mx-bluesky instructions.
    Returns:
        The generated sequence of mx-bluesky parameters, or empty list if
        no instructions."""
    beamline_name = get_beamline_name("i03")
    agamemnon_instruction = _get_next_instruction(beamline_name)
    if agamemnon_instruction:
        match _instruction_and_data(agamemnon_instruction):
            case (_InstructionType.COLLECT, data):
                return _populate_parameters_from_agamemnon(data)
            case (_InstructionType.WAIT, data):
                return [
                    Wait.model_validate(
                        {
                            "duration_s": data,
                            "parameter_model_version": _get_param_version(),
                        }
                    )
                ]

    return []


def compare_params(load_centre_collect_params: LoadCentreCollect):
    """Compare the supplied parameters (as supplied from GDA) with those directly
    created from agamemnon. Any differences are logged.
    Args:
        load_centre_collect_params: The parameters from GDA to compare."""
    try:
        lcc_requests = create_parameters_from_agamemnon()
        # Log differences against GDA populated parameters
        if not lcc_requests:
            LOGGER.info("Agamemnon returned no instructions")
        else:
            differences = DeepDiff(
                lcc_requests[0], load_centre_collect_params, math_epsilon=1e-5
            )
            if differences:
                LOGGER.info(
                    f"Different parameters found when directly reading from Hyperion: {differences}"
                )
    except (ValueError, KeyError):
        LOGGER.warning(f"Failed to compare parameters: {traceback.format_exc()}")
    except Exception:
        LOGGER.warning(
            f"Unexpected error occurred. Failed to compare parameters: {traceback.format_exc()}"
        )


def update_params_from_agamemnon(parameters: T) -> T:
    """Update the supplied parameters with additional information from agamemnon.
    This is currently necessary for multipin processing and called when Hyperion is invoked
    from GDA.

    Args:
        parameters: The LoadCentreCollectParameters that will be updated with additional info,
        such as multipin dimensions, number of crystals.
    """
    try:
        beamline_name = get_beamline_name("i03")
        agamemnon_params = _get_next_instruction(beamline_name)
        instruction, collect_params = _instruction_and_data(agamemnon_params)
        assert instruction == _InstructionType.COLLECT, (
            "Unable to augment GDA parameters from agamemnon, agamemnon reports 'wait'"
        )
        pin_type = _get_pin_type_from_agamemnon_collect_parameters(collect_params)
        if isinstance(parameters, LoadCentreCollect):
            parameters.robot_load_then_centre.tip_offset_um = pin_type.full_width / 2
            parameters.robot_load_then_centre.grid_width_um = pin_type.full_width
            parameters.select_centres.n = pin_type.expected_number_of_crystals
            if pin_type != _SinglePin():
                # Rotation snapshots will be generated from the gridscan snapshots,
                # no need to specify snapshot omega.
                parameters.multi_rotation_scan.snapshot_omegas_deg = []
                parameters.multi_rotation_scan.use_grid_snapshots = True
    except (ValueError, ValidationError) as e:
        LOGGER.warning(f"Failed to update parameters: {e}")
    except Exception as e:
        LOGGER.warning(f"Unexpected error occurred. Failed to update parameters: {e}")

    return parameters


def _instruction_and_data(agamemnon_instruction: dict) -> tuple[str, Any]:
    instruction, data = next(iter(agamemnon_instruction.items()))
    if instruction not in _InstructionType.__members__.values():
        raise KeyError(
            f"Unexpected instruction from agamemnon: {agamemnon_instruction}"
        )
    return instruction, data


def _get_parameters_from_url(url: str) -> dict:
    response = requests.get(url, headers={"Accept": "application/json"})
    response.raise_for_status()
    return json.loads(response.content)


def _get_pin_type_from_agamemnon_collect_parameters(
    collect_parameters: dict,
) -> _PinType:
    loop_type_name: str | None = collect_parameters["sample"]["loopType"]
    if loop_type_name:
        regex_search = re.search(MULTIPIN_REGEX, loop_type_name)
        if regex_search:
            wells, well_size, tip_to_first_well = regex_search.groups()
            return _PinType(int(wells), float(well_size), float(tip_to_first_well))
        else:
            loop_type_message = (
                f"Agamemnon loop type of {loop_type_name} not recognised"
            )
            if loop_type_name.startswith(MULTIPIN_PREFIX):
                raise ValueError(f"{loop_type_message}. {MULTIPIN_FORMAT_DESC}")
            LOGGER.warning(f"{loop_type_message}, assuming single pin")
    return _SinglePin()


def _get_next_instruction(beamline: str) -> dict:
    return _get_parameters_from_url(get_agamemnon_url() + f"getnextcollect/{beamline}")


def get_agamemnon_url() -> str:
    return os.environ.get("AGAMEMNON_URL", "http://agamemnon.diamond.ac.uk/")


def _get_withvisit_parameters_from_agamemnon(parameters: dict) -> tuple:
    try:
        prefix = parameters["prefix"]
        collection = parameters["collection"]
        # Assuming distance is identical for multiple collections. Remove after https://github.com/DiamondLightSource/mx-bluesky/issues/773
        detector_distance = collection[0]["distance"]
    except KeyError as e:
        raise KeyError("Unexpected json from agamemnon") from e

    match = re.match(MX_GENERAL_ROOT_REGEX, prefix) if prefix else None

    if match:
        return (match.group("visit"), detector_distance)

    raise ValueError(
        f"Agamemnon prefix '{prefix}' does not match MX-General root structure"
    )


def _get_withenergy_parameters_from_agamemnon(parameters: dict) -> dict[str, Any]:
    try:
        first_collection: dict = parameters["collection"][0]
        wavelength = first_collection.get("wavelength")
        assert isinstance(wavelength, float)
        demand_energy_ev = convert_angstrom_to_eV(wavelength)
        return {"demand_energy_ev": demand_energy_ev}
    except (KeyError, IndexError, AttributeError, TypeError):
        return {"demand_energy_ev": None}


def _get_param_version() -> SemanticVersion:
    return SemanticVersion.validate_from_str(str(PARAMETER_VERSION))


def _populate_parameters_from_agamemnon(
    agamemnon_params,
) -> Sequence[LoadCentreCollect]:
    if not agamemnon_params:
        # Empty dict means no instructions
        return []

    visit, detector_distance = _get_withvisit_parameters_from_agamemnon(
        agamemnon_params
    )
    with_energy_params = _get_withenergy_parameters_from_agamemnon(agamemnon_params)
    pin_type = _get_pin_type_from_agamemnon_collect_parameters(agamemnon_params)
    collections = agamemnon_params["collection"]
    visit_directory, file_name = path.split(agamemnon_params["prefix"])

    return [
        LoadCentreCollect.model_validate(
            {
                "parameter_model_version": _get_param_version(),
                "visit": visit,
                "detector_distance_mm": detector_distance,
                "sample_id": agamemnon_params["sample"]["id"],
                "sample_puck": agamemnon_params["sample"]["container"],
                "sample_pin": agamemnon_params["sample"]["position"],
                "select_centres": {
                    "name": "TopNByMaxCount",
                    "n": pin_type.expected_number_of_crystals,
                },
                "robot_load_then_centre": {
                    "storage_directory": str(visit_directory) + "/xraycentring",
                    "file_name": file_name,
                    "tip_offset_um": pin_type.full_width / 2,
                    "grid_width_um": pin_type.full_width,
                    "omega_start_deg": 0.0,
                    "chi_start_deg": collection["chi"],
                    "transmission_frac": 1.0,
                    **with_energy_params,
                },
                "multi_rotation_scan": {
                    "comment": collection["comment"],
                    "storage_directory": str(visit_directory),
                    "exposure_time_s": collection["exposure_time"],
                    "file_name": file_name,
                    "transmission_frac": collection["transmission"],
                    "rotation_increment_deg": collection["omega_increment"],
                    "ispyb_experiment_type": collection["experiment_type"],
                    "snapshot_omegas_deg": [0.0, 90.0, 180.0, 270.0],
                    "rotation_scans": [
                        {
                            "scan_width_deg": (
                                collection["number_of_images"]
                                * collection["omega_increment"]
                            ),
                            "omega_start_deg": collection["omega_start"],
                            "phi_start_deg": collection["phi_start"],
                            "chi_start_deg": collection["chi"],
                            "rotation_direction": "Positive",
                        }
                    ],
                    **with_energy_params,
                },
            }
        )
        for collection in collections
    ]
