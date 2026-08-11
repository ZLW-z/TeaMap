<template>
  <section class="page-wrap">
    <ChapterIntro
      ch-no="壹"
      title="茶生山水间"
      desc="群山蕴灵气，活水育新芽。茶自山野萌芽扎根，循着山川脉络散落四方，这片广袤土地，便是茶叶最初的故乡。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <!-- 地图全屏 -->
    <div class="map-fullscreen" :class="{ show: introDone }">
      <div ref="mapEl" class="map"></div>

      <!-- 图例 -->
      <div class="map-legend">
        <div class="legend-title">图 例</div>
        <div class="legend-row tang" :class="{ dim: stage < 1 }">
          <span class="sw tang-sw"></span>唐代产茶区
        </div>
        <div class="legend-subtitle">古茶树 · 现存资源</div>
        <div class="legend-row t1" :class="{ dim: stage < 2 }">
          <span class="sw t-sw"></span>野生型 <span class="count">（{{ counts[1] }}）</span>
        </div>
        <div class="legend-row t2" :class="{ dim: stage < 2 }">
          <span class="sw t-sw t2"></span>过渡/其他 <span class="count">（{{ counts[2] }}）</span>
        </div>
        <div class="legend-row t3" :class="{ dim: stage < 2 }">
          <span class="sw t-sw t3"></span>栽培型 <span class="count">（{{ counts[3] }}）</span>
        </div>
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
  BG_DEM_IMG, MASK_IMG, DEM_IMG, loadDemBounds, MAP_INIT,
  OUTLINE_URL, TENDASH_URL, TANG_AREAS_URL, TEA_TREES_URL,
  TREE_TYPE_STYLE, OUTLINE_STYLE, TENDASH_STYLE, TANG_STYLE, TANG_BLUR_STYLE
} from '../config/ch1.js'

const props = defineProps({ id: { type: String, default: 'ch1' } })

const mapEl = ref(null)
let map = null
let bgDemLayer = null, maskLayer = null, demLayer = null
let outlineLayer = null, tendashLayer = null, tangLayer = null, tangBlurLayer = null
let treeMarkers = []
const stage = ref(0)
const counts = reactive({ 1: 0, 2: 0, 3: 0 })
const introDone = ref(false)
// SVG <defs> 高斯模糊滤镜引用 id (保证唯一)
const TANG_BLUR_FILTER_ID = 'tang-blur-filter-' + Math.random().toString(36).slice(2, 8)

function onIntroDone() {
  introDone.value = true
  setTimeout(() => {
    if (map) map.invalidateSize()
    applyStage(0, true)
    // 1.5s 后 → Stage 1 (产茶区淡入 + 遮罩淡出)
    autoTimers.push(setTimeout(() => applyStage(1), 1500))
    // 4.0s 后 → Stage 2 (茶树点淡入)
    autoTimers.push(setTimeout(() => applyStage(2), 4000))
  }, 300)
}

let animRAF = null
let tangRAF = null
let maskRAF = null
let autoTimers = []

