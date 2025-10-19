# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`AngioReport dataset <mednet.data.classify.angioreport>` (CNV binary task using FA).

* Labels
    - 0 (no),
    - 1 (yes),
"""

import importlib.resources

from mednet.data.classify.angioreport import DataModule

datamodule = DataModule(
    split_path=importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "cnv.json",
    num_classes=1,
    problem_type="binary",
)
