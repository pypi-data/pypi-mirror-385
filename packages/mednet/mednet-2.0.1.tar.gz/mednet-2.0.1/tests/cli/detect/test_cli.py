# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for our CLI applications."""

import click.testing
import pytest
import testing.cli


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_config_describe_montgomery():
    from mednet.scripts.config import describe

    runner = click.testing.CliRunner()
    result = runner.invoke(describe, ["montgomery-detect"])
    testing.cli.assert_exit_0(result)
    assert (
        ":py:mod:`Montgomery database <mednet.data.detect.montgomery>` (default split)."
        in result.output
    )


@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_database_check():
    from mednet.scripts.database import check

    runner = click.testing.CliRunner()
    result = runner.invoke(check, ["--verbose", "--limit=1", "montgomery-detect"])
    testing.cli.assert_exit_0(result)


def test_evaluate_help():
    from mednet.scripts.detect.evaluate import evaluate

    testing.cli.check_help(evaluate)


@pytest.mark.slow
@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_train_faster_rcnn_montgomery_from_checkpoint(tmp_path):
    from mednet.scripts.train import train
    from mednet.utils.checkpointer import (
        CHECKPOINT_EXTENSION,
        _get_checkpoint_from_alias,
    )

    runner = click.testing.CliRunner()

    result0 = runner.invoke(
        train,
        [
            "faster-rcnn",
            "montgomery-detect",
            "-vv",
            "--epochs=1",
            "--batch-size=1",
            f"--output-folder={str(tmp_path)}",
        ],
    )
    testing.cli.assert_exit_0(result0)

    # asserts checkpoints are there, or raises FileNotFoundError
    last = _get_checkpoint_from_alias(tmp_path, "periodic")
    assert last.name.endswith("epoch=0" + CHECKPOINT_EXTENSION)
    best = _get_checkpoint_from_alias(tmp_path, "best")
    assert best.name.endswith("epoch=0" + CHECKPOINT_EXTENSION)

    assert (tmp_path / "train.meta.json").exists()
    assert len(list((tmp_path / "logs").glob("events.out.tfevents.*"))) == 1

    with testing.cli.stdout_logging() as buf:
        result = runner.invoke(
            train,
            [
                "faster-rcnn",
                "montgomery-detect",
                "-vv",
                "--epochs=2",
                "--batch-size=1",
                f"--output-folder={tmp_path}",
            ],
        )
        testing.cli.assert_exit_0(result)

        # asserts checkpoints are there, or raises FileNotFoundError
        last = _get_checkpoint_from_alias(tmp_path, "periodic")
        assert last.name.endswith("epoch=1" + CHECKPOINT_EXTENSION)
        best = _get_checkpoint_from_alias(tmp_path, "best")

        assert (tmp_path / "train.meta.json").exists()
        assert len(list((tmp_path / "logs").glob("events.out.tfevents.*"))) == 2

        keywords = {
            r"^Writing run metadata at .*$": 1,
            r"^Loading dataset:`train` without caching. Trade-off: CPU RAM usage: less | Disk I/O: more.$": 1,
            # Re-starting from checkpoint:
            # 1) it is a known model, so the next message should NOT appear
            r"^Model `.*` is not known. Skipping input normalization from train dataloader setup (unsupported external model).$": 0,
            # 2) should NOT compute a new set of normalization factors
            r"^Computing z-norm input normalization from dataloader.$": 0,
            # 3) should reload pre-calculated normalization factors from checkpoint
            r"^Restored input normalizer from checkpoint.$": 1,
            # The loss used in LWNet balances batches on-the-fly so pre-balancing is not
            # supported
            r"No loss configured to be balanced.": 1,
            r"^Loss `.*` is not supported and will not be balanced.$": 0,
            r"^Applying train/valid loss balancing...$": 0,
            r"^Training for at most 2 epochs.$": 1,
            r"^Resuming from epoch 0 \(checkpoint file: .*$": 1,
            r"^Dataset `train` is already setup. Not re-instantiating it.$": 1,
        }
        buf.seek(0)
        logging_output = buf.read()

        for k, v in keywords.items():
            assert testing.cli.str_counter(k, logging_output) == v, (
                f"Count for string '{k}' appeared "
                f"({testing.cli.str_counter(k, logging_output)}) "
                f"instead of the expected {v}:\nOutput:\n{logging_output}"
            )


@pytest.mark.slow
@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_experiment(tmp_path):
    from mednet.scripts.experiment import experiment

    runner = click.testing.CliRunner()

    num_epochs = 2
    result = runner.invoke(
        experiment,
        [
            "-vv",
            "faster-rcnn",
            "montgomery-detect",
            f"--epochs={num_epochs}",
            f"--output-folder={str(tmp_path)}",
        ],
    )
    testing.cli.assert_exit_0(result)

    assert (tmp_path / "train.meta.json").exists()
    assert (tmp_path / f"model-at-epoch={num_epochs - 1}.ckpt").exists()

    # Need to glob because we cannot be sure of the checkpoint with lowest validation loss
    assert len(list(tmp_path.glob("model-at-lowest-validation-loss-epoch=*.ckpt"))) == 1
    assert (tmp_path / "trainlog.pdf").exists()
    assert len(list((tmp_path / "logs").glob("events.out.tfevents.*"))) == 1
    assert (tmp_path / "predictions.json").exists()
    assert (tmp_path / "predictions.meta.json").exists()
    assert (tmp_path / "evaluation.json").exists()
    assert (tmp_path / "evaluation.meta.json").exists()
    assert (tmp_path / "evaluation.pdf").exists()
    assert (tmp_path / "evaluation.rst").exists()
