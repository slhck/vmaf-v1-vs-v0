#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy",
#   "pandas",
#   "plotnine",
#   "pyarrow",
#   "scipy",
# ]
# ///

"""Analysis + plots comparing VMAF v0.6.1 and VMAF v1.0.16 on the a2_2k ladder."""
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
from plotnine import *

AN = Path(__file__).resolve().parent.parent / "analysis"
PL = AN / "plots"; PL.mkdir(exist_ok=True)
ov = pd.read_parquet(AN / "overall.parquet")
fr = pd.read_parquet(AN / "frames.parquet")

ov["short_side"] = ov.apply(lambda r: min(r.pvs_w, r.pvs_h), axis=1)
ov["res_label"] = ov.short_side.astype(str) + "p"
res_order = [f"{h}p" for h in sorted(ov.short_side.unique(), reverse=True)]
ov["res_label"] = pd.Categorical(ov.res_label, res_order)
ov["codec"] = pd.Categorical(ov.codec, ["h264", "hevc", "vp9", "av1"])
ov["src_bitdepth"] = ov.src.str.contains("10bit|Skater|ToddlerFountain|DinnerScene", regex=True).map({True: "10-bit src", False: "8-bit src"})

# ---- wide table: one row per pvs, one column per config
wide = ov.pivot_table(index=["pvs", "src", "codec", "res_label", "short_side", "crf", "pvs_set", "bitrate_kbps", "src_bitdepth", "fps"],
                      columns="config", values="vmaf_mean").reset_index()
wide.to_csv(AN / "overall_wide.csv", index=False)

SZ = dict(width=10, height=7.5, dpi=200)
PAIRS = [("v0_4k", "v1_1d5h_2160", "VMAF 4K v0.6.1 (old)", "VMAF v1.0.16 1.5H 2160 (new)"),
         ("v0_1080", "v1_3d0h_1080", "VMAF v0.6.1 (old, 1080p)", "VMAF v1.0.16 3.0H (new, 1080p)"),
         ("v1_1d5h_2160", "v1_3d0h_1080", "VMAF v1 1.5H 2160", "VMAF v1 3.0H 1080"),
         ("v1_1d5h_2160_8bit", "v1_1d5h_2160", "VMAF v1 1.5H 2160, native bit depth", "VMAF v1 1.5H 2160, --vmaf-10bit")]

def corr_txt(x, y):
    m = x.notna() & y.notna(); x, y = x[m], y[m]
    if m.sum() < 3: return f"n = {m.sum()}"
    r = stats.pearsonr(x, y)[0]; s = stats.spearmanr(x, y)[0]
    return f"n = {m.sum()}, Pearson r = {r:.3f}, Spearman rho = {s:.3f}, RMSE = {np.sqrt(np.mean((x-y)**2)):.1f}"

