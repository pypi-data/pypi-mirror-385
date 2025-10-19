# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`DRISHTI-GS1 database <mednet.data.segment.drishtigs1>` (optic-disc annotations agreed by all annotators)."""

import importlib.resources

from mednet.data.segment.drishtigs1 import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "optic-disc.json",
    target_all=True,
)
