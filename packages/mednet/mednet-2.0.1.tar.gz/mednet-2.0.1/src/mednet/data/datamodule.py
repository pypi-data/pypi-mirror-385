# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Extension of ``lightning.LightningDataModule`` with dictionary split loading, mini-batching, parallelisation and caching."""

import functools
import itertools
import logging
import sys
import typing

import lightning
import loky
import torch
import torch.backends
import torch.utils.data
import torchvision.transforms
import torchvision.tv_tensors
import tqdm

from .typing import (
    ConcatDatabaseSplit,
    DatabaseSplit,
    DataLoader,
    Dataset,
    RawDataLoader,
    Sample,
    TransformSequence,
)

logger = logging.getLogger(__name__)


def _sample_size_bytes(dataset: Dataset):
    """Recurse into the first sample of a dataset and figures out its total occupance in bytes.

    Parameters
    ----------
    dataset
        The dataset containing the samples to load.
    """

    def _tensor_size_bytes(t: torch.Tensor, n: str) -> int:
        """Return a tensor size in bytes.

        Parameters
        ----------
        t
            A torch Tensor.
        n
            Name of the object.

        Returns
        -------
        int
            The size of the Tensor in bytes.
        """

        logger.info(f"`{n}`: {list(t.shape)}@{t.dtype}")
        return int(t.element_size() * t.shape.numel())

    def _dict_size_bytes(d):
        """Return a dictionary size in bytes.

        Parameters
        ----------
        d
            A dictionary.

        Returns
        -------
        int
            The size of the dictionary in bytes.
        """

        size = 0
        for k, v in d.items():
            if isinstance(v, torch.Tensor):
                size += _tensor_size_bytes(v, k)

        return size

    first_sample = dataset[0]
    size = sys.getsizeof(first_sample)  # measures size of all pythonic objects
    size += _dict_size_bytes(first_sample)  # adds torch tensor sizes

    sample_size_mb = size / (1024.0 * 1024.0)
    logger.info(f"Estimated sample size: {sample_size_mb:.1f} Mb")


def _apply_iff_tv_tensor(
    data: typing.Any, transform: typing.Callable[[torch.Tensor], torch.Tensor]
):
    """Apply model_transform iff input object is TVTensor.

    Parameters
    ----------
    data
        Sample data to which apply the provided transform.
    transform
        Callable containing a single or a composition of transforms to
        potentially apply to ``data``.

    Returns
    -------
        The transformed version of ``data`` iff applicable.
    """
    if isinstance(data, torchvision.tv_tensors.TVTensor):
        return transform(data)
    return data


class _DelayedLoadingDataset(Dataset):
    """A list that loads its samples on demand.

    This list mimics a pytorch Dataset, except that raw data loading is done
    on-the-fly, as the samples are requested through the bracket operator.

    Parameters
    ----------
    raw_dataset
        An iterable containing the raw dataset samples representing one of the
        database split datasets.
    loader
        An object instance that can load samples from storage.
    transforms
        A set of transforms that should be applied on-the-fly for this dataset,
        to fit the output of the raw-data-loader to the model of interest.
    disable_pbar
        If set, disables progress bars.
    """

    def __init__(
        self,
        raw_dataset: typing.Sequence[typing.Any],
        loader: RawDataLoader,
        transforms: TransformSequence = [],
        disable_pbar: bool = False,
    ):
        self.raw_dataset = raw_dataset
        self.loader = loader
        self.transform = torchvision.transforms.Compose(transforms)
        self.disable_pbar = disable_pbar

        _sample_size_bytes(self)

    def targets(self) -> list[torch.Tensor]:
        """Return the targets for all samples in the dataset.

        Returns
        -------
            The targets for all samples in the dataset.
        """

        return [
            self.loader.target(k)
            for k in tqdm.tqdm(
                self.raw_dataset, unit="sample", disable=self.disable_pbar
            )
        ]

    def __getitem__(self, key: int) -> Sample:
        sample = self.loader.sample(self.raw_dataset[key])
        return {k: _apply_iff_tv_tensor(v, self.transform) for k, v in sample.items()}

    def __len__(self):
        return len(self.raw_dataset)

    def __iter__(self):
        for x in range(len(self)):
            yield self[x]


