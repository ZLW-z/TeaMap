import { assetUrl } from '../utils/base.js'

// 第二章 · 五因子适宜性配置
const FACTORS = {
  precip: {
    id: 'precip',
    name: '降水',
    short: '降水',
    icon: '',
    png: assetUrl('data/2/precip_suitability.png'),
    boundsUrl: assetUrl('data/2/precip_bounds.json'),
    desc: '茶树喜湿润，年降水量 1200–1800 mm 为最适宜区',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#A8C5A0' },
      { value: 2, label: '较适宜', color: '#6BA368' },
      { value: 3, label: '最适宜', color: '#2F6B2F' },
    ],
  },
  temp: {
    id: 'temp',
    name: '气温',
    short: '气温',
    icon: '',
    png: assetUrl('data/2/temp_suitability.png'),
    boundsUrl: assetUrl('data/2/temp_bounds.json'),
    desc: '茶树喜温暖，中温区最宜生长，低温与高温区为次适宜',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '低温适宜', color: '#9AC4D6' },
      { value: 2, label: '中温适宜', color: '#5C9EAF' },
      { value: 3, label: '高温适宜', color: '#C8462E' },
    ],
  },
  accum: {
    id: 'accum',
    name: '积温',
    short: '积温',
    icon: '',
    png: assetUrl('data/2/accum_suitability.png'),
    boundsUrl: assetUrl('data/2/accum_bounds.json'),
    desc: '≥10℃ 年活动积温 4000℃·d 以上方可满足茶树生长需求',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#D4B44C' },
      { value: 2, label: '较适宜', color: '#93B55A' },
      { value: 3, label: '最适宜', color: '#516D33' },
    ],
  },
  rad: {
    id: 'rad',
    name: '光照',
    short: '光照',
    icon: '',
    png: assetUrl('data/2/rad_suitability.png'),
    boundsUrl: assetUrl('data/2/rad_bounds.json'),
    desc: '茶树喜光耐阴，年太阳辐射总量适中为最适宜',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#C3C19A' },
      { value: 2, label: '较适宜', color: '#93B55A' },
      { value: 3, label: '最适宜', color: '#516D33' },
    ],
  },
  ph: {
    id: 'ph',
    name: '酸碱度',
    short: 'pH',
    icon: '',
    png: assetUrl('data/2/ph_suitability.png'),
    boundsUrl: assetUrl('data/2/ph_bounds.json'),
    desc: '茶树喜酸性土壤，pH 4.5–5.5 为最适宜区',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#D4B44C' },
      { value: 2, label: '较适宜', color: '#5C7C3A' },
      { value: 3, label: '最适宜', color: '#516D33' },
    ],
  },
}

const COMPOSITE = {
  id: 'composite',
  name: '综合',
  short: '综合',
  icon: '🍃',
  png: assetUrl('data/2/composite_suitability.png'),
  boundsUrl: assetUrl('data/2/composite_bounds.json'),
  desc: '五因子等权重叠加，综合评分 ≥2.5 为茶树生长最适宜区',
  levels: [
    { value: 0, label: '不适宜', color: '#E8E2D0' },
    { value: 1, label: '限制适宜', color: '#C3C19A' },
    { value: 2, label: '较适宜', color: '#93B55A' },
    { value: 3, label: '最适宜', color: '#516D33' },
  ],
}

const FACTOR_ORDER = ['precip', 'temp', 'accum', 'rad', 'ph']

const MAP_BOUNDS = [
  [-2521178, -15157622], // [southY, westX] Albers
  [16124181,  15157622], // [northY, eastX] Albers
]

const PROV_BG_URL = assetUrl('data/2/china-provinces-albers.geojson')

// 国界轮廓 + 九段线（与 ch1 共享同一 Albers 投影坐标系）
const OUTLINE_URL = assetUrl('data/1/china_outline.geojson')
const TENDASH_URL = assetUrl('data/1/china_tendash.geojson')

