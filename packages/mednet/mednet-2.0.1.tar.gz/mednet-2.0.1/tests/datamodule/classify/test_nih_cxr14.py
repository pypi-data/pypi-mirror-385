# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for NIH CXR-14 dataset."""

import importlib

import click.testing
import pytest
import testing.database


def test_binarize_findings():
    import numpy
    import torch

    from mednet.data.classify.nih_cxr14 import RADIOLOGICAL_FINDINGS, binarize_findings

    for i, k in enumerate(RADIOLOGICAL_FINDINGS):
        assert (
            binarize_findings([k])
            == torch.tensor(numpy.eye(1, len(RADIOLOGICAL_FINDINGS), i, dtype=float))
        ).all()

    cases = {
        (): [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        (0, 3, 13): [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        (1, 2): [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        (4, 5, 7, 9, 10, 11): [0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0],
    }

    for key, value in cases.items():
        assert (
            binarize_findings([RADIOLOGICAL_FINDINGS[k] for k in key])
            == torch.tensor(numpy.array(value)).float()
        ).all()


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("default.json.bz2", dict(train=98637, validation=6350, test=7133)),
        ("first-100.json", dict(train=100, validation=100, test=100)),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(split: str, lengths: dict[str, int]):
    from mednet.data.classify.nih_cxr14 import RADIOLOGICAL_FINDINGS
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.classify.data.nih_cxr14", f"{split}"),
        lengths=lengths,
        prefixes=("images/000",),
        possible_labels=RADIOLOGICAL_FINDINGS,
    )


testdata = [
    ("default", "train", 1),  # 1 x 14
    ("default", "validation", 1),  # 1 x 14
    ("default", "test", 1),  # 1 x 14
    ("first_100", "train", 1),  # 1 x 14
    ("first_100", "validation", 1),  # 1 x 14
    ("first_100", "test", 1),  # 1 x 14
]


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["--limit=10", "nih-cxr14"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
@pytest.mark.parametrize("name,dataset,num_labels", testdata)
def test_loading(name: str, dataset: str, num_labels: int):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.classify.data.nih_cxr14"
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
            prefixes=("images/000",),
            possible_labels=(0, 1),
            expected_num_labels=num_labels,
            # expected_image_shape=(1, 1024, 1024),
            expected_meta_size=2,
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
def test_raw_transforms_image_quality(datadir):
    datamodule = importlib.import_module(
        ".default",
        "mednet.config.classify.data.nih_cxr14",
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    reference_histogram_file = (
        datadir / "histograms/raw_data/histograms_nih_cxr14_default.json"
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
            / "histograms_nih_cxr14_preprocessed_default.json"
        )

    testing.database.check_image_quality(datamodule, reference_histogram_file)


@pytest.mark.skip_if_rc_var_not_set("datadir.cxr8")
@pytest.mark.parametrize("model_name", ["pasa"])
def test_model_transforms_image_quality(datadir, model_name):
    reference_histogram_file = (
        datadir / f"histograms/models/histograms_{model_name}_nih_cxr14_default.json"
    )

    datamodule = importlib.import_module(
        ".default",
        "mednet.config.classify.data.nih_cxr14",
    ).datamodule

    model = importlib.import_module(
        f".{model_name}",
        "mednet.config.classify.models",
    ).model

    datamodule.model_transforms = model.model_transforms
    datamodule.setup("predict")

    testing.database.check_image_quality(
        datamodule,
        reference_histogram_file,
        compare_type="statistical",
        pearson_coeff_threshold=0.005,
    )
