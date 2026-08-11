"""
将 china_dem.tif 从 WGS84 Albers 重投影到 EPSG:4326
1. 读取降采样 DEM
2. 逐像素从 EPSG:4326 -> Albers 采样
3. 渲染色带 PNG，NoData 透明
4. 保存 bounds JSON
"""
import os
import json
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = 200000000
from pyproj import CRS, Transformer

# === 路径 ===
DEM_TIF = r'D:\Desktop\星湖杯\茶叶\早期人工茶区分布\MyProject\china_dem.tif'
OUT_DIR = r'd:\Desktop\teamap\public\data\1'
OUT_PNG = os.path.join(OUT_DIR, 'dem_relief.png')
OUT_BOUNDS = os.path.join(OUT_DIR, 'dem_bounds.json')

# === CRS ===
crs_albers = CRS.from_string(
    '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 '
    '+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
)
to_albers = Transformer.from_crs('EPSG:4326', crs_albers, always_xy=True)

# === GeoTIFF 参数 ===
ul_x = -6520913.109840605
ul_y = 7043715.705487048
pixel_x = 865.8048346495104
pixel_y = 608.8370737602679
orig_w, orig_h = 14816, 11910

# === 1. 读取并降采样 DEM ===
print('Reading DEM...')
img = Image.open(DEM_TIF)
ds_w = 4096
ds_h = int(orig_h * ds_w / orig_w)
print(f'Downsampling to {ds_w}x{ds_h}')
img_ds = img.resize((ds_w, ds_h), Image.NEAREST)
dem_arr = np.array(img_ds, dtype=np.float32)
img.close()
img_ds.close()
print(f'DEM shape: {dem_arr.shape}, range: [{dem_arr.min()}, {dem_arr.max()}]')

# === 2. 定义输出网格 (EPSG:4326) ===
# 中国及周边区域
lon_min, lon_max = 70.0, 140.0
lat_min, lat_max = 15.0, 55.0
resolution = 0.04  # 度/像素

out_w = int((lon_max - lon_min) / resolution)
out_h = int((lat_max - lat_min) / resolution)
print(f'Output grid: {out_w}x{out_h}, resolution: {resolution}°')

# === 3. 重投影采样 ===
print('Reprojecting...')
# 创建输出网格的经纬度坐标
out_lons = np.linspace(lon_min, lon_max, out_w, endpoint=False)
out_lats = np.linspace(lat_max, lat_min, out_h, endpoint=False)  # 北到南
lon_grid, lat_grid = np.meshgrid(out_lons, out_lats)

# 变换到 Albers 坐标
# pyproj transform: input (lon, lat) -> (x, y)
flat_lons = lon_grid.ravel()
flat_lats = lat_grid.ravel()
x_proj, y_proj = to_albers.transform(flat_lons, flat_lats)

# 计算在降采样 DEM 中的像素坐标
# 降采样后的像素大小
ds_pixel_x = pixel_x * orig_w / ds_w
ds_pixel_y = pixel_y * orig_h / ds_h
# Pixel (col, row) center = (ul_x + (col + 0.5) * ds_pixel_x, ul_y - (row + 0.5) * ds_pixel_y)
col_src = (x_proj - ul_x) / ds_pixel_x - 0.5
row_src = (ul_y - y_proj) / ds_pixel_y - 0.5

# 重塑为网格
col_grid = col_src.reshape(out_h, out_w)
row_grid = row_src.reshape(out_h, out_w)

# 过滤超出范围的像素
valid = (col_grid >= 0) & (col_grid < ds_w - 1) & (row_grid >= 0) & (row_grid < ds_h - 1)

# 最近邻采样
col_int = np.clip(np.round(col_grid).astype(int), 0, ds_w - 1)
row_int = np.clip(np.round(row_grid).astype(int), 0, ds_h - 1)

# 采样
sampled = dem_arr[row_int, col_int]
sampled[~valid] = 0  # 超出范围的设为 NoData

print(f'Sampled data: shape={sampled.shape}, non-zero={np.sum(sampled != 0)}')
print(f'Value range: [{sampled[sampled != 0].min() if np.any(sampled != 0) else 0}, '
      f'{sampled.max()}]')

