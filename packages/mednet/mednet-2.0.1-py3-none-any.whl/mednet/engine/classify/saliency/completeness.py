# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Engine and functions for score completeness analysis."""

import functools
import logging
import multiprocessing
import typing

import lightning.pytorch
import numpy as np
import torch
import tqdm
from pytorch_grad_cam.metrics.road import (
    ROADLeastRelevantFirstAverage,
    ROADMostRelevantFirstAverage,
)
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from ....data.typing import Sample
from ....engine.device import DeviceManager
from ....models.classify.typing import SaliencyMapAlgorithm

logger = logging.getLogger(__name__)


class SigmoidClassifierOutputTarget(torch.nn.Module):
    """Consider output to be a sigmoid.

    Parameters
    ----------
    category
        The category.
    """

    def __init__(self, category):
        self.category = category

    def __call__(self, model_output):
        sigmoid_output = torch.sigmoid(model_output)
        if len(sigmoid_output.shape) == 1:
            return sigmoid_output[self.category]
        return sigmoid_output[:, self.category]


def _calculate_road_scores(
    model: lightning.pytorch.LightningModule,
    images: torch.Tensor,
    output_num: int,
    saliency_map_callable: typing.Callable,
    percentiles: typing.Sequence[int],
) -> tuple[float, float, float]:
    """Calculate average ROAD scores for different removal percentiles.

    This function calculates ROAD scores by averaging the scores for
    different removal (hardcoded) percentiles, for a single input image, a
    given visualization method, and a target class.

    Parameters
    ----------
    model
        Neural network model (e.g. pasa).
    images
        A batch of input images to use for evaluating the ROAD scores.  Currently,
        we only support batches with a single image.
    output_num
        Target output neuron to take into consideration when evaluating the
        saliency maps and calculating ROAD scores.
    saliency_map_callable
        A callable saliency-map generator from grad-cam.
    percentiles
        A sequence of percentiles (percent x100) integer values indicating the
        proportion of pixels to perturb in the original image to calculate both
        MoRF and LeRF scores.

    Returns
    -------
    tuple[float, float, float]
        A 3-tuple containing floating point numbers representing the
        most-relevant-first average score (``morf``), least-relevant-first
        average score (``lerf``) and the combined value (``(lerf-morf)/2``).
    """

    saliency_map = saliency_map_callable(
        input_tensor=images,
        targets=[ClassifierOutputTarget(output_num)],
    )

    cam_metric_roadmorf_avg = ROADMostRelevantFirstAverage(
        percentiles=percentiles,
    )
    cam_metric_roadlerf_avg = ROADLeastRelevantFirstAverage(
        percentiles=percentiles,
    )

    # Calculate ROAD scores for all percentiles and average - this is NOT the
    # current processing bottleneck.  If you want to optimise anyting, look at
    # the evaluation of the perturbation using scipy.sparse at the
    # NoisyLinearImputer, part of the grad-cam package (submodule
    # ``metrics.road``).
    metric_target = [SigmoidClassifierOutputTarget(output_num)]

    morf_scores = cam_metric_roadmorf_avg(
        input_tensor=images,
        cams=saliency_map,
        model=model,
        targets=metric_target,
    )

    lerf_scores = cam_metric_roadlerf_avg(
        input_tensor=images,
        cams=saliency_map,
        model=model,
        targets=metric_target,
    )

    return (
        float(morf_scores.item()),
        float(lerf_scores.item()),
        float(lerf_scores.item() - morf_scores.item()) / 2.0,
    )