lines = ["# VMAF v0 vs v1 on a2_2k ladder", ""]
for a, b, la, lb in PAIRS:
    lines.append(f"## {lb} vs {la}\n")
    lines.append("- overall: " + corr_txt(wide[a], wide[b]))
    for key in ["res_label", "codec", "src_bitdepth"]:
        for g, d in wide.groupby(key, observed=True):
            lines.append(f"- {key}={g}: " + corr_txt(d[a], d[b]))
    lines.append("")
    base = (ggplot(wide, aes(a, b)) + geom_abline(slope=1, intercept=0, linetype="dashed", color="#d62728")
            + coord_equal(xlim=(0, 100), ylim=(0, 100)) + theme_bw() + labs(x=la, y=lb))
    (base + geom_point(aes(color="res_label"), alpha=0.5, size=1.5) + scale_color_brewer(type="qual", palette="Set1")
     + labs(color="PVS resolution", title=f"Overall (mean) score per PVS, colored by encoding resolution", subtitle=corr_txt(wide[a], wide[b]))
     ).save(PL / f"scatter_{b}_vs_{a}_by_res.png", **SZ, verbose=False)
    (base + geom_point(aes(color="codec"), alpha=0.5, size=1.5) + scale_color_brewer(type="qual", palette="Dark2")
     + labs(color="Codec", title=f"Overall (mean) score per PVS, colored by codec", subtitle=corr_txt(wide[a], wide[b]))
     ).save(PL / f"scatter_{b}_vs_{a}_by_codec.png", **SZ, verbose=False)
    (base + geom_point(aes(color="codec"), alpha=0.5, size=1) + facet_wrap("res_label") + scale_color_brewer(type="qual", palette="Dark2")
     + labs(color="Codec", title="Overall score per PVS, faceted by encoding resolution")
     ).save(PL / f"scatter_{b}_vs_{a}_facet_res.png", **SZ, verbose=False)
    (base + geom_point(aes(color="res_label"), alpha=0.5, size=1) + facet_wrap("codec") + scale_color_brewer(type="qual", palette="Set1")
     + labs(color="PVS resolution", title="Overall score per PVS, faceted by codec")
     ).save(PL / f"scatter_{b}_vs_{a}_facet_codec.png", **SZ, verbose=False)
    (base + geom_point(alpha=0.35, size=1.2, color="#1f77b4")
     + labs(title="Overall (mean) score per PVS, all data", subtitle=corr_txt(wide[a], wide[b]))
     ).save(PL / f"scatter_{b}_vs_{a}_all.png", **SZ, verbose=False)
    (base + geom_point(aes(color="res_label"), alpha=0.5, size=1) + facet_wrap("src", ncol=6) + scale_color_brewer(type="qual", palette="Set1")
     + labs(color="PVS resolution", title="Overall score per PVS, faceted by source") + theme(strip_text=element_text(size=6), figure_size=(14, 10))
     ).save(PL / f"scatter_{b}_vs_{a}_facet_src.png", dpi=200, verbose=False)

# ---- difference new - old vs old, by resolution and codec
wide["diff_4k"] = wide["v1_1d5h_2160"] - wide["v0_4k"]
wide["diff_1080"] = wide["v1_3d0h_1080"] - wide["v0_1080"]
(ggplot(wide, aes("res_label", "diff_4k", fill="codec")) + geom_boxplot(outlier_size=0.5) + geom_hline(yintercept=0, linetype="dashed")
 + theme_bw() + scale_fill_brewer(type="qual", palette="Dark2")
 + labs(x="PVS encoding resolution (upscaled to 1080p before VMAF)", y="VMAF v1 1.5H 2160  minus  VMAF 4K v0.6.1", fill="Codec",
        title="Score difference new minus old, per resolution and codec")).save(PL / "diff_4k_box_res_codec.png", **SZ, verbose=False)
(ggplot(wide, aes("res_label", "diff_1080", fill="codec")) + geom_boxplot(outlier_size=0.5) + geom_hline(yintercept=0, linetype="dashed")
 + theme_bw() + scale_fill_brewer(type="qual", palette="Dark2")
 + labs(x="PVS encoding resolution (upscaled to 1080p before VMAF)", y="VMAF v1 3.0H  minus  VMAF v0.6.1", fill="Codec",
        title="Score difference new minus old (1080p models), per resolution and codec")).save(PL / "diff_1080_box_res_codec.png", **SZ, verbose=False)

# ---- rate-quality curves: rows = source, columns = model, fixed axes
lad = ov[ov.pvs_set == "ladder"].copy()
MODEL_LABELS = {"v0_4k": "old: 4K v0.6.1", "v1_1d5h_2160": "new: v1 1.5H 2160", "v0_1080": "old: v0.6.1 (1080p)", "v1_3d0h_1080": "new: v1 3.0H (1080p)"}
lad["model"] = pd.Categorical(lad.config.map(MODEL_LABELS), list(MODEL_LABELS.values()))
lad = lad[lad.model.notna()]
BR_BREAKS = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
def br_label(vals):
    return [f"{v/1000:g} Mbps" if v >= 1000 else f"{v:g} kbps" for v in vals]
