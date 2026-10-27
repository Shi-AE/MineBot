import ctypes
import importlib.util
import os
from pathlib import Path


_DLL_HANDLES: list[object] = []


def _prepare_cuda_runtime() -> bool:
    if os.name != "nt":
        return True

    spec = importlib.util.find_spec("onnxruntime")
    if spec is None or not spec.submodule_search_locations:
        return False

    site_packages = Path(next(iter(spec.submodule_search_locations))).parent
    torch_lib = site_packages / "torch" / "lib"
    if not torch_lib.is_dir():
        return False

    os.environ["PATH"] = str(torch_lib) + os.pathsep + os.environ.get("PATH", "")
    try:
        _DLL_HANDLES.append(os.add_dll_directory(str(torch_lib)))
        _DLL_HANDLES.append(ctypes.WinDLL("cublas64_13.dll"))
        _DLL_HANDLES.append(ctypes.WinDLL("cublasLt64_13.dll"))
        _DLL_HANDLES.append(ctypes.WinDLL("cudnn64_9.dll"))
    except OSError:
        return False
    return True


_CUDA_RUNTIME_AVAILABLE = _prepare_cuda_runtime()

import onnxruntime as ort


_CPU_INTRA_OP_THREADS = min(12, os.cpu_count() or 1)


def create_session(
    model_path: Path,
    processor: str,
) -> tuple[ort.InferenceSession, str]:
    available = set(ort.get_available_providers())
    gpu_device = _gpu_device(processor)
    if (
        gpu_device is not None
        and _CUDA_RUNTIME_AVAILABLE
        and "CUDAExecutionProvider" in available
    ):
        providers = ["CUDAExecutionProvider"]
        if "CPUExecutionProvider" in available:
            providers.append("CPUExecutionProvider")
        session_args: dict[str, object] = {}
        if gpu_device > 0:
            session_args["provider_options"] = [
                {"device_id": str(gpu_device)},
                *([{}] if "CPUExecutionProvider" in available else []),
            ]

        try:
            session = ort.InferenceSession(
                str(model_path),
                sess_options=_gpu_session_options(),
                providers=providers,
                **session_args,
            )
            if session.get_providers()[0] == "CUDAExecutionProvider":
                return session, f"cuda:{gpu_device}"
        except Exception:
            pass

    if "CPUExecutionProvider" not in available:
        raise RuntimeError("no compatible ONNX Runtime provider")
    session = ort.InferenceSession(
        str(model_path),
        sess_options=_cpu_session_options(),
        providers=["CPUExecutionProvider"],
    )
    return session, "cpu"


def _gpu_session_options() -> ort.SessionOptions:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.log_severity_level = 3
    return options


def _cpu_session_options() -> ort.SessionOptions:
    options = ort.SessionOptions()
    options.intra_op_num_threads = _CPU_INTRA_OP_THREADS
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.add_session_config_entry("session.intra_op.allow_spinning", "0")
    options.add_session_config_entry("session.inter_op.allow_spinning", "0")
    options.log_severity_level = 3
    return options


def _gpu_device(processor: str) -> int | None:
    if processor == "cpu":
        return None
    if processor == "auto":
        return 0
    if processor.startswith("cuda:"):
        try:
            return max(0, int(processor.split(":", 1)[1]))
        except ValueError:
            return None
    return None