def _process_sample(
    sample: Sample,
    model: lightning.pytorch.LightningModule,
    device: torch.device,
    saliency_map_callable: typing.Callable,
    target_class: typing.Literal["highest", "all"],
    positive_only: bool,
    percentiles: typing.Sequence[int],
) -> list:
    """Process a single sample.

    Helper function to :py:func:`run` to be used in multiprocessing contexts.

    Parameters
    ----------
    sample
        The Sample to process.
    model
        Neural network model (e.g. pasa).
    device
        The device to process samples on.
    saliency_map_callable
        A callable saliency-map generator from grad-cam.
    target_class
        Class to target for saliency estimation. Can be set to
        "all" or "highest". "highest" is default, which means
        only saliency maps for the class with the highest
        activation will be generated.
    positive_only
        If set, and the model chosen has a single output (binary), then
        saliency maps will only be generated for samples of the positive class.
    percentiles
        A sequence of percentiles (percent x100) integer values indicating the
        proportion of pixels to perturb in the original image to calculate both
        MoRF and LeRF scores.

    Returns
    -------
    list
        A list containing the following items for a particular sample:
        * The relative path to the sample.
        * The label.
        * An index to the specified target_class.
        * The computed ROAD scores.
    """

    name: str = sample["name"][0]
    label: int = int(sample["target"].item())
    image = sample["image"]

    # in binary classification systems, negative labels may be skipped
    if positive_only and (model.num_classes == 1) and (label == 0):
        return [name, label]

    # chooses target outputs to generate saliency maps for
    if model.num_classes > 1:  # type: ignore
        if target_class == "all":
            # test all outputs
            for output_num in range(model.num_classes):  # type: ignore
                results = _calculate_road_scores(
                    model,
                    image,
                    output_num,
                    saliency_map_callable,
                    percentiles,
                )
                return [name, label, output_num, *results]

        else:
            # we will figure out the output with the highest value and
            # evaluate the saliency mapping technique over it.
            outputs = saliency_map_callable.activations_and_grads(image)  # type: ignore
            output_nums = np.argmax(outputs.cpu().data.numpy(), axis=-1)
            assert len(output_nums) == 1
            results = _calculate_road_scores(
                model,
                image,
                output_nums[0],
                saliency_map_callable,
                percentiles,
            )
            return [name, label, output_nums[0], *results]

    # default route for binary classification
    results = _calculate_road_scores(
        model,
        image,
        0,
        saliency_map_callable,
        percentiles,
    )
    return [name, label, 0, *results]


