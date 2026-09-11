#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Generate a bitrate-ladder style set of PVSs from the a2_2k sources.

For each source: 4 resolutions x {x264, x265, vp9, svt-av1} x CRF ladder.
Native bit depth is preserved (8-bit sources -> yuv420p, 10-bit -> yuv420p10le).
"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src"
OUT = BASE / "pvs"
OUT.mkdir(exist_ok=True)
FFMPEG = "ffmpeg"  # system ffmpeg 7.1 (encoders)
THREADS_PER_JOB = 4
PARALLEL = 8

CRF = {
    "h264": [18, 23, 28, 33, 38, 43],
    "hevc": [18, 23, 28, 33, 38, 43],
    "vp9": [20, 30, 40, 50, 60],
    "av1": [20, 30, 40, 50, 60],
}
HEIGHTS = [1080, 720, 540, 360]  # short side


def probe(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,pix_fmt,r_frame_rate",
        "-of", "json", str(path)])
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"], s["pix_fmt"], s["r_frame_rate"]


def enc_args(codec, crf, pix_fmt, t):
    ten = pix_fmt == "yuv420p10le"
    if codec == "h264":
        return ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-threads", str(t)]
    if codec == "hevc":
        return ["-c:v", "libx265", "-preset", "fast", "-crf", str(crf),
                "-x265-params", f"log-level=error:pools={t}"]
    if codec == "vp9":
        a = ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", str(crf), "-deadline", "good",
             "-cpu-used", "4", "-row-mt", "1", "-threads", str(t)]
        if ten:
            a += ["-profile:v", "2"]
        return a
    if codec == "av1":
        return ["-c:v", "libsvtav1", "-preset", "8", "-crf", str(crf),
                "-svtav1-params", f"lp={t}"]
    raise ValueError(codec)


def jobs():
    for src in sorted(SRC.glob("*.y4m")):
        w, h, pix, fr = probe(src)
        portrait = h > w
        for short in HEIGHTS:
            if portrait:
                ow, oh = short, int(round(short * 16 / 9))
            else:
                ow, oh = int(round(short * 16 / 9)), short
            ow += ow % 2; oh += oh % 2
            for codec, crfs in CRF.items():
                for crf in crfs:
                    name = f"{src.stem}__{ow}x{oh}__{codec}__crf{crf}.mkv"
                    yield dict(src=src, out=OUT / name, w=ow, h=oh, codec=codec,
                               crf=crf, pix=pix, src_w=w, src_h=h)


def run(j):
    out = j["out"]
    if out.exists() and out.stat().st_size > 0:
        return j, 0.0, "skip"
    vf = f"scale={j['w']}:{j['h']}:flags=bicubic" if (j["w"], j["h"]) != (j["src_w"], j["src_h"]) else "null"
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", str(j["src"]),
           "-vf", vf, "-pix_fmt", j["pix"], *enc_args(j["codec"], j["crf"], j["pix"], THREADS_PER_JOB),
           "-an", str(out) + ".tmp.mkv"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return j, time.time() - t0, "ERR " + p.stderr[-500:]
    os.rename(str(out) + ".tmp.mkv", out)
    return j, time.time() - t0, "ok"


if __name__ == "__main__":
    all_jobs = list(jobs())
    print(f"{len(all_jobs)} encodes", flush=True)
    done = 0
    with ThreadPoolExecutor(PARALLEL) as ex:
        futs = [ex.submit(run, j) for j in all_jobs]
        for f in as_completed(futs):
            j, dt, status = f.result()
            done += 1
            if status != "ok" and status != "skip":
                print(f"[{done}/{len(all_jobs)}] {j['out'].name}: {status}", flush=True)
            elif done % 50 == 0:
                print(f"[{done}/{len(all_jobs)}] {j['out'].name} {dt:.1f}s", flush=True)
    print("ENCODE_DONE", flush=True)
