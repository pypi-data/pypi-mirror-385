# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`AngioReport dataset <mednet.data.classify.angioreport>` (HyperF_Type multiclass task using FA).

* Labels
    - 0 (leakage),
    - 1 (staining),
    - 2 (no),
    - 3 (pooling),
    - 4 (window defect).
"""

import importlib.resources

from mednet.data.classify.angioreport import DataModule

datamodule = DataModule(
    split_path=importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "hyperftype.json",
    num_classes=5,
    problem_type="multiclass",
)
