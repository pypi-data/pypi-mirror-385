# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`CXR8 database <mednet.data.segment.cxr8>` (default split)."""

import importlib.resources

from mednet.data.segment.cxr8 import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "default.json.bz2"
)
