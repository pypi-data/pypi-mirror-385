# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`DRIONS-DB database <mednet.data.segment.chasedb1>` (default split with second-annotator labels)."""

import importlib.resources

from mednet.data.segment.drionsdb import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "expert2.json"
)
