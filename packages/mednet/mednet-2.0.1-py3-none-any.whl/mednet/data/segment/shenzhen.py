# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shenzhen DataModule for computer-aided semantic sementation of lungs.

The standard digital image database for Tuberculosis was created by the
National Library of Medicine, Maryland, USA in collaboration with Shenzhen No.3
People’s Hospital, Guangdong Medical College, Shenzhen, China. The Chest X-rays
are from out-patient clinics, and were captured as part of the daily routine
using Philips DR Digital Diagnose systems.

The database includes 336 cases with manifestation of tuberculosis, and 326
normal cases.  It contains a total  of 662 images.  Image size varies for each
X-ray. It is approximately 3K x 3K. One set of ground-truth lung annotations is
available for 566 of the 662 images.

* Database references:

  * Original data :cite:p:`jaeger_two_2014`
  * Splits: :cite:p:`gaal_attention_2020`

.. important:: **Raw data organization**

    The Shenzhen_ base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at least these two
    subdirectories:

    - ``CXR_png/`` (directory containing the CXR images)
    - ``mask/`` (contains masks downloaded from `Shenzhen Annotations`_)

Data specifications:

* Raw data input (on disk):

  * PNG 8-bit RGB images issued from digital radiography machines (grayscale,
    but encoded as RGB images with "inverted" grayscale scale requiring special
    treatment).
  * Original resolution: variable width and height of 3000 x 3000 pixels or
    less
  * Samples: 566 images and associated labels

* Output image:

  * Transforms:

    * Load raw PNG with :py:mod:`PIL`
    * Torch center cropping to get square image

  * Final specifications:

    * Grayscale, encoded as a 3-plane plane tensor, 32-bit floats,
      square with varying resolutions, depending on the input image
    * Labels: Binary mask with annotated lungs (1 where lungs are; 0 otherwise)
    * Mask: Binary mask with all ones

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
    """A specialized raw-data-loader for the shenzhen dataset."""

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

        image = PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB")
        image = to_dtype(to_image(image), torch.float32, scale=True)

        target = self.target(sample)

        # use image as a base since target() can be overriden by child class
        mask = torch.ones((1, image.shape[-2], image.shape[-1]), dtype=torch.float32)

        image = tv_tensors.Image(image)
        target = tv_tensors.Mask(target)
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
    """Shenzhen database for lung segmentation.

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
