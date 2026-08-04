<template>
  <section class="chapter chapter-6" :id="id">
    <ChapterIntro
      ch-no="拓 展"
      title="世界共饮"
      desc="茶越山海，化为世界共饮之物。悬停一国，见中国茶之占比，亦见当地饮茶之俗。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }" ref="scrollContainer">
    <!-- 全球数据看板 -->
    <div class="stats-board card-stagger">
      <div v-for="(s, si) in GLOBAL_STATS" :key="s.label" class="stat-card" :style="{ animationDelay: (si * 0.08) + 's' }">
        <span class="stat-icon">{{ s.icon }}</span>
        <div class="stat-body">
          <div class="stat-value num-roll">{{ s.value }}<small>{{ s.unit }}</small></div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- TOP5 进口国条形图 -->
    <div class="importers-bar card-stagger" style="animation-delay: 0.32s;">
      <h3 class="bar-title">TOP5 茶叶进口国 · 占比</h3>
      <div class="bar-rows">
        <div v-for="(item, idx) in TOP_IMPORTERS" :key="item.country" class="bar-row" :style="{ animationDelay: (idx * 0.12) + 's' }">
          <span class="bar-country">{{ item.country }}</span>
          <div class="bar-track">
            <div class="bar-fill bar-grow-fill" :style="{ width: item.rate + '%', background: item.color, animationDelay: (idx * 0.12) + 's' }"></div>
          </div>
          <span class="bar-pct">{{ item.rate }}%</span>
        </div>
      </div>
    </div>

    <!-- 世界地图区域 -->
    <div class="map-container radial-emerge" ref="mapContainer">
      <!-- 只有地图做 3D 倾斜 -->
      <div class="map-scene" :style="{ transform: sceneTransform }" :class="{ 'is-3d': is3D }">
        <div class="map-tilt">
          <div ref="mapEl" class="world-map"></div>
        </div>
      </div>

      <!-- 以下覆盖层保持 2D 正视角，不随地图倾斜 -->
      <!-- 地标标签层 -->
      <div class="marker-layer">
        <div
          v-for="(p, idx) in TEA_CULTURE_POINTS"
          :key="p.id"
          class="landmark-marker wave-pop"
          :class="{ active: selectedPoint && selectedPoint.id === p.id, origin: p.isOrigin }"
          :style="{ ...getMarkerStyle(p), animationDelay: (idx * 0.15) + 's' }"
          @mouseenter="onMarkerHover(p)"
          @mouseleave="onMarkerLeave"
          @click.stop="onMarkerClick(p)"
        >
          <div class="marker-pin">
            <div class="pin-head">
              <img :src="p.image" :alt="p.country" @error="onImgError" />
            </div>
            <div class="pin-stick"></div>
            <div class="pin-dot"></div>
          </div>
          <div class="marker-label">{{ p.country }}</div>
        </div>
      </div>

      <!-- 图例 -->
      <div class="map-legend">
        <div class="legend-row"><span class="legend-dot origin"></span>茶之原产地</div>
        <div class="legend-row"><span class="legend-dot import"></span>主要进口国</div>
      </div>
    </div>

    <!-- 信息卡 -->
    <transition name="card-slide">
      <div v-if="selectedPoint || hoveredPoint" class="info-card slide-in-right card-stagger" :class="{ pinned: selectedPoint }">
        <div v-if="selectedPoint" class="card-close" @click="selectedPoint = null">×</div>
        <div class="card-image">
          <img :src="(selectedPoint || hoveredPoint).image" :alt="(selectedPoint || hoveredPoint).country" @error="onImgError" />
          <div class="card-img-overlay">
            <span class="card-country">{{ (selectedPoint || hoveredPoint).country }}</span>
            <span v-if="(selectedPoint || hoveredPoint).importRate" class="card-import">中国茶进口占比 {{ (selectedPoint || hoveredPoint).importRate }}</span>
          </div>
        </div>
        <div class="card-body">
          <h3 class="card-title">{{ (selectedPoint || hoveredPoint).title }}</h3>
          <div class="card-tags">
            <span class="tag">{{ (selectedPoint || hoveredPoint).drinkStyle }}</span>
            <span class="tag type">{{ (selectedPoint || hoveredPoint).teaType }}</span>
          </div>
          <p class="card-intro">{{ (selectedPoint || hoveredPoint).intro }}</p>
          <p v-if="!selectedPoint && hoveredPoint" class="card-hint">点击 📌 查看完整信息</p>
        </div>
      </div>
    </transition>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import gsap from 'gsap'
import ChapterIntro from './ChapterIntro.vue'
import { TEA_CULTURE_POINTS, TOP_IMPORTERS, GLOBAL_STATS } from '../data/ch6.js'

const props = defineProps({ id: { type: String, required: true } })