srcs = sorted(lad.src.unique())
chunks = [srcs[i:i + 8] for i in range(0, len(srcs), 8)]
for codec in ["h264", "hevc", "vp9", "av1"]:
    for ci, chunk in enumerate(chunks, 1):
        d = lad[(lad.codec == codec) & lad.src.isin(chunk)].copy()
        if d.empty: continue
        d["src"] = d.src.str.replace(r"_\d{3,4}x\d{3,4}.*$", "", regex=True).str.replace(r"_1920_1080.*$", "", regex=True)
        d["generation"] = pd.Categorical(d.model.astype(str).str.startswith("new").map({True: "new", False: "old"}), ["new", "old"])
        (ggplot(d, aes("bitrate_kbps", "vmaf_mean", color="res_label", linetype="generation"))
         + geom_line() + geom_point(size=1.2)
         + scale_linetype_manual(values={"new": "solid", "old": "dashed"}, guide=None)
         + scale_x_log10(breaks=BR_BREAKS, labels=br_label, limits=(lad.bitrate_kbps.min() * 0.9, lad.bitrate_kbps.max() * 1.1))
         + scale_y_continuous(breaks=range(0, 101, 20), limits=(0, 100))
         + facet_grid("src", "model") + theme_bw() + scale_color_brewer(type="qual", palette="Set1")
         + labs(x="Bitrate", y="Mean VMAF", color="PVS resolution", title=f"Rate-quality curves, {codec} (part {ci}/{len(chunks)}): each column is one VMAF model")
         + theme(strip_text_y=element_text(size=7, angle=-90), strip_text_x=element_text(size=9),
                 axis_text_x=element_text(angle=45, hjust=1, size=7), figure_size=(14, 2.4 * len(chunk) + 1), legend_position="bottom")
         ).save(PL / f"rq_{codec}_part{ci}.png", dpi=150, verbose=False)

# ---- per-frame agreement
fr_w = fr.pivot_table(index=["pvs", "src", "codec", "res", "n"], columns="config", values="vmaf").reset_index()
fr_w.to_parquet(AN / "frames_wide.parquet", index=False)
pf = fr_w.groupby("pvs").apply(lambda d: pd.Series({
    "r_frames_4k": d[["v0_4k", "v1_1d5h_2160"]].dropna().corr().iloc[0, 1] if len(d.dropna(subset=["v0_4k", "v1_1d5h_2160"])) > 2 else np.nan,
    "r_frames_1080": d[["v0_1080", "v1_3d0h_1080"]].dropna().corr().iloc[0, 1] if len(d.dropna(subset=["v0_1080", "v1_3d0h_1080"])) > 2 else np.nan,
    "mean_v0_4k": d["v0_4k"].mean(), "mean_v1_4k": d["v1_1d5h_2160"].mean(),
    "range_v0_4k": d["v0_4k"].max() - d["v0_4k"].min(), "range_v1_4k": d["v1_1d5h_2160"].max() - d["v1_1d5h_2160"].min(),
}), include_groups=False).reset_index().merge(wide[["pvs", "res_label", "codec", "crf", "src"]], on="pvs")
pf.to_csv(AN / "per_frame_agreement.csv", index=False)
lines.append("## Per-frame agreement (within each PVS)\n")
lines.append(f"- median per-PVS Pearson r of frame scores, 4K pair: {pf.r_frames_4k.median():.3f}; 1080p pair: {pf.r_frames_1080.median():.3f}")
lines.append(f"- median within-PVS score range (max-min over frames): old 4K {pf.range_v0_4k.median():.1f}, new 4K {pf.range_v1_4k.median():.1f}\n")
(ggplot(pf, aes("r_frames_4k", fill="res_label")) + geom_histogram(bins=40) + theme_bw() + scale_fill_brewer(type="qual", palette="Set1")
 + labs(x="Pearson r between per-frame scores (old 4K vs new 4K), one value per PVS", y="PVS count", fill="PVS resolution",
        title="Per-frame agreement between old and new model within each PVS")).save(PL / "perframe_corr_hist.png", **SZ, verbose=False)

