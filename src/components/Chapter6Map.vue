<template>
  <section class="chapter chapter-6" :id="id">
    <ChapterIntro
      ch-no="拓 展"
      title="世界共饮"
      desc="茶香跨越山海国界，从中国走向全球各地，融入不同地域生活日常，多元饮茶习俗共生交融，编织出异彩纷呈的世界茶文化图景。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }">
      <div class="bg-layer">
        <div class="bg-image" :style="{ backgroundImage: `url(${bgImageUrl})` }"></div>
        <div class="bg-mask"></div>
      </div>

      <!-- 旋转立体地球 -->
      <div class="globe-wrap" ref="globeWrap">
        <svg ref="globeSvg" class="globe-svg" :width="size.w" :height="size.h" :viewBox="`0 0 ${size.w} ${size.h}`"></svg>
        <div class="globe-tooltip" ref="tooltipEl" hidden></div>
        <ul class="globe-legend">
          <li><span class="dot origin"></span>茶之原产地</li>
          <li><span class="dot importer"></span>主要进口国</li>
        </ul>
        <div class="globe-hint">拖拽旋转 · 悬停查看</div>
      </div>

      <!-- 信息卡 -->
      <transition name="card-slide">
        <div
          v-if="selectedPoint || hoveredPoint"
          class="info-card"
          :class="{ pinned: selectedPoint }"
        >
          <div v-if="selectedPoint" class="card-close" @click="selectedPoint = null">×</div>
          <div class="card-body">
            <div class="card-header">
              <span class="card-country">{{ (selectedPoint || hoveredPoint).country }}</span>
              <span v-if="(selectedPoint || hoveredPoint).importRate" class="card-import">
                中国茶进口占比 {{ (selectedPoint || hoveredPoint).importRate }}
              </span>
            </div>
            <h3 class="card-title">{{ (selectedPoint || hoveredPoint).title }}</h3>
            <div class="card-tags">
              <span class="tag">{{ (selectedPoint || hoveredPoint).drinkStyle }}</span>
              <span class="tag type">{{ (selectedPoint || hoveredPoint).teaType }}</span>
            </div>
            <p class="card-intro">{{ (selectedPoint || hoveredPoint).intro }}</p>
            <div class="card-image-bottom">
              <img
                v-if="(selectedPoint || hoveredPoint).image"
                :src="(selectedPoint || hoveredPoint).image"
                :alt="(selectedPoint || hoveredPoint).country"
                @error="onImgErrorBottom"
              />
              <div v-else class="card-image-fallback-bottom">
                <span class="fallback-text">{{ (selectedPoint || hoveredPoint).country }}</span>
              </div>
            </div>
            <p v-if="!selectedPoint && hoveredPoint" class="card-hint"></p>
          </div>
        </div>
      </transition>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as d3 from 'd3'
import { feature } from 'topojson-client'
import ChapterIntro from './ChapterIntro.vue'
import { TEA_CULTURE_POINTS } from '../data/ch6.js'
import { assetUrl } from '../utils/base.js'

const props = defineProps({ id: { type: String, required: true } })

const globeWrap = ref(null)
const globeSvg = ref(null)
const tooltipEl = ref(null)
const selectedPoint = ref(null)
const hoveredPoint = ref(null)
const introDone = ref(false)
const size = reactive({ w: 800, h: 600 })

// 把数据映射成点（区分原产地 / 进口国）
const POINTS = TEA_CULTURE_POINTS.map(p => ({
  ...p,
  type: p.isOrigin ? 'origin' : 'importer',
}))

const LAND_URL = assetUrl('/data/6/land-110m.json')
const bgImageUrl = assetUrl('/data/6/bg-ch6-tea.jpg')

let landFeature = null
let projection = null
let path = null
let svgSel = null
let gSphere, gGraticule, gLand, gPoints
let autoRotate = true
let hoverInside = false
let timerHandle = null
let dragStart = null
let resumeTimer = null
let wrapEnterHandler = null
let wrapLeaveHandler = null

function onImgError(e) {
  e.target.style.display = 'none'
  e.target.parentElement.style.background = 'linear-gradient(135deg, #B28F4C, #516D33)'
}
function onImgErrorBottom(e) {
  e.target.style.display = 'none'
  e.target.parentElement.querySelector('.card-image-fallback-bottom').style.display = 'flex'
}

