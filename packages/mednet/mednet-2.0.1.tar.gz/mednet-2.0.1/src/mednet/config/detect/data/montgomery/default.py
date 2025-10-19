# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Montgomery database <mednet.data.detect.montgomery>` (default split)."""

import importlib.resources

from mednet.data.detect.montgomery import DataModule

datamodule = DataModule(
    importlib.resources.files("mednet.config.segment.data.montgomery") / "default.json"
)
