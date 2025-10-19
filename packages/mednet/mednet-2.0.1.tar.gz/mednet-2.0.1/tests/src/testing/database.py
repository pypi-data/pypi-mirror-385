# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Utilities for testing databases."""

import typing

import numpy
import torch

from mednet.data.split import JSONDatabaseSplit
from mednet.data.typing import DatabaseSplit


def check_split(
    split: DatabaseSplit,
    lengths: dict[str, int],
    prefixes: typing.Sequence[str],
    possible_labels: typing.Sequence[int | str],
):
    """Run a simple consistency check on the data split.

    Parameters
    ----------
    split
        An instance of DatabaseSplit.
    lengths
        A dictionary that contains keys matching those of the split (this
        will be checked).  The values of the dictionary should correspond
        to the sizes of each of the datasets in the split.
    prefixes
        Each file named in a split should start with at least one of these
        prefixes.
    possible_labels
        These are the list of possible labels contained in any split.
    """

    assert len(split) == len(lengths)

    for k in lengths.keys():
        # dataset must have been declared
        assert k in split

        assert len(split[k]) == lengths[k]
        for s in split[k]:
            # check filename prefixes match, if prefixes were passed
            if prefixes:
                assert any([s[0].startswith(k) for k in prefixes]), (
                    f"Sample with name {s[0]} does not start with any of the "
                    f"prefixes in {prefixes}"
                )

            # check if labels match, if labels were passed
            if possible_labels:
                if isinstance(s[1], list):
                    assert all([k in possible_labels for k in s[1]])
                else:
                    assert s[1] in possible_labels


def check_loaded_batch(
    batch,
    batch_size: int,
    color_planes: int,
    prefixes: typing.Sequence[str],
    possible_labels: typing.Sequence[int],
    expected_num_labels: int,
    expected_meta_size: int,
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
    expected_meta_size
        The expected number of elements on the meta-information dictionary
        on every sample.
    expected_image_shape
        The expected shape of the image (num_channels, width, height).
    """

    assert isinstance(batch, dict)
    assert len(batch) == (expected_meta_size + 1)  # account for image

    assert "image" in batch
    assert isinstance(batch["image"], torch.Tensor)
    assert batch["image"].shape[0] == batch_size  # mini-batch size
    assert batch["image"].shape[1] == color_planes

    if expected_image_shape:
        assert all(
            [data.shape == expected_image_shape for data in batch["image"]],
        )

    assert "target" in batch

    if possible_labels:
        assert all([k in possible_labels for k in batch["target"].ravel()])

    if expected_num_labels:
        assert len(batch["target"]) == expected_num_labels

    assert "name" in batch
    if prefixes:
        assert all(
            [any([k.startswith(j) for j in prefixes]) for k in batch["name"]],
        )

    # use the code below to view generated images
    # from torchvision.transforms.v2.functional import to_pil_image
    # to_pil_image(batch["image"]).show()
    # __import__("pdb").set_trace()


def check_image_quality(
    datamodule,
    reference_histogram_file,
    compare_type="equal",
    pearson_coeff_threshold=0.005,
):
    """Check image quality.

    Parameters
    ----------
    datamodule
        The datamodule to be checked.
    reference_histogram_file
        A reference histogram file to compare the loaded data to.
    compare_type
        The type of comparison to be used.
    pearson_coeff_threshold
        The acceptable correlation coefficient to check.
    """
    ref_histogram_splits = JSONDatabaseSplit(reference_histogram_file)

    for split_name in ref_histogram_splits:
        raw_samples = datamodule.splits[split_name][0][0]

        # It is not possible to get a sample from a Dataset by name/path,
        # only by index. This creates a dict of sample name to dataset
        # index.
        raw_samples_indices = {}
        for idx, rs in enumerate(raw_samples):
            raw_samples_indices[rs[0]] = idx

        for ref_hist_path, ref_hist_data in ref_histogram_splits[split_name]:
            # Get index in the dataset that will return the data
            # corresponding to the specified sample name
            dataset_sample_index = raw_samples_indices[ref_hist_path]

            image_tensor = datamodule._datasets[split_name][  # noqa: SLF001
                dataset_sample_index
            ]["image"]

            histogram = []
            for color_channel in image_tensor:
                color_channel = numpy.multiply(
                    color_channel.numpy(),
                    255,
                ).astype(int)
                histogram.extend(
                    numpy.histogram(
                        color_channel,
                        bins=256,
                        range=(0, 256),
                    )[0].tolist(),
                )

            if compare_type == "statistical":
                # Compute pearson coefficients between histogram and
                # reference and check the similarity within a certain
                # threshold
                pearson_coeffs = numpy.corrcoef(histogram, ref_hist_data)
                assert 1 - pearson_coeff_threshold <= pearson_coeffs[0][1] <= 1

            else:
                assert histogram == ref_hist_data


def id_function(val: typing.Any) -> str:
    """Convert value to string representation.

    Treats dictionary specially.

    Parameters
    ----------
    val
        The value to be converted.

    Returns
    -------
        A string representation of the value.
    """

    match val:
        case str() | int():
            return str(val)
        case dict():
            return "{" + "".join(
                ",".join(
                    [id_function(k) + ":" + id_function(v) for k, v in val.items()]
                )
            )
        case tuple():
            return ",".join([id_function(k) for k in val])
        case _:
            return repr(val)
