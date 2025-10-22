from unittest.mock import patch

import pytest
from bluesky.callbacks import CallbackBase
from bluesky.plan_stubs import null
from bluesky.run_engine import RunEngine
from bluesky.simulators import RunEngineSimulator, assert_message_and_return_remaining
from bluesky.utils import MsgGenerator
from dodal.devices.fast_grid_scan import ZebraFastGridScanThreeD
from dodal.devices.synchrotron import Synchrotron, SynchrotronMode
from dodal.devices.zocalo.zocalo_results import (
    ZOCALO_STAGE_GROUP,
)
from event_model.documents import Event, RunStart
from numpy.testing import assert_equal
from ophyd_async.core import init_devices
from ophyd_async.testing import set_mock_value

from mx_bluesky.common.experiment_plans.inner_plans.do_fgs import (
    kickoff_and_complete_gridscan,
)
from mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback import (
    GridscanPlane,
)
from mx_bluesky.common.parameters.constants import (
    PlanNameConstants,
)

from .....conftest import create_dummy_scan_spec


@pytest.fixture
def fgs_devices(RE, eiger):
    with init_devices(mock=True):
        synchrotron = Synchrotron()
        grid_scan_device = ZebraFastGridScanThreeD("zebra_fgs")

    return {
        "synchrotron": synchrotron,
        "grid_scan_device": grid_scan_device,
        "detector": eiger,
    }


@patch("mx_bluesky.common.experiment_plans.inner_plans.do_fgs.read_hardware_for_zocalo")
@patch(
    "mx_bluesky.common.experiment_plans.inner_plans.do_fgs.check_topup_and_wait_if_necessary"
)
def test_kickoff_and_complete_gridscan_correct_messages(
    mock_check_topup,
    mock_read_hardware,
    sim_run_engine: RunEngineSimulator,
    fgs_devices,
):
    def null_plan() -> MsgGenerator:
        yield from null()

    synchrotron = fgs_devices["synchrotron"]
    detector = fgs_devices["detector"]
    fgs_device = fgs_devices["grid_scan_device"]

    msgs = sim_run_engine.simulate_plan(
        kickoff_and_complete_gridscan(
            fgs_device,
            detector,
            synchrotron,
            scan_points=create_dummy_scan_spec(),
            plan_during_collection=null_plan,
        )
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "read"
        and msg.obj.name == "grid_scan_device-expected_images",
    )

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "read" and msg.obj.name == "eiger_cam_acquire_time",
    )

    mock_check_topup.assert_called_once()
    mock_read_hardware.assert_called_once()

    msgs = assert_message_and_return_remaining(msgs, lambda msg: msg.command == "wait")

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "wait" and msg.kwargs["group"] == ZOCALO_STAGE_GROUP,
    )

    msgs = assert_message_and_return_remaining(
        msgs, lambda msg: msg.command == "kickoff"
    )

    msgs = assert_message_and_return_remaining(msgs, lambda msg: msg.command == "wait")

    msgs = assert_message_and_return_remaining(msgs, lambda msg: msg.command == "null")

    msgs = assert_message_and_return_remaining(
        msgs,
        lambda msg: msg.command == "complete" and msg.obj.name == "grid_scan_device",
    )

    msgs = assert_message_and_return_remaining(msgs, lambda msg: msg.command == "wait")


# This test should use the real Zocalo callbacks once https://github.com/DiamondLightSource/mx-bluesky/issues/215 is done
def test_kickoff_and_complete_gridscan_with_run_engine_correct_documents(
    RE: RunEngine, fgs_devices
):
    class TestCallback(CallbackBase):
        def start(self, doc: RunStart):
            self.subplan_name = doc.get("subplan_name")
            self.omega_to_scan_spec = doc.get("omega_to_scan_spec")

        def event(self, doc: Event):
            self.event_data = list(doc.get("data").keys())
            return doc

    test_callback = TestCallback()

    RE.subscribe(test_callback)
    synchrotron = fgs_devices["synchrotron"]
    set_mock_value(synchrotron.synchrotron_mode, SynchrotronMode.DEV)
    detector = fgs_devices["detector"]
    fgs_device: ZebraFastGridScanThreeD = fgs_devices["grid_scan_device"]

    set_mock_value(fgs_device.status, 1)

    expected_scan_points = create_dummy_scan_spec()
    with patch("mx_bluesky.common.experiment_plans.inner_plans.do_fgs.bps.complete"):
        RE(
            kickoff_and_complete_gridscan(
                fgs_device,
                detector,
                synchrotron,
                scan_points=expected_scan_points,
            )
        )

    assert test_callback.subplan_name == PlanNameConstants.DO_FGS
    assert test_callback.omega_to_scan_spec
    assert_equal(
        test_callback.omega_to_scan_spec[GridscanPlane.OMEGA_XY],
        expected_scan_points[0],
    )
    assert_equal(
        test_callback.omega_to_scan_spec[GridscanPlane.OMEGA_XZ],
        expected_scan_points[1],
    )
    assert len(test_callback.event_data) == 1
    assert test_callback.event_data[0] == "eiger_odin_file_writer_id"
