<template>
  <header
    v-if="chapter"
    class="chapter-corner-intro"
    :class="[`chapter-corner-intro--${chapterKey}`, { 'is-visible': visible }]"
    aria-hidden="true"
  >
    <div class="chapter-corner-heading">
      <span class="chapter-corner-number">{{ chapter.number }}</span>
      <h1 class="chapter-corner-title">{{ chapter.title }}</h1>
    </div>
    <div class="chapter-corner-rule"></div>
    <p class="chapter-corner-description">{{ chapter.description }}</p>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { getChapterMeta } from '../data/chapterMeta.js'

const props = defineProps({
  chapterKey: { type: String, required: true },
  visible: { type: Boolean, default: false }
})

const chapter = computed(() => getChapterMeta(props.chapterKey))
</script>

<style scoped>
.chapter-corner-intro {
  position: absolute;
  top: var(--chapter-corner-top, clamp(28px, 4vh, 46px));
  left: var(--chapter-corner-left, clamp(28px, 3vw, 58px));
  z-index: 360;
  width: var(--chapter-corner-width, clamp(320px, 26vw, 480px));
  max-width: calc(100vw - 56px);
  color: #405c2d;
  pointer-events: none;
  user-select: none;
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 700ms ease, transform 800ms cubic-bezier(.22, .75, .22, 1);
  text-shadow: 0 1px 8px rgba(247, 244, 235, .78);
}

.chapter-corner-intro.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.chapter-corner-heading {
  display: flex;
  align-items: baseline;
  gap: .7em;
  font-family: "QuanHengDuLiang", "Noto Serif SC", Georgia, "Times New Roman", serif;
}

.chapter-corner-number {
  flex: 0 0 auto;
  color: #b28f4c;
  font-size: clamp(16px, 1.2vw, 22px);
  line-height: 1;
}

.chapter-corner-title {
  margin: 0;
  color: #405c2d;
  font-family: inherit;
  font-size: clamp(34px, 2.8vw, 52px);
  font-weight: 500;
  line-height: 1.12;
  letter-spacing: .08em;
}

.chapter-corner-rule {
  width: min(100%, 210px);
  height: 1px;
  margin: 12px 0 11px;
  background: linear-gradient(90deg, rgba(178, 143, 76, .72), rgba(178, 143, 76, 0));
}

.chapter-corner-description {
  margin: 0;
  color: #675f4d;
  font-family: "ChillHuoKai", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif;
  font-size: clamp(14px, .95vw, 18px);
  font-weight: 400;
  line-height: 1.85;
  letter-spacing: .04em;
  text-align: justify;
}

.chapter-corner-intro--ch4 {
  --chapter-corner-top: clamp(92px, 12vh, 126px);
  --chapter-corner-width: clamp(300px, 22vw, 410px);
}

.chapter-corner-intro--ch5 {
  --chapter-corner-top: clamp(22px, 3vh, 36px);
  --chapter-corner-width: clamp(260px, 20vw, 350px);
}

.chapter-corner-intro--ch6 {
  --chapter-corner-top: clamp(34px, 5vh, 58px);
  --chapter-corner-width: clamp(300px, 22vw, 410px);
}

/* 第一章底图是山脉/海洋纹理 art，art 不同 stage 亮度/色调不同。
   用户诉求：标题与简介文字亮度独立（不跟随底图 art 变化）。
   仅通过 text-shadow 在字体渲染层叠加米色光晕（不动文字 color），
   让文字"自带光晕"在不同底图下都有稳定亮度感。
   不改变任何版式（不增 padding/border/background），不修改文字颜色。 */
.chapter-corner-intro--ch1 {
  text-shadow:
    0 0 10px rgba(247, 244, 235, 0.95),
    0 0 22px rgba(247, 244, 235, 0.88),
    0 0 36px rgba(247, 244, 235, 0.72),
    0 1px 2px rgba(247, 244, 235, 1);
}

@media (max-width: 900px) {
  .chapter-corner-intro {
    --chapter-corner-left: 18px;
    --chapter-corner-width: min(360px, calc(100vw - 36px));
  }
  .chapter-corner-title { font-size: clamp(30px, 6vw, 42px); }
}

@media (prefers-reduced-motion: reduce) {
  .chapter-corner-intro { transition: none; transform: none; }
}
</style>