// ----------- 初始化地图 -----------
async function initMap() {
  const albersCRS = createAlbersCRS()
  // 使用 SVG renderer (默认就是 SVG), 稍后给 SVG <defs> 注入高斯模糊滤镜
  const svgRenderer = L.svg({ padding: 2 })
  map = L.map(mapEl.value, {
    crs: albersCRS,
    center: MAP_INIT.center,
    zoom: MAP_INIT.zoom,
    minZoom: MAP_INIT.minZoom,
    maxZoom: MAP_INIT.maxZoom,
    scrollWheelZoom: true,
    zoomControl: true,
    attributionControl: false,
    dragging: true,
    doubleClickZoom: false,
    touchZoom: true,
    keyboard: false,
    renderer: svgRenderer
  })

  // 注入 SVG <defs> 高斯模糊滤镜: 两个 blur radius
  // 1. tang-blur-big:   σ=14px —— 模糊扩展的底晕 (向外扩张大)
  // 2. tang-blur-small: σ=7px  —— 顶部轻微软化边缘
  setTimeout(installSvgFilters, 50)

  const demBounds = await loadDemBounds()

  // === Layer 0: 背景全球 DEM (淡色, 底层, 一直可见) ===
  bgDemLayer = L.imageOverlay(BG_DEM_IMG, demBounds, {
    opacity: 0.78, interactive: false
  }).addTo(map)

  // === Layer 1: 遮罩层 (中国外半透明白, 聚焦) ===
  // 在 Stage 0 为不透明，Stage>=1 时淡出到 0（产茶区、茶树点叠加上来时移除遮罩）
  maskLayer = L.imageOverlay(MASK_IMG, demBounds, {
    opacity: 0, interactive: false
  }).addTo(map)

  // === Layer 2: 中国 DEM + 下沉投影阴影 (主要视觉层) ===
  demLayer = L.imageOverlay(DEM_IMG, demBounds, {
    opacity: 1, interactive: false
  }).addTo(map)

  // === Layer 3: 轮廓线 + 十段线 (线画层面) ===
  try {
    const ro = await fetch(OUTLINE_URL)
    const outlineData = await ro.json()
    outlineLayer = L.geoJSON(outlineData, {
      style: () => ({ ...OUTLINE_STYLE }),
      interactive: false
    }).addTo(map)
  } catch (e) { console.warn('load outline failed:', e) }

  try {
    const rt = await fetch(TENDASH_URL)
    const tendashData = await rt.json()
    tendashLayer = L.geoJSON(tendashData, {
      style: () => ({ ...TENDASH_STYLE }),
      interactive: false
    }).addTo(map)
  } catch (e) { console.warn('load tendash failed:', e) }

  // === Layer 4: 唐代茶区 (初始隐藏) —— 双层: 底层模糊扩张 + 顶层轻微柔边 ===
  // 效果: 没有清晰的边界线, 填充向外有高斯模糊扩展, 像模糊区划
  try {
    const r1 = await fetch(TANG_AREAS_URL)
    const tangData = await r1.json()

    // Layer 4a: 模糊扩张底层 (先渲染, 在最下面)
    tangBlurLayer = L.geoJSON(tangData, {
      style: () => ({
        ...TANG_BLUR_STYLE,
        opacity: 0,
        fillOpacity: 0,
        filter: `url(#${TANG_BLUR_FILTER_ID}-big)`
      }),
      interactive: false
    })
    tangBlurLayer.addTo(map)

    // Layer 4b: 轻微柔边的主填充层 (在上面)
    tangLayer = L.geoJSON(tangData, {
      style: () => ({
        ...TANG_STYLE,
        opacity: 0,
        fillOpacity: 0,
        filter: `url(#${TANG_BLUR_FILTER_ID}-small)`
      }),
      interactive: true
    })
    tangLayer.bindTooltip(layer => {
      const p = layer.feature.properties
      return `<div style="font-family:Noto Serif SC,serif;color:#516D33;padding:2px 4px">
        <b>${p.name || ''}</b><br/><span style="font-size:11px;color:#8a8478">${p.areaLabel || ''}</span></div>`
    }, { direction: 'top', sticky: true, offset: [0, -6] })
    tangLayer.addTo(map)
  } catch (e) { console.warn('load tang areas failed:', e) }

  // === Layer 5: 古茶树点 (Albers坐标: [x_meter, y_meter]) ===
  try {
    const r2 = await fetch(TEA_TREES_URL)
    const treeData = await r2.json()
    treeData.features.forEach(f => {
      const g = f && f.geometry
      if (!g || !Array.isArray(g.coordinates) || g.coordinates.length < 2) return
      const [x_m, y_m] = g.coordinates
      if (typeof x_m !== 'number' || typeof y_m !== 'number' || !isFinite(x_m) || !isFinite(y_m)) return
      const t = (f.properties && (f.properties.type || 2)) || 2
      const s = TREE_TYPE_STYLE[t]
      counts[t] = (counts[t] || 0) + 1
      // Leaflet [lat, lng] = [y_meter, x_meter]
      const m = L.circleMarker([y_m, x_m], {
        radius: 7,
        color: '#fff',
        weight: 1.5,
        fillColor: s.fill,
        fillOpacity: 0, opacity: 0
      })
      const props = f.properties || {}
      const name = props.name || '古茶树'
      const province = props.province
      const species = props.species
      const tn = s.label
      m.bindPopup(
        `<div style="font-family:Noto Sans SC,sans-serif;min-width:170px">
          <b style="color:${s.color};font-family:Noto Serif SC,serif">${name}</b><br/>
          <span style="font-size:12px;color:#4a4a40">类型：${tn}</span><br/>
          ${province ? `<span style="font-size:12px;color:#4a4a40">省份：${province}</span><br/>` : ''}
          ${species ? `<span style="font-size:12px;color:#4a4a40">学名：<i>${species}</i></span><br/>` : ''}
          <span style="font-size:11px;color:#8a8478">坐标：${(y_m/1000).toFixed(1)}km, ${(x_m/1000).toFixed(1)}km</span>
        </div>`
      )
      m._teaType = t
      m._targetFO = 0.92
      treeMarkers.push(m)
    })
  } catch (e) { console.warn('load tea trees failed:', e) }

  map.fitBounds(MAP_INIT.fitBounds, { animate: false })
  setTimeout(() => map && map.invalidateSize(), 300)
}

