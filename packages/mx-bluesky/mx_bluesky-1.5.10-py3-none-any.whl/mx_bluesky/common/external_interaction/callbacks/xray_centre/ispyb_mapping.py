from __future__ import annotations

import numpy
from dodal.devices.oav import utils as oav_utils

from mx_bluesky.common.external_interaction.ispyb.data_model import (
    DataCollectionGridInfo,
)


def construct_comment_for_gridscan(grid_info: DataCollectionGridInfo) -> str:
    assert grid_info is not None, "StoreGridScanInIspyb failed to get parameters"

    bottom_right = oav_utils.bottom_right_from_top_left(
        numpy.array(
            [grid_info.snapshot_offset_x_pixel, grid_info.snapshot_offset_y_pixel]
        ),  # type: ignore
        grid_info.steps_x,
        grid_info.steps_y,
        grid_info.dx_in_mm,
        grid_info.dy_in_mm,
        grid_info.microns_per_pixel_x,
        grid_info.microns_per_pixel_y,
    )
    return (
        "Diffraction grid scan of "
        f"{grid_info.steps_x} by "
        f"{grid_info.steps_y} images in "
        f"{(grid_info.dx_in_mm * 1e3):.1f} um by "
        f"{(grid_info.dy_in_mm * 1e3):.1f} um steps. "
        f"Top left (px): [{int(grid_info.snapshot_offset_x_pixel)},{int(grid_info.snapshot_offset_y_pixel)}], "
        f"bottom right (px): [{bottom_right[0]},{bottom_right[1]}]."
    )
