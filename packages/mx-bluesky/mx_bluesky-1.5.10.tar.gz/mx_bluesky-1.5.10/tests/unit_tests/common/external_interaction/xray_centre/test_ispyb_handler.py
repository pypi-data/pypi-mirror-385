from unittest.mock import MagicMock, patch

import pytest
from graypy import GELFTCPHandler

from mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback import (
    GridscanISPyBCallback,
)
from mx_bluesky.common.external_interaction.ispyb.ispyb_store import (
    IspybIds,
    StoreInIspyb,
)
from mx_bluesky.common.utils.log import ISPYB_ZOCALO_CALLBACK_LOGGER
from mx_bluesky.hyperion.external_interaction.callbacks.__main__ import setup_logging
from mx_bluesky.hyperion.parameters.gridscan import GridCommonWithHyperionDetectorParams

from .....conftest import TestData

DC_IDS = (1, 2)
DCG_ID = 4
DC_GRID_IDS = (11, 12)
td = TestData()


def mock_store_in_ispyb(config, *args, **kwargs) -> StoreInIspyb:
    mock = MagicMock(spec=StoreInIspyb)
    mock.end_deposition = MagicMock(return_value=None)
    mock.begin_deposition = MagicMock(
        return_value=IspybIds(
            data_collection_group_id=DCG_ID, data_collection_ids=DC_IDS
        )
    )
    mock.update_deposition = MagicMock(
        return_value=IspybIds(
            data_collection_group_id=DCG_ID,
            data_collection_ids=DC_IDS,
            grid_ids=DC_GRID_IDS,
        )
    )
    mock.append_to_comment = MagicMock()
    return mock


@patch(
    "mx_bluesky.common.external_interaction.callbacks.common.ispyb_mapping.get_current_time_string",
    MagicMock(return_value=td.DUMMY_TIME_STRING),
)
@patch(
    "mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback.StoreInIspyb",
    mock_store_in_ispyb,
)
class TestXrayCentreIspybHandler:
    def test_fgs_failing_results_in_bad_run_status_in_ispyb(self, TestEventData):
        ispyb_handler = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        ispyb_handler.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_pre_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_pre_data_collection
        )
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_during_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_during_data_collection  # pyright: ignore
        )
        ispyb_handler.activity_gated_stop(
            TestEventData.test_grid_detect_and_gridscan_failed_stop_document
        )

        ispyb_handler.ispyb.end_deposition.assert_called_once_with(  # type: ignore
            IspybIds(
                data_collection_group_id=DCG_ID,
                data_collection_ids=DC_IDS,
                grid_ids=DC_GRID_IDS,
            ),
            "fail",
            "could not connect to devices",
        )

    def test_fgs_raising_no_exception_results_in_good_run_status_in_ispyb(
        self, TestEventData
    ):
        ispyb_handler = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        ispyb_handler.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )
        ispyb_handler.activity_gated_start(TestEventData.test_do_fgs_start_document)
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_pre_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_pre_data_collection
        )
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_during_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_during_data_collection
        )
        ispyb_handler.activity_gated_stop(TestEventData.test_do_fgs_stop_document)
        ispyb_handler.activity_gated_stop(
            TestEventData.test_grid_detect_and_gridscan_stop_document
        )
        ispyb_handler.ispyb.end_deposition.assert_called_once_with(  # type: ignore
            IspybIds(
                data_collection_group_id=DCG_ID,
                data_collection_ids=DC_IDS,
                grid_ids=DC_GRID_IDS,
            ),
            "success",
            "",
        )

    @pytest.mark.skip_log_setup
    def test_given_ispyb_callback_started_writing_to_ispyb_when_messages_logged_then_they_contain_dcgid(
        self, TestEventData
    ):
        setup_logging(True)
        gelf_handler: MagicMock = next(
            filter(
                lambda h: isinstance(h, GELFTCPHandler),
                ISPYB_ZOCALO_CALLBACK_LOGGER.handlers,  # type: ignore
            )
        )
        gelf_handler.emit = MagicMock()

        ispyb_handler = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        ispyb_handler.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_pre_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_pre_data_collection
        )
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_during_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_during_data_collection
        )

        ISPYB_ZOCALO_CALLBACK_LOGGER.info("test")
        latest_record = gelf_handler.emit.call_args.args[-1]
        assert latest_record.dc_group_id == DCG_ID

    @pytest.mark.skip_log_setup
    def test_given_ispyb_callback_finished_writing_to_ispyb_when_messages_logged_then_they_do_not_contain_dcgid(
        self, TestEventData
    ):
        setup_logging(True)
        gelf_handler: MagicMock = next(
            filter(
                lambda h: isinstance(h, GELFTCPHandler),
                ISPYB_ZOCALO_CALLBACK_LOGGER.handlers,  # type: ignore
            )
        )
        gelf_handler.emit = MagicMock()

        ispyb_handler = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        ispyb_handler.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_pre_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_pre_data_collection
        )
        ispyb_handler.activity_gated_descriptor(
            TestEventData.test_descriptor_document_during_data_collection
        )
        ispyb_handler.activity_gated_event(
            TestEventData.test_event_document_during_data_collection
        )
        ispyb_handler.activity_gated_stop(
            TestEventData.test_grid_detect_and_gridscan_failed_stop_document
        )

        ISPYB_ZOCALO_CALLBACK_LOGGER.info("test")
        latest_record = gelf_handler.emit.call_args.args[-1]
        assert not hasattr(latest_record, "dc_group_id")

    @patch(
        "mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback.time",
        side_effect=[2, 100],
    )
    def test_given_fgs_plan_finished_when_zocalo_results_event_then_expected_comment_deposited(
        self, mock_time, dummy_rotation_data_collection_group_info, TestEventData
    ):
        ispyb_handler = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams,
        )

        ispyb_handler.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )  # type:ignore

        ispyb_handler.activity_gated_start(TestEventData.test_do_fgs_start_document)  # type:ignore
        ispyb_handler.activity_gated_stop(TestEventData.test_do_fgs_stop_document)
        ispyb_handler.activity_gated_stop(
            TestEventData.test_grid_detect_and_gridscan_stop_document
        )

        ispyb_handler.data_collection_group_info = (
            dummy_rotation_data_collection_group_info
        )
        assert (
            ispyb_handler.ispyb.append_to_comment.call_args.args[1]  # type:ignore
            == "Zocalo processing took 98.00 s."
        )