// --- Mask 淡入淡出动画 (Stage 切换遮罩用) ---
function animateMaskOpacity(target, immediate) {
  if (!maskLayer) return
  if (immediate) {
    maskLayer.setOpacity(target)
    return
  }
  cancelAnimationFrame(maskRAF)
  const cur = maskLayer.options && typeof maskLayer.options.opacity === 'number'
    ? maskLayer.options.opacity : 0
  let start = null, DUR = 900
  const tick = ts => {
    if (start === null) start = ts
    const e = Math.min(1, (ts - start) / DUR)
    const k = e < 1 ? 1 - Math.pow(1 - e, 3) : 1
    maskLayer.setOpacity(cur + (target - cur) * k)
    if (e < 1) maskRAF = requestAnimationFrame(tick)
  }
  maskRAF = requestAnimationFrame(tick)
}

// --- 给 Leaflet 渲染的 SVG 注入 <defs> 高斯模糊滤镜 ---
//   σ=14 用于底层向外扩散晕染, σ=6 用于顶层轻微柔边去硬边
function installSvgFilters() {
  if (!map) return
  const svg = mapEl.value && mapEl.value.querySelector('svg')
  if (!svg) { setTimeout(installSvgFilters, 100); return }
  // 避免重复注入
  if (svg.querySelector('#' + CSS.escape(TANG_BLUR_FILTER_ID + '-big'))) return
  let defs = svg.querySelector('defs')
  if (!defs) {
    defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
    svg.insertBefore(defs, svg.firstChild)
  }
  defs.insertAdjacentHTML('beforeend', `
    <filter id="${TANG_BLUR_FILTER_ID}-big" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="14" result="blur14"/>
      <feGaussianBlur in="blur14" stdDeviation="8" result="blur22"/>
      <feMerge>
        <feMergeNode in="blur22"/>
        <feMergeNode in="blur14"/>
      </feMerge>
    </filter>
    <filter id="${TANG_BLUR_FILTER_ID}-small" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="5.5"/>
    </filter>
  `)
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

  // Stage 定义:
  // 0 — 仅 DEM 展示 (背景DEM + 遮罩 + 中国DEM + 轮廓 + 十段线): 遮罩打开 = 聚焦中国
  // 1 — 产茶区淡入; 遮罩淡出为 0 (用户需求: 产茶区/茶树点叠加上来时不再遮罩中国 DEM)
  // 2 — 茶树点淡入; 保持遮罩关闭

  // === 背景 DEM 透明度: 全程略低, 保持"底色感" ===
  const bgOp = [0.78, 0.70, 0.65][next]
  if (bgDemLayer) bgDemLayer.setOpacity(bgOp)

  // === 中国 DEM 透明度 (顶层): 略有弱化, 让位给上层数据 ===
  const demOp = [1.00, 0.90, 0.80][next]
  if (demLayer) demLayer.setOpacity(demOp)

  // === 遮罩: Stage 0 显示, Stage 1+ 关闭 ===
  // 用户需求: 当产茶区图层和古茶树点位图层叠加上来时不需要给中国DEM增加遮罩
  const maskOp = [0.65, 0.0, 0.0][next]
  animateMaskOpacity(maskOp, immediate)

  // === 唐代茶区: Stage>=1 淡入 —— 双层: 底层模糊更淡、范围更大; 顶层更清晰 ===
  // 填充向外高斯模糊扩散, 像没有清晰边界的模糊区划
  const tang = [
    { o: 0,    f: 0,    bo: 0,    bf: 0 },
    { o: 0.95, f: 0.68, bo: 0.95, bf: 0.48 },  // Stage 1: 完整显示模糊区划
    { o: 0.85, f: 0.55, bo: 0.80, bf: 0.42 }   // Stage 2: 让位茶树点
  ][next]
  setTangOpacity(tangLayer, tang.o, tang.f, immediate)
  setTangOpacity(tangBlurLayer, tang.bo, tang.bf, immediate)

  // === 古茶树点: Stage>=2 淡入 ===
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
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animRAF)
  cancelAnimationFrame(tangRAF)
  cancelAnimationFrame(maskRAF)
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
  /* 匹配背景DEM的米纸色，让无数据处颜色一致 */
  background: #EDE9DE;
}

