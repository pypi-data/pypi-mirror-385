# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tools for interacting with the running computer or GPU."""

import logging
import multiprocessing
import multiprocessing.synchronize
import os
import plistlib
import queue
import shutil
import subprocess
import time
import typing
import warnings

import numpy
import psutil

from ..engine.device import SupportedPytorchDevice

logger = logging.getLogger(__name__)

_nvidia_smi = shutil.which("nvidia-smi")
"""Location of the nvidia-smi program, if one exists."""


GB = float(2**30)
"""The number of bytes in a gigabyte."""


def _run_nvidia_smi(query: typing.Sequence[str]) -> dict[str, str | float]:
    """Return GPU information from query.

    For a comprehensive list of options and help, execute ``nvidia-smi
    --help-query-gpu`` on a host with a GPU

    Parameters
    ----------
    query
        A list of query strings as defined by ``nvidia-smi --help-query-gpu``.

    Returns
    -------
    dict[str, str | float]
        A dictionary containing the queried parameters (``rename`` versions).
        If ``nvidia-smi`` is not available, returns ``None``.  Percentage
        information is left alone, memory information is transformed to
        gigabytes (floating-point).
    """

    if _nvidia_smi is None:
        warnings.warn(
            "Cannot find `nvidia-smi` on your $PATH. Install it or choose "
            "another backend to run. Cannot return GPU information without "
            "this executable."
        )
        return {}

    # Gets GPU information, based on a GPU device if that is set. Returns
    # ordered results.
    query_str = f"{_nvidia_smi} --query-gpu={','.join(query)} --format=csv,noheader"
    visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES")
    if visible_devices:
        query_str += f" --id={visible_devices}"
    values = subprocess.getoutput(query_str)

    retval: dict[str, str | float] = {}
    for i, k in enumerate([k.strip() for k in values.split(",")]):
        retval[query[i]] = k
        if k.endswith("%"):
            retval[query[i]] = float(k[:-1].strip())
        elif k.endswith("MiB"):
            retval[query[i]] = float(k[:-3].strip()) / 1024
    return retval


def _run_powermetrics(
    time_window_ms: int = 500, key: str | None = None
) -> dict[str, typing.Any]:
    """Return GPU information from the system.

    For a comprehensive list of options and help, execute ``man powermetrics``
    on a Mac computer with Apple silicon.

    Parameters
    ----------
    time_window_ms
        The amount of time, in milliseconds, to collect usage information on
        the GPU.
    key
        If specified returns only a sub-key of the dictionary.

    Returns
    -------
        A dictionary containing the GPU information.
    """

    cmd = [
        "sudo",
        "-n",
        "/usr/bin/powermetrics",
        "--samplers",
        "gpu_power",
        f"-i{time_window_ms}",
        "-n1",
        "-fplist",
    ]

    try:
        raw_bytes = subprocess.check_output(cmd)
        data = plistlib.loads(raw_bytes)
        return data[key] if key is not None else data

    except subprocess.CalledProcessError:
        warnings.warn(
            f"Cannot run `sudo powermetrics` without a password. Probably, "
            f"you did not setup sudo to execute the macOS CLI application "
            f"`powermetrics` passwordlessly and therefore this warning is "
            f"being issued. This does not affect the running of your model "
            f"training, only the ability of the resource monitor of gathering "
            f"GPU usage information on macOS while using the MPS compute "
            f"backend.  To configure this properly and get rid of this "
            f"warning, execute `sudo visudo` and add the following line where "
            f"suitable: `yourusername ALL=(ALL) NOPASSWD:SETENV: "
            f"/usr/bin/powermetrics`. Replace `yourusername` by your actual "
            f"username on the machine. Test the setup running the command "
            f"`{' '.join(cmd)}` by hand."
        )

    return {}


def cuda_constants() -> dict[str, str | int | float]:
    """Return GPU (static) information using nvidia-smi.

    Check ``_run_nvidia_smi()`` for operational details if necessary.

    Returns
    -------
    dict[str, str | int | float]
        If ``nvidia-smi`` is not available, returns ``None``, otherwise, we
        return a dictionary containing the following ``nvidia-smi`` query
        information, in this order:

        * ``gpu_name``, as ``gpu_name`` (:py:class:`str`)
        * ``driver_version``, as ``gpu_driver_version`` (:py:class:`str`)
        * ``memory.total``, as ``gpu_memory_total`` (transformed to gigabytes,
          :py:class:`float`)
    """

    retval = _run_nvidia_smi(("gpu_name", "driver_version", "memory.total"))
    if retval:
        retval["driver-version/gpu"] = retval.pop("driver_version")
        retval["total-memory-GB/gpu"] = retval.pop("memory.total")
    return retval


