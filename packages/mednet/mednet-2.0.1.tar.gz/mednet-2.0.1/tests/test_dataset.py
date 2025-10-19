# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Test code for datasets."""

import typing

import pytest
import testing.database
import torch
from torchvision import tv_tensors

import mednet.data.typing

_NUM_SAMPLES = 1000
_raw_dataset = [(f"sample-{k:3d}", k, f"metadata-{k:3d}") for k in range(_NUM_SAMPLES)]


class _RawDataLoader(mednet.data.typing.RawDataLoader):
    def sample(
        self, sample: tuple[str, int, typing.Any | None]
    ) -> mednet.data.typing.Sample:
        image = torch.rand([1, 128, 128])
        image = tv_tensors.Image(image)

        return dict(
            image=image, name=sample[0], target=self.target(sample), metadata=sample[2]
        )

    def target(self, sample: typing.Any) -> torch.Tensor:
        return torch.FloatTensor([sample[1]])


@pytest.mark.parametrize(
    "parallel",
    [-1, 1, 2, 4],
    ids=testing.database.id_function,
)
def test_cached_dataset(parallel):
    from mednet.data.datamodule import CachedDataset

    dataset = CachedDataset(
        raw_dataset=_raw_dataset,
        loader=_RawDataLoader(),
        parallel=parallel,
        disable_pbar=True,
    )

    # tests targets
    assert len(dataset.targets()) == _NUM_SAMPLES

    # checks __len__
    assert len(dataset) == _NUM_SAMPLES

    # checks __iter__ works
    # and returns in due order
    for loaded_sample, raw_sample in zip(dataset, _raw_dataset):
        assert loaded_sample["name"] == raw_sample[0]
        assert loaded_sample["target"].item() == raw_sample[1]
        assert loaded_sample["metadata"] == raw_sample[2]

    # checks __getitem__
    for k, raw_sample in enumerate(_raw_dataset):
        loaded_sample = dataset[k]
        assert loaded_sample["name"] == raw_sample[0]
        assert loaded_sample["target"].item() == raw_sample[1]
        assert loaded_sample["metadata"] == raw_sample[2]
