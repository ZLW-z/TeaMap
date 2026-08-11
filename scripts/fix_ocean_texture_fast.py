# -*- coding: utf-8 -*-
"""
超快速修复 - 用 DEM OVERVIEW (概览层) 读取获取地形纹理
不读取5.7GB原始高分辨率, 直接用已有的降采样概览
"""
import os
import numpy as np
from PIL import Image, ImageDraw
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
# Step 1: Check available OVERVIEWS
# ============================================================
print('\n[1/5] Checking DEM overviews...')
with rasterio.open(GLOBAL_TIF) as src:
    print(f'  Base level: {src.width}x{src.height}')
    overviews = src.overviews(1)
    print(f'  Available overviews: {overviews}')
    
    # Pick a suitable overview level
    # We need out_shape ~ 1/4 of base for fast reprojection
    # Use overview level 4 (16x reduction) or level 3 (8x)
    desired_reduction = max(1, src.width // (W * 2))  # Aim for ~2x canvas width for detail
    print(f'  Desired reduction factor: ~{desired_reduction}')
    
    best_ovr = None
    for ovr in overviews:
        if ovr >= desired_reduction:
            best_ovr = ovr
            break
    if best_ovr is None and overviews:
        best_ovr = overviews[-1]  # Use largest reduction available
    if best_ovr is None:
        best_ovr = desired_reduction  # Use out_shape resampling
    
    # Use OUT_SHAPE resampling: read at reduced resolution
    read_width = src.width // best_ovr if best_ovr else W * 2
    read_height = src.height // best_ovr if best_ovr else H * 2
    # Clamp
    read_width = max(W, min(src.width, read_width))
    read_height = max(H, min(src.height, read_height))
    
    # Read in one shot with OUT_SHAPE resampling
    print(f'  Reading DEM at resolution: {read_width}x{read_height} (via resampling)')
    dem_low = src.read(
        1,
        out_shape=(read_height, read_width),
        resampling=Resampling.bilinear
    )
    # Compute the transform for the reduced resolution read
    scale_x = src.width / read_width
    scale_y = src.height / read_height
    dem_transform = src.transform * src.transform.scale(scale_x, scale_y)
    dem_nodata = src.nodata if src.nodata is not None else -32767
    dem_crs = src.crs

print(f'  DEM loaded: shape={dem_low.shape}, range=[{dem_low.min():.0f}, {dem_low.max():.0f}]')

# ============================================================
# Step 2: Reproject low-res DEM
# ============================================================
print('\n[2/5] Reprojecting DEM to Albers canvas...')

# Use a canvas that's 1/2 size for speed
HALF = 2
hw, hh = W // HALF, H // HALF
half_px_size = PX_SIZE * HALF
htransform = rasterio.transform.from_origin(ALB_X_MIN, ALB_Y_MAX, half_px_size, half_px_size)

NODATA = -32767
dem_albers_low = np.full((hh, hw), NODATA, dtype=np.float32)
reproject(
    source=dem_low,
    destination=dem_albers_low,
    src_transform=dem_transform,
    src_crs=dem_crs,
    dst_transform=htransform,
    dst_crs=ALBERS_CRS,
    src_nodata=dem_nodata,
    dst_nodata=NODATA,
    resampling=Resampling.bilinear,
    num_threads=4
)
dem_low = None
print(f'  Albers low-res DEM: {dem_albers_low.shape}')

# Fill NODATA with 0 (sea level)
num_nodata = (dem_albers_low <= NODATA).sum()
print(f'  Filling {num_nodata} NODATA pixels with sea level...')
dem_albers_low[dem_albers_low <= NODATA] = 0.0

# Upsample to full resolution using PIL (fast bilinear interpolation)
print('\n[3/5] Upsampling to full resolution...')
# Scale DEM to uint16 for PIL transport
dem_scaled = ((np.clip(dem_albers_low, -6000, 8000) + 6000) / 14000 * 65535).astype(np.uint16)
dem_pil = Image.fromarray(dem_scaled, mode='I;16')
dem_full_pil = dem_pil.resize((W, H), Image.BILINEAR)
dem_full = ((np.array(dem_full_pil).astype(np.float64) / 65535) * 14000) - 6000
dem_scaled = None; dem_pil = None; dem_full_pil = None; dem_albers_low = None
print(f'  Full-res DEM: {dem_full.shape}, range=[{dem_full.min():.0f}, {dem_full.max():.0f}]')

# ============================================================
# Step 3: China land mask
# ============================================================
print('\n[4/5] Creating land mask...')
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

# Rasterize at half resolution then upsample
china_half = np.zeros((hh, hw), dtype=np.uint8)
cpil = Image.fromarray(china_half, mode='L')
cdraw = ImageDraw.Draw(cpil)

def hpx_to_px(x, y):
    return ((x - ALB_X_MIN) / half_px_size, (ALB_Y_MAX - y) / half_px_size)

def rgeom(g, d):
    if g.is_empty: return
    if g.geom_type in ('Polygon', 'MultiPolygon'):
        ps = [g] if g.geom_type == 'Polygon' else list(g.geoms)
        for p in ps:
            ext = []
            for x, y in p.exterior.coords:
                c, r = hpx_to_px(x, y); ext.append((c, r))
            if len(ext) >= 3:
                d.polygon(ext, fill=255, outline=255)
            for interior in p.interiors:
                ip = []
                for x, y in interior.coords:
                    c, r = hpx_to_px(x, y); ip.append((c, r))
                if len(ip) >= 3:
                    d.polygon(ip, fill=0)
    elif g.geom_type == 'GeometryCollection':
        for gg in g.geoms:
            rgeom(gg, d)

rgeom(china_union, cdraw)
china_full = np.array(Image.fromarray(np.array(cpil), mode='L').resize((W, H), Image.BILINEAR)) > 128
ocean_mask = ~china_full
print(f'  China land: {china_full.sum()}, Ocean/BG: {ocean_mask.sum()}')

# Read existing bg_dem.png
img = Image.open(OUT_BG)
orig_rgba = np.array(img).astype(np.float64)
orig_rgb = orig_rgba[:,:,:3].copy()
print(f'  Existing image: {orig_rgba.shape}')

# ============================================================
# Step 4: Hillshade + paper color ocean
# ============================================================
print('\n[5/5] Hillshade + paper-colored DEM texture...')

def hs_calc(dem, azim=320, alt=40, zf=1.2):
    dc = dem.copy() * zf
    dy, dx = np.gradient(dc, PX_SIZE, PX_SIZE)
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)
    azr = np.deg2rad(360 - azim + 90)
    altr = np.deg2rad(alt)
    return np.clip(np.sin(altr)*np.sin(slope)*np.cos(aspect-azr) + np.cos(altr)*np.cos(slope), 0, 1)

