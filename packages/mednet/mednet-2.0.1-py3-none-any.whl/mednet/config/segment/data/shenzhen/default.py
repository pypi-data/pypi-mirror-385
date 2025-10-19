# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Shenzhen database <mednet.data.segment.shenzhen>` (default split)."""

import importlib.resources

from mednet.data.segment.shenzhen import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "default.json"
)
