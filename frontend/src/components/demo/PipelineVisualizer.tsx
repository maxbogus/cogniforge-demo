'use client'

import { useState, useEffect } from 'react'
import { 
  FileText, 
  Scissors, 
  Brain, 
  Database,
  Search,
  ArrowRight,
  CheckCircle2,
  Loader2
} from 'lucide-react'

interface PipelineStep {
  id: string
  title: string
  description: string
  icon: typeof FileText
  duration?: string
}

const PIPELINE_STEPS: PipelineStep[] = [
  { id: 'upload', title: 'Загрузка документа', description: 'PDF, DOCX, TXT → файл сохранён', icon: FileText },
  { id: 'extract', title: 'Извлечение текста', description: 'Текст извлечён из документа', icon: Scissors },
  { id: 'chunk', title: 'Разбиение на чанки', description: '512 токенов на чанк', icon: Scissors },
  { id: 'embed', title: 'Генерация эмбеддингов', description: 'all-MiniLM-L6-v2 (384 dim)', icon: Brain },
  { id: 'index', title: 'Индексация в FAISS', description: 'Векторный индекс обновлён', icon: Database },
  { id: 'search', title: 'Семантический поиск', description: 'cosine similarity ≥ 0.7', icon: Search },
]

interface PipelineVisualizerProps {
  isRunning: boolean
  onStepComplete?: (stepId: string) => void
}

export function PipelineVisualizer({ isRunning, onStepComplete }: PipelineVisualizerProps) {
  const [activeStep, setActiveStep] = useState<number>(-1)
  const [completedSteps, setCompletedSteps] = useState<string[]>([])

  useEffect(() => {
    if (isRunning && activeStep < PIPELINE_STEPS.length - 1) {
      const timer = setTimeout(() => {
        const nextStep = activeStep + 1
        setActiveStep(nextStep)
        onStepComplete?.(PIPELINE_STEPS[nextStep].id)
        setCompletedSteps(prev => [...prev, PIPELINE_STEPS[nextStep].id])
      }, 800)
      return () => clearTimeout(timer)
    }
    return () => {}
  }, [isRunning, activeStep, onStepComplete])

  useEffect(() => {
    if (!isRunning) {
      setActiveStep(-1)
      setCompletedSteps([])
    }
  }, [isRunning])

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">
        RAG Pipeline Visualization
      </h3>
      
      <div className="flex items-center gap-2 overflow-x-auto pb-4">
        {PIPELINE_STEPS.map((step, index) => {
          const isActive = index === activeStep
          const isCompleted = completedSteps.includes(step.id)
          
          return (
            <div key={step.id} className="flex items-center">
              <div className={`
                flex flex-col items-center p-4 rounded-lg min-w-[120px] transition-all duration-300
                ${isActive 
                  ? 'bg-blue-100 dark:bg-blue-900/30 ring-2 ring-blue-500' 
                  : isCompleted 
                    ? 'bg-green-100 dark:bg-green-900/30' 
                    : 'bg-slate-100 dark:bg-slate-700 opacity-50'
                }
              `}>
                <div className="mb-2">
                  {isActive ? (
                    <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                  ) : isCompleted ? (
                    <CheckCircle2 className="w-8 h-8 text-green-600" />
                  ) : (
                    <step.icon className="w-8 h-8 text-slate-400" />
                  )}
                </div>
                <p className={`
                  text-sm font-medium text-center
                  ${isActive 
                    ? 'text-blue-700 dark:text-blue-300' 
                    : isCompleted 
                      ? 'text-green-700 dark:text-green-300' 
                      : 'text-slate-500 dark:text-slate-400'
                  }
                `}>
                  {step.title}
                </p>
                {isActive && (
                  <p className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                    Обработка...
                  </p>
                )}
              </div>
              
              {index < PIPELINE_STEPS.length - 1 && (
                <div className="mx-2">
                  <ArrowRight className={`
                    w-5 h-5
                    ${isCompleted ? 'text-green-500' : 'text-slate-300 dark:text-slate-600'}
                  `} />
                </div>
              )}
            </div>
          )
        })}
      </div>
      
      {activeStep >= 0 && (
        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-900/50 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-300">
            <span className="font-medium">Текущий шаг:</span> {PIPELINE_STEPS[activeStep].description}
          </p>
          {PIPELINE_STEPS[activeStep].duration && (
            <p className="mt-1 text-xs text-slate-400">
              Время: {PIPELINE_STEPS[activeStep].duration}
            </p>
          )}
        </div>
      )}
    </div>
  )
}