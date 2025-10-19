# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`TB-POC database <mednet.data.classify.tbpoc>` (cross validation fold 1)."""

import importlib.resources

from mednet.data.classify.tbpoc import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0]) / "fold-1.json"
)