function measure() {
  const wrap = globeWrap.value
  if (!wrap) return { w: 800, h: 600 }
  const w = Math.max(320, wrap.clientWidth)
  const h = Math.min(640, Math.max(400, w))
  return { w, h }
}

function onResize() {
  const m = measure()
  if (m.w === size.w && m.h === size.h) return
  size.w = m.w
  size.h = m.h
  if (projection) {
    projection.scale(Math.min(m.w, m.h) * 0.46).translate([m.w / 2, m.h / 2])
    gSphere.selectAll('circle').attr('cx', m.w / 2).attr('cy', m.h / 2).attr('r', projection.scale())
    render()
  }
}

async function initGlobe() {
  const { w, h } = measure()
  size.w = w
  size.h = h

  svgSel = d3.select(globeSvg.value)
  svgSel.attr('width', w).attr('height', h).attr('viewBox', `0 0 ${w} ${h}`)

  // 球体投影 — 初始看向亚洲（茶之原乡）
  projection = d3.geoOrthographic()
    .scale(Math.min(w, h) * 0.46)
    .translate([w / 2, h / 2])
    .rotate([-105, -18, 0])
    .clipAngle(90)

  path = d3.geoPath(projection)

  // === Defs：球面渐变阴影 ===
  const defs = svgSel.append('defs')
  const grad = defs.append('radialGradient')
    .attr('id', 'ch6-sphere-shade')
    .attr('cx', '35%').attr('cy', '32%').attr('r', '72%')
  grad.append('stop').attr('offset', '0%').attr('stop-color', 'rgba(255,255,255,0.32)')
  grad.append('stop').attr('offset', '55%').attr('stop-color', 'rgba(255,255,255,0)')
  grad.append('stop').attr('offset', '100%').attr('stop-color', 'rgba(81,109,51,0.18)')

  // 陆地光晕（外层环绕）
  const glowGrad = defs.append('radialGradient')
    .attr('id', 'ch6-sphere-glow')
    .attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
  glowGrad.append('stop').attr('offset', '78%').attr('stop-color', 'rgba(178,143,76,0)')
  glowGrad.append('stop').attr('offset', '92%').attr('stop-color', 'rgba(178,143,76,0.18)')
  glowGrad.append('stop').attr('offset', '100%').attr('stop-color', 'rgba(178,143,76,0)')

  // === 图层 ===
  gSphere = svgSel.append('g')
  gGraticule = svgSel.append('g')
  gLand = svgSel.append('g')
  gPoints = svgSel.append('g')

  // 外层光晕
  gSphere.append('circle')
    .attr('cx', w / 2).attr('cy', h / 2).attr('r', projection.scale() * 1.05)
    .attr('fill', 'url(#ch6-sphere-glow)')
    .attr('pointer-events', 'none')

  // 球体本体（海洋）
  gSphere.append('circle')
    .attr('cx', w / 2).attr('cy', h / 2).attr('r', projection.scale())
    .attr('class', 'sphere-ocean')
    .attr('fill', '#F7F4EB')
    .attr('stroke', '#C3C19A')
    .attr('stroke-width', 1)

  // 球面阴影叠加
  gSphere.append('circle')
    .attr('cx', w / 2).attr('cy', h / 2).attr('r', projection.scale())
    .attr('fill', 'url(#ch6-sphere-shade)')
    .attr('pointer-events', 'none')

  // === 加载世界陆地数据 ===
  try {
    const world = await fetch(LAND_URL).then(r => r.json())
    landFeature = feature(world, world.objects.land)
  } catch (e) {
    console.error('加载 land-110m 失败', e)
  }

  // 经纬线
  const graticule = d3.geoGraticule10()
  gGraticule.selectAll('path').data([graticule]).join('path')
    .attr('class', 'graticule-line')
    .attr('d', path)
    .attr('fill', 'none')
    .attr('stroke', '#C3C19A')
    .attr('stroke-width', 0.6)
    .attr('opacity', 0.45)

  // 陆地
  if (landFeature) {
    gLand.selectAll('path').data([landFeature]).join('path')
      .attr('class', 'land-shape')
      .attr('d', path)
      .attr('fill', '#EFE9DA')
      .attr('stroke', '#B28F4C')
      .attr('stroke-width', 0.5)
      .attr('stroke-opacity', 0.55)
  }

  // 茶文化点
  const pts = gPoints.selectAll('g.pt').data(POINTS).enter().append('g')
    .attr('class', d => `pt pt-${d.type}`)
    .style('cursor', 'pointer')
    .on('mouseenter', (event, d) => {
      hoverInside = true
      hoveredPoint.value = d
      showTooltip(event, d)
    })
    .on('mousemove', (event) => moveTooltip(event))
    .on('mouseleave', () => {
      hoverInside = false
      if (!selectedPoint.value) hoveredPoint.value = null
      hideTooltip()
    })
    .on('click', (event, d) => {
      event.stopPropagation()
      selectedPoint.value = d
      hoveredPoint.value = null
      hideTooltip()
    })

  pts.append('circle').attr('class', 'halo').attr('r', 9)
  pts.append('circle').attr('class', 'core').attr('r', 4)

  render()

  // === 自动旋转 ===
  let lastT = 0
  timerHandle = d3.timer(t => {
    if (!autoRotate) { lastT = t; return }
    const dt = t - lastT
    lastT = t
    const r = projection.rotate()
    const speed = hoverInside ? 0.0035 : 0.013
    projection.rotate([r[0] + dt * speed, r[1], r[2]])
    render()
  })

  // === 拖拽旋转 ===
  svgSel.call(
    d3.drag()
      .on('start', (event) => {
        autoRotate = false
        hideTooltip()
        dragStart = { x: event.x, y: event.y, rot: projection.rotate() }
      })
      .on('drag', (event) => {
        if (!dragStart) return
        const dx = event.x - dragStart.x
        const dy = event.y - dragStart.y
        const k = 0.4
        const newRot = [
          dragStart.rot[0] + dx * k,
          Math.max(-85, Math.min(85, dragStart.rot[1] - dy * k)),
          dragStart.rot[2],
        ]
        projection.rotate(newRot)
        render()
      })
      .on('end', () => {
        dragStart = null
        if (resumeTimer) clearTimeout(resumeTimer)
        resumeTimer = setTimeout(() => { autoRotate = true }, 1800)
      })
  )

  // 点击地球空白处取消选中
  svgSel.on('click', () => {
    selectedPoint.value = null
  })

  // 鼠标进入地球区域时减速
  const wrap = globeWrap.value
  wrapEnterHandler = () => { hoverInside = true }
  wrapLeaveHandler = () => { hoverInside = false }
  wrap.addEventListener('pointerenter', wrapEnterHandler)
  wrap.addEventListener('pointerleave', wrapLeaveHandler)

  // 尺寸响应
  window.addEventListener('resize', onResize)
}

