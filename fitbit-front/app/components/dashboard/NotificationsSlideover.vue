<script setup lang="ts">
import { formatTimeAgo } from '@vueuse/core'
import type { Notification } from '~/types/dashboard'
import { useDashboard } from '~/composables/useDashboard'

const { isNotificationsSlideoverOpen } = useDashboard()

// Mock notifications - você pode substituir por uma chamada real à API
const notifications = ref<Notification[]>([
  {
    id: 1,
    unread: true,
    sender: {
      id: 1,
      name: 'João Silva',
      email: 'joao@example.com',
      avatar: {
        src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=joao',
        alt: 'João Silva'
      },
      status: 'subscribed',
      location: 'São Paulo, SP'
    },
    body: 'Atingiu a meta de 10.000 passos hoje!',
    date: new Date(Date.now() - 1000 * 60 * 30).toISOString()
  },
  {
    id: 2,
    unread: true,
    sender: {
      id: 2,
      name: 'Maria Santos',
      email: 'maria@example.com',
      avatar: {
        src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=maria',
        alt: 'Maria Santos'
      },
      status: 'subscribed',
      location: 'Rio de Janeiro, RJ'
    },
    body: 'Frequência cardíaca elevada detectada',
    date: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
  },
  {
    id: 3,
    sender: {
      id: 3,
      name: 'Carlos Oliveira',
      email: 'carlos@example.com',
      avatar: {
        src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=carlos',
        alt: 'Carlos Oliveira'
      },
      status: 'subscribed',
      location: 'Belo Horizonte, MG'
    },
    body: 'Completou 7 dias consecutivos de exercícios',
    date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString()
  }
])
</script>

<template>
  <USlideover v-model:open="isNotificationsSlideoverOpen" title="Notificações">
    <template #body>
      <NuxtLink v-for="notification in notifications" :key="notification.id"
        :to="`/dashboard/patients?id=${notification.id}`"
        class="px-3 py-2.5 rounded-md hover:bg-elevated/50 flex items-center gap-3 relative -mx-3 first:-mt-3 last:-mb-3">
        <UChip color="error" :show="!!notification.unread" inset>
          <UAvatar v-bind="notification.sender.avatar" :alt="notification.sender.name" size="md" />
        </UChip>

        <div class="text-sm flex-1">
          <p class="flex items-center justify-between">
            <span class="text-highlighted font-medium">{{ notification.sender.name }}</span>

            <time :datetime="notification.date" class="text-muted text-xs"
              v-text="formatTimeAgo(new Date(notification.date))" />
          </p>

          <p class="text-dimmed">
            {{ notification.body }}
          </p>
        </div>
      </NuxtLink>
    </template>
  </USlideover>
</template>
