# VMAF v0 vs v1 on a2_2k ladder

## VMAF v1.0.16 1.5H 2160 (new) vs VMAF 4K v0.6.1 (old)

- overall: n = 1936, Pearson r = 0.928, Spearman rho = 0.927, RMSE = 17.9
- res_label=1080p: n = 484, Pearson r = 0.931, Spearman rho = 0.934, RMSE = 11.4
- res_label=720p: n = 484, Pearson r = 0.927, Spearman rho = 0.919, RMSE = 15.0
- res_label=540p: n = 484, Pearson r = 0.913, Spearman rho = 0.897, RMSE = 19.1
- res_label=360p: n = 484, Pearson r = 0.878, Spearman rho = 0.871, RMSE = 23.7
- codec=h264: n = 528, Pearson r = 0.932, Spearman rho = 0.935, RMSE = 19.5
- codec=hevc: n = 528, Pearson r = 0.923, Spearman rho = 0.924, RMSE = 19.9
- codec=vp9: n = 440, Pearson r = 0.920, Spearman rho = 0.917, RMSE = 16.0
- codec=av1: n = 440, Pearson r = 0.908, Spearman rho = 0.907, RMSE = 14.9
- src_bitdepth=10-bit src: n = 792, Pearson r = 0.942, Spearman rho = 0.927, RMSE = 16.9
- src_bitdepth=8-bit src: n = 1144, Pearson r = 0.920, Spearman rho = 0.929, RMSE = 18.5

## VMAF v1.0.16 3.0H (new, 1080p) vs VMAF v0.6.1 (old, 1080p)

- overall: n = 1936, Pearson r = 0.974, Spearman rho = 0.979, RMSE = 6.1
- res_label=1080p: n = 484, Pearson r = 0.973, Spearman rho = 0.973, RMSE = 5.2
- res_label=720p: n = 484, Pearson r = 0.974, Spearman rho = 0.975, RMSE = 5.8
- res_label=540p: n = 484, Pearson r = 0.970, Spearman rho = 0.970, RMSE = 6.1
- res_label=360p: n = 484, Pearson r = 0.963, Spearman rho = 0.967, RMSE = 7.0
- codec=h264: n = 528, Pearson r = 0.975, Spearman rho = 0.985, RMSE = 7.0
- codec=hevc: n = 528, Pearson r = 0.975, Spearman rho = 0.982, RMSE = 6.4
- codec=vp9: n = 440, Pearson r = 0.969, Spearman rho = 0.973, RMSE = 5.6
- codec=av1: n = 440, Pearson r = 0.971, Spearman rho = 0.970, RMSE = 4.9
- src_bitdepth=10-bit src: n = 792, Pearson r = 0.972, Spearman rho = 0.971, RMSE = 6.2
- src_bitdepth=8-bit src: n = 1144, Pearson r = 0.977, Spearman rho = 0.985, RMSE = 6.0

## VMAF v1 3.0H 1080 vs VMAF v1 1.5H 2160

- overall: n = 1936, Pearson r = 0.999, Spearman rho = 1.000, RMSE = 2.4
- res_label=1080p: n = 484, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 1.6
- res_label=720p: n = 484, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 2.1
- res_label=540p: n = 484, Pearson r = 0.999, Spearman rho = 1.000, RMSE = 2.5
- res_label=360p: n = 484, Pearson r = 0.999, Spearman rho = 1.000, RMSE = 3.0
- codec=h264: n = 528, Pearson r = 0.999, Spearman rho = 1.000, RMSE = 2.6
- codec=hevc: n = 528, Pearson r = 0.999, Spearman rho = 1.000, RMSE = 2.6
- codec=vp9: n = 440, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 2.1
- codec=av1: n = 440, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 1.9
- src_bitdepth=10-bit src: n = 792, Pearson r = 0.999, Spearman rho = 1.000, RMSE = 2.4
- src_bitdepth=8-bit src: n = 1144, Pearson r = 0.999, Spearman rho = 1.000, RMSE = 2.4

## VMAF v1 1.5H 2160, --vmaf-10bit vs VMAF v1 1.5H 2160, native bit depth

