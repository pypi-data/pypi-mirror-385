# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`TBX11k database <mednet.data.classify.tbx11k>` (v1: healthy vs active TB; cross validation fold 4)."""

import importlib.resources

from mednet.data.classify.tbx11k import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "v1-fold-4.json"
)
