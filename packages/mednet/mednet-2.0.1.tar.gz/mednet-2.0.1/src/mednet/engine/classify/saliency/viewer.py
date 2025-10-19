# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Engine and functions for visualization of saliency maps."""

import logging
import pathlib
import typing

import lightning.pytorch
import numpy
import numpy.typing
import PIL.Image
import PIL.ImageColor
import PIL.ImageDraw
import torchvision.transforms.v2.functional
from torchvision import tv_tensors
from tqdm import tqdm

logger = logging.getLogger(__name__)


def _overlay_saliency_map(
    image: PIL.Image.Image,
    saliencies: numpy.typing.NDArray[numpy.double],
    colormap: typing.Literal[  # we accept any "Sequential" colormap from mpl
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "cividis",
        "Greys",
        "Purples",
        "Blues",
        "Greens",
        "Oranges",
        "Reds",
        "YlOrBr",
        "YlOrRd",
        "OrRd",
        "PuRd",
        "RdPu",
        "BuPu",
        "GnBu",
        "PuBu",
        "YlGnBu",
        "PuBuGn",
        "BuGn",
        "YlGn",
    ],
    image_weight: float,
) -> PIL.Image.Image:
    """Create an overlayed represention of the saliency map on the original
    image.

    This is a slightly modified version of the show_cam_on_image implementation in:
    https://github.com/jacobgil/pytorch-grad-cam, but uses matplotlib instead
    of opencv.

    Parameters
    ----------
    image
        The input image that will be overlaid with the saliency map.
    saliencies
        The saliency map that will be overlaid on the (raw) image.
    colormap
        The name of the (matplotlib) colormap to be used.
    image_weight
        The final result is ``image_weight * image + (1-image_weight) *
        saliency_map``.

    Returns
    -------
    PIL.Image.Image
        A modified version of the input ``image`` with the overlaid saliency
        map.
    """
    import matplotlib

    image_array = numpy.array(image, dtype=numpy.float32) / 255.0

    assert image_array.shape[:2] == saliencies.shape, (
        f"The shape of the saliency map ({saliencies.shape}) is different "
        f"from the shape of the input image ({image_array.shape[:2]})."
    )

    assert (
        saliencies.max() <= 1
    ), f"The input saliency map should be in the range [0, 1] (max={saliencies.max()})"

    assert (
        image_weight > 0 and image_weight < 1
    ), f"image_weight should be in the range [0, 1], but got {image_weight}"

    heatmap = matplotlib.colormaps[colormap](saliencies)

    # For pixels where the mask is zero, the original image pixels are being
    # used without a mask.
    result = numpy.where(
        saliencies[..., numpy.newaxis] == 0,
        image_array,
        (image_weight * image_array) + ((1 - image_weight) * heatmap[:, :, :3]),
    )

    return PIL.Image.fromarray((result * 255).astype(numpy.uint8), "RGB")


def _process_sample(
    raw_data: numpy.typing.NDArray[numpy.double],
    saliencies: numpy.typing.NDArray[numpy.double],
    ground_truth: tv_tensors.BoundingBoxes,
) -> PIL.Image.Image:
    """Generate an overlaid representation of the original sample and saliency
    maps.

    Parameters
    ----------
    raw_data
        The raw data representing the input sample that will be overlaid with
        saliency maps and annotations.
    saliencies
        The saliency map recovered from the model, that will be imprinted on
        the raw_data.
    ground_truth
        Ground-truth annotations that may be imprinted on the final image.

    Returns
    -------
    PIL.Image.Image
        An image with the original raw data overlaid with the different
        elements as selected by the user.
    """

    # we need a colour image to eventually overlay a (coloured) saliency map on
    # the top, draw rectangles and other annotations in coulour.  So, we force
    # it right up front.
    retval = torchvision.transforms.v2.functional.to_pil_image(raw_data).convert(
        "RGB",
    )

    retval = _overlay_saliency_map(
        retval,
        saliencies,
        colormap="plasma",
        image_weight=0.5,
    )

    if ground_truth is not None:
        retval = torchvision.transforms.v2.functional.to_pil_image(
            torchvision.utils.draw_bounding_boxes(
                tv_tensors.Image(retval), ground_truth[0], colors="green", width=2
            )
        )

    return retval


def run(
    datamodule: lightning.pytorch.LightningDataModule,
    input_folder: pathlib.Path,
    target_label: int,
    output_folder: pathlib.Path,
    show_groundtruth: bool,
    threshold: float,
):
    """Overlay saliency maps on CXR to output final images with heatmaps.

    Parameters
    ----------
    datamodule
        The Lightning DataModule to iterate on.
    input_folder
        Directory in which the saliency maps are stored for a specific
        visualization type.
    target_label
        The label to target for evaluating interpretability metrics. Samples
        contining any other label are ignored.
    output_folder
        Directory in which the resulting visualizations will be saved.
    show_groundtruth
        If set, imprint ground truth labels over the original image and
        saliency maps.
    threshold : float
        The pixel values above ``threshold`` % of max value are kept in the
        original saliency map.  Everything else is set to zero.  The value
        proposed on :cite:p:`wang_score-cam_2020` is 0.2.  Use this value if unsure.
    """

    for dataset_name, dataset_loader in datamodule.predict_dataloader().items():
        logger.info(
            f"Generating visualizations for samples (target = {target_label}) "
            f"at dataset `{dataset_name}`..."
        )

        for sample in tqdm(
            dataset_loader,
            desc="batches",
            leave=False,
            disable=None,
        ):
            # WARNING: following code assumes a batch size of 1. Will break if
            # not the case.
            name = str(sample["name"][0])
            label = int(sample["target"].item())
            data = sample["image"][0]

            if label != target_label:
                # no visualisation was generated
                continue

            saliencies = numpy.load(
                input_folder / pathlib.Path(name).with_suffix(".npy"),
            )
            saliencies[saliencies < (threshold * saliencies.max())] = 0

            # TODO: This is very specific to the TBX11k system for labelling
            # regions of interest.  We need to abstract from this to support more
            # datasets and other ways to annotate.
            if show_groundtruth:
                ground_truth = sample.get("bboxes", None)
            else:
                ground_truth = None

            # we fully process this entry
            image = _process_sample(
                data,
                saliencies,
                ground_truth,
            )

            # Save image
            output_file_path = output_folder / pathlib.Path(name).with_suffix(
                ".png",
            )
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_file_path)
