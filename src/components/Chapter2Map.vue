<template>
  <section class="chapter chapter-2">
    <ChapterIntro
      ch-no="贰"
      title="何以生茶"
      desc="得天独厚的光照、气候与土壤条件，编织出适配茶树生长的天然温床，一方水土的禀赋，悄悄决定了茶叶的诞生与品质。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{
      show: introDone,
      'mode-empty':     displayMode === 'empty',
      'mode-single':    displayMode === 'single',
      'mode-grid':      displayMode === 'grid',
      'mode-composite': displayMode === 'composite',
    }">
      <!-- 主地图 (Leaflet, 用于大图/综合图) -->
      <div
        class="map-stage"
        :class="{ active: displayMode === 'single' || displayMode === 'composite' || displayMode === 'empty' }"
      >
        <div ref="mapRef" class="map"></div>
        <!-- 地图标题 (大图模式下显示) -->
        <div v-if="displayMode !== 'grid'" class="map-title-bar">
          <div v-if="isComposite" key="composite-title" class="map-title">
            茶树生态适宜性<strong>综合评价</strong>
          </div>
          <div v-else-if="currentFactor" :key="'title-'+currentFactor" class="map-title">
            {{ currentConfig.name }}适宜性分析
          </div>
          <div v-else class="map-title">开启转盘 · 抽取因子</div>
        </div>
      </div>

      <!-- 缩略图网格: 2 行 × 3 列, 用于 mode-grid (集齐5因子) -->
      <div v-if="displayMode === 'grid'" class="thumb-grid">
        <div v-for="(fid, idx) in pickedFactorHistory"
             :key="'thumb-grid-'+fid"
             class="thumb-cell"
             :class="{'pos-last': idx===4}"
             @click="openThumbAsMain(fid)"
        >
          <div class="thumb-tag">
            <span class="thumb-tag-icon">{{ FACTORS[fid].icon }}</span>
            <span class="thumb-tag-name">{{ FACTORS[fid].name }}</span>
          </div>
          <div class="thumb-img-wrap">
            <img class="thumb-img" :src="FACTORS[fid].png" :alt="FACTORS[fid].name" />
          </div>
        </div>
      </div>

      <!-- 已抽取因子缩略条: 2~5 个, 位于左上 (mode-single) -->
      <transition-group v-if="displayMode === 'single' && pickedFactorHistory.length >= 2"
                        name="thumb-strip"
                        tag="div"
                        class="thumb-strip">
        <div v-for="(fid, i) in thumbnailsShown"
             :key="'thumb-strip-'+fid"
             class="strip-card"
             :class="{ active: fid === currentFactor }"
             @click="openThumbAsMain(fid)"
        >
          <div class="strip-img-wrap">
            <img class="strip-img" :src="FACTORS[fid].png" :alt="FACTORS[fid].name" />
          </div>
          <div class="strip-meta">
            <span class="strip-meta-icon">{{ FACTORS[fid].icon }}</span>
            <span class="strip-meta-name">{{ FACTORS[fid].name }}</span>
          </div>
        </div>
      </transition-group>

      <!-- 图例: 垂直居中左侧 (非 grid 模式显示) -->
      <div class="map-legend" :class="{ 'hide-in-grid': displayMode === 'grid' }">
        <div v-if="isComposite" key="legend-composite">
          <div class="legend-title">综合分级</div>
          <div v-for="lv in COMPOSITE.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
        <div v-else-if="currentFactor" :key="'legend-'+currentFactor">
          <div class="legend-title">{{ currentConfig.name }}</div>
          <div v-for="lv in currentConfig.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
        <div v-else>
          <div class="legend-title">五因子分级</div>
          <div v-for="lv in FACTORS.precip.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
      </div>

      <!-- 转盘停靠区 (始终固定右下) -->
      <div class="wheel-dock">
        <transition name="card-expand">
          <div v-if="expandedFactor && (displayMode==='single' || displayMode==='composite')"
               class="factor-card" @click="collapseCard">
            <div class="card-header">
              <span class="card-icon">{{ expandedConfig.icon }}</span>
              <span class="card-title">{{ expandedConfig.name }}适宜性</span>
              <span class="card-close">×</span>
            </div>
            <div class="card-desc">{{ expandedConfig.desc }}</div>
            <div class="card-legend">
              <div v-for="lv in expandedConfig.levels" :key="lv.value" class="legend-item">
                <span class="swatch" :style="{ background: lv.color }"></span>
                <span>{{ lv.label }}</span>
              </div>
            </div>
          </div>
        </transition>

        <div
          class="wheel-wrap"
          ref="wheelRef"
          @click="onWheelClick"
        >
          <div class="wheel">
            <svg viewBox="-110 -110 220 220" class="wheel-svg">
              <defs>
                <filter id="glow-filter" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="4" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              <template v-for="(fid, i) in FACTOR_ORDER" :key="fid">
                <path
                  :d="sectorPath(i, 8, 88)"
                  :fill="WHEEL_COLORS[i]"
                  class="sector"
                  :class="{ active: currentFactor === fid, picked: isPicked(fid) }"
                  :data-fid="fid"
                />
              </template>

              <line
                v-for="i in 5"
                :key="'line'+i"
                :x1="0" :y1="0"
                :x2="Math.cos((i*72-90)*Math.PI/180)*88"
                :y2="Math.sin((i*72-90)*Math.PI/180)*88"
                stroke="#8B7D5A" stroke-width="0.5"
              />
              <circle cx="0" cy="0" r="88" fill="none" stroke="#8B7D5A" stroke-width="1.2" />
              <circle cx="0" cy="0" r="60" fill="none" stroke="#B2A67D" stroke-width="0.6" stroke-dasharray="2 3" />

              <path
                class="glow-sector"
                :d="sectorPath(0, 4, 95)"
                fill="rgba(255,250,215,0.58)"
                stroke="rgba(255,235,160,0.95)"
                stroke-width="0.8"
                filter="url(#glow-filter)"
                :style="{ transform: `rotate(${pointerAngle}deg)`, transformOrigin: '0 0', transition: 'transform 3.8s cubic-bezier(0.17, 0.67, 0.12, 0.99)' }"
              />
            </svg>

            <div
              v-for="(fid, i) in FACTOR_ORDER"
              :key="'label'+fid"
              class="factor-label"
              :style="labelStyle(i)"
              :class="{ active: currentFactor === fid, picked: isPicked(fid) }"
              :data-fid="fid"
            >
              <span class="label-icon">{{ FACTORS[fid].icon }}</span>
              <span class="label-name">{{ FACTORS[fid].name }}</span>
            </div>
          </div>

          <button class="center-btn"
                  :class="{ composite: isComposite, ready: allPicked && !isComposite }"
                  @click.stop="onCenterClick">
            <div class="center-icon">{{ centerIcon }}</div>
            <div class="center-text">{{ centerText }}</div>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import ChapterIntro from './ChapterIntro.vue'
