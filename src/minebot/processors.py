import os
import platform


def detect_processor_options() -> list[dict[str, object]]:
    options: list[dict[str, object]] = [
        {
            "value": "auto",
            "label": "自动（优先 GPU）",
            "kind": "auto",
            "device_id": -1,
        },
        {
            "value": "cpu",
            "label": f"CPU · {_cpu_name()}",
            "kind": "cpu",
            "device_id": -1,
        },
    ]

    try:
        import pynvml

        pynvml.nvmlInit()
        try:
            for index in range(pynvml.nvmlDeviceGetCount()):
                handle = pynvml.nvmlDeviceGetHandleByIndex(index)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8", errors="replace")
                options.append(
                    {
                        "value": f"cuda:{index}",
                        "label": f"GPU {index} · {name}",
                        "kind": "cuda",
                        "device_id": index,
                    }
                )
        finally:
            pynvml.nvmlShutdown()
    except Exception:
        pass

    return options


def _cpu_name() -> str:
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            ) as key:
                name = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
                if name:
                    return name
        except OSError:
            pass
    return platform.processor() or f"{os.cpu_count() or 1} threads"
