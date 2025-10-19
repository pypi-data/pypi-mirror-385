# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Test code for database splits."""

from mednet.data.split import JSONDatabaseSplit


def test_json_loading(datadir):
    # tests if we can build a simple JSON loader for the Iris Flower dataset

    database_split = JSONDatabaseSplit(datadir / "iris.json")

    assert len(database_split["train"]) == 75
    for k in database_split["train"]:
        for f in range(4):
            assert isinstance(k[f], int | float)
        assert isinstance(k[4], str)

    assert len(database_split["test"]) == 75
    for k in database_split["test"]:
        for f in range(4):
            assert isinstance(k[f], int | float)
        assert isinstance(k[4], str)