import {
  FACTORS, COMPOSITE, FACTOR_ORDER, WHEEL_COLORS,
  PROV_BG_URL, PROV_STYLE,
  loadFactorBounds,
} from '../config/ch2.js'
import { createAlbersCRS, getMapOptions } from '../utils/crs.js'

const mapRef = ref(null)
const wheelRef = ref(null)
const introDone = ref(false)

function onIntroDone() {
  introDone.value = true
  setTimeout(() => {
    if (map) map.invalidateSize()
  }, 300)
}

const currentFactor = ref(null)
const pointerAngle = ref(0)
const expandedFactor = ref(null)

// 已抽取过的因子记录 (保证不重复)
const pickedFactors = ref(new Set())
// 按抽取顺序记录的因子ID列表 (用于缩略图排序)
const pickedFactorHistory = ref([])
const allPicked = computed(() => pickedFactors.value.size >= FACTOR_ORDER.length)

// 是否展示grid视图 (5因子集齐后, 需要用户点击中心按钮才切换)
const showGrid = ref(false)

// 布局模式: empty → single → grid → composite
const displayMode = computed(() => {
  if (isComposite.value) return 'composite'
  if (pickedFactorHistory.value.length === 0) return 'empty'
  if (allPicked.value && showGrid.value) return 'grid'
  return 'single'
})

