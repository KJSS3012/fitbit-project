<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { Period, Range, Sale } from '~/types/dashboard'
import { randomInt, randomFrom } from '~/utils/dashboard'

const props = defineProps<{
  period: Period
  range: Range
}>()

const UBadge = resolveComponent('UBadge')

const sampleEmails = [
  'joao.silva@example.com',
  'maria.santos@example.com',
  'carlos.oliveira@example.com',
  'ana.costa@example.com',
  'pedro.souza@example.com'
]

const { data } = await useAsyncData('activities', async () => {
  const activities: Sale[] = []
  const currentDate = new Date()

  for (let i = 0; i < 5; i++) {
    const hoursAgo = randomInt(0, 48)
    const date = new Date(currentDate.getTime() - hoursAgo * 3600000)

    activities.push({
      id: (4600 - i).toString(),
      date: date.toISOString(),
      status: randomFrom(['paid', 'failed', 'refunded']),
      email: randomFrom(sampleEmails),
      amount: randomInt(5000, 15000)
    })
  }

  return activities.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}, {
  watch: [() => props.period, () => props.range],
  default: () => []
})

const columns: TableColumn<Sale>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ row }) => `#${row.getValue('id')}`
  },
  {
    accessorKey: 'date',
    header: 'Data',
    cell: ({ row }) => {
      return new Date(row.getValue('date')).toLocaleString('pt-BR', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })
    }
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const statusMap = {
        paid: { label: 'Ativo', color: 'success' as const },
        failed: { label: 'Inativo', color: 'error' as const },
        refunded: { label: 'Pendente', color: 'neutral' as const }
      }

      const status = statusMap[row.getValue('status') as keyof typeof statusMap]

      return h(UBadge, { class: 'capitalize', variant: 'subtle', color: status.color }, () =>
        status.label
      )
    }
  },
  {
    accessorKey: 'email',
    header: 'Paciente'
  },
  {
    accessorKey: 'amount',
    header: () => h('div', { class: 'text-right' }, 'Passos'),
    cell: ({ row }) => {
      const amount = Number.parseFloat(row.getValue('amount'))
      const formatted = new Intl.NumberFormat('pt-BR').format(amount)

      return h('div', { class: 'text-right font-medium' }, formatted)
    }
  }
]
</script>

<template>
  <UTable :data="data" :columns="columns" class="shrink-0" :ui="{
    base: 'table-fixed border-separate border-spacing-0',
    thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
    tbody: '[&>tr]:last:[&>td]:border-b-0',
    th: 'first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
    td: 'border-b border-default'
  }" />
</template>
