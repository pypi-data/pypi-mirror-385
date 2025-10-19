# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`STARE database <mednet.data.segment.stare>` (default split with AH annotations)."""

import importlib.resources

from mednet.data.segment.stare import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0]) / "ah.json"
)
