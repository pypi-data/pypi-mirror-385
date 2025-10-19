# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Montgomery database <mednet.data.classify.montgomery>` (default split) with multi-class (C=2) targets."""

import importlib.resources

from mednet.data.classify.montgomery import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "default.json",
    multiclass=True,
)
