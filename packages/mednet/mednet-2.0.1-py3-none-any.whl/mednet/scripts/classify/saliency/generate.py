# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import typing

import click
from clapper.click import ResourceOption, verbosity_option

from ....models.classify.typing import SaliencyMapAlgorithm
from ...click import ConfigCommand
from ...logging import setup_cli_logger
from ...utils import get_ckpt_metric_mode

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Generate saliency maps using GradCAM for all prediction dataloaders on a
   DataModule, using a pre-trained DenseNet model, and saves them as
   numpy-pickeled objects on the output directory:

   .. code:: sh

      mednet classify saliency generate -vv densenet tbx11k-v1-healthy-vs-atb --saliency-map-algorithm="gradcam" --weight=path/to/model-at-lowest-validation-loss.ckpt --output-folder=path/to/output

""",
)
@click.option(
    "--model",
    "-m",
    help="""A lightning module instance implementing the network architecture
    (not the weights, necessarily) to be used for inference.  Currently, only
    supports pasa and densenet models.""",
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--datamodule",
    "-d",
    help="""A lightning DataModule that will be asked for prediction data
    loaders. Typically, this includes all configured splits in a DataModule,
    however this is not a requirement.  A DataModule that returns a single
    dataloader for prediction (wrapped in a dictionary) is acceptable.""",
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--output-folder",
    "-o",
    help="Directory in which to store saliency maps (created if does not exist)",
    required=True,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=pathlib.Path,
    ),
    default="saliency-maps",
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--device",
    "-x",
    help='A string indicating the device to use (e.g. "cpu" or "cuda:0")',
    show_default=True,
    required=True,
    default="cpu",
    cls=ResourceOption,
)
@click.option(
    "--cache-samples/--no-cache-samples",
    help="If set to True, loads the sample into memory, "
    "otherwise loads them at runtime.",
    required=True,
    show_default=True,
    default=False,
    cls=ResourceOption,
)
@click.option(
    "--weight",
    "-w",
    help="""Path or URL to a pretrained model file (`.ckpt` extension),
    corresponding to the architecture set with `--model`.  Optionally, you may
    also pass a directory containing the result of a training session, in which
    case either the best (lowest validation) or latest model will be loaded.""",
    required=True,
    cls=ResourceOption,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--parallel",
    "-P",
    help="""Use multiprocessing for data loading: if set to -1 (default),
    disables multiprocessing data loading.  Set to 0 to enable as many data
    loading instances as processing cores available in the system.  Set to
    >= 1 to enable that many multiprocessing instances for data loading.""",
    type=click.IntRange(min=-1),
    show_default=True,
    required=True,
    default=-1,
    cls=ResourceOption,
)
@click.option(
    "--saliency-map-algorithm",
    "-s",
    help="""Saliency map algorithm to be used.""",
    type=click.Choice(
        typing.get_args(SaliencyMapAlgorithm),
        case_sensitive=False,
    ),
    default="gradcam",
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--target-class",
    "-C",
    help="""This option should only be used with multiclass models.  It
    defines the class to target for saliency estimation. Can be either set to
    "all" or "highest". "highest" (the default), means only saliency maps for
    the class with the highest activation will be generated.""",
    required=False,
    type=click.Choice(
        ["highest", "all"],
        case_sensitive=False,
    ),
    default="highest",
    cls=ResourceOption,
)
@click.option(
    "--positive-only/--no-positive-only",
    "-z/-Z",
    help="""If set, and the model chosen has a single output (binary), then
    saliency maps will only be generated for samples of the positive class.
    This option has no effect for multiclass models.""",
    default=False,
    cls=ResourceOption,
)
@click.option(
    "--only-dataset",
    "-S",
    help="""If set, will only run the command for the named dataset on the
    provided datamodule, skipping any other dataset.""",
    cls=ResourceOption,
)
@verbosity_option(logger=logger, expose_value=False)
def generate(
    model,
    datamodule,
    output_folder,
    device,
    cache_samples,
    weight,
    parallel,
    saliency_map_algorithm,
    target_class,
    positive_only,
    only_dataset,
    **_,
) -> None:  # numpydoc ignore=PR01
    """Generate saliency maps for locations on input images that affected the
    prediction.

    The quality of saliency information depends on the saliency map
    algorithm and trained model.
    """

    from ....engine.classify.saliency.generator import run
    from ....engine.device import DeviceManager
    from ....engine.trainer import validate_model_datamodule
    from ....models.classify.model import Model as ClassificationModel
    from ....utils.checkpointer import get_checkpoint_to_run_inference
    from ...utils import save_json_metadata

    validate_model_datamodule(model, datamodule)
    assert isinstance(model, ClassificationModel)

    logger.info(f"Output folder: {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)

    device_manager = DeviceManager(device)

    # sets-up the data module
    datamodule.cache_samples = cache_samples
    datamodule.model_transforms = list(model.model_transforms)
    datamodule.batch_size = 1
    datamodule.parallel = -1
    datamodule.prepare_data()
    datamodule.setup(stage="predict")

    if weight.is_dir():
        metric, mode = get_ckpt_metric_mode(weight / "train.meta.json")
        weight = get_checkpoint_to_run_inference(weight, metric, mode)

    logger.info(f"Loading checkpoint from `{weight}`...")
    model = type(model).load_from_checkpoint(weight, strict=False)

    save_json_metadata(
        output_file=output_folder / "generation.meta.json",
        datamodule=datamodule,
        model=model,
        output_folder=output_folder,
        device=device,
        cache_samples=cache_samples,
        weight=weight,
        parallel=parallel,
        saliency_map_algorithm=saliency_map_algorithm,
        target_class=target_class,
        positive_only=positive_only,
        only_dataset=only_dataset,
    )

    run(
        model=model,
        datamodule=datamodule,
        device_manager=device_manager,
        saliency_map_algorithm=saliency_map_algorithm,
        target_class=target_class,
        positive_only=positive_only,
        output_folder=output_folder,
        only_dataset=only_dataset,
    )
