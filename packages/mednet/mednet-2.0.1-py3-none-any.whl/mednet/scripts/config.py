# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import click
from clapper.click import AliasedGroup, verbosity_option

from .logging import setup_cli_logger

logger = setup_cli_logger()


@click.group(cls=AliasedGroup)
def config():
    """Command for listing, describing and copying configuration resources."""
    pass


@config.command(
    name="list",
    epilog="""Examples:

\b
  1. Lists all configuration resources installed:

     .. code:: sh

        mednet config list


\b
  2. Lists all configuration resources and their descriptions (notice this may
     be slow as it needs to load all modules once):

     .. code:: sh

        mednet config list -v

""",
)
@verbosity_option(logger=logger, expose_value=False)
@click.pass_context
def list_(ctx, **_) -> None:  # numpydoc ignore=PR01
    """List configuration files installed."""

    import importlib.metadata
    import inspect
    import typing

    entry_points = importlib.metadata.entry_points().select(group="mednet.config")
    entry_point_dict = {k.name: k for k in entry_points}

    # all potential modules with configuration resources
    modules = {k.module.rsplit(".", 1)[0] for k in entry_point_dict.values()}

    # sort data entries by originating module
    entry_points_by_module: dict[str, dict[str, typing.Any]] = {}
    for k in modules:
        entry_points_by_module[k] = {}
        for name, ep in entry_point_dict.items():
            if ep.module.rsplit(".", 1)[0] == k:
                entry_points_by_module[k][name] = ep

    for config_type in sorted(entry_points_by_module):
        # calculates the longest config name so we offset the printing
        longest_name_length = max(
            len(k) for k in entry_points_by_module[config_type].keys()
        )

        # set-up printing options
        print_string = f"  %-{longest_name_length}s   %s"
        # 79 - 4 spaces = 75 (see string above)
        description_leftover = 75 - longest_name_length

        click.echo(f"module: {config_type}")
        for name in sorted(entry_points_by_module[config_type]):
            ep = entry_point_dict[name]

            if ctx.meta.get("verbose", 0) >= 1:
                module = ep.load()
                doc = inspect.getdoc(module)
                if doc is not None:
                    summary = doc.split("\n\n")[0]
                else:
                    summary = "<DOCSTRING NOT AVAILABLE>"
            else:
                summary = ""

            summary = (
                (summary[: (description_leftover - 3)] + "...")
                if len(summary) > (description_leftover - 3)
                else summary
            )

            click.echo(print_string % (name, summary))


@config.command(
    epilog="""Examples:

\b
  1. Describe the Montgomery dataset configuration:

     .. code:: sh

        mednet config describe montgomery


\b
  2. Describe the Montgomery dataset configuration and lists its
     contents:

     .. code:: sh

        mednet config describe montgomery -v

""",
)
@click.argument(
    "name",
    required=True,
    nargs=-1,
)
@verbosity_option(logger=logger, expose_value=False)
@click.pass_context
def describe(ctx, name, **_) -> None:  # numpydoc ignore=PR01
    """Describe a specific configuration file."""

    import importlib.metadata
    import inspect
    import pathlib

    entry_points = importlib.metadata.entry_points().select(group="mednet.config")
    entry_point_dict = {k.name: k for k in entry_points}

    for k in name:
        if k not in entry_point_dict:
            logger.error("Cannot find configuration resource '%s'", k)
            continue
        ep = entry_point_dict[k]
        click.echo(f"Configuration: {ep.name}")
        click.echo(f"Python Module: {ep.module}")
        click.echo("")
        mod = ep.load()

        if ctx.meta.get("verbose", 0) >= 1:
            fname = inspect.getfile(mod)
            click.echo("Contents:")
            with pathlib.Path(fname).open() as f:
                click.echo(f.read())
        else:  # only output documentation
            click.echo("Documentation:")
            click.echo(inspect.getdoc(mod))


@config.command(
    epilog="""Examples:

\b
  1. Make a copy of one of the stock configuration files locally, so it can be
     adapted:

     .. code:: sh

        $ mednet config copy montgomery -vvv newdataset.py

""",
)
@click.argument(
    "source",
    required=True,
    nargs=1,
)
@click.argument(
    "destination",
    required=True,
    nargs=1,
)
@verbosity_option(logger=logger, expose_value=False)
def copy(source, destination) -> None:  # numpydoc ignore=PR01
    """Copy a specific configuration resource so it can be modified locally."""

    import importlib.metadata
    import inspect
    import shutil

    entry_points = importlib.metadata.entry_points().select(group="mednet.config")
    entry_point_dict = {k.name: k for k in entry_points}

    if source not in entry_point_dict:
        logger.error("Cannot find configuration resource '%s'", source)
        return

    ep = entry_point_dict[source]
    mod = ep.load()
    src_name = inspect.getfile(mod)
    logger.info(f"cp {src_name} -> {destination}")
    shutil.copyfile(src_name, destination)
