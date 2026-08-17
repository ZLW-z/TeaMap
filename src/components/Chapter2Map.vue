<template>
  <section class="chapter chapter-2">
    <ChapterIntro
      ch-no="贰"
      title="何以生茶"
      desc="得天独厚的光照、气候与土壤条件，编织出适配茶树生长的天然温床，一方水土的禀赋，悄悄决定了茶叶的诞生与品质。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div
      class="chapter-body"
      :class="{ 'ready': layoutReady }"
    >
      <!-- ========= 左侧：固定六宫格（2列3行，顶部开始排列） ========= -->
      <aside class="left-panel">
        <div class="six-grid">
          <!-- 槽位 1~5：缩略图卡槽（永远存在 5 个 slot，内部 thumb-card 按是否有内容挂载；用于动画前测量位置） -->
          <div
            v-for="slotIdx in 5"
            :key="'slot-'+slotIdx"
            class="grid-slot thumb-slot"
            :class="'thumb-slot-'+slotIdx"
          >
            <div
              v-if="thumbSlot[slotIdx - 1]"
              class="thumb-card"
              :class="{ 'is-animating-enter': _thumbEnterKey === slotIdx }"
              @click="onThumbClick(thumbSlot[slotIdx - 1])"
            >
              <div class="thumb-img-wrap">
                <img
                  v-if="thumbSrc(thumbSlot[slotIdx - 1])"
                  :src="thumbSrc(thumbSlot[slotIdx - 1])"
                  :alt="FACTORS[thumbSlot[slotIdx - 1]].name"
                />
              </div>
              <div class="thumb-label">
                <span class="thumb-order">{{ slotIdx }}</span>
                <span class="thumb-name">{{ FACTORS[thumbSlot[slotIdx - 1]].name }}</span>
              </div>
            </div>
          </div>

          <!-- 槽位 6：图例（第三行第二列，固定位置） -->
          <div class="grid-slot legend-slot">
            <div v-if="showLegend" class="legend-inner">
              <div class="legend-title">{{ legendTitle }}</div>
              <div
                v-for="lv in legendLevels"
                :key="lv.value"
                class="legend-row"
              >
                <span class="sw" :style="{ background: lv.color }"></span>
                <span>{{ lv.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- ========= 中间：主地图区（整幅画布，不单独加框） ========= -->
      <main class="main-panel">
        <div
          class="map-title-bar"
          v-if="viewMode === 'composite' || activeFactorId"
        >
          <div v-if="viewMode === 'composite'" class="map-title">
            茶树生态适宜性<strong>综合评价</strong>
          </div>
          <div v-else class="map-title">
            {{ currentConfig.name }}适宜性分析
          </div>
        </div>

        <div
          class="map-stage"
          :class="{ 'map-fade-in': mapReady }"
        >
          <div ref="mapRef" class="map"></div>

          <div
            class="factor-fade-mask"
            :class="{ show: layerFading }"
          ></div>
        </div>
      </main>

      <!-- ========= 右侧工具组：说明卡（上） + 转盘/溯回（下），固定在右下角 ========= -->
      <div class="tool-group">
        <!-- 因子说明卡：绝对定位在转盘正上方 -->
        <transition name="info-fade">
          <div
            v-if="showInfoCard"
            key="'info-'+(activeFactorId||'c')"
            class="factor-info"
          >
            <button class="info-close" @click="infoClosed = true" aria-label="关闭说明">×</button>
            <div class="factor-info-title">{{ currentConfig.name }}适宜性</div>
            <div class="factor-info-desc">{{ currentConfig.desc }}</div>
          </div>
        </transition>

        <!-- 转盘：右下角固定 -->
        <div
          v-if="viewMode === 'detail'"
          class="wheel-area"
        >
          <div class="wheel-wrap">
            <div class="wheel">
              <svg viewBox="-110 -110 220 220" class="wheel-svg">
                <defs>
                  <filter id="ch2-sector-glow" x="-60%" y="-60%" width="220%" height="220%">
                    <feGaussianBlur stdDeviation="3" result="b1" />
                    <feMerge>
                      <feMergeNode in="b1" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                  <radialGradient id="ch2-lock-highlight" cx="50%" cy="50%" r="50%">
                    <stop offset="0%"   stop-color="rgba(255,255,255,0.45)" />
                    <stop offset="60%"  stop-color="rgba(255,245,200,0.12)" />
                    <stop offset="100%" stop-color="rgba(255,245,200,0)" />
                  </radialGradient>
                </defs>
                <circle cx="0" cy="0" r="92" fill="none" stroke="#B2A67D" stroke-width="0.7" opacity="0.7"/>
                <circle cx="0" cy="0" r="60" fill="none" stroke="#B2A67D" stroke-width="0.4" stroke-dasharray="2 3" opacity="0.5"/>
                <g v-for="(fid, i) in WHEEL_ORDER" :key="'sec-'+fid">
                  <path
                    :d="sectorPath(i, 10, 88)"
                    :fill="WHEEL_SECTOR_COLORS[fid]"
                    class="sector"
                    :class="SectorClass(fid)"
                  />
                  <path
                    v-if="lockedFactor === fid"
                    :d="sectorPath(i, 10, 90)"
                    fill="url(#ch2-lock-highlight)"
                    stroke="#EACF78"
                    stroke-width="1.6"
                    class="sector-lock-stroke"
                    filter="url(#ch2-sector-glow)"
                    :style="LockedSectorStyle(i)"
                    pointer-events="none"
                  />
                </g>
                <line
                  v-for="i in 5"
                  :key="'sep'+i"
                  :x1="Math.cos((i*72 - 90) * Math.PI/180) * 10"
                  :y1="Math.sin((i*72 - 90) * Math.PI/180) * 10"
                  :x2="Math.cos((i*72 - 90) * Math.PI/180) * 88"
                  :y2="Math.sin((i*72 - 90) * Math.PI/180) * 88"
                  stroke="rgba(139,125,90,0.5)"
                  stroke-width="0.5"
                />
              </svg>
              <div
                v-for="(fid, i) in WHEEL_ORDER"
                :key="'lbl-'+fid"
                class="factor-label"
                :style="labelStyle(i)"
                :class="{
                  'lbl-scan':   scanIndex === i && drawPhase === 'spinning',
                  'lbl-locked': lockedFactor === fid,
                  'lbl-picked': drawOrder.includes(fid) && lockedFactor !== fid,
                }"
              >
                <span class="label-name">{{ FACTORS[fid].name }}</span>
                <span
                  v-if="drawOrder.includes(fid) && lockedFactor !== fid"
                  class="picked-dot"
                ></span>
              </div>
            </div>
            <button
              class="center-btn"
              :class="{
                'ready-hl': drawPhase === 'complete',
                'busy':     drawPhase === 'spinning' || drawPhase === 'committing',
              }"
              :disabled="btnDisabled"
              @click.stop="onCenterClick"
            >
              <div class="center-text">{{ centerText }}</div>
            </button>
          </div>
        </div>

        <!-- 综合分析状态下的溯回按钮：右下角，取代转盘 -->
        <div v-if="viewMode === 'composite'" class="return-area">
          <button class="return-btn" @click="onReturn">溯回</button>
        </div>
      </div>
    </div>

    <!-- ========= 固定定位动画覆盖层（主图↔缩略图的位移/缩放/圆角/阴影过渡） ========= -->
    <div
      v-for="layer in _flipLayers"
      :key="layer.id"
      class="flip-overlay-fixed"
      :style="layer.style"
    >
      <img :src="layer.png" />
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick, shallowRef } from 'vue'
import L from 'leaflet'
import ChapterIntro from './ChapterIntro.vue'
import {
  FACTORS, COMPOSITE,
  PROV_BG_URL, PROV_STYLE,
  PROV_FILL_STYLE, PROV_STROKE_STYLE,
  OUTLINE_URL, TENDASH_URL,
  OUTLINE_STYLE, TENDASH_STYLE,
  FULL_CHINA_BOUNDS, THUMBNAIL_DISPLAY_BOUNDS, TOOL_GROUP_SAFE_WIDTH,
  loadFactorBounds,
} from '../config/ch2.js'
import { getMapOptions } from '../utils/crs.js'

