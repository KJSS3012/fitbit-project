<script setup lang="ts">
interface Props {
  title: string
  value: string | number
  subtitle?: string
  icon: string
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info'
  trend?: {
    value: number
    label: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary'
})

const colorClasses = {
  primary: 'text-primary-500 bg-primary-50 dark:bg-primary-950',
  success: 'text-success-500 bg-success-50 dark:bg-success-950',
  warning: 'text-warning-500 bg-warning-50 dark:bg-warning-950',
  error: 'text-error-500 bg-error-50 dark:bg-error-950',
  info: 'text-info-500 bg-info-50 dark:bg-info-950'
}
</script>

<template>
  <UCard>
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <p class="text-sm text-muted mb-1">{{ title }}</p>
        <div class="flex items-baseline gap-2">
          <h3 class="text-2xl font-bold">{{ value }}</h3>
          <span v-if="subtitle" class="text-sm text-dimmed">{{ subtitle }}</span>
        </div>

        <div v-if="trend" class="flex items-center gap-1 mt-2">
          <UIcon :name="trend.value >= 0 ? 'i-lucide-trending-up' : 'i-lucide-trending-down'"
            :class="trend.value >= 0 ? 'text-success-500' : 'text-error-500'" class="size-4" />
          <span class="text-xs" :class="trend.value >= 0 ? 'text-success-500' : 'text-error-500'">
            {{ Math.abs(trend.value) }}%
          </span>
          <span class="text-xs text-dimmed">{{ trend.label }}</span>
        </div>
      </div>

      <div :class="colorClasses[color]" class="p-3 rounded-lg">
        <UIcon :name="icon" class="size-6" />
      </div>
    </div>
  </UCard>
</template>
