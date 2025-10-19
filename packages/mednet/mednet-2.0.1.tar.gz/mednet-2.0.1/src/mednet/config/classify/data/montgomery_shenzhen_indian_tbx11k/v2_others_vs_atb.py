# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`Montgomery/Shenzhen/Indian/TBX11k aggregated database <mednet.data.classify.montgomery_shenzhen_indian_tbx11k>` (v2: healthy, sick and latent vs active TB; default split)."""

import importlib.resources

from mednet.data.classify.montgomery_shenzhen_indian_tbx11k import DataModule

datamodule = DataModule(
    "v2-others-vs-atb",
    (
        importlib.resources.files("mednet.config.classify.data.montgomery")
        / "default.json",
        importlib.resources.files("mednet.config.classify.data.shenzhen")
        / "default.json",
        importlib.resources.files("mednet.config.classify.data.indian")
        / "default.json",
        importlib.resources.files("mednet.config.classify.data.tbx11k")
        / "v2-others-vs-atb.json",
    ),
)
