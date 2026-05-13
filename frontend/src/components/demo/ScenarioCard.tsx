'use client'

import { ReactNode } from 'react'
import { 
  ChevronRight, 
  Play, 
  Pause, 
  RotateCcw,
  CheckCircle2,
  Loader2
} from 'lucide-react'

interface ScenarioCardProps {
  title: string
  description: string
  icon: ReactNode
  isActive: boolean
  isRunning: boolean
  onStart: () => void
  onStop: () => void
  onReset: () => void
  children?: ReactNode
}

export function ScenarioCard({
  title,
  description,
  icon,
  isActive,
  isRunning,
  onStart,
  onStop,
  onReset,
  children
}: ScenarioCardProps) {
  return (
    <div className={`
      bg-white dark:bg-slate-800 rounded-xl shadow-sm border transition-all duration-300
      ${isActive 
        ? 'border-blue-500 ring-2 ring-blue-500/20' 
        : 'border-slate-200 dark:border-slate-700 hover:border-blue-300'
      }
    `}>
      <div className="p-6 border-b border-slate-100 dark:border-slate-700">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className={`
              p-3 rounded-lg transition-colors
              ${isActive 
                ? 'bg-blue-100 dark:bg-blue-900/30' 
                : 'bg-slate-100 dark:bg-slate-700'
              }
            `}>
              {icon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                {title}
              </h3>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                {description}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {!isRunning ? (
              <button
                onClick={onStart}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
              >
                <Play className="w-4 h-4" />
                Запустить
              </button>
            ) : (
              <button
                onClick={onStop}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
              >
                <Pause className="w-4 h-4" />
                Стоп
              </button>
            )}
            
            <button
              onClick={onReset}
              className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              title="Сбросить"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      
      {children && (
        <div className="p-6 bg-slate-50 dark:bg-slate-900/50">
          {children}
        </div>
      )}
    </div>
  )
}

interface StepProps {
  number: number
  title: string
  status: 'pending' | 'running' | 'completed' | 'error'
  children?: ReactNode
}

export function ScenarioStep({ number, title, status, children }: StepProps) {
  const statusConfig = {
    pending: {
      icon: <span className="w-6 h-6 flex items-center justify-center bg-slate-200 dark:bg-slate-600 text-slate-500 dark:text-slate-400 text-sm font-medium rounded-full">{number}</span>,
      textColor: 'text-slate-500 dark:text-slate-400'
    },
    running: {
      icon: <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />,
      textColor: 'text-blue-600 dark:text-blue-400'
    },
    completed: {
      icon: <CheckCircle2 className="w-6 h-6 text-green-600" />,
      textColor: 'text-green-600 dark:text-green-400'
    },
    error: {
      icon: <span className="w-6 h-6 flex items-center justify-center bg-red-100 dark:bg-red-900/30 text-red-600 text-sm font-medium rounded-full">!</span>,
      textColor: 'text-red-600 dark:text-red-400'
    }
  }

  return (
    <div className="flex items-start gap-4">
      {statusConfig[status].icon}
      <div className="flex-1">
        <p className={`font-medium ${statusConfig[status].textColor}`}>
          {title}
        </p>
        {children && (
          <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {children}
          </div>
        )}
      </div>
    </div>
  )
}