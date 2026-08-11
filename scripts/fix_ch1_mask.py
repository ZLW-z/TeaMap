# -*- coding: utf-8 -*-
"""
快速修复：重新生成遮罩层 (加入十段线缓冲区) + 优化海洋渲染
使用已缓存的 DEM 数组 (如果可用)
"""
import os
import json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import geopandas as gpd
from shapely.ops import unary_union
from shapely.validation import make_valid
from pyproj import CRS, Transformer

OUT_DIR = r'd:\Desktop\teamap\public\data\1'
CACHE_DIR = os.path.join(OUT_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# 矢量源
OUTLINE_SHP = r'D:\Desktop\数据\202405中国标准行政区划数据4\202405中国标准行政区划数据4\02_中国轮廓线\中国轮廓线.shp'
TENDASH_SHP = r'D:\Desktop\数据\202405中国标准行政区划数据4\202405中国标准行政区划数据4\02_中国轮廓线\十段线.shp'
PROVINCES_GEOJSON = r'd:\Desktop\teamap\public\data\1\china_provinces_background.geojson'

# CRS
ALBERS_PROJ4 = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
ALBERS_CRS = CRS.from_string(ALBERS_PROJ4)

# 画布参数 (与 process_ch1_global.py 一致)
ALB_X_MIN, ALB_X_MAX = -14320729, 9878377
ALB_Y_MIN, ALB_Y_MAX = -1771173, 12105913
CANVAS_W_M = ALB_X_MAX - ALB_X_MIN
CANVAS_H_M = ALB_Y_MAX - ALB_Y_MIN
TARGET_W = 6144
PX_SIZE = CANVAS_W_M / TARGET_W
TARGET_H = int(round(CANVAS_H_M / PX_SIZE))
W, H = TARGET_W, TARGET_H

print(f'画布: {W}x{H}px, 像元: {PX_SIZE:.0f}m')

def albers_to_px(x_m, y_m):
    col = (x_m - ALB_X_MIN) / PX_SIZE
    row = (ALB_Y_MAX - y_m) / PX_SIZE
    return col, row

def rasterize_geom_to_draw(gdf_obj, pil_draw, dx_col=0, dy_row=0, value=255):
    def ring_to_poly(ring):
        poly = []
        for x_m, y_m in ring.coords:
            c, r = albers_to_px(x_m, y_m)
            poly.append((c + dx_col, r + dy_row))
        if len(poly) >= 3:
            pil_draw.polygon(poly, fill=value, outline=value)
    for geom in gdf_obj.geometry:
        if geom.geom_type == 'Polygon':
            ring_to_poly(geom.exterior)
            for interior in geom.interiors:
                poly = []
                for x_m, y_m in interior.coords:
                    c, r = albers_to_px(x_m, y_m)
                    poly.append((c + dx_col, r + dy_row))
                if len(poly) >= 3:
                    pil_draw.polygon(poly, fill=0)
        elif geom.geom_type == 'MultiPolygon':
            for p in geom.geoms:
                ring_to_poly(p.exterior)
                for interior in p.interiors:
                    poly = []
                    for x_m, y_m in interior.coords:
                        c, r = albers_to_px(x_m, y_m)
                        poly.append((c + dx_col, r + dy_row))
                    if len(poly) >= 3:
                        pil_draw.polygon(poly, fill=0)

# ============================================================
# 1. 加载/生成 DEM 缓存
# ============================================================
bg_cache = os.path.join(CACHE_DIR, 'bg_arr.npy')
cn_cache = os.path.join(CACHE_DIR, 'cn_arr.npy')

if os.path.exists(bg_cache) and os.path.exists(cn_cache):
    print('[1/5] 加载缓存的 DEM 数据...')
    bg_arr = np.load(bg_cache)
    cn_arr = np.load(cn_cache)
    print(f'  bg_arr: {bg_arr.shape}, range=[{bg_arr.min():.0f}, {bg_arr.max():.0f}]')
    print(f'  cn_arr: {cn_arr.shape}, range=[{cn_arr.min():.0f}, {cn_arr.max():.0f}]')
else:
    print('[1/5] 缓存不存在，需要先运行完整的 process_ch1_global.py 生成缓存')
    print('  正在运行完整处理脚本...')
    # 如果没有缓存，就运行完整脚本
    import subprocess
    result = subprocess.run(
        ['python', 'scripts/process_ch1_global.py'],
        capture_output=True, text=True, cwd=r'd:\Desktop\teamap',
        timeout=600
    )
    print(result.stdout[-500:] if result.stdout else 'No output')
    if result.returncode != 0:
        print(f'Error: {result.stderr}')
        exit(1)
    print('  完整处理脚本已完成，现在请重新运行此脚本')
    exit(0)

# ============================================================
# 2. 填充 NODATA 为海平面
# ============================================================
print('\n[2/5] 填充 NODATA 值为海平面 (0m)...')
NODATA = -32767
bg_nodata = bg_arr <= NODATA
cn_nodata = cn_arr <= NODATA
print(f'  bg NODATA 像素: {bg_nodata.sum()}')
print(f'  cn NODATA 像素: {cn_nodata.sum()}')
bg_arr[bg_nodata] = 0.0
cn_arr[cn_nodata] = 0.0

# ============================================================
# 3. 更新遮罩 (加入十段线缓冲区)
# ============================================================
print('\n[3/5] 重新生成遮罩 (加入十段线缓冲区)...')
gdf_prov = gpd.read_file(PROVINCES_GEOJSON)
gdf_prov_alb = gdf_prov.to_crs(ALBERS_CRS)

fixed_geoms = []
for g in gdf_prov_alb.geometry.tolist():
    try:
        if not g.is_valid:
            g = make_valid(g)
        fixed_geoms.append(g.buffer(0) if not g.is_empty else g)
    except Exception:
        try:
            fixed_geoms.append(g.buffer(0))
        except Exception:
            pass
china_union = unary_union(fixed_geoms)

# 加入十段线缓冲区 (100km)
print('  加载十段线并缓冲...')
gdf_tendash = gpd.read_file(TENDASH_SHP)
gdf_tendash_alb = gdf_tendash.to_crs(ALBERS_CRS)
tendash_buffered = gdf_tendash_alb.geometry.buffer(100000)
china_union = unary_union([china_union, unary_union(tendash_buffered)])

gdf_china = gpd.GeoDataFrame(geometry=[china_union], crs=ALBERS_CRS)

# 栅格化遮罩
china_mask = np.zeros((H, W), dtype=np.uint8)
mask_pil = Image.fromarray(china_mask, mode='L')
draw = ImageDraw.Draw(mask_pil)
rasterize_geom_to_draw(gdf_china, draw, 0, 0, 255)
china_bool = np.array(mask_pil) > 128

print(f'  中国遮罩像素: {china_bool.sum()} / {W*H}')

# 保存更新后的 mask_outside.png
print('  保存 mask_outside.png...')
mask_rgba = np.zeros((H, W, 4), dtype=np.uint8)
outside = ~china_bool
mask_rgba[outside, 0] = 255
mask_rgba[outside, 1] = 255
mask_rgba[outside, 2] = 255
mask_rgba[outside, 3] = 170
alp = Image.fromarray(mask_rgba[:, :, 3], mode='L')
alp = alp.filter(ImageFilter.GaussianBlur(radius=2.5))
mask_rgba[:, :, 3] = np.array(alp)
Image.fromarray(mask_rgba, 'RGBA').save(os.path.join(OUT_DIR, 'mask_outside.png'), 'PNG', optimize=True)
mask_rgba = None

# ============================================================
# 4. Hillshade 计算 (使用缓存的数据)
# ============================================================
print('\n[4/5] 计算 Hillshade...')

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

bg_land = bg_arr > 0
bg_ocean = (bg_arr < 0)
bg_valid = np.ones_like(bg_arr, dtype=bool)  # All valid after filling

cn_land = cn_arr > 0
cn_ocean = (cn_arr < 0)
cn_valid = np.ones_like(cn_arr, dtype=bool)

# 全球背景 DEM hillshade
bg_intensity, bg_shadow, bg_highlight = multi_layer_hillshade(
    bg_arr, bg_valid, PX_X_M, PX_Y_M,
    main_azim=320, main_alt=38,
    z_factor_main=1.3, z_factor_detail=2.5
)

# 中国 DEM hillshade
cn_intensity, cn_shadow, cn_highlight = multi_layer_hillshade(
    cn_arr, cn_valid, PX_X_M, PX_Y_M,
    main_azim=320, main_alt=36,
    z_factor_main=2.2, z_factor_detail=4.8
)
hs_cn_extreme = compute_hillshade(cn_arr, cn_valid, PX_X_M, PX_Y_M,
                                  azimuth_deg=320, altitude_deg=30, z_factor=8.0)
cn_shadow = np.clip(cn_shadow * 0.75 + (1.0 - hs_cn_extreme) * 0.25, 0, 1)
cn_highlight = np.clip(cn_highlight * 0.80 + hs_cn_extreme * 0.20, 0, 1)
cn_intensity = 0.50 - cn_shadow * 0.62 + cn_highlight * 0.58
cn_intensity = np.clip(cn_intensity, 0.20, 1.40)

# ============================================================
# 5. 渲染 (全球背景 + 中国 DEM)
# ============================================================
print('\n[5/5] 渲染 DEM 图片...')

# --- 5a. 全球背景 DEM (带深度分层海洋渲染) ---
t_bg = np.clip(bg_arr / 7000.0, 0, 1)
bgc = np.zeros((H, W, 3), dtype=np.float64)

# 陆地渲染
s1 = bg_land & (t_bg < 0.07)
k1 = np.clip(t_bg[s1] / 0.07, 0, 1)
bgc[s1, 0] = 220 + (234 - 220) * k1
bgc[s1, 1] = 228 + (232 - 228) * k1
bgc[s1, 2] = 224 + (225 - 224) * k1

s2 = bg_land & (t_bg >= 0.07) & (t_bg < 0.22)
k2 = np.clip((t_bg[s2] - 0.07) / 0.15, 0, 1)
bgc[s2, 0] = 234 + (228 - 234) * k2
bgc[s2, 1] = 232 + (222 - 232) * k2
bgc[s2, 2] = 225 + (205 - 225) * k2

s3 = bg_land & (t_bg >= 0.22) & (t_bg < 0.5)
k3 = np.clip((t_bg[s3] - 0.22) / 0.28, 0, 1)
bgc[s3, 0] = 228 + (226 - 228) * k3
bgc[s3, 1] = 222 + (221 - 222) * k3
bgc[s3, 2] = 205 + (211 - 205) * k3

s4 = bg_land & (t_bg >= 0.5)
k4 = np.clip((t_bg[s4] - 0.5) / 0.5, 0, 1)
bgc[s4, 0] = 226 + (242 - 226) * k4
bgc[s4, 1] = 221 + (239 - 221) * k4
bgc[s4, 2] = 211 + (233 - 211) * k4

# 海洋: 深度分层渲染
ocean_shallow = bg_ocean & (bg_arr >= -200)
if ocean_shallow.any():
    ot = np.clip((-bg_arr[ocean_shallow]) / 200.0, 0, 1)
    bgc[ocean_shallow, 0] = 214 + (198 - 214) * ot
    bgc[ocean_shallow, 1] = 224 + (218 - 224) * ot
    bgc[ocean_shallow, 2] = 228 + (222 - 228) * ot

ocean_mid = bg_ocean & (bg_arr < -200) & (bg_arr >= -1500)
if ocean_mid.any():
    ot = np.clip((-bg_arr[ocean_mid] - 200) / 1300.0, 0, 1)
    bgc[ocean_mid, 0] = 198 + (174 - 198) * ot
    bgc[ocean_mid, 1] = 218 + (206 - 218) * ot
    bgc[ocean_mid, 2] = 222 + (218 - 222) * ot

ocean_deep = bg_ocean & (bg_arr < -1500) & (bg_arr >= -4000)
if ocean_deep.any():
    ot = np.clip((-bg_arr[ocean_deep] - 1500) / 2500.0, 0, 1)
    bgc[ocean_deep, 0] = 174 + (138 - 174) * ot
    bgc[ocean_deep, 1] = 206 + (174 - 206) * ot
    bgc[ocean_deep, 2] = 218 + (198 - 218) * ot

ocean_abyss = bg_ocean & (bg_arr < -4000)
if ocean_abyss.any():
    ot = np.clip(np.minimum((-bg_arr[ocean_abyss] - 4000) / 3000.0, 1.0), 0, 1)
    bgc[ocean_abyss, 0] = 138 + (108 - 138) * ot
    bgc[ocean_abyss, 1] = 174 + (144 - 174) * ot
    bgc[ocean_abyss, 2] = 198 + (176 - 198) * ot

# 光照增强
intensity_b_3c = np.stack([bg_intensity] * 3, axis=-1)
bg_final = bgc * intensity_b_3c
shadow_rgb = np.zeros((H, W, 3), dtype=np.float64)
shadow_rgb[:, :, 0] = 30; shadow_rgb[:, :, 1] = 40; shadow_rgb[:, :, 2] = 55
sh_3c = np.stack([bg_shadow] * 3, axis=-1)
bg_final = bg_final * (1 - sh_3c * 0.55) + shadow_rgb * sh_3c * 0.55
hl_rgb = np.zeros((H, W, 3), dtype=np.float64)
hl_rgb[:, :, 0] = 255; hl_rgb[:, :, 1] = 248; hl_rgb[:, :, 2] = 228
hl_3c = np.stack([bg_highlight] * 3, axis=-1)
bg_final = bg_final * (1 - hl_3c * 0.18) + hl_rgb * hl_3c * 0.25

bg_final_uint8 = np.clip(bg_final, 0, 255).astype(np.uint8)
bg_rgba = np.dstack([bg_final_uint8, np.full((H, W), 255, dtype=np.uint8)])
Image.fromarray(bg_rgba, 'RGBA').save(os.path.join(OUT_DIR, 'bg_dem.png'), 'PNG', optimize=True)
print('  保存 bg_dem.png ✓')
bg_rgba = None; bgc = None; bg_final_uint8 = None; bg_final = None

# --- 5b. 中国 DEM 主图 ---
cn_show_land = china_bool & cn_land
cn_show_ocean = china_bool & cn_ocean
cn_fallback = china_bool & (~cn_valid | cn_arr <= NODATA)

cn_filled = cn_arr.copy()
cn_filled[cn_fallback] = bg_arr[cn_fallback]
tc = np.clip(cn_filled / 7000.0, 0, 1)

crc = np.zeros((H, W, 3), dtype=np.float64)

# 段1-6: 陆地色带
s1 = cn_show_land & (tc < 0.03)
k1 = np.clip(tc[s1] / 0.03, 0, 1)
crc[s1, 0] = 180 + (202 - 180) * k1
crc[s1, 1] = 207 + (216 - 207) * k1
crc[s1, 2] = 194 + (198 - 194) * k1

s2 = cn_show_land & (tc >= 0.03) & (tc < 0.115)
k2 = np.clip((tc[s2] - 0.03) / 0.085, 0, 1)
crc[s2, 0] = 202 + (220 - 202) * k2
crc[s2, 1] = 216 + (216 - 216) * k2
crc[s2, 2] = 198 + (179 - 198) * k2

s3 = cn_show_land & (tc >= 0.115) & (tc < 0.26)
k3 = np.clip((tc[s3] - 0.115) / 0.145, 0, 1)
crc[s3, 0] = 220 + (206 - 220) * k3
crc[s3, 1] = 216 + (188 - 216) * k3
crc[s3, 2] = 179 + (141 - 179) * k3

s4 = cn_show_land & (tc >= 0.26) & (tc < 0.5)
k4 = np.clip((tc[s4] - 0.26) / 0.24, 0, 1)
crc[s4, 0] = 206 + (189 - 206) * k4
crc[s4, 1] = 188 + (141 - 188) * k4
crc[s4, 2] = 141 + (119 - 141) * k4

s5 = cn_show_land & (tc >= 0.5) & (tc < 0.78)
k5 = np.clip((tc[s5] - 0.5) / 0.28, 0, 1)
crc[s5, 0] = 189 + (240 - 189) * k5
crc[s5, 1] = 141 + (233 - 141) * k5
crc[s5, 2] = 119 + (223 - 119) * k5

s6 = cn_show_land & (tc >= 0.78)
crc[s6] = [247, 242, 232]

# 中国海洋渲染 (增强版)
crc[cn_show_ocean] = [198, 215, 220]

# Fallback
if cn_fallback.any():
    tf = np.clip(bg_arr / 7000.0, 0, 1)
    fbg = np.zeros((H, W, 3), dtype=np.float64)
    for seg, (t_lo, t_hi, col_lo, col_hi) in enumerate([
        (0, 0.07, (220,228,224), (234,232,225)),
        (0.07, 0.22, (234,232,225), (228,222,205)),
        (0.22, 0.5, (228,222,205), (226,221,211)),
        (0.5, 1.0, (226,221,211), (242,239,233)),
    ]):
        fs = cn_fallback & bg_land & (tf >= t_lo) & (tf < t_hi)
        if fs.any():
            fk = np.clip((tf[fs] - t_lo) / (t_hi - t_lo), 0, 1)
            fbg[fs, 0] = col_lo[0] + (col_hi[0] - col_lo[0]) * fk
            fbg[fs, 1] = col_lo[1] + (col_hi[1] - col_lo[1]) * fk
            fbg[fs, 2] = col_lo[2] + (col_hi[2] - col_lo[2]) * fk
    fbg[cn_fallback & bg_ocean] = [224, 228, 232]
    crc[cn_fallback] = fbg[cn_fallback]

# 外部透明
crc[~china_bool] = 0

# 光照增强
cn_3c = np.stack([cn_intensity] * 3, axis=-1)
cn_final = crc * cn_3c
cn_sh_rgb = np.zeros((H, W, 3), dtype=np.float64)
cn_sh_rgb[:, :, 0] = 22; cn_sh_rgb[:, :, 1] = 30; cn_sh_rgb[:, :, 2] = 48
cn_sh_3c = np.stack([cn_shadow] * 3, axis=-1)
cn_final = cn_final * (1 - cn_sh_3c * 0.72) + cn_sh_rgb * cn_sh_3c * 0.72
cn_hl_rgb = np.zeros((H, W, 3), dtype=np.float64)
cn_hl_rgb[:, :, 0] = 255; cn_hl_rgb[:, :, 1] = 250; cn_hl_rgb[:, :, 2] = 232
cn_hl_3c = np.stack([cn_highlight] * 3, axis=-1)
cn_final = cn_final * (1 - cn_hl_3c * 0.15) + cn_hl_rgb * cn_hl_3c * 0.32
cn_final_uint8 = np.clip(cn_final, 0, 255).astype(np.uint8)

china_alpha = np.where(china_bool, 255, 0).astype(np.uint8)

# 下沉投影
shadow_dx_col = 8
shadow_dy_row = 9
shadow_blur = 7
shadow_a_max = 175
shadow_rgb_v = (42, 38, 34)

sh_pil = Image.new('L', (W, H), 0)
sh_draw = ImageDraw.Draw(sh_pil)
rasterize_geom_to_draw(gdf_china, sh_draw, shadow_dx_col, shadow_dy_row, 255)
sh_pil = sh_pil.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
sh_mask_np = np.array(sh_pil).astype(np.float64) / 255.0

shadow_rgba = np.zeros((H, W, 4), dtype=np.uint8)
shadow_rgba[:, :, 0] = (shadow_rgb_v[0] * sh_mask_np).astype(np.uint8)
shadow_rgba[:, :, 1] = (shadow_rgb_v[1] * sh_mask_np).astype(np.uint8)
shadow_rgba[:, :, 2] = (shadow_rgb_v[2] * sh_mask_np).astype(np.uint8)
shadow_rgba[:, :, 3] = (shadow_a_max * sh_mask_np).astype(np.uint8)

china_rgba_full = np.dstack([cn_final_uint8, china_alpha])
b_img = Image.fromarray(shadow_rgba, 'RGBA')
t_img = Image.fromarray(china_rgba_full, 'RGBA')
b_img.alpha_composite(t_img)
final_rgba = np.array(b_img)

Image.fromarray(final_rgba, 'RGBA').save(os.path.join(OUT_DIR, 'dem_relief.png'), 'PNG', optimize=True)
print('  保存 dem_relief.png ✓')

# 同时保存缓存
print('\n保存缓存数据...')
np.save(bg_cache, bg_arr)
np.save(cn_cache, cn_arr)
print(f'  缓存已保存到 {CACHE_DIR}')

print('\n✅ 完成!')
