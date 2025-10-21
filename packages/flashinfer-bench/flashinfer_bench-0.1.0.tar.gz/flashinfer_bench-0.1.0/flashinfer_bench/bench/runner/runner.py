from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import torch

from flashinfer_bench.bench.config import BenchmarkConfig
from flashinfer_bench.data import Definition, Evaluation, Solution, Workload


class RunnerError(RuntimeError): ...


class RunnerFatalError(RunnerError): ...


class BaselineHandle(str):
    pass


@dataclass
class DeviceBaseline:
    handle: BaselineHandle
    defn: Definition
    device: str
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, torch.Tensor]]
    mean_latency_ms: float


class Runner(ABC):
    def __init__(self, logger: logging.Logger) -> None: ...

    @abstractmethod
    def run_workload(
        self,
        defn: Definition,
        wl: Workload,
        solutions: List[Solution],
        config: BenchmarkConfig,
        root: Path,
    ) -> Dict[str, Evaluation]: ...
