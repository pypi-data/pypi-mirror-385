# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Test code for losses."""

import numpy
import pytest
import torch

from mednet.models.losses import MOONBCEWithLogitsLoss


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_pos_weight_for_bcewithlogitsloss_binary():
    from mednet.config.classify.data.montgomery.default import datamodule
    from mednet.models.losses import pos_weight_for_bcewithlogitsloss

    datamodule.model_transforms = []
    datamodule.prepare_data()
    datamodule.setup(stage="fit")

    train, val = pos_weight_for_bcewithlogitsloss(datamodule)

    assert "pos_weight" in train
    assert train["pos_weight"].shape == (1,)
    # there are 37 positives out of 88 samples in the training set
    # therefore, pos_weight = # neg / # pos
    pos_ratio = (88 - 37) / 37
    assert numpy.isclose(train["pos_weight"].item(), pos_ratio)

    assert "pos_weight" in val
    assert train["pos_weight"].shape == (1,)
    # there are 9 positives out of 22 samples in the validation set
    # therefore, pos_weight = # neg / # pos
    pos_ratio = (22 - 9) / 9
    assert numpy.isclose(val["pos_weight"].item(), pos_ratio)


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_pos_weight_for_bcewithlogitsloss_multiclass():
    from mednet.config.classify.data.montgomery.multiclass import datamodule
    from mednet.models.losses import pos_weight_for_bcewithlogitsloss

    datamodule.model_transforms = []
    datamodule.prepare_data()
    datamodule.setup(stage="fit")

    train, val = pos_weight_for_bcewithlogitsloss(datamodule)

    assert "pos_weight" in train
    assert train["pos_weight"].shape == (2,)
    # there are 37 positives out of 88 samples in the training set
    # therefore, pos_weight = # neg / # pos
    pos_ratio = (88 - 37) / 37
    assert numpy.allclose(train["pos_weight"], (1 / pos_ratio, pos_ratio))

    assert "pos_weight" in val
    assert train["pos_weight"].shape == (2,)
    # there are 9 positives out of 22 samples in the validation set
    # therefore, pos_weight = # neg / # pos
    pos_ratio = (22 - 9) / 9
    assert numpy.allclose(val["pos_weight"], (1 / pos_ratio, pos_ratio))


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_weight_for_moonbcewithlogitsloss_weights():
    from mednet.config.classify.data.montgomery.multiclass import datamodule

    datamodule.model_transforms = []
    datamodule.prepare_data()
    datamodule.setup(stage="fit")

    train, val = MOONBCEWithLogitsLoss.get_arguments_from_datamodule(datamodule)

    assert "weights" in train
    assert train["weights"].shape == (2, 2)
    # there are 37 positives out of 88 samples in the training set
    # therefore, pos_weight = # neg / # pos
    pos_ratio = (88 - 37) / 37
    # the w- vector should be [1 , 1 / pos_ratio] (1st row)
    # the w+ vector should be [1/pos_ratio , 1] (2nd row)
    assert numpy.allclose(train["weights"], ((1, 1 / pos_ratio), (1 / pos_ratio, 1)))

    assert "weights" in val
    assert train["weights"].shape == (2, 2)
    # there are 9 positives out of 22 samples in the validation set
    # therefore, pos_weight = # neg / # pos
    pos_ratio = (22 - 9) / 9
    # the w- vector should be [1 , 1/pos_ratio] (1st row)
    # the w+ vector should be [1/pos_ratio , 1] (2nd row)
    assert numpy.allclose(val["weights"], ((1, 1 / pos_ratio), (1 / pos_ratio, 1)))


def test_weight_for_moonbcewithlogitsloss_multiclass():
    target = torch.FloatTensor(
        [
            [0, 1],
            [0, 1],
            [1, 0],
            [1, 0],
            [1, 0],
        ]
    )
    model_output = torch.FloatTensor(
        [
            [0, 1],  # ideal case
            [1, 0],  # worst case
            [0.5, 0.5],
            [0.75, 0.10],
            [0.9, 0.25],
        ]
    )

    # We should first create a composition of weights depending on the "ones"
    # in each column. If there is a "1" on a target item, then it should get
    # the w+ (position [1]) of the weight of that column, otherwise, the w-
    # (position [0]). Manually, this should be equivalent to this:
    pos_ratio = (88 - 37) / 37  # copied from previous test
    w = torch.FloatTensor(((1, 1 / pos_ratio), (1 / pos_ratio, 1)))
    w_neg, w_pos = w
    weights_manual = torch.FloatTensor(
        [
            # N.B.: weights are organized as a [2, C] matrix with w- at row [0]
            # and w+ at row [1]
            [w_neg[0], w_pos[1]],
            [w_neg[0], w_pos[1]],
            [w_pos[0], w_neg[1]],
            [w_pos[0], w_neg[1]],
            [w_pos[0], w_neg[1]],
        ]
    )

    # You can implement this in a faster operation using the following
    # expression:
    weights = ((1 - target) * w_neg) + (target * w_pos)
    assert numpy.allclose(weights_manual, weights)

    # the loss should evaluate the BCE with logits first
    individual_losses = torch.nn.functional.binary_cross_entropy_with_logits(
        model_output, target, reduction="none"
    )

    loss = MOONBCEWithLogitsLoss(weights=w)
    result = loss.forward(model_output, target)
    assert numpy.isclose(result, (individual_losses * weights).mean())


def test_compare_moon_to_bce_loss():
    # Tests that MOON and BCE with simple weighting are different only w.r.t.
    # the weights that are used to weigh samples.

    pos_bce_weight = torch.FloatTensor([3, 0.5, 1])

    loss_bce = torch.nn.BCEWithLogitsLoss(pos_weight=pos_bce_weight)

    # MOON: neg_moon_weight = (1 / pos_bce_weight).clamp(min=0, max=1)
    neg_moon_weight = torch.ones_like(pos_bce_weight)  # BCE equivalent
    # MOON: pos_moon_weight = pos_bce_weight.clamp(min=0, max=1)
    pos_moon_weight = pos_bce_weight  # BCE equivalent
    moon_weights = torch.vstack([neg_moon_weight, pos_moon_weight])
    loss_moon = MOONBCEWithLogitsLoss(weights=moon_weights)

    # assert they provide the same answer
    target = torch.FloatTensor(
        [
            [0, 1, 1],
            [0, 1, 0],
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 1],
        ]
    )
    model_output = torch.FloatTensor(
        [
            [0, 1, 1],  # ideal case
            [1, 0, 1],  # worst case
            [0.5, 0.5, 0.5],
            [0.75, 0.10, 0.1],
            [0.9, 0.25, 0.8],
        ]
    )

    assert loss_bce.forward(model_output, target) == loss_moon.forward(
        model_output, target
    )