function render() {
  if (landFeature) {
    gLand.selectAll('path').attr('d', path)
  }
  gGraticule.selectAll('path').attr('d', path)

  const visible = (d) => {
    const r = projection.rotate()
    const center = [-r[0], -r[1]]
    return d3.geoDistance([d.lon, d.lat], center) < Math.PI / 2 - 0.02
  }

  gPoints.selectAll('g.pt')
    .attr('transform', d => {
      const c = projection([d.lon, d.lat])
      if (!c) return 'translate(-9999,-9999)'
      return `translate(${c[0]},${c[1]})`
    })
    .attr('opacity', d => visible(d) ? 1 : 0)
}

// === Tooltip ===
function showTooltip(event, d) {
  const tip = tooltipEl.value
  if (!tip) return
  tip.innerHTML = `
    <span class="tip-kind tip-${d.type}">${d.type === 'origin' ? '原产地' : '进口国'}</span>
    <strong>${d.country}</strong>
    <em>${d.drinkStyle}</em>
  `
  tip.hidden = false
  moveTooltip(event)
}
function moveTooltip(event) {
  const tip = tooltipEl.value
  if (!tip || tip.hidden) return
  const rect = globeWrap.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const tw = tip.offsetWidth
  const th = tip.offsetHeight
  let left = x + 14
  let top = y + 14
  if (left + tw > rect.width - 8) left = x - tw - 14
  if (top + th > rect.height - 8) top = y - th - 14
  tip.style.left = `${Math.max(8, left)}px`
  tip.style.top = `${Math.max(8, top)}px`
}
function hideTooltip() {
  const tip = tooltipEl.value
  if (tip) tip.hidden = true
}

