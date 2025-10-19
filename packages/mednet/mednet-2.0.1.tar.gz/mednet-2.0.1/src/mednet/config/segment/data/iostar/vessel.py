# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`IOSTAR database <mednet.data.segment.iostar>` (default split for vessel segmentation)."""

import importlib.resources

from mednet.data.segment.iostar import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0]) / "vessel.json"
)