const mapEl = ref(null)
const mapContainer = ref(null)
const scrollContainer = ref(null)
const selectedPoint = ref(null)
const hoveredPoint = ref(null)
const sceneTransform = ref('')
const forceUpdate = ref(0)
const introDone = ref(false)
const is3D = ref(false)

let map = null
let tl = null

function onImgError(e) {
  e.target.style.display = 'none'
  e.target.parentElement.style.background = 'linear-gradient(135deg, #B28F4C, #516D33)'
}

const sceneAngle = ref(0)
const sceneScale = ref(1)
const PERSPECTIVE_D = 2600 // 与 .map-container CSS perspective 一致

// 把 Leaflet 地图内的像素坐标 → 经过 rotateX + perspective 投影后的屏幕坐标（相对于 .map-container）
function projectToScreen(ptX, ptY, mapW, mapH) {
  // 地图中心
  const cx = mapW / 2
  const cy = mapH / 2

  // 相对中心偏移
  let x = ptX - cx
  let y = ptY - cy

  // rotateX 变换（绕 X 轴旋转，Y 坐标会产生 Z 位移）
  const angleRad = sceneAngle.value * Math.PI / 180
  const cosA = Math.cos(angleRad)
  const sinA = Math.sin(angleRad)

  // rotateX: y' = y*cos - z*sin, z' = y*sin + z*cos
  const yTilted = y * cosA
  const zTilted = y * sinA // 地图原本 z=0，旋转后产生 z 位移

  // perspective 投影：screenScale = d / (d - z)
  const pScale = PERSPECTIVE_D / (PERSPECTIVE_D - zTilted)

  // 整体 scale
  const s = sceneScale.value

  // 最终屏幕坐标（相对于地图中心）
  const screenX = cx + x * pScale * s
  const screenY = cy + yTilted * pScale * s

  return { x: screenX, y: screenY, scale: pScale, z: zTilted }
}

// 根据经纬度计算标记在 map-container 中的像素位置
function getMarkerStyle(p) {
  forceUpdate.value
  const container = mapEl.value
  if (!container || !map || !mapContainer.value) return { display: 'none' }

  const pt = map.latLngToContainerPoint([p.lat, p.lon])
  const mapW = container.clientWidth
  const mapH = container.clientHeight

  const proj = projectToScreen(pt.x, pt.y, mapW, mapH)

  return {
    left: proj.x + 'px',
    top: proj.y + 'px',
    // 轻微缩放增强立体层次感（近处稍大，远处稍小）
    transform: `translate(-50%, -100%) scale(${0.9 + proj.scale * 0.1})`,
    transformOrigin: 'center bottom',
    zIndex: 600 + Math.round(proj.z),
  }
}

// 2D → 3D 自动转换动画
function play2DTo3D() {
  if (!mapContainer.value) return
  is3D.value = false
  sceneAngle.value = 0
  sceneScale.value = 1

  // 初始 2D 状态
  sceneTransform.value = 'rotateX(0deg) scale(1)'

  // GSAP 时序：停顿 → 缓动转为 3D
  tl = gsap.timeline({
    onComplete: () => { is3D.value = true }
  })

  // 先停顿 2.5 秒，让 2D 地图被看清
  tl.to({}, { duration: 2.5 })

  // 然后用 2 秒转换为 3D
  tl.to({ angle: 38, scale: 0.96 }, {
    duration: 2,
    ease: 'power2.inOut',
    onUpdate: function() {
      const angle = this.targets()[0].angle
      const sc = this.targets()[0].scale
      sceneAngle.value = angle
      sceneScale.value = sc
      // perspective 在父元素上，这里只放 transform
      sceneTransform.value = `rotateX(${angle}deg) scale(${sc})`
      forceUpdate.value++
    }
  })
}

function onMarkerHover(p) {
  if (!selectedPoint.value) {
    hoveredPoint.value = p
  }
}

function onMarkerLeave() {
  hoveredPoint.value = null
}

function onMarkerClick(p) {
  selectedPoint.value = p
  hoveredPoint.value = null
  if (map) {
    map.flyTo([p.lat, p.lon], Math.max(map.getZoom(), 3), { duration: 0.8 })
  }
}

function initMap() {
  map = L.map(mapEl.value, {
    center: [25, 30],
    zoom: 2,
    minZoom: 1,
    maxZoom: 6,
    worldCopyJump: true,
    zoomControl: true,
    attributionControl: false,
  })

  // 世界地图底图 — 浅色风格
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map)

  // 点击地图空白处取消选中
  map.on('click', () => {
    selectedPoint.value = null
  })

  // 地图移动/缩放时更新标记位置
  map.on('move zoom', onMapMove)

  // 把 Leaflet 缩放控件从地图容器中移到外层 2D 容器（保持正视角）
  setTimeout(() => {
    const ctrl = mapEl.value?.querySelector('.leaflet-control-zoom')
    if (ctrl && mapContainer.value) {
      ctrl.style.position = 'absolute'
      ctrl.style.right = '16px'
      ctrl.style.bottom = '14px'
      ctrl.style.zIndex = '900'
      mapContainer.value.appendChild(ctrl)
    }
  }, 50)
}