function onIntroDone() {
  introDone.value = true
  setTimeout(() => initGlobe(), 200)
}

onMounted(async () => {
  await nextTick()
  // 真正的初始化在 intro 结束后触发
})

onBeforeUnmount(() => {
  if (timerHandle) timerHandle.stop()
  if (resumeTimer) clearTimeout(resumeTimer)
  window.removeEventListener('resize', onResize)
  const wrap = globeWrap.value
  if (wrap) {
    if (wrapEnterHandler) wrap.removeEventListener('pointerenter', wrapEnterHandler)
    if (wrapLeaveHandler) wrap.removeEventListener('pointerleave', wrapLeaveHandler)
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
  padding: 1.5rem 2rem 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  position: fixed;
}
.map-fullscreen .bg-layer {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}
.map-fullscreen .bg-layer .bg-image {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.28;
  filter: blur(5px);
  transform: scale(1.05);
}
.map-fullscreen .bg-layer .bg-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(239,233,218,0.45) 0%, rgba(247,244,235,0.65) 60%, rgba(247,244,235,0.8) 100%);
}
.map-fullscreen > .globe-wrap,
.map-fullscreen > .legend-box,
.map-fullscreen > .tip-box,
.map-fullscreen > .rotate-tip,
.map-fullscreen > .ch-nav {
  position: relative;
  z-index: 1;
}
.map-fullscreen.show {
  opacity: 1;
}

/* === 旋转地球容器 === */
.globe-wrap {
  position: relative;
  width: 100%;
  max-width: 880px;
  margin: 0 auto;
  touch-action: none;
}

.globe-svg {
  display: block;
  width: 100%;
  height: auto;
  cursor: grab;
  touch-action: none;
}
.globe-svg:active {
  cursor: grabbing;
}

