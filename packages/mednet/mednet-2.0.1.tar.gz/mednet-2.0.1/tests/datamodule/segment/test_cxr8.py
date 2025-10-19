# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for cxr8 dataset."""

import importlib
import pathlib

import click.testing
import pytest
import testing.database


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("default", dict(train=78484, validation=11212, test=22424)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.segment.data.cxr8", f"{split}.json.bz2"),
        lengths=lengths,
        prefixes=[],
        possible_labels=[],
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["--limit=10", "cxr8"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
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
        "default",
    ],
)
def test_loading(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}",
        "mednet.config.segment.data.cxr8",
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
            prefixes=[],
            possible_labels=[],
            expected_num_labels=1,
            expected_meta_size=3,
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
def test_raw_transforms_image_quality(datadir: pathlib.Path):
    datamodule = importlib.import_module(
        ".default",
        "mednet.config.segment.data.cxr8",
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    reference_histogram_file = (
        datadir / "histograms/raw_data/histograms_cxr8_default.json"
    )

    # Are we working with the original or pre-processed data set?
    # -> We retrieve the first sample and check its shape, if it is of the
    # expected size (1024x1024 pixels).  If not, we are working with a
    # preprocessed version of the database.  In this case, we check the
    # reference histogram against another file.
    is_original = (
        datamodule.unshuffled_train_dataloader().dataset[0]["image"].shape[-1] == 1024
    )
    if not is_original:
        reference_histogram_file = (
            reference_histogram_file.parent
            / "histograms_cxr8_preprocessed_default.json"
        )

    testing.database.check_image_quality(datamodule, reference_histogram_file)


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
@pytest.mark.parametrize(
    "model_name",
    ["lwnet"],
)
def test_model_transforms_image_quality(datadir: pathlib.Path, model_name):
    reference_histogram_file = (
        datadir / f"histograms/models/histograms_{model_name}_cxr8_default.json"
    )

    datamodule = importlib.import_module(
        ".default",
        "mednet.config.segment.data.cxr8",
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
