<template>
  <div id="app-root">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">茶</span>
        <span class="brand-text">茶之中国</span>
      </div>
      <div class="nav-links">
        <router-link
          v-for="r in navItems"
          :key="r.path"
          :to="r.path"
          :class="{ active: currentRoute === r.path }"
        >
          <span class="nav-num">{{ r.idx }}</span>
          <span class="nav-label">{{ r.label }}</span>
        </router-link>
      </div>
      <div class="nav-progress">
        <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
      </div>
    </nav>

    <!-- 路由视图 -->
    <router-view v-slot="{ Component }">
      <transition name="page-fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- 章节切换底部控制 -->
    <div class="chapter-switch">
      <button
        v-if="prevRoute"
        class="switch-btn prev"
        @click="$router.push(prevRoute)"
      >
        ← {{ prevLabel }}
      </button>
      <div v-else class="switch-btn hidden"></div>
      <div class="page-indicator">{{ currentIdx }} / 6</div>
      <button
        v-if="nextRoute"
        class="switch-btn next"
        @click="$router.push(nextRoute)"
      >
        {{ nextLabel }} →
      </button>
      <div v-else class="switch-btn hidden"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/ch1', idx: '一', label: '茶生山水间' },
  { path: '/ch2', idx: '二', label: '何以生茶' },
  { path: '/ch3', idx: '三', label: '云雾深处' },
  { path: '/ch4', idx: '四', label: '一叶行远' },
  { path: '/ch5', idx: '五', label: '今日茶境' },
  { path: '/ch6', idx: '六', label: '世界共饮' },
]

const currentRoute = computed(() => route.path)
const currentIdx = computed(() => {
  const item = navItems.find(n => n.path === route.path)
  return item ? navItems.indexOf(item) + 1 : 1
})

const prevRoute = computed(() => {
  const i = navItems.findIndex(n => n.path === route.path)
  return i > 0 ? navItems[i - 1].path : null
})
const nextRoute = computed(() => {
  const i = navItems.findIndex(n => n.path === route.path)
  return i < navItems.length - 1 ? navItems[i + 1].path : null
})
const prevLabel = computed(() => {
  const i = navItems.findIndex(n => n.path === route.path)
  return i > 0 ? navItems[i - 1].label : ''
})
const nextLabel = computed(() => {
  const i = navItems.findIndex(n => n.path === route.path)
  return i < navItems.length - 1 ? navItems[i + 1].label : ''
})

const progressPct = ref(0)
function onScroll() {
  const h = document.documentElement
  const max = Math.max(1, h.scrollHeight - h.clientHeight)
  progressPct.value = Math.round((h.scrollTop / max) * 1000) / 10
}
onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
#app-root {
  min-height: 100vh;
  background: var(--c-paper-2, #F7F4EB);
}

/* ===== 顶部导航 ===== */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(247, 244, 235, 0.96);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line, rgba(81,109,51,.18));
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  box-shadow: 0 2px 16px -8px rgba(61, 84, 40, 0.15);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.brand-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--c-olive, #516D33);
  color: var(--c-paper, #EFE9DA);
  border-radius: 50%;
  font: 700 18px var(--serif);
}
.brand-text {
  font: 700 18px var(--serif);
  color: var(--c-olive, #516D33);
  letter-spacing: 0.05em;
}

.nav-links {
  display: flex;
  gap: 4px;
  margin-left: 32px;
  flex: 1;
  overflow-x: auto;
}
.nav-links::-webkit-scrollbar { display: none; }

.nav-links a {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 24px;
  text-decoration: none;
  color: var(--ink-soft, #4a4a40);
  font: 500 13px var(--sans);
  white-space: nowrap;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}
.nav-links a .nav-num {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--c-paper, #EFE9DA);
  color: var(--c-olive-mid, #5C7C3A);
  border-radius: 50%;
  font: 600 11px var(--sans);
  transition: all 0.3s ease;
}
.nav-links a:hover {
  color: var(--c-olive, #516D33);
  background: rgba(81,109,51,0.08);
}
.nav-links a:hover .nav-num {
  background: var(--c-olive, #516D33);
  color: #fff;
}
.nav-links a.active {
  color: var(--c-olive, #516D33);
  background: var(--c-paper, #EFE9DA);
  border-color: var(--c-olive-light, #8BA06A);
  font-weight: 600;
}
.nav-links a.active .nav-num {
  background: var(--c-olive, #516D33);
  color: #fff;
}

.nav-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--c-paper, #EFE9DA);
  width: 100%;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--c-olive, #516D33), var(--c-gold, #B28F4C));
  transition: width 0.15s ease;
}

/* ===== 章节切换 ===== */
.chapter-switch {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 999;
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(247, 244, 235, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid var(--line, rgba(81,109,51,.18));
  border-radius: 40px;
  padding: 8px 12px;
  box-shadow: 0 8px 32px -8px rgba(61, 84, 40, 0.25);
}
.switch-btn {
  background: transparent;
  border: none;
  padding: 8px 16px;
  color: var(--ink-soft, #4a4a40);
  font: 500 14px var(--sans);
  cursor: pointer;
  border-radius: 24px;
  transition: all 0.3s ease;
}
.switch-btn:hover:not(.hidden) {
  background: var(--c-olive, #516D33);
  color: #fff;
}
.switch-btn.hidden {
  visibility: hidden;
}
.page-indicator {
  font: 600 13px var(--sans);
  color: var(--c-olive, #516D33);
  padding: 0 8px;
}

/* ===== 页面切换过渡 ===== */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* 为页面内容留出顶部导航和底部切换栏空间 */
:deep(.chapter),
:deep(.page-wrap) {
  padding-top: 80px;
  padding-bottom: 80px;
}

@media (max-width: 880px) {
  .nav-brand .brand-text { display: none; }
  .nav-links { margin-left: 16px; }
  .nav-links a { padding: 6px 10px; font-size: 12px; }
  .nav-links a .nav-label { display: none; }
}
</style>
