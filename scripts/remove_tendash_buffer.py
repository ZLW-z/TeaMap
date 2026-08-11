# -*- coding: utf-8 -*-
"""
重新生成遮罩 + 修复DEM背景:
  - 遮罩: 仅保留中国省份边界, 去除十段线缓冲
  - DEM背景: 去除十段线周围的海洋蓝色, 恢复为纸色
保持南海区域效果如用户图示 (纸色背景 + 十段线条)
"""
import os
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = 900_000_000
import geopandas as gpd
from pyproj import CRS, Transformer
from shapely.ops import unary_union
from shapely.validation import make_valid

OUT_DIR = r'd:\Desktop\teamap\public\data\1'
OUT_MASK = os.path.join(OUT_DIR, 'mask_outside.png')
OUT_BG = os.path.join(OUT_DIR, 'bg_dem.png')

PROVINCES_GEOJSON = r'd:\Desktop\teamap\public\data\1\china_provinces_background.geojson'
TENDASH_SHP = r'D:\Desktop\数据\202405中国标准行政区划数据4\202405中国标准行政区划数据4\02_中国轮廓线\十段线.shp'

ALBERS_PROJ4 = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
ALBERS_CRS = CRS.from_string(ALBERS_PROJ4)
EPSG4326 = CRS.from_epsg(4326)
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

def albers_to_px(x_m, y_m):
    col = (x_m - ALB_X_MIN) / PX_SIZE
    row = (ALB_Y_MAX - y_m) / PX_SIZE
    return col, row

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

# ============================================================
# Step 1: Regenerate mask - ONLY China provinces, NO Ten-Dash Line buffer
# ============================================================
print('[1/3] 重新生成遮罩 (仅中国省份, 无十段线缓冲)...')

gdf_prov = gpd.read_file(PROVINCES_GEOJSON)
gdf_prov_alb = gdf_prov.to_crs(ALBERS_CRS)

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

# DO NOT include Ten-Dash Line buffer in mask
# The mask only covers China's actual territory
print(f'  China bounds (Albers): {china_union.bounds}')

gdf_china = gpd.GeoDataFrame(geometry=[china_union], crs=ALBERS_CRS)

# Rasterize mask: inside = transparent (alpha=0), outside = semi-transparent white (alpha=170)
inside_mask = np.zeros((H, W), dtype=np.uint8)
mask_pil = Image.fromarray(inside_mask, mode='L')
draw = ImageDraw.Draw(mask_pil)
draw_geom(china_union, draw, 255)
inside_mask = np.array(mask_pil)
inside_bool = inside_mask > 128
print(f'  Mask inside pixels (China territory): {inside_bool.sum()} / {W*H}')

# Create RGBA mask: inside = transparent, outside = semi-transparent white
mask_rgba = np.zeros((H, W, 4), dtype=np.uint8)
mask_rgba[:,:,0] = 255  # R=255 (white)
mask_rgba[:,:,1] = 255  # G=255 (white)
mask_rgba[:,:,2] = 247  # B=247 (paper-like)
mask_rgba[:,:,3] = np.where(inside_bool, 0, 170)  # Inside=0, Outside=170

print(f'  Saving mask → {OUT_MASK}')
Image.fromarray(mask_rgba, 'RGBA').save(OUT_MASK, 'PNG', optimize=True)
print(f'  File size: {os.path.getsize(OUT_MASK):,} bytes')

# Verify mask
y_coords, x_coords = np.where(mask_rgba[:,:,3] == 0)
if len(y_coords) > 0:
    y_min = ALB_Y_MAX - y_coords.max() * PX_SIZE
    y_max = ALB_Y_MAX - y_coords.min() * PX_SIZE
    x_min = ALB_X_MIN + x_coords.min() * PX_SIZE
    x_max = ALB_X_MIN + x_coords.max() * PX_SIZE
    print(f'  透明区 (中国领域) bounds:')
    print(f'    Y: {y_min:.0f} to {y_max:.0f}')
    print(f'    X: {x_min:.0f} to {x_max:.0f}')
    
    td_y, td_x = 362652, 386164
    inside = (y_min <= td_y <= y_max) and (x_min <= td_x <= x_max)
    print(f'  十段线南端 (Y={td_y:.0f}, X={td_x:.0f}) 是否在遮罩透明区: {inside}')
    print(f'  (十段线南端应该被遮罩白色覆盖, 因为它只是线条, 不属于中国陆地遮罩)')