// single模式下左上缩略条显示的因子 (排除当前主图因子)
const thumbnailsShown = computed(() => {
  return pickedFactorHistory.value.filter(fid => fid !== currentFactor.value)
})

const isComposite = computed(() => currentFactor.value === 'composite')
const currentConfig = computed(() => {
  if (isComposite.value) return COMPOSITE
  if (!currentFactor.value) return FACTORS[FACTOR_ORDER[0]]
  return FACTORS[currentFactor.value] || COMPOSITE
})
const expandedConfig = computed(() => expandedFactor.value === 'composite' ? COMPOSITE : FACTORS[expandedFactor.value || ''] || COMPOSITE)

// 中心按钮文案/图标
const centerIcon = computed(() => {
  if (isComposite.value) return COMPOSITE.icon
  if (allPicked.value && showGrid.value) return COMPOSITE.icon
  if (allPicked.value && !showGrid.value) return '📊'
  return wheelBusy ? '🎯' : '▶'
})
const centerText = computed(() => {
  if (isComposite.value) return '重抽'
  if (allPicked.value && showGrid.value) return '综合'
  if (allPicked.value && !showGrid.value) return '汇总'
  if (pickedFactors.value.size === 0) return '开始'
  return '下一个'
})

// 中国在 Albers 投影下的实际边界 (lon[73,135] × lat[18,53] + 500km padding)
const CHINA_ALBERS_BOUNDS = [
  [1836948, -3917344],  // [southY, westX]
  [6597902,  3710529],  // [northY, eastX]
]

let map = null
let provLayer = null
let factorLayer = null

async function initMap() {
  if (map) return
  const opts = getMapOptions()
  map = L.map(mapRef.value, {
    ...opts,
    zoomControl: true,
    attributionControl: false,
  })

  try {
    const res = await fetch(PROV_BG_URL)
    const provData = await res.json()
    provLayer = L.geoJSON(provData, {
      style: () => ({ ...PROV_STYLE }),
      coordsToLatLng: function (coords) {
        return new L.LatLng(coords[1], coords[0], true)
      },
    }).addTo(map)
    // 让地图聚焦中国而不是全画布
    map.fitBounds(CHINA_ALBERS_BOUNDS, { padding: [20, 20] })
  } catch (e) { console.warn('[ch2] provinces failed:', e) }

  await updateFactorLayer()

  setTimeout(() => map && map.invalidateSize(), 300)
}

async function updateFactorLayer() {
  if (!map) return
  if (factorLayer) { map.removeLayer(factorLayer); factorLayer = null }
  if (!currentFactor.value) return
  const cfg = currentConfig.value
  const bounds = await loadFactorBounds(currentFactor.value)
  factorLayer = L.imageOverlay(cfg.png, bounds, {
    opacity: 1,
    interactive: false,
    crossOrigin: true,
  }).addTo(map)
  // 聚焦中国范围, 不使用 bounds (bounds 是全画布太大)
  map.fitBounds(CHINA_ALBERS_BOUNDS, { padding: [30, 30] })
}

watch(currentFactor, () => { nextTick(updateFactorLayer) })

// ==================== 转盘: 发光指针 + 不重复随机抽取 ====================
const SPIN_DURATION_MS = 3800          // 与模板内 transition-duration 保持严格一致
const SPIN_EASING = 'cubic-bezier(0.17, 0.67, 0.12, 0.99)' // 平滑起-缓落
const wheelBusy = ref(false)

function isPicked(fid) {
  return pickedFactors.value.has(fid)
}

