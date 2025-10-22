import dataclasses
from collections.abc import Sequence
from typing import Any
from unittest.mock import AsyncMock, MagicMock, call, patch

import numpy as np
import pytest
from bluesky.protocols import Location
from bluesky.run_engine import RunEngine
from bluesky.simulators import RunEngineSimulator, assert_message_and_return_remaining
from bluesky.utils import Msg
from dodal.devices.baton import Baton
from dodal.devices.mx_phase1.beamstop import BeamstopPositions
from dodal.devices.oav.oav_parameters import OAVParameters
from dodal.devices.oav.pin_image_recognition import PinTipDetection
from dodal.devices.synchrotron import SynchrotronMode
from dodal.devices.zebra.zebra import RotationDirection
from ophyd.sim import NullStatus
from ophyd_async.testing import set_mock_value
from pydantic import ValidationError

from mx_bluesky.common.parameters.components import (
    TopNByMaxCountForEachSampleSelection,
)
from mx_bluesky.common.utils.exceptions import (
    CrystalNotFoundException,
    WarningException,
)
from mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan import (
    LoadCentreCollectComposite,
    load_centre_collect_full,
)
from mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan import (
    RobotLoadThenCentreComposite,
)
from mx_bluesky.hyperion.experiment_plans.rotation_scan_plan import (
    RotationScanComposite,
)
from mx_bluesky.hyperion.parameters.constants import CONST
from mx_bluesky.hyperion.parameters.load_centre_collect import LoadCentreCollect
from mx_bluesky.hyperion.parameters.robot_load import RobotLoadAndEnergyChange
from mx_bluesky.hyperion.parameters.rotation import (
    RotationScan,
    RotationScanPerSweep,
)

from ....conftest import pin_tip_edge_data, raw_params_from_file
from .conftest import (
    FLYSCAN_RESULT_HIGH,
    FLYSCAN_RESULT_HIGH_NO_SAMPLE_ID,
    FLYSCAN_RESULT_LOW,
    FLYSCAN_RESULT_MED,
    sim_fire_event_on_open_run,
)

GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION = "tests/test_data/parameter_json_files/good_test_load_centre_collect_params_multi_rotation.json"

POS_HIGH = {
    "x_start_um": 100,
    "y_start_um": 200,
    "z_start_um": 300,
}
POS_MED = {
    "x_start_um": 400,
    "y_start_um": 500,
    "z_start_um": 600,
}

(
    FLYSCAN_RESULT_POS_1,
    FLYSCAN_RESULT_POS_2,
    FLYSCAN_RESULT_POS_3,
    FLYSCAN_RESULT_POS_4,
    FLYSCAN_RESULT_POS_5,
) = [
    dataclasses.replace(
        FLYSCAN_RESULT_MED, centre_of_mass_mm=np.array(coords), sample_id=sample_id
    )
    for (coords, sample_id) in [
        ([0.01, 0.02, 0.03], 1),
        ([0.02, 0.02, 0.03], 2),
        ([0.03, 0.02, 0.03], 3),
        ([0.04, 0.02, 0.03], 4),
        ([0.05, 0.02, 0.03], 5),
    ]
]


