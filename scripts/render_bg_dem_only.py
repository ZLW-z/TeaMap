# -*- coding: utf-8 -*-
"""快速重渲染全球 DEM 背景 (仅 bg_dem.png, 修复海洋分类)"""
import os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = 900_000_000
import rasterio
from rasterio.warp import reproject, Resampling
from pyproj import CRS, Transformer

GLOBAL_TIF = r'D:\Desktop\2026年DEM地形数据\1.拼接成全球一张图的数据\global.tif'
OUT_DIR = r'd:\Desktop\teamap\public\data\1'
OUT_BG = os.path.join(OUT_DIR, 'bg_dem.png')

EPSG4326 = CRS.from_epsg(4326)
ALBERS_PROJ4 = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
ALBERS_CRS = CRS.from_string(ALBERS_PROJ4)
ll_to_albers = Transformer.from_crs(EPSG4326, ALBERS_CRS, always_xy=True)

# Canvas parameters (same as process_ch1_global.py)
LON_MIN_GEO, LON_MAX_GEO = -40.0, 180.0
LAT_MIN_GEO, LAT_MAX_GEO = -20.0, 75.0

sample_step = 2.0
xs, ys = [], []
for lon in np.arange(LON_MIN_GEO, LON_MAX_GEO + sample_step, sample_step):
    x, y = ll_to_albers.transform(lon, LAT_MAX_GEO); xs.append(x); ys.append(y)
    x, y = ll_to_albers.transform(lon, LAT_MIN_GEO); xs.append(x); ys.append(y)
for lat in np.arange(LAT_MIN_GEO, LAT_MAX_GEO + sample_step, sample_step):
    x, y = ll_to_albers.transform(LON_MIN_GEO, lat); xs.append(x); ys.append(y)
    x, y = ll_to_albers.transform(LON_MAX_GEO, lat); xs.append(x); ys.append(y)

ALB_X_MIN, ALB_X_MAX = min(xs), max(xs)
ALB_Y_MIN, ALB_Y_MAX = min(ys), max(ys)

CANVAS_W_M = ALB_X_MAX - ALB_X_MIN
CANVAS_H_M = ALB_Y_MAX - ALB_Y_MIN

TARGET_W = 6144
PX_SIZE = CANVAS_W_M / TARGET_W
TARGET_H = int(round(CANVAS_H_M / PX_SIZE))
W, H = TARGET_W, TARGET_H

dst_transform = rasterio.transform.from_origin(ALB_X_MIN, ALB_Y_MAX, PX_SIZE, PX_SIZE)

print(f'Canvas: {W}x{H}, PX_SIZE={PX_SIZE:.0f}m')

# 1. Reproject global DEM
print('\n[1/4] Reprojecting global DEM (EPSG:4326 -> Albers)...')
with rasterio.open(GLOBAL_TIF) as src:
    src_nodata = src.nodata
    bg_arr = np.full((H, W), -32767, dtype=np.float32)
    reproject(
        source=rasterio.band(src, 1),
        destination=bg_arr,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=dst_transform,
        dst_crs=ALBERS_CRS,
        src_nodata=src_nodata,
        dst_nodata=-32767,
        resampling=Resampling.bilinear,
        num_threads=4
    )

print(f'  bg_dem shape={bg_arr.shape}, range=[{np.nanmin(bg_arr):.0f}, {np.nanmax(bg_arr):.0f}]')

# 2. Fill NODATA with sea level (0m)
print('\n[2/4] Filling NODATA with sea level (0m)...')
NODATA_FILL = -32767
nodata_mask = bg_arr <= NODATA_FILL
nodata_count = nodata_mask.sum()
print(f'  Found {nodata_count} NODATA pixels')
if nodata_count > 0:
    bg_arr[nodata_mask] = 0.0

# 3. Classify ocean vs land
NODATA = -32767
bg_land = bg_arr > 0
bg_ocean = (bg_arr <= 0) & (bg_arr > NODATA)
bg_valid = bg_arr > NODATA

print(f'\n[3/4] Classification:')
print(f'  Land pixels: {bg_land.sum()}')
print(f'  Ocean pixels: {bg_ocean.sum()}')
print(f'  Valid pixels: {bg_valid.sum()}')

# 4. Compute hillshade
print('\n[4/4] Computing hillshade and rendering...')
PX_X_M = PX_SIZE
PX_Y_M = PX_SIZE

