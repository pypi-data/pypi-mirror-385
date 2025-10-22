from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from bluesky.simulators import RunEngineSimulator, assert_message_and_return_remaining
from bluesky.utils import Msg
from dodal.devices.aperturescatterguard import ApertureValue
from dodal.devices.backlight import InOut
from dodal.devices.detector.detector_motion import ShutterState
from dodal.devices.i03 import BeamstopPositions
from dodal.devices.smargon import CombinedMove
from dodal.devices.synchrotron import SynchrotronMode

from mx_bluesky.common.experiment_plans.common_flyscan_xray_centre_plan import (
    _fire_xray_centre_result_event,
)
from mx_bluesky.hyperion.experiment_plans.hyperion_grid_detect_then_xray_centre_plan import (
    HyperionGridDetectThenXRayCentreComposite,
)
from mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan import (
    create_parameters_for_grid_detection,
    pin_centre_then_flyscan_plan,
    pin_tip_centre_then_xray_centre,
)
from mx_bluesky.hyperion.parameters.constants import CONST
from mx_bluesky.hyperion.parameters.gridscan import (
    PinTipCentreThenXrayCentre,
)

from ....conftest import TEST_RESULT_LARGE, raw_params_from_file, simulate_xrc_result
from .conftest import FLYSCAN_RESULT_LOW, FLYSCAN_RESULT_MED, sim_fire_event_on_open_run


@pytest.fixture
def test_pin_centre_then_xray_centre_params(tmp_path):
    params = raw_params_from_file(
        "tests/test_data/parameter_json_files/good_test_pin_centre_then_xray_centre_parameters.json",
        tmp_path,
    )
    return PinTipCentreThenXrayCentre(**params)


@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.pin_tip_centre_plan",
    autospec=True,
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.detect_grid_and_do_gridscan",
    autospec=True,
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.change_aperture_then_move_to_xtal",
    autospec=True,
)
def test_pin_tip_centre_then_xray_centre_moves_to_centre_of_first_flyscan_result(
    mock_change_aperture_then_move_to_xtal: MagicMock,
    mock_detect_and_do_gridscan: MagicMock,
    mock_pin_tip_centre: MagicMock,
    hyperion_grid_detect_xrc_devices: HyperionGridDetectThenXRayCentreComposite,
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
    test_config_files,
    RE: RunEngine,
):
    mock_detect_and_do_gridscan.side_effect = lambda *_: _fire_xray_centre_result_event(
        [FLYSCAN_RESULT_MED, FLYSCAN_RESULT_LOW]
    )
    RE(
        pin_tip_centre_then_xray_centre(
            hyperion_grid_detect_xrc_devices,
            test_pin_centre_then_xray_centre_params,
            test_config_files["oav_config_json"],
        )
    )

    mock_detect_and_do_gridscan.assert_called_once()
    mock_pin_tip_centre.assert_called_once()
    mock_change_aperture_then_move_to_xtal.assert_called_once()
    assert (
        mock_change_aperture_then_move_to_xtal.mock_calls[0].args[0]
        == FLYSCAN_RESULT_MED
    )


def test_when_create_parameters_for_grid_detection_then_parameters_created(
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
):
    grid_detect_params = create_parameters_for_grid_detection(
        test_pin_centre_then_xray_centre_params
    )

    assert grid_detect_params.exposure_time_s == 0.1


@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.pin_tip_centre_plan",
    autospec=True,
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.detect_grid_and_do_gridscan",
    autospec=True,
)
def test_when_pin_centre_xray_centre_called_then_plan_runs_correctly(
    mock_detect_and_do_gridscan: MagicMock,
    mock_pin_tip_centre: MagicMock,
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
    hyperion_grid_detect_xrc_devices: HyperionGridDetectThenXRayCentreComposite,
    test_config_files,
    RE: RunEngine,
):
    RE(
        pin_centre_then_flyscan_plan(
            hyperion_grid_detect_xrc_devices,
            test_pin_centre_then_xray_centre_params,
            test_config_files["oav_config_json"],
        )
    )

    mock_detect_and_do_gridscan.assert_called_once()
    mock_pin_tip_centre.assert_called_once()


