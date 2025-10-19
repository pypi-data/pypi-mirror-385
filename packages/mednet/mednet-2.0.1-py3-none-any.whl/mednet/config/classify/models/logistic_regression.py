# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Logistic regression classifier, to be trained from scratch.

It is preset to take 14 inputs (e.g. from the output of a model for
radiological sign classification based on :py:mod:`.data.nih_cxr14`).
"""

from mednet.models.classify.logistic_regression import LogisticRegression

model = LogisticRegression(input_size=14)