const WHEEL_ORDER = ['ph', 'precip', 'temp', 'accum', 'rad']
const WHEEL_SECTOR_COLORS = {
  ph:     '#516D33',
  precip: '#5C7C3A',
  temp:   '#5C9EAF',
  accum:  '#B28F4C',
  rad:    '#C3C19A',
}

/* =========================================================
 * 章节状态
 * ========================================================= */
const introDone   = ref(false)
const layoutReady = ref(false)
const mapReady    = ref(false)

function onIntroDone() {
  introDone.value = true
  nextTick(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(async () => {
        await initMapAndFit()
        layoutReady.value = true
        nextTick(() => { if (map) map.invalidateSize(false) })
      })
    })
  })
}

/* =========================================================
 * 有限状态机
 * ========================================================= */
const drawPhase = ref(/** @type {'idle'|'ready'|'spinning'|'committing'|'complete'|'comprehensive'} */ ('idle'))
const drawOrder = ref([])
const selectedFactors = ref(new Set())
const activeFactorId = ref(null)
const lastDrawnFactorId = ref(null)
const viewMode = ref(/** @type {'detail'|'composite'} */ ('detail'))
const infoClosed = ref(false)

const isVisualLocked = ref(false)

// 说明卡：只有切换到新因子才重新显示；用户主动×后保持隐藏直到因子变化
const showInfoCard = computed(() => {
  if (viewMode.value !== 'detail') return false
  if (!activeFactorId.value) return false
  return !infoClosed.value
})
// 因子变化时，解除关闭状态（让说明卡重新出现）
watch(activeFactorId, () => {
  infoClosed.value = false
})

const isDrawComplete = computed(() => drawOrder.value.length >= 5)

const remainingFactors = computed(() => {
  const set = new Set(drawOrder.value)
  return WHEEL_ORDER.filter(f => !set.has(f))
})

// 新 thumbSlot 规则：detail 模式下 = drawOrder 中除 activeFactorId 外按顺序；
//                  composite 模式下 = 全部 5 张
const thumbSlot = computed(() => {
  if (viewMode.value === 'composite') return [...drawOrder.value]
  return drawOrder.value.filter(fid => fid !== activeFactorId.value)
})

const currentConfig = computed(() => {
  if (viewMode.value === 'composite') return COMPOSITE
  if (!activeFactorId.value) return null
  return FACTORS[activeFactorId.value]
})

const showLegend = computed(() => {
  if (viewMode.value === 'composite') return true
  return !!activeFactorId.value
})
const legendTitle = computed(() => {
  if (viewMode.value === 'composite') return '综合分级'
  return currentConfig.value?.name ?? ''
})
const legendLevels = computed(() => {
  if (viewMode.value === 'composite') return COMPOSITE.levels
  return currentConfig.value?.levels ?? []
})

const btnDisabled = computed(() => {
  return drawPhase.value === 'spinning'
      || drawPhase.value === 'committing'
      || isVisualLocked.value
})
const centerText = computed(() => {
  if (drawPhase.value === 'spinning' || drawPhase.value === 'committing') return '抽取中'
  if (viewMode.value === 'composite') return '综合分析'
  if (drawPhase.value === 'complete') return '综合分析'
  if (drawOrder.value.length === 0) return '开始'
  return '继续抽取'
})

/* =========================================================
 * 转盘扫描 & 动画控制
 * ========================================================= */
const scanIndex    = ref(-1)
const lockedFactor = ref(null)
const layerFading  = ref(false)
const _thumbEnterKey = ref(0)

let _opId = 0
let _currentOpId = 0
let _spinTimers = []
let _hardKillTimer = null
let _flipIdCounter = 0
const _flipLayers = shallowRef([])   // 固定定位动画层列表
let _flipCleanupTimers = []
let _resizeTimer = null

// 缩略图缓存：key = `${fid}__v${version}` → dataURL
// _thumbCacheVersion 在每次组件挂载时自增, 保证旧版本缓存失效。
const _thumbCacheVersion = { v: 7 }
const _thumbCache = reactive({})

function _thumbKey(fid) {
  return `${fid}__v${_thumbCacheVersion.v}`
}
function _getThumb(fid) {
  return _thumbCache[_thumbKey(fid)] || ''
}
function _setThumb(fid, dataUrl) {
  _thumbCache[_thumbKey(fid)] = dataUrl
}
function _hasThumb(fid) {
  return !!_thumbCache[_thumbKey(fid)]
}
function _clearAllThumbs() {
  Object.keys(_thumbCache).forEach(k => { delete _thumbCache[k] })
}

function clearSpinTimers() {
  _spinTimers.forEach(t => clearTimeout(t))
  _spinTimers = []
}
function addTimer(fn, ms) {
  const h = setTimeout(fn, ms)
  _spinTimers.push(h)
  return h
}
function clearHardKill() {
  if (_hardKillTimer) { clearTimeout(_hardKillTimer); _hardKillTimer = null }
}

/* =========================================================
 * GeoJSON 数据缓存（避免重复 fetch）
 * ========================================================= */
let _provDataCache = null
let _outlineDataCache = null
let _tendashDataCache = null

async function _getProvData() {
  if (!_provDataCache) {
    const res = await fetch(PROV_BG_URL)
    _provDataCache = await res.json()
  }
  return _provDataCache
}
async function _getOutlineData() {
  if (!_outlineDataCache) {
    try {
      const res = await fetch(OUTLINE_URL)
      _outlineDataCache = await res.json()
    } catch (e) {
      console.warn('[ch2] outline data fetch failed:', e)
      _outlineDataCache = null
    }
  }
  return _outlineDataCache
}
async function _getTendashData() {
  if (!_tendashDataCache) {
    try {
      const res = await fetch(TENDASH_URL)
      _tendashDataCache = await res.json()
    } catch (e) {
      console.warn('[ch2] tendash data fetch failed:', e)
      _tendashDataCache = null
    }
  }
  return _tendashDataCache
}

/* =========================================================
 * 共享图层添加函数（主图和缩略图渲染器共用）
 *
 * 图层顺序（从下到上）：
 *   1. ch2Base pane  (zIndex 200) → 省级行政区底图（fill）
 *   2. overlayPane   (zIndex 400) → 因子重分类 ImageOverlay
 *   3. ch2Border pane(zIndex 450) → 省级边界线 + 国界 + 九段线
 * ========================================================= */
const COORDS_TO_LATLNG = coords => new L.LatLng(coords[1], coords[0], true)

async function _addProvFillLayer(m) {
  const data = await _getProvData()
  return L.geoJSON(data, {
    pane: 'ch2Base',
    style: () => ({ ...PROV_FILL_STYLE }),
    coordsToLatLng: COORDS_TO_LATLNG,
    interactive: false,
  }).addTo(m)
}
async function _addProvStrokeLayer(m) {
  const data = await _getProvData()
  return L.geoJSON(data, {
    pane: 'ch2Border',
    style: () => ({ ...PROV_STROKE_STYLE }),
    coordsToLatLng: COORDS_TO_LATLNG,
    interactive: false,
  }).addTo(m)
}
async function _addOutlineLayer(m) {
  const data = await _getOutlineData()
  if (!data) return null
  return L.geoJSON(data, {
    pane: 'ch2Border',
    style: () => ({ ...OUTLINE_STYLE }),
    coordsToLatLng: COORDS_TO_LATLNG,
    interactive: false,
  }).addTo(m)
}
async function _addTendashLayer(m) {
  const data = await _getTendashData()
  if (!data) return null
  return L.geoJSON(data, {
    pane: 'ch2Border',
    style: () => ({ ...TENDASH_STYLE }),
    coordsToLatLng: COORDS_TO_LATLNG,
    interactive: false,
  }).addTo(m)
}
async function _addFactorOverlay(m, fid) {
  const cfg = fid === 'composite' ? COMPOSITE : FACTORS[fid]
  if (!cfg) return null
  const bounds = await loadFactorBounds(fid)
  const layer = L.imageOverlay(cfg.png, bounds, {
    opacity: 1, interactive: false, crossOrigin: true,
  }).addTo(m)
  // 等待图片加载完成
  await new Promise(resolve => {
    const img = layer.getElement()
    if (img && img.complete && img.naturalWidth > 0) {
      resolve()
    } else if (img) {
      img.onload = resolve
      img.onerror = resolve
      setTimeout(resolve, 3000)
    } else {
      setTimeout(resolve, 500)
    }
  })
  return layer
}