# ============================================================
# Step 2: Fix bg_dem.png - Remove ocean blue colors around Ten-Dash Line
# ============================================================
print('\n[2/3] 修复 DEM 背景: 移除十段线周围的海洋蓝色...')

img = Image.open(OUT_BG)
bg_rgba = np.array(img).astype(np.float64)
rgb = bg_rgba[:,:,:3].copy()

# First, let's identify what we added: ocean blue pixels from the Ten-Dash Line buffer
# We need to restore paper-like colors in these areas

# Approach: Use the original land classification (bg_dem has light colors for land)
# For the extended Ten-Dash Line region, if the pixel is blue-ish (ocean) and
# was originally paper color (from old DEM), restore it.

# Load Ten-Dash Line and create a restore mask (areas where we want to remove ocean blue)
gdf_td = gpd.read_file(TENDASH_SHP)
gdf_td_alb = gdf_td.to_crs(ALBERS_CRS)

# Create restore mask: Ten-Dash Line + 800km buffer (same as what we added earlier)
td_buffered = gdf_td_alb.geometry.buffer(800000)
td_union = unary_union(td_buffered)

# Also create a larger mask for the extended buffer (1500km)
td_east_buffered = gdf_td_alb.geometry.buffer(1500000)
td_east_union = unary_union(td_east_buffered)

# Combine restore region (we want paper color, not ocean blue, in these areas)
restore_region = unary_union([td_union, td_east_union])

# BUT: We want to EXCLUDE actual China territory from restore (China is land color)
restore_region = restore_region.difference(china_union)

# Rasterize restore region
restore_mask = np.zeros((H, W), dtype=np.uint8)
rest_pil = Image.fromarray(restore_mask, mode='L')
rest_draw = ImageDraw.Draw(rest_pil)
draw_geom(restore_region, rest_draw, 255)
restore_mask = np.array(rest_pil)
restore_bool = restore_mask > 128
print(f'  Restore region pixels: {restore_bool.sum()} / {W*H}')

# Now identify which pixels in restore region are ocean-like (B > R, B > G)
ocean_like = (rgb[:,:,2] > rgb[:,:,0] + 3) & (rgb[:,:,2] > rgb[:,:,1] + 3)
to_restore = restore_bool & ocean_like
print(f'  Ocean pixels to restore to paper: {to_restore.sum()}')

# Restore paper colors using a gradient based on the original DEM values
# For simplicity, use the average paper color with slight terrain-like variation
# (similar to how ocean-free areas look in the original DEM)

# Sample some existing paper-color pixels to get the base tone
paper_mask = (rgb[:,:,0] > 225) & (rgb[:,:,1] > 220) & (rgb[:,:,2] > 210) & ~ocean_like
if paper_mask.sum() > 1000:
    paper_r = float(np.mean(rgb[paper_mask, 0]))
    paper_g = float(np.mean(rgb[paper_mask, 1]))
    paper_b = float(np.mean(rgb[paper_mask, 2]))
    print(f'  Sample paper base color: ({paper_r:.0f}, {paper_g:.0f}, {paper_b:.0f})')
else:
    paper_r, paper_g, paper_b = 238, 236, 227
    print(f'  Using default paper base: ({paper_r:.0f}, {paper_g:.0f}, {paper_b:.0f})')

# Create terrain-like variation for restored paper
# Use the blue variation as a proxy for very subtle terrain shading
# (Blue channels had depth shading, we can reuse it for subtle terrain texture)
blue_shading = (rgb[:,:,2] - rgb[:,:,0])  # B-R delta
blue_norm = np.clip(blue_shading / 40.0, -1, 1)

# For the restored area, apply: base paper color + very subtle shading
to_restore_3d = np.stack([to_restore]*3, axis=-1)
base_color = np.array([paper_r, paper_g, paper_b])

