# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Shenzhen database <mednet.data.classify.shenzhen>` (all-test split, only test set available)."""

import importlib.resources

from mednet.data.classify.shenzhen import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "alltest.json"
)
