// 第三章 · 十大名茶配置
import { assetUrl } from '../utils/base.js'
import teasData from '../../data/3/teas-albers.json'

export const TEAS = teasData.map(t => ({
  ...t,
  image: assetUrl(t.image),
}))

// 茶类颜色映射
export const TEA_TYPE_COLORS = {
  '绿茶': '#5C7C3A',
  '乌龙茶（青茶）': '#B28F4C',
  '白茶（微发酵茶）': '#C3C19A',
  '黑茶（后发酵茶）': '#516D33',
  '黄茶': '#D4B44C',
  '红茶': '#92402E',
}

// 十大名茶点样式（醒目）
export const TOP10_STYLE = {
  radius: 9,
  fillColor: '#B28F4C',
  color: '#FFFFFF',
  weight: 2.5,
  opacity: 1,
  fillOpacity: 0.9,
}

// 其他名茶点样式（较小）
export const OTHER_STYLE = {
  radius: 6,
  fillColor: '#5C7C3A',
  color: '#FFFFFF',
  weight: 1.5,
  opacity: 1,
  fillOpacity: 0.8,
}

// 省份底图样式 (Albers 等积圆锥投影，与第一章/第二章一致)
export const PROV_BG_URL = assetUrl('data/2/china-provinces-albers.geojson')

export const PROV_STYLE = {
  color: '#A8A28D',
  weight: 0.6,
  fillColor: '#F0EBD9',
  fillOpacity: 0.5,
}

// 地图初始视图 — Albers 坐标系 (y_m, x_m)，与第一章 createAlbersCRS 匹配
export const MAP_INIT = {
  center: [3908108, -132361],
  zoom: 3.5,
  minZoom: 3.5,
  maxZoom: 8,
  // 确保完整中国可视 + 南海十段线区域（与第一章一致）
  // Albers 米: [[south_y, west_x], [north_y, east_x]]
  fitBounds: [[-800000, -3500000], [7500000, 2500000]],
}

// 名茶点集中区域
// 16 个名茶点 Albers 范围: X[-474271, 1518626], Y[2289479, 3451811]
// 加上 padding 后的中心与缩放
export const TEA_AREA = {
  center: [2870645, 522177],
  zoom: 6.0,
}
