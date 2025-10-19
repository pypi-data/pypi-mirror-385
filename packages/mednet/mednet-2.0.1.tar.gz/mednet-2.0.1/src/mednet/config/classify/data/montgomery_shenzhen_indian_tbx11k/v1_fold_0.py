# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Montgomery/Shenzhen/Indian/TBX11k aggregated database <mednet.data.classify.montgomery_shenzhen_indian_tbx11k>` (v1: healthy vs active TB; cross validation fold 0)."""

import importlib.resources

from mednet.data.classify.montgomery_shenzhen_indian_tbx11k import DataModule

datamodule = DataModule(
    "v1-fold-0",
    (
        importlib.resources.files("mednet.config.classify.data.montgomery")
        / "fold-0.json",
        importlib.resources.files("mednet.config.classify.data.shenzhen")
        / "fold-0.json",
        importlib.resources.files("mednet.config.classify.data.indian") / "fold-0.json",
        importlib.resources.files("mednet.config.classify.data.tbx11k")
        / "v1-fold-0.json",
    ),
)