def _apply_loader_and_transforms(
    info: typing.Any,
    load: typing.Callable[[typing.Any], Sample],
    model_transform: typing.Callable[[torch.Tensor], torch.Tensor],
) -> Sample:
    """Local wrapper to apply raw-data loading and transformation in a single
    step.

    Parameters
    ----------
    info
        The sample information, as loaded from its raw dataset dictionary.
    load
        The raw-data loader function to use for loading the sample.
    model_transform
        A callable that will transform the loaded tensor into something
        suitable for the model it will train.  Typically, this will be a
        composed transform.

    Returns
    -------
    Sample
        The loaded and transformed sample.
    """
    sample = load(info)
    return {k: _apply_iff_tv_tensor(v, model_transform) for k, v in sample.items()}


class CachedDataset(Dataset):
    """Basically, a list of preloaded samples.

    This dataset will load all samples from the raw dataset during construction
    instead of delaying that to the indexing.  Beyond raw-data-loading,
    ``transforms`` given upon construction contribute to the cached samples.

    Parameters
    ----------
    raw_dataset
        An iterable containing the raw dataset samples representing one of the
        database split datasets.
    loader
        An object instance that can load samples and targets from storage.
    transforms
        A set of transforms that should be applied to the cached samples for
        this dataset, to fit the output of the raw-data-loader to the model of
        interest.
    parallel
        Use multiprocessing for data loading: if set to -1 (default), disables
        multiprocessing data loading.  Set to 0 to enable as many data loading
        instances as processing cores available in the system.  Set to >= 1
        to enable that many multiprocessing instances for data loading.
    disable_pbar
        If set, disables progress bars.
    """

    def __init__(
        self,
        raw_dataset: typing.Sequence[typing.Any],
        loader: RawDataLoader,
        transforms: TransformSequence = [],
        parallel: int = -1,
        disable_pbar: bool = False,
    ):
        self.loader = functools.partial(
            _apply_loader_and_transforms,
            load=loader.sample,
            model_transform=torchvision.transforms.Compose(transforms),
        )

        if parallel < 0:
            self.data = [
                self.loader(k)
                for k in tqdm.tqdm(raw_dataset, unit="sample", disable=disable_pbar)
            ]
        else:
            instances = parallel or torch.multiprocessing.cpu_count()
            logger.info(f"Caching dataset using {instances} processes...")
            # loky executor replaces torch.multiprocessing.Pool, but uses cloudpickle
            # for more robust data exchange between main process and workers.
            with loky.ProcessPoolExecutor(max_workers=instances) as executor:
                # submit all tasks
                _ = {
                    executor.submit(self.loader, sample): sample
                    for sample in raw_dataset
                }
                mapped = executor.map(self.loader, raw_dataset)
                self.data = list(
                    tqdm.tqdm(
                        mapped,
                        total=len(raw_dataset),
                        disable=disable_pbar,
                        unit="sample",
                    )
                )

        _sample_size_bytes(self)

    def targets(self) -> list[torch.Tensor]:
        """Return the targets for all samples in the dataset.

        Returns
        -------
            The targets for all samples in the dataset.
        """

        return [k["target"] for k in self.data]

    def __getitem__(self, key: int) -> Sample:
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from self.data


class ConcatDataset(Dataset):
    """A dataset that represents a concatenation of other cached or delayed datasets.

    Parameters
    ----------
    datasets
        An iterable over pre-instantiated datasets.
    """

    def __init__(self, datasets: typing.Sequence[Dataset]):
        self._datasets = datasets
        self._indices = [
            (i, j)  # dataset relative position, sample relative position
            for i in range(len(datasets))
            for j in range(len(datasets[i]))
        ]

    def targets(self) -> list[torch.Tensor]:
        """Return the targets for all samples in the dataset.

        Returns
        -------
            The targets for all samples in the dataset.
        """

        return list(itertools.chain(*[k.targets() for k in self._datasets]))

    def __getitem__(self, key: int) -> Sample:
        i, j = self._indices[key]
        return self._datasets[i][j]

    def __len__(self):
        return sum([len(k) for k in self._datasets])

    def __iter__(self):
        for dataset in self._datasets:
            yield from dataset


