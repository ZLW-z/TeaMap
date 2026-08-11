# -*- coding: utf-8 -*-
"""
快速修复：重新生成 mask_outside.png (加入十段线缓冲区)
这解决十段线南部区域被白色遮罩覆盖的问题
无需 DEM 数据，仅处理矢量数据和遮罩
"""
import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import geopandas as gpd
from shapely.ops import unary_union
from shapely.validation import make_valid
from pyproj import CRS

OUT_DIR = r'd:\Desktop\teamap\public\data\1'
OUT_MASK = os.path.join(OUT_DIR, 'mask_outside.png')

# 矢量源
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
print(f'输出: {OUT_MASK}')

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
# 1. 加载中国省份数据
# ============================================================
print('\n[1/4] 加载中国省份数据...')
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
print(f'  中国省份联合面积: {china_union.area:.0f} m²')

# ============================================================
# 2. 加载十段线并生成缓冲区
# ============================================================
print('\n[2/4] 加载十段线并生成缓冲区 (100km)...')
gdf_tendash = gpd.read_file(TENDASH_SHP)
print(f'  十段线要素数: {len(gdf_tendash)}')

gdf_tendash_alb = gdf_tendash.to_crs(ALBERS_CRS)
tendash_buffered = gdf_tendash_alb.geometry.buffer(100000)  # 100km 缓冲
tendash_union = unary_union(tendash_buffered)
print(f'  十段线缓冲面积: {tendash_union.area:.0f} m²')

# 合并到中国
china_union = unary_union([china_union, tendash_union])
gdf_china = gpd.GeoDataFrame(geometry=[china_union], crs=ALBERS_CRS)
print(f'  合并后总面积: {china_union.area:.0f} m²')

# ============================================================
# 3. 栅格化遮罩
# ============================================================
print('\n[3/4] 栅格化遮罩...')
mask_arr = np.zeros((H, W), dtype=np.uint8)
mask_pil = Image.fromarray(mask_arr, mode='L')
draw = ImageDraw.Draw(mask_pil)
rasterize_geom_to_draw(gdf_china, draw, 0, 0, 255)
china_bool = np.array(mask_pil) > 128
print(f'  遮罩内像素 (中国+十段线): {china_bool.sum()} / {W*H} ({china_bool.sum()/(W*H)*100:.1f}%)')

# 检查十段线区域是否在遮罩内
col, row = albers_to_px(372915, 299040)  # 十段线南端
in_mask = china_bool[int(row), int(col)]
print(f'  十段线南端 pixel=({int(col)},{int(row)}), 在遮罩内: {in_mask}')

# ============================================================
# 4. 保存 mask_outside.png
# ============================================================
print('\n[4/4] 保存 mask_outside.png...')
mask_rgba = np.zeros((H, W, 4), dtype=np.uint8)
outside = ~china_bool
mask_rgba[outside, 0] = 255
mask_rgba[outside, 1] = 255
mask_rgba[outside, 2] = 255
mask_rgba[outside, 3] = 170  # 67% 透明度

# 高斯模糊边缘
alp = Image.fromarray(mask_rgba[:, :, 3], mode='L')
alp = alp.filter(ImageFilter.GaussianBlur(radius=2.5))
mask_rgba[:, :, 3] = np.array(alp)

Image.fromarray(mask_rgba, 'RGBA').save(OUT_MASK, 'PNG', optimize=True)
print(f'  已保存: {OUT_MASK}')
print(f'  文件大小: {os.path.getsize(OUT_MASK)/1024:.0f}KB')

# 验证结果
print('\n=== 验证 ===')
verify_mask = np.array(Image.open(OUT_MASK))
verify_alpha = verify_mask[:, :, 3]
print(f'  透明像素 (中国+十段线): {(verify_alpha == 0).sum()} / {verify_alpha.size}')
print(f'  半透明像素 (外部): {(verify_alpha > 0).sum()} / {verify_alpha.size}')

# 检查十段线南端的 alpha
alpha_at_td = verify_alpha[int(row), int(col)]
print(f'  十段线南端 alpha: {alpha_at_td} (应为 0 = 透明)')
if alpha_at_td == 0:
    print('  ✅ 十段线区域不再被白色遮罩覆盖!')
else:
    print('  ❌ 十段线区域仍有遮罩，请检查')

print('\n✅ 遮罩修复完成!')
