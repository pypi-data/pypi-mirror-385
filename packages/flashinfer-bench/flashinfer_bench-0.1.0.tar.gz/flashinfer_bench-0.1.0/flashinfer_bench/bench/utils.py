from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch

from flashinfer_bench.bench.config import BenchmarkConfig
from flashinfer_bench.data import (
    Correctness,
    Definition,
    Evaluation,
    EvaluationStatus,
    Performance,
    Workload,
)
from flashinfer_bench.utils import dtype_str_to_torch_dtype, env_snapshot, flush_stdio_streams


def _rand_tensor(shape: List[int], dtype: torch.dtype, device: torch.device) -> torch.Tensor:
    if dtype in (torch.float32, torch.float16, torch.bfloat16):
        return torch.randn(shape, dtype=dtype, device=device)

    # low-precision floats
    if dtype in (torch.float8_e4m3fn, torch.float8_e5m2, torch.float4_e2m1fn_x2):
        t = torch.randn(shape, dtype=torch.float32, device=device).clamp_(-2.0, 2.0)
        return t.to(dtype)

    # booleans
    if dtype is torch.bool:
        return torch.randint(0, 2, shape, dtype=torch.bool, device=device)

    # integers
    if dtype in (torch.int8, torch.int16, torch.int32, torch.int64):
        ranges = {
            torch.int8: (-128, 128),
            torch.int16: (-1024, 1024),
            torch.int32: (-1024, 1024),
            torch.int64: (-1024, 1024),
        }
        low, high = ranges[dtype]
        return torch.randint(low, high, shape, device=device, dtype=dtype)

    raise ValueError(f"Unsupported random dtype: {dtype}")


def normalize_outputs(
    out: Any,
    *,
    device: torch.device,
    output_names: List[str],
    output_dtypes: Dict[str, torch.dtype],
) -> Dict[str, torch.Tensor]:
    def to_tensor(name: str, v: Any) -> torch.Tensor:
        if isinstance(v, torch.Tensor):
            return v.to(device) if v.device != device else v
        dtype = output_dtypes[name]
        # Python scalar -> 0-D tensor for comparison
        return torch.tensor(v, dtype=dtype, device=device)

    if isinstance(out, dict):
        return {k: to_tensor(k, v) for k, v in out.items() if k in output_dtypes}

    if isinstance(out, torch.Tensor):
        if len(output_names) != 1:
            raise RuntimeError("Single Tensor returned but multiple outputs are defined")
        name = output_names[0]
        return {name: to_tensor(name, out)}

    if isinstance(out, (int, float, bool)):
        if len(output_names) != 1:
            raise RuntimeError("Scalar returned but multiple outputs are defined")
        name = output_names[0]
        return {name: to_tensor(name, out)}

    if isinstance(out, (tuple, list)):
        if len(out) != len(output_names):
            raise RuntimeError(
                f"Tuple/list has {len(out)} elements but {len(output_names)} outputs expected"
            )
        return {name: to_tensor(name, val) for name, val in zip(output_names, out)}

    raise RuntimeError(
        "Unexpected return type; must be Tensor, scalar, or dict[name -> Tensor/scalar]"
    )


def compute_error_stats(
    output: torch.Tensor, reference: torch.Tensor, cfg: BenchmarkConfig
) -> Tuple[float, float, bool, float]:
    x = output.to(torch.float32)
    y = reference.to(torch.float32)

    eps = 1e-8
    abs_error = torch.abs(x - y)
    rel_error = abs_error / (torch.abs(y) + eps)

    total_elements = abs_error.numel()
    if total_elements == 0:
        return 0.0, 0.0, False, 1.0

    required_matched_ratio = (
        cfg.required_matched_ratio if cfg.required_matched_ratio is not None else 1.0
    )
    exceeds_tol_mask = (abs_error > cfg.atol) & (rel_error > cfg.rtol)
    exceeds_count = float(exceeds_tol_mask.sum().item())
    matched_ratio = 1.0 - (exceeds_count / float(total_elements))
    matched_ratio = max(0.0, min(1.0, matched_ratio))

    exceeds_tol = matched_ratio < required_matched_ratio

    max_abs = float(abs_error.max().item())
    max_rel = float(rel_error.max().item())

    return max_abs, max_rel, exceeds_tol, matched_ratio


def is_sampling_operation(defn: Definition) -> bool:
    return getattr(defn, "op_type", None) == "sampling"


