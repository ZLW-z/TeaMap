# -*- coding: utf-8 -*-
"""
正确修复 DEM 背景:
  - 保留全球 DEM 真实地形纹理 (hillshade)
  - 海洋区域: 颜色使用暖纸色调 (非蓝色), 但保留地形光照
  - 陆地区域: 保持原有颜色不变
  - 不用统一纯色纸色覆盖!
"""
import os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = 900_000_000
import rasterio
from rasterio.warp import reproject, Resampling
from pyproj import CRS, Transformer
import geopandas as gpd
from shapely.ops import unary_union
from shapely.validation import make_valid

GLOBAL_TIF = r'D:\Desktop\2026年DEM地形数据\1.拼接成全球一张图的数据\global.tif'
OUT_DIR = r'd:\Desktop\teamap\public\data\1'
OUT_BG = os.path.join(OUT_DIR, 'bg_dem.png')
PROVINCES_GEOJSON = r'd:\Desktop\teamap\public\data\1\china_provinces_background.geojson'

ALBERS_PROJ4 = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
ALBERS_CRS = CRS.from_string(ALBERS_PROJ4)
EPSG4326 = CRS.from_epsg(4326)
ll_to_albers = Transformer.from_crs(EPSG4326, ALBERS_CRS, always_xy=True)

# Canvas parameters
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

# ============================================================
# Step 1: Read EXISTING bg_dem.png (has correct land colors)
# ============================================================
print('[1/5] Reading existing bg_dem.png...')
img = Image.open(OUT_BG)
orig_rgba = np.array(img).astype(np.float64)
orig_rgb = orig_rgba[:,:,:3].copy()
print(f'  Shape: {orig_rgba.shape}')

# ============================================================
# Step 2: Reproject global DEM at moderate resolution (1/2 of full)
# This is faster than full res, we can upsample later
# Actually, let's try 1/1 resolution but bilinear warp with num_threads
# To speed things up, use the same resolution but only compute once
# ============================================================
print('\n[2/5] Reprojecting global DEM to Albers (for terrain texture)...')
# Use a LOW-RES approach to get DEM values quickly:
# 1/8 resolution for reprojection, then upsample for hillshade calc
LOW_DIV = 4
low_w = W // LOW_DIV
low_h = H // LOW_DIV
low_px = PX_SIZE * LOW_DIV
low_transform = rasterio.transform.from_origin(ALB_X_MIN, ALB_Y_MAX, low_px, low_px)

low_dem = np.full((low_h, low_w), -32767, dtype=np.float32)
with rasterio.open(GLOBAL_TIF) as src:
    src_nodata = src.nodata
    reproject(
        source=rasterio.band(src, 1),
        destination=low_dem,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=low_transform,
        dst_crs=ALBERS_CRS,
        src_nodata=src_nodata,
        dst_nodata=-32767,
        resampling=Resampling.bilinear,
        num_threads=4
    )

print(f'  Low-res DEM: {low_dem.shape}, range=[{low_dem.min():.0f}, {low_dem.max():.0f}]')

# Fill NODATA with sea level 0
NODATA = -32767
low_dem[low_dem <= NODATA] = 0.0

# ============================================================
# Step 3: Upsample DEM to full resolution for detailed hillshade
# ============================================================
print('\n[3/5] Upsampling DEM & computing hillshade...')

# Upsample low DEM using PIL
low_dem_pil = Image.fromarray(((np.clip(low_dem, -6000, 8000) + 6000) / 14000 * 65535).astype(np.uint16), mode='I;16')
full_dem_pil = low_dem_pil.resize((W, H), Image.BILINEAR)
full_dem = ((np.array(full_dem_pil).astype(np.float64) / 65535) * 14000) - 6000
print(f'  Full-res DEM: {full_dem.shape}')

# Compute hillshade (keep terrain texture)
PX_X_M = PX_SIZE
PX_Y_M = PX_SIZE

# Valid mask = everything (we filled NODATA)
valid_mask = np.ones_like(full_dem, dtype=bool)

def compute_hillshade(dem_in, valid_mask_in, px_x_m, px_y_m,
                      azimuth_deg=320.0, altitude_deg=40.0, z_factor=1.0):
    dem = dem_in.copy()
    vmean = float(np.mean(dem_in[valid_mask_in])) if valid_mask_in.any() else 0.0
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

