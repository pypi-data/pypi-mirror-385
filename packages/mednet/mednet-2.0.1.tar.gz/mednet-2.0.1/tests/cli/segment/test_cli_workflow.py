# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for our CLI applications."""

import pathlib

import click.testing
import pytest
import testing.cli


@pytest.mark.slow
@pytest.mark.skip_if_rc_var_not_set("datadir.drive")
def test_train_lwnet_drive(module_tmp_path: pathlib.Path):
    from mednet.scripts.train import train
    from mednet.utils.checkpointer import (
        CHECKPOINT_EXTENSION,
        _get_checkpoint_from_alias,
    )

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "segmentation-standalone"
        result = runner.invoke(
            train,
            [
                "lwnet",
                "drive",
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
            # Starting from scratch:
            # 1) it is a known model, so the next message should NOT appear
            r"^Model `.*` is not known. Skipping input normalization from train dataloader setup (unsupported external model).$": 0,
            # 2) should compute a new set of normalization factors
            r"^Computing z-norm input normalization from dataloader.$": 1,
            # 3) should NOT reload pre-calculated normalization factors from checkpoint
            r"^Restored input normalizer from checkpoint.$": 0,
            # The loss used in LWNet balances batches on-the-fly so pre-balancing is not
            # supported
            r"^Loss `.*` is not supported and will not be balanced.$": 1,
            r"^Applying train/valid loss balancing...$": 0,
            r"^Training for at most 1 epochs.$": 1,
            r"^Dataset `train` is already setup. Not re-instantiating it.$": 3,
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
@pytest.mark.skip_if_rc_var_not_set("datadir.drive")
def test_predict_lwnet_drive(module_tmp_path: pathlib.Path):
    from mednet.scripts.predict import predict
    from mednet.utils.checkpointer import (
        CHECKPOINT_EXTENSION,
        _get_checkpoint_from_alias,
    )

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "segmentation-standalone"
        last_ckpt = _get_checkpoint_from_alias(output_folder, "periodic")
        assert last_ckpt.name.endswith("epoch=0" + CHECKPOINT_EXTENSION)
        result = runner.invoke(
            predict,
            [
                "lwnet",
                "drive",
                "-vv",
                "--batch-size=1",
                f"--weight={str(last_ckpt)}",
                f"--output-folder={str(output_folder)}",
            ],
        )
        testing.cli.assert_exit_0(result)

        assert (output_folder / "predictions.meta.json").exists()
        assert (output_folder / "predictions.json").exists()

        keywords = {
            r"^Writing run metadata at .*$": 1,
            r"^Loading dataset: * without caching. Trade-off: CPU RAM usage: less | Disk I/O: more$": 2,
            r"^Loading checkpoint from .*$": 1,
            # Prediction
            # 1) should NOT compute a new set of normalization factors
            r"^Computing z-norm input normalization from dataloader.$": 0,
            # 2) should reload pre-calculated normalization factors from checkpoint
            r"^Restored input normalizer from checkpoint.$": 1,
            r"^Running prediction on `train` split...$": 1,
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
@pytest.mark.skip_if_rc_var_not_set("datadir.drive")
def test_dump_annotations_lwnet_drive(module_tmp_path: pathlib.Path):
    from mednet.scripts.segment.dump_annotations import dump_annotations

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "segmentation-standalone" / "second-annotator"
        result = runner.invoke(
            dump_annotations,
            [
                "lwnet",
                "drive-2nd",
                "-vv",
                f"--output-folder={str(output_folder)}",
            ],
        )
        testing.cli.assert_exit_0(result)

        assert (output_folder / "annotations.meta.json").exists()
        assert (output_folder / "annotations.json").exists()

        keywords = {
            r"^Writing run metadata at .*$": 1,
            r"^Loading dataset:.*$": 1,
            r"^Dumping annotations from split.*$": 1,
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
@pytest.mark.skip_if_rc_var_not_set("datadir.drive")
def test_evaluate_lwnet_drive(module_tmp_path: pathlib.Path):
    from mednet.scripts.segment.evaluate import evaluate

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "segmentation-standalone"
        result = runner.invoke(
            evaluate,
            [
                "-vv",
                f"--predictions={str(output_folder / 'predictions.json')}",
                f"--output-folder={str(output_folder)}",
                "--threshold=test",
                f"--compare-annotator={str(output_folder / 'second-annotator' / 'annotations.json')}",
            ],
        )
        testing.cli.assert_exit_0(result)

        assert (output_folder / "evaluation.json").exists()
        assert (output_folder / "evaluation.meta.json").exists()
        assert (output_folder / "evaluation.rst").exists()
        assert (output_folder / "evaluation.pdf").exists()

        keywords = {
            r"^Writing run metadata at .*$": 1,
            r"^Counting true/false positive/negatives at split.*$": 2,
            r"^Evaluating threshold on split .*$": 1,
            r"^Computing metrics on split .*$": 2,
            r"^Comparing 2nd. annotator using .*$": 1,
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
@pytest.mark.skip_if_rc_var_not_set("datadir.drive")
def test_view_lwnet_drive(module_tmp_path: pathlib.Path):
    from mednet.scripts.segment.view import view

    runner = click.testing.CliRunner()

    with testing.cli.stdout_logging() as buf:
        output_folder = module_tmp_path / "segmentation-standalone"
        result = runner.invoke(
            view,
            [
                "-vv",
                f"--predictions={str(output_folder / 'predictions.json')}",
                f"--output-folder={str(output_folder)}",
            ],
        )
        testing.cli.assert_exit_0(result)

        assert len(list((output_folder / "training" / "images").glob("*.png"))) == 20
        assert len(list((output_folder / "test" / "images").glob("*.png"))) == 20

        keywords = {
            r"^Creating 20 visualisations for split.*$": 2,
            r"^Set --threshold.*$": 1,
        }
        buf.seek(0)
        logging_output = buf.read()

        for k, v in keywords.items():
            assert testing.cli.str_counter(k, logging_output) == v, (
                f"Count for string '{k}' appeared "
                f"({testing.cli.str_counter(k, logging_output)}) "
                f"instead of the expected {v}:\nOutput:\n{logging_output}"
            )
