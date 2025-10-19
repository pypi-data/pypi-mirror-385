# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import numpy as np
from torchvision import tv_tensors

from mednet.engine.classify.saliency.interpretability import (
    _compute_avg_saliency_focus,
    _compute_binary_mask,
    _compute_proportional_energy,
    _process_sample,
)


def test_compute_avg_saliency_focus():
    grayscale_cams = np.ones((200, 200))
    grayscale_cams2 = np.full((512, 512), 0.5)
    grayscale_cams3 = np.zeros((256, 256))
    grayscale_cams3[50:75, 50:100] = 1

    bbox_data = [50, 50, 100, 100]

    gt_boxes = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )
    binary_mask = _compute_binary_mask(gt_boxes, grayscale_cams)
    gt_boxes2 = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )
    binary_mask2 = _compute_binary_mask(gt_boxes2, grayscale_cams2)
    gt_boxes3 = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )
    binary_mask3 = _compute_binary_mask(gt_boxes3, grayscale_cams3)

    avg_saliency_focus = _compute_avg_saliency_focus(
        grayscale_cams,
        binary_mask,
    )
    avg_saliency_focus2 = _compute_avg_saliency_focus(
        grayscale_cams2,
        binary_mask2,
    )
    avg_saliency_focus3 = _compute_avg_saliency_focus(
        grayscale_cams3,
        binary_mask3,
    )

    assert avg_saliency_focus == 1
    assert avg_saliency_focus2 == 0.5
    assert avg_saliency_focus3 == 0.5


def test_compute_avg_saliency_focus_no_activations():
    grayscale_cams = np.zeros((200, 200))

    bbox_data = [50, 50, 100, 100]

    gt_boxes = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )

    binary_mask = _compute_binary_mask(gt_boxes, grayscale_cams)
    avg_saliency_focus = _compute_avg_saliency_focus(
        grayscale_cams,
        binary_mask,
    )

    assert avg_saliency_focus == 0


def test_compute_avg_saliency_focus_zero_gt_area():
    grayscale_cams = np.ones((200, 200))

    bbox_data = [50, 50, 50, 50]

    gt_boxes = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )

    binary_mask = _compute_binary_mask(gt_boxes, grayscale_cams)
    avg_saliency_focus = _compute_avg_saliency_focus(
        grayscale_cams,
        binary_mask,
    )

    assert avg_saliency_focus == 0


def test_compute_proportional_energy():
    grayscale_cams = np.ones((200, 200))
    grayscale_cams2 = np.full((512, 512), 0.5)
    grayscale_cams3 = np.zeros((512, 512))
    grayscale_cams3[100:200, 100:200] = 1

    bbox_data = [50, 50, 150, 150]

    gt_boxes = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )
    binary_mask = _compute_binary_mask(gt_boxes, grayscale_cams)
    gt_boxes2 = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams2.shape
    )
    binary_mask2 = _compute_binary_mask(gt_boxes2, grayscale_cams2)
    gt_boxes3 = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams3.shape
    )
    binary_mask3 = _compute_binary_mask(gt_boxes3, grayscale_cams3)

    proportional_energy = _compute_proportional_energy(
        grayscale_cams,
        binary_mask,
    )
    proportional_energy2 = _compute_proportional_energy(
        grayscale_cams2,
        binary_mask2,
    )
    proportional_energy3 = _compute_proportional_energy(
        grayscale_cams3,
        binary_mask3,
    )

    assert proportional_energy == 0.25
    assert proportional_energy2 == 0.03814697265625
    assert proportional_energy3 == 0.25


def test_compute_proportional_energy_no_activations():
    grayscale_cams = np.zeros((200, 200))

    bbox_data = [50, 50, 150, 150]

    gt_boxes = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )

    binary_mask = _compute_binary_mask(gt_boxes, grayscale_cams)
    proportional_energy = _compute_proportional_energy(
        grayscale_cams,
        binary_mask,
    )

    assert proportional_energy == 0


def test_compute_proportional_energy_no_gt_box():
    grayscale_cams = np.ones((200, 200))

    bbox_data = [0, 0, 0, 0]

    gt_boxes = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )

    binary_mask = _compute_binary_mask(gt_boxes, grayscale_cams)
    proportional_energy = _compute_proportional_energy(
        grayscale_cams,
        binary_mask,
    )

    assert proportional_energy == 0


def test_process_sample():
    grayscale_cams = np.ones((200, 200))

    bbox_data = [50, 50, 50, 50]

    gt_boxes = tv_tensors.BoundingBoxes(
        data=bbox_data, format="XYXY", canvas_size=grayscale_cams.shape
    )

    proportional_energy, avg_saliency_focus = _process_sample(
        gt_boxes,
        grayscale_cams,
    )

    assert proportional_energy == 0
    assert avg_saliency_focus == 0
