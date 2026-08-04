# -*- coding: utf-8 -*-
"""
图层对齐诊断
对照：dem.tif transform 与 渲染出的 dem_relief.png 的 bounds 是否一致
以及几个古茶树/唐代茶区的实际坐标应该落在中国的哪些地方。
"""
import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import json
import numpy as np
import rasterio
import geopandas as gpd
from PIL import Image

BASE = r'd:\Desktop\teamap\data\1'

with rasterio.open(BASE + r'\高程.tif') as dem:
    print('=== 高程.tif 原始 ===')
    print('crs:', dem.crs)
    print('count(bands):', dem.count)
    print('dtypes:', dem.dtypes)
    print('width, height:', dem.width, dem.height)
    print('bounds:', dem.bounds)  # (left, bottom, right, top)
    print('transform:')
    print(dem.transform)
    # transform 含义：
    # a = transform.a （pixel width, 经度每像素）
    # e = transform.e （pixel height, 通常负值，纬度每像素）
    # c = transform.c （左上角 x / 经度）
    # f = transform.f （左上角 y / 纬度）
    a, c, d, b, e, f = list(dem.transform)[:6]
    print(f'  a(width/col)={a:.8f}, b(row)= {b}')
    print(f'  c(ulx)= {c},  f(uly)={f}')
    print(f'  d= {d},  e(height/row neg)={e:.8f}')
    print()
    print('由此计算四角:')
    W = dem.width; H = dem.height
    ulx = c            ; uly = f
    urx = c + a*W      ; ury = f
    llx = c            ; lly = f + e*H
    lrx = c + a*W      ; lry = f + e*H
    print(f'  UL [{uly:.4f}, {ulx:.4f}] (lat,lon)')
    print(f'  UR [{ury:.4f}, {urx:.4f}]')
    print(f'  LL [{lly:.4f}, {llx:.4f}]')
    print(f'  LR [{lry:.4f}, {lrx:.4f}]')

    # 读取 PNG (6x downsample)
    arr = dem.read(1, masked=True)
    print()
    print('tif 数组 shape:', arr.shape, 'row, col → lat-row (top→bottom) , lon-col (left→right)')
    print('tif 左上角(0,0): pixel value =', arr[0, 0], ' → lat/lon ≈', uly, ulx)
    print('tif 右下角(-1,-1): pixel value =', arr[-1, -1], ' → lat/lon ≈', lry, lrx)

print()
print('=== dem_relief.png ===')
img = np.array(Image.open(BASE + r'\dem_relief.png'))
print('png shape:', img.shape, '(H,W,4)')
print('png 非零 alpha 的 bounding lat/lon（按原 bounds 推算）：')

# 原来渲染时用的是 dem bounds [[bottom,left],[top,right]]
# 我们要算 png (y=0 对应 top，y=H 对应 bottom)是否和 tif 一致
pngH, pngW = img.shape[:2]
alpha = img[:,:,3]
print(f'png alpha>0 最少列/最多列/最少行/最多行:')
rows, cols = np.where(alpha>0)
print(f'  rows {rows.min()} - {rows.max()}  (0=top, {pngH-1}=bottom)')
print(f'  cols {cols.min()} - {cols.max()}  (0=left, {pngW-1}=right)')

# 从 png 的行列反推地理坐标，看左下角的海南/台湾在哪
def px_to_ll(r, c):
    # 按原 bounds (来自 tif 的 bounds)
    south, north = 3.8291666666666515, 53.562499999999986
    west, east = 73.49583333333331, 135.08749999999998
    lat = north - (r / (pngH-1)) * (north - south)
    lon = west  + (c / (pngW-1)) * (east - west)
    return lat, lon

print()
r1,c1 = rows.min(), cols.min()
lat1, lon1 = px_to_ll(r1, c1)
print(f'png 左上角陆地 (row={r1}, col={c1})  lat={lat1:.2f} lon={lon1:.2f}')
r2,c2 = rows.max(), cols.max()
lat2, lon2 = px_to_ll(r2, c2)
print(f'png 右下角陆地 (row={r2}, col={c2})  lat={lat2:.2f} lon={lon2:.2f}')
# 找海南（≈18.3-20.1, 108.6-111）
print()
print('=== 点坐标与 DEM 定位对照 ===')
print('理论：')
print('  海南岛 lat 18~20, lon 108~111')
print('  北京  lat 39.9,  lon 116.4')
print('  成都  lat 30.7,  lon 104.1')
print('  上海  lat 31.2,  lon 121.5')
print('  拉萨  lat 29.65, lon 91.1')

trees = gpd.read_file(BASE + r'\Export_Output.shp')
print()
print('=== 古茶树 Export_Output 前3条 + 几个代表性点 ===')
print(trees[['茶树名','省份','x','y','种类']].head(10).to_string())
print()
print('北京附近点（北纬约39.8-40.6，lon≈116.1-117）:')
sub = trees[(trees.y.between(39.4, 40.8)) & (trees.x.between(115.5, 117.5))]
print(sub[['茶树名','x','y','省份']].to_string())
print()
print('海南附近点（北纬约18-20）:')
sub2 = trees[(trees.y.between(18, 21)) & (trees.x.between(108, 112))]
print(sub2[['茶树名','x','y','省份']].to_string())
