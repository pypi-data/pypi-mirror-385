# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for PadChest dataset."""

import importlib
import pathlib

import click.testing
import pytest
import testing.database


@pytest.mark.parametrize(
    "split,lengths",
    [
        # ("idiap.json.bz2", dict(train=96269)),  ## many labels
        ("tb-idiap.json", dict(train=200, test=50)),  # 0: no-tb, 1: tb
        (
            "no-tb-idiap.json.bz2",
            dict(train=54371, validation=4052),
        ),  # 14 labels
        ("cardiomegaly-idiap.json", dict(train=40)),  # 14 labels
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.classify.data.padchest", split),
        lengths=lengths,
        prefixes=("",),
        possible_labels=(0, 1),
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.padchest")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["--limit=10", "padchest-idiap"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


testdata = [
    ("idiap", "train", 193),
    ("idiap", "test", 1),
    ("tb_idiap", "train", 1),
    ("no_tb_idiap", "train", 14),
    ("cardiomegaly_idiap", "train", 14),
]


@pytest.mark.skip_if_rc_var_not_set("datadir.padchest")
@pytest.mark.parametrize("name,dataset,num_labels", testdata)
def test_loading(name: str, dataset: str, num_labels: int):
    datamodule = importlib.import_module(
        f".{name}",
        "mednet.config.classify.data.padchest",
    ).datamodule

    datamodule.model_transforms = []  # should be done before setup()
    datamodule.setup("predict")  # sets up all datasets

    if dataset in datamodule.predict_dataloader():
        loader = datamodule.predict_dataloader()[dataset]

        limit = 3  # limit load checking
        for batch in loader:
            if limit == 0:
                break
            testing.database.check_loaded_batch(
                batch,
                batch_size=1,
                color_planes=1,
                prefixes=("",),
                possible_labels=(0, 1),
                expected_num_labels=num_labels,
                expected_meta_size=2,
            )
            limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.padchest")
def test_loaded_image_quality(datadir: pathlib.Path):
    reference_histogram_file = (
        datadir / "histograms/raw_data/histograms_padchest_idiap.json"
    )

    datamodule = importlib.import_module(
        ".idiap", "mednet.config.classify.data.padchest"
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    testing.database.check_image_quality(datamodule, reference_histogram_file)
