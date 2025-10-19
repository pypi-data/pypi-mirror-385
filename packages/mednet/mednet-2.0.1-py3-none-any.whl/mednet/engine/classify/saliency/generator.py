# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Engine and functions for saliency map generation."""

import logging
import pathlib
import typing

import lightning.pytorch
import numpy
import torch
import torch.nn
import tqdm

from ....engine.device import DeviceManager
from ....models.classify.typing import SaliencyMapAlgorithm

logger = logging.getLogger(__name__)


def _create_saliency_map_callable(
    algo_type: SaliencyMapAlgorithm,
    model: torch.nn.Module,
    target_layers: list[torch.nn.Module] | None,
):
    """Create a class activation map (CAM) instance for a given model.

    Parameters
    ----------
    algo_type
        The algorithm to use for saliency map estimation.
    model
        Neural network model (e.g. pasa).
    target_layers
        The target layers to compute CAM for.

    Returns
    -------
        A class activation map (CAM) instance for the given model.
    """

    import pytorch_grad_cam

    match algo_type:
        case "gradcam":
            return pytorch_grad_cam.GradCAM(
                model=model,
                target_layers=target_layers,
            )
        case "scorecam":
            return pytorch_grad_cam.ScoreCAM(
                model=model,
                target_layers=target_layers,
            )
        case "fullgrad":
            return pytorch_grad_cam.FullGrad(
                model=model,
                target_layers=target_layers,
            )
        case "randomcam":
            return pytorch_grad_cam.RandomCAM(
                model=model,
                target_layers=target_layers,
            )
        case "hirescam":
            return pytorch_grad_cam.HiResCAM(
                model=model,
                target_layers=target_layers,
            )
        case "gradcamelementwise":
            return pytorch_grad_cam.GradCAMElementWise(
                model=model,
                target_layers=target_layers,
            )
        case "gradcam++" | "gradcamplusplus":
            return pytorch_grad_cam.GradCAMPlusPlus(
                model=model,
                target_layers=target_layers,
            )
        case "xgradcam":
            return pytorch_grad_cam.XGradCAM(
                model=model,
                target_layers=target_layers,
            )
        case "ablationcam":
            assert (
                target_layers is not None
            ), "AblationCAM cannot have target_layers=None"
            return pytorch_grad_cam.AblationCAM(
                model=model,
                target_layers=target_layers,
            )
        case "eigencam":
            return pytorch_grad_cam.EigenCAM(
                model=model,
                target_layers=target_layers,
            )
        case "eigengradcam":
            return pytorch_grad_cam.EigenGradCAM(
                model=model,
                target_layers=target_layers,
            )
        case "layercam":
            return pytorch_grad_cam.LayerCAM(
                model=model,
                target_layers=target_layers,
            )
        case _:
            raise ValueError(
                f"Saliency map algorithm `{algo_type}` is not currently " f"supported.",
            )


def _save_saliency_map(
    output_folder: pathlib.Path,
    name: str,
    saliency_map: torch.Tensor,
) -> None:
    """Save a saliency map to permanent storage (disk).

    Helper function to save a saliency map to disk.

    Parameters
    ----------
    output_folder
        Directory in which the resulting saliency maps will be saved.
    name
        Name of the saved file.
    saliency_map
        A real-valued saliency-map that conveys regions used for
        classification in the original sample.
    """

    n = pathlib.Path(name)
    (output_folder / n.parent).mkdir(parents=True, exist_ok=True)
    numpy.save(output_folder / n.with_suffix(".npy"), saliency_map[0])


def run(
    model: lightning.pytorch.LightningModule,
    datamodule: lightning.pytorch.LightningDataModule,
    device_manager: DeviceManager,
    saliency_map_algorithm: SaliencyMapAlgorithm,
    target_class: typing.Literal["highest", "all"],
    positive_only: bool,
    output_folder: pathlib.Path,
    only_dataset: str | None,
) -> None:
    """Apply saliency mapping techniques on input CXR, outputs pickled saliency
    maps directly to disk.

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
        The algorithm to use for saliency map estimation.
    target_class
        (Use only with multi-label models) Which class to target for CAM
        calculation. Can be either set to "all" or "highest". "highest" is
        default, which means only saliency maps for the class with the highest
        activation will be generated.
    positive_only
        If set, saliency maps will only be generated for positive samples (ie.
        label == 1 in a binary classification task).  This option is ignored on
        a multi-class output model.
    output_folder
        Where to save all the saliency maps (this path should exist before
        this function is called).
    only_dataset
        If set, will only run this code for the named dataset on the provided
        datamodule, skipping any other datasets.
    """

    from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

    from ....models.classify.densenet import Densenet
    from ....models.classify.pasa import Pasa

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

    # prepares model for evaluation, cast to target device
    device = device_manager.torch_device()
    model = model.to(device)
    model.eval()

    saliency_map_callable = _create_saliency_map_callable(
        saliency_map_algorithm,
        model,
        target_layers,  # type: ignore
    )

    for k, v in datamodule.predict_dataloader().items():
        if only_dataset is not None and k != only_dataset:
            logger.warning(
                f"Skipping processing for dataset `{k}` following user request..."
            )
            continue

        logger.info(
            f"Generating saliency maps for dataset `{k}` via "
            f"`{saliency_map_algorithm}`...",
        )

        for sample in tqdm.tqdm(v, desc="samples", leave=False, disable=None):
            name = sample["name"][0]
            target = sample["target"].item()
            image = sample["image"].to(
                device=device,
                non_blocking=torch.cuda.is_available(),
            )

            # in binary classification systems, negative targets may be skipped
            if positive_only and (model.num_classes == 1) and (target == 0):
                continue

            # chooses target outputs to generate saliency maps for
            if model.num_classes > 1:
                if target_class == "all":
                    # just blindly generate saliency maps for all outputs
                    # - make one directory for every target output and lay
                    # images there like in the original dataset.
                    for output_num in range(model.num_classes):
                        use_folder = output_folder / str(output_num)
                        saliency_map = saliency_map_callable(
                            input_tensor=image,
                            targets=[ClassifierOutputTarget(output_num)],  # type: ignore
                        )
                        _save_saliency_map(use_folder, name, saliency_map)  # type: ignore

                else:
                    # pytorch-grad-cam will figure out the output with the
                    # highest value and produce a saliency map for it - we
                    # will save it to disk.
                    use_folder = output_folder / "highest-output"
                    saliency_map = saliency_map_callable(
                        input_tensor=image,
                        # setting `targets=None` will set target to the
                        # maximum output index using
                        # ClassifierOutputTarget(max_output_index)
                        targets=None,  # type: ignore
                    )
                    _save_saliency_map(use_folder, name, saliency_map)  # type: ignore
            else:
                # binary classification model with a single output - just
                # lay all cams uniformily like the original dataset
                saliency_map = saliency_map_callable(
                    input_tensor=image,
                    targets=[
                        ClassifierOutputTarget(0),  # type: ignore
                    ],
                )
                _save_saliency_map(output_folder, name, saliency_map)  # type: ignore
