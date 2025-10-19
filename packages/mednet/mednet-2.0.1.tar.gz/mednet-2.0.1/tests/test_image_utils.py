# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for image utilities."""

import numpy
import PIL.Image

from mednet.data.image_utils import remove_black_borders


def test_remove_black_borders(datadir):
    # Get a raw sample with black border
    data_file = str(datadir / "raw_with_black_border.png")
    raw_with_black_border = PIL.Image.open(data_file)

    # Remove the black border
    raw_rbb_removed, _ = remove_black_borders(raw_with_black_border)

    # Get the same sample without black border
    data_file_2 = str(datadir / "raw_without_black_border.png")
    raw_without_black_border = PIL.Image.open(data_file_2)

    # Compare both
    raw_rbb_removed = numpy.asarray(raw_rbb_removed)
    raw_without_black_border = numpy.asarray(raw_without_black_border)

    numpy.testing.assert_array_equal(raw_without_black_border, raw_rbb_removed)


def test_load_pil_16bit(datadir):
    # If the ratio is higher 0.5, image is probably clipped

    image = PIL.Image.open(datadir / "16bits.png")
    array = numpy.array(image).astype(numpy.float32) / 65535

    count_pixels = numpy.count_nonzero(array)
    count_max_value = numpy.count_nonzero(array == array.max())

    assert count_max_value / count_pixels < 0.5
