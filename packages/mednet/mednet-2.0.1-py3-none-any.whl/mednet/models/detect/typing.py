# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Definition of types related to models used in object detection tasks."""

import typing

Prediction: typing.TypeAlias = tuple[
    str,
    typing.Sequence[tuple[typing.Sequence[int], int]],
    typing.Sequence[tuple[typing.Sequence[int | float], int, float]],
]
"""The sample name, the target (boxes and labels), and the predicted value (boxes,
labels and scores)."""

PredictionSplit: typing.TypeAlias = typing.Mapping[str, typing.Sequence[Prediction]]
"""A series of predictions for different database splits."""