- overall: n = 1936, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.3
- res_label=1080p: n = 484, Pearson r = 1.000, Spearman rho = 0.999, RMSE = 0.5
- res_label=720p: n = 484, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.1
- res_label=540p: n = 484, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.3
- res_label=360p: n = 484, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.4
- codec=h264: n = 528, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.4
- codec=hevc: n = 528, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.3
- codec=vp9: n = 440, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.3
- codec=av1: n = 440, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.4
- src_bitdepth=10-bit src: n = 792, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.0
- src_bitdepth=8-bit src: n = 1144, Pearson r = 1.000, Spearman rho = 1.000, RMSE = 0.4

## Per-frame agreement (within each PVS)

- median per-PVS Pearson r of frame scores, 4K pair: 0.871; 1080p pair: 0.876
- median within-PVS score range (max-min over frames): old 4K 11.5, new 4K 15.0

## Feature attribution (v1 1.5H 2160 features vs new-minus-old difference)

Spearman rho between per-PVS mean feature value and (new - old) score difference:

- cambi_cmxv_17_vlt_0.06: rho = -0.198
- speed_chroma_u: rho = -0.919
- speed_chroma_v: rho = -0.939
- speed_chroma_uv: rho = -0.938
- integer_adm2: rho = 0.840
- integer_aim: rho = -0.843
- integer_adm3: rho = 0.850
- integer_adm_scale0: rho = 0.497
- integer_adm_scale1: rho = 0.723
- integer_adm_scale2: rho = 0.832
- integer_adm_scale3: rho = 0.843
- VMAF_integer_feature_motion_sad_score: rho = -0.220
- integer_motion2: rho = -0.220
- integer_motion3: rho = -0.220

## Per-source mean difference (new 4K minus old 4K)

                                                 n  mean_old  mean_new  mean_diff  min_diff  max_diff
src                                                                                                  
MountainBike_1920x1080_30fps_8bit               88      91.8      65.4      -26.5     -65.1       0.0
Riverbed_1920x1080p25                           88      77.0      53.8      -23.2     -47.8       0.0
TunnelFlag_1920x1080_5994_10bit_420             88      95.2      75.1      -20.1     -59.1       0.1
TreesAndGrass_1920_1080_30fps_8bit              88      88.8      69.4      -19.4     -55.9       0.0
ToddlerFountain_1920x1080_2997fps_10bit_420     88      73.9      55.1      -18.7     -42.5       0.0
Motorcycle_1920x1080_30fps_8bit                 88      81.1      62.9      -18.3     -47.9       0.0
DinnerSceneCropped_1920x1080_2997fps_10bit_420  88      78.3      60.8      -17.5     -34.8      -3.2
WalkingInStreet_1920x1080_30fps                 88      83.7      70.4      -13.3     -44.5       0.0
PedestrianArea_1920x1080p25                     88      77.4      64.6      -12.8     -38.3      -0.2
Skater227_1920x1080_30fps                       88      78.4      67.0      -11.3     -27.5      -0.3
RitualDance_1920x1080_5994_10bit_420            88      72.3      61.2      -11.1     -31.8      -0.2
Aerial3200_1920x1080_5994_10bit_420             88      74.7      63.8      -10.9     -37.2      -0.0
OldTownCross_1920x1080p50                       88      73.3      62.9      -10.4     -33.8      -1.1
Vertical_Carnaby_1080x1920_5994                 88      74.8      64.6      -10.2     -28.6      -2.8
RushFieldCuts_1920x1080_2997                    88      73.8      63.7      -10.2     -38.6       0.3
CrowdRun_1920x1080p50                           88      69.1      58.8      -10.2     -36.0       0.5
MeridianTalk_sdr_1920x1080p_5994_10bit          88      78.4      68.7       -9.8     -27.7      -2.3
FoodMarket_1920x1080_5994_10bit_420             88      77.8      68.0       -9.8     -39.4      -0.1
WorldCup_1920x1080_30p                          88      77.8      70.7       -7.0     -30.0      -0.6
WorldCup_far_1920x1080_30p                      88      80.5      75.3       -5.3     -33.2       0.5
Boat_1920x1080_5994_10bit_420                   88      73.8      69.2       -4.5     -29.9       1.5
Vertical_bees_1080x1920_2997                    88      79.3      77.2       -2.1     -22.0       0.8