def compute_hillshade(dem_in, valid_mask_in, px_x_m, px_y_m,
                      azimuth_deg=320.0, altitude_deg=40.0, z_factor=1.0):
    dem = dem_in.copy()
    vmean = float(np.mean(dem_in[valid_mask_in])) if valid_mask_in.any() else 500.0
    dem[~valid_mask_in] = vmean * 0.15
    dem[valid_mask_in] = dem[valid_mask_in] * z_factor
    dy, dx = np.gradient(dem, px_y_m, px_x_m)
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)
    azim_r = np.deg2rad(360.0 - azimuth_deg + 90.0)
    alt_r = np.deg2rad(altitude_deg)
    hs = (np.sin(alt_r) * np.sin(slope) * np.cos(aspect - azim_r) +
          np.cos(alt_r) * np.cos(slope))
    return np.clip(hs, 0, 1)

def multi_layer_hillshade(dem_in, valid_mask_in, px_x_m, px_y_m,
                          main_azim=320, main_alt=40,
                          z_factor_main=1.0, z_factor_detail=2.5):
    hs_main = compute_hillshade(dem_in, valid_mask_in, px_x_m, px_y_m,
                                azimuth_deg=main_azim, altitude_deg=main_alt,
                                z_factor=z_factor_main)
    hs_low = compute_hillshade(dem_in, valid_mask_in, px_x_m, px_y_m,
                               azimuth_deg=main_azim + 15, altitude_deg=22,
                               z_factor=z_factor_main * 1.5)
    hs_anti = compute_hillshade(dem_in, valid_mask_in, px_x_m, px_y_m,
                                azimuth_deg=(main_azim + 180) % 360, altitude_deg=55,
                                z_factor=z_factor_main * 0.7)
    hs_detail = compute_hillshade(dem_in, valid_mask_in, px_x_m, px_y_m,
                                  azimuth_deg=main_azim, altitude_deg=main_alt,
                                  z_factor=z_factor_detail)
    shadow_map = (1.0 - hs_low) * 0.65 + (1.0 - hs_main) * 0.25 + (1.0 - hs_detail) * 0.10
    shadow_map = np.power(np.clip(shadow_map, 0, 1), 1.3)
    highlight_map = hs_main * 0.55 + hs_detail * 0.35 + hs_anti * 0.10
    highlight_map = np.power(np.clip(highlight_map, 0, 1), 0.75)
    intensity = 0.55 - shadow_map * 0.52 + highlight_map * 0.50
    intensity = np.clip(intensity, 0.25, 1.25)
    fill = hs_anti * 0.12
    intensity = np.clip(intensity + fill, 0.25, 1.30)
    return intensity, shadow_map, highlight_map

bg_intensity, bg_shadow, bg_highlight = multi_layer_hillshade(
    bg_arr, bg_valid, PX_X_M, PX_Y_M,
    main_azim=320, main_alt=38,
    z_factor_main=1.3, z_factor_detail=2.5
)

# Render colors
t = np.clip(bg_arr / 7000.0, 0, 1)
bgc = np.zeros((H, W, 3), dtype=np.float64)

# Land: elevation-based coloring
s1 = bg_land & (t < 0.07)
k1 = np.clip(t[s1] / 0.07, 0, 1)
bgc[s1, 0] = 220 + (234 - 220) * k1
bgc[s1, 1] = 228 + (232 - 228) * k1
bgc[s1, 2] = 224 + (225 - 224) * k1

s2 = bg_land & (t >= 0.07) & (t < 0.22)
k2 = np.clip((t[s2] - 0.07) / 0.15, 0, 1)
bgc[s2, 0] = 234 + (228 - 234) * k2
bgc[s2, 1] = 232 + (222 - 232) * k2
bgc[s2, 2] = 225 + (205 - 225) * k2

s3 = bg_land & (t >= 0.22) & (t < 0.5)
k3 = np.clip((t[s3] - 0.22) / 0.28, 0, 1)
bgc[s3, 0] = 228 + (226 - 228) * k3
bgc[s3, 1] = 222 + (221 - 222) * k3
bgc[s3, 2] = 205 + (211 - 205) * k3

s4 = bg_land & (t >= 0.5)
k4 = np.clip((t[s4] - 0.5) / 0.5, 0, 1)
bgc[s4, 0] = 226 + (242 - 226) * k4
bgc[s4, 1] = 221 + (239 - 221) * k4
bgc[s4, 2] = 211 + (233 - 211) * k4