/* 图例 */
.map-legend {
  position: absolute;
  left: 16px;
  bottom: 18px;
  background: rgba(247, 244, 235, 0.94);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px 16px;
  font: 400 12px/1.5 var(--sans);
  color: var(--ink-soft);
  min-width: 218px;
  backdrop-filter: blur(4px);
  z-index: 500;
  box-shadow: 0 4px 20px rgba(81, 109, 51, 0.08);
}
.legend-title {
  font: 600 13px/1 var(--serif);
  color: var(--c-olive);
  letter-spacing: 0.15em;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(81, 109, 51, 0.15);
}
.legend-subtitle {
  font: 500 11px/1 var(--sans);
  color: #8a8478;
  letter-spacing: 0.05em;
  margin: 10px 0 6px;
}
.legend-row {
  display: flex; align-items: center; gap: 9px; margin: 5px 0;
  transition: opacity 0.5s ease;
}
.legend-row.dim { opacity: 0.25; }
.legend-row .count {
  color: #8a8478;
  margin-left: auto;
  font-variant-numeric: tabular-nums;
  font-size: 11px;
}
.legend-row .sw {
  width: 14px; height: 14px; border-radius: 3px; flex: 0 0 auto;
  border: 1px solid rgba(0,0,0,0.12);
}

/* 产茶区 swatch */
.legend-row .tang-sw {
  background: #D4B44C;
  border: 1.5px solid #8E6F38;
  border-radius: 2px;
}

/* 茶树点 swatch: 圆形, 白边 */
.legend-row .t-sw {
  width: 13px; height: 13px;
  border-radius: 50%;
  background: #C8462E;
  border: 1.5px solid #fff;
  box-shadow: 0 0 0 1px rgba(200, 70, 46, 0.25);
}
.legend-row .t-sw.t2 {
  background: #B28F4C;
  box-shadow: 0 0 0 1px rgba(178, 143, 76, 0.25);
}
.legend-row .t-sw.t3 {
  background: #2F5D3A;
  box-shadow: 0 0 0 1px rgba(47, 93, 58, 0.25);
}

@media (max-width: 880px) {
  .map-legend { left: 8px; bottom: 8px; min-width: 190px; padding: 10px 12px; font-size: 11px; }
  .legend-title { font-size: 12px; }
}
</style>
