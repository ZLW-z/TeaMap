import { assetUrl } from '../utils/base.js'

// 第一章 · 图层路径与地理范围 (Albers 等积圆锥投影)
// 多层 DEM 体系 (从底到顶):
//   1. BG_DEM_IMG        —— 全球 DEM 淡色背景 (Albers, 填充整页)
//   2. MASK_IMG          —— 中国外遮罩 (中国外半透明白)
//   3. DEM_IMG           —— 中国 DEM + 3D 阴影 + 下沉投影
export const BG_DEM_IMG = assetUrl('data/1/bg_dem.png')
export const MASK_IMG = assetUrl('data/1/mask_outside.png')
export const DEM_IMG = assetUrl('data/1/dem_relief.png')
export const DEM_BOUNDS_URL = assetUrl('data/1/dem_bounds.json')

// 中国轮廓线 + 十段线 + 市级茶区 + 古茶树 (全部 Albers)
export const OUTLINE_URL = assetUrl('data/1/china_outline.geojson')
export const TENDASH_URL = assetUrl('data/1/china_tendash.geojson')
export const TANG_AREAS_URL = assetUrl('data/1/tang_areas.geojson')
export const TEA_TREES_URL = assetUrl('data/1/tea_trees.geojson')

// Albers 默认 bounds (若 dem_bounds.json 加载失败则回退到此)
// 格式: [[south_y, west_x], [north_y, east_x]] (Albers 米)
// 对应 lon[-120,180] lat[-30,80] 的密集采样真实范围
export const DEM_BOUNDS_FALLBACK = [
  [-2521178, -15157622],
  [16124181, 15157622]
]

export async function loadDemBounds() {
  try {
    const res = await fetch(DEM_BOUNDS_URL)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const b = await res.json()
    return [[b.south, b.west], [b.north, b.east]]
  } catch (e) {
    console.warn('[ch1] dem_bounds.json 加载失败', e)
    return DEM_BOUNDS_FALLBACK
  }
}

export const MAP_INIT = {
  // 中国中心 (Albers Y, X)
  center: [3908108, -132361],
  zoom: 3.5,
  minZoom: 3.5,
  maxZoom: 8,
  // fitBounds: 确保中国完整可视 + 十段线南海区域在画布内
  // Albers 米: Y 向北增大, X 向东增大
  fitBounds: [[-800000, -3500000], [7500000, 2500000]]
}

// 古茶树类型配色：强对比三色
export const TREE_TYPE_STYLE = {
  1: { color: '#C8462E', fill: '#C8462E', label: '野生型' },
  2: { color: '#B28F4C', fill: '#B28F4C', label: '过渡/其他' },
  3: { color: '#2F5D3A', fill: '#2F5D3A', label: '栽培型' }
}

// 中国轮廓线样式
export const OUTLINE_STYLE = {
  color: '#516D33', weight: 1.2, fill: false, opacity: 0.7
}

// 十段线样式
export const TENDASH_STYLE = {
  color: '#516D33', weight: 1.0, dashArray: '4,3', opacity: 0.7
}

// 唐代茶区样式: 无描边 + 向外高斯模糊的模糊区划效果
// - 描边完全去除 (weight=0, opacity=0)
// - 填充通过两层叠加: 下层 blurRadius=22 向外扩展模糊, 上层轻微柔边
//   (渲染时在 Chapter1Map.vue 中用 SVG filter + 双层图层实现)
export const TANG_STYLE = {
  color: 'transparent',
  weight: 0,
  opacity: 0,
  fillColor: '#D4B44C',
  fillOpacity: 0.55
}
// 模糊阴影的填充 (向外扩张晕染层, 与主层同色)
export const TANG_BLUR_STYLE = {
  color: 'transparent',
  weight: 0,
  opacity: 0,
  fillColor: '#D4B44C',
  fillOpacity: 0.55
}
