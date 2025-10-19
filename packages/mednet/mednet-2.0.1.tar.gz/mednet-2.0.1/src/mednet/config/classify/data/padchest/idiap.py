# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`pad-chest database <mednet.data.classify.padchest>` (idiap split)."""

import importlib.resources

from mednet.data.classify.padchest import DataModule

datamodule = DataModule(
    importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "idiap.json.bz2"
)