# Compute MULTI-LAYER hillshade (keep terrain texture but use MODERATE z_factor for ocean)
# For OCEAN: use lower z_factor so terrain is subtle (as in reference image)

# Land mask (China actual land) for reference
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

# Rasterize China mask at low resolution first, then upsample
from PIL import ImageDraw
china_low = np.zeros((low_h, low_w), dtype=np.uint8)
cl_pil = Image.fromarray(china_low, mode='L')
cl_draw = ImageDraw.Draw(cl_pil)

def low_px(x_m, y_m):
    col = (x_m - ALB_X_MIN) / low_px
    row = (ALB_Y_MAX - y_m) / low_px
    return col, row

def draw_low_geom(geom, d):
    if geom.is_empty:
        return
    if geom.geom_type == 'Polygon':
        poly = []
        for x_m, y_m in geom.exterior.coords:
            c, r = low_px(x_m, y_m)
            poly.append((c, r))
        if len(poly) >= 3:
            d.polygon(poly, fill=255, outline=255)
    elif geom.geom_type == 'MultiPolygon':
        for p in geom.geoms:
            draw_low_geom(p, d)
    elif geom.geom_type == 'GeometryCollection':
        for g in geom.geoms:
            draw_low_geom(g, d)

draw_low_geom(china_union, cl_draw)
china_low = np.array(cl_pil)
# Upsample
china_full_pil = Image.fromarray(china_low, mode='L').resize((W, H), Image.BILINEAR)
china_full = np.array(china_full_pil) > 128
print(f'  China land pixels: {china_full.sum()}')

# Ocean = NOT China land
# Note: full_dem <= 0 includes actual sea and sea-level NODATA fill
ocean_mask = ~china_full  # Everything outside China is "ocean/sea area"
print(f'  Ocean/sea area pixels: {ocean_mask.sum()}')

# ============================================================
# Step 4: Compute hillshade and render PAPER-COLORED OCEAN WITH TERRAIN TEXTURE
# ============================================================
print('\n[4/5] Applying terrain-colored ocean...')

# Compute hillshade with MODERATE intensity (good for subtle ocean floor texture)
hs_main = compute_hillshade(full_dem, valid_mask, PX_X_M, PX_Y_M,
                            azimuth_deg=320, altitude_deg=38, z_factor=1.5)

# Low-angle hillshade for deeper shadows
hs_low = compute_hillshade(full_dem, valid_mask, PX_X_M, PX_Y_M,
                           azimuth_deg=335, altitude_deg=22, z_factor=2.0)

# Compute shadow and intensity (subtle!)
shadow_map = np.clip((1.0 - hs_low) * 0.5 + (1.0 - hs_main) * 0.3, 0, 1)
highlight_map = np.clip(hs_main * 0.7 + hs_low * 0.2, 0, 1)

# Overall intensity: MILD variation (0.88 ~ 1.08) for subtle paper texture
ocean_intensity = 0.97 - shadow_map * 0.15 + highlight_map * 0.10
ocean_intensity = np.clip(ocean_intensity, 0.85, 1.10)

# Warm PAPER base color for ocean (as in reference image)
# From the user's reference image, the background is warm off-white/beige
# RGB(238, 236, 227) — this matches the existing paper tone
base_paper = np.array([237.0, 235.0, 226.0])

# Add SUBTLE warm-cool tone variation based on depth (not blue!)
# Slightly warmer for shallow, slightly cooler for deep (but stay in paper range!)
# Depth = -full_dem for ocean areas (negative elevation = depth)
depth_m = np.clip(-full_dem, 0, 5000)  # meters, capped
depth_norm = depth_m / 5000.0  # 0 = shallow/land, 1 = deep

# Very subtle tint: warm for shallow (RGB slightly higher R/G), slightly cooler for deep (slightly more B)
tint = np.zeros((H, W, 3), dtype=np.float64)
tint[:,:,0] = base_paper[0] - 3 * depth_norm  # Slightly less red in deep
tint[:,:,1] = base_paper[1] - 2 * depth_norm  # Slightly less green in deep
tint[:,:,2] = base_paper[2] + 0 * depth_norm  # Keep B same for paper look (NO blue)

