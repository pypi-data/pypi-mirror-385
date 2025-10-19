# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Shenzhen database <mednet.data.detect.shenzhen>` (default split)."""

import importlib.resources

from mednet.data.detect.shenzhen import DataModule

datamodule = DataModule(
    importlib.resources.files("mednet.config.segment.data.shenzhen") / "default.json"
)
