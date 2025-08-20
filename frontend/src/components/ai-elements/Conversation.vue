<template>
  <div ref="scrollContainer" class="relative flex-1 overflow-y-auto" :class="className">
    <slot></slot>
    <button
      v-if="!isAtBottom"
      class="absolute bottom-4 left-[50%] translate-x-[-50%] rounded-full"
      @click="scrollToBottom"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="size-4"
      >
        <path d="M12 5v14" />
        <path d="m19 12-7 7-7-7" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  className: String,
})

const scrollContainer = ref<HTMLElement | null>(null)
const isAtBottom = ref(true)

const handleScroll = () => {
  if (scrollContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = scrollContainer.value
    isAtBottom.value = scrollTop + clientHeight >= scrollHeight - 10 // Add a small tolerance
  }
}

const scrollToBottom = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}

onMounted(() => {
  if (scrollContainer.value) {
    scrollContainer.value.addEventListener('scroll', handleScroll)
    scrollToBottom()
  }
  const observer = new MutationObserver(() => {
    if (isAtBottom.value) {
      nextTick(() => {
        scrollToBottom()
      })
    }
  })
  if (scrollContainer.value) {
    observer.observe(scrollContainer.value, {
      childList: true,
      subtree: true,
    })
  }
  onUnmounted(() => {
    if (scrollContainer.value) {
      scrollContainer.value.removeEventListener('scroll', handleScroll)
    }
    observer.disconnect()
  })
})
</script>
