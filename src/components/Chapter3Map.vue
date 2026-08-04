<template>
  <section class="chapter chapter-3" :id="id" ref="sectionEl">
    <ChapterIntro
      ch-no="第 三 章"
      title="云雾深处"
      desc="山川毓秀，名茶辈出。十大名茶与六大茶类名茶星罗棋布于华夏大地，点击圆点，一览茶之故事。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }">
      <div ref="mapEl" class="map"></div>

      <!-- 图例 -->
      <div class="map-legend">
        <div class="legend-title">图例</div>
        <div class="legend-row top10">
          <span class="sw top10-sw"></span>十大名茶（{{ top10Count }}）
        </div>
        <div class="legend-row other">
          <span class="sw other-sw"></span>其他名茶（{{ otherCount }}）
        </div>
        <div class="legend-hint">点击标记查看详情</div>
      </div>

      <!-- 固定信息面板 -->
      <transition name="panel-slide">
        <div
          v-if="selectedTea"
          class="tea-info-panel"
        >
          <div class="panel-header">
            <div class="panel-title-wrap">
              <span class="panel-badge" :class="{ top10: selectedTea.isTop10 }">
                {{ selectedTea.isTop10 ? '十大名茶' : '名茶' }}
              </span>
              <h3 class="panel-title">{{ selectedTea.name }}</h3>
            </div>
            <button class="panel-close" @click="closePanel">×</button>
          </div>

          <div class="panel-scroll">
            <div class="panel-image-wrap">
              <img :src="selectedTea.image" :alt="selectedTea.name" class="panel-image" />
            </div>

            <div class="panel-meta">
              <span class="meta-type">{{ selectedTea.type }}</span>
              <span class="meta-origin">{{ selectedTea.origin }}</span>
            </div>

            <div class="panel-section">
              <div class="section-label">核心特点</div>
              <p class="section-text">{{ selectedTea.features }}</p>
            </div>

            <div class="panel-section">
              <div class="section-label">故事 / 传说</div>
              <p class="section-text story">{{ selectedTea.story }}</p>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import { createAlbersCRS } from '../utils/crs.js'
import ChapterIntro from './ChapterIntro.vue'
import {
  TEAS,
  TEA_TYPE_COLORS,
  TOP10_STYLE,
  OTHER_STYLE,
  PROV_BG_URL,
  PROV_STYLE,
  MAP_INIT,
} from '../config/ch3.js'

const props = defineProps({ id: { type: String, required: true } })

const sectionEl = ref(null)
const mapEl = ref(null)
const selectedTea = ref(null)
const activeMarker = ref(null)
const introDone = ref(false)
let map = null
let markers = []
let zoomAnimDone = false
let io = null

function onIntroDone() {
  introDone.value = true
  setTimeout(() => {
    if (map) map.invalidateSize()
    runZoomAnimation()
  }, 300)
}

const top10Count = TEAS.filter(t => t.isTop10).length
const otherCount = TEAS.filter(t => !t.isTop10).length

onMounted(async () => {
  await nextTick()
  initMap()
  // 缩放动画在 intro 结束后由 onIntroDone 触发
})

onBeforeUnmount(() => {
  if (io) { io.disconnect(); io = null }
  if (map) { map.remove(); map = null }
})

function initMap() {
  map = L.map(mapEl.value, {
    crs: createAlbersCRS(),
    center: MAP_INIT.center,
    zoom: MAP_INIT.zoom,
    minZoom: MAP_INIT.minZoom,
    maxZoom: MAP_INIT.maxZoom,
    zoomControl: false,
    attributionControl: false,
  })

  L.control.zoom({ position: 'bottomright' }).addTo(map)

  // 创建省份底图专用 pane，z-index 低于标记所在 overlay pane(400)
  map.createPane('provPane')
  map.getPane('provPane').style.zIndex = 350

  // 省份底图
  fetch(PROV_BG_URL)
    .then(r => r.json())
    .then(geo => {
      L.geoJSON(geo, {
        pane: 'provPane',
        style: () => ({
          color: PROV_STYLE.color,
          weight: PROV_STYLE.weight,
          fillColor: PROV_STYLE.fillColor,
          fillOpacity: PROV_STYLE.fillOpacity,
        }),
      }).addTo(map)
    })
    .catch(err => console.warn('省份底图加载失败:', err))

  // 添加名茶点
  TEAS.forEach(tea => {
    if (tea.lat == null || tea.lng == null) return

    const style = tea.isTop10 ? TOP10_STYLE : OTHER_STYLE
    const marker = L.circleMarker([tea.lat, tea.lng], style)

    // 十大名茶添加脉冲外圈
    if (tea.isTop10) {
      const pulse = L.circleMarker([tea.lat, tea.lng], {
        radius: style.radius + 6,
        fillColor: '#B28F4C',
        color: '#B28F4C',
        weight: 0,
        fillOpacity: 0.15,
      })
      pulse.addTo(map)
    }

    marker.bindTooltip(tea.name, {
      permanent: false,
      direction: 'top',
      offset: [0, -8],
      className: 'tea-tip',
    })

    marker.on('mouseover', () => {
      if (!selectedTea.value || selectedTea.value.name !== tea.name) {
        marker.setStyle({ radius: style.radius + 2, weight: 3 })
      }
    })

    marker.on('mouseout', () => {
      if (!selectedTea.value || selectedTea.value.name !== tea.name) {
        marker.setStyle(style)
      }
    })

    marker.on('click', (e) => {
      L.DomEvent.stopPropagation(e)
      selectTea(tea, marker, style)
    })

    marker.addTo(map)
    markers.push(marker)
  })

  // 点击地图空白处关闭面板
  map.on('click', () => {
    closePanel()
  })

  // 暴露到 window 便于调试
  if (import.meta.env.DEV) {
    window.__ch3map = map
    window.__ch3markers = markers
  }
}

