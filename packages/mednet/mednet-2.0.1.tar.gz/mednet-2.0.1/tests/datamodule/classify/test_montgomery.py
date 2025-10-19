# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for Montgomery dataset."""

import importlib
import pathlib

import click.testing
import pytest
import testing.database


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("default", dict(train=88, validation=22, test=28)),
        ("fold-0", dict(train=99, validation=25, test=14)),
        ("fold-1", dict(train=99, validation=25, test=14)),
        ("fold-2", dict(train=99, validation=25, test=14)),
        ("fold-3", dict(train=99, validation=25, test=14)),
        ("fold-4", dict(train=99, validation=25, test=14)),
        ("fold-5", dict(train=99, validation=25, test=14)),
        ("fold-6", dict(train=99, validation=25, test=14)),
        ("fold-7", dict(train=99, validation=25, test=14)),
        ("fold-8", dict(train=100, validation=25, test=13)),
        ("fold-9", dict(train=100, validation=25, test=13)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.classify.data.montgomery", f"{split}.json"),
        lengths=lengths,
        prefixes=("CXR_png/MCUCXR_0",),
        possible_labels=(0, 1),
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["montgomery"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
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
def test_loading(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}",
        "mednet.config.classify.data.montgomery",
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
            prefixes=("CXR_png/MCUCXR_0",),
            possible_labels=(0, 1),
            expected_num_labels=1,
            expected_meta_size=2,
        )
        limit -= 1


@pytest.mark.slow
@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_raw_transforms_image_quality(datadir: pathlib.Path):
    datamodule = importlib.import_module(
        ".default",
        "mednet.config.classify.data.montgomery",
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    reference_histogram_file = (
        datadir / "histograms" / "raw_data" / "histograms_montgomery_default.json"
    )

    # Are we working with the original or pre-processed data set?
    # -> We retrieve the first sample and check its shape, if it is of the
    # expected size (4020x4892 pixels).  If not, we are working with a
    # preprocessed version of the database.  In this case, we check the
    # reference histogram against another file.
    is_original = (
        datamodule.unshuffled_train_dataloader().dataset[0]["image"].shape[-1] == 4892
    )
    if not is_original:
        reference_histogram_file = (
            reference_histogram_file.parent
            / "histograms_montgomery_preprocessed_default.json"
        )

    # Uncomment the next line to re-write the reference histogram
    # testing.database.write_image_quality_histogram(datamodule, reference_histogram_file)
    testing.database.check_image_quality(datamodule, reference_histogram_file)


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
@pytest.mark.parametrize("model_name", ["alexnet", "densenet", "pasa"])
def test_model_transforms_image_quality(datadir: pathlib.Path, model_name: str):
    datamodule = importlib.import_module(
        ".default",
        "mednet.config.classify.data.montgomery",
    ).datamodule

    model = importlib.import_module(
        f".{model_name}",
        "mednet.config.classify.models",
    ).model

    datamodule.model_transforms = model.model_transforms
    datamodule.setup("predict")

    reference_histogram_file = (
        datadir
        / "histograms"
        / "models"
        / f"histograms_{model_name}_montgomery_default.json"
    )

    testing.database.check_image_quality(
        datamodule,
        reference_histogram_file,
        compare_type="statistical",
        pearson_coeff_threshold=0.005,
    )
