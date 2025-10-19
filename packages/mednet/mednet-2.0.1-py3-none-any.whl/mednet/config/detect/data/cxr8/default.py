# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`CXR8 database <mednet.data.detect.cxr8>` (default split)."""

import importlib.resources

from mednet.data.detect.cxr8 import DataModule

datamodule = DataModule(
    importlib.resources.files("mednet.config.segment.data.cxr8") / "default.json.bz2"
)
