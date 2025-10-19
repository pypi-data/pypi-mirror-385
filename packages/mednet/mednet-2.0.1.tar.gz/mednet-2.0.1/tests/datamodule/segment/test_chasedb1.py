# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for chasedb1 dataset."""

import importlib
import pathlib

import click.testing
import pytest
import testing.database


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("first-annotator", dict(train=8, test=20)),
        ("second-annotator", dict(train=8, test=20)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.segment.data.chasedb1", f"{split}.json"),
        lengths=lengths,
        prefixes=["Image_"],
        possible_labels=[],
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.chasedb1")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["chasedb1"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.chasedb1")
@pytest.mark.parametrize("dataset", ["train", "test"])
@pytest.mark.parametrize("name", ["first_annotator", "second_annotator"])
def test_loading(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.segment.data.chasedb1"
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
            color_planes=3,
            expected_num_labels=1,
            expected_meta_size=3,
            prefixes=["Image_"],
            possible_labels=[],
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.chasedb1")
def test_raw_transforms_image_quality(datadir: pathlib.Path):
    reference_histogram_file = (
        datadir / "histograms/raw_data/histograms_chasedb1_first_annotator.json"
    )

    datamodule = importlib.import_module(
        ".first_annotator", "mednet.config.segment.data.chasedb1"
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    testing.database.check_image_quality(datamodule, reference_histogram_file)


@pytest.mark.skip_if_rc_var_not_set("datadir.chasedb1")
@pytest.mark.parametrize("model_name", ["lwnet"])
def test_model_transforms_image_quality(datadir: pathlib.Path, model_name):
    reference_histogram_file = (
        datadir
        / f"histograms/models/histograms_{model_name}_chasedb1_first_annotator.json"
    )

    datamodule = importlib.import_module(
        ".first_annotator", "mednet.config.segment.data.chasedb1"
    ).datamodule

    model = importlib.import_module(
        f".{model_name}", "mednet.config.segment.models"
    ).model

    datamodule.model_transforms = model.model_transforms
    datamodule.setup("predict")

    testing.database.check_image_quality(
        datamodule,
        reference_histogram_file,
        compare_type="statistical",
        pearson_coeff_threshold=0.005,
    )
