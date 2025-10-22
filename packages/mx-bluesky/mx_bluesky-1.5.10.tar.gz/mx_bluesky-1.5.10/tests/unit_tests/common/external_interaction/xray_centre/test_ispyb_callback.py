from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest
from bluesky.preprocessors import run_decorator, subs_decorator
from ophyd_async.core import init_devices
from ophyd_async.epics.core import epics_signal_rw

from mx_bluesky.common.experiment_plans.inner_plans.read_hardware import (
    read_hardware_plan,
)
from mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback import (
    GridscanISPyBCallback,
    GridscanPlane,
    _smargon_omega_to_xyxz_plane,
)
from mx_bluesky.common.parameters.constants import DocDescriptorNames
from mx_bluesky.hyperion.parameters.gridscan import GridCommonWithHyperionDetectorParams

from .....conftest import (
    EXPECTED_START_TIME,
    TEST_DATA_COLLECTION_GROUP_ID,
    TEST_DATA_COLLECTION_IDS,
    TEST_SAMPLE_ID,
    TEST_SESSION_ID,
    assert_upsert_call_with,
    mx_acquisition_from_conn,
    remap_upsert_columns,
    replace_all_tmp_paths,
)

EXPECTED_DATA_COLLECTION_3D_XY = {
    "visitid": TEST_SESSION_ID,
    "parentid": TEST_DATA_COLLECTION_GROUP_ID,
    "sampleid": TEST_SAMPLE_ID,
    "comments": "MX-Bluesky: Xray centring 1 -",
    "detectorid": 78,
    "detector_distance": 100.0,
    "exp_time": 0.1,
    "imgdir": "{tmp_data}/",
    "imgprefix": "file_name",
    "imgsuffix": "h5",
    "n_passes": 1,
    "overlap": 0,
    "start_image_number": 1,
    "wavelength": None,
    "xbeam": 150.0,
    "ybeam": 160.0,
    "synchrotron_mode": None,
    "undulator_gap1": None,
    "starttime": EXPECTED_START_TIME,
}

EXPECTED_DATA_COLLECTION_3D_XZ = EXPECTED_DATA_COLLECTION_3D_XY | {
    "comments": "MX-Bluesky: Xray centring 2 -",
}


TEST_GRID_INFO_IDS = (56, 57)
TEST_POSITION_ID = 78

EXPECTED_END_TIME = "2024-02-08 14:04:01"