# Subtle shading: ±5 RGB variation
shading = blue_norm * 4.0

# Create variation per channel: slightly warm tint, slight grain
new_paper_rgb = np.zeros_like(rgb)
new_paper_rgb[:,:,0] = base_color[0] + shading * 0.8
new_paper_rgb[:,:,1] = base_color[1] + shading * 1.0
new_paper_rgb[:,:,2] = base_color[2] + shading * 1.2

# Apply restoration
rgb = np.where(to_restore_3d, new_paper_rgb, rgb)

# ============================================================
# Step 3: Also check if there are other ocean-blue pixels far from 
# actual coasts that should be paper color
# ============================================================

# Define the full canvas region: most of it should be paper color
# as per the user's example (global background is paper-like, not full ocean)

# In the user's example image:
# - Land areas have terrain colors (brown/yellow/terrain)
# - Sea areas (including around China) are PAPER COLOR (not blue!)
# Only small bays/coastlines have subtle blue

# So we should restore ALL distant ocean-blue pixels back to paper color
# EXCEPT possibly some near actual coastlines in China

# Create mask for "far from China" or "no data area"
# Simple approach: everything outside the 1500km buffer
distant_mask = ~restore_bool & ~inside_bool

# Find ocean-like pixels in distant areas and convert to paper
distant_ocean = distant_mask & ocean_like
if distant_ocean.sum() > 0:
    print(f'  Distant ocean pixels to convert: {distant_ocean.sum()}')
    
    # For distant areas, use a slightly more uniform paper color
    dist_paper_rgb = np.zeros_like(rgb)
    # Larger shading scale for more distant areas (but still subtle)
    shading_d = blue_norm * 3.0
    dist_paper_rgb[:,:,0] = (paper_r - 1) + shading_d * 0.7
    dist_paper_rgb[:,:,1] = (paper_g - 0) + shading_d * 0.9
    dist_paper_rgb[:,:,2] = (paper_b - 2) + shading_d * 1.1
    
    dist_restore_3d = np.stack([distant_ocean]*3, axis=-1)
    rgb = np.where(dist_restore_3d, dist_paper_rgb, rgb)

# Combine with alpha
new_bg_rgba = np.dstack([rgb, bg_rgba[:,:,3]])
new_bg_rgba = np.clip(new_bg_rgba, 0, 255).astype(np.uint8)

# ============================================================
# VERIFY
# ============================================================
print('\n[VERIFY] Color check after fix:')
areas = [
    ('十段线南端', 2982, 3733),
    ('南海中部', 3023, 3800),
    ('赤道附近', 3073, 3900),
    ('中国华南', 2302, 3500),
    ('海南岛上', 2523, 3630),
    ('台湾以东', 2700, 4500),
]
for name, row, col in areas:
    if 0 <= row < H and 0 <= col < W:
        pixel = rgb[row, col, :3]
        is_ocean = pixel[2] > pixel[0] + 2 and pixel[2] > pixel[1] + 2
        m_a = mask_rgba[row, col, 3]
        otype = 'OCEAN_BLUE' if is_ocean else 'PAPER/LAND'
        mtype = 'TRANSPARENT' if m_a < 10 else 'WHITE_MASK'
        print(f'  {name} (r={row},c={col}): RGB({pixel[0]:.0f},{pixel[1]:.0f},{pixel[2]:.0f}) <- {otype}, 遮罩 <- {mtype}')

# Count ocean-like pixels
ocean_check = (rgb[:,:,2] > rgb[:,:,0] + 2) & (rgb[:,:,2] > rgb[:,:,1] + 2)
print(f'\n  Total ocean-blue pixels: {ocean_check.sum()} / {W*H} ({ocean_check.sum()/(W*H)*100:.3f}%)')

# Save
print(f'\n[3/3] Saving fixed bg_dem.png → {OUT_BG}')
Image.fromarray(new_bg_rgba, 'RGBA').save(OUT_BG, 'PNG', optimize=True)
print(f'Done! File size: {os.path.getsize(OUT_BG):,} bytes')
