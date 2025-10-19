# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for measure functions."""

import numpy


def test_centered_maxf1() -> None:
    from mednet.engine.classify.evaluator import _get_centered_maxf1

    # Multiple max F1
    f1_scores = numpy.array([0.8, 0.9, 1.0, 1.0, 1.0, 0.3])
    thresholds = numpy.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7])

    maxf1, threshold = _get_centered_maxf1(f1_scores, thresholds)

    assert maxf1 == 1.0
    assert threshold == 0.5

    # Single max F1
    f1_scores = numpy.array([0.8, 0.9, 1.0, 0.9, 0.7, 0.3])
    thresholds = numpy.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7])

    maxf1, threshold = _get_centered_maxf1(f1_scores, thresholds)

    assert maxf1 == 1.0
    assert threshold == 0.4


def test_run_binary_1() -> None:
    from mednet.engine.classify.evaluator import run
    from mednet.models.classify.typing import Prediction

    predictions: list[Prediction] = [
        # (name, target, predicted-value)
        ("s0", [0], [0.1]),
        ("s2", [0], [0.8]),
        ("s3", [1], [0.9]),
        ("s3", [1], [0.4]),
    ]

    rng = numpy.random.default_rng(42)

    results = run(
        "test",
        predictions,
        binning=10,
        rng=rng,
        threshold_a_priori=0.5,
    )

    assert results["num_samples"] == 4
    assert numpy.isclose(results["threshold"], 0.5)
    assert not results["threshold_a_posteriori"]
    assert numpy.isclose(results["precision"], 1 / 2)  # tp / (tp + fp)
    assert numpy.isclose(results["recall"], 1 / 2)  # tp / (tp + fn)
    assert numpy.isclose(
        results["f1"],
        2 * (1 / 2 * 1 / 2) / (1 / 2 + 1 / 2),
    )  # 2 * (prec. * recall) / (prec. + recall)
    assert numpy.isclose(
        results["accuracy"],
        (1 + 1) / (1 + 1 + 1 + 1),
    )  # (tp + tn) / (tp + fn + tn + fp)
    assert numpy.isclose(results["specificity"], 1 / 2)  # tn / (tn + fp)

    # threshold table:
    # threshold |  TNR  | 1-TNR |  TPR
    # ----------+-------+-------+---------
    #  < 0.1    |  0    |  1    |  1
    #    0.1    |  0.5  |  0.5  |  1
    #    0.4    |  0.5  |  0.5  |  0.5
    #    0.8    |  1    |  0    |  0.5
    #    0.9    |  1    |  0    |  0
    #  > 0.9    |  1    |  0    |  0
    assert numpy.isclose(results["roc_auc"], 0.75)

    # threshold table:
    # threshold |  Prec.  |  Recall
    # ----------+---------+----------
    #  < 0.1    |  0.5    |  1
    #    0.1    |  2/3    |  1
    #    0.4    |  0.5    |  0.5
    #    0.8    |  1      |  0.5
    #    0.9    |  0      |  0
    #  > 0.9    |  0      |  0
    assert numpy.isclose(results["average_precision"], 0.8333333)


def test_run_binary_2() -> None:
    from mednet.engine.classify.evaluator import run
    from mednet.models.classify.typing import Prediction

    predictions: list[Prediction] = [
        # (name, target, predicted-value)
        ("s0", [0], [0.1]),
        ("s2", [0], [0.8]),
        ("s3", [1], [0.9]),
        ("s3", [1], [0.4]),
    ]

    rng = numpy.random.default_rng(42)

    # a change in the threshold should not affect auc and average precision scores
    results = run(
        "test",
        predictions,
        binning=10,
        rng=rng,
        threshold_a_priori=0.3,
    )

    assert results["num_samples"] == 4
    assert numpy.isclose(results["threshold"], 0.3)
    assert not results["threshold_a_posteriori"]

    assert numpy.isclose(results["precision"], 2 / 3)  # tp / (tp + fp)
    assert numpy.isclose(results["recall"], 2 / 2)  # tp / (tp + fn)
    assert numpy.isclose(
        results["f1"],
        2 * (2 / 3 * 2 / 2) / (2 / 3 + 2 / 2),
    )  # 2 * (prec. * recall) / (prec. + recall)
    assert numpy.isclose(
        results["accuracy"],
        (2 + 1) / (2 + 0 + 1 + 1),
    )  # (tp + tn) / (tp + fn + tn + fp)
    assert numpy.isclose(results["specificity"], 1 / (1 + 1))  # tn / (tn + fp)

    # threshold table:
    # threshold |  TNR  | 1-TNR |  TPR
    # ----------+-------+-------+---------
    #  < 0.1    |  0    |  1    |  1
    #    0.1    |  0.5  |  0.5  |  1
    #    0.4    |  0.5  |  0.5  |  0.5
    #    0.8    |  1    |  0    |  0.5
    #    0.9    |  1    |  0    |  0
    #  > 0.9    |  1    |  0    |  0
    assert numpy.isclose(results["roc_auc"], 0.75)

    # threshold table:
    # threshold |  Prec.  |  Recall
    # ----------+---------+----------
    #  < 0.1    |  0.5    |  1
    #    0.1    |  2/3    |  1
    #    0.4    |  0.5    |  0.5
    #    0.8    |  1      |  0.5
    #    0.9    |  0      |  0
    #  > 0.9    |  0      |  0
    assert numpy.isclose(results["average_precision"], 0.8333333)
