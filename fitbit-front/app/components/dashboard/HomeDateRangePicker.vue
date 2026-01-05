<script setup lang="ts">
import { DateFormatter, getLocalTimeZone, CalendarDate, today } from '@internationalized/date'
import type { Range } from '~/types/dashboard'

const df = new DateFormatter('pt-BR', {
  dateStyle: 'medium'
})

const toast = useToast()
const selected = defineModel<Range>({ required: true })

const ranges = [
  { label: 'Hoje', type: 'today' },
  { label: 'Esta semana', type: 'week' },
  { label: 'Este mês', type: 'month' },
  { label: 'Últimos 7 dias', days: 7 },
  { label: 'Últimos 14 dias', days: 14 },
  { label: 'Últimos 30 dias', days: 30 },
  { label: 'Últimos 3 meses', months: 3 },
  { label: 'Últimos 6 meses', months: 6 },
  { label: 'Último ano', years: 1 }
]

const toCalendarDate = (date: Date) => {
  return new CalendarDate(
    date.getFullYear(),
    date.getMonth() + 1,
    date.getDate()
  )
}

/**
 * Valida se o range selecionado é válido
 */
const validateRange = (start: Date | null, end: Date | null): boolean => {
  // Teste 04: Validação de campos obrigatórios
  if (!start || !end) {
    toast.add({
      title: 'Período inválido',
      description: 'Selecione uma data inicial e final',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
    return false
  }

  // Teste 03: Validação de data inicial maior que data final
  if (start > end) {
    toast.add({
      title: 'Período inválido',
      description: 'A data inicial não pode ser maior que a data final',
      color: 'error',
      icon: 'i-lucide-alert-circle'
    })
    return false
  }

  return true
}

const calendarRange = computed({
  get: () => ({
    start: selected.value.start ? toCalendarDate(selected.value.start) : undefined,
    end: selected.value.end ? toCalendarDate(selected.value.end) : undefined
  }),
  set: (newValue: { start: CalendarDate | null, end: CalendarDate | null }) => {
    const startDate = newValue.start ? newValue.start.toDate(getLocalTimeZone()) : null
    const endDate = newValue.end ? newValue.end.toDate(getLocalTimeZone()) : null

    // Valida o range antes de aplicar
    if (validateRange(startDate, endDate)) {
      selected.value = {
        start: startDate!,
        end: endDate!
      }
    }
  }
})

const isRangeSelected = (range: { type?: string, days?: number, months?: number, years?: number }) => {
  if (!selected.value.start || !selected.value.end) return false

  const currentDate = today(getLocalTimeZone())
  let startDate = currentDate.copy()
  let endDate = currentDate.copy()

  // Teste 01: Filtro por dia, semana e mês atual
  if (range.type === 'today') {
    // Mesmo dia
    startDate = currentDate
    endDate = currentDate
  } else if (range.type === 'week') {
    // Início da semana (domingo) até hoje
    startDate = currentDate.subtract({ days: currentDate.day })
    endDate = currentDate
  } else if (range.type === 'month') {
    // Início do mês até hoje
    startDate = currentDate.set({ day: 1 })
    endDate = currentDate
  } else if (range.days) {
    startDate = startDate.subtract({ days: range.days })
  } else if (range.months) {
    startDate = startDate.subtract({ months: range.months })
  } else if (range.years) {
    startDate = startDate.subtract({ years: range.years })
  }

  const selectedStart = toCalendarDate(selected.value.start)
  const selectedEnd = toCalendarDate(selected.value.end)

  return selectedStart.compare(startDate) === 0 && selectedEnd.compare(endDate) === 0
}

const selectRange = (range: { type?: string, days?: number, months?: number, years?: number }) => {
  const currentDate = today(getLocalTimeZone())
  let startDate = currentDate.copy()
  let endDate = currentDate.copy()

  // Teste 01: Filtro por dia, semana e mês atual
  if (range.type === 'today') {
    startDate = currentDate
    endDate = currentDate
  } else if (range.type === 'week') {
    startDate = currentDate.subtract({ days: currentDate.day })
    endDate = currentDate
  } else if (range.type === 'month') {
    startDate = currentDate.set({ day: 1 })
    endDate = currentDate
  } else if (range.days) {
    startDate = startDate.subtract({ days: range.days })
  } else if (range.months) {
    startDate = startDate.subtract({ months: range.months })
  } else if (range.years) {
    startDate = startDate.subtract({ years: range.years })
  }

  selected.value = {
    start: startDate.toDate(getLocalTimeZone()),
    end: endDate.toDate(getLocalTimeZone())
  }
}
</script>

<template>
  <UPopover :content="{ align: 'start' }" :modal="true">
    <UButton color="neutral" variant="ghost" icon="i-lucide-calendar" class="data-[state=open]:bg-elevated group">
      <span class="truncate">
        <template v-if="selected.start">
          <template v-if="selected.end">
            {{ df.format(selected.start) }} - {{ df.format(selected.end) }}
          </template>
          <template v-else>
            {{ df.format(selected.start) }}
          </template>
        </template>
        <template v-else>
          Selecione uma data
        </template>
      </span>

      <template #trailing>
        <UIcon name="i-lucide-chevron-down"
          class="shrink-0 text-dimmed size-5 group-data-[state=open]:rotate-180 transition-transform duration-200" />
      </template>
    </UButton>

    <template #content>
      <div class="flex items-stretch sm:divide-x divide-default">
        <div class="hidden sm:flex flex-col justify-center">
          <UButton v-for="(range, index) in ranges" :key="index" :label="range.label" color="neutral" variant="ghost"
            class="rounded-none px-4" :class="[isRangeSelected(range) ? 'bg-elevated' : 'hover:bg-elevated/50']"
            truncate @click="selectRange(range)" />
        </div>

        <UCalendar v-model="calendarRange" class="p-2" :number-of-months="2" range />
      </div>
    </template>
  </UPopover>
</template>
