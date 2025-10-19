# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Japanese Society of Radiological Technology dataset for lung segmentation.

The database includes 154 nodule and 93 non-nodule images.  It contains a total
of 247 resolution of 2048 x 2048 pixels, issued from original digitized
Radiographies (laser scanner). One set of ground-truth lung annotations is
available.

* Database references:

  * Original data: :cite:p:`shiraishi_development_2000`
  * Split: :cite:p:`gaal_attention_2020`

.. important:: **Raw data organization**

   The JSRT_ base datadir, which you should configure following the
   :ref:`mednet.setup` instructions, must contain at least the following
   directories:

   - ``All247images/`` (directory containing the CXR images, in raw format)
   - ``scratch/`` (must contain masks downloaded from `JSRT-Annotations`_)

Data specifications:

* Raw data input (on disk):

  * Original images encoded in proprietary 12-bit RAW format.  A PNG-converted
    set of images is provided at JSRT-Kaggle_ for your reference.  Input
    resolution is 2048 x 2048 pixels.
  * Masks: encoded as GIF files with separate portions for left and right
    lungs, with a resolution of 1024 x 1024 pixels
  * Total samples: 247

* Output sample:

    * Image: Load raw image from folder ``All247images/`` using
      :py:func:`numpy.fromfile`, then applies a simple histogram equalization
      to the 8-bit representation of the image, to obtain something along the
      lines of the PNG (unofficial) version distributed at JSRT-Kaggle_.
      Output images have a size of 1024 x 1024 pixels, achieved by resizing the
      original input with bilinear interpolation.
    * Labels for each of the lungs are read from the provided GIF files and
      merged into a single output image.

The ``default`` split contains 172 samples for training, 25 for validation and
50 for test.

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import numpy as np
import PIL.Image
import skimage.exposure
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
    """A specialized raw-data-loader for the jsrt dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )

    def load_pil_raw_12bit_jsrt(self, path: pathlib.Path) -> PIL.Image.Image:
        """Load a raw 16-bit sample data.

        This method was designed to handle the raw images from the JSRT dataset.
        It reads the data file and applies a simple histogram equalization to the
        8-bit representation of the image to obtain something along the lines of
        the PNG (unofficial) version distributed at `JSRT-Kaggle`.

        Parameters
        ----------
        path
            The full path leading to the image to be loaded.

        Returns
        -------
            A PIL image in RGB mode, with `width`x`width` pixels.
        """

        raw_image = np.fromfile(path, np.dtype(">u2")).reshape(2048, 2048)
        raw_image[raw_image > 4095] = 4095
        raw_image = 4095 - raw_image  # invert colors
        raw_image = (raw_image >> 4).astype(np.uint8)  # 8-bit uint
        raw_image = skimage.exposure.equalize_hist(raw_image)
        return PIL.Image.fromarray((raw_image * 255).astype(np.uint8)).convert("RGB")

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

        image = self.load_pil_raw_12bit_jsrt(self.datadir / sample[0])

        # N.B.: Original image size is 2048x2048 px, however annotations were done on
        # 1024x1024 px canvas.
        #
        # assert image.size == (2048, 2048)

        image = image.resize((1024, 1024), PIL.Image.Resampling.BILINEAR)
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

        # Combine left and right lung masks into a single tensor
        left = PIL.Image.open(self.datadir / sample[1]).convert(mode="1", dither=None)
        right = PIL.Image.open(self.datadir / sample[2]).convert(mode="1", dither=None)
        target = np.ma.mask_or(np.asarray(left), np.asarray(right))

        return to_dtype(to_image(target), torch.float32, scale=True)


class DataModule(CachingDataModule):
    """Japanese Society of Radiological Technology dataset for lung segmentation.

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