function runZoomAnimation() {
  if (!map || markers.length === 0) return

  // 阶段1：确保展示完整中国地图（初始视图）
  map.setView(MAP_INIT.center, MAP_INIT.zoom, { animate: false })

  // 阶段2：等待2秒后，放大到所有名茶点的最小地理范围
  setTimeout(() => {
    if (!map) return

    // 计算所有标记的边界
    const bounds = L.latLngBounds(markers.map(m => m.getLatLng()))

    // 使用 flyTo 平滑过渡到包含所有标记的范围
    // padding 让标记不贴边
    map.flyToBounds(bounds, {
      padding: [60, 60],
      maxZoom: 6,
      duration: 2.5,
      easeLinearity: 0.25,
    })
  }, 2000)
}

function selectTea(tea, marker, style) {
  // 恢复之前激活的标记
  if (activeMarker.value && activeMarker.value !== marker) {
    const prevTea = selectedTea.value
    const prevStyle = prevTea && prevTea.isTop10 ? TOP10_STYLE : OTHER_STYLE
    activeMarker.value.setStyle(prevStyle)
  }

  selectedTea.value = tea
  activeMarker.value = marker

  // 激活状态样式
  marker.setStyle({
    radius: style.radius + 4,
    weight: 4,
    color: '#FFFFFF',
    fillOpacity: 1,
  })

  // 平移地图使标记可见
  map.panTo([tea.lat, tea.lng], { animate: true, duration: 0.4 })
}

function closePanel() {
  if (activeMarker.value && selectedTea.value) {
    const tea = selectedTea.value
    const style = tea.isTop10 ? TOP10_STYLE : OTHER_STYLE
    activeMarker.value.setStyle(style)
  }
  selectedTea.value = null
  activeMarker.value = null
}
</script>

<style scoped>
.chapter-3 {
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

/* 南海九段线插图已移除 */

/* 图例 */
.map-legend {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 800;
  background: rgba(247, 244, 235, 0.92);
  backdrop-filter: blur(8px);
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  font-size: 0.85rem;
}

.legend-title {
  font-weight: 700;
  color: var(--c-olive);
  margin-bottom: 8px;
  font-size: 0.8rem;
  letter-spacing: 0.1em;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  color: var(--c-beige-dark);
}

.legend-row .sw {
  display: inline-block;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.top10-sw {
  width: 16px;
  height: 16px;
  background: var(--c-gold);
}

.other-sw {
  width: 12px;
  height: 12px;
  background: var(--c-olive-mid);
}

.legend-hint {
  margin-top: 8px;
  font-size: 0.72rem;
  color: var(--c-beige);
  font-style: italic;
}

/* 固定信息面板 */
.tea-info-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  bottom: 16px;
  width: 360px;
  max-width: 40%;
  z-index: 900;
  background: rgba(247, 244, 235, 0.97);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(81, 109, 51, 0.18);
  border: 1px solid rgba(178, 143, 76, 0.15);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(178, 143, 76, 0.12);
  flex-shrink: 0;
}

.panel-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.panel-badge {
  display: inline-block;
  background: var(--c-olive-mid);
  color: #fff;
  font-size: 0.7rem;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  width: fit-content;
}

.panel-badge.top10 {
  background: var(--c-gold);
}

.panel-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--c-olive);
  margin: 0;
  letter-spacing: 0.05em;
}

.panel-close {
  width: 28px;
  height: 28px;
  border: none;
  background: var(--c-paper-3);
  color: var(--c-beige-dark);
  font-size: 1.2rem;
  line-height: 1;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.panel-close:hover {
  background: var(--c-gold);
  color: #fff;
}

.panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px 20px;
}

.panel-scroll::-webkit-scrollbar {
  width: 6px;
}

.panel-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.panel-scroll::-webkit-scrollbar-thumb {
  background: rgba(178, 143, 76, 0.3);
  border-radius: 3px;
}

.panel-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(178, 143, 76, 0.5);
}

.panel-image-wrap {
  width: 100%;
  height: 160px;
  overflow: hidden;
  border-radius: 8px;
  background: var(--c-paper-2);
  margin-bottom: 12px;
}

.panel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.panel-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 0.78rem;
  flex-wrap: wrap;
}

.meta-type {
  background: var(--c-paper-2);
  color: var(--c-gold-deep);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  white-space: nowrap;
}

.meta-origin {
  color: var(--c-beige-dark);
}

.panel-section {
  margin-bottom: 14px;
}

.section-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--c-gold);
  letter-spacing: 0.1em;
  margin-bottom: 5px;
}

.section-text {
  font-size: 0.85rem;
  line-height: 1.65;
  color: #555;
  margin: 0;
}

/* 面板滑入动画 */
.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.3s ease;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Leaflet tooltip */
:deep(.tea-tip) {
  background: var(--c-olive);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  padding: 3px 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  pointer-events: none;
}

:deep(.tea-tip::before) {
  border-top-color: var(--c-olive);
}

/* 响应式 */
@media (max-width: 768px) {
  .tea-info-panel {
    position: absolute;
    top: auto;
    right: 8px;
    bottom: 8px;
    left: 8px;
    width: auto;
    max-width: none;
    max-height: 50%;
  }
}
</style>