/* =========================================================
 * 右侧安全区宽度计算
 * ========================================================= */
function _getSafetyRight() {
  const vw = window.innerWidth
  if (vw <= 900) return 260
  if (vw <= 1200) return 300
  return TOOL_GROUP_SAFE_WIDTH
}

/* =========================================================
 * Leaflet 主地图
 * ========================================================= */
const mapRef = ref(null)
let map = null
let provFillLayer = null
let provStrokeLayer = null
let outlineLayer = null
let tendashLayer = null
let factorLayer = null

async function initMapAndFit() {
  if (map) return
  const opts = getMapOptions()
  map = L.map(mapRef.value, { ...opts, zoomControl: true, attributionControl: false })

  // 创建自定义 pane：ch2Base (省填充) 在因子图层下方，ch2Border (省界+国界+九段线) 在因子图层上方
  map.createPane('ch2Base')
  map.getPane('ch2Base').style.zIndex = 200
  map.createPane('ch2Border')
  map.getPane('ch2Border').style.zIndex = 450

  // 省级填充（因子图层下方）
  try {
    provFillLayer = await _addProvFillLayer(map)
  } catch (e) { console.warn('[ch2] province fill failed:', e) }

  // 省级边界 + 国界 + 九段线（因子图层上方）
  try { provStrokeLayer = await _addProvStrokeLayer(map) } catch (e) { console.warn('[ch2] province stroke failed:', e) }
  try { outlineLayer = await _addOutlineLayer(map) } catch (e) { console.warn('[ch2] outline failed:', e) }
  try { tendashLayer = await _addTendashLayer(map) } catch (e) { console.warn('[ch2] tendash failed:', e) }

  map.invalidateSize(false)
  // 使用统一全国范围 + 右侧安全区 padding
  map.fitBounds(FULL_CHINA_BOUNDS, {
    paddingTopLeft: [50, 50],
    paddingBottomRight: [_getSafetyRight(), 60],
    animate: false,
  })
  setTimeout(() => { mapReady.value = true }, 80)

  // 窗口尺寸变化时重新计算安全区域
  window.addEventListener('resize', _onResize)
}

function _onResize() {
  if (_resizeTimer) clearTimeout(_resizeTimer)
  _resizeTimer = setTimeout(() => {
    if (!map) return
    map.invalidateSize(false)
    map.fitBounds(FULL_CHINA_BOUNDS, {
      paddingTopLeft: [50, 50],
      paddingBottomRight: [_getSafetyRight(), 60],
      animate: false,
    })
  }, 250)
}

async function updateFactorLayer() {
  if (!map) return
  if (factorLayer) { map.removeLayer(factorLayer); factorLayer = null }
  layerFading.value = false

  if (viewMode.value === 'composite') {
    layerFading.value = true
    await new Promise(r => setTimeout(r, 30))
    try {
      const bounds = await loadFactorBounds('composite')
      factorLayer = L.imageOverlay(COMPOSITE.png, bounds, {
        opacity: 0, interactive: false, crossOrigin: true,
      }).addTo(map)
      animateOpacity(factorLayer, 450)
      // 后台生成综合分析缩略图
      _generateThumbInBackground('composite')
    } catch (e) { layerFading.value = false }
    return
  }
  const fid = activeFactorId.value
  if (!fid) return
  layerFading.value = true
  await new Promise(r => setTimeout(r, 30))
  try {
    const cfg = FACTORS[fid]
    const bounds = await loadFactorBounds(fid)
    factorLayer = L.imageOverlay(cfg.png, bounds, {
      opacity: 0, interactive: false, crossOrigin: true,
    }).addTo(map)
    animateOpacity(factorLayer, 450)
    // 后台生成因子缩略图
    _generateThumbInBackground(fid)
  } catch (e) {
    console.warn('[ch2] factor overlay failed:', e)
    layerFading.value = false
  }
}

function animateOpacity(layer, dur) {
  const t0 = performance.now()
  const step = () => {
    if (!layer) return
    const p = Math.min(1, (performance.now() - t0) / dur)
    layer.setOpacity(p)
    if (p < 1) requestAnimationFrame(step)
    else layerFading.value = false
  }
  requestAnimationFrame(step)
}

watch([activeFactorId, viewMode], () => {
  if (mapReady.value) nextTick(updateFactorLayer)
})

/* =========================================================
 * 缩略图（完整地图合成图）生成器
 *
 * 使用单个固定尺寸离屏 Leaflet 地图实例生成所有缩略图。
 *   - 容器: 640×400 (16:10), position:fixed, left:-10000px, 不用 display:none
 *   - 与主图共享同一套 CRS、图层配置、loadFactorBounds
 *   - 加载顺序: 省填充 → 因子 ImageOverlay → 省界 → 国界 → 九段线
 *   - 关键: 等待 moveend 事件 + 2x requestAnimationFrame 后再导出
 *     (Leaflet 在 moveend 后才会把 SVG <g transform> 和 img translate3d 同步到新视图)
 *   - 通过 SVG 序列化 + Canvas 合成导出单张扁平化 PNG dataURL
 *   - 缓存到 _thumbCache[key], 供缩略图卡片和 FLIP 动画共用
 * ========================================================= */
const _thumbRenderer = {
  container: null,
  map: null,
  provFill: null,
  provStroke: null,
  outline: null,
  tendash: null,
  factor: null,
  initialized: false,
}

// 离屏容器固定尺寸（16:10 横向比例）
const THUMB_CONTAINER_W = 640
const THUMB_CONTAINER_H = 400
// 缩略图 fitBounds 内部 padding（水平 20px / 垂直 16px）
const THUMB_FIT_PADDING = [20, 16]

async function _ensureThumbRenderer() {
  if (_thumbRenderer.initialized) return _thumbRenderer

  // 创建隐藏容器: 640×400, position:fixed, 不能用 display:none (会导致 clientWidth=0)
  // visibility:visible 但 left:-10000px 移出视口, 保证布局真实
  const container = document.createElement('div')
  container.style.cssText =
    `position:fixed;left:-10000px;top:0;` +
    `width:${THUMB_CONTAINER_W}px;height:${THUMB_CONTAINER_H}px;` +
    `margin:0;padding:0;background:#EFE9DA;` +
    `pointer-events:none;visibility:visible;`
  document.body.appendChild(container)
  _thumbRenderer.container = container

  // 关键: 等待容器实际拥有 640×400 尺寸后再创建地图
  // (position:fixed 元素通常立即可布局, 但保险起见等一帧)
  await new Promise(r => requestAnimationFrame(() => r()))

  if (container.clientWidth !== THUMB_CONTAINER_W || container.clientHeight !== THUMB_CONTAINER_H) {
    console.warn('[ch2-thumb] container size mismatch before map init:',
      container.clientWidth, container.clientHeight, 'expected', THUMB_CONTAINER_W, THUMB_CONTAINER_H)
  }

  const opts = getMapOptions()
  const m = L.map(container, {
    ...opts,
    zoomControl: false,
    attributionControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
    fadeAnimation: false,
    zoomAnimation: false,
    markerZoomAnimation: false,
  })
  _thumbRenderer.map = m

  // 创建与主图相同的 pane
  m.createPane('ch2Base')
  m.getPane('ch2Base').style.zIndex = 200
  m.createPane('ch2Border')
  m.getPane('ch2Border').style.zIndex = 450

  // 加载基础图层（省填充 + 省界 + 国界 + 九段线）
  _thumbRenderer.provFill = await _addProvFillLayer(m)
  _thumbRenderer.provStroke = await _addProvStrokeLayer(m)
  _thumbRenderer.outline = await _addOutlineLayer(m)
  _thumbRenderer.tendash = await _addTendashLayer(m)

  // 初次定位: invalidateSize + fitBounds + 等待 moveend
  m.invalidateSize(false)
  await _fitBoundsAndWait(m, THUMBNAIL_DISPLAY_BOUNDS)

  _thumbRenderer.initialized = true
  return _thumbRenderer
}