@pytest.fixture
def composite(
    robot_load_composite,
    fake_create_rotation_devices,
    pin_tip_detection_with_found_pin,
    sim_run_engine: RunEngineSimulator,
    baton: Baton,
) -> LoadCentreCollectComposite:
    rlaec_args = {
        field.name: getattr(robot_load_composite, field.name)
        for field in dataclasses.fields(robot_load_composite)
    }
    rotation_args = {
        field.name: getattr(fake_create_rotation_devices, field.name)
        for field in dataclasses.fields(fake_create_rotation_devices)
    }

    composite = LoadCentreCollectComposite(baton=baton, **(rlaec_args | rotation_args))
    composite.pin_tip_detection = pin_tip_detection_with_found_pin
    composite.undulator_dcm.set = MagicMock(return_value=NullStatus())
    minaxis = Location(setpoint=-2, readback=-2)
    maxaxis = Location(setpoint=2, readback=2)
    tip_x_px, tip_y_px, top_edge_array, bottom_edge_array = pin_tip_edge_data()
    sim_run_engine.add_handler(
        "locate", lambda _: minaxis, "smargon-x-low_limit_travel"
    )
    sim_run_engine.add_handler(
        "locate", lambda _: minaxis, "smargon-y-low_limit_travel"
    )
    sim_run_engine.add_handler(
        "locate", lambda _: minaxis, "smargon-z-low_limit_travel"
    )
    sim_run_engine.add_handler(
        "locate", lambda _: maxaxis, "smargon-x-high_limit_travel"
    )
    sim_run_engine.add_handler(
        "locate", lambda _: maxaxis, "smargon-y-high_limit_travel"
    )
    sim_run_engine.add_handler(
        "locate", lambda _: maxaxis, "smargon-z-high_limit_travel"
    )
    sim_run_engine.add_read_handler_for(
        composite.synchrotron.synchrotron_mode, SynchrotronMode.USER
    )
    sim_run_engine.add_read_handler_for(
        composite.synchrotron.top_up_start_countdown, -1
    )
    sim_run_engine.add_read_handler_for(
        composite.pin_tip_detection.triggered_top_edge, top_edge_array
    )
    sim_run_engine.add_read_handler_for(
        composite.pin_tip_detection.triggered_bottom_edge, bottom_edge_array
    )
    zoom_levels_list = ["1.0x", "3.0x", "5.0x", "7.5x", "10.0x"]
    composite.oav.zoom_controller.level.describe = AsyncMock(
        return_value={"level": {"choices": zoom_levels_list}}
    )
    set_mock_value(composite.oav.zoom_controller.level, "1.0x")

    sim_run_engine.add_read_handler_for(
        composite.pin_tip_detection.triggered_tip, (tip_x_px, tip_y_px)
    )
    sim_run_engine.add_read_handler_for(composite.oav.microns_per_pixel_x, 1.58)
    sim_run_engine.add_read_handler_for(composite.oav.microns_per_pixel_y, 1.58)
    return composite


@pytest.fixture
def load_centre_collect_params_multi(tmp_path):
    params = raw_params_from_file(
        GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION, tmp_path
    )
    return LoadCentreCollect(**params)


@pytest.fixture
def load_centre_collect_with_top_n_params(tmp_path):
    params = raw_params_from_file(
        "tests/test_data/parameter_json_files/load_centre_collect_params_top_n_by_max_count.json",
        tmp_path,
    )
    return LoadCentreCollect(**params)


@pytest.fixture
def load_centre_collect_with_top_n_for_each_sample(
    load_centre_collect_with_top_n_params,
):
    load_centre_collect_with_top_n_params.select_centres = (
        TopNByMaxCountForEachSampleSelection(n=5)
    )
    return load_centre_collect_with_top_n_params


@pytest.fixture
def mock_multi_rotation_scan():
    with (
        patch(
            "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.robot_load_and_change_energy_plan",
            new=MagicMock(
                return_value=iter([Msg(command="robot_load_and_change_energy")])
            ),
        ),
        patch(
            "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal",
            side_effect=lambda _, __, ___: iter([Msg(command="multi_rotation_scan")]),
        ) as mock_rotation,
    ):
        yield mock_rotation


def test_can_serialize_load_centre_collect_params(load_centre_collect_params):
    load_centre_collect_params.model_dump_json()


def test_params_good_multi_rotation_load_centre_collect_params(
    load_centre_collect_params_multi, tmp_path
):
    params = raw_params_from_file(
        GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION, tmp_path
    )
    LoadCentreCollect(**params)


def test_params_with_varying_frames_per_rotation_is_rejected(tmp_path):
    params = raw_params_from_file(
        GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION, tmp_path
    )
    params["multi_rotation_scan"]["rotation_scans"][0]["scan_width_deg"] = 180
    params["multi_rotation_scan"]["rotation_scans"][1]["scan_width_deg"] = 90
    with pytest.raises(
        ValidationError,
        match="Sweeps with different numbers of frames are not supported.",
    ):
        LoadCentreCollect(**params)


@pytest.mark.parametrize(
    "param, value",
    [
        ["x_start_um", 1.0],
        ["y_start_um", 2.0],
        ["z_start_um", 3.0],
    ],
)
def test_params_with_start_xyz_is_rejected(param: str, value: float, tmp_path):
    params = raw_params_from_file(
        GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION, tmp_path
    )
    params["multi_rotation_scan"]["rotation_scans"][1][param] = value
    with pytest.raises(
        ValidationError,
        match="Specifying start xyz for sweeps is not supported in combination with centring.",
    ):
        LoadCentreCollect(**params)


def test_params_with_different_energy_for_rotation_gridscan_rejected(tmp_path):
    params = raw_params_from_file(
        GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION, tmp_path
    )
    params["multi_rotation_scan"]["demand_energy_ev"] = 11000
    params["robot_load_then_centre"]["demand_energy_ev"] = 11100
    with pytest.raises(
        ValidationError,
        match="Setting a different energy for gridscan and rotation is not supported.",
    ):
        LoadCentreCollect(**params)


