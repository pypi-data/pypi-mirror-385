# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`JSRT database <mednet.data.segment.jsrt>` (default split)."""

import importlib.resources

from mednet.data.detect.jsrt import DataModule

datamodule = DataModule(
    importlib.resources.files("mednet.config.segment.data.jsrt") / "default.json"
)