/**
 * 执行 fitBounds 并等待地图完全稳定:
 *   1. invalidateSize(false)
 *   2. fitBounds(animate:false, padding)
 *   3. 等待 moveend 事件 (Leaflet 完成所有图层重定位的信号)
 *   4. 再等 2x requestAnimationFrame (DOM/CSS flush)
 *   5. 兜底超时 1500ms
 *
 * 必须在导出快照前调用, 否则 SVG <g transform> 与 img translate3d 可能仍是旧值。
 */
function _fitBoundsAndWait(m, bounds) {
  return new Promise(resolve => {
    let settled = false
    const finish = () => {
      if (settled) return
      settled = true
      // 2x rAF: 第一帧让 Leaflet 提交 DOM 变更, 第二帧让浏览器绘制
      requestAnimationFrame(() => {
        requestAnimationFrame(() => resolve())
      })
    }

    // moveend 是 Leaflet 完成视图重定位的权威信号
    const onMoveEnd = () => {
      m.off('moveend', onMoveEnd)
      finish()
    }
    m.on('moveend', onMoveEnd)

    m.invalidateSize(false)
    m.fitBounds(bounds, { animate: false, padding: THUMB_FIT_PADDING })

    // 兜底: 如果 800ms 内没 moveend (例如 bounds 未变化), 直接 finish
    setTimeout(() => { if (!settled) { m.off('moveend', onMoveEnd); finish() } }, 800)
  })
}

async function generateThumbnail(fid) {
  if (_hasThumb(fid)) return _getThumb(fid)
  if (!map) { console.warn('[ch2-thumb] main map not ready'); return null }

  const savedCenter = map.getCenter()
  const savedZoom = map.getZoom()

  try {
    map.invalidateSize(false)
    map.fitBounds(THUMBNAIL_DISPLAY_BOUNDS, { animate: false, padding: THUMB_FIT_PADDING })
    await _waitMapSettled(map)

    const container = map.getContainer()
    const controls = container.querySelectorAll('.leaflet-control-container')
    const prevDisplay = []
    controls.forEach(c => { prevDisplay.push({ el: c, display: c.style.display }); c.style.display = 'none' })

    const dataUrl = await _captureFromMap(map)

    prevDisplay.forEach(({ el, display }) => { el.style.display = display })

    if (dataUrl) {
      _setThumb(fid, dataUrl)
    } else {
      console.error('[ch2-thumb] capture failed for:', fid)
    }
  } finally {
    map.setView(savedCenter, savedZoom, { animate: false })
  }

  return _getThumb(fid) || null
}

/** 等待地图视图完全稳定 (moveend + 因子图层就绪) */
function _waitMapSettled(m) {
  return new Promise(resolve => {
    let settled = false
    const finish = () => { if (settled) return; settled = true; requestAnimationFrame(() => requestAnimationFrame(resolve)) }
    const onMoveEnd = () => { m.off('moveend zoomend', onMoveEnd); finish() }
    m.on('moveend zoomend', onMoveEnd)
    const checkFactor = () => {
      const c = m.getContainer()
      const img = c.querySelector('.leaflet-overlay-pane img.leaflet-image-layer')
      if (img && img.complete && img.naturalWidth > 0 && img.style.transform) { finish(); return }
      if (!settled) setTimeout(checkFactor, 80)
    }
    checkFactor()
    setTimeout(() => { if (!settled) { m.off('moveend zoomend', onMoveEnd); finish() } }, 2000)
  })
}

function _generateThumbInBackground(fid) {
  if (_hasThumb(fid)) return
  setTimeout(async () => {
    try { await generateThumbnail(fid) } catch (e) { console.warn('[ch2-thumb] bg failed:', fid, e) }
  }, 600)
}

/**
 * 从 Leaflet 地图实例栅格化导出单张 PNG。
 *
 * 策略: 以 .leaflet-map-pane 的 boundingRect 为统一参考系,
 * 按 Leaflet 图层 z-order 顺序 (tile → ch2Base → overlay → ch2Border)
 * 逐图层把 SVG / <img> 绘制到同一 canvas, 保证所有图层使用完全一致的
 * 相对像素坐标, 不会出现错位。
 */
async function _captureFromMap(m) {
  const container = m.getContainer()
  const w = container.clientWidth
  const h = container.clientHeight
  if (w === 0 || h === 0) { console.warn('[ch2-thumb] zero size'); return null }

  const mapPane = container.querySelector('.leaflet-map-pane')
  if (!mapPane) { console.warn('[ch2-thumb] no leaflet-map-pane'); return null }

  // 隐藏控件
  const controls = container.querySelectorAll('.leaflet-control-container')
  const prevDisplay = []
  controls.forEach(c => { prevDisplay.push({ el: c, display: c.style.display }); c.style.display = 'none' })

  // 统一参考系: mapPane 的 boundingRect
  const mpRect = mapPane.getBoundingClientRect()

  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')

  // 背景填充
  ctx.fillStyle = '#EFE9DA'
  ctx.fillRect(0, 0, w, h)

  try {
    // 绘制顺序: 与 Leaflet z-index 一致
    // 1) ch2Base pane (省填充)
    await _drawPaneByRect(mpRect, m, 'ch2Base', ctx)

    // 2) overlay-pane (因子数据 ImageOverlay)
    await _drawOverlayPane(mpRect, m, ctx)

    // 3) ch2Border pane (省界 + 国界 + 九段线)
    await _drawPaneByRect(mpRect, m, 'ch2Border', ctx)

    return canvas.toDataURL('image/png')
  } catch (e) {
    console.warn('[ch2-thumb] capture failed:', e)
    return null
  } finally {
    // 还原控件
    controls.forEach(({ el, display }) => { el.style.display = display })
  }
}

/**
 * 绘制指定 pane (SVG) 到 canvas, 所有坐标相对 mapPane 参考系。
 */
function _drawPaneByRect(mpRect, m, paneName, ctx) {
  return new Promise(resolve => {
    const pane = m.getPane(paneName)
    if (!pane) { resolve(); return }

    const svgEl = pane.querySelector('svg')
    if (!svgEl) { resolve(); return }

    // 使用 pane 相对于 mapPane 的位置
    const paneRect = pane.getBoundingClientRect()
    const x = paneRect.left - mpRect.left
    const y = paneRect.top - mpRect.top
    const rw = paneRect.width
    const rh = paneRect.height
    if (rw <= 0 || rh <= 0) { resolve(); return }

    const clone = svgEl.cloneNode(true)
    clone.setAttribute('width', rw)
    clone.setAttribute('height', rh)
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
    clone.setAttribute('preserveAspectRatio', 'none')

    // 注入关键 CSS, 使序列化后的 SVG 正确渲染
    const styleBlock = document.createElement('style')
    styleBlock.textContent = `
      .leaflet-pane { position: absolute; }
      .leaflet-overlay-pane img { pointer-events: none; }
      svg.leaflet-zoom-box { position: absolute; }
    `
    clone.insertBefore(styleBlock, clone.firstChild)

    const svgStr = new XMLSerializer().serializeToString(clone)
    const svgUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgStr)

    const img = new Image()
    img.onload = () => {
      ctx.drawImage(img, x, y, rw, rh)
      resolve()
    }
    img.onerror = () => {
      console.warn('[ch2-thumb] pane load error:', paneName)
      resolve()
    }
    img.src = svgUrl
  })
}

/**
 * 绘制 overlay-pane 中的因子 ImageOverlay <img> 到 canvas。
 * 使用与 SVG pane 相同的 mpRect 参考系, 确保坐标对齐。
 */