@patch(
    "mx_bluesky.common.experiment_plans.common_grid_detect_then_xray_centre_plan.GridDetectionCallback",
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.pin_tip_centre_plan",
    autospec=True,
)
@patch(
    "mx_bluesky.common.experiment_plans.common_grid_detect_then_xray_centre_plan.grid_detection_plan",
    autospec=True,
)
def test_when_pin_centre_xray_centre_called_then_detector_positioned(
    mock_grid_detect: MagicMock,
    mock_pin_tip_centre: MagicMock,
    mock_grid_callback: MagicMock,
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
    hyperion_grid_detect_xrc_devices: HyperionGridDetectThenXRayCentreComposite,
    test_config_files,
    sim_run_engine: RunEngineSimulator,
):
    mock_grid_callback.return_value.get_grid_parameters.return_value = {
        "transmission_frac": 1.0,
        "exposure_time_s": 0,
        "x_start_um": 0,
        "y_start_um": 0,
        "y2_start_um": 0,
        "z_start_um": 0,
        "z2_start_um": 0,
        "x_steps": 10,
        "y_steps": 10,
        "z_steps": 10,
        "x_step_size_um": 0.1,
        "y_step_size_um": 0.1,
        "z_step_size_um": 0.1,
    }

    sim_run_engine.add_handler_for_callback_subscribes()

    sim_run_engine.add_handler(
        "read",
        lambda msg_: {"values": {"value": SynchrotronMode.SHUTDOWN}},
        "synchrotron-synchrotron_mode",
    )
    simulate_xrc_result(
        sim_run_engine, hyperion_grid_detect_xrc_devices.zocalo, TEST_RESULT_LARGE
    )

    def add_handlers_to_simulate_detector_motion(msg: Msg):
        sim_run_engine.add_handler(
            "read",
            lambda msg_: {"values": {"value": int(ShutterState.OPEN)}},
            "detector_motion_shutter",
        )
        sim_run_engine.add_handler(
            "read",
            lambda msg_: {"values": {"value": 1}},
            "detector_motion_z_motor_done_move",
        )

    sim_fire_event_on_open_run(sim_run_engine, CONST.PLAN.FLYSCAN_RESULTS)
    sim_run_engine.add_wait_handler(
        add_handlers_to_simulate_detector_motion, CONST.WAIT.GRID_READY_FOR_DC
    )

    simulate_xrc_result(
        sim_run_engine, hyperion_grid_detect_xrc_devices.zocalo, TEST_RESULT_LARGE
    )
    messages = sim_run_engine.simulate_plan(
        pin_tip_centre_then_xray_centre(
            hyperion_grid_detect_xrc_devices,
            test_pin_centre_then_xray_centre_params,
            test_config_files["oav_config_json"],
        ),
    )

    messages = assert_message_and_return_remaining(
        messages,
        lambda msg: msg.obj is hyperion_grid_detect_xrc_devices.detector_motion.z,
    )
    assert messages[0].args[0] == 100
    assert messages[0].kwargs["group"] == CONST.WAIT.GRID_READY_FOR_DC
    assert messages[1].obj is hyperion_grid_detect_xrc_devices.detector_motion.shutter
    assert messages[1].args[0] == ShutterState.OPEN
    assert messages[1].kwargs["group"] == CONST.WAIT.GRID_READY_FOR_DC
    messages = assert_message_and_return_remaining(
        messages[2:],
        lambda msg: msg.command == "wait"
        and msg.kwargs["group"] == CONST.WAIT.GRID_READY_FOR_DC,
    )
    assert_message_and_return_remaining(
        messages[2:],
        lambda msg: msg.command == "open_run"
        and msg.kwargs["subplan_name"] == "do_fgs",
    )


@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.pin_tip_centre_plan",
    autospec=True,
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.detect_grid_and_do_gridscan",
    autospec=True,
)
def test_pin_centre_then_xray_centre_plan_activates_ispyb_callback_before_pin_tip_centre_plan(
    mock_detect_grid_and_do_gridscan,
    mock_pin_tip_centre_plan,
    sim_run_engine: RunEngineSimulator,
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
    hyperion_grid_detect_xrc_devices: HyperionGridDetectThenXRayCentreComposite,
    test_config_files,
):
    mock_detect_grid_and_do_gridscan.return_value = iter(
        [Msg("detect_grid_and_do_gridscan")]
    )
    mock_pin_tip_centre_plan.return_value = iter([Msg("pin_tip_centre_plan")])

    msgs = sim_run_engine.simulate_plan(
        pin_centre_then_flyscan_plan(
            hyperion_grid_detect_xrc_devices,
            test_pin_centre_then_xray_centre_params,
            test_config_files["oav_config_json"],
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "open_run"
        and "GridscanISPyBCallback" in msg.kwargs["activate_callbacks"],
    )
    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "pin_tip_centre_plan"
    )
    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "detect_grid_and_do_gridscan"
    )
    assert_message_and_return_remaining(msgs, lambda msg: msg.command == "close_run")