# per-frame example traces: pick a few PVSs across the quality range
ex = wide.sort_values("v0_4k")
picks = pd.concat([ex.iloc[[int(q * (len(ex) - 1))]] for q in (0.05, 0.3, 0.5, 0.7, 0.9, 0.99)]).pvs.tolist()
frx = fr[fr.pvs.isin(picks) & fr.config.isin(["v0_4k", "v1_1d5h_2160"])].copy()
frx["model"] = frx.config.map({"v0_4k": "old: 4K v0.6.1", "v1_1d5h_2160": "new: v1 1.5H 2160"})
(ggplot(frx, aes("n", "vmaf", color="model")) + geom_line() + facet_wrap("pvs", ncol=2, scales="free_x") + theme_bw()
 + labs(x="Frame", y="VMAF", color="Model", title="Per-frame scores, example PVSs across the quality range")
 + theme(strip_text=element_text(size=7), figure_size=(12, 9))).save(PL / "perframe_examples.png", dpi=150, verbose=False)

# ---- old-score histogram: where does the old model saturate?
(ggplot(wide.melt(id_vars=["pvs", "res_label"], value_vars=["v0_4k", "v1_1d5h_2160"], var_name="model", value_name="vmaf"), aes("vmaf", fill="model"))
 + geom_histogram(bins=50, alpha=0.6, position="identity") + theme_bw() + facet_wrap("res_label")
 + labs(x="Mean VMAF", y="PVS count", title="Distribution of overall scores per model and resolution")).save(PL / "score_hist.png", **SZ, verbose=False)

(AN / "summary.md").write_text("\n".join(lines))
print("\n".join(lines))

# ---- feature attribution: which v1 features explain the new-minus-old difference?
v1 = ov[ov.config == "v1_1d5h_2160"].copy()
featcols = [c for c in v1.columns if c.endswith("__average") and v1[c].notna().any()]
short = {c: c.replace("__average", "").split("_csf_")[0].split("_mxv_")[0].split("_mmxv_")[0].replace("cambi_hrs_1080", "cambi") for c in featcols}
v1 = v1.rename(columns=short)
feat = list(short.values())
v1 = v1.merge(wide[["pvs", "diff_4k", "v0_4k", "v1_1d5h_2160"]], on="pvs")
v1.to_csv(AN / "v1_features_per_pvs.csv", index=False)
lines.append("## Feature attribution (v1 1.5H 2160 features vs new-minus-old difference)\n")
lines.append("Spearman rho between per-PVS mean feature value and (new - old) score difference:\n")
for f in feat:
    if v1[f].std() == 0: continue
    rho = v1[[f, "diff_4k"]].dropna().corr(method="spearman").iloc[0, 1]
    lines.append(f"- {f}: rho = {rho:.3f}")
lines.append("")
long = v1.melt(id_vars=["pvs", "diff_4k", "res_label", "codec"], value_vars=[f for f in feat if f.startswith(("cambi", "speed_chroma_uv", "integer_adm2", "integer_motion2", "integer_aim"))],
               var_name="feature", value_name="value")
(ggplot(long, aes("value", "diff_4k", color="res_label")) + geom_point(alpha=0.4, size=1) + facet_wrap("feature", scales="free_x") + theme_bw()
 + geom_hline(yintercept=0, linetype="dashed") + scale_color_brewer(type="qual", palette="Set1")
 + labs(x="Mean feature value (v1 1.5H 2160 model)", y="VMAF v1 1.5H 2160 minus VMAF 4K v0.6.1", color="PVS resolution",
        title="Score difference vs v1 feature values")).save(PL / "feature_attribution.png", **SZ, verbose=False)

# per-source mean difference table
src_tab = wide.groupby("src", observed=True).agg(n=("pvs", "size"), mean_old=("v0_4k", "mean"), mean_new=("v1_1d5h_2160", "mean"),
                                                 mean_diff=("diff_4k", "mean"), min_diff=("diff_4k", "min"), max_diff=("diff_4k", "max")).round(1).sort_values("mean_diff")
src_tab.to_csv(AN / "per_source_diff.csv")
lines.append("## Per-source mean difference (new 4K minus old 4K)\n")
lines.append(src_tab.to_string()); lines.append("")
(AN / "summary.md").write_text("\n".join(lines))
print("\n".join(lines[-40:]))
