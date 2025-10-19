# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib

import click
from clapper.click import AliasedGroup


@click.group(
    cls=AliasedGroup,
    context_settings=dict(help_option_names=["-?", "-h", "--help"]),
)
def cli():
    """Medical image analysis AI toolbox."""
    pass


def _add_command(module, obj):
    cli.add_command(
        getattr(importlib.import_module("." + module, package=__name__), obj)
    )


_add_command(".info", "info")
_add_command(".info", "version")
_add_command(".config", "config")
_add_command(".database", "database")
_add_command(".train", "train")
_add_command(".train_analysis", "train_analysis")
_add_command(".predict", "predict")
_add_command(".experiment", "experiment")
_add_command(".upload", "upload")
_add_command(".classify.cli", "classify")
_add_command(".detect.cli", "detect")
_add_command(".segment.cli", "segment")
