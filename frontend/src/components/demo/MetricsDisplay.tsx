'use client'

interface MetricCardProps {
  label: string
  value: string
  description: string
  trend?: 'up' | 'down' | 'neutral'
  unit?: string
}

function MetricCard({ label, value, description, trend, unit }: MetricCardProps) {
  const trendColors = {
    up: 'text-green-600 dark:text-green-400',
    down: 'text-red-600 dark:text-red-400',
    neutral: 'text-slate-500 dark:text-slate-400'
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
      <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <div className="flex items-baseline gap-2 mt-1">
        <span className="text-2xl font-bold text-slate-900 dark:text-white">
          {value}
        </span>
        {unit && (
          <span className="text-sm text-slate-400">{unit}</span>
        )}
        {trend && (
          <span className={`text-xs ${trendColors[trend]}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
          </span>
        )}
      </div>
      <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
        {description}
      </p>
    </div>
  )
}

interface MetricsDisplayProps {
  customMetrics?: MetricCardProps[]
}

export function MetricsDisplay({ customMetrics }: MetricsDisplayProps) {
  const defaultMetrics: MetricCardProps[] = [
    {
      label: 'TTP',
      value: '~2',
      description: 'Время исправления через AI',
      unit: 'мин',
      trend: 'down'
    },
    {
      label: 'P2D',
      value: '~10',
      description: 'Время от пуша до деплоя',
      unit: 'мин',
      trend: 'down'
    },
    {
      label: 'MCC',
      value: '<5',
      description: 'Процент ручного кода',
      unit: '%',
      trend: 'down'
    },
    {
      label: 'NSM',
      value: '<100',
      description: 'Задержка RAG поиска',
      unit: 'мс',
      trend: 'neutral'
    },
    {
      label: 'AC',
      value: '1',
      description: 'Основной агент + Clinerules',
      unit: '',
      trend: 'neutral'
    }
  ]

  const metrics = customMetrics || defaultMetrics

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {metrics.map((metric) => (
        <MetricCard key={metric.label} {...metric} />
      ))}
    </div>
  )
}