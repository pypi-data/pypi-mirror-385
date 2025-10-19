# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
""":py:mod:`AngioReport dataset <mednet.data.classify.angioreport>` (impression multilabel task using ICGA).

* Labels
    - unremarkable changes
    - macular neovascularization
    - central serous chorioretinopathy
    - uveitis
    - polypoidal choroidal vasculopathy
    - pachychoroid pigment epitheliopathy
    - choroidal mass
    - Other
"""

import importlib.resources

from mednet.data.classify.angioreport import DataModule

datamodule = DataModule(
    split_path=importlib.resources.files(__package__ or __name__.rsplit(".", 1)[0])
    / "impression.json",
    num_classes=8,
    problem_type="multilabel",
    modality="ICGA",
)