# Actually: keep base color but add a VERY subtle brown-greenish tint for depth
# Better approach: keep color uniform, let the hillshade intensity do all the variation
# (matching user's reference image where ocean is uniform paper with subtle texture)

# Create ocean rgb: base paper color × hillshade intensity (preserves terrain texture!)
ocean_rgb = np.zeros((H, W, 3), dtype=np.float64)
oi3 = np.stack([ocean_intensity] * 3, axis=-1)
ocean_rgb[:,:,0] = base_paper[0] * oi3[:,:,0]
ocean_rgb[:,:,1] = base_paper[1] * oi3[:,:,1]
ocean_rgb[:,:,2] = base_paper[2] * oi3[:,:,2]

# Clip to valid range
ocean_rgb = np.clip(ocean_rgb, 210, 255)

# ============================================================
# Now assemble the final image:
#   - China land area: keep ORIGINAL colors (land terrain is correct already!)
#   - Everything else (ocean/sea): use new PAPER-colored terrain texture
# ============================================================
final_rgb = orig_rgb.copy()

# Only replace OCEAN areas (everything outside China land)
ocean_3d = np.stack([ocean_mask] * 3, axis=-1)
final_rgb = np.where(ocean_3d, ocean_rgb, final_rgb)

# Combine with alpha
final_rgba = np.dstack([final_rgb, orig_rgba[:,:,3]])
final_rgba = np.clip(final_rgba, 0, 255).astype(np.uint8)

# ============================================================
# VERIFY
# ============================================================
print('\n[5/5] VERIFYING result...')

areas = [
    ('十段线南端 (r=2982,c=3733)', 2982, 3733),
    ('南海中部 (r=3023,c=3800)', 3023, 3800),
    ('赤道附近 (r=3073,c=3900)', 3073, 3900),
    ('中国华南 (r=2302,c=3500)', 2302, 3500),
    ('海南岛上 (r=2523,c=3630)', 2523, 3630),
    ('远海区域 (r=3400,c=5500)', 3400, 5500),
]
for name, row, col in areas:
    if 0 <= row < H and 0 <= col < W:
        orig_p = orig_rgb[row, col, :3]
        new_p = final_rgb[row, col, :3]
        is_china = china_full[row, col]
        # Check if there's texture variation (sample small area)
        if row > 5 and col > 5:
            sample = final_rgb[row-5:row+5, col-5:col+5, :]
            std_r = np.std(sample[:,:,0])
            std_g = np.std(sample[:,:,1])
            std_b = np.std(sample[:,:,2])
            texture_idx = (std_r + std_g + std_b) / 3
            texture_note = '有纹理' if texture_idx > 1.5 else '纹理较弱/纯色'
        else:
            texture_note = '边界'
        area_type = '中国陆地' if is_china else '海洋/背景'
        changed = not np.allclose(orig_p, new_p, atol=1)
        chg_note = '颜色已更新' if changed else '保持原样'
        print(f'  {name}:')
        print(f'    类型: {area_type}, {texture_note}, {chg_note}')
        print(f'    原RGB: ({orig_p[0]:.0f},{orig_p[1]:.0f},{orig_p[2]:.0f}) → 新RGB: ({new_p[0]:.0f},{new_p[1]:.0f},{new_p[2]:.0f})')

# Check for blue pixels
blue_count = ((final_rgb[:,:,2] > final_rgb[:,:,0] + 2) & 
              (final_rgb[:,:,2] > final_rgb[:,:,1] + 2)).sum()
print(f'\n  蓝色像素 (B > R+2 且 B > G+2): {blue_count} / {W*H} ({blue_count/(W*H)*100:.3f}%)')

# Check texture variation (std in a large ocean patch)
ocean_sample = final_rgb[3200:3400, 4500:5000, :]
if ocean_sample.size > 0:
    mean_std = (np.std(ocean_sample[:,:,0]) + np.std(ocean_sample[:,:,1]) + np.std(ocean_sample[:,:,2])) / 3
    print(f'  远海大样本地形纹理 (std): {mean_std:.2f} (原纯色=0.0, 有纹理>1.0)')

# Save
print(f'\n  Saving bg_dem.png → {OUT_BG}')
Image.fromarray(final_rgba, 'RGBA').save(OUT_BG, 'PNG', optimize=True)
print(f'Done! File size: {os.path.getsize(OUT_BG):,} bytes')
