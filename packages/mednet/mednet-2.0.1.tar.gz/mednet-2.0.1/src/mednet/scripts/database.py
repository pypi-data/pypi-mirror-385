# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import click
from clapper.click import AliasedGroup, verbosity_option

from .logging import setup_cli_logger

logger = setup_cli_logger()


def _get_raw_databases() -> dict[str, dict[str, str | list]]:
    """Return a list of all supported (raw) databases.

    Returns
    -------
    dict[str, dict[str, str]]
        Dictionary where keys are database names, and values are dictionaries
        containing two string keys:

        * ``module``: the full Pythonic module name (e.g.
          ``mednet.data.classify.montgomery``).
        * ``datadir``: points to the user-configured data directory for the
          current database, if set, or ``None`` otherwise.
    """

    import importlib
    import pkgutil
    import typing

    from ..data import classify as classify_data
    from ..data import detect as detect_data
    from ..data import segment as segment_data
    from ..utils.rc import load_rc

    user_configuration = load_rc()

    retval: dict[str, dict[str, typing.Any]] = {}
    for data in (classify_data, segment_data, detect_data):
        for k in pkgutil.iter_modules(data.__path__):
            assert data.__package__ is not None
            module = importlib.import_module(data.__package__ + "." + k.name)
            datadir = getattr(module, "CONFIGURATION_KEY_DATADIR", None)
            if datadir is None:
                continue

            retval.setdefault(
                k.name,
                dict(module=[], datadir=user_configuration.get(datadir)),
            )["module"].append(module.__name__.rsplit(".", 1)[0])

    return retval


def _list_raw_databases():
    """List raw databases to a string representation."""

    def _echo(left: str, right: str, color: str = "white") -> None:
        s = [
            click.style(left, bold=True),
            click.style(": ", bold=True),
            click.style(right, fg=color),
        ]
        click.echo("".join(s))

    for k, v in _get_raw_databases().items():
        if "datadir" not in v:
            # this database does not have a "datadir"
            continue

        if v["datadir"] is not None:
            _echo(f"  - {k} ({', '.join(v['module'])})", f"{v['datadir']}", "green")
        else:
            _echo(f"  - {k} ({', '.join(v['module'])})", "NOT installed", "red")


@click.group(cls=AliasedGroup)
def database() -> None:
    """Command for listing and verifying databases installed."""
    pass


@database.command(
    name="list",
    epilog="""Examples:

\b
    1. To install a database, set up its data directory ("datadir").  For
       example, to setup access to Montgomery files you downloaded locally at
       the directory "/path/to/montgomery/files", edit the RC file (typically
       ``$HOME/.config/mednet.toml``), and add a line like the following:

       .. code:: toml

          [datadir]
          montgomery = "/path/to/montgomery/files"

       .. note::

          This setting **is** case-sensitive.

\b
    2. List all raw databases supported (and configured):

       .. code:: sh

          $ mednet database list

""",
)
@verbosity_option(logger=logger, expose_value=False)
def list_():
    """List all supported and configured databases."""

    _list_raw_databases()


@database.command(
    epilog="""Examples:

    1. Check if all files from the config split 'montgomery-f0' of the Montgomery
       database can be loaded:

       .. code:: sh

          mednet database check -vv montgomery-f0

""",
)
@click.argument(
    "entrypoint",
    nargs=1,
)
@click.option(
    "--limit",
    "-l",
    help="Limit check to the first N samples in each split in the "
    "configuration, making the check sensibly faster. Set it to "
    "zero (default) to check everything.",
    required=True,
    type=click.IntRange(0),
    default=0,
    show_default=True,
)
@verbosity_option(logger=logger, expose_value=False)
def check(entrypoint, limit):  # numpydoc ignore=PR01
    """Check file access on a database configuration split."""
    import importlib.metadata
    import sys

    click.secho(f"Checking database split config `{entrypoint}`...", fg="yellow")
    try:
        module = importlib.metadata.entry_points(group="mednet.config")[
            entrypoint
        ].module
    except KeyError:
        raise Exception(f"Could not find database split config `{entrypoint}`")

    datamodule = importlib.import_module(module).datamodule

    datamodule.model_transforms = []  # should be done before setup()
    datamodule.batch_size = 1  # ensure one sample is loaded at a time
    datamodule.setup("predict")  # sets up all datasets

    loaders = datamodule.predict_dataloader()

    errors = 0
    for k, loader in loaders.items():
        if limit == 0:
            click.secho(
                f"Checking all {len(loader)} samples of split `{k}` at config "
                f"`{entrypoint}`...",
                fg="yellow",
            )
            loader_limit = sys.maxsize
        else:
            click.secho(
                f"Checking first {limit} samples of dataset "
                f"`{k}` at config `{entrypoint}`...",
                fg="yellow",
            )
            loader_limit = limit

        # the for loop will trigger raw data loading (ie. user code), protect it
        i = 0
        try:
            for i, batch in enumerate(loader):
                if loader_limit == 0:
                    break
                logger.info(
                    f"{batch['name'][0]}: "
                    f"{[s for s in batch['image'][0].shape]}@{batch['image'][0].dtype}",
                )
                loader_limit -= 1
        except Exception:
            logger.exception(f"Unable to load sample {i} at split {k}")
            errors += 1

    if not errors:
        click.secho(
            f"OK! No errors were reported for database entrypoint `{entrypoint}`.",
            fg="green",
        )
    else:
        click.secho(
            f"Found {errors} errors loading DataModule `{entrypoint}`.",
            fg="red",
        )


# Add "preprocess" subcommand
database.add_command(
    getattr(
        __import__("importlib").import_module("..preprocess", package=__name__),
        "preprocess",
    )
)