@pytest.mark.parametrize(
    "key, value",
    [
        # MxBlueskyParameters
        ["parameter_model_version", "1.2.3"],
        # WithSample
        ["sample_id", 12345],
        ["sample_puck", 1],
        ["sample_pin", 2],
        # WithVisit
        ["beamline", "i03"],
        ["visit", "cm12345"],
        ["insertion_prefix", "SR03"],
        ["detector_distance_mm", 123],
        ["det_dist_to_beam_converter_path", "/foo/bar"],
    ],
)
def test_params_with_unexpected_info_in_robot_load_rejected(
    key: str, value: Any, tmp_path
):
    params = raw_params_from_file(
        GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION, tmp_path
    )
    params["robot_load_then_centre"][key] = value
    with pytest.raises(
        ValidationError, match="Unexpected keys in robot_load_then_centre"
    ):
        LoadCentreCollect(**params)


@pytest.mark.parametrize(
    "key, value",
    [
        # MxBlueskyParameters
        ["parameter_model_version", "1.2.3"],
        # WithSample
        ["sample_id", 12345],
        ["sample_puck", 1],
        ["sample_pin", 2],
        # WithVisit
        ["beamline", "i03"],
        ["visit", "cm12345"],
        ["insertion_prefix", "SR03"],
        ["detector_distance_mm", 123],
        ["det_dist_to_beam_converter_path", "/foo/bar"],
    ],
)
def test_params_with_unexpected_info_in_multi_rotation_scan_rejected(
    key: str, value: Any, tmp_path
):
    params = raw_params_from_file(
        GOOD_TEST_LOAD_CENTRE_COLLECT_MULTI_ROTATION, tmp_path
    )
    params["multi_rotation_scan"][key] = value
    with pytest.raises(ValidationError, match="Unexpected keys in multi_rotation_scan"):
        LoadCentreCollect(**params)


def test_can_serialize_load_centre_collect_robot_load_params(
    load_centre_collect_params,
):
    load_centre_collect_params.robot_load_then_centre.model_dump_json()


def test_can_serialize_load_centre_collect_multi_rotation_scan(
    load_centre_collect_params,
):
    load_centre_collect_params.multi_rotation_scan.model_dump_json()


def test_can_serialize_load_centre_collect_single_rotation_scans(
    load_centre_collect_params,
):
    list(load_centre_collect_params.multi_rotation_scan.single_rotation_scans)[
        0
    ].model_dump_json()


@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.pin_centre_then_flyscan_plan",
    return_value=iter(
        [
            Msg(
                "open_run",
                xray_centre_results=[dataclasses.asdict(FLYSCAN_RESULT_MED)],
                run=CONST.PLAN.FLYSCAN_RESULTS,
            ),
            Msg("close_run"),
        ]
    ),
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.robot_load_and_change_energy_plan",
    return_value=iter([Msg(command="robot_load_and_change_energy")]),
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal",
    return_value=iter([Msg(command="multi_rotation_scan")]),
)
def test_collect_full_plan_happy_path_invokes_all_steps_and_centres_on_best_flyscan_result(
    mock_rotation_scan: MagicMock,
    mock_full_robot_load_plan: MagicMock,
    mock_pin_centre_then_xray_centre_plan: MagicMock,
    composite: LoadCentreCollectComposite,
    load_centre_collect_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    sim_run_engine: RunEngineSimulator,
):
    sim_run_engine.add_handler_for_callback_subscribes()
    sim_fire_event_on_open_run(sim_run_engine, CONST.PLAN.FLYSCAN_RESULTS)
    msgs = sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite, load_centre_collect_params, oav_parameters_for_rotation
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "open_run" and "xray_centre_results" in msg.kwargs,
    )
    # TODO re-enable tests see mx-bluesky 561
    # msgs = assert_message_and_return_remaining(
    #     msgs, lambda msg: msg.command == "set" and msg.args[0] == ApertureValue.MEDIUM
    # )
    # msgs = assert_message_and_return_remaining(
    #     msgs,
    #     lambda msg: msg.command == "set"
    #     and msg.obj.name == "smargon-x"
    #     and msg.args[0] == 0.1,
    # )
    # msgs = assert_message_and_return_remaining(
    #     msgs,
    #     lambda msg: msg.command == "set"
    #     and msg.obj.name == "smargon-y"
    #     and msg.args[0] == 0.2,
    # )
    # msgs = assert_message_and_return_remaining(
    #     msgs,
    #     lambda msg: msg.command == "set"
    #     and msg.obj.name == "smargon-z"
    #     and msg.args[0] == 0.3,
    # )
    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "multi_rotation_scan"
    )

    robot_load_energy_change_composite = mock_full_robot_load_plan.mock_calls[0].args[0]
    robot_load_energy_change_params = mock_full_robot_load_plan.mock_calls[0].args[1]
    assert isinstance(robot_load_energy_change_composite, RobotLoadThenCentreComposite)
    assert isinstance(robot_load_energy_change_params, RobotLoadAndEnergyChange)
    mock_pin_centre_then_xray_centre_plan.assert_called_once()
    mock_rotation_scan.assert_called_once()
    rotation_scan_composite = mock_rotation_scan.mock_calls[0].args[0]
    rotation_scan_params = mock_rotation_scan.mock_calls[0].args[1]
    assert isinstance(rotation_scan_composite, RotationScanComposite)
    assert isinstance(rotation_scan_params, RotationScan)
    # XXX sample test file xyz conflicts with detected xyz
    # see https://github.com/DiamondLightSource/mx-bluesky/issues/563
    expected_rotation_scans = [
        {
            "omega_start_deg": 0,
            "chi_start_deg": 23.85,
            "x_start_um": 400,
            "y_start_um": 500,
            "z_start_um": 600,
            "nexus_vds_start_img": 0,
            "rotation_direction": RotationDirection.NEGATIVE,
        },
    ]
    _compare_rotation_scans(
        expected_rotation_scans, rotation_scan_params.rotation_scans
    )


