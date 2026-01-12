import { createSharedComposable, useDebounceFn } from '@vueuse/core'

type FilterPeriod = 'day' | 'week' | 'month' | 'custom'

interface DateRange {
  start: string
  end: string
}

const _useDashboard = () => {
  const route = useRoute()
  const router = useRouter()
  const toast = useToast()
  const isNotificationsSlideoverOpen = ref(false)

  const selectedPeriod = useState<FilterPeriod>('dashboardFilterPeriod', () => 'week')
  const customDateRange = useState<DateRange | null>('dashboardCustomRange', () => null)
  const isLoadingData = ref(false)

  defineShortcuts({
    'g-h': () => router.push('/dashboard'),
    'g-p': () => router.push('/patients'),
    'n': () => isNotificationsSlideoverOpen.value = !isNotificationsSlideoverOpen.value
  })

  watch(() => route.fullPath, () => {
    isNotificationsSlideoverOpen.value = false
  })

  /**
   * Calculates date range based on selected period
   */
  const getDateRangeForPeriod = (period: FilterPeriod): DateRange => {
    const end = new Date()
    const start = new Date()

    switch (period) {
      case 'day':
        break
      case 'week':
        start.setDate(end.getDate() - 7)
        break
      case 'month':
        start.setMonth(end.getMonth() - 1)
        break
      case 'custom':
        return customDateRange.value || { start: '', end: '' }
    }

    return {
      start: start.toISOString().split('T')[0]!,
      end: end.toISOString().split('T')[0]!
    }
  }

  /**
   * Validates custom date range
   */
  const validateCustomRange = (startDate: string, endDate: string): boolean => {
    if (!startDate || !endDate) {
      toast.add({
        title: 'Período inválido',
        description: 'Data inicial e final são obrigatórias para o período customizado.',
        color: 'error',
        icon: 'i-lucide-alert-circle'
      })
      return false
    }

    const start = new Date(startDate)
    const end = new Date(endDate)
    const today = new Date()
    today.setHours(23, 59, 59, 999) // Set to end of today

    if (start > end) {
      toast.add({
        title: 'Período inválido',
        description: 'Período inválido. Verifique as datas informadas.',
        color: 'error',
        icon: 'i-lucide-alert-circle'
      })
      return false
    }

    if (end > today) {
      toast.add({
        title: 'Data inválida',
        description: 'A data final não pode ser posterior à data de hoje.',
        color: 'error',
        icon: 'i-lucide-alert-circle'
      })
      return false
    }

    const diffTime = Math.abs(end.getTime() - start.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays > 365) {
      toast.add({
        title: 'Período muito longo',
        description: 'O período customizado não pode exceder 365 dias.',
        color: 'error',
        icon: 'i-lucide-alert-circle'
      })
      return false
    }

    return true
  }

  /**
   * Sets custom date range with validation
   */
  const setCustomDateRange = (startDate: string, endDate: string): boolean => {
    if (!validateCustomRange(startDate, endDate)) {
      return false
    }

    customDateRange.value = { start: startDate, end: endDate }
    selectedPeriod.value = 'custom'
    return true
  }

  /**
   * Returns current active date range
   */
  const currentDateRange = computed<DateRange>(() => {
    if (selectedPeriod.value === 'custom' && customDateRange.value) {
      return customDateRange.value
    }
    return getDateRangeForPeriod(selectedPeriod.value)
  })

  /**
   * Changes filter period with debounce optimization
   */
  const changePeriod = useDebounceFn((period: FilterPeriod) => {
    if (period === 'custom' && !customDateRange.value) {
      return
    }
    selectedPeriod.value = period
    isLoadingData.value = true

    setTimeout(() => {
      isLoadingData.value = false
    }, 300)
  }, 150)

  return {
    isNotificationsSlideoverOpen,
    selectedPeriod,
    customDateRange,
    currentDateRange,
    isLoadingData,
    getDateRangeForPeriod,
    validateCustomRange,
    setCustomDateRange,
    changePeriod
  }
}

export const useDashboard = createSharedComposable(_useDashboard)
