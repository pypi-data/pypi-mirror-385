# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for stare dataset."""

import importlib

import click.testing
import pytest
import testing.database


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("ah", dict(train=10, test=10)),
        ("vk", dict(train=10, test=10)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.segment.data.stare", f"{split}.json"),
        lengths=lengths,
        prefixes=["stare-images/im0"],
        possible_labels=[],
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.stare")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["stare"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.stare")
@pytest.mark.parametrize(
    "dataset",
    ["train", "test"],
)
@pytest.mark.parametrize(
    "name",
    ["ah", "vk"],
)
def test_loading(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.segment.data.stare"
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
            prefixes=["stare-images/im0"],
            possible_labels=[],
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.stare")
def test_raw_transforms_image_quality(datadir):
    reference_histogram_file = datadir / "histograms/raw_data/histograms_stare_ah.json"

    datamodule = importlib.import_module(
        ".ah", "mednet.config.segment.data.stare"
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    testing.database.check_image_quality(datamodule, reference_histogram_file)


@pytest.mark.skip_if_rc_var_not_set("datadir.stare")
@pytest.mark.parametrize("model_name", ["lwnet"])
def test_model_transforms_image_quality(datadir, model_name):
    reference_histogram_file = (
        datadir / f"histograms/models/histograms_{model_name}_stare_ah.json"
    )

    datamodule = importlib.import_module(
        ".ah", "mednet.config.segment.data.stare"
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
