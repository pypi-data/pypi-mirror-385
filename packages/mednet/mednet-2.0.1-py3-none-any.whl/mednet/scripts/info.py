# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import click
from clapper.click import verbosity_option

from .logging import setup_cli_logger

logger = setup_cli_logger()


def _echo(left: str, right: str, color: str = "white") -> None:
    s = [
        click.style(left, bold=True),
        click.style(": ", bold=True),
        click.style(right, fg=color),
    ]
    click.echo("".join(s))


@click.command(
    epilog="""Examples:

1. Provide information about the current installation:

   .. code:: sh

      mednet info

""",
)
@verbosity_option(logger=logger, expose_value=False)
def info(
    **_,
) -> None:  # numpydoc ignore=PR01
    """Provide information about the current installation."""

    import typing

    from ..utils.rc import load_rc
    from .database import _list_raw_databases
    from .utils import execution_metadata

    m = execution_metadata()
    package_name = __name__.split(".")[0]

    _echo(f"{package_name} version", typing.cast(str, m["package-version"]), "green")
    _echo("platform", typing.cast(str, m["platform"]), "yellow")
    _echo(
        "accelerators",
        ", ".join(typing.cast(list[str], m["accelerators"])),
        "cyan",
    )

    rc = load_rc()

    if not rc.path.exists():
        _echo(f"{package_name} configuration", f"{str(rc.path)} [MISSING]", "white")
    else:
        _echo(f"{package_name} configuration file", f"{str(rc.path)}", "white")

    click.secho("databases:", bold=True)
    _list_raw_databases()

    click.secho("dependencies:", bold=True)
    python = typing.cast(dict[str, str], m["python"])
    _echo(
        "  - python",
        f"{python['version']} ({python['path']})",
        "white",
    )
    deps = typing.cast(dict[str, str], m["dependencies"])
    for name, version in deps.items():
        _echo(f"  - {name}", version, "white")


@click.command(
    epilog="""Examples:

1. Provide versio of the current installation:

   .. code:: sh

      mednet version

""",
)
@verbosity_option(logger=logger, expose_value=False)
def version(
    **_,
) -> None:  # numpydoc ignore=PR01
    """Provide version of the current installation."""

    import importlib.metadata

    package_name = __name__.split(".")[0]
    version = importlib.metadata.version(package_name)

    click.echo(version)