function getNextUnpickedIndex() {
  const available = []
  for (let i = 0; i < FACTOR_ORDER.length; i++) {
    if (!pickedFactors.value.has(FACTOR_ORDER[i])) available.push(i)
  }
  if (available.length === 0) return -1
  return available[Math.floor(Math.random() * available.length)]
}

// 发光扇形本身中心位于 -54° (sectorPath(0) 中心角), CSS rotate(angle) 后指向 -54° + angle
// 要指向扇区 i 的中心 (i*72 - 54), 需要 angle = i*72
function indexToPointerAngle(index) {
  return index * 72
}

// 仅顺时针单向旋转: 计算从 current 出发, 转到 targetIndex 的"绝对目标角度".
// 保证: targetAngle > current 且 targetAngle - current ∈ [360 + 0°, 360 + ~340°] ≈ 正正好好一圈直达.
function computeTargetAngle(current, targetIndex) {
  const now = current || 0
  const base = indexToPointerAngle(targetIndex)

  // 把 base 抬到"刚好大于 now 的等效位置"
  // round = 已转过的完整圈数 (向下取整)
  const rounds = Math.floor(now / 360)
  let equiv = rounds * 360 + base
  if (equiv <= now) equiv += 360 // 保证在当前角度前方
  // 强制至少再前进一整圈 (满足"转一圈直达")
  const minFinal = now + 360
  if (equiv < minFinal) equiv += Math.ceil((minFinal - equiv) / 360) * 360
  // + 扇区内 ±24° 随机微调 (不越过 ±36°, 仍落在目标扇区内), 自然感
  equiv += (Math.random() * 2 - 1) * 24
  return equiv
}

function spinToIndex(targetIndex, onComplete) {
  const current = pointerAngle.value || 0
  const targetAngle = computeTargetAngle(current, targetIndex)
  wheelBusy.value = true
  pointerAngle.value = targetAngle

  setTimeout(() => {
    wheelBusy.value = false
    if (onComplete) onComplete()
  }, SPIN_DURATION_MS)
}

function startSpinThenSnap() {
  if (wheelBusy.value) return
  if (allPicked.value) return  // 5因子已集齐, 不再触发自动选择
  const nextIndex = getNextUnpickedIndex()
  if (nextIndex < 0) return

  const fid = FACTOR_ORDER[nextIndex]

  spinToIndex(nextIndex, () => {
    // 指针到达瞬间与因子/地图切换完全同步
    pickedFactors.value.add(fid)
    if (!pickedFactorHistory.value.includes(fid)) {
      pickedFactorHistory.value.push(fid)
    }
    currentFactor.value = fid
    expandedFactor.value = fid
  })
}

function onCenterClick() {
  if (wheelBusy.value) return
  if (isComposite.value) {
    resetWheel()
    return
  }
  if (allPicked.value && showGrid.value) {
    // grid视图下点击中心 → 切换到综合评价
    selectComposite()
    return
  }
  if (allPicked.value && !showGrid.value) {
    // 5因子集齐但仍在single模式 → 切换到grid视图
    showGrid.value = true
    return
  }
  startSpinThenSnap()
}

function resetWheel() {
  pickedFactors.value = new Set()
  pickedFactorHistory.value = []
  showGrid.value = false
  currentFactor.value = null
  expandedFactor.value = null
  pointerAngle.value = 0
  wheelBusy.value = false
  nextTick(updateFactorLayer)
}

function onWheelClick(e) {
  if (wheelBusy.value) return
  const target = e.target
  if (!target || !target.closest) return
  const el = target.closest('[data-fid]')
  if (el) {
    const fid = el.dataset.fid
    if (!fid) return
    if (!FACTOR_ORDER.includes(fid)) return
    if (isComposite.value) return
    const idx = FACTOR_ORDER.indexOf(fid)
    const now = pointerAngle.value || 0
    const rounds = Math.round(now / 360)
    pointerAngle.value = rounds * 360 + indexToPointerAngle(idx)
    pickedFactors.value.add(fid)
    if (!pickedFactorHistory.value.includes(fid)) {
      pickedFactorHistory.value.push(fid)
    }
    currentFactor.value = fid
    expandedFactor.value = fid
  }
}

