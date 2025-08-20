<script setup lang="ts">
import { ref } from 'vue'
import Conversation from '@/components/ai-elements/conversation'
import Message from '@/components/ai-elements/message'
import PromptInput from '@/components/ai-elements/prompt-input'

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

const onNewMessage = async (message: string) => {
  messages.value.push({
    id: String(messages.value.length + 1),
    author: 'user',
    content: message,
  })

  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
    }),
  })

  const data = await response.json()

  messages.value.push({
    id: String(messages.value.length + 1),
    author: 'assistant',
    content: data.message,
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