@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal",
    return_value=iter([]),
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_and_change_energy.set_energy_plan",
    new=MagicMock(),
)
def test_load_centre_collect_full_skips_collect_if_pin_tip_not_found(
    mock_rotation_scan: MagicMock,
    composite: LoadCentreCollectComposite,
    load_centre_collect_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    sim_run_engine: RunEngineSimulator,
):
    sim_run_engine.add_read_handler_for(
        composite.pin_tip_detection.triggered_tip, PinTipDetection.INVALID_POSITION
    )

    with pytest.raises(WarningException, match="Pin tip centring failed"):
        sim_run_engine.simulate_plan(
            load_centre_collect_full(
                composite, load_centre_collect_params, oav_parameters_for_rotation
            )
        )

    mock_rotation_scan.assert_not_called()


@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal",
    return_value=iter([]),
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_and_change_energy.set_energy_plan",
    new=MagicMock(),
)
def test_load_centre_collect_full_plan_skips_collect_if_no_diffraction(
    mock_rotation_scan: MagicMock,
    composite: LoadCentreCollectComposite,
    load_centre_collect_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    sim_run_engine: RunEngineSimulator,
    grid_detection_callback_with_detected_grid,
):
    with pytest.raises(CrystalNotFoundException):
        sim_run_engine.simulate_plan(
            load_centre_collect_full(
                composite, load_centre_collect_params, oav_parameters_for_rotation
            )
        )

    mock_rotation_scan.assert_not_called()


@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal",
    return_value=iter([]),
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_and_change_energy.set_energy_plan",
    new=MagicMock(),
)
def test_load_centre_collect_full_plan_collects_at_current_pos_if_no_diffraction_and_dummy_xtal_selection_chosen(
    mock_rotation_scan: MagicMock,
    composite: LoadCentreCollectComposite,
    load_centre_collect_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    sim_run_engine: RunEngineSimulator,
    grid_detection_callback_with_detected_grid,
):
    load_centre_collect_params.select_centres = TopNByMaxCountForEachSampleSelection(
        ignore_xtal_not_found=True, n=5
    )
    sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite, load_centre_collect_params, oav_parameters_for_rotation
        )
    )

    mock_rotation_scan.assert_called_once()


@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal"
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.RotationScan.model_validate"
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.pin_centre_then_flyscan_plan"
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_and_change_energy.do_plan_while_lower_gonio_at_home",
    new=MagicMock(),
)
def test_load_centre_collect_moves_beamstop_into_place(
    mock_pin_tip_then_flyscan_plan: MagicMock,
    mock_model_validate: MagicMock,
    mock_multi_rotation_scan: MagicMock,
    composite: LoadCentreCollectComposite,
    load_centre_collect_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    sim_run_engine: RunEngineSimulator,
):
    fake_model = MagicMock()
    fake_model.demand_energy_ev = (
        load_centre_collect_params.robot_load_then_centre.demand_energy_ev
    )

    mock_pin_tip_then_flyscan_plan.return_value = iter(
        [Msg("pin_tip_then_flyscan_plan")]
    )

    mock_model_validate.return_value = fake_model
    msgs = sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite, load_centre_collect_params, oav_parameters_for_rotation
        )
    )
    msgs = assert_message_and_return_remaining(
        msgs,
        predicate=lambda msg: msg.command == "set"
        and msg.obj.name == "beamstop-selected_pos"
        and msg.args[0] == BeamstopPositions.DATA_COLLECTION,
    )
    msgs = assert_message_and_return_remaining(
        msgs, predicate=lambda msg: msg.command == "pin_tip_then_flyscan_plan"
    )


