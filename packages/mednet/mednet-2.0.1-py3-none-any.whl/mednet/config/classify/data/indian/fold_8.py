# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Indian database <mednet.data.classify.indian>` (cross validation fold 8)."""

import importlib.resources

from mednet.data.classify.indian import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0]) / "fold-8.json"
)
