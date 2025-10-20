"""
Builtin implementations with optional hookspec version range and priorities.
"""
from __future__ import annotations
import time
import pluggy
from typing import Any, Dict, Optional
from ddoc.core.io import read_text, write_text, write_json

hookimpl = pluggy.HookimplMarker("ddoc")

# Builtin declares compatibility window (optional)
DDOC_HOOKSPEC_MIN = "1.0.0"
DDOC_HOOKSPEC_MAX = "1.999.999"

@hookimpl(tryfirst=True)  # prefer builtin for EDA if multiple present
def eda_run(input_path: str, modality: str, output_path: str):
    try:
        data = read_text(input_path)
        summary = {
            "modality": modality,
            "lines": len(data.splitlines()),
            "bytes": len(data.encode("utf-8")),
            "preview": data[:100],
            "created_at": time.time(),
        }
        write_json(output_path, summary)
        return {"ok": True, "written": output_path}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@hookimpl  # default priority
def transform_apply(input_path: str, transform: str, args: Dict[str, Any], output_path: str):
    try:
        data = read_text(input_path)
        if transform == "text.upper":
            out = data.upper()
        elif transform == "text.lower":
            out = data.lower()
        else:
            out = data
        write_text(output_path, out)
        return {"ok": True, "written": output_path, "transform": transform}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@hookimpl(trylast=True)  # run last; allows external drift impls to win
def drift_detect(ref_path: str, cur_path: str, detector: str, cfg: Optional[Dict[str, Any]], output_path: str):
    try:
        ref = read_text(ref_path).splitlines()
        cur = read_text(cur_path).splitlines()
        ref_n, cur_n = len(ref), len(cur)
        diff = abs(ref_n - cur_n)
        ratio = diff / max(ref_n, 1)
        report = {"detector": detector, "ref_lines": ref_n, "cur_lines": cur_n, "diff_ratio": ratio, "is_drift": ratio > 0.1}
        write_json(output_path, report)
        return {"ok": True, "written": output_path, "is_drift": report["is_drift"]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@hookimpl
def reconstruct_apply(input_path: str, method: str, args: Dict[str, Any], output_path: str):
    try:
        lines = [ln for ln in read_text(input_path).splitlines() if ln.strip()]
        write_text(output_path, "\n".join(lines))
        return {"ok": True, "written": output_path, "method": method}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@hookimpl
def retrain_run(train_path: str, trainer: str, params: Dict[str, Any], model_out: str):
    try:
        content = read_text(train_path)
        meta = {"trainer": trainer, "params": params, "train_size": len(content), "artifact": model_out}
        write_json(model_out, meta)
        return {"ok": True, "model": model_out}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@hookimpl
def monitor_run(source: str, mode: str, schedule: Optional[str]):
    return {"ok": True, "mode": mode, "source": source, "scheduled": bool(schedule)}