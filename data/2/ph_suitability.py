import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from rasterio.mask import mask
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# =========================
# 1. 文件路径
# =========================
ph_file = r"D:\Desktop\星湖杯\茶叶\ppho2\soil_ph.tif"

china_file = r"D:\Desktop\星湖杯\茶叶\ppho2\china-provinces.geojson"

out_png = r"D:\Desktop\星湖杯\茶叶\ppho2\output\soil_ph_suitability.png"


# ==========================
# 读取中国边界
# ==========================


china = gpd.read_file(china_file)



# ==========================
# 读取pH栅格
# ==========================


src = rasterio.open(ph_file)


if china.crs != src.crs:
    china = china.to_crs(src.crs)



# ==========================
# 裁剪中国区域
# ==========================


data, transform = mask(
    src,
    china.geometry,
    crop=True
)


ph = data[0]



# 去除NoData

nodata = src.nodata

if nodata is not None:
    ph = np.where(
        ph==nodata,
        np.nan,
        ph
    )



# ==========================
# pH分类
# ==========================


suitability = np.zeros(
    ph.shape,
    dtype=np.uint8
)


# 不适宜
suitability[
    (ph<4) | (ph>7.5)
]=0


# 限制适宜
suitability[
    ((ph>=4)&(ph<4.5))
    |
    ((ph>6.5)&(ph<=7.5))
]=1


# 较适宜
suitability[
    ((ph>=5.5)&(ph<=6.5))
]=2


# 最适宜
suitability[
    ((ph>=4.5)&(ph<5.5))
]=3



# nodata

suitability[
    np.isnan(ph)
]=255



# ==========================
# 绘图
# ==========================


fig, ax_main = plt.subplots(figsize=(10, 8), dpi=300)


colors = [
    "#D9D9D9",
    "#FFD966",
    "#93D18B",
    "#238B45"
]


cmap = ListedColormap(colors)


show = np.ma.masked_where(
    suitability == 255,
    suitability
)


extent = [
    transform[2],
    transform[2] + transform[0] * ph.shape[1],
    transform[5] + transform[4] * ph.shape[0],
    transform[5]
]


ax_main.imshow(
    show,
    cmap=cmap,
    interpolation="nearest",
    extent=extent
)


china.boundary.plot(
    ax=ax_main,
    color="black",
    linewidth=0.4
)


ax_main.set_title(
    "中国茶叶种植土壤酸碱度适宜性分析",
    fontsize=16,
    fontproperties="SimHei",
    pad=25
)


ax_main.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.5)


ax_main.set_xticks(np.arange(70, 145, 10))
ax_main.set_yticks(np.arange(18, 55, 10))


ax_main.set_xlabel('经度', fontproperties="SimHei", fontsize=12, labelpad=15)
ax_main.set_ylabel('纬度', fontproperties="SimHei", fontsize=12, labelpad=15)


ax_main.tick_params(axis='both', labelsize=10)


ax_main.set_xlim(68, 138)
ax_main.set_ylim(15, 55)


# 指北针
x_north, y_north = 0.88, 0.96
ax_main.annotate('N',
                 xy=(x_north, y_north), xycoords='axes fraction',
                 fontsize=14, fontweight='bold',
                 ha='center', va='center')

ax_main.add_patch(FancyArrowPatch(
    (x_north, y_north - 0.05),
    (x_north, y_north - 0.01),
    arrowstyle='->',
    mutation_scale=18,
    linewidth=1.5,
    color='black',
    transform=ax_main.transAxes
))


# 比例尺
scale_x = 0.10
scale_y = 0.05
scale_lengths = [0, 200, 400, 600, 800, 1000, 1200]

ax_main.add_line(Line2D(
    [scale_x, scale_x + 0.4],
    [scale_y, scale_y],
    linewidth=2,
    color='black',
    transform=ax_main.transAxes
))

for i, length in enumerate(scale_lengths):
    x_pos = scale_x + (i * 0.4 / 6)
    ax_main.add_line(Line2D(
        [x_pos, x_pos],
        [scale_y, scale_y + 0.01],
        linewidth=1.5,
        color='black',
        transform=ax_main.transAxes
    ))
    ax_main.text(
        x_pos,
        scale_y - 0.015,
        str(length),
        fontsize=8,
        ha='center',
        transform=ax_main.transAxes
    )

ax_main.text(
    scale_x + 0.2,
    scale_y - 0.035,
    '单位：km',
    fontsize=8,
    ha='center',
    transform=ax_main.transAxes
)


# 图例
legend = [
    Patch(color=colors[0], label="不适宜区"),
    Patch(color=colors[1], label="限制适宜区"),
    Patch(color=colors[2], label="较适宜区"),
    Patch(color=colors[3], label="最适宜区")
]

ax_main.legend(
    handles=legend,
    loc="center right",
    bbox_to_anchor=(1.22, 0.5),
    prop={
        "family": "SimHei",
        "size": 10
    },
    title="适宜性等级",
    title_fontproperties={"family": "SimHei", "size": 12}
)


# 南海小图（放在主图右下角）
ax_south_china = inset_axes(
    ax_main,
    width="22%",
    height="30%",
    loc="lower right",
    borderpad=1.5
)

south_china_extent = [105, 125, 2, 25]

ax_south_china.imshow(
    show,
    cmap=cmap,
    interpolation="nearest",
    extent=extent
)

china.boundary.plot(
    ax=ax_south_china,
    color="black",
    linewidth=0.25
)

ax_south_china.set_xlim(south_china_extent[0], south_china_extent[1])
ax_south_china.set_ylim(south_china_extent[2], south_china_extent[3])

ax_south_china.set_title("南海诸岛", fontsize=9, fontproperties="SimHei", pad=3)

ax_south_china.set_xticks([110, 120])
ax_south_china.set_yticks([5, 15, 25])

ax_south_china.tick_params(axis='both', labelsize=5)

ax_south_china.grid(True, linestyle='--', linewidth=0.25, color='gray', alpha=0.5)

ax_south_china.set_xlabel('经度', fontproperties="SimHei", fontsize=5, labelpad=2)
ax_south_china.set_ylabel('纬度', fontproperties="SimHei", fontsize=5, labelpad=2)

plt.savefig(
    out_png,
    dpi=300,
    bbox_inches="tight"
)


print("完成:")
print(out_png)