# === 4. 渲染色带 PNG ===
print('Rendering colors...')
arr = sampled
h, w = arr.shape
rgba = np.zeros((h, w, 4), dtype=np.uint8)

# NoData = 0: 透明
nodata_mask = (arr == 0)

# 负值（海洋深度）: 浅蓝灰半透明
neg_mask = arr < 0
rgba[neg_mask] = (180, 195, 200, 100)

# 正值: 按高程着色
pos_mask = arr > 0
pos_vals = arr[pos_mask]

# 归一化: 0-7000m
t = np.clip(pos_vals / 7000, 0, 1)

colors = np.zeros((len(pos_vals), 4), dtype=np.uint8)

# 段1: 0-200m 深绿 #516D33 -> #5C7C3A
s1 = t < 0.03
k1 = np.clip(t[s1] / 0.03, 0, 1)
colors[s1, 0] = (81 + (92 - 81) * k1).astype(np.uint8)
colors[s1, 1] = (109 + (124 - 109) * k1).astype(np.uint8)
colors[s1, 2] = (51 + (58 - 51) * k1).astype(np.uint8)
colors[s1, 3] = 230

# 段2: 200-1000m 绿 -> 米色 #C3C19A
s2 = (t >= 0.03) & (t < 0.15)
k2 = np.clip((t[s2] - 0.03) / 0.12, 0, 1)
colors[s2, 0] = (92 + (195 - 92) * k2).astype(np.uint8)
colors[s2, 1] = (124 + (193 - 124) * k2).astype(np.uint8)
colors[s2, 2] = (58 + (154 - 58) * k2).astype(np.uint8)
colors[s2, 3] = 255

# 段3: 1000-3000m 米色 -> 金棕 #B28F4C
s3 = (t >= 0.15) & (t < 0.45)
k3 = np.clip((t[s3] - 0.15) / 0.30, 0, 1)
colors[s3, 0] = (195 + (178 - 195) * k3).astype(np.uint8)
colors[s3, 1] = (193 + (143 - 193) * k3).astype(np.uint8)
colors[s3, 2] = (154 + (76 - 154) * k3).astype(np.uint8)
colors[s3, 3] = 255

# 段4: 3000-5000m 金棕 -> 深棕
s4 = (t >= 0.45) & (t < 0.72)
k4 = np.clip((t[s4] - 0.45) / 0.27, 0, 1)
colors[s4, 0] = (178 + (107 - 178) * k4).astype(np.uint8)
colors[s4, 1] = (143 + (85 - 143) * k4).astype(np.uint8)
colors[s4, 2] = (76 + (48 - 76) * k4).astype(np.uint8)
colors[s4, 3] = 255

# 段5: 5000m+ 深棕 -> 浅纸色 #F7F4EB
s5 = t >= 0.72
k5 = np.clip((t[s5] - 0.72) / 0.28, 0, 1)
colors[s5, 0] = (107 + (247 - 107) * k5).astype(np.uint8)
colors[s5, 1] = (85 + (244 - 85) * k5).astype(np.uint8)
colors[s5, 2] = (48 + (235 - 48) * k5).astype(np.uint8)
colors[s5, 3] = 255

rgba[pos_mask] = colors

# 保存 PNG
print(f'Saving PNG to {OUT_PNG}...')
result = Image.fromarray(rgba, 'RGBA')
result.save(OUT_PNG, 'PNG', optimize=True)
result = None

# === 5. 保存 bounds JSON ===
bounds_data = {
    "south": lat_min,
    "west": lon_min,
    "north": lat_max,
    "east": lon_max,
    "southWest": [lat_min, lon_min],
    "northEast": [lat_max, lon_max],
    "center": [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2],
    "imageSize": [out_w, out_h],
    "crs": "EPSG:4326"
}
with open(OUT_BOUNDS, 'w', encoding='utf-8') as f:
    json.dump(bounds_data, f, indent=2, ensure_ascii=False)
print(f'Saved bounds: {bounds_data}')

# 释放内存
dem_arr = None
sampled = None
rgba = None
arr = None

print('\nDone!')
