import json
from pathlib import Path
from unittest.mock import patch

import pytest
from dodal.devices.aperturescatterguard import ApertureValue
from pydantic import ValidationError

from mx_bluesky.common.external_interaction.callbacks.common.grid_detection_callback import (
    GridParamUpdate,
)
from mx_bluesky.common.parameters.constants import GridscanParamConstants
from mx_bluesky.hyperion.parameters.gridscan import (
    HyperionSpecifiedThreeDGridScan,
    OddYStepsException,
)
from mx_bluesky.hyperion.parameters.load_centre_collect import LoadCentreCollect
from mx_bluesky.hyperion.parameters.robot_load import RobotLoadThenCentre
from mx_bluesky.hyperion.parameters.rotation import SingleRotationScan

from ....conftest import raw_params_from_file


@pytest.fixture
def load_centre_collect_params_with_panda(tmp_path, request):
    with patch(
        "mx_bluesky.common.parameters.constants.GDA_DOMAIN_PROPERTIES_PATH",
        new="tests/test_data/test_domain_properties_with_panda",
    ):
        params = raw_params_from_file(
            "tests/test_data/parameter_json_files/good_test_load_centre_collect_params.json",
            tmp_path,
        )
        params["features"]["use_panda_for_gridscan"] = True
        if params_dict := getattr(request, "param", {}):
            for k, v in params_dict.items():
                params.setdefault("features", {})[k] = v
        return LoadCentreCollect(**params)


@pytest.fixture()
def minimal_3d_gridscan_params():
    return {
        "sample_id": 123,
        "x_start_um": 0.123,
        "y_start_um": 0.777,
        "z_start_um": 0.05,
        "parameter_model_version": "5.0.0",
        "visit": "cm12345",
        "file_name": "test_file_name",
        "y2_start_um": 2,
        "z2_start_um": 2,
        "x_steps": 5,
        "y_steps": 7,
        "z_steps": 9,
        "storage_directory": "/tmp/dls/i03/data/2024/cm31105-4/xraycentring/123456/",
    }


def get_empty_grid_parameters() -> GridParamUpdate:
    return {
        "x_start_um": 1,
        "y_start_um": 1,
        "y2_start_um": 1,
        "z_start_um": 1,
        "z2_start_um": 1,
        "x_steps": 1,
        "y_steps": 1,
        "z_steps": 1,
        "x_step_size_um": 1,
        "y_step_size_um": 1,
        "z_step_size_um": 1,
    }


def test_minimal_3d_gridscan_params(minimal_3d_gridscan_params):
    test_params = HyperionSpecifiedThreeDGridScan(**minimal_3d_gridscan_params)
    assert {"sam_x", "sam_y", "sam_z"} == set(test_params.scan_points.keys())
    assert test_params.scan_indices == [0, 35]
    assert test_params.num_images == (5 * 7 + 5 * 9)
    assert test_params.exposure_time_s == GridscanParamConstants.EXPOSURE_TIME_S


def test_cant_do_panda_fgs_with_odd_y_steps(minimal_3d_gridscan_params):
    test_params = HyperionSpecifiedThreeDGridScan(**minimal_3d_gridscan_params)
    with pytest.raises(OddYStepsException):
        _ = test_params.panda_FGS_params
    assert test_params.FGS_params


def test_serialise_deserialise(minimal_3d_gridscan_params):
    test_params = HyperionSpecifiedThreeDGridScan(**minimal_3d_gridscan_params)
    serialised = json.loads(test_params.model_dump_json())
    deserialised = HyperionSpecifiedThreeDGridScan(**serialised)
    assert deserialised.demand_energy_ev is None
    assert deserialised.visit == "cm12345"
    assert deserialised.x_start_um == 0.123


@pytest.mark.parametrize(
    "version, valid",
    [
        ("4.3.0", False),
        ("6.3.7", False),
        ("5.0.0", True),
        ("5.3.0", True),
        ("5.3.7", True),
    ],
)
def test_param_version(minimal_3d_gridscan_params, version: str, valid: bool):
    minimal_3d_gridscan_params["parameter_model_version"] = version
    if valid:
        _ = HyperionSpecifiedThreeDGridScan(**minimal_3d_gridscan_params)
    else:
        with pytest.raises(ValidationError):
            _ = HyperionSpecifiedThreeDGridScan(**minimal_3d_gridscan_params)


def test_robot_load_then_centre_params():
    params = {
        "parameter_model_version": "5.0.0",
        "sample_id": 123456,
        "visit": "cm12345",
        "file_name": "file_name",
        "storage_directory": "/tmp/dls/i03/data/2024/cm31105-4/xraycentring/123456/",
    }
    params["detector_distance_mm"] = 200
    test_params = RobotLoadThenCentre(**params)
    assert test_params.detector_params


def test_default_snapshot_path(minimal_3d_gridscan_params):
    gridscan_params = HyperionSpecifiedThreeDGridScan(**minimal_3d_gridscan_params)
    assert gridscan_params.snapshot_directory == Path(
        "/tmp/dls/i03/data/2024/cm31105-4/xraycentring/123456/snapshots"
    )

    params_with_snapshot_path = dict(minimal_3d_gridscan_params)
    params_with_snapshot_path["snapshot_directory"] = "/tmp/my_snapshots"

    gridscan_params_with_snapshot_path = HyperionSpecifiedThreeDGridScan(
        **params_with_snapshot_path
    )
    assert gridscan_params_with_snapshot_path.snapshot_directory == Path(
        "/tmp/my_snapshots"
    )


def test_osc_is_used(tmp_path):
    raw_params = raw_params_from_file(
        "tests/test_data/parameter_json_files/good_test_rotation_scan_parameters.json",
        tmp_path,
    )
    for osc in [0.001, 0.05, 0.1, 0.2, 0.75, 1, 1.43]:
        raw_params["rotation_increment_deg"] = osc
        params = SingleRotationScan(**raw_params)
        assert params.rotation_increment_deg == osc
        assert params.num_images == int(params.scan_width_deg / osc)


def test_selected_aperture_uses_default(tmp_path):
    raw_params = raw_params_from_file(
        "tests/test_data/parameter_json_files/good_test_rotation_scan_parameters.json",
        tmp_path,
    )
    raw_params["selected_aperture"] = None
    params = SingleRotationScan(**raw_params)
    assert params.selected_aperture == ApertureValue.LARGE


@pytest.mark.parametrize(
    "enable_gpu",
    [
        True,
        False,
    ],
)
@patch("mx_bluesky.common.parameters.components.os")
def test_dev_shm_enabled_if_use_gpu_results_enabled(
    _, enable_gpu, minimal_3d_gridscan_params
):
    minimal_3d_gridscan_params["detector_distance_mm"] = 100
    properties_path = (
        "tests/test_data/test_domain_properties_with_no_gpu"
        if not enable_gpu
        else "tests/test_data/test_domain_properties"
    )
    with patch(
        "mx_bluesky.common.external_interaction.config_server.GDA_DOMAIN_PROPERTIES_PATH",
        new=properties_path,
    ):
        grid_scan = HyperionSpecifiedThreeDGridScan(**minimal_3d_gridscan_params)
        assert grid_scan.detector_params.enable_dev_shm == enable_gpu