@patch(
    "mx_bluesky.common.external_interaction.callbacks.common.ispyb_mapping.get_current_time_string",
    new=MagicMock(return_value=EXPECTED_START_TIME),
)
class TestXrayCentreISPyBCallback:
    def test_activity_gated_start_3d(self, mock_ispyb_conn, TestEventData, tmp_path):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )  # pyright: ignore
        mx_acq = mx_acquisition_from_conn(mock_ispyb_conn)
        assert_upsert_call_with(
            mx_acq.upsert_data_collection_group.mock_calls[0],  # pyright: ignore
            mx_acq.get_data_collection_group_params(),
            {
                "parentid": TEST_SESSION_ID,
                "experimenttype": "Mesh3D",
                "sampleid": TEST_SAMPLE_ID,
            },
        )
        assert_upsert_call_with(
            mx_acq.upsert_data_collection.mock_calls[0],
            mx_acq.get_data_collection_params(),
            replace_all_tmp_paths(EXPECTED_DATA_COLLECTION_3D_XY, tmp_path),
        )
        assert_upsert_call_with(
            mx_acq.upsert_data_collection.mock_calls[1],
            mx_acq.get_data_collection_params(),
            replace_all_tmp_paths(EXPECTED_DATA_COLLECTION_3D_XZ, tmp_path),
        )
        mx_acq.upsert_data_collection.update_dc_position.assert_not_called()
        mx_acq.upsert_data_collection.upsert_dc_grid.assert_not_called()

    @patch(
        "mx_bluesky.common.external_interaction.ispyb.ispyb_store.StoreInIspyb.update_data_collection_group_table",
    )
    def test_reason_provided_if_crystal_not_found_error(
        self, mock_update_data_collection_group_table, mock_ispyb_conn, TestEventData
    ):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )  # pyright: ignore
        mx_acq = mx_acquisition_from_conn(mock_ispyb_conn)
        callback.activity_gated_stop(
            TestEventData.test_grid_detect_and_gridscan_stop_document_with_crystal_exception
        )
        assert mx_acq.update_data_collection_append_comments.call_args_list[0] == (
            (
                TEST_DATA_COLLECTION_IDS[0],
                "DataCollection Unsuccessful reason: Diffraction not found, skipping sample.",
                " ",
            ),
        )
        assert (
            mock_update_data_collection_group_table.call_args_list[0][0][0].comments
            == "Diffraction not found, skipping sample."
        )

    def test_hardware_read_event_3d(self, mock_ispyb_conn, TestEventData):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )  # pyright: ignore
        mx_acq = mx_acquisition_from_conn(mock_ispyb_conn)
        mx_acq.upsert_data_collection_group.reset_mock()
        mx_acq.upsert_data_collection.reset_mock()
        callback.activity_gated_descriptor(
            TestEventData.test_descriptor_document_pre_data_collection
        )
        callback.activity_gated_event(
            TestEventData.test_event_document_pre_data_collection
        )
        mx_acq.upsert_data_collection_group.assert_called_once()
        expected_upsert = {
            "parentid": TEST_DATA_COLLECTION_GROUP_ID,
            "slitgaphorizontal": 0.1234,
            "slitgapvertical": 0.2345,
            "synchrotronmode": "User",
            "undulatorgap1": 1.234,
            "resolution": 1.1830593331191241,
            "wavelength": 1.11647184541378,
        }
        assert_upsert_call_with(
            mx_acq.upsert_data_collection.mock_calls[0],
            mx_acq.get_data_collection_params(),
            {"id": TEST_DATA_COLLECTION_IDS[0], **expected_upsert},
        )
        assert_upsert_call_with(
            mx_acq.upsert_data_collection.mock_calls[1],
            mx_acq.get_data_collection_params(),
            {"id": TEST_DATA_COLLECTION_IDS[1], **expected_upsert},
        )

    def test_flux_read_events_3d(self, mock_ispyb_conn, TestEventData):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )  # pyright: ignore
        mx_acq = mx_acquisition_from_conn(mock_ispyb_conn)
        callback.activity_gated_descriptor(
            TestEventData.test_descriptor_document_pre_data_collection
        )
        callback.activity_gated_event(
            TestEventData.test_event_document_pre_data_collection
        )
        mx_acq.upsert_data_collection_group.reset_mock()
        mx_acq.upsert_data_collection.reset_mock()

        callback.activity_gated_descriptor(
            TestEventData.test_descriptor_document_during_data_collection
        )
        callback.activity_gated_event(
            TestEventData.test_event_document_during_data_collection
        )

        assert_upsert_call_with(
            mx_acq.upsert_data_collection.mock_calls[0],
            mx_acq.get_data_collection_params(),
            {
                "parentid": TEST_DATA_COLLECTION_GROUP_ID,
                "id": TEST_DATA_COLLECTION_IDS[0],
                "wavelength": 1.11647184541378,
                "transmission": 100,
                "flux": 10,
                "resolution": 1.1830593331191241,
                "focal_spot_size_at_samplex": 0.05,
                "focal_spot_size_at_sampley": 0.02,
                "beamsize_at_samplex": 0.05,
                "beamsize_at_sampley": 0.02,
            },
        )
        assert_upsert_call_with(
            mx_acq.upsert_data_collection.mock_calls[1],
            mx_acq.get_data_collection_params(),
            {
                "parentid": TEST_DATA_COLLECTION_GROUP_ID,
                "id": TEST_DATA_COLLECTION_IDS[1],
                "wavelength": 1.11647184541378,
                "transmission": 100,
                "flux": 10,
                "resolution": 1.1830593331191241,
                "focal_spot_size_at_samplex": 0.05,
                "focal_spot_size_at_sampley": 0.02,
                "beamsize_at_samplex": 0.05,
                "beamsize_at_sampley": 0.02,
            },
        )
        mx_acq.update_dc_position.assert_not_called()
        mx_acq.upsert_dc_grid.assert_not_called()

    @pytest.mark.parametrize(
        "snapshot_events",
        [
            [
                "test_event_document_oav_snapshot_xy",
                "test_event_document_oav_snapshot_xz",
            ],
            [
                "test_event_document_oav_snapshot_xz",
                "test_event_document_oav_snapshot_xy",
            ],
        ],
        ids=["xy-then-xz", "xz-then-xy"],
    )
    def test_activity_gated_event_oav_snapshot_triggered(
        self, mock_ispyb_conn, TestEventData, snapshot_events: list[str]
    ):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback.activity_gated_start(
            TestEventData.test_grid_detect_and_gridscan_start_document
        )  # pyright: ignore
        mx_acq = mx_acquisition_from_conn(mock_ispyb_conn)
        mx_acq.upsert_data_collection_group.reset_mock()
        mx_acq.upsert_data_collection.reset_mock()

        callback.activity_gated_descriptor(
            TestEventData.test_descriptor_document_oav_snapshot
        )
        for event in [
            getattr(TestEventData, event_name) for event_name in snapshot_events
        ]:
            callback.activity_gated_event(event)

        dc_params = mx_acq.get_data_collection_params()
        ids_to_dc_upsert_calls = {
            c.args[0][0]: c for c in mx_acq.upsert_data_collection.mock_calls[0:2]
        }
        assert_upsert_call_with(
            ids_to_dc_upsert_calls[TEST_DATA_COLLECTION_IDS[0]],
            dc_params,
            {
                "id": TEST_DATA_COLLECTION_IDS[0],
                "parentid": TEST_DATA_COLLECTION_GROUP_ID,
                "nimages": 40 * 20,
                "xtal_snapshot1": "test_1_y",
                "xtal_snapshot2": "test_2_y",
                "xtal_snapshot3": "test_3_y",
                "axisstart": 0,
                "omegastart": 0,
                "axisend": 0,
                "axisrange": 0,
                "datacollectionnumber": 1,
                "filetemplate": "file_name_1_master.h5",
            },
        )
        mx_acq.update_data_collection_append_comments.assert_any_call(
            TEST_DATA_COLLECTION_IDS[0],
            "Diffraction grid scan of 40 by 20 "
            "images in 126.4 um by 126.4 um steps. Top left (px): [50,100], "
            "bottom right (px): [3250,1700].",
            " ",
        )
        assert_upsert_call_with(
            ids_to_dc_upsert_calls[TEST_DATA_COLLECTION_IDS[1]],
            dc_params,
            {
                "id": TEST_DATA_COLLECTION_IDS[1],
                "parentid": TEST_DATA_COLLECTION_GROUP_ID,
                "nimages": 40 * 10,
                "xtal_snapshot1": "test_1_z",
                "xtal_snapshot2": "test_2_z",
                "xtal_snapshot3": "test_3_z",
                "axisstart": 90,
                "omegastart": 90,
                "axisend": 90,
                "axisrange": 0,
                "datacollectionnumber": 2,
                "filetemplate": "file_name_2_master.h5",
            },
        )
        mx_acq.update_data_collection_append_comments.assert_any_call(
            TEST_DATA_COLLECTION_IDS[1],
            "Diffraction grid scan of 40 by 10 "
            "images in 126.4 um by 126.4 um steps. Top left (px): [50,0], "
            "bottom right (px): [3250,800].",
            " ",
        )
        ids_to_grid_upsert_calls = {
            c.args[0][1]: c for c in mx_acq.upsert_dc_grid.mock_calls[0:2]
        }
        assert_upsert_call_with(
            ids_to_grid_upsert_calls[TEST_DATA_COLLECTION_IDS[0]],
            mx_acq.get_dc_grid_params(),
            {
                "parentid": TEST_DATA_COLLECTION_IDS[0],
                "dxinmm": 0.1264,
                "dyinmm": 0.1264,
                "stepsx": 40,
                "stepsy": 20,
                "micronsperpixelx": 1.58,
                "micronsperpixely": 1.58,
                "snapshotoffsetxpixel": 50,
                "snapshotoffsetypixel": 100,
                "orientation": "horizontal",
                "snaked": True,
            },
        )
        assert_upsert_call_with(
            ids_to_grid_upsert_calls[TEST_DATA_COLLECTION_IDS[1]],
            mx_acq.get_dc_grid_params(),
            {
                "parentid": TEST_DATA_COLLECTION_IDS[1],
                "dxinmm": 0.1264,
                "dyinmm": 0.1264,
                "stepsx": 40,
                "stepsy": 10,
                "micronsperpixelx": 1.58,
                "micronsperpixely": 1.58,
                "snapshotoffsetxpixel": 50,
                "snapshotoffsetypixel": 0,
                "orientation": "horizontal",
                "snaked": True,
            },
        )

        group_dc_cols = remap_upsert_columns(
            mx_acq.get_data_collection_group_params(),
            mx_acq.upsert_data_collection_group.mock_calls[1].args[0],
        )
        assert group_dc_cols["comments"] == "Diffraction grid scan of 40 by 20 by 10."

    async def test_ispyb_callback_handles_read_hardware_in_run_engine(
        self, RE, mock_ispyb_conn, dummy_rotation_data_collection_group_info
    ):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback._handle_ispyb_hardware_read = MagicMock()
        callback._handle_ispyb_transmission_flux_read = MagicMock()
        callback.ispyb = MagicMock()
        callback.params = MagicMock()
        callback.data_collection_group_info = dummy_rotation_data_collection_group_info

        with init_devices(mock=True):
            test_readable = epics_signal_rw(str, "pv")

        @subs_decorator(callback)
        @run_decorator(
            md={
                "activate_callbacks": ["GridscanISPyBCallback"],
            },
        )
        def test_plan():
            yield from read_hardware_plan(
                [test_readable], DocDescriptorNames.HARDWARE_READ_PRE
            )
            yield from read_hardware_plan(
                [test_readable], DocDescriptorNames.HARDWARE_READ_DURING
            )

        RE(test_plan())

        callback._handle_ispyb_hardware_read.assert_called_once()
        callback._handle_ispyb_transmission_flux_read.assert_called_once()

    @patch(
        "mx_bluesky.common.external_interaction.callbacks.xray_centre.ispyb_callback.GridscanISPyBCallback._handle_oav_grid_snapshot_triggered",
    )
    @patch(
        "mx_bluesky.common.external_interaction.ispyb.ispyb_store.StoreInIspyb.update_deposition",
    )
    @patch(
        "mx_bluesky.common.external_interaction.ispyb.ispyb_store.StoreInIspyb.update_data_collection_group_table",
    )
    def test_given_event_doc_before_start_doc_received_then_exception_raised(
        self,
        mock_update_data_collection_group_table,
        mock_update_deposition,
        mock__handle_oav_grid_snapshot_triggered,
        TestEventData,
    ):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback.activity_gated_descriptor(
            TestEventData.test_descriptor_document_oav_snapshot
        )
        callback.ispyb = MagicMock()
        callback.params = MagicMock()
        callback.data_collection_group_info = None
        with pytest.raises(AssertionError) as e:
            callback.activity_gated_event(
                TestEventData.test_event_document_oav_snapshot_xy
            )

        assert "No data collection group info" in str(e.value)

    def test_ispyb_callback_clears_state_after_run_stop(
        self, TestEventData, mock_ispyb_conn
    ):
        callback = GridscanISPyBCallback(
            param_type=GridCommonWithHyperionDetectorParams
        )
        callback.active = True
        callback.start(TestEventData.test_grid_detect_and_gridscan_start_document)  # type: ignore
        callback.descriptor(TestEventData.test_descriptor_document_oav_snapshot)
        callback.event(TestEventData.test_event_document_oav_snapshot_xy)
        callback.event(TestEventData.test_event_document_oav_snapshot_xz)
        callback.start(TestEventData.test_gridscan_outer_start_document)  # type: ignore
        callback.start(TestEventData.test_do_fgs_start_document)  # type: ignore
        callback.descriptor(TestEventData.test_descriptor_document_pre_data_collection)  # type: ignore
        callback.event(TestEventData.test_event_document_pre_data_collection)
        callback.descriptor(TestEventData.test_descriptor_document_zocalo_hardware)
        callback.event(TestEventData.test_event_document_zocalo_hardware)
        callback.descriptor(
            TestEventData.test_descriptor_document_during_data_collection  # type: ignore
        )
        assert callback._grid_plane_to_id_map
        callback.stop(TestEventData.test_do_fgs_stop_document)
        callback.stop(TestEventData.test_gridscan_outer_stop_document)  # type: ignore
        callback.stop(TestEventData.test_grid_detect_and_gridscan_stop_document)
        assert not callback._grid_plane_to_id_map