/* === 点位（原产地/进口国） === */
:deep(.pt) { transition: opacity 0.25s ease; }
:deep(.pt .halo) {
  transition: r 0.2s ease, fill-opacity 0.2s ease;
}
:deep(.pt .core) {
  stroke: #F7F4EB;
  stroke-width: 1.4;
  transition: r 0.2s ease;
}
:deep(.pt-origin .core) { fill: #516D33; }
:deep(.pt-origin .halo) { fill: #516D33; fill-opacity: 0.22; }
:deep(.pt-importer .core) { fill: #B28F4C; }
:deep(.pt-importer .halo) { fill: #B28F4C; fill-opacity: 0.22; }

:deep(.pt:hover .core) { r: 5.5; }
:deep(.pt:hover .halo) { r: 12; fill-opacity: 0.36; }

/* 标记呼吸脉冲（原产地） */
:deep(.pt-origin .halo) {
  animation: ch6HaloPulse 2.6s ease-in-out infinite;
}
@keyframes ch6HaloPulse {
  0%, 100% { r: 9; fill-opacity: 0.22; }
  50% { r: 13; fill-opacity: 0.08; }
}

/* === Tooltip === */
.globe-tooltip {
  position: absolute;
  pointer-events: none;
  z-index: 10;
  background: rgba(247, 244, 235, 0.96);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 8px 12px;
  max-width: 240px;
  font-size: 0.78rem;
  line-height: 1.4;
  box-shadow: 0 4px 18px rgba(50, 42, 38, 0.12);
  backdrop-filter: blur(6px);
}
.globe-tooltip strong {
  display: block;
  font: 700 0.9rem/1.2 var(--serif);
  color: var(--c-olive);
  margin: 4px 0 2px;
}
.globe-tooltip em {
  display: block;
  font: 400 0.72rem/1.4 var(--sans);
  font-style: normal;
  color: var(--ink-soft);
}
.globe-tooltip .tip-kind {
  display: inline-block;
  font: 500 0.62rem/1 var(--sans);
  letter-spacing: 0.08em;
  padding: 2px 6px;
  border-radius: 3px;
  text-transform: uppercase;
}
.tip-kind.tip-origin { background: rgba(81,109,51,0.12); color: var(--c-olive); }
.tip-kind.tip-importer { background: rgba(178,143,76,0.16); color: var(--c-gold-deep); }

/* === 图例 === */
.globe-legend {
  position: absolute;
  right: 8px;
  bottom: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font: 500 0.7rem/1 var(--sans);
  letter-spacing: 0.06em;
  color: var(--ink-soft);
  pointer-events: none;
  background: rgba(247, 244, 235, 0.7);
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--line);
}
.globe-legend li {
  display: flex;
  align-items: center;
  gap: 6px;
}
.globe-legend .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.15);
}
.globe-legend .dot.origin { background: #516D33; }
.globe-legend .dot.importer { background: #B28F4C; }

/* 操作提示 */
.globe-hint {
  position: absolute;
  left: 8px;
  bottom: 8px;
  font: 400 0.68rem/1 var(--sans);
  letter-spacing: 0.15em;
  color: var(--muted);
  background: rgba(247, 244, 235, 0.7);
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid var(--line);
  pointer-events: none;
}

/* === 信息卡 === */
.info-card {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  width: 380px;
  height: 80vh;
  max-height: 80vh;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
}
.info-card.pinned {
  border-color: var(--c-gold);
  box-shadow: 0 12px 40px rgba(178, 143, 76, 0.25);
}
.card-close {
  position: absolute;
  top: 10px;
  right: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
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
.fallback-text {
  font: 900 1.6rem/1.2 var(--serif);
  color: #F7F4EB;
  letter-spacing: 0.1em;
  text-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.card-body {
  padding: 18px 20px 20px;
  overflow-y: auto;
  flex: 1;
  height: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(178, 143, 76, 0.2);
}
.card-country {
  font: 700 1.2rem/1 var(--serif);
  color: var(--c-olive);
}
.card-import {
  font: 600 0.72rem/1 var(--sans);
  color: #fff;
  background: var(--c-gold);
  padding: 4px 8px;
  border-radius: 4px;
  flex-shrink: 0;
  margin-left: 10px;
}
.card-title {
  font: 700 1.05rem/1.3 var(--serif);
  color: var(--c-olive);
  margin-bottom: 8px;
  margin-top: 4px;
}
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
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
  font: 400 0.85rem/1.75 var(--sans);
  color: #444;
  margin-bottom: 16px;
}
.card-image-bottom {
  width: 100%;
  margin-top: 8px;
  margin-bottom: 4px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(194, 193, 154, 0.4);
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.08);
}
.card-image-bottom img {
  width: 100%;
  height: auto;
  max-height: 320px;
  object-fit: contain;
  display: block;
  background: var(--c-paper-2);
}
.card-image-fallback-bottom {
  width: 100%;
  height: 200px;
  display: none;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #516D33 0%, #5C7C3A 50%, #B28F4C 100%);
  position: relative;
}
.card-image-fallback-bottom::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 30% 30%, rgba(247,244,235,0.15), transparent 50%),
    radial-gradient(circle at 70% 70%, rgba(81,109,51,0.2), transparent 50%);
}
.card-hint {
  margin-top: 12px;
  font: 500 0.72rem/1 var(--sans);
  color: var(--c-gold);
  text-align: center;
}

/* 滚动条美化 */
.card-body::-webkit-scrollbar {
  width: 6px;
}
.card-body::-webkit-scrollbar-track {
  background: transparent;
}
.card-body::-webkit-scrollbar-thumb {
  background: rgba(178, 143, 76, 0.35);
  border-radius: 3px;
}
.card-body::-webkit-scrollbar-thumb:hover {
  background: rgba(178, 143, 76, 0.55);
}

/* === 过渡 === */
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
  .info-card {
    width: 320px;
    height: 75vh;
    max-height: 75vh;
  }
}
@media (max-width: 640px) {
  .map-fullscreen {
    padding: 1rem 1rem 4rem;
  }
  .info-card {
    width: calc(100% - 24px);
    right: 12px;
    top: auto;
    bottom: 12px;
    transform: none;
    height: 60vh;
    max-height: 60vh;
  }
  .card-slide-enter-from,
  .card-slide-leave-to {
    opacity: 0;
    transform: translateY(30px);
  }
  .info-card {
    transform: none;
  }
}
</style>
