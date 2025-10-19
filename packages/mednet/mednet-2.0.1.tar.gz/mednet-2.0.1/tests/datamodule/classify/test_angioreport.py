# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the AngioReport dataset."""

import importlib

import click.testing
import pytest
import testing.database


def test_binarize_findings():
    import numpy
    import torch

    from mednet.data.classify.angioreport import IMPRESSION_TYPE_ICGA, binarize_findings

    for i, k in enumerate(IMPRESSION_TYPE_ICGA):
        assert (
            binarize_findings([k])
            == torch.tensor(numpy.eye(1, len(IMPRESSION_TYPE_ICGA), i, dtype=float))
        ).all()

    cases = {
        (): [0, 0, 0, 0, 0, 0, 0, 0],
        (0, 3): [1, 0, 0, 1, 0, 0, 0, 0],
        (1, 2): [0, 1, 1, 0, 0, 0, 0, 0],
        (0, 4, 5, 7): [1, 0, 0, 0, 1, 1, 0, 1],
    }

    for key, value in cases.items():
        assert (
            binarize_findings([IMPRESSION_TYPE_ICGA[k] for k in key])
            == torch.tensor(numpy.array(value)).float()
        ).all()


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("hyperftype", dict(train=1312, validation=287, test=278)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.classify.data.angioreport", f"{split}.json"),
        lengths=lengths,
        prefixes=("Train/Train",),
        possible_labels=(0, 1, 2, 3, 4),
    )


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("impression", dict(train=1310, validation=280, test=287)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency_multilabel(split: str, lengths: dict[str, int]):
    from mednet.data.classify.angioreport import IMPRESSION_TYPE_ICGA
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.classify.data.angioreport", f"{split}.json"),
        lengths=lengths,
        prefixes=("Train/Train",),
        possible_labels=IMPRESSION_TYPE_ICGA,
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.angioreport")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["--limit=10", "angioreport-hyperftype"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.angioreport")
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
        "hyperftype",
    ],
)
def test_loading(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.classify.data.angioreport"
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
            prefixes=("Train/Train",),
            possible_labels=(0, 1, 2, 3, 4),
            expected_num_labels=1,
            expected_meta_size=2,
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.angioreport")
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
        "impression",
    ],
)
def test_loading_impression(name: str, dataset: str):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.classify.data.angioreport"
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
            prefixes=("Train/Train",),
            possible_labels=(0, 1),
            expected_num_labels=1,
            expected_meta_size=2,
        )
        limit -= 1