@pytest.mark.parametrize(
    "omega, expected_plane",
    [
        [0, GridscanPlane.OMEGA_XY],
        [180, GridscanPlane.OMEGA_XY],
        [-180, GridscanPlane.OMEGA_XY],
        [540, GridscanPlane.OMEGA_XY],
        [90, GridscanPlane.OMEGA_XZ],
        [-90, GridscanPlane.OMEGA_XZ],
        [270, GridscanPlane.OMEGA_XZ],
        [-270, GridscanPlane.OMEGA_XZ],
        [0.999, GridscanPlane.OMEGA_XY],
        [-0.999, GridscanPlane.OMEGA_XY],
        [1.001, AssertionError],
        [-1.001, AssertionError],
        [91.001, AssertionError],
        [90.999, GridscanPlane.OMEGA_XZ],
        [89.999, GridscanPlane.OMEGA_XZ],
    ],
)
def test_smargon_omega_to_xyxz_plane(omega, expected_plane):
    expects_exception = not (isinstance(expected_plane, GridscanPlane))
    raises_or_not = (
        pytest.raises(expected_plane) if expects_exception else (nullcontext())
    )
    with raises_or_not:
        plane = _smargon_omega_to_xyxz_plane(omega)
        assert expects_exception or plane == expected_plane