# Ocean: depth-based coloring (MULTI-LEVEL BLUE)
# 0 ~ -200m: shallow sea (light blue)
ocean_shallow = bg_ocean & (bg_arr >= -200)
if ocean_shallow.any():
    ot = np.clip((-bg_arr[ocean_shallow]) / 200.0, 0, 1)
    bgc[ocean_shallow, 0] = 214 + (198 - 214) * ot
    bgc[ocean_shallow, 1] = 224 + (218 - 224) * ot
    bgc[ocean_shallow, 2] = 228 + (222 - 228) * ot

# -200 ~ -1500m: mid sea (medium blue)
ocean_mid = bg_ocean & (bg_arr < -200) & (bg_arr >= -1500)
if ocean_mid.any():
    ot = np.clip((-bg_arr[ocean_mid] - 200) / 1300.0, 0, 1)
    bgc[ocean_mid, 0] = 198 + (174 - 198) * ot
    bgc[ocean_mid, 1] = 218 + (206 - 218) * ot
    bgc[ocean_mid, 2] = 222 + (218 - 222) * ot

# -1500 ~ -4000m: deep sea (dark blue)
ocean_deep = bg_ocean & (bg_arr < -1500) & (bg_arr >= -4000)
if ocean_deep.any():
    ot = np.clip((-bg_arr[ocean_deep] - 1500) / 2500.0, 0, 1)
    bgc[ocean_deep, 0] = 174 + (138 - 174) * ot
    bgc[ocean_deep, 1] = 206 + (174 - 206) * ot
    bgc[ocean_deep, 2] = 218 + (198 - 218) * ot

# -4000m+: abyss (deepest blue)
ocean_abyss = bg_ocean & (bg_arr < -4000)
if ocean_abyss.any():
    ot = np.clip(np.minimum((-bg_arr[ocean_abyss] - 4000) / 3000.0, 1.0), 0, 1)
    bgc[ocean_abyss, 0] = 138 + (108 - 138) * ot
    bgc[ocean_abyss, 1] = 174 + (144 - 174) * ot
    bgc[ocean_abyss, 2] = 198 + (176 - 198) * ot

# NODATA: paper color
bgc[~bg_valid] = [244, 240, 231]

# Apply lighting
intensity_b_3c = np.stack([bg_intensity] * 3, axis=-1)
bg_final = bgc * intensity_b_3c

# Shadow (cool blue tint)
shadow_rgb = np.zeros((H, W, 3), dtype=np.float64)
shadow_rgb[:, :, 0] = 30
shadow_rgb[:, :, 1] = 40
shadow_rgb[:, :, 2] = 55
sh_3c = np.stack([bg_shadow] * 3, axis=-1)
bg_final = bg_final * (1 - sh_3c * 0.55) + shadow_rgb * sh_3c * 0.55

# Highlight (warm tint)
hl_rgb = np.zeros((H, W, 3), dtype=np.float64)
hl_rgb[:, :, 0] = 255
hl_rgb[:, :, 1] = 248
hl_rgb[:, :, 2] = 228
hl_3c = np.stack([bg_highlight] * 3, axis=-1)
bg_final = bg_final * (1 - hl_3c * 0.18) + hl_rgb * hl_3c * 0.25

bg_final_uint8 = np.clip(bg_final, 0, 255).astype(np.uint8)
bg_rgba = np.dstack([bg_final_uint8, np.full((H, W), 255, dtype=np.uint8)])

# Verify colors in South China Sea area
print('\n[VERIFY] Color check in key areas:')
areas = [
    ('十段线南端', 2982, 3733),
    ('南海中部', 3023, 3800),
    ('赤道附近', 3073, 3900),
]
for name, row, col in areas:
    if 0 <= row < H and 0 <= col < W:
        pixel = bg_final_uint8[row, col, :3]
        is_ocean = pixel[2] > pixel[0] and pixel[2] > pixel[1]
        print(f'  {name} (row={row}, col={col}): RGB({pixel[0]}, {pixel[1]}, {pixel[2]}) {"← OCEAN" if is_ocean else "← LAND/PAPER"}')

# Check ocean pixel count
ocean_check = (bg_final_uint8[:,:,2] > bg_final_uint8[:,:,0]) & (bg_final_uint8[:,:,2] > bg_final_uint8[:,:,1])
print(f'\n  Ocean-like pixels (B > R and B > G): {ocean_check.sum()} / {W*H} ({ocean_check.sum()/(W*H)*100:.2f}%)')

# Save
print(f'\nSaving bg_dem.png -> {OUT_BG}')
Image.fromarray(bg_rgba, 'RGBA').save(OUT_BG, 'PNG', optimize=True)
print(f'Done! File size: {os.path.getsize(OUT_BG):,} bytes')
