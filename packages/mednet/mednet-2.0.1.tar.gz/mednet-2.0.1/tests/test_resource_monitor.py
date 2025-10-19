# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for the CPU/GPU resource monitor utilities."""

import os
import platform
import shutil
import time

import numpy
import pytest


def test_cpu_constants():
    from mednet.utils.resources import cpu_constants

    v = cpu_constants()
    assert "memory-total-GB/cpu" in v
    assert "number-of-cores/cpu" in v


def test_combined_monitor_cpu_only():
    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import _CombinedMonitor

    monitor = _CombinedMonitor(
        device_type=DeviceManager("cpu").device_type,
        main_pid=os.getpid(),
    )

    log1 = monitor.log()

    assert isinstance(log1, dict)
    assert "timestamp" in log1
    assert "num-processes/cpu" in log1
    assert log1["num-processes/cpu"] >= 1

    log2 = monitor.log()

    assert isinstance(log2, dict)
    assert "timestamp" in log2
    assert log1["timestamp"] != log2["timestamp"]


@pytest.mark.skipif(
    (platform.system().lower() != "darwin" or platform.processor() != "arm"),
    reason="Requires macOS on Apple silicon to run",
)
def test_mps_constants():
    from mednet.utils.resources import mps_constants

    v = mps_constants()
    assert "apple-processor-model" in v
    assert "number-of-cores/gpu" in v


@pytest.mark.skipif(
    (platform.system().lower() != "darwin" or platform.processor() != "arm"),
    reason="Requires macOS on Apple silicon to run",
)
def test_combined_monitor_macos_gpu():
    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import _CombinedMonitor

    monitor = _CombinedMonitor(
        device_type=DeviceManager("mps").device_type,
        main_pid=os.getpid(),
    )

    log1 = monitor.log()

    assert isinstance(log1, dict)
    assert "timestamp" in log1
    assert "num-processes/cpu" in log1
    assert log1["num-processes/cpu"] >= 1
    assert "percent-usage/gpu" in log1
    assert "frequency-MHz/gpu" in log1

    log2 = monitor.log()

    assert isinstance(log2, dict)
    assert "timestamp" in log2
    assert "percent-usage/gpu" in log2
    assert "frequency-MHz/gpu" in log2
    assert log1["timestamp"] != log2["timestamp"]


@pytest.mark.skipif(
    shutil.which("nvidia-smi") is None, reason="Requires nvidia-smi to run"
)
def test_cuda_constants():
    from mednet.utils.resources import cuda_constants

    v = cuda_constants()
    assert "driver-version/gpu" in v
    assert "total-memory-GB/gpu" in v


@pytest.mark.skipif(
    shutil.which("nvidia-smi") is None, reason="Requires nvidia-smi to run"
)
def test_combined_monitor_nvidia_gpu():
    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import _CombinedMonitor

    monitor = _CombinedMonitor(
        device_type=DeviceManager("cuda").device_type,
        main_pid=os.getpid(),
    )

    log1 = monitor.log()

    assert isinstance(log1, dict)
    assert "timestamp" in log1
    assert "num-processes/cpu" in log1
    assert log1["num-processes/cpu"] >= 1
    assert "percent-usage/gpu" in log1
    assert "memory-used-GB/gpu" in log1
    assert "memory-percent/gpu" in log1

    log2 = monitor.log()

    assert isinstance(log2, dict)
    assert "timestamp" in log2
    assert "percent-usage/gpu" in log2
    assert "memory-used-GB/gpu" in log2
    assert "memory-percent/gpu" in log2
    assert log1["timestamp"] != log2["timestamp"]


def test_aggregation():
    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import _CombinedMonitor, aggregate

    monitor = _CombinedMonitor(
        device_type=DeviceManager("cpu").device_type,
        main_pid=os.getpid(),
    )

    logs = []

    for _ in range(5):
        time.sleep(0.2)
        logs.append(monitor.log())

    agg = aggregate(logs)
    assert "cpu-monitoring-samples" in agg
    assert agg["cpu-monitoring-samples"] == 5

    assert "timestamp" in agg
    assert agg["timestamp"] == logs[-1]["timestamp"] - logs[0]["timestamp"]

    assert "num-processes/cpu" in agg
    assert agg["num-processes/cpu"] == max([k["num-processes/cpu"] for k in logs])

    assert "num-open-files/cpu" in agg
    assert agg["num-open-files/cpu"] == max([k["num-open-files/cpu"] for k in logs])

    assert "percent-usage/cpu" in agg
    assert numpy.isclose(
        agg["percent-usage/cpu"],
        sum([k["percent-usage/cpu"] for k in logs]) / agg["cpu-monitoring-samples"],
    )


def test_mp_cpu_monitoring():
    # Checks a "normal" workflow, where the monitoring interval is smaller than
    # the total work time

    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import ResourceMonitor, aggregate

    rm = ResourceMonitor(
        interval=0.2,
        device_type=DeviceManager("cpu").device_type,
        main_pid=os.getpid(),
    )

    with rm:
        time.sleep(0.5)
        logs = rm.checkpoint()
        assert len(logs) >= 2
        agg = aggregate(logs)
        assert agg["cpu-monitoring-samples"] >= 2


def test_mp_cpu_monitoring_short_processing():
    # Checks we can get at least 1 monitoring sample even if the processing is
    # super short

    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import ResourceMonitor, aggregate

    rm = ResourceMonitor(
        interval=0.5,
        device_type=DeviceManager("cpu").device_type,
        main_pid=os.getpid(),
    )

    with rm:
        time.sleep(0.2)  # shorter than interval
        logs = rm.checkpoint()
        assert len(logs) == 1
        agg = aggregate(logs)
        assert agg["cpu-monitoring-samples"] == 1


@pytest.mark.skipif(
    (platform.system().lower() != "darwin" or platform.processor() != "arm"),
    reason="Requires macOS on Apple silicon to run",
)
def test_mp_macos_gpu_monitoring():
    # Checks a "normal" workflow, where the monitoring interval is smaller than
    # the total work time

    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import ResourceMonitor, aggregate

    rm = ResourceMonitor(
        interval=1.5,
        device_type=DeviceManager("mps").device_type,
        main_pid=os.getpid(),
    )

    with rm:
        time.sleep(3.0)
        logs = rm.checkpoint()
        assert len(logs) >= 1
        agg = aggregate(logs)
        assert agg["cpu-monitoring-samples"] >= 1


@pytest.mark.skipif(
    (platform.system().lower() != "darwin" or platform.processor() != "arm"),
    reason="Requires macOS on Apple silicon to run",
)
def test_mp_macos_gpu_monitoring_short_processing():
    # Checks we can get at least 1 monitoring sample even if the processing is
    # shorter.  In this check we execute an external utility which may
    # delay obtaining samples.

    from mednet.engine.device import DeviceManager
    from mednet.utils.resources import ResourceMonitor, aggregate

    rm = ResourceMonitor(
        interval=1.5,  # on my mac, this measurements take ~0.9s
        device_type=DeviceManager("mps").device_type,
        main_pid=os.getpid(),
    )

    with rm:
        time.sleep(1)  # shorter than interval
        logs = rm.checkpoint()
        assert len(logs) == 1
        agg = aggregate(logs)
        assert agg["cpu-monitoring-samples"] == 1
