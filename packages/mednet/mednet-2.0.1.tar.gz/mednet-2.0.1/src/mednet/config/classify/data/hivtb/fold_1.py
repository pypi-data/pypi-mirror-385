# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`HIV-TB database <mednet.data.classify.hivtb>` (cross validation fold 1)."""

import importlib.resources

from mednet.data.classify.hivtb import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0]) / "fold-1.json"
)
