# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Splits for :py:mod:`.data.classify.angioreport` database.

Each json file is associated with one task among those available in the
dataset. All of them contain the last frame image for each eye.
Moreover there is no patient overlap among the train, validation and test
splits, meaning that, if both eyes of a patient are available, they will always be
assigned to the same split to avoid data leakage.
"""