function _drawOverlayPane(mpRect, m, ctx) {
  return new Promise(resolve => {
    const container = m.getContainer()
    const img = container.querySelector('.leaflet-overlay-pane img.leaflet-image-layer')
    if (!img) { resolve(); return }
    if (!img.complete || img.naturalWidth === 0) {
      // 等待图片加载完成
      const onLoad = () => {
        img.removeEventListener('load', onLoad)
        drawIt()
      }
      img.addEventListener('load', onLoad)
      setTimeout(() => { img.removeEventListener('load', onLoad); drawIt() }, 3000)
      return
    }

    drawIt()

    function drawIt() {
      const r = img.getBoundingClientRect()
      const x = r.left - mpRect.left
      const y = r.top - mpRect.top
      const rw = r.width
      const rh = r.height
      if (rw <= 0 || rh <= 0) { resolve(); return }

      ctx.drawImage(img, x, y, rw, rh)
      resolve()
    }
  })
}

/** 模板辅助：获取缓存的缩略图 dataURL */
function thumbSrc(fid) {
  if (!fid) return ''
  return _getThumb(fid)
}

/* =========================================================
 * 转盘 SVG 几何
 * ========================================================= */
function sectorPath(index, innerR, outerR) {
  const startAngle = index * 72 - 90 + 1.2
  const endAngle   = startAngle + 72 - 2.4
  const toRad = d => d * Math.PI / 180
  const s1 = { x: Math.cos(toRad(startAngle)) * outerR, y: Math.sin(toRad(startAngle)) * outerR }
  const e1 = { x: Math.cos(toRad(endAngle))   * outerR, y: Math.sin(toRad(endAngle))   * outerR }
  const e2 = { x: Math.cos(toRad(endAngle))   * innerR, y: Math.sin(toRad(endAngle))   * innerR }
  const s2 = { x: Math.cos(toRad(startAngle)) * innerR, y: Math.sin(toRad(startAngle)) * innerR }
  return `M ${s1.x} ${s1.y} A ${outerR} ${outerR} 0 0 1 ${e1.x} ${e1.y} L ${e2.x} ${e2.y} A ${innerR} ${innerR} 0 0 0 ${s2.x} ${s2.y} Z`
}
function sectorCenterAngle(index) { return (index * 72 - 90 + 36) * Math.PI / 180 }
function SectorClass(fid) {
  const isScan = drawPhase.value === 'spinning' && WHEEL_ORDER[scanIndex.value] === fid
  const isPicked = drawOrder.value.includes(fid)
  return {
    'sec-scan':   isScan,
    'sec-picked': isPicked && lockedFactor.value !== fid,
  }
}
function LockedSectorStyle(i) {
  const ang = sectorCenterAngle(i)
  const tx = Math.cos(ang) * 8
  const ty = Math.sin(ang) * 8
  return {
    transform: `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(1.03)`,
    transformOrigin: '0 0',
    animation: 'sector-lock-bounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both',
  }
}
function labelStyle(index) {
  const ang = sectorCenterAngle(index)
  const r = 70
  const x = Math.cos(ang) * r
  const y = Math.sin(ang) * r
  const pctX = 50 + (x / 110) * 50
  const pctY = 50 + (y / 110) * 50
  return { left: `${pctX}%`, top: `${pctY}%`, transform: 'translate(-50%, -50%)' }
}

/* =========================================================
 * 抽取流程
 * ========================================================= */
function pickRandomTargetIndex() {
  const remain = remainingFactors.value
  if (remain.length === 0) return -1
  const targetFid = remain[Math.floor(Math.random() * remain.length)]
  return WHEEL_ORDER.indexOf(targetFid)
}
function buildScanSequence(targetIndex) {
  const steps = []
  let cur = 0
  for (let i = 0; i < 14; i++) { steps.push({ idx: cur, delay: 80 }); cur = (cur + 1) % 5 }
  for (let i = 0; i < 6; i++)  { steps.push({ idx: cur, delay: 135 }); cur = (cur + 1) % 5 }
  const phase3Delays = [180, 240, 320, 420, 520, 640]
  let remainingSteps = (targetIndex - cur + 5) % 5
  if (remainingSteps < 5) remainingSteps += 5
  let p3i = 0
  for (let i = 0; i < remainingSteps; i++) {
    steps.push({ idx: cur, delay: phase3Delays[Math.min(p3i, phase3Delays.length - 1)] })
    cur = (cur + 1) % 5
    p3i++
  }
  if (steps.length) steps[steps.length - 1].idx = targetIndex
  return steps
}
async function runSpinSequence(steps, myOpId) {
  let acc = 0
  for (let s = 0; s < steps.length; s++) {
    acc += steps[s].delay
    const sIdx = s
    addTimer(() => {
      if (_currentOpId !== myOpId) return
      if (drawPhase.value !== 'spinning') return
      scanIndex.value = steps[sIdx].idx
    }, acc)
  }
  await new Promise(res => {
    acc += 80
    addTimer(() => { if (_currentOpId === myOpId) res(true); else res(false) }, acc)
  })
}

/* =========================================================
 * 固定定位 FLIP 动画工具
 *   - 先测量 sourceRect、targetRect（在 activeFactorId 改变之前）
 *   - 创建一个 position: fixed 的动画层，初始尺寸与主图完全相同
 *   - 一个 requestAnimationFrame 后，对 left/top/width/height + borderRadius + boxShadow 做 800ms 过渡
 *   - 过渡开始约 250ms 后，新图淡入
 *   - Promise.race([动画 850ms, 超时 1200ms]) 确保最终清理
 * ========================================================= */
function _makeFlipLayerId() { return 'fl' + (++_flipIdCounter) }
function _getThumbSlotRect(slotIndex0Based) {
  const el = document.querySelector('.thumb-slot-' + (slotIndex0Based + 1))
  if (!el) return null
  return el.getBoundingClientRect()
}
function _getMainStageRect() {
  const el = mapRef.value?.closest('.map-stage')
  if (!el) return null
  return el.getBoundingClientRect()
}

/**
 * 获取因子缩略图 dataURL（优先用缓存，否则同步生成）
 */
async function _ensureThumbPng(fid) {
  if (_hasThumb(fid)) return _getThumb(fid)
  // 后台尚未生成完成，等待最多 3 秒
  try {
    const result = await Promise.race([
      generateThumbnail(fid),
      _sleep(3000).then(() => null),
    ])
    if (result) return result
  } catch (e) {
    console.warn('[ch2] _ensureThumbPng failed:', fid, e)
  }
  return null
}

function _pushFlipLayer({ fid, png, sourceRect, targetRect }) {
  const id = _makeFlipLayerId()
  const layer = {
    id,
    png,
    fid,
    style: {
      position: 'fixed',
      left:   sourceRect.left + 'px',
      top:    sourceRect.top  + 'px',
      width:  sourceRect.width  + 'px',
      height: sourceRect.height + 'px',
      borderRadius: '2px',
      boxShadow: '0 2px 8px rgba(81,109,51,0.0)',
      overflow: 'hidden',
      pointerEvents: 'none',
      zIndex: 99999,
      transition: 'none',
    },
  }
  _flipLayers.value = [..._flipLayers.value, layer]

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      layer.style = {
        position: 'fixed',
        left:   targetRect.left + 'px',
        top:    targetRect.top  + 'px',
        width:  targetRect.width  + 'px',
        height: targetRect.height + 'px',
        borderRadius: '10px',
        boxShadow: '0 2px 8px rgba(81,109,51,0.12)',
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 99999,
        transition:
          'left 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
          'top 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
          'width 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
          'height 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
          'border-radius 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
          'box-shadow 800ms cubic-bezier(0.22, 1, 0.36, 1)',
      }
      _flipLayers.value = [..._flipLayers.value]
    })
  })

  return id
}
function _removeFlipLayer(id) {
  _flipLayers.value = _flipLayers.value.filter(x => x.id !== id)
}
function _sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

/**
 * 执行主图归档动画：从主图位置 -> 第 N 个缩略图卡槽
 * 调用时机：在 activeFactorId / viewMode 改变 **之前** 调用
 * 返回 Promise：动画结束或 1200ms 超时后 resolve（永远 resolve，不抛错）
 */