let moveTimer = null
function onMapMove() {
  if (moveTimer) cancelAnimationFrame(moveTimer)
  moveTimer = requestAnimationFrame(() => {
    forceUpdate.value++
  })
}

function onIntroDone() {
  introDone.value = true
  setTimeout(() => {
    if (map) map.invalidateSize()
    play2DTo3D()
  }, 300)
}

onMounted(async () => {
  await nextTick()
  initMap()
  // 2D→3D 动画在 intro 结束后由 onIntroDone 触发
})

onBeforeUnmount(() => {
  if (tl) tl.kill()
  // 把 zoom 控件归还到 map 容器（否则 map.remove 时会残留 DOM）
  if (map && mapEl.value && mapContainer.value) {
    const ctrl = mapContainer.value.querySelector('.leaflet-control-zoom')
    if (ctrl) mapEl.value.appendChild(ctrl)
  }
  if (moveTimer) cancelAnimationFrame(moveTimer)
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
.chapter-6 {
  position: relative;
  background: var(--c-paper-2);
}

.map-fullscreen {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.8s ease;
  overflow-y: auto;
  padding: 1rem 2rem 5rem;
}
.map-fullscreen.show {
  opacity: 1;
}

/* === 全球数据看板 === */
.stats-board {
  max-width: 1100px;
  margin: 0 auto 1.5rem;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #FAF7EF, #F2EDE0);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.06);
}
.stat-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
}
.stat-value {
  font: 900 1.6rem/1 var(--serif);
  color: var(--c-olive);
}
.stat-value small {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--c-beige-dark);
  margin-left: 4px;
}
.stat-label {
  font: 500 0.75rem/1.3 var(--sans);
  color: var(--muted);
  margin-top: 2px;
}

