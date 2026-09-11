#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Run ffmpeg-quality-metrics (VMAF) for every PVS against its source, for several models.

Usage: run_vmaf.py <pvs_dir> [parallel] [vmaf_threads]
Output: results/<config>/<pvs_stem>.json (skipped if present and valid).
"""
import json, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src"
RES = BASE / "results"
FF = BASE / "bin/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg"
# Scoring tool. Default: fetch from PyPI via uvx. To use a local checkout instead,
# set FQM_CHECKOUT=<checkout path> (expects <checkout>/.venv/bin/ffmpeg-quality-metrics).
HARNESS_DIR = None
HARNESS = ["uvx", "ffmpeg-quality-metrics>=3.12.1"]
if os.environ.get("FQM_CHECKOUT"):
    HARNESS_DIR = os.environ["FQM_CHECKOUT"]
    HARNESS = [f"{HARNESS_DIR}/.venv/bin/ffmpeg-quality-metrics"]

# config name -> (model file, extra args)
CONFIGS = {
    "v0_1080":        ("vmaf_v0.6.1.json",            ["--vmaf-10bit"]),
    "v0_4k":          ("vmaf_4k_v0.6.1.json",         ["--vmaf-10bit"]),
    "v1_3d0h_1080":   ("vmaf_v1.0.16_3d0h.json",      ["--vmaf-10bit"]),
    "v1_1d5h_2160":   ("vmaf_v1.0.16_1d5h_2160.json", ["--vmaf-10bit"]),
    "v1_1d5h_2160_8bit": ("vmaf_v1.0.16_1d5h_2160.json", []),
}

pvs_dir = Path(sys.argv[1]).resolve()
PARALLEL = int(sys.argv[2]) if len(sys.argv) > 2 else 12
VT = sys.argv[3] if len(sys.argv) > 3 else "2"


def src_for(pvs: Path) -> Path:
    p = SRC / f"{pvs.stem.split('__')[0]}.y4m"
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def valid(out: Path) -> bool:
    try:
        d = json.load(open(out))
        return "vmaf" in d and len(d["vmaf"]) > 0 and "global" in d
    except Exception:
        return False


def run(pvs: Path, cfg: str):
    model, extra = CONFIGS[cfg]
    out = RES / cfg / f"{pvs.stem}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if valid(out):
        return pvs, cfg, 0.0, "skip"
    tmpd = BASE / "tmp" / cfg / pvs.stem
    tmpd.mkdir(parents=True, exist_ok=True)
    cmd = [*HARNESS, str(pvs), str(src_for(pvs)), "-m", "vmaf",
           "--vmaf-model-path", model, *extra, "--vmaf-threads", VT,
           "--ffmpeg-path", str(FF), "--tmp-dir", str(tmpd), "-o", str(out)]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=HARNESS_DIR)
    shutil.rmtree(tmpd, ignore_errors=True)
    if p.returncode != 0 or not valid(out):
        return pvs, cfg, time.time() - t0, "ERR " + (p.stderr[-800:] or p.stdout[-300:])
    return pvs, cfg, time.time() - t0, "ok"


if __name__ == "__main__":
    pvss = sorted(pvs_dir.glob("*.mkv"))
    tasks = [(p, c) for p in pvss for c in CONFIGS]
    print(f"{len(pvss)} PVS x {len(CONFIGS)} configs = {len(tasks)} runs", flush=True)
    done = 0; errs = 0; t_start = time.time()
    with ThreadPoolExecutor(PARALLEL) as ex:
        futs = [ex.submit(run, p, c) for p, c in tasks]
        for f in as_completed(futs):
            pvs, cfg, dt, status = f.result()
            done += 1
            if status.startswith("ERR"):
                errs += 1
                print(f"[{done}/{len(tasks)}] {cfg} {pvs.name}: {status}", flush=True)
            elif done % 100 == 0:
                el = time.time() - t_start
                print(f"[{done}/{len(tasks)}] {el:.0f}s elapsed, eta {el/done*(len(tasks)-done):.0f}s", flush=True)
    print(f"VMAF_DONE errors={errs}", flush=True)
