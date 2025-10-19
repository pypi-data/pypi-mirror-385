# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for TBX11K dataset."""

import importlib
import pathlib
import typing

import click.testing
import pytest
import testing.database
import torch


@pytest.mark.parametrize(
    "split,lengths,prefixes",
    [
        (
            "v1-healthy-vs-atb",
            dict(train=2767, validation=706, test=957),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-0",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-1",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-2",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-3",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-4",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-5",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-6",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-7",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-8",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v1-fold-9",
            dict(train=3177, validation=810, test=443),
            ("imgs/health", "imgs/tb"),
        ),
        (
            "v2-others-vs-atb",
            dict(train=5241, validation=1335, test=1793),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-0",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-1",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-2",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-3",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-4",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-5",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-6",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-7",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-8",
            dict(train=6003, validation=1529, test=837),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
        (
            "v2-fold-9",
            dict(train=6003, validation=1530, test=836),
            ("imgs/health", "imgs/sick", "imgs/tb"),
        ),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(
    split: str, lengths: dict[str, int], prefixes: typing.Sequence[str]
):
    from mednet.data.split import make_split

    testing.database.check_split(
        make_split("mednet.config.classify.data.tbx11k", f"{split}.json"),
        lengths=lengths,
        prefixes=prefixes,
        possible_labels=(0, 1),
    )


def check_loaded_batch(
    batch,
    batch_size: int,
    color_planes: int,
    prefixes: typing.Sequence[str],
    possible_labels: typing.Sequence[int],
    expected_num_labels: int,
    expected_image_shape: tuple[int, ...] | None = None,
):
    """Check the consistency of an individual (loaded) batch.

    Parameters
    ----------
    batch
        The loaded batch to be checked.
    batch_size
        The mini-batch size.
    color_planes
        The number of color planes in the images.
    prefixes
        Each file named in a split should start with at least one of these
        prefixes.
    possible_labels
        These are the list of possible labels contained in any split.
    expected_num_labels
        The expected number of labels each sample should have.
    expected_image_shape
        The expected shape of the image (num_channels, width, height).
    """

    # label, name and radiological sign bounding-boxes, image, bb targets
    assert len(batch) == 5

    assert isinstance(batch, dict)
    assert isinstance(batch["image"], torch.Tensor)
    assert batch["image"].shape[0] == batch_size  # mini-batch size
    assert batch["image"].shape[1] == color_planes
    assert batch["image"].shape[2] == batch["image"].shape[3]  # image is square

    if expected_image_shape:
        assert all([data.shape == expected_image_shape for data in batch["image"]])

    assert "target" in batch
    assert all([k in possible_labels for k in batch["target"]])

    if expected_num_labels:
        assert len(batch["target"]) == expected_num_labels

    assert "name" in batch
    assert all(
        [any([k.startswith(j) for j in prefixes]) for k in batch["name"]],
    )

    assert "bboxes" in batch

    for sample, target, bboxes, bbox_targets in zip(
        batch["image"],
        batch["target"],
        batch["bboxes"],
        batch["bbox_targets"],
    ):
        # there must be a sign indicated on the image, if active TB is detected
        if target[0] == 1:
            assert len(bboxes) != 0

        # eif label == 0:  # not true, may have TBI!
        #    assert len(bboxes) == 0

        # asserts all bounding boxes are within the raw image width and height
        if bboxes is not None:
            for bbox in bboxes:
                if target[0] == 1:
                    assert (bbox_targets == 1).all()
                else:
                    assert (bbox_targets == 0).all()
                assert (
                    bbox.data[2] < sample.shape[2]
                )  # check bbox is not outside image width
                assert bbox.data[3] < sample.shape[1]  # same with height
        else:
            assert bbox_targets is None

    # use the code below to view generated images
    # from torchvision.transforms.v2.functional import to_pil_image
    # to_pil_image(batch["image"]).show()
    # __import__("pdb").set_trace()


@pytest.mark.skip_if_rc_var_not_set("datadir.tbx11k")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["--limit=10", "tbx11k-v1-f0"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"

    result = runner.invoke(check, ["--limit=10", "tbx11k-v2-f0"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.tbx11k")
@pytest.mark.parametrize(
    "dataset",
    [
        "train",
        "validation",
        "test",
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
@pytest.mark.parametrize(
    "name,prefixes",
    [
        ("v1_healthy_vs_atb", ("imgs/health", "imgs/tb")),
        ("v1_fold_0", ("imgs/health", "imgs/tb")),
        ("v1_fold_1", ("imgs/health", "imgs/tb")),
        ("v1_fold_2", ("imgs/health", "imgs/tb")),
        ("v1_fold_3", ("imgs/health", "imgs/tb")),
        ("v1_fold_4", ("imgs/health", "imgs/tb")),
        ("v1_fold_5", ("imgs/health", "imgs/tb")),
        ("v1_fold_6", ("imgs/health", "imgs/tb")),
        ("v1_fold_7", ("imgs/health", "imgs/tb")),
        ("v1_fold_8", ("imgs/health", "imgs/tb")),
        ("v1_fold_9", ("imgs/health", "imgs/tb")),
        ("v2_others_vs_atb", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_0", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_1", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_2", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_3", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_4", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_5", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_6", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_7", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_8", ("imgs/health", "imgs/sick", "imgs/tb")),
        ("v2_fold_9", ("imgs/health", "imgs/sick", "imgs/tb")),
    ],
    ids=testing.database.id_function,  # just changes how pytest prints it
)
def test_loading(name: str, dataset: str, prefixes: typing.Sequence[str]):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.classify.data.tbx11k"
    ).datamodule

    datamodule.model_transforms = []  # should be done before setup()
    datamodule.setup("predict")  # sets up all datasets

    loader = datamodule.predict_dataloader()[dataset]

    limit = 50  # limit load checking
    for batch in loader:
        if limit == 0:
            break
        check_loaded_batch(
            batch,
            batch_size=1,
            color_planes=3,
            prefixes=prefixes,
            possible_labels=(0, 1),
            expected_num_labels=1,
            expected_image_shape=(3, 512, 512),
        )
        limit -= 1


@pytest.mark.parametrize(
    "split",
    [
        "v1_fold_0",
        "v2_fold_0",
    ],
)
@pytest.mark.skip_if_rc_var_not_set("datadir.tbx11k")
def test_loaded_image_quality(datadir: pathlib.Path, split):
    reference_histogram_file = (
        datadir / f"histograms/raw_data/histograms_tbx11k_{split}.json"
    )

    datamodule = importlib.import_module(
        f".{split}", "mednet.config.classify.data.tbx11k"
    ).datamodule

    datamodule.model_transforms = []
    datamodule.batch_size = 2
    datamodule.setup("predict")

    testing.database.check_image_quality(datamodule, reference_histogram_file)
