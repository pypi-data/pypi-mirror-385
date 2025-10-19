# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests the workflow of our CLI applications on ViT when adapted through LoRA."""

import pathlib

import click.testing
import pytest
import testing.cli


@pytest.mark.slow
@pytest.mark.skip_if_rc_var_not_set("datadir.montgomery")
def test_train_vit_montgomery(module_tmp_path: pathlib.Path):
    from mednet.scripts.train import train
    from mednet.utils.checkpointer import (
        CHECKPOINT_EXTENSION,
        _get_checkpoint_from_alias,
    )

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "classification-standalone"
        result = runner.invoke(
            train,
            [
                "vit-small-lora",
                "montgomery",
                "-vv",
                "--epochs=1",
                "--batch-size=1",
                f"--output-folder={str(output_folder)}",
            ],
        )
        testing.cli.assert_exit_0(result)

        # asserts checkpoints are there, or raises FileNotFoundError
        last = _get_checkpoint_from_alias(output_folder, "periodic")
        assert last.name.endswith("epoch=0" + CHECKPOINT_EXTENSION)
        best = _get_checkpoint_from_alias(output_folder, "best")
        assert best.name.endswith("epoch=0" + CHECKPOINT_EXTENSION)

        assert len(list((output_folder / "logs").glob("events.out.tfevents.*"))) == 1
        assert (output_folder / "train.meta.json").exists()

        keywords = {
            r"^Writing run metadata at .*$": 1,
            r"^Loading dataset:`train` without caching. Trade-off: CPU RAM usage: less | Disk I/O: more.$": 1,
            r"^Loading dataset:`validation` without caching. Trade-off: CPU RAM usage: less | Disk I/O: more.$": 1,
            # Starting from scratch:
            # 1) it is a known model, so the next message should NOT appear
            r"^Model `.*` is not known. Skipping input normalization from train dataloader setup (unsupported external model).$": 0,
            # 2) should compute a new set of normalization factors
            r"^Computing z-norm input normalization from dataloader.$": 0,
            # 3) should NOT reload pre-calculated normalization factors from checkpoint
            r"^Restored input normalizer from checkpoint.$": 0,
            # The loss used in ViT must be balanced using the training dataloader
            r"^Applying train/valid loss balancing...$": 1,
            r"^Loss `.*` is not supported and will not be balanced.$": 0,
            r"^Training for at most 1 epochs.$": 1,
            r"^Dataset `train` is already setup. Not re-instantiating it.$": 1,
            r"^Dataset `validation` is already setup. Not re-instantiating it.$": 1,
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
def test_predict_vit_montgomery(module_tmp_path: pathlib.Path):
    from mednet.scripts.predict import predict
    from mednet.utils.checkpointer import (
        CHECKPOINT_EXTENSION,
        _get_checkpoint_from_alias,
    )

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "classification-standalone"
        last = _get_checkpoint_from_alias(output_folder, "periodic")
        assert last.name.endswith("epoch=0" + CHECKPOINT_EXTENSION)
        result = runner.invoke(
            predict,
            [
                "vit-small-lora",
                "montgomery",
                "-vv",
                "--batch-size=1",
                f"--weight={str(last)}",
                f"--output-folder={str(output_folder)}",
            ],
        )
        testing.cli.assert_exit_0(result)

        assert (output_folder / "predictions.meta.json").exists()
        assert (output_folder / "predictions.json").exists()

        keywords = {
            r"^Writing run metadata at .*$": 1,
            r"^Loading dataset: * without caching. Trade-off: CPU RAM usage: less | Disk I/O: more$": 3,
            r"^Loading checkpoint from .*$": 1,
            # Prediction
            # 1) should NOT compute a new set of normalization factors
            r"^Computing z-norm input normalization from dataloader.$": 0,
            # 2) should reload pre-calculated normalization factors from checkpoint
            r"^Restored input normalizer from checkpoint.$": 1,
            r"^Running prediction on `train` split...$": 1,
            r"^Running prediction on `validation` split...$": 1,
            r"^Running prediction on `test` split...$": 1,
            r"^Predictions saved to .*$": 1,
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
def test_evaluate_vit_montgomery(module_tmp_path: pathlib.Path):
    from mednet.scripts.classify.evaluate import evaluate

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "classification-standalone"
        result = runner.invoke(
            evaluate,
            [
                "-vv",
                f"--predictions={str(output_folder / 'predictions.json')}",
                f"--output-folder={str(output_folder)}",
                "--threshold=test",
                "--credible-regions",
            ],
        )
        testing.cli.assert_exit_0(result)

        assert (output_folder / "evaluation.json").exists()
        assert (output_folder / "evaluation.meta.json").exists()
        assert (output_folder / "evaluation.rst").exists()
        assert (output_folder / "evaluation.pdf").exists()

        keywords = {
            r"^Writing run metadata at .*$": 1,
            r"^Setting --threshold=.*$": 1,
            r"^Computing performance on split .*...$": 3,
            r"^Computing credible regions for metrics on split .*": 3,
            r"^Saving evaluation results at .*$": 1,
            r"^Saving tabulated performance summary at .*$": 1,
            r"^Saving evaluation figures at .*$": 1,
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
def test_train_vit_montgomery_from_checkpoint(tmp_path):
    from mednet.scripts.train import train
    from mednet.utils.checkpointer import (
        CHECKPOINT_EXTENSION,
        _get_checkpoint_from_alias,
    )

    runner = click.testing.CliRunner()

    result0 = runner.invoke(
        train,
        [
            "vit-small-lora",
            "montgomery",
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
                "vit-small-lora",
                "montgomery",
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
            r"^Loading dataset:`train` without caching. Trade-off: CPU RAM usage: less | Disk I/O: more.$": 1,
            r"^Loading dataset:`validation` without caching. Trade-off: CPU RAM usage: less | Disk I/O: more.$": 1,
            # Re-starting from checkpoint:
            # 1) it is a known model, so the next message should NOT appear
            r"^Model `.*` is not known. Skipping input normalization from train dataloader setup (unsupported external model).$": 0,
            # 2) should NOT compute a new set of normalization factors
            r"^Computing z-norm input normalization from dataloader.$": 0,
            # 3) should reload pre-calculated normalization factors from checkpoint
            r"^Restored input normalizer from checkpoint.$": 1,
            # The loss used in ViT must be balanced
            r"^Loss `.*` is not supported and will not be balanced.$": 0,
            r"^Applying train/valid loss balancing...$": 1,
            r"^Training for at most 2 epochs.$": 1,
            r"^Resuming from epoch 0 \(checkpoint file: .*$": 1,
            r"^Writing run metadata at.*$": 1,
            r"^Dataset `train` is already setup. Not re-instantiating it.$": 1,
            r"^Dataset `validation` is already setup. Not re-instantiating it.$": 1,
        }
        buf.seek(0)
        logging_output = buf.read()

        for k, v in keywords.items():
            assert testing.cli.str_counter(k, logging_output) == v, (
                f"Count for string '{k}' appeared "
                f"({testing.cli.str_counter(k, logging_output)}) "
                f"instead of the expected {v}:\nOutput:\n{logging_output}"
            )
