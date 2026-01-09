import { format as formatDate } from 'date-fns'
import jsPDF from 'jspdf'

export type ExportFormat = 'pdf' | 'csv' | 'json'

export interface ExportOptions {
  format: ExportFormat
  startDate: Date
  endDate: Date
  patientId: string
}

export const useExport = () => {
  const config = useRuntimeConfig()
  const toast = useToast()
  const { user } = useAuth()
  const { isSimulationMode, getStepsData, getHeartRateData, getSleepData, getCaloriesData } = useFitbitData()

  const isExporting = ref(false)

  const validatePeriod = (startDate: Date, endDate: Date): boolean => {
    if (startDate > endDate) {
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

  const generateFileName = (format: ExportFormat, patientId: string): string => {
    const timestamp = formatDate(new Date(), 'yyyy-MM-dd_HHmmss')
    return `fitbit_dados_${patientId}_${timestamp}.${format}`
  }

  const downloadFile = (blob: Blob, fileName: string) => {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const exportSimulatedData = async (format: ExportFormat, startDate: Date, endDate: Date, patientId: string) => {
    await new Promise(resolve => setTimeout(resolve, 1000))

    const stepsData = getStepsData(startDate, endDate, 'daily')
    const heartRateData = getHeartRateData(startDate, endDate, 'daily')
    const sleepData = getSleepData(startDate, endDate, 'daily')
    const caloriesData = getCaloriesData(startDate, endDate, 'daily')

    const exportData = {
      metadata: {
        generatedAt: new Date().toISOString(),
        patientId: patientId,
        patientName: user.value?.name || 'Paciente',
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString()
      },
      data: {
        steps: stepsData,
        heartRate: heartRateData,
        sleep: sleepData,
        calories: caloriesData
      }
    }

    if (format === 'json') {
      const jsonString = JSON.stringify(exportData, null, 2)
      const blob = new Blob([jsonString], { type: 'application/json' })
      const fileName = generateFileName('json', patientId)
      downloadFile(blob, fileName)
    } else if (format === 'csv') {
      let csvContent = 'Data,Passos,Frequência Cardíaca (BPM),Sono (min),Calorias\n'

      const allDates = new Set([
        ...stepsData.map(d => d.date),
        ...heartRateData.map(d => d.date),
        ...sleepData.map(d => d.date),
        ...caloriesData.map(d => d.date)
      ])

      Array.from(allDates).sort().forEach(date => {
        const steps = stepsData.find(d => d.date === date)?.value || 0
        const hr = heartRateData.find(d => d.date === date)?.value || 0
        const sleep = sleepData.find(d => d.date === date)?.value || 0
        const calories = caloriesData.find(d => d.date === date)?.value || 0

        csvContent += `${date},${steps},${hr},${sleep},${calories}\n`
      })

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const fileName = generateFileName('csv', patientId)
      downloadFile(blob, fileName)
    } else if (format === 'pdf') {
      const doc = new jsPDF()

      doc.setFontSize(18)
      doc.text('RELATÓRIO DE DADOS DE SAÚDE', 20, 20)

      doc.setFontSize(12)
      let yPos = 35
      doc.text(`Paciente: ${user.value?.name || 'Paciente'}`, 20, yPos)
      yPos += 7
      doc.text(`ID: ${patientId}`, 20, yPos)
      yPos += 7
      doc.text(`Período: ${startDate.toLocaleDateString('pt-BR')} - ${endDate.toLocaleDateString('pt-BR')}`, 20, yPos)
      yPos += 7
      doc.text(`Gerado em: ${new Date().toLocaleString('pt-BR')}`, 20, yPos)

      yPos += 15
      doc.setFontSize(14)
      doc.text('RESUMO DOS DADOS', 20, yPos)

      doc.setFontSize(11)
      yPos += 10
      doc.text(`Total de registros de passos: ${stepsData.length}`, 20, yPos)
      yPos += 6
      doc.text(`Total de registros de frequência cardíaca: ${heartRateData.length}`, 20, yPos)
      yPos += 6
      doc.text(`Total de registros de sono: ${sleepData.length}`, 20, yPos)
      yPos += 6
      doc.text(`Total de registros de calorias: ${caloriesData.length}`, 20, yPos)

      yPos += 15
      doc.setFontSize(14)
      doc.text('DETALHAMENTO', 20, yPos)

      doc.setFontSize(10)
      const allDates = new Set([...stepsData.map(d => d.date)])
      Array.from(allDates).sort().forEach(date => {
        const steps = stepsData.find(d => d.date === date)?.value || 0
        const hr = heartRateData.find(d => d.date === date)?.value || 0
        const sleep = sleepData.find(d => d.date === date)?.value || 0
        const calories = caloriesData.find(d => d.date === date)?.value || 0

        yPos += 10
        if (yPos > 270) {
          doc.addPage()
          yPos = 20
        }

        doc.text(`Data: ${date}`, 20, yPos)
        yPos += 5
        doc.text(`  Passos: ${steps} | FC: ${hr} bpm | Sono: ${sleep} min | Calorias: ${calories} kcal`, 20, yPos)
      })

      const pdfBlob = doc.output('blob')
      const fileName = generateFileName('pdf', patientId)
      downloadFile(pdfBlob, fileName)
    }

    toast.add({
      title: 'Exportação concluída',
      description: `Arquivo ${format.toUpperCase()} gerado com sucesso (modo simulação)`,
      color: 'success',
      icon: 'i-lucide-check-circle'
    })
  }

  const exportToPDF = async (startDate: Date, endDate: Date, patientId: string) => {
    if (isSimulationMode.value) {
      await exportSimulatedData('pdf', startDate, endDate, patientId)
      return
    }

    try {
      const response = await $fetch(`${config.public.apiBase}/export/pdf`, {
        method: 'GET',
        query: {
          patient_id: patientId,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        },
        responseType: 'blob'
      })

      const fileName = generateFileName('pdf', patientId)
      downloadFile(response as Blob, fileName)

      toast.add({
        title: 'Exportação concluída',
        description: 'Arquivo PDF gerado com sucesso',
        color: 'success',
        icon: 'i-lucide-check-circle'
      })
    } catch (error: any) {
      throw error
    }
  }

  const exportToCSV = async (startDate: Date, endDate: Date, patientId: string) => {
    if (isSimulationMode.value) {
      await exportSimulatedData('csv', startDate, endDate, patientId)
      return
    }

    try {
      const response = await $fetch(`${config.public.apiBase}/export/csv`, {
        method: 'GET',
        query: {
          patient_id: patientId,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        },
        responseType: 'blob'
      })

      const fileName = generateFileName('csv', patientId)
      downloadFile(response as Blob, fileName)

      toast.add({
        title: 'Exportação concluída',
        description: 'Arquivo CSV gerado com sucesso',
        color: 'success',
        icon: 'i-lucide-check-circle'
      })
    } catch (error: any) {
      throw error
    }
  }

  const exportToJSON = async (startDate: Date, endDate: Date, patientId: string) => {
    if (isSimulationMode.value) {
      await exportSimulatedData('json', startDate, endDate, patientId)
      return
    }

    try {
      const response = await $fetch(`${config.public.apiBase}/export/json`, {
        method: 'GET',
        query: {
          patient_id: patientId,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        }
      })

      const jsonString = JSON.stringify(response, null, 2)
      const blob = new Blob([jsonString], { type: 'application/json' })
      const fileName = generateFileName('json', patientId)
      downloadFile(blob, fileName)

      toast.add({
        title: 'Exportação concluída',
        description: 'Arquivo JSON gerado com sucesso',
        color: 'success',
        icon: 'i-lucide-check-circle'
      })
    } catch (error: any) {
      throw error
    }
  }

  const exportData = async (options: ExportOptions) => {
    if (!validatePeriod(options.startDate, options.endDate)) {
      return
    }

    isExporting.value = true

    try {
      switch (options.format) {
        case 'pdf':
          await exportToPDF(options.startDate, options.endDate, options.patientId)
          break
        case 'csv':
          await exportToCSV(options.startDate, options.endDate, options.patientId)
          break
        case 'json':
          await exportToJSON(options.startDate, options.endDate, options.patientId)
          break
      }
    } catch (error: any) {
      console.error('Export error:', error)

      if (error.status === 404 || error.statusCode === 404) {
        toast.add({
          title: 'Nenhum dado disponível',
          description: 'Nenhum dado disponível para o período selecionado',
          color: 'warning',
          icon: 'i-lucide-alert-triangle'
        })
      } else {
        toast.add({
          title: 'Erro na exportação',
          description: 'Não foi possível gerar o arquivo. Tente novamente mais tarde',
          color: 'error',
          icon: 'i-lucide-x-circle'
        })
      }
    } finally {
      isExporting.value = false
    }
  }

  return {
    isExporting,
    exportData,
    validatePeriod
  }
}
