# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Engine and functions for human interpretability analysis."""

import logging
import pathlib
import typing

import lightning.pytorch
import numpy
import numpy.typing
from torchvision import tv_tensors
from tqdm import tqdm

logger = logging.getLogger(__name__)

SaliencyMap: typing.TypeAlias = (
    typing.Sequence[typing.Sequence[float]] | numpy.typing.NDArray[numpy.double]
)
BinaryMask: typing.TypeAlias = numpy.typing.NDArray[numpy.bool_]


def _compute_avg_saliency_focus(
    saliency_map: SaliencyMap,
    gt_mask: BinaryMask,
) -> float:
    """Integrate the saliency map over the ground-truth boxes and normalizes by
    total bounding-box area.

    This function will integrate (sum) the value of the saliency map over the
    ground-truth bounding boxes and normalize it by the total area covered by
    all ground-truth bounding boxes.

    Parameters
    ----------
    saliency_map
        A real-valued saliency-map that conveys regions used for
        classification in the original sample.
    gt_mask
        Ground-truth mask containing the bounding boxes of the ground-truth
        drawn as ``True`` values.

    Returns
    -------
    float
        A single floating-point number representing the Average saliency focus.
    """

    area = gt_mask.sum()
    if area == 0:
        return 0.0

    return numpy.sum(saliency_map * gt_mask) / area


def _compute_proportional_energy(
    saliency_map: SaliencyMap,
    gt_mask: BinaryMask,
) -> float:
    """Calculate how much activation lies within the ground truth boxes
    compared to the total sum of the activations (integral).

    Parameters
    ----------
    saliency_map
        A real-valued saliency-map that conveys regions used for
        classification in the original sample.
    gt_mask
        Ground-truth mask containing the bounding boxes of the ground-truth
        drawn as ``True`` values.

    Returns
    -------
    float
        A single floating-point number representing the proportional energy.
    """

    denominator = numpy.sum(saliency_map)

    if denominator == 0.0:
        return 0.0

    return float(numpy.sum(saliency_map * gt_mask) / denominator)  # type: ignore


def _compute_binary_mask(
    gt_bboxes: tv_tensors.BoundingBoxes,
    saliency_map: SaliencyMap,
) -> BinaryMask:
    """Compute a binary mask for the saliency map using BoundingBoxes.

    The binary_mask will be ON/True where the gt boxes are located.

    Parameters
    ----------
    gt_bboxes
        Ground-truth bounding boxes in the format ``(x, y, width,
        height)``.
    saliency_map
        A real-valued saliency-map that conveys regions used for
        classification in the original sample.

    Returns
    -------
    BinaryMask
        A numpy array of the same size as saliency_map with
        the value False everywhere except at the positions inside
        the bounding boxes, which will be True.
    """

    binary_mask = numpy.zeros_like(saliency_map, dtype=numpy.bool_)
    if gt_bboxes.format != tv_tensors.BoundingBoxFormat.XYXY:
        raise ValueError(
            f"Only boundingBoxes of format xyxy are supported. Got {gt_bboxes.format}."
        )

    for bbox in gt_bboxes:
        binary_mask[
            bbox.data[1] : bbox.data[1] + (bbox.data[3] - bbox.data[1]),
            bbox.data[0] : bbox.data[0] + (bbox.data[2] - bbox.data[0]),
        ] = True
    return binary_mask


def _process_sample(
    gt_bboxes: tv_tensors.BoundingBoxes,
    saliency_map: SaliencyMap,
) -> tuple[float, float]:
    """Calculate the metrics for a single sample.

    Parameters
    ----------
    gt_bboxes
        A list of ground-truth bounding boxes.
    saliency_map
        A real-valued saliency-map that conveys regions used for
        classification in the original sample.

    Returns
    -------
    tuple[float, float]
        A tuple containing the following values:

        * Proportional energy
        * Average saliency focus
    """

    binary_mask = _compute_binary_mask(gt_bboxes, saliency_map)

    return (
        _compute_proportional_energy(saliency_map, binary_mask),
        _compute_avg_saliency_focus(saliency_map, binary_mask),
    )


def run(
    input_folder: pathlib.Path,
    target_label: int,
    datamodule: lightning.pytorch.LightningDataModule,
    only_dataset: str | None,
) -> dict[str, list[typing.Any]]:
    """Compute the proportional energy and average saliency focus for a given
    target label in a DataModule.

    Parameters
    ----------
    input_folder
        Directory in which the saliency maps are stored for a specific
        visualization type.
    target_label
        The label to target for evaluating interpretability metrics. Samples
        contining any other label are ignored.
    datamodule
        The lightning DataModule to iterate on.
    only_dataset
        If set, will only run this code for the named dataset on the provided
        datamodule, skipping any other datasets.

    Returns
    -------
        A dictionary where keys are dataset names in the provided DataModule,
        and values are lists containing sample information alongside metrics
        calculated:

        * Sample name (str)
        * Sample target class (int)
        * Proportional energy (float)
        * Average saliency focus (float)
    """

    retval: dict[str, list[typing.Any]] = {}

    # TODO: This loads the images from the dataset, but they are not useful at
    # this point.  Possibly using the contents of ``datamodule.splits`` can
    # substantially speed this up.
    for dataset_name, dataset_loader in datamodule.predict_dataloader().items():
        if only_dataset is not None and dataset_name != only_dataset:
            logger.warning(
                f"Skipping processing for dataset `{dataset_name}` following user request..."
            )
            continue

        logger.info(
            f"Estimating interpretability metrics for dataset `{dataset_name}`...",
        )
        retval[dataset_name] = []

        for sample in tqdm(
            dataset_loader,
            desc="batches",
            leave=False,
            disable=None,
        ):
            name = str(sample["name"][0])
            label = int(sample["target"].item())

            if label != target_label:
                # we add the entry for dataset completeness, but do not treat
                # it
                retval[dataset_name].append([name, label])
                continue

            # TODO: This is very specific to the TBX11k system for labelling
            # regions of interest.  We need to abstract from this to support more
            # datasets and other ways to annotate.
            bboxes: tv_tensors.BoundingBoxes | None = sample.get("bboxes", None)

            if bboxes is None:
                logger.warning(
                    f"Sample `{name}` does not contain bounding-box information. "
                    f"No localization metrics can be calculated in this case. "
                    f"Skipping...",
                )
                # we add the entry for dataset completeness
                retval[dataset_name].append([name, label])
                continue

            # we fully process this entry
            retval[dataset_name].append(
                [
                    name,
                    label,
                    *_process_sample(
                        bboxes[0],
                        numpy.load(
                            input_folder / pathlib.Path(name).with_suffix(".npy"),
                        ),
                    ),
                ],
            )

    return retval
