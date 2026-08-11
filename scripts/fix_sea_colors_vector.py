# -*- coding: utf-8 -*-
"""
快速修复南海区域颜色:
  使用矢量数据(十段线+中国轮廓)定义海洋区域, 将 paper-like 颜色改为海洋蓝色
  不依赖 5.7GB DEM 重投影, 仅需数秒
"""
import os
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = 900_000_000
import geopandas as gpd
from pyproj import CRS, Transformer
from shapely.ops import unary_union

OUT_DIR = r'd:\Desktop\teamap\public\data\1'
OUT_BG = os.path.join(OUT_DIR, 'bg_dem.png')
TENDASH_SHP = r'D:\Desktop\数据\202405中国标准行政区划数据4\202405中国标准行政区划数据4\02_中国轮廓线\十段线.shp'
PROVINCES_GEOJSON = r'd:\Desktop\teamap\public\data\1\china_provinces_background.geojson'

ALBERS_PROJ4 = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
ALBERS_CRS = CRS.from_string(ALBERS_PROJ4)
EPSG4326 = CRS.from_epsg(4326)
ll_to_albers = Transformer.from_crs(EPSG4326, ALBERS_CRS, always_xy=True)

# Canvas parameters (must match process_ch1_global.py)
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

def albers_to_px(x_m, y_m):
    col = (x_m - ALB_X_MIN) / PX_SIZE
    row = (ALB_Y_MAX - y_m) / PX_SIZE
    return col, row

# Step 1: Read existing bg_dem.png
print('[1/4] Reading existing bg_dem.png...')
img = Image.open(OUT_BG)
arr = np.array(img).astype(np.float64)
print(f'  Shape: {arr.shape}')

# Step 2: Load vector data and create ocean masks
print('\n[2/4] Loading vector data...')

# Load Ten-Dash Line
gdf_td = gpd.read_file(TENDASH_SHP)
gdf_td_alb = gdf_td.to_crs(ALBERS_CRS)
print(f'  Ten-Dash Line bounds (Albers): {gdf_td_alb.total_bounds}')

# Create South China Sea region by buffering Ten-Dash Line (800km)
td_buffered = gdf_td_alb.geometry.buffer(800000)  # 800km buffer
td_union = unary_union(td_buffered)
print(f'  Ten-Dash Line + 800km buffer bounds: {td_union.bounds}')

# Also load China provinces for land mask
gdf_prov = gpd.read_file(PROVINCES_GEOJSON)
gdf_prov_alb = gdf_prov.to_crs(ALBERS_CRS)
from shapely.validation import make_valid
fixed_geoms = []
for g in gdf_prov_alb.geometry.tolist():
    try:
        if not g.is_valid:
            g = make_valid(g)
        fixed_geoms.append(g.buffer(0) if not g.is_empty else g)
    except:
        try:
            fixed_geoms.append(g.buffer(0))
        except:
            pass
china_union = unary_union(fixed_geoms)
print(f'  China provinces bounds: {china_union.bounds}')

# Define ocean region = Ten-Dash Line buffer MINUS China land
# (This gives us the South China Sea area around the Ten-Dash Line)
sea_region = td_union.difference(china_union)

# Step 3: Rasterize ocean region
print('\n[3/4] Rasterizing ocean region...')

# Create raster mask
ocean_mask = np.zeros((H, W), dtype=np.uint8)
mask_pil = Image.fromarray(ocean_mask, mode='L')
draw = ImageDraw.Draw(mask_pil)

def draw_geom(geom, pil_draw, value=255):
    if geom.is_empty:
        return
    if geom.geom_type == 'Polygon':
        poly = []
        for x_m, y_m in geom.exterior.coords:
            c, r = albers_to_px(x_m, y_m)
            poly.append((c, r))
        if len(poly) >= 3:
            pil_draw.polygon(poly, fill=value, outline=value)
        for interior in geom.interiors:
            poly = []
            for x_m, y_m in interior.coords:
                c, r = albers_to_px(x_m, y_m)
                poly.append((c, r))
            if len(poly) >= 3:
                pil_draw.polygon(poly, fill=0)
    elif geom.geom_type == 'MultiPolygon':
        for p in geom.geoms:
            draw_geom(p, pil_draw, value)
    elif geom.geom_type == 'GeometryCollection':
        for g in geom.geoms:
            draw_geom(g, pil_draw, value)

draw_geom(sea_region, draw, 255)

ocean_mask = np.array(mask_pil)
ocean_bool = ocean_mask > 128
print(f'  Ocean mask pixels: {ocean_bool.sum()} / {W*H}')

