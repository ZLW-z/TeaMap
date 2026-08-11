<template>
  <transition name="intro-fade">
    <div v-if="visible" class="chapter-intro" ref="introRef">
      <div class="intro-overlay"></div>
      <div class="intro-content">
        <div class="intro-ch-no" ref="chNoRef">{{ chNo }}</div>
        <div class="intro-title-row" ref="titleRowRef">
          <span
            v-for="(ch, i) in titleChars"
            :key="i"
            class="intro-char"
            :ref="el => charRefs[i] = el"
          >{{ ch === ' ' ? '\u00A0' : ch }}</span>
        </div>
        <div class="intro-desc" ref="descRef">{{ desc }}</div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import gsap from 'gsap'

const props = defineProps({
  chNo: { type: String, required: true },
  title: { type: String, required: true },
  desc: { type: String, default: '' },
  duration: { type: Number, default: 2.8 },
})

const emit = defineEmits(['done'])

const visible = ref(true)
const introRef = ref(null)
const chNoRef = ref(null)
const titleRowRef = ref(null)
const descRef = ref(null)

const titleChars = props.title.split('')
const charRefs = []

let tl = null

onMounted(async () => {
  await nextTick()

  // 初始状态
  gsap.set(charRefs, { opacity: 0, y: 40, rotateX: -90 })
  gsap.set(chNoRef.value, { opacity: 0, y: -20, scale: 0.6 })
  gsap.set(descRef.value, { opacity: 0, y: 30 })

  const holdTime = props.duration
  const charStagger = Math.min(0.08, holdTime * 0.4 / titleChars.length)

  tl = gsap.timeline({
    onComplete: () => {
      visible.value = false
      emit('done')
    }
  })

  // 1. 章节号浮现
  tl.to(chNoRef.value, {
    opacity: 1,
    y: 0,
    scale: 1,
    duration: 0.6,
    ease: 'power3.out'
  })

  // 2. 标题逐字浮现
  tl.to(charRefs, {
    opacity: 1,
    y: 0,
    rotateX: 0,
    duration: 0.5,
    stagger: charStagger,
    ease: 'back.out(1.4)'
  }, '-=0.2')

  // 3. 描述渐显
  tl.to(descRef.value, {
    opacity: 0.85,
    y: 0,
    duration: 0.8,
    ease: 'power2.out'
  }, '-=0.15')

  // 4. 停留
  tl.to({}, { duration: holdTime })

  // 5. 整体消散
  tl.to([chNoRef.value, titleRowRef.value, descRef.value], {
    opacity: 0,
    y: -30,
    filter: 'blur(8px)',
    duration: 0.8,
    stagger: 0.06,
    ease: 'power2.in'
  })
  tl.to(introRef.value, {
    opacity: 0,
    duration: 0.4,
    ease: 'power2.in'
  }, '-=0.3')
})

onBeforeUnmount(() => {
  if (tl) tl.kill()
})
</script>

<style scoped>
.chapter-intro {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.intro-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(247, 244, 235, 0.98) 0%, rgba(239, 233, 218, 0.99) 60%, rgba(221, 213, 192, 1) 100%);
}

.intro-content {
  position: relative;
  text-align: center;
  z-index: 1;
  padding: 0 2rem;
  max-width: 800px;
}

.intro-ch-no {
  font-family: var(--font-qiji, 'Noto Serif SC', serif);
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--c-gold, #B28F4C);
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: center;
}

.intro-title-row {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.intro-char {
  font-family: var(--font-kesong, 'Noto Serif SC', serif);
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 700;
  color: var(--c-olive, #516D33);
  letter-spacing: 0.15em;
  display: inline-block;
  transform-origin: center bottom;
}

.intro-desc {
  font-family: var(--font-huokai, 'Noto Sans SC', sans-serif);
  font-size: 1rem;
  line-height: 1.9;
  color: #6B5F45;
  max-width: 560px;
  margin: 0 auto;
}

/* 过渡 */
.intro-fade-leave-active {
  transition: opacity 0.3s ease;
}
.intro-fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .intro-ch-no {
    font-size: 2.2rem;
  }
  .intro-char {
    font-size: 2.2rem;
  }
  .intro-desc {
    font-size: 0.9rem;
  }
}
</style>