// 原始合并样式（保留用于兼容）
const PROV_STYLE = {
  color: '#A8A28D',
  weight: 0.6,
  fillColor: '#F0EBD9',
  fillOpacity: 0.5,
}

// 分割样式：fill 在因子图层下方，stroke 在因子图层上方
const PROV_FILL_STYLE = {
  fillColor: '#F0EBD9',
  fillOpacity: 0.5,
  color: 'transparent',
  weight: 0,
}
const PROV_STROKE_STYLE = {
  color: '#A8A28D',
  weight: 0.6,
  fill: false,
  opacity: 0.7,
}

// 国界样式
const OUTLINE_STYLE = {
  color: '#516D33',
  weight: 1.0,
  fill: false,
  opacity: 0.65,
}

// 九段线样式
const TENDASH_STYLE = {
  color: '#516D33',
  weight: 0.8,
  dashArray: '4,3',
  fill: false,
  opacity: 0.6,
}

// 统一全国显示范围（控制相机/fitBounds 显示范围, 非数据图层范围）
// 基于 china-provinces-albers.geojson 真实 bbox 计算:
//   china-provinces bbox: west=-2625498, east=2207630, south=361479, north=5921843
//   china_outline      bbox: west=-2625769, east=2207315, south=362652, north=5921486
// 在真实中国范围外预留约 ~170km 横向 / ~60km 纵向 padding, 保证完整可见。
// 注意: 这只是相机显示范围, 因子 ImageOverlay 必须使用各自 *_bounds.json 中的完整 PNG 范围
//       (全球 Albers 范围), 这样 PNG 中央的中国适宜区像素才会落在正确地理位置。
// Albers 米制坐标: [[southY, westX], [northY, eastX]]
const FULL_CHINA_BOUNDS = [
  [300000,   -2800000], // [southY, westX]
  [6000000,   2400000], // [northY, eastX]
]

// 缩略图相机视野（独立于主图, 比 FULL_CHINA_BOUNDS 多预留 ~10% 边距）
// 仅控制离屏地图 fitBounds 视野, 不参与数据图层地理定位。
// 用于: 离屏缩略图渲染器、主图收缩动画快照。
// 包含: 完整中国陆地 + 沿海岛屿 + 南部海域九段线 + 四周安全留白。
const THUMBNAIL_DISPLAY_BOUNDS = [
  [200000,   -2900000], // [southY, westX]
  [6100000,   2500000], // [northY, eastX]
]

// 右侧工具组安全宽度（说明框 + 转盘）
const TOOL_GROUP_SAFE_WIDTH = 360

const WHEEL_COLORS = [
  '#2F6B2F', // precip - deep green-blue
  '#5C9EAF', // temp - medium teal
  '#D4B44C', // accum - gold
  '#C3C19A', // rad - beige
  '#516D33', // ph - deep olive
]

export {
  FACTORS,
  COMPOSITE,
  FACTOR_ORDER,
  MAP_BOUNDS,
  PROV_BG_URL,
  PROV_STYLE,
  PROV_FILL_STYLE,
  PROV_STROKE_STYLE,
  OUTLINE_URL,
  TENDASH_URL,
  OUTLINE_STYLE,
  TENDASH_STYLE,
  FULL_CHINA_BOUNDS,
  THUMBNAIL_DISPLAY_BOUNDS,
  TOOL_GROUP_SAFE_WIDTH,
  WHEEL_COLORS,
}

export async function loadFactorBounds(factorId) {
  const cfg = factorId === 'composite'
    ? COMPOSITE
    : FACTORS[factorId]
  try {
    const res = await fetch(cfg.boundsUrl)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const b = await res.json()
    // Albers 米制坐标: [[southY, westX], [northY, eastX]]
    return [[b.south, b.west], [b.north, b.east]]
  } catch (e) {
    console.warn('[ch2] bounds load failed:', factorId, e)
    return MAP_BOUNDS
  }
}
