# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Data loading code."""

import numpy.typing
import PIL.Image


def remove_black_borders(
    img: PIL.Image.Image,
    threshold: int = 0,
) -> tuple[PIL.Image.Image, numpy.typing.NDArray[numpy.bool_]]:
    """Remove black borders of CXR.

    Parameters
    ----------
    img
        A PIL image.
    threshold
        Threshold value from which borders are considered black.
        Defaults to 0.

    Returns
    -------
        A PIL image with black borders removed, and the mask used to remove the
        black borders from the image, that can be subsequently used to process
        other related image information (e.g. annotation masks).
    """

    img_array = numpy.asarray(img)

    if len(img_array.shape) == 2:  # single channel
        mask = numpy.asarray(img_array) > threshold
        return PIL.Image.fromarray(
            img_array[numpy.ix_(mask.any(1), mask.any(0))],
        ), mask

    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        r_mask = img_array[:, :, 0] > threshold
        g_mask = img_array[:, :, 1] > threshold
        b_mask = img_array[:, :, 2] > threshold

        mask = r_mask | g_mask | b_mask
        return PIL.Image.fromarray(
            img_array[numpy.ix_(mask.any(1), mask.any(0))],
        ), mask

    raise NotImplementedError