def run(
    model: lightning.pytorch.LightningModule,
    datamodule: lightning.pytorch.LightningDataModule,
    device_manager: DeviceManager,
    saliency_map_algorithm: SaliencyMapAlgorithm,
    target_class: typing.Literal["highest", "all"],
    positive_only: bool,
    percentiles: typing.Sequence[int],
    parallel: int,
    only_dataset: str | None,
) -> dict[str, list[typing.Any]]:
    """Evaluate ROAD scores for all samples in a DataModule.

    The ROAD algorithm was first described in :cite:p:`rong_consistent_2022`. It estimates
    explainability (in the completeness sense) of saliency maps by substituting
    relevant pixels in the input image by a local average, re-running
    prediction on the altered image, and measuring changes in the output
    classification score when said perturbations are in place.  By substituting
    the most or least relevant pixels with surrounding averages, the ROAD algorithm
    estimates the importance of such elements in the produced saliency map.  As
    of 2023, this measurement technique is considered to be one of the
    state-of-the-art metrics of explainability.

    This function returns a dictionary containing most-relevant-first (remove a
    percentile of the most relevant pixels), least-relevant-first (remove a
    percentile of the least relevant pixels), and combined ROAD evaluations per
    sample for a particular saliency mapping algorithm.

    Parameters
    ----------
    model
        Neural network model (e.g. pasa).
    datamodule
        The lightning DataModule to iterate on.
    device_manager
        An internal device representation, to be used for training and
        validation.  This representation can be converted into a pytorch device
        or a lightning accelerator setup.
    saliency_map_algorithm
        The algorithm for saliency map estimation to use.
    target_class
        (Use only with multi-label models) Which class to target for CAM
        calculation. Can be set to "all" or "highest". "highest" is
        default, which means only saliency maps for the class with the highest
        activation will be generated.
    positive_only
        If set, saliency maps will only be generated for positive samples (ie.
        label == 1 in a binary classification task).  This option is ignored on
        a multi-class output model.
    percentiles
        A sequence of percentiles (percent x100) integer values indicating the
        proportion of pixels to perturb in the original image to calculate both
        MoRF and LeRF scores.
    parallel
        Use multiprocessing for data processing: if set to -1, disables
        multiprocessing.  Set to 0 to enable as many data processing instances
        as processing cores available in the system.  Set to >= 1 to enable
        that many multiprocessing instances for data processing.
    only_dataset
        If set, will only run this code for the named dataset on the provided
        datamodule, skipping any other datasets.

    Returns
    -------
    dict[str, list[typing.Any]]
        A dictionary where keys are dataset names in the provide DataModule,
        and values are lists containing sample information alongside metrics
        calculated:

        * Sample name
        * Sample target class
        * The model output number used for the ROAD analysis (0, for binary
          classifers as there is typically only one output).
        * ``morf``: ROAD most-relevant-first average of percentiles 20, 40, 60 and
          80 (a.k.a. AOPC-MoRF).
        * ``lerf``: ROAD least-relevant-first average of percentiles 20, 40, 60 and
          80 (a.k.a. AOPC-LeRF).
        * combined: Average ROAD combined score by evaluating ``(lerf-morf)/2``
          (a.k.a. AOPC-Combined).
    """

    from ....models.classify.densenet import Densenet
    from ....models.classify.pasa import Pasa
    from .generator import _create_saliency_map_callable

    if isinstance(model, Pasa):
        if saliency_map_algorithm == "fullgrad":
            raise ValueError(
                "Fullgrad saliency map algorithm is not supported for the "
                "Pasa model.",
            )
        target_layers = [model.fc14]  # Last non-1x1 Conv2d layer
    elif isinstance(model, Densenet):
        target_layers = [
            model.model.features.denseblock4.denselayer16.conv2,  # type: ignore
        ]
    else:
        raise TypeError(f"Model of type `{type(model)}` is not yet supported.")

    if device_manager.device_type in ("cuda", "mps") and (
        parallel == 0 or parallel > 1
    ):
        raise RuntimeError(
            f"The number of multiprocessing instances is set to {parallel} and "
            f"you asked to use a GPU (device = `{device_manager.device_type}`"
            f"). The current implementation can only handle a single GPU.  "
            f"Either disable GPU usage, set the number of "
            f"multiprocessing instances to one, or disable multiprocessing "
            "entirely (ie. set it to -1).",
        )

    # prepares model for evaluation, cast to target device
    device = device_manager.torch_device()
    model.eval()

    saliency_map_callable = _create_saliency_map_callable(
        saliency_map_algorithm,
        model,
        target_layers,  # type: ignore
    )

    retval: dict[str, list[typing.Any]] = {}

    # our worker function
    _process = functools.partial(
        _process_sample,
        model=model,
        device=device,
        saliency_map_callable=saliency_map_callable,
        target_class=target_class,
        positive_only=positive_only,
        percentiles=percentiles,
    )

    for k, v in datamodule.predict_dataloader().items():
        if only_dataset is not None and k != only_dataset:
            logger.warning(
                f"Skipping processing for dataset `{k}` following user request..."
            )
            continue

        retval[k] = []

        if parallel < 0:
            logger.info(
                f"Computing ROAD scores for dataset `{k}` in the current "
                f"process context...",
            )
            for sample in tqdm.tqdm(
                v,
                desc="samples",
                leave=False,
                disable=None,
            ):
                retval[k].append(_process(sample))

        else:
            instances = parallel or multiprocessing.cpu_count()
            logger.info(
                f"Computing ROAD scores for dataset `{k}` using {instances} "
                f"processes...",
            )
            with multiprocessing.Pool(instances) as p:
                retval[k] = list(tqdm.tqdm(p.imap(_process, v), total=len(v)))

    return retval
