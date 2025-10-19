# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the aggregated Montgomery-Shenzhen-Indian-TBX11k dataset."""

import importlib

import pytest
from click.testing import CliRunner


@pytest.mark.parametrize(
    "name,tbx11k_name",
    [
        ("default", "v1_healthy_vs_atb"),
        ("fold_0", "v1_fold_0"),
        ("fold_1", "v1_fold_1"),
        ("fold_2", "v1_fold_2"),
        ("fold_3", "v1_fold_3"),
        ("fold_4", "v1_fold_4"),
        ("fold_5", "v1_fold_5"),
        ("fold_6", "v1_fold_6"),
        ("fold_7", "v1_fold_7"),
        ("fold_8", "v1_fold_8"),
        ("fold_9", "v1_fold_9"),
        ("default", "v2_others_vs_atb"),
        ("fold_0", "v2_fold_0"),
        ("fold_1", "v2_fold_1"),
        ("fold_2", "v2_fold_2"),
        ("fold_3", "v2_fold_3"),
        ("fold_4", "v2_fold_4"),
        ("fold_5", "v2_fold_5"),
        ("fold_6", "v2_fold_6"),
        ("fold_7", "v2_fold_7"),
        ("fold_8", "v2_fold_8"),
        ("fold_9", "v2_fold_9"),
    ],
)
def test_split_consistency(name: str, tbx11k_name: str):
    montgomery = importlib.import_module(
        f".{name}", "mednet.config.classify.data.montgomery"
    ).datamodule

    shenzhen = importlib.import_module(
        f".{name}", "mednet.config.classify.data.shenzhen"
    ).datamodule

    indian = importlib.import_module(
        f".{name}", "mednet.config.classify.data.indian"
    ).datamodule

    tbx11k = importlib.import_module(
        f".{tbx11k_name}", "mednet.config.classify.data.tbx11k"
    ).datamodule

    combined = importlib.import_module(
        f".{tbx11k_name}",
        "mednet.config.classify.data.montgomery_shenzhen_indian_tbx11k",
    ).datamodule

    montgomery_loader = importlib.import_module(
        ".montgomery", "mednet.data.classify"
    ).RawDataLoader

    shenzhen_loader = importlib.import_module(
        ".shenzhen", "mednet.data.classify"
    ).RawDataLoader

    indian_loader = importlib.import_module(
        ".indian", "mednet.data.classify"
    ).RawDataLoader

    tbx11k_loader = importlib.import_module(
        ".tbx11k", "mednet.data.classify"
    ).RawDataLoader

    for split in ("train", "validation", "test"):
        assert montgomery.splits[split][0][0] == combined.splits[split][0][0]
        assert isinstance(montgomery.splits[split][0][1], montgomery_loader)
        assert isinstance(combined.splits[split][0][1], montgomery_loader)

        assert shenzhen.splits[split][0][0] == combined.splits[split][1][0]
        assert isinstance(shenzhen.splits[split][0][1], shenzhen_loader)
        assert isinstance(combined.splits[split][1][1], shenzhen_loader)

        assert indian.splits[split][0][0] == combined.splits[split][2][0]
        assert isinstance(indian.splits[split][0][1], indian_loader)
        assert isinstance(combined.splits[split][2][1], indian_loader)

        assert tbx11k.splits[split][0][0] == combined.splits[split][3][0]
        assert isinstance(tbx11k.splits[split][0][1], tbx11k_loader)
        assert isinstance(combined.splits[split][3][1], tbx11k_loader)


@pytest.mark.parametrize(
    "dataset",
    [
        "train",
    ],
)
@pytest.mark.parametrize(
    "tbx11k_name",
    [
        ("v1_healthy_vs_atb"),
    ],
)
def test_batch_uniformity(tbx11k_name: str, dataset: str):
    combined = importlib.import_module(
        f".{tbx11k_name}",
        "mednet.config.classify.data.montgomery_shenzhen_indian_tbx11k",
    ).datamodule

    combined.model_transforms = []  # should be done before setup()
    combined.setup("predict")  # sets up all datasets

    loader = combined.predict_dataloader()[dataset]

    limit = 5  # limit load checking
    for batch in loader:
        if limit == 0:
            break
        assert len(batch) == 3  # image, target, name


@pytest.mark.slow
@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
@pytest.mark.skip_if_rc_var_not_set("datadir.shenzhen")
@pytest.mark.skip_if_rc_var_not_set("datadir.indian")
@pytest.mark.skip_if_rc_var_not_set("datadir.tbx11k")
def test_database_check():
    from mednet.scripts.database import check

    runner = CliRunner()
    result = runner.invoke(check, ["montgomery-shenzhen-indian-tbx11k-v1"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"
