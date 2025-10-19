# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Montgomery/Shenzhen/Indian aggregated database <mednet.data.classify.montgomery_shenzhen_indian>` (cross validation fold 1)."""

import importlib.resources

from mednet.data.classify.montgomery_shenzhen_indian import DataModule

datamodule = DataModule(
    "fold-1",
    (
        importlib.resources.files("mednet.config.classify.data.montgomery")
        / "fold-1.json",
        importlib.resources.files("mednet.config.classify.data.shenzhen")
        / "fold-1.json",
        importlib.resources.files("mednet.config.classify.data.indian") / "fold-1.json",
    ),
)
