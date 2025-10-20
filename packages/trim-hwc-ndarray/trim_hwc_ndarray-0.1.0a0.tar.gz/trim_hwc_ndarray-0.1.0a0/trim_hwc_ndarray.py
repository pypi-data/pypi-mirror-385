# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from enum import Enum
from numpy import any as numpy_any, argwhere, max as numpy_max, min as numpy_min, ndarray


class Corner(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


def get_corner_color(hwc_ndarray, corner):
    # type: (ndarray, Corner) -> ndarray
    height, width, _ = hwc_ndarray.shape
    if corner == Corner.TOP_LEFT:
        return hwc_ndarray[0, 0, :]
    elif corner == Corner.TOP_RIGHT:
        return hwc_ndarray[0, width - 1, :]
    elif corner == Corner.BOTTOM_LEFT:
        return hwc_ndarray[height - 1, 0, :]
    else:
        return hwc_ndarray[height - 1, width - 1, :]


def trim_hwc_ndarray(hwc_ndarray, corner):
    # type: (ndarray, Corner) -> ndarray
    """
    Trim away border regions that match the corner color.
    Args:
        hwc_ndarray: ndarray with shape (H, W, C)
        corner: which corner's color to consider "background"
    Returns:
        New ndarray containing only the region differing in any channel from the corner color.
    """
    corner_color = get_corner_color(hwc_ndarray, corner)

    # (1, 1, C)-shaped
    # For broadcasting
    reshaped_corner_color = corner_color.reshape((1, 1, -1))

    # (H, W, C)-shaped
    channel_wise_comparison_result = hwc_ndarray != reshaped_corner_color

    # For each pixel (along last axis), check if any channel is different
    # (H, W)-shaped
    pixelwise_comparison_result = numpy_any(channel_wise_comparison_result, axis=-1)  # type: ignore

    # Find coordinates where they differ
    # (..., 2)-shaped
    differing_coordinates = argwhere(pixelwise_comparison_result)

    if not len(differing_coordinates):
        # Empty
        return hwc_ndarray[0:0, 0:0, :].copy()  # type: ignore
    else:
        inclusive_min_h = numpy_min(differing_coordinates[:, 0])
        inclusive_max_h = numpy_max(differing_coordinates[:, 0])

        inclusive_min_w = numpy_min(differing_coordinates[:, 1])
        inclusive_max_w = numpy_max(differing_coordinates[:, 1])

        return hwc_ndarray[inclusive_min_h:inclusive_max_h + 1, inclusive_min_w:inclusive_max_w + 1, :].copy()  # type: ignore
