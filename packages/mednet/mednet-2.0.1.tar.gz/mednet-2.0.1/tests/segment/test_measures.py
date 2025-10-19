# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import random

import numpy

from mednet.engine.segment.evaluator import all_metrics


def test_all_metrics():
    tp = random.randint(1, 100)
    fp = random.randint(1, 100)
    tn = random.randint(1, 100)
    fn = random.randint(1, 100)

    p, r, s, a, j, f1 = all_metrics(tp, fp, tn, fn)

    assert (tp / (tp + fp)) == p
    assert (tp / (tp + fn)) == r
    assert (tn / (tn + fp)) == s
    assert ((tp + tn) / (tp + tn + fp + fn)) == a
    assert (tp / (tp + fp + fn)) == j
    assert ((2.0 * tp) / (2.0 * tp + fp + fn)) == f1
    assert numpy.isclose((2 * p * r) / (p + r), f1)
