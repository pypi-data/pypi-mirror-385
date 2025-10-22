# from collections.abc import Sequence
from typing import Literal

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.beamlines import i24
from dodal.common import inject
from dodal.devices.hutch_shutter import HutchShutter
from dodal.devices.i24.aperture import Aperture
from dodal.devices.i24.beam_center import DetectorBeamCenter
from dodal.devices.i24.beamstop import Beamstop
from dodal.devices.i24.dcm import DCM
from dodal.devices.i24.dual_backlight import BacklightPositions, DualBacklight
from dodal.devices.i24.focus_mirrors import FocusMirrorsMode
from dodal.devices.i24.pmac import PMAC
from dodal.devices.motors import YZStage
from dodal.devices.oav.oav_detector import OAVBeamCentreFile
from dodal.devices.zebra.zebra import Zebra

from mx_bluesky.beamlines.i24.serial.dcid import DCID
from mx_bluesky.beamlines.i24.serial.fixed_target.ft_utils import (
    ChipType,
    MappingType,
    PumpProbeSetting,
)
from mx_bluesky.beamlines.i24.serial.fixed_target.i24ssx_Chip_Collect_py3v1 import (
    run_plan_in_wrapper,
)
from mx_bluesky.beamlines.i24.serial.fixed_target.i24ssx_Chip_Manager_py3v1 import (
    upload_chip_map_to_geobrick,
)
from mx_bluesky.beamlines.i24.serial.fixed_target.i24ssx_moveonclick import (
    _move_on_mouse_click_plan,
)
from mx_bluesky.beamlines.i24.serial.log import (
    SSX_LOGGER,
    _read_visit_directory_from_file,
)
from mx_bluesky.beamlines.i24.serial.parameters import (
    FixedTargetParameters,
    get_chip_format,
)
from mx_bluesky.beamlines.i24.serial.parameters.utils import EmptyMapError
from mx_bluesky.beamlines.i24.serial.setup_beamline import pv
from mx_bluesky.beamlines.i24.serial.setup_beamline.ca import caput
from mx_bluesky.beamlines.i24.serial.setup_beamline.pv_abstract import Eiger
from mx_bluesky.beamlines.i24.serial.setup_beamline.setup_detector import (
    _move_detector_stage,
    get_detector_type,
)


@bpp.run_decorator()
def gui_move_backlight(
    position: str, backlight: DualBacklight = inject("backlight")
) -> MsgGenerator:
    bl_pos = BacklightPositions(position)
    yield from bps.abs_set(backlight, bl_pos, wait=True)
    SSX_LOGGER.debug(f"Backlight moved to {bl_pos.value}")


@bpp.run_decorator()
def gui_set_zoom_level(
    position: str, oav: OAVBeamCentreFile = inject("oav")
) -> MsgGenerator:
    yield from bps.abs_set(oav.zoom_controller, position, wait=True)
    SSX_LOGGER.debug(f"Setting zoom level to {position}")


@bpp.run_decorator()
def gui_stage_move_on_click(
    position_px: tuple[int, int],
    oav: OAVBeamCentreFile = inject("oav"),
    pmac: PMAC = inject("pmac"),
) -> MsgGenerator:
    yield from _move_on_mouse_click_plan(oav, pmac, position_px)


@bpp.run_decorator()
def gui_gonio_move_on_click(position_px: tuple[int, int]) -> MsgGenerator:
    oav = i24.oav()
    gonio = i24.vgonio()

    x_pixels_per_micron = yield from bps.rd(oav.microns_per_pixel_x)
    y_pixels_per_micron = yield from bps.rd(oav.microns_per_pixel_y)

    x_um = position_px[0] * x_pixels_per_micron
    y_um = position_px[1] * y_pixels_per_micron

    # gonio is in mm?
    yield from bps.mv(gonio.x, x_um / 1000, gonio.yh, y_um / 1000)  # type: ignore


# See https://github.com/DiamondLightSource/mx-bluesky/issues/853
@bpp.run_decorator()
def gui_sleep(sec: int) -> MsgGenerator:
    for _ in range(sec):
        yield from bps.sleep(1)


@bpp.run_decorator()
def gui_move_detector(
    det: Literal["eiger"],
    detector_stage: YZStage = inject("detector_motion"),
) -> MsgGenerator:
    det_y_target = Eiger.det_y_target
    yield from _move_detector_stage(detector_stage, det_y_target)
    # Make the output readable
    SSX_LOGGER.debug(f"Detector move done, resetting general PV to {det}")
    caput(pv.me14e_gp101, det)


