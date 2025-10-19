# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Montgomery/Shenzhen/Indian aggregated database <mednet.data.classify.montgomery_shenzhen_indian>` (default split)."""

import importlib.resources

from mednet.data.classify.montgomery_shenzhen_indian import DataModule

datamodule = DataModule(
    "default",
    (
        importlib.resources.files("mednet.config.classify.data.montgomery")
        / "default.json",
        importlib.resources.files("mednet.config.classify.data.shenzhen")
        / "default.json",
        importlib.resources.files("mednet.config.classify.data.indian")
        / "default.json",
    ),
)