# Use ADDITIVE shading mode (not multiplicative)
# Base paper color, then ADD/Subtract delta based on hillshade
# This avoids clamping to 255 (previous bug with 237 × 1.18 = 280 > 255)

# Strong z_factors
hs_a = hs_calc(dem_full, 320, 38, 4.5)   # Main light
hs_b = hs_calc(dem_full, 335, 18, 7.5)   # Low-angle shadow
hs_c = hs_calc(dem_full, 140, 55, 2.0)   # Back fill
hs_d = hs_calc(dem_full, 50, 30, 6.0)    # Side detail

# Shadow map (strong, visible valleys)
shadow = np.clip((1.0 - hs_b) * 0.70 + (1.0 - hs_a) * 0.35 + (1.0 - hs_d) * 0.20, 0, 1)
shadow = np.power(shadow, 0.95)

# Highlight map (ridges and high points)
highlight = np.clip(hs_a * 0.70 + hs_d * 0.25 + hs_c * 0.10, 0, 1)
highlight = np.power(highlight, 0.70)

# Paper base color - warm off-white matching reference
# Use slightly lower base so we have headroom for highlights (don't hit 255 ceiling)
PAPER_R = 231.0
PAPER_G = 229.0
PAPER_B = 220.0

# ADDITIVE delta: -SHADOW_DELTA to +HIGHLIGHT_DELTA
# Target: ~20 units of dynamic range visible (std ~4-6 in large samples)
SHADOW_DELTA = 26.0
HIGHLIGHT_DELTA = 14.0

