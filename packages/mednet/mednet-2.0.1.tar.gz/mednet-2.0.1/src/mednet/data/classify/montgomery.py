# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Montgomery DataModule for TB detection.

The standard digital image database for Tuberculosis was created by the
National Library of Medicine, Maryland, USA in collaboration with Shenzhen No.3
People’s Hospital, Guangdong Medical College, Shenzhen, China.

* Database references: :cite:p:`jaeger_two_2014`,

Data specifications:

* Raw data input (on disk):

  * PNG images 8 bit grayscale issued from digital radiography machines
  * Original resolution (height x width or width x height): 4020x4892 px or
    4892x4020 px
  * Samples: 138 images and associated labels

* Output image:

  * Transforms:

    * Load raw PNG with :py:mod:`PIL`
    * Remove black borders
    * Convert to torch tensor

  * Final specifications

    * Grayscale, encoded as a single plane tensor, 32-bit floats,
      square at most 4020 x 4020 pixels
    * Binary labels: 0 (healthy), 1 (active tuberculosis), encoded as a 1D
      torch float tensor.

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
from ..image_utils import remove_black_borders
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the Montgomery dataset.

    Parameters
    ----------
    config_variable
        Key to search for in the configuration file for the root directory of
        this database.
    multiclass
        Set to ``True`` if the targets should be output as 2 distinct classes
        instead of a single (0/1) output.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    # config_variable: required so this loader can be used for the small
    # version of the Montgomery database as well.
    def __init__(
        self, config_variable: str = CONFIGURATION_KEY_DATADIR, multiclass: bool = False
    ):
        self.datadir = pathlib.Path(
            load_rc().get(config_variable, os.path.realpath(os.curdir)),
        )
        self.multiclass = multiclass

    def sample(self, sample: tuple[str, int, typing.Any | None]) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            Expects a tuple containing the path suffix, within the dataset root
            folder, where to find the image to be loaded, and an integer,
            representing the sample target.

        Returns
        -------
            The sample representation as a dictionary.
        """

        # N.B.: Montgomery images are encoded as grayscale PNGs, so no need to
        # convert them again with Image.convert("L").
        image = PIL.Image.open(self.datadir / sample[0])
        image, _ = remove_black_borders(image)
        image = to_dtype(to_image(image), torch.float32, scale=True)
        image = tv_tensors.Image(image)

        # use the code below to view generated images
        # from torchvision.transforms.v2.functional import to_pil_image
        # to_pil_image(tensor).show()
        # __import__("pdb").set_trace()

        return dict(image=image, target=self.target(sample), name=sample[0])

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
            1D torch float tensor.
        """
        if self.multiclass:
            if sample[1] == 0:
                return torch.FloatTensor([1, 0])

            return torch.FloatTensor([0, 1])

        return torch.FloatTensor([sample[1]])


class DataModule(CachingDataModule):
    """Montgomery DataModule for TB detection.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    multiclass
        Set to ``True`` if the targets should be output as 2 distinct classes
        instead of a single (0/1) output.
    """

    def __init__(
        self,
        split_path: pathlib.Path | importlib.resources.abc.Traversable,
        multiclass: bool = False,
    ):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(multiclass=multiclass),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="classification",
            num_classes=1,
        )
