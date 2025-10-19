# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`NIH-CXR14 database <mednet.data.classify.nih_cxr14>` (default split)."""

import importlib.resources

from mednet.data.classify.nih_cxr14 import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "default.json.bz2"
)