def test_can_deserialize_top_n_by_max_count_params(
    load_centre_collect_with_top_n_params,
):
    assert load_centre_collect_with_top_n_params.select_centres.name == "TopNByMaxCount"
    assert load_centre_collect_with_top_n_params.select_centres.n == 5


def test_bad_selection_method_is_rejected(tmp_path):
    params = raw_params_from_file(
        "tests/test_data/parameter_json_files/load_centre_collect_params_top_n_by_max_count.json",
        tmp_path,
    )
    params["select_centres"]["name"] = "inject_bad_code_here"
    with pytest.raises(
        ValidationError,
        match=(
            "Input tag 'inject_bad_code_here' found using 'name' does not match any "
            "of the expected tags"
        ),
    ):
        LoadCentreCollect(**params)


def test_default_select_centres_is_top_n_by_max_count_n_is_1(
    load_centre_collect_params,
):
    assert load_centre_collect_params.select_centres.name == "TopNByMaxCount"
    assert load_centre_collect_params.select_centres.n == 1


@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.pin_centre_then_flyscan_plan",
    new=MagicMock(
        return_value=iter(
            [
                Msg(
                    "open_run",
                    xray_centre_results=[
                        dataclasses.asdict(r)
                        for r in [
                            FLYSCAN_RESULT_MED,
                            FLYSCAN_RESULT_HIGH,
                            FLYSCAN_RESULT_MED,
                            FLYSCAN_RESULT_LOW,
                            FLYSCAN_RESULT_MED,
                            FLYSCAN_RESULT_HIGH,
                        ]
                    ],
                    run=CONST.PLAN.FLYSCAN_RESULTS,
                ),
                Msg("close_run"),
            ]
        )
    ),
)
def test_load_centre_collect_full_plan_multiple_centres(
    mock_multi_rotation_scan: MagicMock,
    sim_run_engine: RunEngineSimulator,
    load_centre_collect_with_top_n_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    composite: LoadCentreCollectComposite,
):
    sim_run_engine.add_handler_for_callback_subscribes()
    sim_fire_event_on_open_run(sim_run_engine, CONST.PLAN.FLYSCAN_RESULTS)
    msgs = sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite,
            load_centre_collect_with_top_n_params,
            oav_parameters_for_rotation,
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "robot_load_and_change_energy"
    )
    assert sum(1 for msg in msgs if msg.command == "robot_load_and_change_energy") == 1
    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "open_run" and "xray_centre_results" in msg.kwargs,
    )
    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "multi_rotation_scan"
    )

    def _rotation_at_first_position(direction: RotationDirection, chi):
        return {
            "omega_start_deg": 10 if direction == RotationDirection.NEGATIVE else -350,
            "chi_start_deg": chi,
            "x_start_um": 100,
            "y_start_um": 200,
            "z_start_um": 300,
            "rotation_direction": direction,
        }

    def _rotation_at_second_position(direction: RotationDirection, chi):
        return {
            "omega_start_deg": 10 if direction == RotationDirection.NEGATIVE else -350,
            "chi_start_deg": chi,
            "x_start_um": 400,
            "y_start_um": 500,
            "z_start_um": 600,
            "rotation_direction": direction,
        }

    expected_rotation_scans = [
        _rotation_at_first_position(RotationDirection.NEGATIVE, 0),
        _rotation_at_first_position(RotationDirection.POSITIVE, 30),
        _rotation_at_first_position(RotationDirection.NEGATIVE, 0),
        _rotation_at_first_position(RotationDirection.POSITIVE, 30),
        _rotation_at_second_position(RotationDirection.NEGATIVE, 0),
        _rotation_at_second_position(RotationDirection.POSITIVE, 30),
        _rotation_at_second_position(RotationDirection.NEGATIVE, 0),
        _rotation_at_second_position(RotationDirection.POSITIVE, 30),
        _rotation_at_second_position(RotationDirection.NEGATIVE, 0),
        _rotation_at_second_position(RotationDirection.POSITIVE, 30),
    ]
    for i in range(0, len(expected_rotation_scans)):
        expected_rotation_scans[i]["nexus_vds_start_img"] = 3600 * i

    rotation_scan_params = mock_multi_rotation_scan.mock_calls[0].args[1]
    assert isinstance(rotation_scan_params, RotationScan)
    _compare_rotation_scans(
        expected_rotation_scans, rotation_scan_params.rotation_scans
    )
    assert rotation_scan_params.transmission_frac == 0.05


