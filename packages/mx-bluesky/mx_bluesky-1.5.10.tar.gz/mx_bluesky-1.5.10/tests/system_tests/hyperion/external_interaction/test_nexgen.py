import os
import re
import subprocess
from datetime import datetime
from os import environ
from unittest.mock import MagicMock, patch

import bluesky.preprocessors as bpp
import pytest
from bluesky.run_engine import RunEngine

from mx_bluesky.common.experiment_plans.inner_plans.read_hardware import (
    standard_read_hardware_during_collection,
)
from mx_bluesky.hyperion.experiment_plans.rotation_scan_plan import (
    RotationScanComposite,
)
from mx_bluesky.hyperion.external_interaction.callbacks.rotation.nexus_callback import (
    RotationNexusFileCallback,
)
from mx_bluesky.hyperion.parameters.constants import CONST
from mx_bluesky.hyperion.parameters.rotation import SingleRotationScan

from ....conftest import extract_metafile, raw_params_from_file

DOCKER = environ.get("DOCKER", "docker")


@pytest.fixture
def test_params(tmp_path):
    param_dict = raw_params_from_file(
        "tests/test_data/parameter_json_files/good_test_rotation_scan_parameters.json",
        tmp_path,
    )
    params = SingleRotationScan(**param_dict)
    params.demand_energy_ev = 12700
    params.scan_width_deg = 360
    params.storage_directory = "tests/test_data"
    params.x_start_um = 0
    params.y_start_um = 0
    params.z_start_um = 0
    params.exposure_time_s = 0.004
    return params


@pytest.mark.parametrize(
    "test_data_directory, prefix, reference_file",
    [
        (
            "tests/test_data/nexus_files/rotation",
            "ins_8_5",
            "ins_8_5_expected_output.txt",
        ),
        (
            "tests/test_data/nexus_files/rotation_unicode_metafile",
            "ins_8_5",
            "ins_8_5_expected_output.txt",
        ),
    ],
)
@patch(
    "mx_bluesky.common.external_interaction.nexus.nexus_utils.time.time",
    new=MagicMock(
        return_value=datetime.fromisoformat("2024-05-03T17:59:43Z").timestamp()
    ),
)
@pytest.mark.system_test
def test_rotation_nexgen(
    test_params: SingleRotationScan,
    tmpdir,
    fake_create_rotation_devices: RotationScanComposite,
    test_data_directory,
    prefix,
    reference_file,
):
    meta_file = f"{prefix}_meta.h5.gz"
    test_params.file_name = prefix
    test_params.storage_directory = f"{tmpdir}"
    run_number = test_params.detector_params.run_number

    extract_metafile(
        f"{test_data_directory}/{meta_file}", f"{tmpdir}/{prefix}_{run_number}_meta.h5"
    )

    fake_create_rotation_devices.eiger.bit_depth.sim_put(32)  # type: ignore

    RE = RunEngine({})
    RE(
        _fake_rotation_scan(
            test_params, RotationNexusFileCallback(), fake_create_rotation_devices
        )
    )

    master_file = f"{tmpdir}/{prefix}_{run_number}_master.h5"
    _check_nexgen_output_passes_imginfo(
        master_file, f"{test_data_directory}/{reference_file}"
    )


FILE_PATTERN = re.compile("^ ################# File = (.*)")

HEADER_PATTERN = re.compile("^ ===== Header information:")

DATE_PATTERN = re.compile("^ date                                = (.*)")


def _check_nexgen_output_passes_imginfo(test_file, reference_file):
    stdout, stderr = _run_imginfo(test_file)
    assert stderr == ""
    it_actual_lines = iter(stdout.split("\n"))
    i = 0
    try:
        with open(reference_file) as f:
            while True:
                i += 1
                expected_line = f.readline().rstrip("\n")
                actual_line = next(it_actual_lines)
                if FILE_PATTERN.match(actual_line):
                    continue
                if HEADER_PATTERN.match(actual_line):
                    break
                assert actual_line == expected_line, (
                    f"Header line {i} didn't match contents of {reference_file}: {actual_line} <-> {expected_line}"
                )

            while True:
                i += 1
                expected_line = f.readline().rstrip("\n")
                actual_line = next(it_actual_lines)
                assert actual_line == expected_line, (
                    f"Header line {i} didn't match contents of {reference_file}: {actual_line} <-> {expected_line}"
                )

    except StopIteration:
        pass

        # assert stdout == expected


def _run_imginfo(filename):
    imginfo_path = os.environ.get("IMGINFO_PATH", "utility_scripts/run_imginfo.sh")
    process = subprocess.run(
        # This file is provided in the system test docker image
        [imginfo_path, filename],
        text=True,
        capture_output=True,
    )
    assert process.returncode != 2, "imginfo is not available"
    assert process.returncode == 0, (
        f"imginfo failed with returncode {process.returncode}"
    )

    return process.stdout, process.stderr


def _fake_rotation_scan(
    parameters: SingleRotationScan,
    subscription: RotationNexusFileCallback,
    rotation_devices: RotationScanComposite,
):
    @bpp.subs_decorator(subscription)
    @bpp.set_run_key_decorator("rotation_scan_with_cleanup_and_subs")
    @bpp.run_decorator(  # attach experiment metadata to the start document
        md={
            "subplan_name": CONST.PLAN.ROTATION_OUTER,
            "mx_bluesky_parameters": parameters.model_dump_json(),
            "activate_callbacks": "RotationNexusFileCallback",
        }
    )
    def plan():
        yield from standard_read_hardware_during_collection(
            rotation_devices.aperture_scatterguard,
            rotation_devices.attenuator,
            rotation_devices.flux,
            rotation_devices.dcm,
            rotation_devices.eiger,
        )

    return plan()
