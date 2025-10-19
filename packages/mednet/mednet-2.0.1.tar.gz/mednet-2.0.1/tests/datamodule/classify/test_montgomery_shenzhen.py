# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the aggregated Montgomery-Shenzhen dataset."""

import importlib

import pytest
from click.testing import CliRunner


@pytest.mark.parametrize(
    "name",
    [
        "default",
        "fold_0",
        "fold_1",
        "fold_2",
        "fold_3",
        "fold_4",
        "fold_5",
        "fold_6",
        "fold_7",
        "fold_8",
        "fold_9",
    ],
)
def test_split_consistency(name: str):
    montgomery = importlib.import_module(
        f".{name}", "mednet.config.classify.data.montgomery"
    ).datamodule

    shenzhen = importlib.import_module(
        f".{name}", "mednet.config.classify.data.shenzhen"
    ).datamodule

    combined = importlib.import_module(
        f".{name}", "mednet.config.classify.data.montgomery_shenzhen"
    ).datamodule

    montgomery_loader = importlib.import_module(
        ".montgomery", "mednet.data.classify"
    ).RawDataLoader

    shenzhen_loader = importlib.import_module(
        ".shenzhen", "mednet.data.classify"
    ).RawDataLoader

    for split in ("train", "validation", "test"):
        assert montgomery.splits[split][0][0] == combined.splits[split][0][0]
        assert isinstance(montgomery.splits[split][0][1], montgomery_loader)
        assert isinstance(combined.splits[split][0][1], montgomery_loader)

        assert shenzhen.splits[split][0][0] == combined.splits[split][1][0]
        assert isinstance(shenzhen.splits[split][0][1], shenzhen_loader)
        assert isinstance(combined.splits[split][1][1], shenzhen_loader)


@pytest.mark.slow
@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
@pytest.mark.skip_if_rc_var_not_set("datadir.shenzhen")
def test_database_check():
    from mednet.scripts.database import check

    runner = CliRunner()
    result = runner.invoke(check, ["montgomery-shenzhen"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"