@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.pin_centre_then_flyscan_plan",
    new=MagicMock(
        return_value=iter(
            [
                Msg(
                    "open_run",
                    xray_centre_results=[
                        dataclasses.asdict(r)
                        for r in [
                            FLYSCAN_RESULT_POS_2,
                            FLYSCAN_RESULT_POS_3,
                            FLYSCAN_RESULT_POS_1,
                            FLYSCAN_RESULT_POS_5,
                            FLYSCAN_RESULT_POS_4,
                        ]
                    ],
                    run=CONST.PLAN.FLYSCAN_RESULTS,
                ),
                Msg("close_run"),
            ]
        )
    ),
)
def test_load_centre_collect_full_sorts_collections_by_distance_from_pin_tip(
    mock_multi_rotation_scan: MagicMock,
    sim_run_engine: RunEngineSimulator,
    load_centre_collect_with_top_n_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    composite: LoadCentreCollectComposite,
):
    sim_run_engine.add_handler_for_callback_subscribes()
    sim_fire_event_on_open_run(sim_run_engine, CONST.PLAN.FLYSCAN_RESULTS)
    sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite,
            load_centre_collect_with_top_n_params,
            oav_parameters_for_rotation,
        )
    )

    expected_xyz = [
        (10.0, 20.0, 30.0, 0.0),
        (10.0, 20.0, 30.0, 30.0),
        (20.0, 20.0, 30.0, 0.0),
        (20.0, 20.0, 30.0, 30.0),
        (30.0, 20.0, 30.0, 0.0),
        (30.0, 20.0, 30.0, 30.0),
        (40.0, 20.0, 30.0, 0.0),
        (40.0, 20.0, 30.0, 30.0),
        (50.0, 20.0, 30.0, 0.0),
        (50.0, 20.0, 30.0, 30.0),
    ]

    expected_sample_ids = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

    mock_multi_rotation_scan.assert_called_once()
    params: RotationScan = mock_multi_rotation_scan.mock_calls[0].args[1]
    actual_coords = [
        (scan.x_start_um, scan.y_start_um, scan.z_start_um, scan.chi_start_deg)
        for scan in list(params.single_rotation_scans)
    ]
    assert actual_coords == expected_xyz
    actual_ids = [scan.sample_id for scan in list(params.single_rotation_scans)]
    assert actual_ids == expected_sample_ids


def _rotation_at(
    chi: float,
    position: dict,
    omega_start_deg: int,
    rotation_direction: RotationDirection,
) -> dict:
    return {
        "omega_start_deg": omega_start_deg,
        "chi_start_deg": chi,
        "rotation_direction": rotation_direction,
    } | position


