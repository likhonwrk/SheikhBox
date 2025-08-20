<script setup lang="ts">
import { ref } from 'vue'
import { Conversation } from '@/components/ai-elements/conversation'
import { Message } from '@/components/ai-elements/message'
import { PromptInput } from '@/components/ai-elements/prompt-input'

const messages = ref([
  {
    id: '1',
    author: 'user',
    content: 'Hello!',
  },
  {
    id: '2',
    author: 'assistant',
    content: 'Hi! How can I help you today?',
  },
])

const onNewMessage = (message: string) => {
  messages.value.push({
    id: String(messages.value.length + 1),
    author: 'user',
    content: message,
  })
}
</script>

<template>
  <div class="flex flex-col h-screen">
    <div class="flex-1 overflow-y-auto">
      <Conversation>
        <Message
          v-for="message in messages"
          :key="message.id"
          :author="message.author"
        >
          {{ message.content }}
        </Message>
      </Conversation>
    </div>
    <div class="p-4">
      <PromptInput @submit="onNewMessage" />
    </div>
  </div>
</template>
