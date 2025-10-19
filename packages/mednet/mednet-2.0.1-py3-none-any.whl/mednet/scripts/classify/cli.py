# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib

import click
from clapper.click import AliasedGroup


@click.group(
    cls=AliasedGroup,
    context_settings=dict(help_option_names=["-?", "-h", "--help"]),
)
def classify():
    """Image classification specialized commands."""
    pass


def _add_command(cli, module, obj):
    cli.add_command(
        getattr(importlib.import_module("." + module, package=__name__), obj)
    )


_add_command(classify, ".evaluate", "evaluate")


@click.group(
    cls=AliasedGroup,
    context_settings=dict(help_option_names=["-?", "-h", "--help"]),
)
def saliency():
    """Generate, evaluate and view saliency maps."""
    pass


classify.add_command(saliency)

_add_command(saliency, ".saliency.generate", "generate")
_add_command(saliency, ".saliency.completeness", "completeness")
_add_command(saliency, ".saliency.interpretability", "interpretability")
_add_command(saliency, ".saliency.view", "view")
