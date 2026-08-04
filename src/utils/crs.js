import L from 'leaflet'

export function createAlbersCRS() {
  return L.CRS.EPSG4326
}

export function getAlbersMapOptions() {
  return {
    crs: L.CRS.EPSG4326,
    center: [35, 105],
    zoom: 4,
    minZoom: 3,
    maxZoom: 8,
  }
}