function selectFactor(fid) {
  const idx = FACTOR_ORDER.indexOf(fid)
  if (idx >= 0) {
    const now = pointerAngle.value || 0
    const rounds = Math.round(now / 360)
    pointerAngle.value = rounds * 360 + indexToPointerAngle(idx)
    pickedFactors.value.add(fid)
    if (!pickedFactorHistory.value.includes(fid)) {
      pickedFactorHistory.value.push(fid)
    }
  }
  currentFactor.value = fid
  expandedFactor.value = fid
}

// 点击缩略图切换为主地图 (single模式)
function openThumbAsMain(fid) {
  if (!FACTOR_ORDER.includes(fid)) return
  const idx = FACTOR_ORDER.indexOf(fid)
  const now = pointerAngle.value || 0
  const rounds = Math.round(now / 360)
  pointerAngle.value = rounds * 360 + indexToPointerAngle(idx)
  currentFactor.value = fid
  expandedFactor.value = fid
}

function selectComposite() {
  currentFactor.value = 'composite'
  expandedFactor.value = 'composite'
}

function collapseCard() {
  expandedFactor.value = null
}

function sectorPath(index, innerR, outerR) {
  const startAngle = index * 72 - 90 + 1   // +1/-1 留 2° 缝
  const endAngle = startAngle + 70
  const start = { x: Math.cos(startAngle * Math.PI / 180) * outerR, y: Math.sin(startAngle * Math.PI / 180) * outerR }
  const end = { x: Math.cos(endAngle * Math.PI / 180) * outerR, y: Math.sin(endAngle * Math.PI / 180) * outerR }
  const innerEnd = { x: Math.cos(endAngle * Math.PI / 180) * innerR, y: Math.sin(endAngle * Math.PI / 180) * innerR }
  const innerStart = { x: Math.cos(startAngle * Math.PI / 180) * innerR, y: Math.sin(startAngle * Math.PI / 180) * innerR }
  return `M ${start.x} ${start.y} A ${outerR} ${outerR} 0 0 1 ${end.x} ${end.y} L ${innerEnd.x} ${innerEnd.y} A ${innerR} ${innerR} 0 0 0 ${innerStart.x} ${innerStart.y} Z`
}

function labelStyle(index) {
  const angle = index * 72 - 54  // 扇区中心角 -90+36 = -54
  const rad = angle * Math.PI / 180
  const r = 75
  const x = Math.cos(rad) * r
  const y = Math.sin(rad) * r
  const pctX = 50 + (x / 100) * 50
  const pctY = 50 + (y / 100) * 50
  return { left: `${pctX}%`, top: `${pctY}%`, transform: `translate(-50%, -50%)` }
}

onMounted(async () => {
  await nextTick()
  initMap()
})

onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
.chapter-2 {
  position: relative;
  background: var(--c-paper);
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
  background: var(--c-paper-2);
}

