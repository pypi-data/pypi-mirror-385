# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later


from mednet.engine.detect.evaluator import run
from mednet.models.detect.typing import Prediction


def test_iou_from_no_predictions() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # bounding-box, target
            (([10, 10, 20, 20], 1),),  # target #1
            (),  # no predictions
        )
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 1
    assert result["num-targets"] == 1
    assert result["num-detections"] == 0
    assert result["mean-iou"] == 0.0
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == 0.0
    assert result["per-class"][1]["num-targets"] == 1
    assert result["per-class"][1]["num-detections"] == 0


def test_iou_from_no_matching_predictions() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (([10, 10, 20, 20], 1),),  # target #1
            # detections: bounding-box, target, classifier score
            (([10, 10, 20, 20], 0, 1.0),),  # does not match target
        )
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 1
    assert result["num-targets"] == 1
    assert result["num-detections"] == 1
    assert result["mean-iou"] == 0.0
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == 0.0
    assert result["per-class"][1]["num-targets"] == 1
    assert result["per-class"][1]["num-detections"] == 0


def test_iou_from_single_prediction() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (([10, 10, 20, 20], 1),),  # target #1
            # detections: bounding-box, target, classifier score
            (([10, 10, 20, 20], 1, 1.0),),  # perfectly matches target
        )
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 1
    assert result["num-targets"] == 1
    assert result["num-detections"] == 1
    assert result["mean-iou"] == 1.0
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == 1.0
    assert result["per-class"][1]["num-targets"] == 1
    assert result["per-class"][1]["num-detections"] == 1


def test_iou_from_multiple_predictions() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (([10, 10, 20, 20], 1),),  # target #1
            # detections: bounding-box, target, classifier score
            (
                ([10, 10, 20, 20], 0, 0.1),  # does not match target
                ([15, 10, 20, 20], 1, 0.9),  # somewhat matches target
            ),
        )
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 1
    assert result["num-targets"] == 1
    assert result["num-detections"] == 2
    assert result["mean-iou"] == 0.5
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == 0.5
    assert result["per-class"][1]["num-targets"] == 1
    assert result["per-class"][1]["num-detections"] == 1


def test_iou_from_multiple_predictions_that_can_match() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (([10, 10, 20, 20], 1),),  # target #1
            # detections: bounding-box, target, classifier score
            (
                ([15, 10, 20, 20], 1, 0.9),  # somewhat matches target
                ([12.5, 10, 20, 20], 1, 0.9),  # better matches target
            ),
        )
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 1
    assert result["num-targets"] == 1
    assert result["num-detections"] == 2
    assert result["mean-iou"] == 0.75
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == 0.75
    assert result["per-class"][1]["num-targets"] == 1
    assert result["per-class"][1]["num-detections"] == 2


def test_iou_from_prediction_that_misses() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (([10, 10, 20, 20], 1),),  # target #1
            # detections: bounding-box, target, classifier score
            (
                ([30, 30, 40, 40], 1, 0.2),  # completely misses
            ),
        )
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 1
    assert result["num-targets"] == 1
    assert result["num-detections"] == 1
    assert result["mean-iou"] == 0.0
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == 0.0
    assert result["per-class"][1]["num-targets"] == 1
    assert result["per-class"][1]["num-detections"] == 1


def test_iou_from_multiple_predictions_and_targets() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (
                ([10, 10, 20, 20], 1),  # target #0
                ([30, 30, 40, 40], 1),  # target #1
            ),
            # detections: bounding-box, target, classifier score
            (
                ([35, 30, 40, 40], 1, 0.9),  # matches target #1
                ([12.5, 10, 20, 20], 1, 0.9),  # matches target #0
            ),
        )
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 1
    assert result["num-targets"] == 2
    assert result["num-detections"] == 2
    assert result["mean-iou"] == (0.75 + 0.5) / 2
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == (0.75 + 0.5) / 2
    assert result["per-class"][1]["num-targets"] == 2
    assert result["per-class"][1]["num-detections"] == 2


def test_iou_from_multiple_samples() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (([10, 10, 20, 20], 1),),
            # detections: bounding-box, target, classifier score
            (([12.5, 10, 20, 20], 1, 0.9),),
        ),
        (
            "path/to/sample2.png",
            # ground-truth: bounding-box, target
            (([30, 30, 40, 40], 1),),
            # detections: bounding-box, target, classifier score
            (
                ([35, 30, 40, 40], 1, 0.9),  # matches target
            ),
        ),
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 2
    assert result["num-targets"] == 2
    assert result["num-detections"] == 2
    assert result["mean-iou"] == (0.75 + 0.5) / 2
    assert len(result["per-class"]) == 1
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == (0.75 + 0.5) / 2
    assert result["per-class"][1]["num-targets"] == 2
    assert result["per-class"][1]["num-detections"] == 2


def test_iou_from_multiple_samples_and_classes() -> None:
    predictions: list[Prediction] = [
        (
            "path/to/sample1.png",
            # ground-truth: bounding-box, target
            (([10, 10, 20, 20], 1),),
            # detections: bounding-box, target, classifier score
            (([12.5, 10, 20, 20], 1, 0.9),),
        ),
        (
            "path/to/sample2.png",
            # ground-truth: bounding-box, target
            (([30, 30, 40, 40], 2),),
            # detections: bounding-box, target, classifier score
            (
                ([35, 30, 40, 40], 2, 0.9),  # matches target
            ),
        ),
    ]

    result = run(predictions, binning=10)

    assert result["num-samples"] == 2
    assert result["num-targets"] == 2
    assert result["num-detections"] == 2
    assert result["mean-iou"] == (0.75 + 0.5) / 2
    assert len(result["per-class"]) == 2
    assert 1 in result["per-class"]
    assert result["per-class"][1]["mean-iou"] == 0.75
    assert result["per-class"][1]["num-targets"] == 1
    assert result["per-class"][1]["num-detections"] == 1
    assert result["per-class"][2]["mean-iou"] == 0.5
    assert result["per-class"][2]["num-targets"] == 1
    assert result["per-class"][2]["num-detections"] == 1