async function playArchiveAnimation({ fid, targetSlotIndex0Based }) {
  const sourceRect = _getMainStageRect()
  if (!sourceRect) return { ok: false }

  const targetRect = _getThumbSlotRect(targetSlotIndex0Based)
  if (!targetRect) return { ok: false }

  // 使用缓存的完整缩略图（包含行政底图+因子+省界+国界+九段线）
  const png = await _ensureThumbPng(fid)
  if (!png) {
    console.warn('[ch2] archive animation: thumbnail not available for', fid)
    return { ok: false }
  }

  const layerId = _pushFlipLayer({ fid, png, sourceRect, targetRect })

  const cleanup = () => _removeFlipLayer(layerId)
  try {
    await Promise.race([_sleep(850), _sleep(1200)])
  } finally {
    cleanup()
  }
  return { ok: true }
}

/**
 * 缩略图点击 -> 主图放大动画（source=thumbSlot, target=mainStage）
 * 同时把当前主图做一次归档动画到它未来的缩略图槽（双向）
 */
async function playThumbToMainAnimations({ clickedFid, currentActiveFid, futureDrawOrder, futureView }) {
  const futureThumb = futureView === 'composite'
    ? [...futureDrawOrder]
    : futureDrawOrder.filter(x => x !== clickedFid)

  const clickedSourceIdx = thumbSlot.value.indexOf(clickedFid)
  const currentActiveTargetIdx = futureThumb.indexOf(currentActiveFid)
  const mainRect = _getMainStageRect()

  if (!mainRect) return null

  const layerIds = []
  const cleanupAll = () => layerIds.forEach(id => _removeFlipLayer(id))

  try {
    // Layer A: clicked 缩略图放大到主图
    if (clickedSourceIdx >= 0) {
      const srcRect = _getThumbSlotRect(clickedSourceIdx)
      const srcPng = await _ensureThumbPng(clickedFid)
      if (srcRect && srcPng) {
        const id = _makeFlipLayerId()
        const layer = {
          id, png: srcPng, fid: clickedFid,
          style: {
            position: 'fixed',
            left:   srcRect.left + 'px', top: srcRect.top + 'px',
            width:  srcRect.width + 'px', height: srcRect.height + 'px',
            borderRadius: '10px',
            boxShadow: '0 2px 8px rgba(81,109,51,0.12)',
            overflow: 'hidden', pointerEvents: 'none', zIndex: 99999, transition: 'none',
          },
        }
        _flipLayers.value = [..._flipLayers.value, layer]
        layerIds.push(id)
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            layer.style = {
              position: 'fixed',
              left:   mainRect.left + 'px', top: mainRect.top + 'px',
              width:  mainRect.width + 'px', height: mainRect.height + 'px',
              borderRadius: '2px',
              boxShadow: '0 2px 8px rgba(81,109,51,0.0)',
              overflow: 'hidden', pointerEvents: 'none', zIndex: 99999,
              transition:
                'left 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
                'top 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
                'width 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
                'height 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
                'border-radius 800ms cubic-bezier(0.22, 1, 0.36, 1),' +
                'box-shadow 800ms cubic-bezier(0.22, 1, 0.36, 1)',
            }
            _flipLayers.value = [..._flipLayers.value]
          })
        })
      }
    }

    // Layer B: currentActiveFid（原主图）归档到 futureThumb 中它对应的缩略图槽
    if (currentActiveTargetIdx >= 0 && currentActiveFid && currentActiveFid !== clickedFid) {
      const targetRect = _getThumbSlotRect(currentActiveTargetIdx)
      const png = await _ensureThumbPng(currentActiveFid)
      if (targetRect && png) {
        const id = _pushFlipLayer({
          fid: currentActiveFid,
          png,
          sourceRect: mainRect,
          targetRect,
        })
        layerIds.push(id)
      }
    }

    await Promise.race([_sleep(850), _sleep(1200)])
  } finally {
    cleanupAll()
  }
  return true
}

/* =========================================================
 * 抽取主流程（状态机保持稳定）
 * ========================================================= */
async function runSpinAnimation() {
  if (drawPhase.value === 'spinning' || drawPhase.value === 'committing') return
  if (isDrawComplete.value) return
  if (viewMode.value === 'composite') return
  if (isVisualLocked.value) return

  const targetIndex = pickRandomTargetIndex()
  if (targetIndex < 0) return

  const myOpId = ++_opId
  _currentOpId = myOpId
  clearSpinTimers(); clearHardKill()

  const newFid = WHEEL_ORDER[targetIndex]
  const previousActive = activeFactorId.value

  drawPhase.value = 'spinning'
  scanIndex.value = -1
  lockedFactor.value = null
  isVisualLocked.value = true

  try {
    const steps = buildScanSequence(targetIndex)
    const hardKillPromise = new Promise(res => {
      _hardKillTimer = setTimeout(() => {
        if (_currentOpId === myOpId) { console.warn('[ch2] draw hard-kill (5.5s): force commit'); res('timeout') }
      }, 5500)
    })
    const raceRes = await Promise.race([runSpinSequence(steps, myOpId), hardKillPromise])
    if (_currentOpId !== myOpId) return

    drawPhase.value = 'committing'
    lockedFactor.value = newFid
    scanIndex.value = -1

    // 播放旧主图归档动画（如果存在 previousActive）
    if (previousActive && previousActive !== newFid) {
      const futureDrawOrder = [...drawOrder.value, newFid]
      const futureThumb     = futureDrawOrder.filter(x => x !== newFid)
      const targetSlotIdx   = futureThumb.indexOf(previousActive)

      if (targetSlotIdx >= 0) {
        const animPromise = playArchiveAnimation({
          fid: previousActive,
          targetSlotIndex0Based: targetSlotIdx,
        })
        await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r())))
        animPromise.catch(() => {})
      } else {
        await new Promise(r => requestAnimationFrame(() => r()))
      }
    }

    // 提交业务状态（原子化，同步）
    selectedFactors.value = new Set([...selectedFactors.value, newFid])
    drawOrder.value = [...drawOrder.value, newFid]
    lastDrawnFactorId.value = newFid
    activeFactorId.value = newFid
    if (map) map.invalidateSize(false)

    if (isDrawComplete.value) drawPhase.value = 'complete'
    else drawPhase.value = 'ready'
  } catch (e) {
    console.error('[ch2] draw error:', e)
    if (_currentOpId === myOpId) {
      if (!drawOrder.value.includes(newFid)) {
        selectedFactors.value = new Set([...selectedFactors.value, newFid])
        drawOrder.value = [...drawOrder.value, newFid]
        lastDrawnFactorId.value = newFid
        activeFactorId.value = newFid
        if (map) map.invalidateSize(false)
      }
      if (isDrawComplete.value) drawPhase.value = 'complete'
      else drawPhase.value = 'ready'
    }
  } finally {
    if (_currentOpId === myOpId) {
      setTimeout(() => {
        if (_currentOpId === myOpId) {
          clearHardKill(); clearSpinTimers()
          isVisualLocked.value = false
          if (drawPhase.value === 'spinning' || drawPhase.value === 'committing') {
            drawPhase.value = isDrawComplete.value ? 'complete' : 'ready'
          }
        }
      }, 820)
    }
  }
}

/* =========================================================
 * 缩略图点击（双向动画）
 * ========================================================= */
function onThumbClick(targetFid) {
  if (btnDisabled.value) return
  if (viewMode.value !== 'detail') return
  if (targetFid === activeFactorId.value) return
  if (!drawOrder.value.includes(targetFid)) return

  const myOpId = ++_opId
  _currentOpId = myOpId
  clearSpinTimers(); clearHardKill()

  isVisualLocked.value = true

  const currentActive = activeFactorId.value
  const futureDrawOrder = [...drawOrder.value]
  const futureThumb = futureDrawOrder.filter(x => x !== targetFid)

  Promise.resolve()
    .then(() => playThumbToMainAnimations({
      clickedFid: targetFid,
      currentActiveFid: currentActive,
      futureDrawOrder,
      futureView: 'detail',
    }))
    .catch(() => {})

  setTimeout(() => {
    if (_currentOpId !== myOpId) return
    activeFactorId.value = targetFid
    if (map) map.invalidateSize(false)
  }, 220)

  setTimeout(() => {
    if (_currentOpId !== myOpId) return
    isVisualLocked.value = false
  }, 900)
}

/* =========================================================
 * 中心按钮 & 综合分析 & 溯回
 * ========================================================= */
