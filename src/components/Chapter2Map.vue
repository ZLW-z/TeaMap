<template>
  <section class="chapter chapter-2">
    <ChapterIntro
      ch-no="第 二 章"
      title="何以生茶"
      desc="降水、气温、积温、光照、土壤酸碱度五大生态因子叠加分析，揭示茶树生长适宜性的空间格局。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }">
      <div ref="mapRef" class="map"></div>

      <!-- 地图标题浮层 -->
      <div class="map-title-bar">
        <div v-if="isComposite" key="composite-title" class="map-title">
          茶树生态适宜性<strong>综合评价</strong>
        </div>
        <div v-else :key="'title-'+currentFactor" class="map-title">
          {{ currentConfig.name }}适宜性分析
        </div>
      </div>

      <!-- 图例 -->
      <div class="map-legend">
        <div v-if="isComposite" key="legend-composite">
          <div class="legend-title">综合分级</div>
          <div v-for="lv in COMPOSITE.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
        <div v-else :key="'legend-'+currentFactor">
          <div class="legend-title">{{ currentConfig.name }}</div>
          <div v-for="lv in currentConfig.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
      </div>

      <!-- 转盘停靠区 -->
      <div class="wheel-dock">
        <transition name="card-expand">
          <div v-if="expandedFactor" class="factor-card" @click="collapseCard">
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
          @pointerdown="onWheelDown"
          @click="onWheelClick"
        >
          <div class="wheel" :style="{ transform: `rotate(${wheelAngle}deg)` }">
            <svg viewBox="-100 -100 200 200" class="wheel-svg">
              <template v-for="(fid, i) in FACTOR_ORDER" :key="fid">
                <path
                  :d="sectorPath(i, 0, 88)"
                  :fill="WHEEL_COLORS[i]"
                  class="sector"
                  :class="{ active: currentFactor === fid }"
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
            </svg>

            <div
              v-for="(fid, i) in FACTOR_ORDER"
              :key="'label'+fid"
              class="factor-label"
              :style="labelStyle(i)"
              :class="{ active: currentFactor === fid }"
              :data-fid="fid"
            >
              <span class="label-icon">{{ FACTORS[fid].icon }}</span>
              <span class="label-name">{{ FACTORS[fid].name }}</span>
            </div>
          </div>

          <div class="center-btn" :class="{ composite: isComposite }" @click.stop="selectComposite">
            <div class="center-icon">{{ COMPOSITE.icon }}</div>
            <div class="center-text">{{ isComposite ? '综合' : '叠加' }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import { createAlbersCRS } from '../utils/crs.js'
import ChapterIntro from './ChapterIntro.vue'
import {
  FACTORS, COMPOSITE, FACTOR_ORDER, WHEEL_COLORS,
  PROV_BG_URL, PROV_STYLE,
  loadFactorBounds,
} from '../config/ch2.js'

const mapRef = ref(null)
const wheelRef = ref(null)
const introDone = ref(false)

function onIntroDone() {
  introDone.value = true
  setTimeout(() => {
    if (map) map.invalidateSize()
  }, 300)
}

const currentFactor = ref('precip')
const wheelAngle = ref(0)
const expandedFactor = ref(null)
const isComposite = computed(() => currentFactor.value === 'composite')
const currentConfig = computed(() => isComposite.value ? COMPOSITE : FACTORS[currentFactor.value])
const expandedConfig = computed(() => expandedFactor.value === 'composite' ? COMPOSITE : FACTORS[expandedFactor.value || ''])

let map = null
let provLayer = null
let factorLayer = null

async function initMap() {
  if (map) return
  map = L.map(mapRef.value, {
    crs: createAlbersCRS(),
    zoomControl: true,
    attributionControl: false,
    minZoom: 3,
    maxZoom: 7,
  })
  map.setView([30, 108], 4)

  try {
    const res = await fetch(PROV_BG_URL)
    const provData = await res.json()
    provLayer = L.geoJSON(provData, { style: () => ({ ...PROV_STYLE }) }).addTo(map)
  } catch (e) { console.warn('[ch2] provinces failed:', e) }

  await updateFactorLayer()

  setTimeout(() => map && map.invalidateSize(), 300)
}

async function updateFactorLayer() {
  if (!map) return
  if (factorLayer) { map.removeLayer(factorLayer); factorLayer = null }
  const cfg = currentConfig.value
  const bounds = await loadFactorBounds(currentFactor.value)
  factorLayer = L.imageOverlay(cfg.png, bounds, { opacity: 1, interactive: false }).addTo(map)
  map.fitBounds(bounds, { padding: [20, 20] })
}

watch(currentFactor, () => { nextTick(updateFactorLayer) })

// ==================== 转盘交互 ====================
let isDragging = false
let startAngle = 0
let startRotation = 0
let dragMoved = false

function angleBetweenCenter(x, y) {
  const el = wheelRef.value
  if (!el) return 0
  const rect = el.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height / 2
  return Math.atan2(y - cy, x - cx) * 180 / Math.PI
}

function onWheelDown(e) {
  isDragging = true
  dragMoved = false
  startAngle = angleBetweenCenter(e.clientX, e.clientY)
  startRotation = wheelAngle.value
  document.addEventListener('pointermove', onWheelMove, { passive: false })
  document.addEventListener('pointerup', onWheelUp)
}

function onWheelMove(e) {
  if (!isDragging) return
  e.preventDefault()
  dragMoved = true
  const currentAngle = angleBetweenCenter(e.clientX, e.clientY)
  const delta = currentAngle - startAngle
  wheelAngle.value = startRotation + delta
}

function onWheelUp() {
  if (!isDragging) return
  isDragging = false
  document.removeEventListener('pointermove', onWheelMove)
  document.removeEventListener('pointerup', onWheelUp)
  if (dragMoved) {
    const angle = wheelAngle.value % 360
    const normalized = (angle + 360) % 360
    const snapped = Math.round(normalized / 72) * 72
    wheelAngle.value = snapped
    const idx = Math.round(normalized / 72) % 5
    const fid = FACTOR_ORDER[idx]
    if (fid && fid !== currentFactor.value) currentFactor.value = fid
  }
}

function onWheelClick(e) {
  if (dragMoved) { dragMoved = false; return }
  const target = e.target
  if (!target || !target.closest) return
  const el = target.closest('[data-fid]')
  if (el) {
    const fid = el.dataset.fid
    if (fid) selectFactor(fid)
  }
}

function selectFactor(fid) {
  currentFactor.value = fid
  expandedFactor.value = fid
  const idx = FACTOR_ORDER.indexOf(fid)
  if (idx >= 0) wheelAngle.value = -(idx * 72)
}

function selectComposite() {
  currentFactor.value = 'composite'
  expandedFactor.value = 'composite'
  wheelAngle.value = 0
}

function collapseCard() {
  expandedFactor.value = null
}

function sectorPath(index, innerR, outerR) {
  const startAngle = index * 72 - 90
  const endAngle = startAngle + 70
  const start = { x: Math.cos(startAngle * Math.PI / 180) * outerR, y: Math.sin(startAngle * Math.PI / 180) * outerR }
  const end = { x: Math.cos(endAngle * Math.PI / 180) * outerR, y: Math.sin(endAngle * Math.PI / 180) * outerR }
  const innerEnd = { x: Math.cos(endAngle * Math.PI / 180) * innerR, y: Math.sin(endAngle * Math.PI / 180) * innerR }
  const innerStart = { x: Math.cos(startAngle * Math.PI / 180) * innerR, y: Math.sin(startAngle * Math.PI / 180) * innerR }
  return `M ${start.x} ${start.y} A ${outerR} ${outerR} 0 0 1 ${end.x} ${end.y} L ${innerEnd.x} ${innerEnd.y} A ${innerR} ${innerR} 0 0 0 ${innerStart.x} ${innerStart.y} Z`
}

function labelStyle(index) {
  const angle = index * 72 - 54
  const rad = angle * Math.PI / 180
  const r = 75
  const x = Math.cos(rad) * r
  const y = Math.sin(rad) * r
  const pctX = 50 + (x / 100) * 50
  const pctY = 50 + (y / 100) * 50
  const rot = -wheelAngle.value
  return { left: `${pctX}%`, top: `${pctY}%`, transform: `translate(-50%, -50%) rotate(${rot}deg)` }
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

/* 图例 */
.map-legend {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 500;
  background: rgba(247, 244, 235, 0.95);
  backdrop-filter: blur(8px);
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(81, 109, 51, 0.2);
  min-width: 150px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
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

/* ===== 转盘 ===== */
.wheel-wrap {
  position: relative;
  width: 170px;
  height: 170px;
  user-select: none;
  touch-action: none;
}
.wheel {
  position: absolute;
  inset: 0;
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.wheel-svg { width: 100%; height: 100%; display: block; }
.sector { opacity: 0.75; transition: opacity 0.2s; }
.sector.active { opacity: 1; filter: brightness(1.15); }
.sector:hover { opacity: 0.9; }

.factor-label {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  pointer-events: auto;
  cursor: pointer;
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  padding: 2px 5px;
  border-radius: 6px;
}
.factor-label.active {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.25);
}
.label-icon { font-size: 12px; }
.label-name { font-size: 9px; color: var(--c-olive); font-weight: 500; white-space: nowrap; }
.factor-label.active .label-name { font-weight: 700; }

.center-btn {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 44px;
  height: 44px;
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
  box-shadow: 0 4px 12px rgba(81, 109, 51, 0.25);
}
.center-btn:hover {
  background: var(--c-olive);
  transform: translate(-50%, -50%) scale(1.1);
}
.center-btn.composite { background: var(--c-olive); color: var(--c-paper); }
.center-icon { font-size: 14px; margin-bottom: 1px; }
.center-text { font-size: 8px; font-weight: 600; letter-spacing: 1px; }

@media (max-width: 880px) {
  .wheel-wrap { width: 140px; height: 140px; }
  .center-btn { width: 38px; height: 38px; }
  .center-icon { font-size: 12px; }
  .center-text { font-size: 7px; }
  .factor-card { width: 200px; }
  .map-title-bar { top: 10px; }
  .map-title { font-size: 13px; }
}
</style>
