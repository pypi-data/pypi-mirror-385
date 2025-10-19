# Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib

import click
from clapper.click import AliasedGroup


@click.group(
    cls=AliasedGroup,
    context_settings=dict(help_option_names=["-?", "-h", "--help"]),
)
def detect():
    """Object detection specialized commands."""
    pass


def _add_command(cli, module, obj):
    cli.add_command(
        getattr(importlib.import_module("." + module, package=__name__), obj)
    )


_add_command(detect, ".evaluate", "evaluate")
