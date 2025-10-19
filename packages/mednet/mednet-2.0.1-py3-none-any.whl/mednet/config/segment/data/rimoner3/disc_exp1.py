# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`RIM-ONE r3 database <mednet.data.segment.rimoner3>` (default split for optic-disc segmentation with expert 1 annotations)."""

import importlib.resources

from mednet.data.segment.rimoner3 import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "optic-disc-exp1.json"
)