class ConcatDataModule(lightning.LightningDataModule):
    """A conveninent DataModule with dictionary split loading, mini- batching,
    parallelisation and caching, all in one.

    Instances of this class can load and concatenate an arbitrary number of
    data-split (a.k.a. protocol) definitions for (possibly disjoint) databases,
    and can manage raw data-loading from disk.  An optional caching mechanism
    stores the data in associated CPU memory, which can improve data serving
    while training and evaluating models.

    This DataModule defines basic operations to handle data loading and
    mini-batch handling within this package's framework.  It can return
    :py:class:`torch.utils.data.DataLoader` objects for training, validation,
    prediction and testing conditions.  Parallelisation is handled by a simple
    input flag.

    Parameters
    ----------
    splits
        A dictionary that contains string keys representing dataset names, and
        values that are iterables over a 2-tuple containing an iterable over
        arbitrary, user-configurable sample representations (potentially on
        disk or permanent storage), and :py:class:`.data.typing.RawDataLoader`
        (or "sample") loader objects, which concretely implement a mechanism to
        load such samples in memory, from permanent storage.

        Sample representations on permanent storage may be of any iterable
        format (e.g. list, dictionary, etc.), for as long as the assigned
        :py:class:`.data.typing.RawDataLoader` can properly handle it.

        .. tip::

           To check the split and that the loader function works correctly, you may
           use :py:func:`.split.check_database_split_loading`.

        This class expects at least one entry called ``train`` to exist in the
        input dictionary.  Optional entries are ``validation``, and ``test``.
        Entries named ``monitor-...`` will be considered extra datasets that do
        not influence any early stop criteria during training, and are just
        monitored beyond the ``validation`` dataset.
    database_name
        The name of the database, or aggregated database containing the
        raw-samples served by this data module.
    split_name
        The name of the split used to group the samples into the various
        datasets for training, validation and testing.
    task
        The task this datamodule generate samples for (e.g. ``classification``,
        ``segmentation``, or ``detection``).
    num_classes
        The number of target classes samples of this datamodule can have. In a
        classification task, this will dictate the number of outputs for the classifier
        (one-hot-encoded), the number of segmentation outputs for a semantic
        segmentation network, or the types of objects in an object detector.
    collate_fn
        A custom function to batch the samples.
        Uses torch.utils.data.default_collate() by default.
    cache_samples
        If set, then issue raw data loading during ``prepare_data()``, and
        serves samples from CPU memory.  Otherwise, loads samples from disk on
        demand. Running from CPU memory will offer increased speeds in exchange
        for CPU memory.  Sufficient CPU memory must be available before you set
        this attribute to ``True``.  It is typically useful for relatively small
        datasets.
    batch_size
        Number of samples in every **training** batch (this parameter affects
        memory requirements for the network).  If the number of samples in the
        batch is larger than the total number of samples available for
        training, this value is truncated.  If this number is smaller, then
        batches of the specified size are created and fed to the network until
        there are no more new samples to feed (epoch is finished).  If the
        total number of training samples is not a multiple of the batch-size,
        the last batch will be smaller than the first, unless
        ``drop_incomplete_batch`` is set to ``true``, in which case this batch
        is not used.
    drop_incomplete_batch
        If set, then may drop the last batch in an epoch in case it is
        incomplete.  If you set this option, you should also consider
        increasing the total number of training epochs, as the total number
        of training steps may be reduced.
    parallel
        Use multiprocessing for data loading: if set to -1 (default), disables
        multiprocessing data loading.  Set to 0 to enable as many data loading
        instances as processing cores available in the system.  Set to >= 1
        to enable that many multiprocessing instances for data loading.
    """

    DatasetDictionary: typing.TypeAlias = dict[str, Dataset]
    """A dictionary of datasets mapping names to actual datasets."""

    def __init__(
        self,
        splits: ConcatDatabaseSplit,
        database_name: str = "",
        split_name: str = "",
        task: str = "",
        num_classes: int = 1,
        collate_fn=torch.utils.data.default_collate,
        cache_samples: bool = False,
        batch_size: int = 1,
        drop_incomplete_batch: bool = False,
        parallel: int = -1,
    ):
        super().__init__()

        self.splits = splits
        self.database_name = database_name
        self.split_name = split_name
        self.task = task
        self.num_classes = num_classes
        self.collate_fn = collate_fn

        for dataset_name, split_loaders in splits.items():
            count = sum([len(k) for k, _ in split_loaders])
            logger.info(
                f"Dataset `{dataset_name}` (`{database_name}`/`{split_name}`) "
                f"contains {count} samples",
            )

        self.cache_samples = cache_samples

        self._model_transforms: TransformSequence | None = None

        self.batch_size = batch_size

        self.drop_incomplete_batch = drop_incomplete_batch
        self.parallel = parallel  # immutable, otherwise would need to call

        self.pin_memory = (
            torch.cuda.is_available() or torch.backends.mps.is_available()  # type: ignore
        )  # should only be true if GPU available and using it

        # datasets that have been setup() for the current stage
        self._datasets: ConcatDataModule.DatasetDictionary = {}

    @property
    def parallel(self) -> int:
        """Whether to use multiprocessing for data loading.

        Use multiprocessing for data loading: if set to -1 (default),
        disables multiprocessing data loading.  Set to 0 to enable as
        many data loading instances as processing cores available in
        the system.  Set to >= 1 to enable that many multiprocessing
        instances for data loading.

        It sets the parameter ``num_workers`` (from DataLoaders) to match the
        expected pytorch representation.  It also sets the
        ``multiprocessing_context`` to use ``spawn`` instead of the default
        (``fork``, on Linux).

        The mapping between the command-line interface ``parallel`` setting
        works like this:

        .. list-table:: Relationship between ``parallel`` and DataLoader parameters
           :widths: 15 15 70
           :header-rows: 1

           * - CLI ``parallel``
             - :py:class:`torch.utils.data.DataLoader` ``kwargs``
             - Comments
           * - ``<0``
             - 0
             - Disables multiprocessing entirely, executes everything within the
               same processing context
           * - ``0``
             - :py:func:`multiprocessing.cpu_count`
             - Runs mini-batch data loading on as many external processes as CPUs
               available in the current machine
           * - ``>=1``
             - ``parallel``
             - Runs mini-batch data loading on as many external processes as set on
               ``parallel``

        Returns
        -------
        int
            The value of self._parallel.
        """
        return self._parallel

    @parallel.setter
    def parallel(self, value: int) -> None:
        self._dataloader_multiproc: dict[str, typing.Any] = {}
        self._parallel = value

        if value < 0:
            num_workers = 0

        else:
            num_workers = value or torch.multiprocessing.cpu_count()

        self._dataloader_multiproc["num_workers"] = num_workers

        if num_workers > 0:
            self._dataloader_multiproc["multiprocessing_context"] = "spawn"

        # keep workers hanging around if we have multiple
        if value >= 0:
            self._dataloader_multiproc["persistent_workers"] = True

    @property
    def model_transforms(self) -> TransformSequence | None:
        """Transform required to fit data into the model.

        A list of transforms (torch modules) that will be applied after
        raw-data-loading. and just before data is fed into the model or
        eventual data-augmentation transformations for all data loaders
        produced by this DataModule.  This part of the pipeline receives
        data as output by the raw-data-loader, or model-related
        transforms (e.g. resize adaptions), if any is specified.  If
        data is cached, it is cached **after** model-transforms are
        applied, as that is a potential memory saver (e.g., if it
        contains a resizing operation to smaller images).

        Returns
        -------
        list
            A list containing the model tansforms.
        """
        return self._model_transforms

    @model_transforms.setter
    def model_transforms(self, value: TransformSequence | None):
        old_value = self._model_transforms
        if value is None:
            self._model_transforms = value
        else:
            self._model_transforms = list(value)

        # datasets that have been setup() for the current stage are reset
        if value != old_value and len(self._datasets):
            logger.warning(
                f"Resetting {len(self._datasets)} loaded datasets due "
                "to changes in model-transform properties.  If you were caching "
                "data loading, this will (eventually) trigger a reload.",
            )
            self._datasets = {}

    def _setup_dataset(self, name: str) -> None:
        """Set up a single dataset from the input data split.

        Parameters
        ----------
        name
            Name of the dataset to setup.
        """

        if self.model_transforms is None:
            raise RuntimeError(
                "Parameter `model_transforms` has not yet been "
                "set.  If you do not have model transforms, then "
                "set it to an empty list.",
            )

        if name in self._datasets:
            logger.info(
                f"Dataset `{name}` is already setup. Not re-instantiating it.",
            )
            return

        datasets: list[CachedDataset | _DelayedLoadingDataset] = []
        if self.cache_samples:
            logger.info(
                f"Loading dataset:`{name}` into memory (caching)."
                f" Trade-off: CPU RAM usage: more | Disk I/O: less",
            )
            for split, loader in self.splits[name]:
                datasets.append(
                    CachedDataset(split, loader, self.model_transforms, self.parallel)
                )
        else:
            logger.info(
                f"Loading dataset:`{name}` without caching."
                f" Trade-off: CPU RAM usage: less | Disk I/O: more",
            )
            for split, loader in self.splits[name]:
                datasets.append(
                    _DelayedLoadingDataset(split, loader, self.model_transforms)
                )

        if len(datasets) == 1:
            self._datasets[name] = datasets[0]
        else:
            self._datasets[name] = ConcatDataset(datasets)

    def val_dataset_keys(self) -> list[str]:
        """Return list of validation dataset names.

        Returns
        -------
        list[str]
            The list of validation dataset names.
        """

        validation_split_name = "validation"
        if "validation" not in self.splits.keys():
            logger.warning(
                "No split named 'validation', the training split will be used for validation instead."
            )
            validation_split_name = "train"

        return [validation_split_name] + [
            k for k in self.splits.keys() if k.startswith("monitor-")
        ]

    def setup(self, stage: str) -> None:
        """Set up datasets for different tasks on the pipeline.

        This method should setup (load, pre-process, etc) all datasets required
        for a particular ``stage`` (fit, validate, test, predict), and keep
        them ready to be used on one of the `_dataloader()` functions that are
        pertinent for such stage.

        If you have set ``cache_samples``, samples are loaded at this stage and
        cached in memory.

        Parameters
        ----------
        stage
            Name of the stage in which the setup is applicable.  Can be one of
            ``fit``, ``validate``, ``test`` or ``predict``.  Each stage
            typically uses the following data loaders:

            * ``fit``: uses both train and validation datasets
            * ``validate``: uses only the validation dataset
            * ``test``: uses only the test dataset
            * ``predict``: uses only the test dataset
        """

        if stage == "fit":
            for k in ["train"] + self.val_dataset_keys():
                self._setup_dataset(k)

        elif stage == "validate":
            for k in self.val_dataset_keys():
                self._setup_dataset(k)

        elif stage == "test":
            self._setup_dataset("test")

        elif stage == "predict":
            for k in self.splits:
                self._setup_dataset(k)

    def teardown(self, stage: str) -> None:
        """Unset-up datasets for different tasks on the pipeline.

        This method unsets (unload, remove from memory, etc) all datasets required
        for a particular ``stage`` (fit, validate, test, predict).

        If you have set ``cache_samples``, samples are loaded and this may
        effectivley release all the associated memory.

        Parameters
        ----------
        stage
            Name of the stage in which the teardown is applicable.  Can be one of
            ``fit``, ``validate``, ``test`` or ``predict``.  Each stage
            typically uses the following data loaders:

            * ``fit``: uses both train and validation datasets
            * ``validate``: uses only the validation dataset
            * ``test``: uses only the test dataset
            * ``predict``: uses only the test dataset
        """

        super().teardown(stage)

    def train_dataloader(self) -> DataLoader:
        """Return the train data loader.

        Returns
        -------
            The train data loader(s).
        """

        return torch.utils.data.DataLoader(
            self._datasets["train"],
            shuffle=True,
            batch_size=self.batch_size,
            drop_last=self.drop_incomplete_batch,
            pin_memory=self.pin_memory,
            collate_fn=self.collate_fn,
            **self._dataloader_multiproc,
        )

    def unshuffled_train_dataloader(self) -> DataLoader:
        """Return the train data loader without shuffling.

        Returns
        -------
            The train data loader without shuffling.
        """

        return torch.utils.data.DataLoader(
            self._datasets["train"],
            shuffle=False,
            batch_size=self.batch_size,
            drop_last=False,
            collate_fn=self.collate_fn,
            **self._dataloader_multiproc,
        )

    def val_dataloader(self) -> dict[str, DataLoader]:
        """Return the validation data loader(s).

        Returns
        -------
            The validation data loader(s).
        """

        validation_loader_opts = {
            "batch_size": self.batch_size,
            "shuffle": False,
            "drop_last": self.drop_incomplete_batch,
            "pin_memory": self.pin_memory,
        }
        validation_loader_opts.update(self._dataloader_multiproc)

        return {
            k: torch.utils.data.DataLoader(
                self._datasets[k],
                collate_fn=self.collate_fn,
                **validation_loader_opts,
            )
            for k in self.val_dataset_keys()
        }

    def test_dataloader(self) -> dict[str, DataLoader]:
        """Return the test data loader(s).

        Returns
        -------
            The test data loader(s).
        """

        return dict(
            test=torch.utils.data.DataLoader(
                self._datasets["test"],
                batch_size=self.batch_size,
                shuffle=False,
                drop_last=self.drop_incomplete_batch,
                pin_memory=self.pin_memory,
                collate_fn=self.collate_fn,
                **self._dataloader_multiproc,
            ),
        )

    def predict_dataloader(self) -> dict[str, DataLoader]:
        """Return the prediction data loader(s).

        Returns
        -------
            The prediction data loader(s).
        """

        return {
            k: torch.utils.data.DataLoader(
                self._datasets[k],
                batch_size=self.batch_size,
                shuffle=False,
                drop_last=self.drop_incomplete_batch,
                pin_memory=self.pin_memory,
                collate_fn=self.collate_fn,
                **self._dataloader_multiproc,
            )
            for k in self._datasets
        }


