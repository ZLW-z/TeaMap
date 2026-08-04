<template>
  <section class="page-wrap">
    <ChapterIntro
      ch-no="第 一 章"
      title="茶生山水间"
      desc="山为骨，水为脉。DEM 高程铺底，唐代八大茶区以水墨边界渐次浮现，古茶树三型如星散落，照见茶之原生格局。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <!-- 地图全屏 -->
    <div class="map-fullscreen" :class="{ show: introDone }">
      <div ref="mapEl" class="map"></div>

      <!-- 图例 -->
      <div class="map-legend">
        <div class="legend-title">图例</div>
        <div class="legend-row dem"><span class="sw"></span>高程地形（DEM）</div>
        <div class="legend-row prov"><span class="sw"></span>行政区划</div>
        <div class="legend-row tang" :class="{ dim: stage < 1 }"><span class="sw"></span>唐代产茶区</div>
        <div class="legend-row t1" :class="{ dim: stage < 2 }"><span class="sw"></span>古茶树 · 野生型（{{ counts[1] }}）</div>
        <div class="legend-row t2" :class="{ dim: stage < 2 }"><span class="sw"></span>古茶树 · 过渡/其他（{{ counts[2] }}）</div>
        <div class="legend-row t3" :class="{ dim: stage < 2 }"><span class="sw"></span>古茶树 · 栽培型（{{ counts[3] }}）</div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, reactive } from 'vue'
import L from 'leaflet'
import { createAlbersCRS } from '../utils/crs.js'
import ChapterIntro from './ChapterIntro.vue'
import {
  DEM_IMG, loadDemBounds, MAP_INIT,
  PROV_BG_URL, TANG_AREAS_URL, TEA_TREES_URL,
  TREE_TYPE_STYLE, PROV_STYLE, TANG_STYLE
} from '../config/ch1.js'

const props = defineProps({ id: { type: String, default: 'ch1' } })

const mapEl = ref(null)
let map = null, demLayer = null, provLayer = null, tangLayer = null
let treeMarkers = []
const stage = ref(0)
const counts = reactive({ 1: 0, 2: 0, 3: 0 })
const introDone = ref(false)

function onIntroDone() {
  introDone.value = true
  // 延迟启动地图图层动画，等地图容器进场完毕
  setTimeout(() => {
    if (map) map.invalidateSize()
    applyStage(0, true)
    autoTimers.push(setTimeout(() => applyStage(1), 1500))
    autoTimers.push(setTimeout(() => applyStage(2), 4000))
  }, 300)
}

let animRAF = null
let tangRAF = null
let autoTimers = []

// ----------- 初始化地图 -----------
async function initMap() {
  map = L.map(mapEl.value, {
    crs: createAlbersCRS(),
    center: [33, 108],
    zoom: 4,
    minZoom: 3,
    maxZoom: 8,
    scrollWheelZoom: true,
    zoomControl: true,
    attributionControl: false,
    dragging: true,
    doubleClickZoom: false,
    touchZoom: true,
    keyboard: false
  })

  // 0) 省份行政区划底图
  try {
    const rp = await fetch(PROV_BG_URL)
    const provData = await rp.json()
    provLayer = L.geoJSON(provData, { style: () => ({ ...PROV_STYLE }) }).addTo(map)
  } catch (e) { console.warn('load provinces failed:', e) }

  // 1) DEM
  const demBounds = await loadDemBounds()
  demLayer = L.imageOverlay(DEM_IMG, demBounds, { opacity: 1 }).addTo(map)

  // 2) 唐代茶区
  try {
    const r1 = await fetch(TANG_AREAS_URL)
    const tangData = await r1.json()
    tangLayer = L.geoJSON(tangData, {
      style: () => ({ ...TANG_STYLE, opacity: 0, fillOpacity: 0 })
    })
    tangLayer.bindTooltip(layer => {
      const p = layer.feature.properties
      return `<div style="font-family:Noto Serif SC,serif;color:#516D33;padding:2px 4px">
        <b>${p.name || ''}</b><br/><span style="font-size:11px;color:#8a8478">${p.areaLabel || ''}</span></div>`
    }, { direction: 'top', sticky: true, offset: [0, -6] })
    tangLayer.addTo(map)
  } catch (e) { console.warn('load tang areas failed:', e) }

  // 3) 古茶树点
  try {
    const r2 = await fetch(TEA_TREES_URL)
    const treeData = await r2.json()
    treeData.features.forEach(f => {
      const [lon, lat] = f.geometry.coordinates
      const t = f.properties.type || 2
      const s = TREE_TYPE_STYLE[t]
      counts[t] = (counts[t] || 0) + 1
      const m = L.circleMarker([lat, lon], {
        radius: 7,
        color: '#fff',
        weight: 1.5,
        fillColor: s.fill,
        fillOpacity: 0, opacity: 0
      })
      const name = f.properties.name || '古茶树'
      const province = f.properties.province
      const species = f.properties.species
      const tn = s.label
      m.bindPopup(
        `<div style="font-family:Noto Sans SC,sans-serif;min-width:170px">
          <b style="color:${s.color};font-family:Noto Serif SC,serif">${name}</b><br/>
          <span style="font-size:12px;color:#4a4a40">类型：${tn}</span><br/>
          ${province ? `<span style="font-size:12px;color:#4a4a40">省份：${province}</span><br/>` : ''}
          ${species ? `<span style="font-size:12px;color:#4a4a40">学名：<i>${species}</i></span><br/>` : ''}
          <span style="font-size:11px;color:#8a8478">${lat.toFixed(3)}, ${lon.toFixed(3)}</span>
        </div>`
      )
      m._teaType = t
      m._targetFO = 0.92
      treeMarkers.push(m)
    })
  } catch (e) { console.warn('load tea trees failed:', e) }

  // 自动适配视图到中国区域
  map.fitBounds([[18, 75], [53, 135]], { animate: false })
  setTimeout(() => map && map.invalidateSize(), 300)
  // 自动播放在 intro 结束后由 onIntroDone 触发
}

