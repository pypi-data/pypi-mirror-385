# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Shenzhen database <mednet.data.classify.shenzhen>` (cross validation fold 5)."""

import importlib.resources

from mednet.data.classify.shenzhen import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0]) / "fold-5.json"
)