@patch(
    "mx_bluesky.hyperion.parameters.constants.I03Constants.ALTERNATE_ROTATION_DIRECTION",
    new=True,
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.pin_centre_then_flyscan_plan",
    new=MagicMock(
        side_effect=lambda *args, **kwargs: iter(
            [
                Msg(
                    "open_run",
                    xray_centre_results=[
                        dataclasses.asdict(r)
                        for r in [
                            FLYSCAN_RESULT_HIGH,
                            FLYSCAN_RESULT_MED,
                        ]
                    ],
                    run=CONST.PLAN.FLYSCAN_RESULTS,
                ),
                Msg("close_run"),
            ]
        )
    ),
)
@pytest.mark.parametrize(
    "rotation_scans, expected_scans",
    [
        [
            (
                {
                    "omega_start_deg": 10,
                    "chi_start_deg": 0,
                    "scan_width_deg": 359,
                },
                {
                    "omega_start_deg": 10,
                    "chi_start_deg": 30,
                    "scan_width_deg": 359,
                },
            ),
            (
                _rotation_at(0, POS_HIGH, 10, RotationDirection.NEGATIVE),
                _rotation_at(30, POS_HIGH, -349, RotationDirection.POSITIVE),
                _rotation_at(0, POS_MED, 10, RotationDirection.NEGATIVE),
                _rotation_at(30, POS_MED, -349, RotationDirection.POSITIVE),
            ),
        ],
        [
            (
                {
                    "omega_start_deg": 10,
                    "chi_start_deg": 0,
                    "scan_width_deg": 359,
                },
            ),
            (
                _rotation_at(0, POS_HIGH, 10, RotationDirection.NEGATIVE),
                _rotation_at(0, POS_MED, -349, RotationDirection.POSITIVE),
            ),
        ],
        [
            (
                {
                    "omega_start_deg": 10,
                    "chi_start_deg": 0,
                    "scan_width_deg": 360,
                },
                {
                    "omega_start_deg": 10,
                    "chi_start_deg": 30,
                    "scan_width_deg": 360,
                },
            ),
            (
                _rotation_at(0, POS_HIGH, 10, RotationDirection.NEGATIVE),
                _rotation_at(30, POS_HIGH, -350, RotationDirection.POSITIVE),
                _rotation_at(0, POS_MED, 10, RotationDirection.NEGATIVE),
                _rotation_at(30, POS_MED, -350, RotationDirection.POSITIVE),
            ),
        ],
    ],
)
def test_load_centre_collect_full_plan_alternates_rotation_with_multiple_centres(
    mock_multi_rotation_scan: MagicMock,
    sim_run_engine: RunEngineSimulator,
    load_centre_collect_with_top_n_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    composite: LoadCentreCollectComposite,
    rotation_scans: tuple[dict],
    expected_scans: tuple[dict],
):
    load_centre_collect_with_top_n_params.multi_rotation_scan.rotation_scans = [
        RotationScanPerSweep.model_construct(**rs) for rs in rotation_scans
    ]
    LoadCentreCollect.model_validate(load_centre_collect_with_top_n_params)

    sim_run_engine.add_handler_for_callback_subscribes()
    sim_fire_event_on_open_run(sim_run_engine, CONST.PLAN.FLYSCAN_RESULTS)
    sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite,
            load_centre_collect_with_top_n_params,
            oav_parameters_for_rotation,
        )
    )

    multi_rotation_params = load_centre_collect_with_top_n_params.multi_rotation_scan
    sweeps = multi_rotation_params.rotation_scans
    for i in range(0, len(expected_scans)):
        sweep_params = sweeps[i % len(sweeps)]
        expected_scans[i]["nexus_vds_start_img"] = (
            sweep_params.scan_width_deg * 10
        ) * i

    rotation_scan_params = mock_multi_rotation_scan.mock_calls[0].args[1]
    assert isinstance(rotation_scan_params, RotationScan)
    _compare_rotation_scans(expected_scans, rotation_scan_params.rotation_scans)
    assert rotation_scan_params.transmission_frac == 0.05


@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.pin_centre_then_flyscan_plan",
    new=MagicMock(
        side_effect=lambda *args, **kwargs: iter(
            [
                Msg(
                    "open_run",
                    xray_centre_results=[
                        dataclasses.asdict(r)
                        for r in [
                            FLYSCAN_RESULT_HIGH,
                            FLYSCAN_RESULT_MED,
                        ]
                    ],
                    run=CONST.PLAN.FLYSCAN_RESULTS,
                ),
                Msg("close_run"),
            ]
        )
    ),
)
def test_load_centre_collect_full_plan_assigns_sample_ids_to_rotations_according_to_zocalo_assignment(
    mock_multi_rotation_scan: MagicMock,
    sim_run_engine: RunEngineSimulator,
    composite: LoadCentreCollectComposite,
    load_centre_collect_with_top_n_for_each_sample: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
):
    sim_run_engine.add_handler_for_callback_subscribes()
    sim_fire_event_on_open_run(sim_run_engine, CONST.PLAN.FLYSCAN_RESULTS)
    sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite,
            load_centre_collect_with_top_n_for_each_sample,
            oav_parameters_for_rotation,
        )
    )

    parameters: RotationScan = mock_multi_rotation_scan.mock_calls[0].args[1]
    assert len(parameters.rotation_scans) == 4
    assert [
        (rs.x_start_um, rs.y_start_um, rs.z_start_um)
        for rs in parameters.rotation_scans
    ] == [
        (100.0, 200.0, 300.0),
        (100.0, 200.0, 300.0),
        (400.0, 500.0, 600.0),
        (400.0, 500.0, 600.0),
    ]

    assert [rs.sample_id for rs in parameters.rotation_scans] == [2, 2, 1, 1]