@bpp.run_decorator()
def gui_run_chip_collection(
    sub_dir: str,
    chip_name: str,
    exp_time: float,
    det_dist: float,
    transmission: float,
    n_shots: int,
    chip_type: str,
    map_type: str,
    chip_format: list[int | float],  # for Lite Oxford it's the chipmap
    checker_pattern: bool,
    pump_probe: str,
    laser_dwell: float,
    laser_delay: float,
    pre_pump: float,
    pmac: PMAC = inject("pmac"),
    zebra: Zebra = inject("zebra"),
    aperture: Aperture = inject("aperture"),
    backlight: DualBacklight = inject("backlight"),
    beamstop: Beamstop = inject("beamstop"),
    detector_stage: YZStage = inject("detector_motion"),
    shutter: HutchShutter = inject("shutter"),
    dcm: DCM = inject("dcm"),
    mirrors: FocusMirrorsMode = inject("focus_mirrors"),
    beam_center_eiger: DetectorBeamCenter = inject("eiger_bc"),
) -> MsgGenerator:
    """Set the parameter model for the data collection.

    Args:
        sub_dir (str): subdirectory of the visit to write data in.
        chip_name (str): a name identifying the current chip collection, will be used
            as filename.
        exp_time (float): exposure time of each window shot, in s.
        det_dist (float): sample-detector distance, in mm.
        transmission (float): requested beam intensity transmission, expressed as
            a fraction, e.g. 0.3.
        n_shots (int): number of times each window should be collected.
        chip_type (str): type of chip in use.
        map_type (str): if an Oxford chip is used, define whether it's a full chip
            collection or lite mapping is in use. For all other chip, this will be None.
        chip_format (list[int|float]): for a custom chip, a list of the number of x,y
            steps and the x,y step size. For an Oxford chip, the list should be empty
            if collecting a full chip and a list of the block numbers to scan for a
            lite collection.
        checker_pattern (bool): whether checker_pattern is turned on, ie. only every
            other window in a block gets collected
        pump_probe (str): pump probe setting.
        laser_dwell (float): laser exposure time for pump probe collections, in s.
        laser_delay (float): delay between laser exposure and collection, in s.
        pre_pump (float): pre-pump exposure time for a pump probe short2 collection,
            ie a pump-in-probe where the collection starts during the pump.
    """
    # NOTE still a work in progress, adding to it as the ui grows
    # See progression of https://github.com/DiamondLightSource/mx-daq-ui/issues/3
    det_type = yield from get_detector_type(detector_stage)
    _format = chip_format if ChipType[chip_type] is ChipType.Custom else None
    chip_params = get_chip_format(ChipType[chip_type], _format)
    if ChipType[chip_type] in [ChipType.Oxford, ChipType.OxfordInner]:
        mapping = MappingType.Lite if map_type == "Lite" else MappingType.NoMap
        if mapping is MappingType.Lite and len(chip_format) == 0:
            # this logic should go in the gui with error message.
            raise EmptyMapError("No blocks chosen")
        chip_map = chip_format
    else:
        mapping = MappingType.NoMap
        chip_map = []

    params = {
        "visit": _read_visit_directory_from_file().as_posix(),  # noqa
        "directory": sub_dir,
        "filename": chip_name,
        "exposure_time_s": exp_time,
        "detector_distance_mm": det_dist,
        "detector_name": str(det_type),
        "num_exposures": n_shots,
        "transmission": transmission,
        "chip": chip_params,
        "map_type": mapping,
        "chip_map": chip_map,
        "pump_repeat": PumpProbeSetting[pump_probe],  # pump_repeat,
        "laser_dwell_s": laser_dwell,
        "laser_delay_s": laser_delay,
        "checker_pattern": checker_pattern,
        "pre_pump_exposure_s": pre_pump,
    }

    parameters = FixedTargetParameters(**params)

    # Create collection directory
    parameters.collection_directory.mkdir(parents=True, exist_ok=True)

    if parameters.chip_map:
        yield from upload_chip_map_to_geobrick(pmac, parameters.chip_map)

    beam_center_device = beam_center_eiger
    SSX_LOGGER.info("Beam center device ready")

    # DCID instance - do not create yet
    dcid = DCID(emit_errors=False, expt_params=parameters)  # noqa
    SSX_LOGGER.info("DCID created")

    yield from run_plan_in_wrapper(
        zebra,
        pmac,
        aperture,
        backlight,
        beamstop,
        detector_stage,
        shutter,
        dcm,
        mirrors,
        beam_center_device,
        parameters,
        dcid,
    )