function onCenterClick() {
  if (btnDisabled.value) return
  if (viewMode.value === 'composite') return
  if (isDrawComplete.value) { enterComposite(); return }
  runSpinAnimation()
}

async function enterComposite() {
  if (drawOrder.value.length < 5) return
  const myOpId = ++_opId
  _currentOpId = myOpId
  isVisualLocked.value = true

  try {
    drawPhase.value = 'comprehensive'

    // 在切换 viewMode/activeFactorId 之前，播放第五个因子主图 → thumb5 归档动画
    const fifthFid = activeFactorId.value
    if (fifthFid) {
      const targetSlotIdx = drawOrder.value.indexOf(fifthFid)
      if (targetSlotIdx === 4) {
        Promise.resolve()
          .then(() => playArchiveAnimation({
            fid: fifthFid,
            targetSlotIndex0Based: 4,
          }))
          .catch(() => {})
        await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r())))
      }
    }

    viewMode.value = 'composite'
    activeFactorId.value = null
    nextTick(() => {
      if (_currentOpId !== myOpId) return
      if (map) map.invalidateSize(false)
      setTimeout(() => {
        if (_currentOpId !== myOpId) return
        isVisualLocked.value = false
      }, 420)
    })
  } catch (e) {
    console.error('[ch2] enterComposite error:', e)
    isVisualLocked.value = false
  }
}

function onReturn() {
  if (drawOrder.value.length < 5) return
  const fifthFid = drawOrder.value[4]
  viewMode.value = 'detail'
  activeFactorId.value = fifthFid
  drawPhase.value = 'complete'
  nextTick(() => { if (map) map.invalidateSize(false) })
}

/* =========================================================
 * 生命周期
 * ========================================================= */