/* === TOP5 进口国条形图 === */
.importers-bar {
  max-width: 1100px;
  margin: 0 auto 2rem;
  background: linear-gradient(135deg, #FAF7EF, #F5F1E8);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 20px 24px;
}
.bar-title {
  font: 600 0.9rem/1 var(--serif);
  color: var(--c-olive);
  margin-bottom: 14px;
}
.bar-rows {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bar-country {
  width: 70px;
  font: 500 0.82rem/1 var(--sans);
  color: var(--c-olive-deep2);
  text-align: right;
  flex-shrink: 0;
}
.bar-track {
  flex: 1;
  height: 22px;
  background: rgba(0,0,0,0.04);
  border-radius: 6px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.bar-pct {
  width: 50px;
  font: 600 0.8rem/1 var(--sans);
  color: var(--c-gold-deep);
  flex-shrink: 0;
}

/* === 地图场景 === */
.map-container {
  position: relative;
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 0 0;
  /* perspective 放在父容器上，子元素才能真正 3D 透视 */
  perspective: 2600px;
  perspective-origin: 50% 50%;
}

/* 只有地图本身做 3D 倾斜 —— perspective 在父元素上，这里只放 transform */
.map-scene {
  width: 100%;
  height: 620px;
  transform-style: preserve-3d;
  will-change: transform;
}
.map-tilt {
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
}
.world-map {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #E8E4D9;
  border-radius: 0;
  border: none;
  box-shadow: none;
}
.map-scene.is-3d .world-map {
  box-shadow: 0 42px 80px -18px rgba(60, 50, 30, 0.25), 0 16px 36px -14px rgba(60, 50, 30, 0.15);
}

/* === 地标标签层（2D 正视角覆盖层） === */
.marker-layer {
  position: absolute;
  top: 1rem;
  left: 0;
  width: 100%;
  height: 620px;
  pointer-events: none;
  z-index: 600;
}
.landmark-marker {
  position: absolute;
  transform: translate(-50%, -100%);
  pointer-events: auto;
  cursor: pointer;
  z-index: 600;
  transition: transform 0.3s ease;
}
.landmark-marker:hover,
.landmark-marker.active {
  z-index: 700;
  transform: translate(-50%, -108%);
}

.marker-pin {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.pin-head {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
  background: linear-gradient(135deg, #B28F4C, #516D33);
  transition: all 0.3s ease;
}
.pin-head img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.landmark-marker:hover .pin-head,
.landmark-marker.active .pin-head {
  width: 64px;
  height: 64px;
  border-color: var(--c-gold);
  box-shadow: 0 6px 20px rgba(178, 143, 76, 0.4);
}
.pin-stick {
  width: 2px;
  height: 18px;
  background: linear-gradient(to bottom, var(--c-gold), var(--c-olive));
  margin-top: -1px;
}
.pin-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--c-olive);
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  margin-top: -5px;
}
.landmark-marker.origin .pin-dot {
  background: var(--c-olive-mid);
}
.landmark-marker:not(.origin) .pin-dot {
  background: var(--c-gold);
}

.marker-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 4px;
  font: 600 0.72rem/1 var(--sans);
  color: var(--c-olive);
  background: rgba(255,255,255,0.92);
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  border: 1px solid var(--line);
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  opacity: 0;
  transition: opacity 0.3s;
}
.landmark-marker:hover .marker-label,
.landmark-marker.active .marker-label {
  opacity: 1;
}

/* === 图例（2D 正视角覆盖层） === */
.map-legend {
  position: absolute;
  top: calc(1rem + 14px);
  left: 14px;
  background: rgba(255,255,255,0.9);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px 14px;
  font: 500 0.75rem/1.5 var(--sans);
  color: var(--c-olive-deep2);
  z-index: 800;
  backdrop-filter: blur(4px);
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.15);
}
.legend-dot.origin { background: var(--c-olive-mid); }
.legend-dot.import { background: var(--c-gold); }

/* === 信息卡 === */
.info-card {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  width: 380px;
  max-height: 80vh;
  background: rgba(255,255,255,0.95);
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
  z-index: 1000;
  backdrop-filter: blur(8px);
}
.info-card.pinned {
  border-color: var(--c-gold);
  box-shadow: 0 12px 40px rgba(178, 143, 76, 0.25);
}
.card-close {
  position: absolute;
  top: 8px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255,255,255,0.9);
  border: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: var(--c-olive);
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s;
}
.card-close:hover {
  background: var(--c-olive);
  color: #fff;
}
.card-image {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-img-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  padding: 24px 16px 10px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.card-country {
  font: 700 1.1rem/1 var(--serif);
  color: #fff;
  text-shadow: 0 1px 4px rgba(0,0,0,0.4);
}
.card-import {
  font: 600 0.72rem/1 var(--sans);
  color: #fff;
  background: rgba(178, 143, 76, 0.85);
  padding: 4px 8px;
  border-radius: 4px;
}
.card-body {
  padding: 14px 18px 18px;
  overflow-y: auto;
  max-height: calc(80vh - 180px);
}
.card-title {
  font: 700 1.05rem/1.3 var(--serif);
  color: var(--c-olive);
  margin-bottom: 8px;
}
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}
.tag {
  font: 500 0.7rem/1 var(--sans);
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(81, 109, 51, 0.1);
  color: var(--c-olive);
}
.tag.type {
  background: rgba(178, 143, 76, 0.12);
  color: var(--c-gold-deep);
}
.card-intro {
  font: 400 0.82rem/1.7 var(--sans);
  color: #444;
}
.card-hint {
  margin-top: 8px;
  font: 500 0.72rem/1 var(--sans);
  color: var(--c-gold);
  text-align: center;
}

/* === 过渡动画 === */
.card-slide-enter-active,
.card-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.card-slide-enter-from,
.card-slide-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(30px);
}

/* === 响应式 === */
@media (max-width: 960px) {
  .stats-board {
    grid-template-columns: repeat(2, 1fr);
  }
  .info-card {
    width: 320px;
  }
  .world-map {
    height: 460px;
  }
}
@media (max-width: 640px) {
  .map-fullscreen {
    padding: 1rem 1rem 4rem;
  }
  .stats-board {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .stat-card {
    padding: 12px;
  }
  .stat-value {
    font-size: 1.2rem;
  }
  .info-card {
    width: calc(100% - 24px);
    right: 12px;
  }
  .world-map {
    height: 380px;
  }
  .pin-head {
    width: 40px;
    height: 40px;
  }
}

/* ---------- 信息卡内部交错淡入 ---------- */
.info-card.card-stagger > * {
  animation-delay: 0.15s;
}
.info-card.card-stagger .card-image { animation-delay: 0s; }
.info-card.card-stagger .card-title-row { animation-delay: 0.12s; }
.info-card.card-stagger .card-desc { animation-delay: 0.24s; }
.info-card.card-stagger .card-tags { animation-delay: 0.36s; }

/* ---------- 地标标记激活时的色彩波浪 ---------- */
.landmark-marker.active .pin-head {
  animation: ch6Pulse 1.2s cubic-bezier(.4,0,.2,1) infinite;
}
@keyframes ch6Pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(178,143,76,.4); }
  50% { box-shadow: 0 0 0 8px rgba(178,143,76,0); }
}

/* ---------- 条形图动画容器 ---------- */
.bar-row {
  animation: barSlideIn .5s cubic-bezier(.4,0,.2,1) both;
}
@keyframes barSlideIn {
  from { opacity: 0; transform: translateX(-16px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
