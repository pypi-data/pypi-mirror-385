# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import sys

import click
from clapper.click import ResourceOption, verbosity_option

from .click import ConfigCommand
from .logging import setup_cli_logger

logger = setup_cli_logger()


@click.command(
    entry_point_group="mednet.config",
    cls=ConfigCommand,
    epilog="""Examples:

1. Pre-process the Montgomery (classification) dataset using model transforms
   from the pasa model.

   .. code:: sh

      mednet database preprocess -vv montgomery pasa

2. Pre-process the CXR8 (segmentation) dataset using model transforms
   from the lwnet model.

   .. code:: sh

      mednet database preprocess -vv cxr8 lwnet

""",
)
@click.option(
    "--output-folder",
    "-o",
    help="Directory in which to store results (created if does not exist)",
    required=True,
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=pathlib.Path,
    ),
    default="results",
    show_default=True,
    cls=ResourceOption,
)
@click.option(
    "--model",
    "-m",
    help="A lightning module instance implementing the network to be trained",
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--datamodule",
    "-d",
    help="A lightning DataModule containing the training and validation sets.",
    required=True,
    cls=ResourceOption,
)
@click.option(
    "--limit",
    "-l",
    help="Limit preprocessing to the first N samples in each split in the "
    "configuration, making the job sensibly faster. Set it to "
    "zero (default) to preprocess everything.",
    required=True,
    type=click.IntRange(0),
    default=0,
    show_default=True,
)
@click.option(
    "--grayscale",
    "-g",
    help="For images to be grayscale, if set.",
    required=False,
    is_flag=True,
    show_default=True,
)
@verbosity_option(logger=logger, expose_value=False)
def preprocess(
    output_folder,
    model,
    datamodule,
    limit,
    grayscale,
    **_,
) -> None:  # numpydoc ignore=PR01
    """Run pre-processing on databases using a set of model transforms.

    This command can be used to generate more compact versions of the databases
    that can be used to speed-up data loading. This is done by running both
    data loading and model transforms so that stored samples are small enough,
    and require no transformations when loading.
    """

    from torchvision.transforms.v2.functional import rgb_to_grayscale, to_pil_image

    # report model/transforms options - set data augmentations
    logger.info(f"Network model: {type(model).__module__}.{type(model).__name__}")

    datamodule.model_transforms = model.model_transforms
    datamodule.setup(stage="predict")
    loaders = datamodule.predict_dataloader()

    for split_name, loader in loaders.items():
        if limit == 0:
            click.secho(
                f"Preprocessing all {len(loader)} samples of split "
                f"`{split_name}` at database `{datamodule.database_name}`...",
                fg="yellow",
            )
            loader_limit = sys.maxsize
        else:
            click.secho(
                f"Preprocessing first {limit} samples of dataset "
                f"`{split_name}` at database `{datamodule.database_name}`...",
                fg="yellow",
            )
            loader_limit = limit

        # the for loop will trigger raw data loading (ie. user code), protect it
        for sample_order, batch in enumerate(loader):
            if loader_limit == 0:
                break
            logger.info(
                f"{batch['name'][0]}: "
                f"{[s for s in batch['image'][0].shape]}@{batch['image'][0].dtype}",
            )

            sample_info = datamodule.splits[split_name][0][0][sample_order]

            # basic sanity check
            assert sample_info[0] == batch["name"][0]

            # we are always interested on the images
            output_image = output_folder / sample_info[0]
            output_image.parent.mkdir(parents=True, exist_ok=True)
            tensor_image = batch["image"][0]

            match tensor_image.shape[0]:
                case 1:
                    image = to_pil_image((255 * tensor_image).byte(), "L")
                case 3:
                    if grayscale:
                        image = to_pil_image(
                            (255 * rgb_to_grayscale(tensor_image)).byte(), "L"
                        )
                    else:
                        image = to_pil_image((255 * tensor_image).byte(), "RGB")
                case _:
                    raise NotImplementedError(
                        f"Cannot preprocess images with {tensor_image.shape[1]} planes"
                    )

            image.save(output_image)

            if datamodule.task == "segmentation":
                # we are also interested on the targets
                output_target = output_folder / sample_info[1]
                output_target.parent.mkdir(parents=True, exist_ok=True)
                tensor_target = batch["target"][0]
                target = to_pil_image((255 * tensor_target).byte(), "L")
                target.save(output_target)

                if len(sample_info) >= 3:
                    # we are also interested on the masks
                    output_mask = output_folder / sample_info[2]
                    output_mask.parent.mkdir(parents=True, exist_ok=True)
                    tensor_mask = batch["mask"][0]
                    mask = to_pil_image((255 * tensor_mask).byte(), "L")
                    mask.save(output_mask)

            loader_limit -= 1
