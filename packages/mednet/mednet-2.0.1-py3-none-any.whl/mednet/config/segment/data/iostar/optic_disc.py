# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`IOSTAR database <mednet.data.segment.iostar>` (default split for optic-disc segmentation)."""

import importlib.resources

from mednet.data.segment.iostar import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "optic-disc.json"
)