onBeforeUnmount(() => {
  clearSpinTimers(); clearHardKill()
  _flipCleanupTimers.forEach(h => clearTimeout(h))
  _flipCleanupTimers = []
  if (_resizeTimer) { clearTimeout(_resizeTimer); _resizeTimer = null }
  window.removeEventListener('resize', _onResize)
  // 清理离屏缩略图渲染器
  if (_thumbRenderer.map) {
    _thumbRenderer.map.remove()
    _thumbRenderer.map = null
  }
  if (_thumbRenderer.container) {
    _thumbRenderer.container.remove()
    _thumbRenderer.container = null
  }
  _thumbRenderer.initialized = false
  // 清空缩略图缓存并递增版本号, 下次挂载时旧 key 全部失效
  _clearAllThumbs()
  _thumbCacheVersion.v++
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
/* =========================================================
 * 章节整体：统一米白浅茶色背景
 * ========================================================= */
.chapter-2 { position: relative; background: #EFE9DA; }

.chapter-body {
  position: fixed;
  top: 60px;
  left: 0; right: 0; bottom: 0;
  display: grid;
  grid-template-columns: clamp(420px, 24vw, 520px) 1fr;
  grid-template-areas: "left main";
  padding: 20px clamp(20px, 3vw, 32px) 16px 20px;
  gap: clamp(16px, 2vw, 24px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.8s ease;
  background: #EFE9DA;
}
.chapter-body.ready { opacity: 1; pointer-events: auto; }

/* ===== 左侧：六宫格（2列 × 3行，顶部对齐；行宽相等，缩略图地图区域比例 16:10） ===== */
.left-panel {
  grid-area: left;
  display: flex;
  align-items: flex-start;
  min-height: 0;
  padding-top: 4px;
}
.six-grid {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-auto-rows: auto;
  grid-template-areas:
    "thumb1 thumb2"
    "thumb3 thumb4"
    "thumb5 legend";
  column-gap: 14px;
  row-gap: 14px;
  align-content: start;
  justify-content: start;
}
.grid-slot {
  position: relative;
  min-width: 0;
  width: 100%;
  aspect-ratio: 16 / 10;
}
.thumb-slot-1 { grid-area: thumb1; }
.thumb-slot-2 { grid-area: thumb2; }
.thumb-slot-3 { grid-area: thumb3; }
.thumb-slot-4 { grid-area: thumb4; }
.thumb-slot-5 { grid-area: thumb5; }
.legend-slot   { grid-area: legend; }

/* 缩略图卡片（地图区域 16:10 + 名称栏 32px） */
.thumb-card {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  background: rgba(255, 253, 247, 0.40);
  border: 1px solid rgba(81, 109, 51, 0.10);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.22s ease, border-color 0.22s ease, background 0.22s ease, box-shadow 0.22s ease;
  box-shadow: 0 1px 3px rgba(81,109,51,0.05);
}
.thumb-card:hover {
  transform: translateY(-1px);
  border-color: rgba(81, 109, 51, 0.32);
  background: rgba(255, 253, 247, 0.62);
  box-shadow: 0 4px 10px rgba(81,109,51,0.12);
}
/* 地图图像区域（thumbnail-map-viewport）：严格水平+垂直居中，不裁切 */
.thumb-img-wrap {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #EFE9DA;
}
.thumb-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center center;
  display: block;
  transform: none;
  margin: 0;
  max-width: 100%;
  max-height: 100%;
}
.thumb-label {
  flex: 0 0 32px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 10px;
  background: rgba(255, 253, 247, 0.45);
  border-top: 1px solid rgba(81, 109, 51, 0.06);
}
.thumb-order {
  font-size: 10px;
  color: #6b5d3c;
  font-weight: 700;
  width: 14px; height: 14px;
  line-height: 14px;
  text-align: center;
  border-radius: 50%;
  background: rgba(81, 109, 51, 0.11);
}
.thumb-name {
  font-size: 11.5px;
  color: #4e4328;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 图例：嵌入固定 16:10 槽位 */
.legend-inner {
  position: absolute;
  left: 0; right: 0; top: 0; bottom: 0;
  padding: 12px 14px;
  background: rgba(255, 253, 247, 0.45);
  border: 1px solid rgba(81, 109, 51, 0.10);
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.legend-title {
  font-size: 12px;
  font-weight: 700;
  color: #4b5d2b;
  letter-spacing: 1px;
  margin-bottom: 6px;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10.5px;
  color: #5a4f38;
  margin-bottom: 3px;
  line-height: 1.35;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.legend-row .sw {
  flex: none;
  width: 12px;
  height: 9px;
  border-radius: 2px;
  border: 0.5px solid rgba(0,0,0,0.06);
}

/* ===== 中间主地图区 ===== */
.main-panel {
  grid-area: main;
  position: relative;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  background: transparent;
}
.map-title-bar {
  padding: 2px 0 8px;
  text-align: center;
  background: transparent;
  flex: none;
}
.map-title {
  font-size: 15px;
  color: #4b5d2b;
  font-weight: 400;
  letter-spacing: 2px;
}
.map-title strong { font-weight: 700; color: #3D5428; }

.map-stage {
  flex: 1 1 auto;
  position: relative;
  border-radius: 2px;
  overflow: hidden;
  background: transparent;
  border: none;
  box-shadow: none;
  opacity: 0;
  transition: opacity 200ms ease-out;
  min-height: 0;
  min-width: 0;
}
.map-stage.map-fade-in { opacity: 1; }

.map {
  width: 100%;
  height: 100%;
  background: transparent;
}
.map :deep(.leaflet-container) {
  background: transparent !important;
  outline: none !important;
}

.factor-fade-mask {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: #EFE9DA;
  opacity: 0;
  transition: opacity 420ms ease-out;
  z-index: 10;
}
.factor-fade-mask.show { opacity: 0.30; }

/* 固定定位动画覆盖层 */
.flip-overlay-fixed {
  pointer-events: none;
  will-change: left, top, width, height, border-radius, box-shadow;
}
.flip-overlay-fixed img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center center;
  display: block;
  transform: none;
  margin: 0;
  max-width: 100%;
  max-height: 100%;
}

/* ===== 右侧工具组：说明卡（上） + 转盘/溯回（下），固定在右下角 ===== */
.tool-group {
  position: absolute;
  right: clamp(28px, 3vw, 48px);
  bottom: clamp(36px, 5vw, 56px);
  pointer-events: none;
  z-index: 5;
}

/* 说明卡：绝对定位在转盘正上方，米白圆角、柔和阴影、茶绿细边框 */
.factor-info {
  pointer-events: auto;
  position: absolute;
  bottom: 100%;
  right: 0;
  margin-bottom: 20px;
  width: clamp(270px, 15.5vw, 320px);
  max-width: 320px;
  min-width: 270px;
  background: rgba(247, 244, 235, 0.965);
  border: 1px solid rgba(81, 109, 51, 0.12);
  border-radius: 17px;
  padding: 22px 24px 24px;
  box-shadow:
    0 6px 18px rgba(81, 109, 51, 0.08),
    0 2px 4px rgba(81, 109, 51, 0.05);
}
.info-close {
  position: absolute;
  top: 8px; right: 10px;
  width: 24px; height: 24px;
  border: none;
  background: transparent;
  color: #8a7b54;
  font-size: 18px;
  line-height: 1;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: color 0.18s ease, background 0.18s ease;
}
.info-close:hover {
  color: #516D33;
  background: rgba(81, 109, 51, 0.08);
}
.factor-info-title {
  font-size: 14.5px;
  font-weight: 700;
  color: #3f5227;
  letter-spacing: 1px;
  margin-bottom: 10px;
  padding-right: 18px;
}
.factor-info-desc {
  font-size: 12px;
  line-height: 1.75;
  color: #5a4f38;
  word-break: break-word;
}

.info-fade-enter-active,
.info-fade-leave-active { transition: opacity 240ms ease, transform 240ms ease; }
.info-fade-enter-from,
.info-fade-leave-to { opacity: 0; transform: translateY(-4px); }

/* 转盘：工具组底部 */
.wheel-area {
  pointer-events: auto;
  position: relative;
  padding: 12px;
  overflow: visible;
}
.wheel-wrap {
  position: relative;
  width: clamp(250px, 16vw, 300px);
  height: clamp(250px, 16vw, 300px);
  user-select: none;
  touch-action: none;
}
.wheel { position: absolute; inset: 0; overflow: visible; }
.wheel-svg { width: 100%; height: 100%; display: block; overflow: visible; }

/* 扇区 */
.sector {
  opacity: 0.82;
  stroke: rgba(139, 125, 90, 0.55);
  stroke-width: 0.55;
  transition: opacity 0.15s ease, filter 0.15s ease;
  transform-origin: 0 0;
  transform-box: fill-box;
}
.sector.sec-picked {
  opacity: 0.92;
  stroke: rgba(212, 180, 76, 0.5);
  stroke-width: 0.8;
}
.sector.sec-scan {
  opacity: 1;
  filter: brightness(1.22) saturate(1.3) drop-shadow(0 0 4px rgba(255,228,140,0.7)) drop-shadow(0 0 8px rgba(255,210,120,0.42));
  stroke: rgba(255, 230, 160, 0.95);
  stroke-width: 1.2;
}
.sector-lock-stroke { transform-origin: 0 0; }
@keyframes sector-lock-bounce {
  0%   { opacity: 0; }
  35%  { opacity: 1; }
  60%  { opacity: 1; }
  100% { opacity: 1; }
}

.factor-label {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 5px;
  pointer-events: none;
  padding: 3px 7px;
  border-radius: 6px;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
}
.label-name {
  font-size: 11.5px;
  color: #FBF8EF;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(30,40,20,0.55);
  white-space: nowrap;
}
.picked-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #EACF78;
  box-shadow: 0 0 3px rgba(234, 207, 120, 0.7);
}
.factor-label.lbl-scan {
  background: rgba(255, 248, 225, 0.96);
  box-shadow: 0 2px 8px rgba(212, 180, 76, 0.45);
  transform: translate(-50%, -50%) scale(1.08);
}
.factor-label.lbl-scan .label-name { color: #5A4A15; text-shadow: none; font-weight: 700; }
.factor-label.lbl-locked {
  background: rgba(255, 252, 238, 0.98);
  box-shadow: 0 2px 10px rgba(212, 180, 76, 0.55), 0 0 0 1.3px rgba(234, 207, 120, 0.75);
  transform: translate(-50%, -50%) scale(1.12);
}
.factor-label.lbl-locked .label-name { color: #3E4F26; text-shadow: none; font-weight: 800; }
.factor-label.lbl-picked { filter: drop-shadow(0 0 2px rgba(234, 207, 120, 0.42)); }

/* 中心按钮 */
.center-btn {
  position: absolute;
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(145deg, #FBF7EA 0%, #F0EAD6 100%);
  border: 1.5px solid #516D33;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: transform 0.3s, background 0.3s, color 0.3s, border-color 0.3s, box-shadow 0.3s, opacity 0.25s;
  box-shadow: 0 3px 10px rgba(81, 109, 51, 0.22), 0 0 16px rgba(255, 230, 160, 0.22);
  padding: 0;
  font-family: inherit;
}
.center-btn:hover:not(:disabled) {
  background: #516D33;
  transform: translate(-50%, -50%) scale(1.08);
  color: #FBF8EF;
  box-shadow: 0 4px 14px rgba(81, 109, 51, 0.42), 0 0 24px rgba(255, 230, 160, 0.55);
}
.center-btn:disabled { cursor: not-allowed; opacity: 0.62; }
.center-btn.busy {
  color: #7C6C3A;
  border-color: #D4B44C;
  box-shadow: 0 3px 10px rgba(212, 180, 76, 0.32), 0 0 22px rgba(255, 230, 160, 0.55);
}
.center-btn.ready-hl {
  border-color: #B28F4C;
  background: linear-gradient(145deg, #FFF2C2 0%, #F3D97E 100%);
  color: #5A4A15;
  animation: composite-btn-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  box-shadow: 0 3px 12px rgba(178, 143, 76, 0.38), 0 0 26px rgba(255, 220, 130, 0.7);
}
.center-btn.ready-hl:hover:not(:disabled) {
  background: linear-gradient(145deg, #EFD26B 0%, #D4B44C 100%);
  color: #3A2E10;
}
@keyframes composite-btn-in {
  0%   { transform: translate(-50%, -50%) scale(0.86); opacity: 0; }
  60%  { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1);   opacity: 1; }
}
.center-text {
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 1.4px;
  line-height: 1;
}

/* 溯回按钮：右下角，取代转盘位置 */
.return-area {
  pointer-events: auto;
  position: relative;
  width: clamp(250px, 16vw, 300px);
  height: clamp(250px, 16vw, 300px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.return-btn {
  padding: 12px 32px;
  background: rgba(81, 109, 51, 0.92);
  color: #FBF8EF;
  border: none;
  border-radius: 22px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  transition: transform 0.25s, box-shadow 0.25s, background 0.25s;
  box-shadow: 0 3px 10px rgba(81, 109, 51, 0.28);
}
.return-btn:hover {
  transform: translateY(-1px);
  background: #516D33;
  box-shadow: 0 4px 14px rgba(81, 109, 51, 0.45);
}

/* 响应式 */
@media (max-width: 1200px) {
  .chapter-body {
    grid-template-columns: clamp(360px, 30vw, 420px) 1fr;
    padding: 14px;
    gap: 14px;
  }
  .factor-info { width: clamp(250px, 14vw, 290px); padding: 18px 20px; border-radius: 15px; }
  .wheel-wrap { width: 230px; height: 230px; }
  .return-area { width: 230px; height: 230px; }
  .center-btn { width: 62px; height: 62px; }
  .center-text { font-size: 11px; letter-spacing: 1px; }
  .label-name { font-size: 10.5px; }
}
@media (max-width: 900px) {
  .chapter-body {
    grid-template-columns: clamp(280px, 36vw, 340px) 1fr;
  }
  .factor-info { padding: 14px 16px; width: 220px; }
  .factor-info-title { font-size: 13px; }
  .factor-info-desc { font-size: 11.5px; line-height: 1.65; }
  .wheel-wrap { width: 180px; height: 180px; }
  .return-area { width: 180px; height: 180px; }
  .legend-title { font-size: 11px; }
  .legend-row .sw { width: 10px; height: 8px; }
  .thumb-name { font-size: 11px; }
}
</style>
