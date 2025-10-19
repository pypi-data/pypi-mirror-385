# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`RIM-ONE r3 database <mednet.data.segment.rimoner3>` (default split for optic-cup segmentation with expert 2 annotations)."""

import importlib.resources

from mednet.data.segment.rimoner3 import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "optic-cup-exp2.json"
)
