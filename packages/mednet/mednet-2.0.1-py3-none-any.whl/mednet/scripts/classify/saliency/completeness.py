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

1. Calculate the ROAD scores using GradCAM, for an existing dataset
   configuration and stores them in .json files:

   .. code:: sh

      mednet classify saliency completeness -vv pasa tbx11k-v1-healthy-vs-atb --saliency-map-algorithm="gradcam" --device="cuda" --weight=path/to/model-at-lowest-validation-loss.ckpt --output-json=path/to/completeness-scores.json

""",
)
@click.option(
    "--model",
    "-m",
    help="""A lightning module instance implementing the network architecture
    (not the weights, necessarily) to be used for inference.  Currently, only
    supports pasa and densenet models.""",
    required=True,
    type=click.UNPROCESSED,
    cls=ResourceOption,
)
@click.option(
    "--datamodule",
    "-d",
    help="""A lightning DataModule that will be asked for prediction DataLoaders.
    Typically, this includes all configured splits in a DataModule,
    however this is not a requirement.  A DataModule that returns a single
    DataLoader for prediction (wrapped in a dictionary) is acceptable.""",
    required=True,
    type=click.UNPROCESSED,
    cls=ResourceOption,
)
@click.option(
    "--output-folder",
    "-o",
    help="""Name of the folder where to store the output .json file containing all
    measures.""",
    required=True,
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        path_type=pathlib.Path,
        writable=True,
    ),
    default="results",
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
    help="""Path or URL to pretrained model file (`.ckpt` extension),
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
    help="""Use multiprocessing for data loading processing: if set to -1
    (default), disables multiprocessing.  Set to 0 to enable as many data
    processing instances as processing cores available in the system.  Set to
    >= 1 to enable that many multiprocessing instances.  Note that if you
    activate this option, then you must use --device=cpu, as using a GPU
    concurrently is not supported.""",
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
    "--percentile",
    "-e",
    help="""One or more percentiles (percent x100) integer values indicating
    the proportion of pixels to perturb in the original image to calculate both
    MoRF and LeRF scores.""",
    multiple=True,
    default=[20, 40, 60, 80],
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--only-dataset",
    "-S",
    help="""If set, will only run the command for the named dataset on the
    provided datamodule, skipping any other dataset.""",
    cls=ResourceOption,
)
@click.option(
    "--plot/--no-plot",
    "-Q",
    help="""If set, then also produces figures containing the plots of
    score histograms.""",
    required=True,
    show_default=True,
    default=True,
    cls=ResourceOption,
)
@verbosity_option(logger=logger, expose_value=False)
def completeness(
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
    percentile,
    only_dataset,
    plot,
    **_,
) -> None:  # numpydoc ignore=PR01
    """Evaluate saliency map algorithm completeness using RemOve And Debias
    (ROAD).

    For the selected saliency map algorithm, evaluates the completeness of
    explanations using the RemOve And Debias (ROAD) algorithm. The ROAD
    algorithm was first described at :cite:p:`rong_consistent_2022`. It estimates explainability
    (in the completeness sense) of saliency mapping algorithms by substituting
    relevant pixels in the input image by a local average, re-running
    prediction on the altered image, and measuring changes in the output
    classification score when said perturbations are in place.  By substituting
    most or least relevant pixels with surrounding averages, the ROAD algorithm
    estimates the importance of such elements in the produced saliency map.  As
    2023, this measurement technique is considered to be one of the
    state-of-the-art metrics of explainability.

    This program outputs a .json file containing the ROAD evaluations (using
    most-relevant-first, or MoRF, and least-relevant-first, or LeRF for each
    sample in the DataModule. Values for MoRF and LeRF represent averages by
    removing 20, 40, 60 and 80% of most or least relevant pixels respectively
    from the image, and averaging results for all these percentiles.

    .. note::

       This application is relatively slow when processing a large DataModule
       with many (positive) samples.
    """

    import matplotlib.backends.backend_pdf

    from ....engine.classify.saliency.completeness import run
    from ....engine.classify.saliency.utils import make_plots, make_table
    from ....engine.device import DeviceManager
    from ....engine.trainer import validate_model_datamodule
    from ....models.classify.model import Model as ClassificationModel
    from ....utils.checkpointer import get_checkpoint_to_run_inference
    from ...utils import save_json_metadata, save_json_with_backup

    if device in ("cuda", "mps") and (parallel == 0 or parallel > 1):
        raise RuntimeError(
            f"The number of multiprocessing instances is set to {parallel} and "
            f"you asked to use a GPU (device = `{device}`). The currently "
            f"implementation can only handle a single GPU.  Either disable GPU "
            f"utilisation or set the number of multiprocessing instances to "
            f"one, or disable multiprocessing entirely (ie. set it to -1).",
        )

    validate_model_datamodule(model, datamodule)
    assert isinstance(model, ClassificationModel)

    device_manager = DeviceManager(device)

    datamodule.cache_samples = cache_samples
    datamodule.model_transforms = list(model.model_transforms)
    datamodule.batch_size = 1
    datamodule.parallel = parallel
    datamodule.prepare_data()
    datamodule.setup(stage="predict")

    output_json = output_folder / "completeness.json"

    if weight.is_dir():
        metric, mode = get_ckpt_metric_mode(weight / "train.meta.json")
        weight = get_checkpoint_to_run_inference(weight, metric, mode)

    logger.info(f"Loading checkpoint from `{weight}`...")
    model = type(model).load_from_checkpoint(weight, strict=False)

    # stores all information we can think of, to reproduce this later
    save_json_metadata(
        output_file=output_json.with_suffix(".meta.json"),
        model=model,
        datamodule=datamodule,
        output_json=output_json,
        device=device,
        cache_samples=cache_samples,
        weight=weight,
        parallel=parallel,
        saliency_map_algorithm=saliency_map_algorithm,
        target_class=target_class,
        positive_only=positive_only,
        percentile=percentile,
        only_dataset=only_dataset,
        plot=plot,
    )

    logger.info(
        f"Evaluating RemOve And Debias (ROAD) average scores for "
        f"algorithm `{saliency_map_algorithm}` with percentiles "
        f"`{', '.join([str(k) for k in percentile])}`...",
    )
    results = run(
        model=model,
        datamodule=datamodule,
        device_manager=device_manager,
        saliency_map_algorithm=saliency_map_algorithm,
        target_class=target_class,
        positive_only=positive_only,
        percentiles=percentile,
        parallel=parallel,
        only_dataset=only_dataset,
    )

    logger.info(f"Saving output file to `{str(output_json)}`...")
    save_json_with_backup(output_json, results)

    table = make_table(
        results=results,
        indexes={3: "ROAD (MoRF)", 4: "ROAD (LeRF)", 5: "ROAD (avg)"},
        format_="rst",
    )
    output_table = output_json.with_suffix(".rst")
    logger.info(f"Saving output summary table to `{str(output_table)}`...")
    with output_table.open("w") as f:
        f.write(table)
    click.echo(table)

    # Plots histograms, if the user asked to do so.
    if plot:
        figure_path = output_json.with_suffix(".pdf")
        logger.info(f"Saving plots to `{str(figure_path)}`...")
        with matplotlib.backends.backend_pdf.PdfPages(figure_path) as pdf:
            for fig in make_plots(
                results=results,
                indexes={3: "ROAD (MoRF)", 4: "ROAD (LeRF)", 5: "ROAD (avg)"},
            ):
                pdf.savefig(fig)