def compute_frequency_distribution(
    runnable: Any,
    inputs: List[Dict[str, Any]],
    device: str,
    defn: Definition,
    num_trials: int = 10000,
) -> torch.Tensor:
    inp = inputs[0]

    workload_batch_size = inp["probs"].shape[0] if inp["probs"].dim() > 1 else 1
    vocab_size = inp["probs"].shape[-1]
    counter = torch.zeros(vocab_size, dtype=torch.int64, device=torch.device(device))

    trials_needed = (num_trials + workload_batch_size - 1) // workload_batch_size
    total_samples_collected = 0

    for trial in range(trials_needed):
        with torch.no_grad():
            out = runnable(**inp)

        output_names = list(defn.outputs.keys())
        output_dtypes = {k: dtype_str_to_torch_dtype(v.dtype) for k, v in defn.outputs.items()}

        out_normalized = normalize_outputs(
            out, device=torch.device(device), output_names=output_names, output_dtypes=output_dtypes
        )

        samples = out_normalized["samples"]

        if samples.dim() == 0:
            sample_idx = samples.item()
            counter[sample_idx] += 1
            total_samples_collected += 1
        else:  # Batch of samples
            for i in range(samples.numel()):
                sample_idx = samples.flatten()[i].item()
                counter[sample_idx] += 1
                total_samples_collected += 1

    frequency = counter.float() / total_samples_collected
    return frequency


def load_safetensors(
    defn: Definition, wl: Workload, traceset_root: Optional[Path] = None
) -> Dict[str, torch.Tensor]:
    try:
        import safetensors.torch as st
    except Exception:
        raise RuntimeError("safetensors is not available in the current environment")

    expected = defn.get_input_shapes(wl.axes)
    stensors: Dict[str, torch.Tensor] = {}
    for name, input_spec in wl.inputs.items():
        if input_spec.type != "safetensors":
            continue

        path = input_spec.path
        if traceset_root is not None and not Path(path).is_absolute():
            path = str(traceset_root / path)

        tensors = st.load_file(path)
        if input_spec.tensor_key not in tensors:
            raise ValueError(f"Missing key '{input_spec.tensor_key}' in '{path}'")
        t = tensors[input_spec.tensor_key]
        # shape check
        if list(t.shape) != expected[name]:
            raise ValueError(f"'{name}' expected {expected[name]}, got {list(t.shape)}")
        # dtype check
        expect_dtype = dtype_str_to_torch_dtype(defn.inputs[name].dtype)
        if t.dtype != expect_dtype:
            raise ValueError(f"'{name}' expected {expect_dtype}, got {t.dtype}")

        try:
            t = t.contiguous().pin_memory()
        except Exception:
            t = t.contiguous()
        stensors[name] = t
    return stensors


def gen_inputs(
    defn: Definition, wl: Workload, device: str, stensors: Optional[Dict[str, torch.Tensor]] = None
) -> Dict[str, Any]:
    shapes = defn.get_input_shapes(wl.axes)
    dev = torch.device(device)
    out: Dict[str, Any] = {}

    for name, spec in defn.inputs.items():
        dtype = dtype_str_to_torch_dtype(spec.dtype)

        if name in wl.inputs and wl.inputs[name].type == "safetensors":
            if stensors is None or name not in stensors:
                raise RuntimeError(f"Missing required safetensors input '{name}'")
            t_cpu = stensors[name]
            out[name] = t_cpu.to(device=dev, non_blocking=True)
        elif name in wl.inputs and wl.inputs[name].type == "scalar":
            out[name] = wl.inputs[name].value
        else:  # random
            shape = shapes[name]
            tensor = _rand_tensor(shape, dtype, dev)

            if is_sampling_operation(defn) and name == "probs":
                tensor = torch.softmax(tensor, dim=-1)  # convert logits to probs for sampling

            out[name] = tensor
    return out


_MAX_EMBEDDED_LOG_BYTES = 5 * 1024 * 1024


def _read_log_file(
    log_path: Optional[str], *, limit: int = _MAX_EMBEDDED_LOG_BYTES
) -> Optional[str]:
    if not log_path:
        return None

    flush_stdio_streams()

    try:
        with open(log_path, "rb") as fh:
            data = fh.read(limit + 1)
    except FileNotFoundError:
        return None
    except OSError:
        return None

    truncated = len(data) > limit
    if truncated:
        data = data[:limit]

    text = data.decode("utf-8", errors="replace")
    if truncated:
        text += "\n\n[log truncated]\n"
    return text


def make_eval(
    status: EvaluationStatus,
    device: str,
    log_path: Optional[str],
    correctness: Optional[Correctness] = None,
    performance: Optional[Performance] = None,
    extra_msg: Optional[str] = None,
) -> Evaluation:
    log_text = _read_log_file(log_path) or ""
    if extra_msg:
        log_text = log_text + "\n" + extra_msg if log_text else extra_msg
    return Evaluation(
        status=status,
        log=log_text,
        environment=env_snapshot(device),
        timestamp=datetime.now().isoformat(),
        correctness=correctness,
        performance=performance,
    )