/* 地图标题 */
.map-title-bar {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 500;
  background: rgba(247, 244, 235, 0.92);
  backdrop-filter: blur(8px);
  padding: 6px 22px;
  border-radius: 20px;
  border: 1px solid rgba(81, 109, 51, 0.2);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.map-title {
  font-size: 15px;
  color: var(--c-olive);
  font-weight: 400;
  letter-spacing: 2px;
  text-align: center;
}
.map-title strong { font-weight: 700; color: #3D5428; }

/* 模式下地图舞台大小 (grid模式地图隐藏 / composite与single全屏) */
.map-stage { position: absolute; inset: 0; }
.map-stage.active { display: block; }
.map-fullscreen.mode-grid .map-stage { display: none; }

/* 图例 - 左侧垂直居中 (single/composite/empty 模式显示, grid 模式隐藏) */
.map-legend {
  position: absolute;
  top: 50%;
  left: 16px;
  transform: translateY(-50%);
  z-index: 500;
  background: rgba(247, 244, 235, 0.95);
  backdrop-filter: blur(8px);
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(81, 109, 51, 0.2);
  min-width: 150px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: opacity 0.3s;
}
.map-legend.hide-in-grid { opacity: 0; pointer-events: none; }
.legend-title { font-size: 13px; font-weight: 600; color: var(--c-olive); margin-bottom: 6px; letter-spacing: 1px; }
.legend-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #5a4f38; margin-bottom: 3px; }
.legend-row .sw { width: 16px; height: 12px; border-radius: 2px; border: 0.5px solid rgba(0,0,0,0.08); }

/* 南海九段线插图已移除 */

/* ===== 转盘停靠区 ===== */
.wheel-dock {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 600;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

/* 因子卡片 */
.factor-card {
  background: rgba(247, 244, 235, 0.97);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(81, 109, 51, 0.25);
  border-radius: 14px;
  padding: 14px 18px;
  width: 240px;
  box-shadow: 0 8px 32px rgba(81, 109, 51, 0.2);
  cursor: pointer;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.card-icon { font-size: 18px; }
.card-title { font: 600 14px var(--serif); color: var(--c-olive); flex: 1; }
.card-close { font-size: 16px; color: var(--muted); }
.card-desc { font-size: 11px; line-height: 1.6; color: #6B5F45; margin-bottom: 8px; }
.card-legend { display: flex; flex-wrap: wrap; gap: 4px 10px; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 10px; color: #5a4f38; }
.legend-item .swatch { width: 10px; height: 10px; border-radius: 2px; border: 0.5px solid rgba(0,0,0,0.1); }

/* 卡片展开/收起动画 */
.card-expand-enter-active, .card-expand-leave-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.card-expand-enter-from, .card-expand-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

/* ===== 转盘 (放大至约1.6倍) ===== */
.wheel-wrap {
  position: relative;
  width: 288px;
  height: 288px;
  user-select: none;
  touch-action: none;
}
.wheel {
  position: absolute;
  inset: 0;
}
.wheel-svg { width: 100%; height: 100%; display: block; overflow: visible; }
.sector {
  opacity: 0.8;
  transition: opacity 0.2s, transform 0.3s;
  transform-origin: center;
}
.sector:hover { opacity: 1; }
.sector.active { opacity: 1; filter: brightness(1.18) drop-shadow(0 0 6px rgba(255,240,180,0.8)); }
.sector.picked { opacity: 1; }

/* 浅色发光扇形指针 */
.glow-sector {
  pointer-events: none;
  mix-blend-mode: screen;
}

.factor-label {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  pointer-events: auto;
  cursor: pointer;
  padding: 2px 5px;
  border-radius: 6px;
  transition: background 0.3s, box-shadow 0.3s, transform 0.3s;
}
.factor-label.active {
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.3);
  transform: translate(-50%, -50%) scale(1.08);
}
.factor-label.picked {
  filter: drop-shadow(0 0 3px rgba(255,220,130,0.6));
}
.label-icon { font-size: 16px; }
.label-name { font-size: 11px; color: var(--c-olive); font-weight: 500; white-space: nowrap; }
.factor-label.active .label-name { font-weight: 700; }

.center-btn {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--c-paper);
  border: 2px solid var(--c-olive);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(81, 109, 51, 0.28), 0 0 18px rgba(255, 230, 160, 0.35);
  padding: 0;
  font-family: inherit;
}
.center-btn:hover {
  background: var(--c-olive);
  transform: translate(-50%, -50%) scale(1.12);
  color: var(--c-paper);
  box-shadow: 0 4px 14px rgba(81, 109, 51, 0.4), 0 0 28px rgba(255, 230, 160, 0.75);
}
.center-btn.composite { background: var(--c-olive); color: var(--c-paper); }
.center-btn.ready {
  border-color: #D4B44C;
  background: #FFF4C2;
  color: #6B5A20;
}
.center-btn.ready:hover {
  background: #D4B44C;
  color: #3D3113;
}
.center-icon { font-size: 20px; margin-bottom: 2px; line-height: 1; }
.center-text { font-size: 11px; font-weight: 700; letter-spacing: 1px; line-height: 1; }

/* ===== 缩略图条 (位于single模式左侧) ===== */
.thumb-strip {
  position: absolute;
  top: 90px;
  left: 14px;
  transform: none;
  z-index: 520;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: rgba(247, 244, 235, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(81, 109, 51, 0.18);
  border-radius: 14px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}
.strip-card {
  flex: 0 0 auto;
  width: 200px;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  background: #fff;
  border: 1px solid rgba(81, 109, 51, 0.15);
  transition: transform 0.28s, box-shadow 0.28s, border-color 0.28s;
}
.strip-card:hover { transform: translateX(4px); box-shadow: 0 6px 16px rgba(81, 109, 51, 0.18); border-color: rgba(81, 109, 51, 0.35); }
.strip-card.active { border-color: #D4B44C; box-shadow: 0 0 0 2px rgba(212, 180, 76, 0.3), 0 6px 16px rgba(0,0,0,0.08); }
.strip-img-wrap {
  width: 100%;
  aspect-ratio: 4 / 3;
  background: var(--c-paper-2);
  overflow: hidden;
}
.strip-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center 5%;
  display: block;
  transform: scale(4);
}
.strip-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: #FBF9F1;
  border-top: 1px solid rgba(81, 109, 51, 0.08);
}
.strip-meta-icon { font-size: 14px; }
.strip-meta-name { font-size: 12px; color: var(--c-olive); font-weight: 600; letter-spacing: 0.5px; }

/* 缩略条进场动画 */
.thumb-strip-enter-active, .thumb-strip-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.thumb-strip-enter-from, .thumb-strip-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* ===== 缩略图网格 (集齐5因子后, 2行3列) ===== */
.thumb-grid {
  position: absolute;
  inset: 0;
  padding: 40px 360px 40px 80px;  /* 右侧留转盘 288 + 16*2 + padding ≈ 360 */
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 24px;
  z-index: 400;
  align-content: center;
  justify-content: center;
}
.thumb-cell {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
  border: 1px solid rgba(81, 109, 51, 0.2);
  box-shadow: 0 6px 24px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.thumb-cell:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(81, 109, 51, 0.18);
}
.thumb-cell.pos-last {
  /* 第5个占第2行第1列 (让网格对称) */
}
.thumb-tag {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(247, 244, 235, 0.95);
  border-bottom: 1px solid rgba(81, 109, 51, 0.12);
}
.thumb-tag-icon { font-size: 14px; }
.thumb-tag-name { font-size: 12px; color: var(--c-olive); font-weight: 700; letter-spacing: 1px; }
.thumb-img-wrap {
  flex: 1;
  min-height: 0;
  background: var(--c-paper-2);
  overflow: hidden;
}
.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center 30%;
  display: block;
  transition: transform 0.4s;
  transform: scale(4);
}
.thumb-cell:hover .thumb-img { transform: scale(2.58); }
.thumb-clip { display: none; }

@media (max-width: 1200px) {
  .thumb-grid { padding: 30px 340px 30px 40px; gap: 18px; }
}
@media (max-width: 880px) {
  .wheel-wrap { width: 220px; height: 220px; }
  .center-btn { width: 56px; height: 56px; }
  .center-icon { font-size: 16px; }
  .center-text { font-size: 9px; }
  .factor-card { width: 200px; }
  .map-title-bar { top: 10px; }
  .map-title { font-size: 13px; }
  .thumb-strip { top: 70px; left: 8px; padding: 8px; gap: 6px; max-height: calc(100vh - 240px); }
  .strip-card { width: 140px; }
  .thumb-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 1fr);
    padding: 20px 20px 280px 140px;
  }
}
</style>