# Step 4: Apply ocean blue colors to the masked region
print('\n[4/4] Applying ocean colors...')

# Get the existing RGB
rgb = arr[:, :, :3].copy()

# For ocean pixels, replace paper-like colors with ocean blue
# Use gradient from shallow to deep based on position in the region
# (Distance from Ten-Dash Line coast)

# Simple approach: apply a base ocean color with slight variation
# based on distance from the Ten-Dash Line

# Create distance-based coloring
# For simplicity, use Y coordinate as a proxy for depth (further south = deeper)
ys_grid = np.arange(H).reshape(-1, 1)
# Y increases northward, so southern areas have lower Y
# Normalize: lower Y = deeper ocean
depth_factor = np.clip(1.0 - (ys_grid - 1500) / 2000, 0, 1)  # 0 at north, 1 at south
# Broadcast to full image
depth_map = np.broadcast_to(depth_factor, (H, W))

# Apply ocean colors
# Shallow (near Ten-Dash Line): light blue RGB(210, 222, 226)
# Deep (further south): darker blue RGB(155, 190, 205)
ocean_pixels = ocean_bool
if ocean_pixels.any():
    d = depth_map[ocean_pixels]
    # Shallow: RGB(210, 222, 226)
    # Deep: RGB(155, 190, 205)
    rgb[ocean_pixels, 0] = 210 + (155 - 210) * d
    rgb[ocean_pixels, 1] = 222 + (190 - 222) * d
    rgb[ocean_pixels, 2] = 226 + (205 - 226) * d

# Also apply ocean colors to areas that are clearly ocean (low elevation near China)
# Use a broader approach: everything in the extended Ten-Dash Line region that's not land
# should be ocean

# Create extended ocean region (buffer Ten-Dash Line more aggressively for surrounding seas)
# Western Pacific: buffer the Ten-Dash Line eastern end
# This covers the area east of Taiwan and south of Japan
td_east_buffer = gdf_td_alb.geometry.buffer(1500000)  # 1500km
td_east_union = unary_union(td_east_buffer)

# Rasterize this extended region
ext_mask = np.zeros((H, W), dtype=np.uint8)
ext_pil = Image.fromarray(ext_mask, mode='L')
ext_draw = ImageDraw.Draw(ext_pil)
ext_region = td_east_union.difference(china_union)
draw_geom(ext_region, ext_draw, 255)
ext_mask = np.array(ext_pil)
ext_bool = ext_mask > 128

# Apply ocean colors to extended region (lighter blue since these are open ocean)
ext_pixels = ext_bool & ~ocean_bool  # Only apply to new pixels
if ext_pixels.any():
    d = depth_map[ext_pixels] * 0.7  # Less depth variation for open ocean
    # Open ocean: RGB(175, 200, 210) to RGB(155, 185, 200)
    rgb[ext_pixels, 0] = 175 + (155 - 175) * d
    rgb[ext_pixels, 1] = 200 + (185 - 200) * d
    rgb[ext_pixels, 2] = 210 + (200 - 210) * d

# Combine with original alpha
new_rgba = np.dstack([rgb, arr[:, :, 3]])

# Verify
print('\n[VERIFY] Color check after fix:')
areas = [
    ('十段线南端', 2982, 3733),
    ('南海中部', 3023, 3800),
    ('赤道附近', 3073, 3900),
    ('中国华南', 2302, 3500),
    ('中国华中', 1921, 3800),
]
for name, row, col in areas:
    if 0 <= row < H and 0 <= col < W:
        pixel = rgb[row, col, :3]
        is_ocean = pixel[2] > pixel[0] and pixel[2] > pixel[1]
        print(f'  {name} (row={row}, col={col}): RGB({pixel[0]:.0f}, {pixel[1]:.0f}, {pixel[2]:.0f}) {"← OCEAN" if is_ocean else "← LAND"}')

# Check ocean pixel count
ocean_check = (rgb[:,:,2] > rgb[:,:,0]) & (rgb[:,:,2] > rgb[:,:,1])
print(f'\n  Ocean-like pixels (B > R and B > G): {ocean_check.sum()} / {W*H} ({ocean_check.sum()/(W*H)*100:.2f}%)')

# Save
print(f'\nSaving fixed bg_dem.png -> {OUT_BG}')
Image.fromarray(np.clip(new_rgba, 0, 255).astype(np.uint8), 'RGBA').save(OUT_BG, 'PNG', optimize=True)
print(f'Done! File size: {os.path.getsize(OUT_BG):,} bytes')
