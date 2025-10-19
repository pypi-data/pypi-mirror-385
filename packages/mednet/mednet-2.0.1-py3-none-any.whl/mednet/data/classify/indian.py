# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Indian database for TB detection (a.k.a. Dataset A/Dataset B).

The Indian collection database has been established to foster research in
computer-aided diagnosis of pulmonary diseases with a special focus on
pulmonary tuberculosis (TB).  This database is also known as the "Database
A/Database B" database.

* Database reference: :cite:p:`noauthor_tbxpredict_2014`
* Split references: :cite:p:`noauthor_tbxpredict_2014` with 20% of train set for the validation
  set

.. important:: **Raw data organization**

    The Indian_ base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at least these two
    subdirectories:

    - ``DatasetA/`` (directory containing the dataset A images in JPG format)
    - ``DatasetB/`` (directory containing the dataset B images in DICOM format)

Data specifications:

* Raw data input (on disk):

  * JPG RGB 8-bit depth images with "inverted" grayscale scale, with varying
    resolution of at least 1024 x 1024 pixels per sample
  * Samples: 156 images and associated labels

* Output image:  Use the same transforms and specifications as for
  :py:mod:`.classify.shenzhen`

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import pathlib

from ..datamodule import CachingDataModule
from ..split import JSONDatabaseSplit
from .shenzhen import RawDataLoader

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class DataModule(CachingDataModule):
    """Indian database for TB detection (a.k.a. Dataset A/Dataset B).
        Names of the JSON files containing the splits to load for montgomery
        and shenzhen databases (in this order).

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    """

    def __init__(self, split_path: pathlib.Path | importlib.resources.abc.Traversable):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(config_variable=CONFIGURATION_KEY_DATADIR),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="classification",
            num_classes=1,
        )