@patch(
    "mx_bluesky.hyperion.experiment_plans.robot_load_then_centre_plan.pin_centre_then_flyscan_plan",
    new=MagicMock(
        side_effect=lambda *args, **kwargs: iter(
            [
                Msg(
                    "open_run",
                    xray_centre_results=[
                        dataclasses.asdict(r)
                        for r in [
                            FLYSCAN_RESULT_HIGH_NO_SAMPLE_ID,
                            FLYSCAN_RESULT_MED,
                        ]
                    ],
                    run=CONST.PLAN.FLYSCAN_RESULTS,
                ),
                Msg("close_run"),
            ]
        )
    ),
)
def test_load_centre_collect_full_plan_omits_collection_if_no_sample_id_is_assigned(
    mock_multi_rotation_scan: MagicMock,
    sim_run_engine: RunEngineSimulator,
    composite: LoadCentreCollectComposite,
    load_centre_collect_with_top_n_for_each_sample: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
):
    sim_run_engine.add_handler_for_callback_subscribes()
    sim_fire_event_on_open_run(sim_run_engine, CONST.PLAN.FLYSCAN_RESULTS)
    sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite,
            load_centre_collect_with_top_n_for_each_sample,
            oav_parameters_for_rotation,
        )
    )

    parameters: RotationScan = mock_multi_rotation_scan.mock_calls[0].args[1]
    assert len(parameters.rotation_scans) == 2
    assert [
        (rs.x_start_um, rs.y_start_um, rs.z_start_um)
        for rs in parameters.rotation_scans
    ] == [
        (400.0, 500.0, 600.0),
        (400.0, 500.0, 600.0),
    ]

    assert [rs.sample_id for rs in parameters.rotation_scans] == [1, 1]


def _compare_rotation_scans(
    expected_rotation_scans: Sequence[dict],
    actual_rotation_scans: Sequence[RotationScanPerSweep],
):
    for expected, rotation_scan in zip(
        expected_rotation_scans, actual_rotation_scans, strict=False
    ):
        assert rotation_scan.omega_start_deg == expected["omega_start_deg"]
        assert rotation_scan.chi_start_deg == expected["chi_start_deg"]
        assert rotation_scan.x_start_um == expected["x_start_um"]
        assert rotation_scan.y_start_um == expected["y_start_um"]
        assert rotation_scan.z_start_um == expected["z_start_um"]
        assert rotation_scan.nexus_vds_start_img == expected["nexus_vds_start_img"]
        assert rotation_scan.rotation_direction == expected["rotation_direction"]


@patch("mx_bluesky.common.parameters.components.os.makedirs")
def test_load_centre_collect_creates_storage_directory_if_not_present(
    mock_makedirs, tmp_path
):
    params = raw_params_from_file(
        "tests/test_data/parameter_json_files/good_test_load_centre_collect_params.json",
        tmp_path,
    )
    LoadCentreCollect(**params)

    mock_makedirs.assert_has_calls(
        [
            call(
                str(tmp_path / "123458/xraycentring"),
                exist_ok=True,
            )
        ],
        any_order=True,
    )
    mock_makedirs.assert_has_calls(
        [call(f"{str(tmp_path)}/123458/", exist_ok=True)],
        any_order=True,
    )


@pytest.mark.timeout(2)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.detect_grid_and_do_gridscan"
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal",
    MagicMock(),
)
def test_box_size_passed_through_to_gridscan(
    mock_detect_grid: MagicMock,
    composite: LoadCentreCollectComposite,
    load_centre_collect_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    RE: RunEngine,
):
    load_centre_collect_params.robot_load_then_centre.box_size_um = 25

    RE(
        load_centre_collect_full(
            composite, load_centre_collect_params, oav_parameters_for_rotation
        )
    )
    detect_grid_call = mock_detect_grid.mock_calls[0]
    assert detect_grid_call.args[1].box_size_um == 25


@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.rotation_scan_internal",
    return_value=iter([]),
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.load_centre_collect_full_plan.robot_load_then_xray_centre",
    return_value=iter([]),
)
def test_load_centre_collect_full_collects_at_current_location_if_no_xray_centring_required(
    _: MagicMock,
    mock_rotation_scan: MagicMock,
    composite: LoadCentreCollectComposite,
    load_centre_collect_params: LoadCentreCollect,
    oav_parameters_for_rotation: OAVParameters,
    sim_run_engine: RunEngineSimulator,
):
    sim_run_engine.add_read_handler_for(composite.smargon.x, 1.1)
    sim_run_engine.add_read_handler_for(composite.smargon.y, 2.2)
    sim_run_engine.add_read_handler_for(composite.smargon.z, 3.3)

    sim_run_engine.simulate_plan(
        load_centre_collect_full(
            composite, load_centre_collect_params, oav_parameters_for_rotation
        )
    )

    rotation_scans = mock_rotation_scan.call_args.args[1].rotation_scans
    assert len(rotation_scans) == 1
    assert rotation_scans[0].x_start_um == 1100
    assert rotation_scans[0].y_start_um == 2200
    assert rotation_scans[0].z_start_um == 3300
