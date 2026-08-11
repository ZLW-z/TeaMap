import L from 'leaflet'

// Albers 等积圆锥投影 CRS for Leaflet
// 中央经线: 105°E, 标准纬线: 25°N / 47°N
// 画布: X [-15157622, 15157622], Y [-2521178, 16124181]
// 宽度 30315244m, 高度 18645360m
export function createAlbersCRS() {
  return L.extend({}, L.CRS.Simple, {
    code: 'ALBERS',
    scale: function (zoom) {
      return 256 / 30315244 * Math.pow(2, zoom)
    }
  })
}

export function getMapOptions() {
  return {
    crs: createAlbersCRS(),
    // 中国中心 (Albers Y, X)
    center: [3908108, -132361],
    zoom: 4,
    minZoom: 4,
    maxZoom: 8,
  }
}
