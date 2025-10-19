# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""DRHAGIS dataset for Vessel Segmentation.

* Reference: :cite:p:`holm_dr_2017`

The DR HAGIS database has been created to aid the development of vessel
extraction algorithms suitable for retinal screening programmes. Researchers
are encouraged to test their segmentation algorithms using this database.

It should be noted that image 24 and 32 are identical, as this fundus image was
obtained from a patient exhibiting both diabetic retinopathy and age-related
macular degeneration.

The images resolutions (height x width) are one of:

* 4752x3168 px, or
* 3456x2304 px, or
* 3126x2136 px, or
* 2896x1944 px, or
* 2816x1880 px

* Protocol ``default``:

  * Training samples: 19 (including labels and masks)
  * Test samples: 20 (including labels and masks)

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
    """A specialized raw-data-loader for the Drive dataset."""

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
            A tuple containing path suffixes to the sample image, target, and mask
            to be loaded, within the dataset root folder.

        Returns
        -------
            The sample representation.
        """

        image = to_image(PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB"))
        image = to_dtype(image, torch.float32, scale=True)

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
    """DRHAGIS dataset for Vessel Segmentation.

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
