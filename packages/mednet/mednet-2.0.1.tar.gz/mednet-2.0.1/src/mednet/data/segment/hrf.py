# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""HRF dataset for vessel segmentation.

The database includes 15 images of each healthy, diabetic retinopathy (DR), and
glaucomatous eyes.  It contains a total  of 45 eye fundus images with a
resolution of 3304 x 2336. One set of ground-truth vessel annotations is
available.

* Database references:

  * Original data: :cite:p:`budai_robust_2013`
  * Split reference: :cite:p:`orlando_discriminatively_2017`

Data specifications:

* Raw data input (on disk):

  * Original images encoded in (color) JPG format, with resolution 3504 x 2336
    pixels (width x height).
  * Vessel labels: encoded as TIFF files, with the same resolution as original
    images.
  * Total samples: 45

* Output sample:

  * Image: Load raw JPG images with :py:mod:`PIL`, with auto-conversion to RGB.
  * Vessel annotations: Load annotations with :py:mod:`PIL`, with
    auto-conversion to mode ``1`` with no dithering.

The ``default`` split contains 15 images for training and 30 for testing.

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import PIL.Image
import torch
from torchvision import tv_tensors
from torchvision.transforms.v2.functional import to_dtype, to_image

from ...models.transforms import crop_image_to_mask
from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name to refer to this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the drishtigs1hrf dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing the
            sample label.

        Returns
        -------
            The sample representation.
        """

        image = PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB")
        image = to_dtype(to_image(image), torch.float32, scale=True)

        target = self.target(sample)

        mask = PIL.Image.open(self.datadir / sample[2]).convert(mode="1", dither=None)
        mask = to_dtype(to_image(mask), torch.float32, scale=True)

        image = tv_tensors.Image(crop_image_to_mask(image, mask))
        target = tv_tensors.Mask(crop_image_to_mask(target, mask))
        mask = tv_tensors.Mask(mask)

        return dict(image=image, target=target, mask=mask, name=sample[0])

    def target(self, sample: typing.Any) -> torch.Tensor:
        """Load only sample target from its raw representation.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
            The label corresponding to the specified sample, encapsulated as a
            torch float tensor.
        """

        target = PIL.Image.open(self.datadir / sample[1]).convert(mode="1", dither=None)
        return to_dtype(to_image(target), torch.float32, scale=True)


class DataModule(CachingDataModule):
    """HRF dataset for vessel segmentation.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    """

    def __init__(self, split_path: pathlib.Path | importlib.resources.abc.Traversable):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="segmentation",
            num_classes=1,
        )