def mps_constants() -> dict[str, str | int | float]:
    """Return GPU (static) information using `/usr/bin/powermetrics`.

    Returns
    -------
    dict[str, str | int | float]
        If ``nvidia-smi`` is not available, returns ``None``, otherwise, we
        return a dictionary containing the following ``nvidia-smi`` query
        information, in this order:

        * ``gpu_name``, as ``gpu_name`` (:py:class:`str`)
        * ``driver_version``, as ``gpu_driver_version`` (:py:class:`str`)
        * ``memory.total``, as ``gpu_memory_total`` (transformed to gigabytes,
          :py:class:`float`)
    """

    raw_bytes = subprocess.check_output(
        ["/usr/sbin/system_profiler", "-xml", "SPDisplaysDataType"],
    )
    data = plistlib.loads(raw_bytes)
    name = data[0]["_items"][0]["_name"]
    no_gpu_cores = int(data[0]["_items"][0]["sppci_cores"])

    return {
        "apple-processor-model": name,
        "number-of-cores/gpu": no_gpu_cores,
    }


def _cuda_log() -> dict[str, float]:
    """Return GPU information about current non-static status using nvidia-
    smi.

    See :py:func:`_run_nvidia_smi` for operational details.

    Returns
    -------
    dict[str, float]
        If ``nvidia-smi`` is not available, returns ``None``, otherwise, we
        return a dictionary containing the following ``nvidia-smi`` query
        information, in this order:

        * ``memory.used``, as ``memory-used-GB/gpu`` (transformed to gigabytes,
          :py:class:`float`)
        * ``memory.free``, as ``memory-free-GB/gpu`` (transformed to gigabytes,
          :py:class:`float`)
        * ``100*memory.used/memory.total``, as ``memory-percent/gpu``,
          (:py:class:`float`, in percent)
        * ``utilization.gpu``, as ``percent-usage/gpu``,
          (:py:class:`float`, in percent)
    """

    result = _run_nvidia_smi(
        ("memory.total", "memory.used", "memory.free", "utilization.gpu"),
    )

    if not result:
        return {}

    return {
        "memory-used-GB/gpu": float(result["memory.used"]),
        "memory-free-GB/gpu": float(result["memory.free"]),
        "memory-percent/gpu": 100
        * float(result["memory.used"])
        / float(result["memory.total"]),
        "percent-usage/gpu": float(result["utilization.gpu"]),
    }


def _mps_log() -> dict[str, float]:
    """Return GPU information about current non-static status using ``sudo
    powermetrics``.

    Returns
    -------
        If ``sudo powermetrics`` is not executable (or is not configured for
        passwordless execution), returns ``None``, otherwise, we return a
        dictionary containing the following query information, in this order:

        * ``freq_hz`` as ``frequency-MHz/gpu``
        * 100 * (1 - ``idle_ratio``), as ``percent-usage/gpu``,
          (:py:class:`float`, in percent).
    """

    result = _run_powermetrics(500, key="gpu")

    if not result:
        return result

    return {
        "frequency-MHz/gpu": float(result["freq_hz"]),
        "percent-usage/gpu": 100 * (1 - result["idle_ratio"]),
    }


def cpu_constants() -> dict[str, int | float]:
    """Return static CPU information about the current system.

    Returns
    -------
    dict[str, int | float]
        A dictionary containing these entries:

        0. ``cpu_memory_total`` (:py:class:`float`): total memory available,
           in gigabytes
        1. ``cpu_count`` (:py:class:`int`): number of logical CPUs available.
    """

    return {
        "memory-total-GB/cpu": psutil.virtual_memory().total / GB,
        "number-of-cores/cpu": psutil.cpu_count(logical=True),
    }