function setTangOpacity(layer, targetOp, targetFOp, immediate) {
  if (!layer) return
  if (immediate) {
    layer.eachLayer(p => p.setStyle({ opacity: targetOp, fillOpacity: targetFOp }))
    return
  }
  cancelAnimationFrame(tangRAF)
  const layers = []
  layer.eachLayer(p => {
    const sty = p.options || {}
    layers.push({
      p,
      a0: typeof sty.opacity === 'number' ? sty.opacity : 0,
      f0: typeof sty.fillOpacity === 'number' ? sty.fillOpacity : 0,
    })
  })
  let start = null, DUR = 900
  const tick = ts => {
    if (start === null) start = ts
    const e = Math.min(1, (ts - start) / DUR)
    const k = e < 1 ? 1 - Math.pow(1 - e, 3) : 1
    layers.forEach(({ p, a0, f0 }) => {
      p.setStyle({ opacity: a0 + (targetOp - a0) * k, fillOpacity: f0 + (targetFOp - f0) * k })
    })
    if (e < 1) tangRAF = requestAnimationFrame(tick)
  }
  tangRAF = requestAnimationFrame(tick)
}

function applyStage(next, immediate = false) {
  if (next === stage.value && !immediate) return
  stage.value = next

  const demOp = [1.00, 0.82, 0.68][next]
  if (demLayer) demLayer.setOpacity(demOp)

  const tang = [{ o: 0, f: 0 }, { o: 1, f: 0.55 }, { o: 1, f: 0.42 }][next]
  setTangOpacity(tangLayer, tang.o, tang.f, immediate)

  if (next >= 2) {
    treeMarkers.forEach(m => { if (!map.hasLayer(m)) m.addTo(map) })
    animateTreesIn(immediate)
  } else {
    treeMarkers.forEach(m => { if (map.hasLayer(m)) map.removeLayer(m) })
    treeMarkers.forEach(m => m.setStyle({ fillOpacity: 0, opacity: 0 }))
  }
}

function animateTreesIn(immediate) {
  cancelAnimationFrame(animRAF)
  const order = { 1: 0, 2: 0.32, 3: 0.64 }
  if (immediate) {
    treeMarkers.forEach(m => m.setStyle({ fillOpacity: m._targetFO, opacity: m._targetFO }))
    return
  }
  treeMarkers.forEach(m => m.setStyle({ fillOpacity: 0, opacity: 0 }))
  let start = null, DURATION = 1100
  const tick = ts => {
    if (start === null) start = ts
    const e = (ts - start) / DURATION
    treeMarkers.forEach(m => {
      const off = order[m._teaType] || 0
      const local = Math.max(0, Math.min(1, (e - off) / (1 - off)))
      const eased = local < 1 ? 1 - Math.pow(1 - local, 3) : 1
      m.setStyle({ fillOpacity: eased * m._targetFO, opacity: eased * m._targetFO })
    })
    if (e < 1.25) animRAF = requestAnimationFrame(tick)
  }
  animRAF = requestAnimationFrame(tick)
}

onMounted(async () => {
  await initMap()
  // 不在此处启动自动播放，等 intro 动画结束
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animRAF)
  cancelAnimationFrame(tangRAF)
  autoTimers.forEach(t => clearTimeout(t))
  autoTimers = []
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
.page-wrap {
  min-height: 100vh;
  background: linear-gradient(180deg, #F7F4EB 0%, #EFE9DA 100%);
}

.map-fullscreen {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.8s ease;
}
.map-fullscreen.show {
  opacity: 1;
}

.map {
  width: 100%;
  height: 100%;
  background: #DDD5C0;
}

/* 图例 */
.map-legend {
  position: absolute;
  left: 14px;
  bottom: 14px;
  background: rgba(247, 244, 235, 0.93);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px 14px;
  font: 400 12px/1.5 var(--sans);
  color: var(--ink-soft);
  min-width: 200px;
  backdrop-filter: blur(4px);
  z-index: 500;
}
.legend-title {
  font: 600 12px/1 var(--serif);
  color: var(--c-olive);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}
.legend-row {
  display: flex; align-items: center; gap: 8px; margin: 4px 0;
  transition: opacity 0.5s ease;
}
.legend-row.dim { opacity: 0.25; }
.legend-row .sw {
  width: 14px; height: 14px; border-radius: 3px; flex: 0 0 auto;
  border: 1px solid rgba(0,0,0,0.12);
}
.legend-row.dem .sw { background: linear-gradient(135deg,#3D5428,#C3C19A); }
.legend-row.prov .sw { background: #E8E2D0; border: 0.8px solid #A8A28D; }
.legend-row.tang .sw { background: #D4B44C; border: 1.5px solid #8E6F38; }
.legend-row.t1 .sw { background: #C8462E; border-radius: 50%; }
.legend-row.t2 .sw { background: #B28F4C; border-radius: 50%; }
.legend-row.t3 .sw { background: #2F5D3A; border-radius: 50%; }

@media (max-width: 880px) {
  .map-legend { left: 8px; bottom: 8px; min-width: 170px; padding: 10px; font-size: 11px; }
}
</style>
