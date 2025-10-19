# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for HIV-TB dataset."""

import importlib
import pathlib

import click.testing
import pytest
import testing.database


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("fold-0", dict(train=174, validation=44, test=25)),
        ("fold-1", dict(train=174, validation=44, test=25)),
        ("fold-2", dict(train=174, validation=44, test=25)),
        ("fold-3", dict(train=175, validation=44, test=24)),
        ("fold-4", dict(train=175, validation=44, test=24)),
        ("fold-5", dict(train=175, validation=44, test=24)),
        ("fold-6", dict(train=175, validation=44, test=24)),
        ("fold-7", dict(train=175, validation=44, test=24)),
        ("fold-8", dict(train=175, validation=44, test=24)),
        ("fold-9", dict(train=175, validation=44, test=24)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.classify.data.hivtb", f"{split}.json"),
        lengths=lengths,
        prefixes=("HIV-TB_Algorithm_study_X-rays",),
        possible_labels=(0, 1),
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.hivtb")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["--limit=10", "hivtb-f0"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.hivtb")
@pytest.mark.parametrize(
    "dataset",
    [
        "train",
        "validation",
        "test",
    ],
)
@pytest.mark.parametrize(
    "name",
    [
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
def test_loading(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.classify.data.hivtb"
    ).datamodule

    datamodule.model_transforms = []  # should be done before setup()
    datamodule.setup("predict")  # sets up all datasets

    loader = datamodule.predict_dataloader()[dataset]

    limit = 3  # limit load checking
    for batch in loader:
        if limit == 0:
            break
        testing.database.check_loaded_batch(
            batch,
            batch_size=1,
            color_planes=1,
            prefixes=("HIV-TB_Algorithm_study_X-rays",),
            possible_labels=(0, 1),
            expected_num_labels=1,
            expected_meta_size=2,
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.hivtb")
def test_loaded_image_quality(datadir: pathlib.Path):
    reference_histogram_file = (
        datadir / "histograms/raw_data/histograms_hivtb_fold_0.json"
    )

    datamodule = importlib.import_module(
        ".fold_0", "mednet.config.classify.data.hivtb"
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    testing.database.check_image_quality(datamodule, reference_histogram_file)