class _CPUMonitor:
    """Monitors CPU information using :py:mod:`psutil`.

    Parameters
    ----------
    pid
        Process identifier of the main process (parent process) to observe.
    """

    def __init__(self, pid: int | None = None):
        this = psutil.Process(pid=pid)
        self.cluster = [this] + this.children(recursive=True)

        # touch cpu_percent() at least once for all processes in the cluster
        gone = set()
        for k in self.cluster:
            try:
                k.cpu_percent(interval=None)
            except (
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                # child process is gone meanwhile
                # update the intermediate list for this time
                gone.add(k)
        self.cluster = list(set(self.cluster) - gone)

    def log(self) -> dict[str, int | float]:
        """Return current process cluster information.

        Returns
        -------
        dict[str, int | float]
            A dictionary containing these entries:

            0. ``cpu_memory_used`` (:py:class:`float`): total memory used from
               the system, in gigabytes
            1. ``cpu_rss`` (:py:class:`float`):  RAM currently used by
               process and children, in gigabytes
            2. ``cpu_vms`` (:py:class:`float`):  total memory (RAM + swap) currently
               used by process and children, in gigabytes
            3. ``cpu_percent`` (:py:class:`float`): percentage of the total CPU
               used by this process and children (recursively) since last call
               (first time called should be ignored).  This number depends on the
               number of CPUs in the system and can be greater than 100%
            4. ``cpu_processes`` (:py:class:`int`): total number of processes
               including self and children (recursively)
            5. ``cpu_open_files`` (:py:class:`int`): total number of open files by
               self and children
        """

        # check all cluster components and update process list
        # done so we can keep the cpu_percent() initialization
        stored_children = set(self.cluster[1:])
        current_children = set(self.cluster[0].children(recursive=True))
        keep_children = stored_children - current_children
        new_children = current_children - stored_children
        gone = set()
        for k in new_children:
            try:
                k.cpu_percent(interval=None)
            except (
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                # child process is gone meanwhile
                # update the intermediate list for this time
                gone.add(k)
        new_children = new_children - gone
        self.cluster = self.cluster[:1] + list(keep_children) + list(new_children)

        memory_info = []
        cpu_percent = []
        open_files = []
        gone = set()

        for k in self.cluster:
            try:
                memory_info.append(k.memory_info())
                cpu_percent.append(k.cpu_percent(interval=None))
                open_files.append(len(k.open_files()))
            except (
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                # child process is gone meanwhile, just ignore it
                # it is too late to update any intermediate list
                # at this point, but ensures to update counts later on
                gone.add(k)
        return {
            "memory-used-GB/cpu": psutil.virtual_memory().used / GB,
            "rss-GB/cpu": sum([k.rss for k in memory_info]) / GB,
            "vms-GB/cpu": sum([k.vms for k in memory_info]) / GB,
            "percent-usage/cpu": sum(cpu_percent),
            "num-processes/cpu": len(self.cluster) - len(gone),
            "num-open-files/cpu": sum(open_files),
        }

    def show_processes(self) -> str:
        """Return a string representation of currently running processes.

        Returns
        -------
            A string representation of currently running processes for
            debugging purposes.
        """
        return "\n".join([f"(pid={k.pid}) {k.cmdline()}" for k in self.cluster])


class _CombinedMonitor:
    """A helper monitor to log execution information.

    Parameters
    ----------
    device_type
        String representation of one of the supported pytorch device types
        triggering the correct readout of resource usage.
    main_pid
        The main process identifier to monitor.
    """

    def __init__(
        self,
        device_type: SupportedPytorchDevice,
        main_pid: int | None,
    ):
        self.cpu_monitor = _CPUMonitor(main_pid)
        self.device_type = device_type

    def log(self) -> dict[str, int | float]:
        """Combine measures from CPU and GPU monitors.

        Returns
        -------
            A dictionary containing the various logged information.
        """

        # we always log the CPU counters
        retval = {"timestamp": time.time()}
        retval.update(self.cpu_monitor.log())

        match self.device_type:
            case "cpu":
                pass
            case "cuda":
                entries = _cuda_log()
                if entries is not None:
                    retval.update(entries)
            case "mps":
                entries = _mps_log()
                if entries is not None:
                    retval.update(entries)
            case _:
                pass

        return retval


def _monitor_worker(
    interval: int | float,
    device_type: SupportedPytorchDevice,
    main_pid: int,
    stop_event: multiprocessing.synchronize.Event,
    wakeup_event: multiprocessing.synchronize.Event,
    queue: multiprocessing.Queue,
):
    """Monitor worker that measures resources and returns lists.

    Parameters
    ----------
    interval
        Number of seconds to wait between each measurement (maybe a floating
        point number as accepted by :py:func:`time.sleep`).
    device_type
        String representation of one of the supported pytorch device types
        triggering the correct readout of resource usage.
    main_pid
        The main process identifier to monitor.
    stop_event
        Event that indicates if we should continue running or stop.
    wakeup_event
        Event that indicates if we should log again immediately or wait for the
        interval timer.
    queue
        A queue, to send monitoring information back to the spawner.
    """

    monitor = _CombinedMonitor(device_type, main_pid)
    queue.put({})

    while not stop_event.is_set():
        try:
            start = time.time()
            queue.put(monitor.log())
            wait_at_most = interval - (time.time() - start)
            if wait_at_most < 0:
                warnings.warn(
                    f"The time to run a monitor.log() call "
                    f"({(time.time() - start):.2f}s) is larger than the "
                    f"interval of {interval}s. The amount of time between "
                    f"monitor log calls may be larger than the estimated "
                    f"interval time."
                )

            if wait_at_most > 0:
                wakeup_event.wait(timeout=wait_at_most)
            wakeup_event.clear()

        except Exception as e:
            import traceback

            warnings.warn(
                "Iterative CPU/GPU logging did not work properly. "
                "Traceback follows:\n"
                "".join(traceback.format_exception(type(e), e, e.__traceback__))
            )
            time.sleep(0.5)  # wait half a second, and try again!


class ResourceMonitor:
    """An external, non-blocking CPU/GPU resource monitor.

    Parameters
    ----------
    interval
        Number of seconds to wait between each measurement (maybe a floating
        point number as accepted by :py:func:`time.sleep`).
    device_type
        String representation of one of the supported pytorch device types
        triggering the correct readout of resource usage.
    main_pid
        The main process identifier to monitor.
    """

    def __init__(
        self,
        interval: int | float,
        device_type: SupportedPytorchDevice,
        main_pid: int,
    ):
        self.interval = interval
        self.device_type = device_type
        self.main_pid = main_pid
        self.stop_event = multiprocessing.Event()
        self.wakeup_event = multiprocessing.Event()
        self.q: multiprocessing.Queue[dict[str, int | float]] = multiprocessing.Queue()

        self.monitor = multiprocessing.Process(
            target=_monitor_worker,
            name="ResourceMonitorProcess",
            args=(
                self.interval,
                self.device_type,
                self.main_pid,
                self.stop_event,
                self.wakeup_event,
                self.q,
            ),
        )

    def start(self) -> None:
        """Start the monitoring process."""
        if not self.monitor.is_alive():
            timeout = 60  # seconds
            self.monitor.start()
            logger.info(
                f"Started resource monitoring process (PID: {self.monitor.pid})"
            )
            try:
                obj = self.q.get(timeout=timeout)
                if obj != {}:
                    raise RuntimeError(
                        f"Start of monitoring process did not work - we "
                        f"received a non-empty dictionary (size={len(obj)}) "
                        f"from the queue, instead of the expected `None`."
                    )
            except queue.Empty:
                raise RuntimeError(
                    f"Start of monitoring process did not work - we timed "
                    f"after {timeout}s waiting for a confirmation."
                )

    def __enter__(self) -> None:
        """Start the monitoring process."""
        self.start()

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the monitoring process (hard-kill after *timeout* seconds).

        Parameters
        ----------
        timeout
            Timeout for joining the main process.
        """

        logger.debug(f"Stopping resource monitoring process (PID: {self.monitor.pid})")

        if not self.monitor.is_alive():
            return

        # tell the child to exit and wake it up
        self.stop_event.set()
        self.wakeup_event.set()

        self.monitor.join(timeout)
        if self.monitor.is_alive():  # still hanging? kill it.
            logger.warning("ResourceMonitor: soft stop timed out – forcing terminate()")
            self.monitor.terminate()
            self.monitor.join(2.0)

        # be nice to the queue – avoid GC deadlocks at interpreter shutdown
        try:
            self.q.close()
            self.q.join_thread()
        except (OSError, ValueError):
            pass

        if self.monitor.exitcode != 0:
            logger.error(
                f"CPU/GPU resource monitor process exited with code "
                f"{self.monitor.exitcode}.  Check logs for errors!",
            )

        logger.info(
            f"Stopped resource monitoring process (PID: {self.monitor.pid}, "
            f"exit code: {self.monitor.exitcode})"
        )

    def __exit__(self, *_) -> None:
        """Stop the monitoring process."""
        self.stop()

    def clear(self) -> None:
        """Prepare for an acquisition cycle by clearing logged events."""
        while not self.q.empty():
            self.q.get()
        self.wakeup_event.set()

    def checkpoint(self) -> list[dict[str, int | float]]:
        """Force the monitoring process to yield data and clear the internal
        accumulator.

        Returns
        -------
        list[dict[str, int | float]]
            A list of hardware counters that were monitored during the
            start/end interval.
        """

        data: list[dict[str, int | float]] = []
        while not self.q.empty():
            data.append(self.q.get())
        self.wakeup_event.set()
        return data


def aggregate(
    data: list[dict[str, int | float]],
    start: int | None = 0,
    end: int | None = None,
) -> dict[str, int | float]:
    """Aggregate monitored data to average/max each entry.

    Parameters
    ----------
    data
        Input data collected by the resource monitor, in the format of a list.
    start
        Start index to aggregate data from at the ``data`` list.
    end
        End index to aggregate data to at the ``data`` list.

    Returns
    -------
    dict[str, int | float]
        A collapsed representation of the input list with the common keys found
        in all dictionaries and averages (or maximum values) of measures found
        across similar keys.
    """
    if not data:
        return {}

    # aggregate data: list of dicts -> dict of lists
    def _acc(k, v):
        match k:
            case "num-processes/cpu" | "num-open-files/cpu":
                return numpy.max(v)
            case "timestamp":
                if len(v) > 1:
                    return v[-1] - v[0]
                return v[0]
            case _:
                return float(numpy.mean(v))

    retval = {
        k: _acc(k, [j.get(k, 0) for j in data][start:end]) for k in data[0].keys()
    }
    retval["cpu-monitoring-samples"] = len(data)
    return retval
