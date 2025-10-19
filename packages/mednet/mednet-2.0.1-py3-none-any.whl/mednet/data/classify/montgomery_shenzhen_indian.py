# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Aggregated DataModule composed of :py:mod:`montgomery's <.data.classify.montgomery>`, :py:mod:`shenzhen's <.data.classify.shenzhen>`, and :py:mod:`indian's <.data.classify.indian>` splits.

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import pathlib

from ..datamodule import ConcatDataModule
from ..split import JSONDatabaseSplit
from .indian import CONFIGURATION_KEY_DATADIR as INDIAN_KEY_DATADIR
from .indian import RawDataLoader as IndianLoader
from .montgomery import RawDataLoader as MontgomeryLoader
from .shenzhen import RawDataLoader as ShenzhenLoader

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""


class DataModule(ConcatDataModule):
    """Aggregated DataModule composed of :py:mod:`montgomery's <.data.classify.montgomery>`, :py:mod:`shenzhen's <.data.classify.shenzhen>`, and :py:mod:`indian's <.data.classify.indian>` splits.

    Parameters
    ----------
    split_name
        The name of the split to assign to this data module.
    split_path
        Path or traversable (resource) with the JSON split description to load
        for montgomery, shenzhen and indian databases (in this order).
    """

    def __init__(
        self,
        split_name: str,
        split_path: tuple[
            pathlib.Path | importlib.resources.abc.Traversable,
            pathlib.Path | importlib.resources.abc.Traversable,
            pathlib.Path | importlib.resources.abc.Traversable,
        ],
    ):
        montgomery_loader = MontgomeryLoader()
        montgomery_split = JSONDatabaseSplit(split_path[0])
        shenzhen_loader = ShenzhenLoader()
        shenzhen_split = JSONDatabaseSplit(split_path[1])
        indian_loader = IndianLoader(INDIAN_KEY_DATADIR)
        indian_split = JSONDatabaseSplit(split_path[2])

        super().__init__(
            splits={
                "train": [
                    (montgomery_split["train"], montgomery_loader),
                    (shenzhen_split["train"], shenzhen_loader),
                    (indian_split["train"], indian_loader),
                ],
                "validation": [
                    (montgomery_split["validation"], montgomery_loader),
                    (shenzhen_split["validation"], shenzhen_loader),
                    (indian_split["validation"], indian_loader),
                ],
                "test": [
                    (montgomery_split["test"], montgomery_loader),
                    (shenzhen_split["test"], shenzhen_loader),
                    (indian_split["test"], indian_loader),
                ],
            },
            database_name=DATABASE_SLUG,
            split_name=split_name,
            task="classification",
            num_classes=1,
        )
