from pathlib import Path
from unittest.mock import MagicMock, call, patch

import numpy as np
import pytest
from bluesky.run_engine import RunEngine
from bluesky.simulators import assert_message_and_return_remaining
from bluesky.utils import Msg
from dodal.devices.aperturescatterguard import (
    ApertureValue,
)
from dodal.devices.zocalo.zocalo_results import _NO_SAMPLE_ID
from ophyd.sim import NullStatus
from ophyd.status import Status
from ophyd_async.fastcs.panda import DatasetTable, PandaHdf5DatasetType
from ophyd_async.testing import set_mock_value

from mx_bluesky.common.experiment_plans.common_flyscan_xray_centre_plan import (
    BeamlineSpecificFGSFeatures,
    FlyScanEssentialDevices,
    common_flyscan_xray_centre,
)
from mx_bluesky.common.external_interaction.callbacks.common.logging_callback import (
    VerbosePlanExecutionLoggingCallback,
)
from mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback import (
    GridscanISPyBCallback,
)
from mx_bluesky.common.external_interaction.callbacks.xray_centre.nexus_callback import (
    GridscanNexusFileCallback,
)
from mx_bluesky.common.parameters.constants import (
    DeviceSettingsConstants,
)
from mx_bluesky.hyperion.experiment_plans.hyperion_flyscan_xray_centre_plan import (
    SmargonSpeedException,
)
from mx_bluesky.hyperion.parameters.device_composites import (
    HyperionFlyScanXRayCentreComposite,
)
from mx_bluesky.hyperion.parameters.gridscan import (
    HyperionSpecifiedThreeDGridScan,
)
from tests.conftest import (
    RunEngineSimulator,
)

from ....conftest import TEST_RESULT_LARGE, TestData, simulate_xrc_result
from ...conftest import (
    mock_zocalo_trigger,
    modified_store_grid_scan_mock,
)

ReWithSubs = tuple[RunEngine, tuple[GridscanNexusFileCallback, GridscanISPyBCallback]]


class CompleteException(Exception):
    # To avoid having to run through the entire plan during tests
    pass


def _custom_msg(command_name: str):
    return lambda *args, **kwargs: iter([Msg(command_name)])


@pytest.fixture
def fgs_composite_with_panda_pcap(
    hyperion_flyscan_xrc_composite: HyperionFlyScanXRayCentreComposite,
):
    capture_table = DatasetTable(name=["name"], dtype=[PandaHdf5DatasetType.FLOAT_64])
    set_mock_value(hyperion_flyscan_xrc_composite.panda.data.datasets, capture_table)

    return hyperion_flyscan_xrc_composite


