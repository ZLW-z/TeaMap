# -*- coding: utf-8 -*-
"""
快速修复: 为海洋区域添加DEM地形纹理 (纸色调)
方法:
  1. 使用rasterio窗口读取, 只读取需要的南海+周边地理窗口 (WGS84)
  2. 重投影到Albers画布
  3. 计算hillshade, 应用纸色底图 + 地形光照
  4. 与原有陆地部分合并
速度优化: 只读需要的地理窗口, 不读全球5.7GB全部
"""
import os
import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = 900_000_000
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.windows import from_bounds as window_from_bounds
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
albers_to_ll = Transformer.from_crs(ALBERS_CRS, EPSG4326, always_xy=True)

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
print(f'Geographic bounds: lon[{LON_MIN_GEO}, {LON_MAX_GEO}], lat[{LAT_MIN_GEO}, {LAT_MAX_GEO}]')

# ============================================================
# Step 1: Read existing bg_dem.png
# ============================================================
print('\n[1/5] Reading existing bg_dem.png...')
img = Image.open(OUT_BG)
orig_rgba = np.array(img).astype(np.float64)
orig_rgb = orig_rgba[:,:,:3].copy()
print(f'  Shape: {orig_rgba.shape}')

# ============================================================
# Step 2: Fast DEM read using WINDOWED READ (only read needed geographic area)
# ============================================================
print('\n[2/5] Windowed read of global DEM (only needed area)...')

