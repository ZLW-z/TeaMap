import { createRouter, createWebHashHistory } from 'vue-router'
import Prologue from '../components/PrologueMap.vue'
import Chapter1 from '../components/Chapter1Map.vue'
import Chapter2 from '../components/Chapter2Map.vue'
import Chapter3 from '../components/Chapter3Map.vue'
import Chapter4 from '../components/Chapter4Map.vue'
import Chapter5 from '../components/Chapter5Map.vue'
import Chapter6 from '../components/Chapter6Map.vue'
import Epilogue from '../components/EpilogueMap.vue'

const routes = [
  { path: '/', redirect: '/prologue' },
  { path: '/prologue', name: 'prologue', component: Prologue, meta: { title: '序言', idx: '序', isBookend: true, order: 0 } },
  { path: '/ch1', name: 'ch1', component: Chapter1, meta: { title: '第一章 · 茶生山水间', idx: '壹', order: 1 } },
  { path: '/ch2', name: 'ch2', component: Chapter2, meta: { title: '第二章 · 何以生茶', idx: '贰', order: 2 } },
  { path: '/ch3', name: 'ch3', component: Chapter3, meta: { title: '第三章 · 云雾深处', idx: '叁', order: 3 } },
  { path: '/ch4', name: 'ch4', component: Chapter4, meta: { title: '第四章 · 一叶行远', idx: '肆', order: 4 } },
  { path: '/ch5', name: 'ch5', component: Chapter5, meta: { title: '第五章 · 今日茶境', idx: '伍', order: 5 } },
  { path: '/ch6', name: 'ch6', component: Chapter6, meta: { title: '第六章 · 世界共饮', idx: '陆', order: 6 } },
  { path: '/epilogue', name: 'epilogue', component: Epilogue, meta: { title: '结语', idx: '终', isBookend: true, order: 7 } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