delta = highlight * HIGHLIGHT_DELTA - shadow * SHADOW_DELTA
delta = np.clip(delta, -SHADOW_DELTA, HIGHLIGHT_DELTA)
# Warm tint: shadows slightly cooler (less warm tint)
delta_r = delta * 0.95
delta_g = delta * 1.00
delta_b = delta * 1.05

ocean_rgb = np.zeros((H, W, 3), dtype=np.float64)
ocean_rgb[:,:,0] = PAPER_R + delta_r
ocean_rgb[:,:,1] = PAPER_G + delta_g
ocean_rgb[:,:,2] = PAPER_B + delta_b

# Very subtle back-fill light (so shadows aren't pitch black)
fill_amt = hs_c * 3.5
ocean_rgb[:,:,0] += fill_amt * 1.0
ocean_rgb[:,:,1] += fill_amt * 1.0
ocean_rgb[:,:,2] += fill_amt * 1.05

ocean_rgb = np.clip(ocean_rgb, 180, 255)

# Combine
final_rgb = np.where(np.stack([ocean_mask]*3, axis=-1), ocean_rgb, orig_rgb)
final_rgba = np.dstack([final_rgb, orig_rgba[:,:,3]])
final_rgba = np.clip(final_rgba, 0, 255).astype(np.uint8)

# ============================================================
# VERIFY
# ============================================================
print('\n=== VERIFY ===')
areas = [
    ('十段线南端', 2982, 3733),
    ('南海中部', 3023, 3800),
    ('赤道附近', 3073, 3900),
    ('中国华南', 2302, 3500),
    ('海南岛', 2523, 3630),
    ('远海样', 3400, 5500),
]
for name, r, c in areas:
    if 0 <= r < H and 0 <= c < W:
        o = orig_rgb[r,c,:3]
        n = final_rgb[r,c,:3]
        chn = china_full[r,c]
        # Texture in 11x11 patch
        r1, r2 = max(0,r-5), min(H,r+5)
        c1, c2 = max(0,c-5), min(W,c+5)
        s = final_rgb[r1:r2, c1:c2, :3]
        t = (np.std(s[:,:,0])+np.std(s[:,:,1])+np.std(s[:,:,2]))/3
        blu = n[2]>n[0]+2 and n[2]>n[1]+2
        print(f'  {name}: {"LAND" if chn else "OCEAN"} RGB({n[0]:.0f},{n[1]:.0f},{n[2]:.0f}) 纹理={t:.2f}{" ✗BLUE" if blu else " ✓PAPER"}')

o_sample = final_rgb[3200:3400, 4500:5000, :3]
o_std = (np.std(o_sample[:,:,0])+np.std(o_sample[:,:,1])+np.std(o_sample[:,:,2]))/3
print(f'\n  远海大样本 纹理std: {o_std:.2f} (纯纸色≈0, DEM纹理>1.0)')
blu_cnt = ((final_rgb[:,:,2]>final_rgb[:,:,0]+2)&(final_rgb[:,:,2]>final_rgb[:,:,1]+2)).sum()
print(f'  蓝色像素: {blu_cnt}/{W*H} ({blu_cnt/(W*H)*100:.3f}%)')

print(f'\nSaving → {OUT_BG}')
Image.fromarray(final_rgba, 'RGBA').save(OUT_BG, 'PNG', optimize=True)
print(f'DONE! File size: {os.path.getsize(OUT_BG):,} bytes')
