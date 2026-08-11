# -*- coding: utf-8 -*-
"""
快速修复 bg_dem.png 海洋颜色:
  1. 读取现有 bg_dem.png
  2. 低分辨率读取全球 DEM 快速分类海陆
  3. 将海洋像素改为蓝色系
  4. 保存修复后的 bg_dem.png
"""
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

# Step 1: Read existing bg_dem.png
print('[1/5] Reading existing bg_dem.png...')
img = Image.open(OUT_BG)
arr = np.array(img)
rgba = arr.astype(np.float64)
print(f'  Shape: {arr.shape}')

# Step 2: Read global DEM at LOW resolution for quick classification
print('\n[2/5] Reading global DEM at low resolution for classification...')
# Use 1/16 resolution for fast classification
low_w = W // 16
low_h = H // 16
low_arr = np.full((low_h, low_w), -32767, dtype=np.float32)

with rasterio.open(GLOBAL_TIF) as src:
    src_nodata = src.nodata
    # Calculate appropriate resolution for low-res read
    # We want low_w pixels across the canvas width
    low_px_size = CANVAS_W_M / low_w
    low_transform = rasterio.transform.from_origin(ALB_X_MIN, ALB_Y_MAX, low_px_size, low_px_size)
    
    reproject(
        source=rasterio.band(src, 1),
        destination=low_arr,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=low_transform,
        dst_crs=ALBERS_CRS,
        src_nodata=src_nodata,
        dst_nodata=-32767,
        resampling=Resampling.bilinear,
        num_threads=4
    )

print(f'  Low-res shape: {low_arr.shape}, range=[{low_arr.min():.0f}, {low_arr.max():.0f}]')

# Step 3: Classify ocean vs land at low resolution
print('\n[3/5] Classifying ocean vs land...')
NODATA = -32767
nodata_mask = low_arr <= NODATA
low_arr[nodata_mask] = 0.0  # Fill NODATA with sea level

low_ocean = (low_arr <= 0) & (low_arr > NODATA)
low_land = low_arr > 0
print(f'  Low-res ocean pixels: {low_ocean.sum()} / {low_arr.size}')

# Upscale ocean mask to full resolution using PIL
low_ocean_img = Image.fromarray(low_ocean.astype(np.uint8) * 255, mode='L')
full_ocean_img = low_ocean_img.resize((W, H), Image.BILINEAR)
full_ocean = np.array(full_ocean_img) > 128

print(f'  Full-res ocean pixels: {full_ocean.sum()} / {W*H}')

# Step 4: Convert ocean pixels to blue colors
print('\n[4/5] Converting ocean pixels to blue...')

# Get DEM values at low-res for depth-based coloring
# Normalize depth values
low_depth = np.clip(-low_arr, 0, 6000)  # Convert to positive depth, cap at 6000m
depth_norm = low_depth / 6000.0

# Upscale depth to full resolution
depth_img = Image.fromarray((depth_norm * 255).astype(np.uint8), mode='L')
full_depth_img = depth_img.resize((W, H), Image.BILINEAR)
full_depth = np.array(full_depth_img).astype(np.float64) / 255.0

# Create ocean color layers based on depth
# Shallow (0-200m): light blue
# Mid (200-1500m): medium blue
# Deep (1500-4000m): dark blue
# Abyss (4000m+): deepest blue

# Calculate depth in meters from normalized depth
depth_m = full_depth * 6000.0

ocean_mask = full_ocean
new_rgb = rgba[:, :, :3].copy()

# Apply ocean colors with depth-based gradient
# Shallow: RGB(214, 224, 228) -> RGB(198, 218, 222)
# Mid: RGB(198, 218, 222) -> RGB(174, 206, 218)  
# Deep: RGB(174, 206, 218) -> RGB(138, 174, 198)
# Abyss: RGB(138, 174, 198) -> RGB(108, 144, 176)

ocean_shallow = ocean_mask & (depth_m <= 200)
ocean_mid = ocean_mask & (depth_m > 200) & (depth_m <= 1500)
ocean_deep = ocean_mask & (depth_m > 1500) & (depth_m <= 4000)
ocean_abyss = ocean_mask & (depth_m > 4000)

# Shallow sea
if ocean_shallow.any():
    t = np.clip(depth_m[ocean_shallow] / 200.0, 0, 1)
    new_rgb[ocean_shallow, 0] = 214 + (198 - 214) * t
    new_rgb[ocean_shallow, 1] = 224 + (218 - 224) * t
    new_rgb[ocean_shallow, 2] = 228 + (222 - 228) * t

# Mid sea
if ocean_mid.any():
    t = np.clip((depth_m[ocean_mid] - 200) / 1300.0, 0, 1)
    new_rgb[ocean_mid, 0] = 198 + (174 - 198) * t
    new_rgb[ocean_mid, 1] = 218 + (206 - 218) * t
    new_rgb[ocean_mid, 2] = 222 + (218 - 222) * t

# Deep sea
if ocean_deep.any():
    t = np.clip((depth_m[ocean_deep] - 1500) / 2500.0, 0, 1)
    new_rgb[ocean_deep, 0] = 174 + (138 - 174) * t
    new_rgb[ocean_deep, 1] = 206 + (174 - 206) * t
    new_rgb[ocean_deep, 2] = 218 + (198 - 218) * t

# Abyss
if ocean_abyss.any():
    t = np.clip(np.minimum((depth_m[ocean_abyss] - 4000) / 2000.0, 1.0), 0, 1)
    new_rgb[ocean_abyss, 0] = 138 + (108 - 138) * t
    new_rgb[ocean_abyss, 1] = 174 + (144 - 174) * t
    new_rgb[ocean_abyss, 2] = 198 + (176 - 198) * t

# Preserve the alpha channel
new_rgba = np.dstack([new_rgb, rgba[:, :, 3]])

# Verify the fix
print('\n[VERIFY] Color check after fix:')
areas = [
    ('十段线南端', 2982, 3733),
    ('南海中部', 3023, 3800),
    ('赤道附近', 3073, 3900),
    ('中国华南', 2302, 3500),
]
for name, row, col in areas:
    if 0 <= row < H and 0 <= col < W:
        pixel = new_rgb[row, col, :3]
        is_ocean = pixel[2] > pixel[0] and pixel[2] > pixel[1]
        print(f'  {name} (row={row}, col={col}): RGB({pixel[0]:.0f}, {pixel[1]:.0f}, {pixel[2]:.0f}) {"← OCEAN" if is_ocean else "← LAND"}')

# Check overall ocean pixel count
ocean_check = (new_rgb[:,:,2] > new_rgb[:,:,0]) & (new_rgb[:,:,2] > new_rgb[:,:,1])
print(f'\n  Ocean-like pixels (B > R and B > G): {ocean_check.sum()} / {W*H} ({ocean_check.sum()/(W*H)*100:.2f}%)')

# Step 5: Save
print(f'\n[5/5] Saving fixed bg_dem.png -> {OUT_BG}')
Image.fromarray(np.clip(new_rgba, 0, 255).astype(np.uint8), 'RGBA').save(OUT_BG, 'PNG', optimize=True)
print(f'Done! File size: {os.path.getsize(OUT_BG):,} bytes')
