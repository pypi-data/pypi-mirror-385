# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for our CLI applications."""

import click.testing
import testing.cli


def test_info_help():
    from mednet.scripts.info import info

    testing.cli.check_help(info)


def test_info():
    from mednet.scripts.info import info

    runner = click.testing.CliRunner()
    result = runner.invoke(info)
    testing.cli.assert_exit_0(result)
    assert "platform:" in result.output
    assert "accelerators:" in result.output
    assert "version:" in result.output
    assert "databases:" in result.output
    assert "dependencies:" in result.output
    assert "python:" in result.output


def test_config_help():
    from mednet.scripts.config import config

    testing.cli.check_help(config)


def test_config_list_help():
    from mednet.scripts.config import list_

    testing.cli.check_help(list_)


def test_config_list():
    from mednet.scripts.config import list_

    runner = click.testing.CliRunner()
    result = runner.invoke(list_)
    testing.cli.assert_exit_0(result)
    assert "module: mednet.config.classify.data" in result.output
    assert "module: mednet.config.classify.models" in result.output
    assert "module: mednet.config.segment.data" in result.output
    assert "module: mednet.config.segment.models" in result.output


def test_config_list_v():
    from mednet.scripts.config import list_

    result = click.testing.CliRunner().invoke(list_, ["--verbose"])
    testing.cli.assert_exit_0(result)
    assert "module: mednet.config.classify.data" in result.output
    assert "module: mednet.config.classify.models" in result.output
    assert "module: mednet.config.segment.data" in result.output
    assert "module: mednet.config.segment.models" in result.output


def test_config_describe_help():
    from mednet.scripts.config import describe

    testing.cli.check_help(describe)


def test_database_help():
    from mednet.scripts.database import database

    testing.cli.check_help(database)


def test_database_list_help():
    from mednet.scripts.database import list_

    testing.cli.check_help(list_)


def test_database_list():
    from mednet.scripts.database import list_

    runner = click.testing.CliRunner()
    result = runner.invoke(list_)
    testing.cli.assert_exit_0(result)
    assert result.output.startswith("  - ")


def test_database_check_help():
    from mednet.scripts.database import check

    testing.cli.check_help(check)


def test_database_preprocess_help():
    from mednet.scripts.preprocess import preprocess

    testing.cli.check_help(preprocess)


def test_train_help():
    from mednet.scripts.train import train

    testing.cli.check_help(train)


def test_predict_help():
    from mednet.scripts.predict import predict

    testing.cli.check_help(predict)


def test_experiment_help():
    from mednet.scripts.experiment import experiment

    testing.cli.check_help(experiment)


def test_upload_help():
    from mednet.scripts.upload import upload

    testing.cli.check_help(upload)
