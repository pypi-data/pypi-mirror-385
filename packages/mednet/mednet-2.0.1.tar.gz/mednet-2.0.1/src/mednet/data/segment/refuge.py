# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""REFUGE for optic disc and cup segmentation.

The dataset consists of 1200 color fundus photographs, created for a MICCAI
challenge. The goal of the challenge is to evaluate and compare automated
algorithms for glaucoma detection and optic disc/cup segmentation on a common
dataset of retinal fundus images.

* Database reference (including train/dev/test split): :cite:p:`noauthor_refuge_nodate`

.. warning::

   The original directory ``Training400/AMD`` in REFUGE is considered to be
   replaced by an updated version provided by the `AMD Grand-Challenge`_ (with
   matching names).

   The changes concerns images ``A0012.jpg``, which was corrupted in REFUGE,
   and ``A0013.jpg``, which only exists in the AMD Grand-Challenge version.

Data specifications:

* Raw data input (on disk):

  * RGB images encoded in JPG format with varying resolution.  Training images
    are (HxW) 2056 x 2124 pixels; Validation (and test) images are 1634 x 1634
    pixels.
  * Vessel annotations are encoded as BMP images with the same resolution as
    input samples.
  * Masks for the eye fundus are provided by this package.
  * Total samples: 1200 distributed as 400 (training), 400 (validation) and 400
    (test).

* Output sample:

    * Image: Load raw TIFF images with :py:mod:`PIL`, with auto-conversion to RGB.
    * Vessel annotations: Load annotations with :py:mod:`PIL`, with
      auto-conversion to mode ``1`` with no dithering.
    * Eye fundus mask: Load mask with :py:mod:`PIL`, with
      auto-conversion to mode ``1`` with no dithering.

Splits ``optic-disc`` and ``cup`` contain annotations for optic-disc or cup
segmentation.

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources
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
    """A specialized raw-data-loader for the drishtigs1 dataset.

    Parameters
    ----------
    target_type
        Indicate whether to use the "cup" or "disc" target.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self, target_type: str):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )
        self.target_type = target_type

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

        assert sample[2] is not None
        mask_path = (
            importlib.resources.files(__package__) / "masks" / DATABASE_SLUG / sample[2]
        )
        with importlib.resources.as_file(mask_path) as path:
            mask = PIL.Image.open(path).convert(mode="1", dither=None)
            mask = to_dtype(to_image(mask), torch.float32, scale=True)

        image = tv_tensors.Image(crop_image_to_mask(image, mask))
        target = tv_tensors.Mask(crop_image_to_mask(target, mask))
        mask = tv_tensors.Mask(crop_image_to_mask(mask, mask))

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

        if self.target_type == "disc":
            target = (
                PIL.Image.open(self.datadir / sample[1])
                .convert(mode="RGB", dither=None)
                .convert("L")
                .point(lambda p: p <= 150, mode="1")
            )

        elif self.target_type == "cup":
            target = (
                PIL.Image.open(self.datadir / sample[1])
                .convert(mode="RGB", dither=None)
                .convert("L")
                .point(lambda p: p <= 100, mode="1")
            )

        else:
            raise ValueError(
                f"Target type {self.target_type} is not an option. "
                f"Available options are 'cup' and 'disc'."
            )

        return to_dtype(to_image(target), torch.float32, scale=True)


class DataModule(CachingDataModule):
    """REFUGE for optic disc and cup segmentation.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    target_type
        Indicate whether to use the "cup" or "disc" target.
    """

    def __init__(
        self,
        split_path: pathlib.Path | importlib.resources.abc.Traversable,
        target_type: str,
    ):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(target_type),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="segmentation",
            num_classes=1,
        )