class CachingDataModule(ConcatDataModule):
    """A simplified version of our DataModule for a single split.

    Apart from construction, the behaviour of this DataModule is very similar
    to its simpler counterpart, serving training, validation and test sets.

    Parameters
    ----------
    database_split
        A dictionary that contains string keys representing dataset names, and
        values that are iterables over sample representations (potentially on
        disk).  These objects are passed to an unique
        :py:class:`.data.typing.RawDataLoader` for loading the
        :py:data:`.typing.Sample` data (and metadata) in memory.  It
        therefore assumes the whole split is homogeneous and can be loaded in
        the same way.

        .. tip::

           To check the split and the loader function works correctly, you may
           use :py:func:`.split.check_database_split_loading`.

        This class expects at least one entry called ``train`` to exist in the
        input dictionary.  Optional entries are ``validation``, and ``test``.
        Entries named ``monitor-...`` will be considered extra datasets that do
        not influence any early stop criteria during training, and are just
        monitored beyond the ``validation`` dataset.
    raw_data_loader
        An object instance that can load samples from storage.
    **kwargs
        List of named parameters matching those of
        :py:class:`ConcatDataModule`, other than ``splits``.
    """

    def __init__(
        self,
        database_split: DatabaseSplit,
        raw_data_loader: RawDataLoader,
        **kwargs,
    ):
        splits = {k: [(v, raw_data_loader)] for k, v in database_split.items()}
        super().__init__(
            splits=splits,
            **kwargs,
        )