with rasterio.open(GLOBAL_TIF) as src:
    print(f'  Source: {src.width}x{src.height}, CRS={src.crs}')
    
    # Create window for our geographic bounds (with 2° buffer for safety)
    try:
        win = window_from_bounds(
            LON_MIN_GEO - 2, LAT_MIN_GEO - 2,
            LON_MAX_GEO + 2, LAT_MAX_GEO + 2,
            src.transform
        )
        # Round to integers
        from rasterio.windows import Window
        win = Window(
            col_off=int(max(0, win.col_off)),
            row_off=int(max(0, win.row_off)),
            width=min(int(win.width + 1), src.width - int(max(0, win.col_off))),
            height=min(int(win.height + 1), src.height - int(max(0, win.row_off)))
        )
        
        # Read only the windowed region!
        print(f'  Window: rows[{win.row_off}, {win.row_off + win.height}], cols[{win.col_off}, {win.col_off + win.width}]')
        print(f'  Window size: {win.width}x{win.height} = {win.width*win.height/1000000:.1f} MPix')
        src_data = src.read(1, window=win, boundless=True, fill_value=-32767)
        src_transform = src.window_transform(win)
        src_nodata = src.nodata if src.nodata is not None else -32767
        src_crs = src.crs
        
    except Exception as e:
        print(f'  Windowed read failed ({e}), falling back to full read with lower res...')
        # Alternative: use overview level if available
        src_data = src.read(1, out_shape=(src.height // 4, src.width // 4))
        src_transform = src.transform * src.transform.scale(
            (src.width / src_data.shape[-1]),
            (src.height / src_data.shape[-2])
        )
        src_nodata = src.nodata if src.nodata is not None else -32767
        src_crs = src.crs

print(f'  Source data shape: {src_data.shape}, range=[{np.nanmin(src_data):.0f}, {np.nanmax(src_data):.0f}]')

# ============================================================
# Step 3: Reproject windowed DEM to Albers canvas
# ============================================================
print('\n[3/5] Reprojecting windowed DEM to Albers canvas...')
NODATA = -32767

# Use moderate resolution: half of full
HALF_DIV = 2
half_w = W // HALF_DIV
half_h = H // HALF_DIV
half_px = PX_SIZE * HALF_DIV
half_transform = rasterio.transform.from_origin(ALB_X_MIN, ALB_Y_MAX, half_px, half_px)

half_dem = np.full((half_h, half_w), NODATA, dtype=np.float32)
reproject(
    source=src_data,
    destination=half_dem,
    src_transform=src_transform,
    src_crs=src_crs,
    dst_transform=half_transform,
    dst_crs=ALBERS_CRS,
    src_nodata=src_nodata,
    dst_nodata=NODATA,
    resampling=Resampling.bilinear,
    num_threads=4
)
src_data = None  # Free memory

print(f'  Half-res DEM: {half_dem.shape}')

# Fill NODATA with sea level 0
nodata_count = (half_dem <= NODATA).sum()
print(f'  Filling {nodata_count} NODATA pixels with sea level (0m)...')
half_dem[half_dem <= NODATA] = 0.0

# Upsample to full resolution for hillshade calculation
half_dem_scaled = ((np.clip(half_dem, -6000, 8000) + 6000) / 14000 * 65535).astype(np.uint16)
half_pil = Image.fromarray(half_dem_scaled, mode='I;16')
full_pil = half_pil.resize((W, H), Image.BILINEAR)
full_dem = ((np.array(full_pil).astype(np.float64) / 65535) * 14000) - 6000
half_dem_scaled = None; half_pil = None; full_pil = None
print(f'  Full-res DEM: {full_dem.shape}')

# ============================================================
# Step 4: Compute hillshade and render paper-colored terrain
# ============================================================
print('\n[4/5] Computing hillshade, rendering paper-textured ocean...')

# China land mask (from provinces)
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

# Rasterize China mask at half resolution, then upsample
china_half = np.zeros((half_h, half_w), dtype=np.uint8)
ch_pil = Image.fromarray(china_half, mode='L')
ch_draw = ImageDraw.Draw(ch_pil)

def hpx(x_m, y_m):
    return ((x_m - ALB_X_MIN) / half_px, (ALB_Y_MAX - y_m) / half_px)

def draw_hgeom(geom, d):
    if geom.is_empty:
        return
    if geom.geom_type in ('Polygon', 'MultiPolygon'):
        polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
        for p in polys:
            ext = []
            for x_m, y_m in p.exterior.coords:
                c, r = hpx(x_m, y_m); ext.append((c, r))
            if len(ext) >= 3:
                d.polygon(ext, fill=255, outline=255)
            for interior in p.interiors:
                poly_int = []
                for x_m, y_m in interior.coords:
                    c, r = hpx(x_m, y_m); poly_int.append((c, r))
                if len(poly_int) >= 3:
                    d.polygon(poly_int, fill=0)
    elif geom.geom_type == 'GeometryCollection':
        for g in geom.geoms:
            draw_hgeom(g, d)

draw_hgeom(china_union, ch_draw)
china_full = np.array(Image.fromarray(np.array(ch_pil), mode='L').resize((W, H), Image.BILINEAR)) > 128
print(f'  China land pixels: {china_full.sum()}')

# Everything OUTSIDE China = "ocean/background" (needs DEM texture in paper color)
ocean_mask = ~china_full

# Compute hillshade
PX_X_M = PX_SIZE
PX_Y_M = PX_SIZE

def compute_hs(dem, azim=320, alt=40, zf=1.0):
    vmask = np.ones_like(dem, dtype=bool)
    dem_c = dem.copy()
    dem_c[~vmask] = 0
    dem_c[vmask] *= zf
    dy, dx = np.gradient(dem_c, PX_Y_M, PX_X_M)
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)
    azr = np.deg2rad(360 - azim + 90)
    altr = np.deg2rad(alt)
    hs = np.sin(altr)*np.sin(slope)*np.cos(aspect-azr) + np.cos(altr)*np.cos(slope)
    return np.clip(hs, 0, 1)

# Main light
hs1 = compute_hs(full_dem, 320, 38, 1.2)
# Low-angle light for subtle shadows
hs2 = compute_hs(full_dem, 335, 22, 1.8)

shadow_map = np.clip((1.0 - hs2) * 0.45 + (1.0 - hs1) * 0.25, 0, 1)
highlight_map = np.clip(hs1 * 0.65 + hs2 * 0.20, 0, 1)

# MILD intensity: range [0.88, 1.08] — keeps a paper look with terrain texture visible
ocean_intensity = 0.97 - shadow_map * 0.14 + highlight_map * 0.09
ocean_intensity = np.clip(ocean_intensity, 0.85, 1.09)

# Warm paper base color — matches the user's reference image (slightly warm off-white)
PAPER_R = 238.0
PAPER_G = 236.0
PAPER_B = 227.0

oi3 = np.stack([ocean_intensity] * 3, axis=-1)
ocean_rgb = np.zeros((H, W, 3), dtype=np.float64)
ocean_rgb[:,:,0] = PAPER_R * oi3[:,:,0]
ocean_rgb[:,:,1] = PAPER_G * oi3[:,:,1]
ocean_rgb[:,:,2] = PAPER_B * oi3[:,:,2]
ocean_rgb = np.clip(ocean_rgb, 210, 255)

# Combine: keep China land as-is, replace ocean with paper-colored DEM texture
final_rgb = orig_rgb.copy()
ocean_3d = np.stack([ocean_mask] * 3, axis=-1)
final_rgb = np.where(ocean_3d, ocean_rgb, final_rgb)

final_rgba = np.dstack([final_rgb, orig_rgba[:,:,3]])
final_rgba = np.clip(final_rgba, 0, 255).astype(np.uint8)

# ============================================================
# VERIFY
# ============================================================
print('\n[5/5] VERIFY:')

areas = [
    ('十段线南端', 2982, 3733),
    ('南海中部', 3023, 3800),
    ('赤道附近', 3073, 3900),
    ('中国华南', 2302, 3500),
    ('海南岛', 2523, 3630),
    ('台湾以东', 2700, 4800),
    ('远海区域', 3400, 5500),
]
for name, row, col in areas:
    if 0 <= row < H and 0 <= col < W:
        orig_p = orig_rgb[row, col, :3]
        new_p = final_rgb[row, col, :3]
        is_china = china_full[row, col]
        # Sample 11x11 area texture
        r1, r2 = max(0,row-5), min(H,row+5)
        c1, c2 = max(0,col-5), min(W,col+5)
        sample = final_rgb[r1:r2, c1:c2, :3]
        std_r = np.std(sample[:,:,0])
        std_g = np.std(sample[:,:,1])
        std_b = np.std(sample[:,:,2])
        texture = (std_r + std_g + std_b) / 3
        is_blue = new_p[2] > new_p[0]+2 and new_p[2] > new_p[1]+2
        print(f'  {name}: 类型={"LAND" if is_china else "OCEAN/BG"} RGB({new_p[0]:.0f},{new_p[1]:.0f},{new_p[2]:.0f}) 纹理std={texture:.2f}{" 有DEM纹理" if texture>1.2 else " 纯/弱"} {"← BLUE!" if is_blue else "✓"}')

# Large-sample ocean texture
os_s = final_rgb[3200:3400, 4500:5000, :3]
ostd = (np.std(os_s[:,:,0]) + np.std(os_s[:,:,1]) + np.std(os_s[:,:,2])) / 3
print(f'\n  远海大样本地形纹理 std: {ostd:.2f} (参考: 纯纸色≈0, 有DEM纹理>1)')

blue_cnt = ((final_rgb[:,:,2] > final_rgb[:,:,0]+2) & (final_rgb[:,:,2] > final_rgb[:,:,1]+2)).sum()
print(f'  蓝色像素数: {blue_cnt} / {W*H} ({blue_cnt/(W*H)*100:.3f}%)')

# Save
print(f'\n  Saving → {OUT_BG}')
Image.fromarray(final_rgba, 'RGBA').save(OUT_BG, 'PNG', optimize=True)
print(f'Done! Size: {os.path.getsize(OUT_BG):,} bytes')
