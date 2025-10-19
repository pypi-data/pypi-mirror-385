# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Defines most common types used in code."""

import typing

Checkpoint: typing.TypeAlias = typing.MutableMapping[str, typing.Any]
"""Definition of a lightning checkpoint."""

TaskType: typing.TypeAlias = typing.Literal["classification", "segmentation"]
"""Types of supported tasks."""

TargetType: typing.TypeAlias = typing.Literal["binary", "multiclass", "multilabel"]
"""Types of classifiers/segmenters we support.

We distinguish target types by looking at sample target values of available databases.

* ``binary``: single (binary) target, where negative labels are set to zero and
   positives to 1.
* ``multiclass``: multiple (binary) outputs, one-hot encoded where
  negative/positive are encoded as in the binary case. Each sample is assigned
  exactly one, and only one, label.
* ``multilabel``: multiple outputs, where each sample may have more than one
  label.
"""
