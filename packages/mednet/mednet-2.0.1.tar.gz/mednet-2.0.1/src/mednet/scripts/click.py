# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

import click
from clapper.click import ConfigCommand as _BaseConfigCommand


class ConfigCommand(_BaseConfigCommand):
    """A click command-class that has the properties of :py:class:`clapper.click.ConfigCommand` and adds verbatim epilog formatting."""

    def format_epilog(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Format the command epilog during --help.

        Parameters
        ----------
        ctx
            The current parsing context.
        formatter
            The formatter to use for printing text.
        """
        del ctx  # silence linter

        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write(line + "\n")


class PathOrURL(click.Path):
    """A click parameter type that represents either an URL or a filesystem path.

    This object may be initialized just like :py:class:`click.Path`. If the
    input resembles an URL (starts with "http"), then its returned as a string.
    Otherwise, it is returned depending on the way it was initialized.

    Parameters
    ----------
    *args
        Positional arguments delivered to super class.
    **kwargs
        Keyword arguments delivered to super class.
    """

    name = "path_or_url"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convert(
        self,
        value: str | os.PathLike[str],
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> str | bytes | os.PathLike[str]:
        """Convert input strings into parameters.

        Parameters
        ----------
        value
            The value passed through the command-line.
        param
            The type of parameter.
        ctx
            The current parser context.

        Returns
        -------
            The parsed parameter.
        """

        if isinstance(value, str | bytes) and value.startswith("http"):
            return value

        return super().convert(value, param, ctx)