@patch(
    "mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback.StoreInIspyb",
    modified_store_grid_scan_mock,
)
class TestFlyscanXrayCentrePlan:
    @patch(
        "dodal.devices.aperturescatterguard.ApertureScatterguard._safe_move_within_datacollection_range",
        return_value=NullStatus(),
    )
    @patch(
        "mx_bluesky.common.experiment_plans.common_flyscan_xray_centre_plan.run_gridscan",
        autospec=True,
    )
    @patch(
        "mx_bluesky.common.experiment_plans.change_aperture_then_move_plan.move_x_y_z",
        autospec=True,
    )
    @pytest.mark.skip(
        reason="TODO mx-bluesky 231 aperture size should be determined from absolute size not box size"
    )
    def test_results_adjusted_and_passed_to_move_xyz(
        self,
        move_x_y_z: MagicMock,
        move_aperture: MagicMock,
        run_gridscan: MagicMock,
        hyperion_flyscan_xrc_composite: HyperionFlyScanXRayCentreComposite,
        hyperion_fgs_params: HyperionSpecifiedThreeDGridScan,
        RE_with_subs: ReWithSubs,
        beamline_specific: BeamlineSpecificFGSFeatures,
    ):
        RE, _ = RE_with_subs
        RE.subscribe(VerbosePlanExecutionLoggingCallback())

        for result in [
            TestData.test_result_large,
            TestData.test_result_medium,
            TestData.test_result_small,
        ]:
            mock_zocalo_trigger(hyperion_flyscan_xrc_composite.zocalo, result)
            RE(
                common_flyscan_xray_centre(
                    hyperion_flyscan_xrc_composite,
                    hyperion_fgs_params,
                    beamline_specific,
                )
            )

        aperture_scatterguard = hyperion_flyscan_xrc_composite.aperture_scatterguard
        large = aperture_scatterguard._loaded_positions[ApertureValue.LARGE]
        medium = aperture_scatterguard._loaded_positions[ApertureValue.MEDIUM]
        ap_call_large = call(large, ApertureValue.LARGE)
        ap_call_medium = call(medium, ApertureValue.MEDIUM)

        move_aperture.assert_has_calls([ap_call_large, ap_call_large, ap_call_medium])

        mv_to_centre = call(
            hyperion_flyscan_xrc_composite.smargon,
            0.05,
            pytest.approx(0.15),
            0.25,
            wait=True,
        )
        move_x_y_z.assert_has_calls(
            [mv_to_centre, mv_to_centre, mv_to_centre], any_order=True
        )

    @patch(
        "mx_bluesky.common.experiment_plans.common_flyscan_xray_centre_plan.run_gridscan",
        autospec=True,
    )
    @patch(
        "mx_bluesky.common.experiment_plans.change_aperture_then_move_plan.move_x_y_z",
        autospec=True,
    )
    async def test_when_gridscan_finished_then_dev_shm_disabled(
        self,
        move_xyz: MagicMock,
        run_gridscan: MagicMock,
        sim_run_engine: RunEngineSimulator,
        hyperion_fgs_params: HyperionSpecifiedThreeDGridScan,
        hyperion_flyscan_xrc_composite: FlyScanEssentialDevices,
        beamline_specific: BeamlineSpecificFGSFeatures,
    ):
        hyperion_flyscan_xrc_composite.eiger.odin.fan.dev_shm_enable.sim_put(1)  # type: ignore
        zocalo = hyperion_flyscan_xrc_composite.zocalo
        sim_run_engine.add_read_handler_for(
            zocalo.centre_of_mass, [np.array([6.0, 6.0, 6.0])]
        )
        sim_run_engine.add_read_handler_for(zocalo.max_voxel, [np.array([5, 5, 5])])
        sim_run_engine.add_read_handler_for(zocalo.max_count, [123456])
        sim_run_engine.add_read_handler_for(zocalo.n_voxels, [321])
        sim_run_engine.add_read_handler_for(zocalo.total_count, [999999])
        sim_run_engine.add_read_handler_for(
            zocalo.bounding_box, [np.array([[3, 3, 3], [9, 9, 9]])]
        )
        sim_run_engine.add_read_handler_for(zocalo.sample_id, [_NO_SAMPLE_ID])
        msgs = sim_run_engine.simulate_plan(
            common_flyscan_xray_centre(
                hyperion_flyscan_xrc_composite,
                hyperion_fgs_params,
                beamline_specific,
            )
        )

        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "set"
            and msg.obj is hyperion_flyscan_xrc_composite.eiger.odin.fan.dev_shm_enable
            and msg.args[0] == 0,
        )
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "wait"
            and msg.kwargs["group"] == msgs[0].kwargs["group"],
        )

    @patch(
        "mx_bluesky.common.experiment_plans.common_flyscan_xray_centre_plan.kickoff_and_complete_gridscan",
    )
    def test_if_smargon_speed_over_limit_then_log_error(
        self,
        mock_kickoff_and_complete: MagicMock,
        fgs_params_use_panda: HyperionSpecifiedThreeDGridScan,
        hyperion_flyscan_xrc_composite: FlyScanEssentialDevices,
        beamline_specific: BeamlineSpecificFGSFeatures,
        RE: RunEngine,
    ):
        fgs_params_use_panda.x_step_size_um = 10000
        fgs_params_use_panda.detector_params.exposure_time_s = 0.01

        # this exception should only be raised if we're using the panda
        with pytest.raises(SmargonSpeedException):
            RE(
                common_flyscan_xray_centre(
                    hyperion_flyscan_xrc_composite,
                    fgs_params_use_panda,
                    beamline_specific,
                )
            )

    @patch(
        "mx_bluesky.hyperion.device_setup_plans.setup_panda.arm_panda_for_gridscan",
        new=MagicMock(side_effect=_custom_msg("arm_panda")),
    )
    @patch(
        "mx_bluesky.hyperion.experiment_plans.hyperion_flyscan_xray_centre_plan.disarm_panda_for_gridscan",
        new=MagicMock(side_effect=_custom_msg("disarm_panda")),
    )
    @patch(
        "mx_bluesky.common.experiment_plans.common_flyscan_xray_centre_plan.run_gridscan",
        new=MagicMock(side_effect=_custom_msg("do_gridscan")),
    )
    @patch(
        "mx_bluesky.hyperion.experiment_plans.hyperion_flyscan_xray_centre_plan.set_panda_directory",
        side_effect=_custom_msg("set_panda_directory"),
    )
    @patch("mx_bluesky.hyperion.device_setup_plans.setup_panda.load_panda_from_yaml")
    def test_flyscan_xray_centre_sets_directory_stages_arms_disarms_unstages_the_panda(
        self,
        mock_load_panda: MagicMock,
        mock_set_panda_directory: MagicMock,
        done_status: Status,
        fgs_params_use_panda: HyperionSpecifiedThreeDGridScan,
        fgs_composite_with_panda_pcap: HyperionFlyScanXRayCentreComposite,
        sim_run_engine: RunEngineSimulator,
        beamline_specific: BeamlineSpecificFGSFeatures,
        tmp_path: Path,
    ):
        sim_run_engine.add_handler("unstage", lambda _: done_status)
        sim_run_engine.add_read_handler_for(
            fgs_composite_with_panda_pcap.smargon.x.max_velocity, 10
        )
        simulate_xrc_result(
            sim_run_engine, fgs_composite_with_panda_pcap.zocalo, TEST_RESULT_LARGE
        )

        msgs = sim_run_engine.simulate_plan(
            common_flyscan_xray_centre(
                fgs_composite_with_panda_pcap, fgs_params_use_panda, beamline_specific
            )
        )

        mock_set_panda_directory.assert_called_with(tmp_path / "xraycentring/123456")
        mock_load_panda.assert_called_once_with(
            DeviceSettingsConstants.PANDA_FLYSCAN_SETTINGS_DIR,
            DeviceSettingsConstants.PANDA_FLYSCAN_SETTINGS_FILENAME,
            fgs_composite_with_panda_pcap.panda,
        )

        msgs = assert_message_and_return_remaining(
            msgs, lambda msg: msg.command == "set_panda_directory"
        )
        msgs = assert_message_and_return_remaining(
            msgs, lambda msg: msg.command == "stage" and msg.obj.name == "panda"
        )
        msgs = assert_message_and_return_remaining(
            msgs, lambda msg: msg.command == "arm_panda"
        )
        msgs = assert_message_and_return_remaining(
            msgs, lambda msg: msg.command == "do_gridscan"
        )
        msgs = assert_message_and_return_remaining(
            msgs, lambda msg: msg.command == "disarm_panda"
        )
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "unstage"
            and msg.obj.name == "panda"
            and msg.kwargs["group"] == "panda_flyscan_tidy",
        )
        msgs = assert_message_and_return_remaining(
            msgs,
            lambda msg: msg.command == "wait"
            and msg.kwargs["group"] == "panda_flyscan_tidy",
        )
