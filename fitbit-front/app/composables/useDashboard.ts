import { createSharedComposable } from '@vueuse/core'

const _useDashboard = () => {
  const route = useRoute()
  const router = useRouter()
  const isNotificationsSlideoverOpen = ref(false)

  // Estado para período selecionado
  const selectedPeriod = ref<'7d' | '1m' | '3m' | '6m' | '1y'>('1m')

  // Estado para range de datas personalizado
  const customDateRange = ref<{ start: string; end: string } | null>(null)

  defineShortcuts({
    'g-h': () => router.push('/dashboard'),
    'g-p': () => router.push('/patients'),
    'n': () => isNotificationsSlideoverOpen.value = !isNotificationsSlideoverOpen.value
  })

  watch(() => route.fullPath, () => {
    isNotificationsSlideoverOpen.value = false
  })

  /**
   * Calcula o range de datas baseado no período selecionado
   */
  const getDateRangeForPeriod = (period: typeof selectedPeriod.value) => {
    const end = new Date()
    const start = new Date()

    switch (period) {
      case '7d':
        start.setDate(end.getDate() - 7)
        break
      case '1m':
        start.setMonth(end.getMonth() - 1)
        break
      case '3m':
        start.setMonth(end.getMonth() - 3)
        break
      case '6m':
        start.setMonth(end.getMonth() - 6)
        break
      case '1y':
        start.setFullYear(end.getFullYear() - 1)
        break
    }

    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    }
  }

  /**
   * Retorna o range de datas atual (customizado ou baseado no período)
   */
  const currentDateRange = computed(() => {
    return customDateRange.value || getDateRangeForPeriod(selectedPeriod.value)
  })

  return {
    isNotificationsSlideoverOpen,
    selectedPeriod,
    customDateRange,
    currentDateRange,
    getDateRangeForPeriod
  }
}

export const useDashboard = createSharedComposable(_useDashboard)
