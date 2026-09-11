#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "pyarrow",
# ]
# ///

"""Collect all harness JSON outputs into two tables:
  analysis/overall.parquet/.csv  - one row per (config, pvs): mean/median/min/max VMAF + all global feature stats + bitrate
  analysis/frames.parquet         - one row per (config, pvs, frame): vmaf + every feature (long-ish, wide columns)
"""
import json, re, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RES = BASE / "results"
AN = BASE / "analysis"; AN.mkdir(exist_ok=True)


def parse_name(stem):
    src, res, codec, crf = stem.split("__")
    return dict(src=src, res=res, codec=codec, crf=int(crf[3:]), pvs_set="ladder")


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,pix_fmt,r_frame_rate:format=bit_rate,duration,size",
        "-of", "json", str(path)])
    j = json.loads(out); s = j["streams"][0]; f = j["format"]
    num, den = map(int, s["r_frame_rate"].split("/"))
    return dict(pvs_w=s["width"], pvs_h=s["height"], pvs_pix_fmt=s["pix_fmt"], fps=num/den,
                bitrate_kbps=int(f["bit_rate"])/1000, duration=float(f["duration"]), size_bytes=int(f["size"]))


def load(p: Path):
    cfg = p.parent.name
    d = json.load(open(p))
    meta = dict(config=cfg, pvs=p.stem, **parse_name(p.stem))
    g = d["global"]["vmaf"]
    overall = dict(meta, n_frames=len(d["vmaf"]),
                   vmaf_mean=g["vmaf"]["average"], vmaf_median=g["vmaf"]["median"],
                   vmaf_min=g["vmaf"]["min"], vmaf_max=g["vmaf"]["max"], vmaf_stdev=g["vmaf"]["stdev"])
    for feat, st in g.items():
        if feat == "vmaf": continue
        for k, v in st.items():
            overall[f"{feat}__{k}"] = v
    frames = pd.DataFrame(d["vmaf"])
    for k, v in meta.items():
        frames[k] = v
    return overall, frames


files = sorted(f for f in RES.glob("*/*.json") if "__" in f.stem)  # ladder encodes only
print(f"{len(files)} result files")
with ThreadPoolExecutor(16) as ex:
    out = list(ex.map(load, files))
overall = pd.DataFrame([o for o, _ in out])
frames = pd.concat([f for _, f in out], ignore_index=True)

# bitrate/probe info per PVS
pvs_paths = {}
for stem in overall.pvs.unique():
    if (BASE / "pvs" / f"{stem}.mkv").exists():
        pvs_paths[stem] = BASE / "pvs" / f"{stem}.mkv"
with ThreadPoolExecutor(16) as ex:
    info = dict(zip(pvs_paths, ex.map(probe, pvs_paths.values())))
info = pd.DataFrame.from_dict(info, orient="index").rename_axis("pvs").reset_index()
overall = overall.merge(info, on="pvs", how="left")

overall.to_parquet(AN / "overall.parquet", index=False)
overall.to_csv(AN / "overall.csv", index=False)
frames.to_parquet(AN / "frames.parquet", index=False)
print(overall.groupby("config").size())
print(f"frames table: {frames.shape}")
