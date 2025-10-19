# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Montgomery/Shenzhen aggregated database <mednet.data.classify.montgomery_shenzhen>` (cross validation fold 4)."""

import importlib.resources

from mednet.data.classify.montgomery_shenzhen import DataModule

datamodule = DataModule(
    "fold-4",
    (
        importlib.resources.files("mednet.config.classify.data.montgomery")
        / "fold-4.json",
        importlib.resources.files("mednet.config.classify.data.shenzhen")
        / "fold-4.json",
    ),
)