@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.pin_tip_centre_plan",
    autospec=True,
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.detect_grid_and_do_gridscan",
    autospec=True,
)
def test_pin_centre_then_xray_centre_plan_sets_up_backlight_and_aperture(
    mock_detect_grid_and_do_gridscan,
    mock_pin_tip_centre_plan,
    hyperion_grid_detect_xrc_devices: HyperionGridDetectThenXRayCentreComposite,
    sim_run_engine: RunEngineSimulator,
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
    test_config_files,
):
    mock_detect_grid_and_do_gridscan.return_value = iter(
        [Msg("detect_grid_and_do_gridscan")]
    )
    mock_pin_tip_centre_plan.return_value = iter([Msg("pin_tip_centre_plan")])

    msgs = sim_run_engine.simulate_plan(
        pin_centre_then_flyscan_plan(
            hyperion_grid_detect_xrc_devices,
            test_pin_centre_then_xray_centre_params,
            test_config_files["oav_config_json"],
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "backlight"
        and msg.args == (InOut.IN,)
        and msg.kwargs["group"] == CONST.WAIT.READY_FOR_OAV,
    )
    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj
        == hyperion_grid_detect_xrc_devices.aperture_scatterguard.selected_aperture
        and msg.args == (ApertureValue.OUT_OF_BEAM,)
        and msg.kwargs["group"] == CONST.WAIT.READY_FOR_OAV,
    )

    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "pin_tip_centre_plan"
    )


@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.pin_tip_centre_plan",
    autospec=True,
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.detect_grid_and_do_gridscan",
    autospec=True,
)
def test_pin_centre_then_xray_centre_plan_goes_to_the_starting_chi_and_phi(
    mock_detect_grid_and_do_gridscan,
    mock_pin_tip_centre_plan,
    sim_run_engine: RunEngineSimulator,
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
    test_config_files,
    hyperion_grid_detect_xrc_devices,
):
    mock_detect_grid_and_do_gridscan.return_value = iter(
        [Msg("detect_grid_and_do_gridscan")]
    )
    mock_pin_tip_centre_plan.return_value = iter([Msg("pin_tip_centre_plan")])

    test_pin_centre_then_xray_centre_params.phi_start_deg = (expected_phi := 30)
    test_pin_centre_then_xray_centre_params.chi_start_deg = (expected_chi := 50)

    msgs = sim_run_engine.simulate_plan(
        pin_centre_then_flyscan_plan(
            hyperion_grid_detect_xrc_devices,
            test_pin_centre_then_xray_centre_params,
            test_config_files["oav_config_json"],
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "set"
        and msg.obj.name == "smargon"
        and msg.args[0] == CombinedMove(phi=expected_phi, chi=expected_chi, omega=None)
        and msg.kwargs["group"] == CONST.WAIT.READY_FOR_OAV,
    )

    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "pin_tip_centre_plan"
    )


@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.pin_centre_then_flyscan_plan"
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.XRayCentreEventHandler"
)
@patch(
    "mx_bluesky.hyperion.experiment_plans.pin_centre_then_xray_centre_plan.change_aperture_then_move_to_xtal"
)
def test_pin_tip_centre_then_xray_centre_moves_beamstop_into_place(
    mock_pin_centre_flyscan_plan: MagicMock,
    mock_events_handler: MagicMock,
    mock_change_aperture_then_move_to_xtal: MagicMock,
    sim_run_engine: RunEngineSimulator,
    hyperion_grid_detect_xrc_devices: HyperionGridDetectThenXRayCentreComposite,
    test_pin_centre_then_xray_centre_params: PinTipCentreThenXrayCentre,
):
    flyscan_event_handler = MagicMock()
    flyscan_event_handler.xray_centre_results = "dummy"
    mock_events_handler.return_value = flyscan_event_handler

    mock_pin_centre_flyscan_plan.return_value = iter([Msg("pin_centre_flyscan_plan")])

    msgs = sim_run_engine.simulate_plan(
        pin_tip_centre_then_xray_centre(
            hyperion_grid_detect_xrc_devices, test_pin_centre_then_xray_centre_params
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        predicate=lambda msg: msg.command == "set"
        and msg.obj.name == "beamstop-selected_pos"
        and msg.args[0] == BeamstopPositions.DATA_COLLECTION,
    )
    msgs = assert_message_and_return_remaining(
        msgs, predicate=lambda msg: msg.command == "pin_centre_flyscan_plan"
    )
