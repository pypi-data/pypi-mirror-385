# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for rimoner3 dataset."""

import importlib

import click.testing
import pytest
import testing.database


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("optic-cup-exp1", dict(train=99, test=60)),
        ("optic-cup-exp2", dict(train=99, test=60)),
        ("optic-disc-exp1", dict(train=99, test=60)),
        ("optic-disc-exp2", dict(train=99, test=60)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.segment.data.rimoner3", f"{split}.json"),
        lengths=lengths,
        prefixes=["Healthy/Stereo Images/N-", "Glaucoma and suspects/Stereo Images/"],
        possible_labels=[],
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.rimoner3")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["rimoner3-cup"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.rimoner3")
@pytest.mark.parametrize(
    "dataset",
    [
        "train",
        "test",
    ],
)
@pytest.mark.parametrize(
    "name",
    [
        "cup_exp1",
        "cup_exp2",
        "disc_exp1",
        "disc_exp2",
    ],
)
def test_loading(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}",
        "mednet.config.segment.data.rimoner3",
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
            prefixes=[
                "Healthy/Stereo Images/N-",
                "Glaucoma and suspects/Stereo Images/",
            ],
            possible_labels=[],
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.rimoner3")
def test_raw_transforms_image_quality(datadir):
    reference_histogram_file = (
        datadir / "histograms/raw_data/histograms_rimoner3_cup_exp1.json"
    )

    datamodule = importlib.import_module(
        ".cup_exp1",
        "mednet.config.segment.data.rimoner3",
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    testing.database.check_image_quality(datamodule, reference_histogram_file)


@pytest.mark.skip_if_rc_var_not_set("datadir.rimoner3")
@pytest.mark.parametrize(
    "model_name",
    ["lwnet"],
)
def test_model_transforms_image_quality(datadir, model_name):
    reference_histogram_file = (
        datadir / f"histograms/models/histograms_{model_name}_rimoner3_cup_exp1.json"
    )

    datamodule = importlib.import_module(
        ".cup_exp1",
        "mednet.config.segment.data.rimoner3",
    ).datamodule

    model = importlib.import_module(
        f".{model_name}",
        "mednet.config.segment.models",
    ).model

    datamodule.model_transforms = model.model_transforms
    datamodule.setup("predict")

    testing.database.check_image_quality(
        datamodule,
        reference_histogram_file,
        compare_type="statistical",
        pearson_coeff_threshold=0.005,
    )
