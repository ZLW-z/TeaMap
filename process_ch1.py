# -*- coding: utf-8 -*-
"""
第一章数据处理
 1) DEM 高程 → 晕渲地形图 PNG（山水底图）
 2) 唐代产茶区点 → 模糊边界密度图 PNG（模糊晕染）
 3) 古茶树点 → GeoJSON（三型分色，类型为暂定地理分组，待真实属性确认）
输出：
  data/1/dem_relief.png
  data/1/tang_density.png
  data/1/dem_bounds.js   (DEM_BOUNDS / DEM_IMG / TANG_BOUNDS / TANG_IMG)
  data/1/tea_trees.js    (TEA_TREES)
"""
import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
import rasterio
from scipy.ndimage import gaussian_filter
import geopandas as gpd

BASE = r'd:\Desktop\teamap\data\1'

# ===================================================================
# 1) DEM 高程 → 晕渲地形图
# ===================================================================
print('[1/3] 处理 DEM ...')
with rasterio.open(BASE + r'\高程.tif') as dem:
    full = dem.read(1)
    b = dem.bounds
    bounds = [[b.bottom, b.left], [b.top, b.right]]
    print('  full shape', full.shape, 'bounds', bounds)

# 降采样
fac = 6
arr = full[::fac, ::fac].astype(np.float32)
print('  downsampled', arr.shape)

land = arr > 0  # 海洋/水域透明
elev = np.where(land, arr, 0)

# 晕渲 hillshade
def hillshade(z, az_deg=315, alt_deg=45):
    dy, dx = np.gradient(z)
    # 经纬度像素纵横比修正（中纬度 1deg_lon/1deg_lat ≈ 0.85）
    dx = dx * 0.85
    slope = np.arctan(np.sqrt(dx*dx + dy*dy))
    aspect = np.arctan2(-dx, dy)
    az = np.deg2rad(az_deg); alt = np.deg2rad(alt_deg)
    sh = np.sin(alt)*np.cos(slope) + np.cos(alt)*np.sin(slope)*np.cos(az - aspect)
    return np.clip(sh, 0, 1)

hs = hillshade(elev)

# 学术山水色带：低地茶绿 → 中山土褐 → 高峰雪白
cmap = LinearSegmentedColormap.from_list('tea_relief', [
    (0.00, '#c7cda6'),  # 低地 茶绿黄
    (0.18, '#b3b48a'),
    (0.38, '#9a8a63'),  # 丘陵 土黄
    (0.58, '#7c6240'),  # 中山 褐
    (0.76, '#5a4028'),  # 高山 深褐
    (0.90, '#a8a098'),  # 极高山 灰
    (1.00, '#f2f2f2'),  # 雪线
])
norm = Normalize(vmin=0, vmax=6000, clip=True)
rgb = cmap(norm(elev))[:, :, :3]  # 0..1

# 合成：地形色 * (环境光 + 晕渲)
shade = 0.38 + 0.62 * hs
comp = rgb * shade[:, :, None]
comp = np.clip(comp, 0, 1)

rgba = np.dstack([comp, land.astype(np.float32)])  # alpha = land
plt.imsave(BASE + r'\dem_relief.png', rgba)
print('  saved dem_relief.png', rgba.shape)

# ===================================================================
# 2) 唐代产茶区点 → 模糊边界密度图
# ===================================================================
print('[2/3] 处理 唐代茶区 ...')
tang = gpd.read_file(BASE + r'\唐代产茶区.shp')
tx = tang.geometry.x.values
ty = tang.geometry.y.values

# 与 DEM 同范围，网格 1500 x H
gw = 1500
left, right = b.left, b.right
bottom, top = b.bottom, b.top
gh = int(round(gw * (top - bottom) / (right - left)))
print('  grid', gw, gh)

grid = np.zeros((gh, gw), dtype=np.float32)
xs = (tx - left) / (right - left) * (gw - 1)
ys = (top - ty) / (top - bottom) * (gh - 1)
for xx, yy in zip(xs, ys):
    ix, iy = int(round(xx)), int(round(yy))
    if 0 <= ix < gw and 0 <= iy < gh:
        grid[iy, ix] += 1.0

# 模糊：先大 sigma 形成区域晕染，保留较软边界
blur = gaussian_filter(grid, sigma=26)
if blur.max() > 0:
    blur = blur / blur.max()

# 透明度：低值剔除，平方根增强层次
alpha = np.clip(blur, 0, 1)
alpha[alpha < 0.04] = 0
alpha = np.power(alpha, 0.55)

# 颜色：土金 #c8a24a，叠一点暖红 #b5651d
amber = np.array([0.784, 0.635, 0.290])  # #c8a24a
warm  = np.array([0.710, 0.396, 0.114])  # #b5651d
strength = alpha[:, :, None]
col = amber[None, None, :] * (1 - 0.35*alpha[:,:,None]) + warm[None,None,:]*0.35*alpha[:,:,None]
rgba_t = np.dstack([col, alpha]).astype(np.float32)
plt.imsave(BASE + r'\tang_density.png', rgba_t)
print('  saved tang_density.png')

# ===================================================================
# 3) 古茶树点 → GeoJSON（三型分色 · 暂定地理分组）
# ===================================================================
print('[3/3] 处理 古茶树点 ...')
pts = gpd.read_file(BASE + r'\古茶树点位.shp')
px = pts.geometry.x.values
py = pts.geometry.y.values

features = []
n_outlier = 0
for xx, yy in zip(px, py):
    # 过滤异常点（如经度<70 的录入错误）
    if xx < 70 or xx > 135 or yy < 15 or yy > 45:
        n_outlier += 1
        continue
    # —— 暂定三型：按地理分布分组（待真实属性确认后替换）——
    if xx <= 108 and yy <= 30:
        t, tn = 1, '类型一（暂定·西南野生）'
    elif xx <= 113 and yy <= 32:
        t, tn = 2, '类型二（暂定·中部过渡）'
    else:
        t, tn = 3, '类型三（暂定·东部栽培）'
    features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(xx), float(yy)]},
        "properties": {
            "type": t,
            "typeName": tn,
            "name": "古茶树"
        }
    })
print(f'  points kept {len(features)}, outliers {n_outlier}')

fc = {"type": "FeatureCollection", "features": features}
with open(BASE + r'\tea_trees.js', 'w', encoding='utf-8') as f:
    f.write('/* 自动生成 · 古茶树点（类型为暂定地理分组，待真实属性确认）*/\n')
    f.write('var TEA_TREES = ')
    json.dump(fc, f, ensure_ascii=False)
    f.write(';\n')
print('  saved tea_trees.js')

# ===================================================================
# 输出 bounds.js
# ===================================================================
with open(BASE + r'\dem_bounds.js', 'w', encoding='utf-8') as f:
    f.write('/* 自动生成 · 第一章图层地理范围 */\n')
    f.write("var DEM_IMG = 'data/1/dem_relief.png';\n")
    f.write('var DEM_BOUNDS = ' + json.dumps(bounds) + ';\n')
    f.write("var TANG_IMG = 'data/1/tang_density.png';\n")
    f.write('var TANG_BOUNDS = ' + json.dumps(bounds) + ';\n')
print('  saved dem_bounds.js')
print('\n全部完成。')
