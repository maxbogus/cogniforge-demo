'use client'

import { useState, useCallback, useEffect } from 'react'
import { 
  FileText, 
  Search, 
  Briefcase, 
  Users,
  Activity,
  Database,
  Cpu,
  TrendingUp,
  Loader2,
  Upload,
  CheckCircle2,
  XCircle
} from 'lucide-react'
import { 
  ScenarioCard, 
  ScenarioStep,
  PipelineVisualizer,
  MetricsDisplay,
  DemoSearchPanel
} from '@/components/demo'
import { searchDocuments, uploadDocument, getDocumentList } from '@/lib/api'
import { useDropzone } from 'react-dropzone'

// Demo scenarios configuration
const SCENARIOS = [
  {
    id: 'rag',
    title: 'RAG Pipeline',
    description: 'Полный цикл работы RAG-системы: загрузка → индексация → поиск',
    icon: <Database className="w-6 h-6 text-blue-600" />
  },
  {
    id: 'due-diligence',
    title: 'Due Diligence',
    description: 'Анализ M&A документов и поиск related content',
    icon: <Briefcase className="w-6 h-6 text-blue-600" />
  },
  {
    id: 'resume',
    title: 'Resume Screening',
    description: 'Сравнение резюме кандидатов с требованиями вакансии',
    icon: <Users className="w-6 h-6 text-blue-600" />
  },
  {
    id: 'monitoring',
    title: 'System Monitoring',
    description: 'Observability: health checks, metrics, status всех сервисов',
    icon: <Activity className="w-6 h-6 text-blue-600" />
  }
]

export default function DemoPage() {
  const [activeScenario, setActiveScenario] = useState<string | null>(null)
  const [runningScenario, setRunningScenario] = useState<string | null>(null)
  const [pipelineStep, setPipelineStep] = useState<string>('')
  const [demoResults, setDemoResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [documentCount, setDocumentCount] = useState(0)
  const [loadingDocs, setLoadingDocs] = useState(true)

  // Fetch document count on mount
  useEffect(() => {
    async function fetchDocCount() {
      try {
        const data = await getDocumentList(1, 0)
        setDocumentCount(data.total || 0)
      } catch (error) {
        console.error('Failed to fetch document count:', error)
      } finally {
        setLoadingDocs(false)
      }
    }
    fetchDocCount()
  }, [])

  const handleStart = async (scenarioId: string) => {
    setActiveScenario(scenarioId)
    setRunningScenario(scenarioId)
    setDemoResults([])
    
    if (scenarioId === 'rag') {
      const steps = ['upload', 'extract', 'chunk', 'embed', 'index', 'search']
      for (let i = 0; i < steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 800))
        setPipelineStep(steps[i])
      }
    } else {
      await new Promise(resolve => setTimeout(resolve, 1500))
      setPipelineStep('search')
    }
    
    setRunningScenario(null)
  }

  const handleStop = () => {
    setRunningScenario(null)
    setPipelineStep('')
  }

  const handleReset = () => {
    setActiveScenario(null)
    setRunningScenario(null)
    setPipelineStep('')
    setDemoResults([])
  }

  const handleSearch = async (query: string) => {
    setLoading(true)
    try {
      const results = await searchDocuments(query, 5)
      setDemoResults(results)
      return results
    } catch (error) {
      console.error('Search error:', error)
      return []
    } finally {
      setLoading(false)
    }
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    
    setUploading(true)
    setUploadError(null)
    setUploadSuccess(false)
    
    try {
      const file = acceptedFiles[0]
      const response = await uploadDocument(file)
      setUploadSuccess(true)
      setDocumentCount(prev => prev + 1)
      console.log('Upload success:', response)
    } catch (error: any) {
      setUploadError(error.response?.data?.detail || 'Ошибка при загрузке документа')
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                🎓 CogniForge Demo
              </h1>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                Демонстрационные сценарии для курса AI-Vibecoding
              </p>
            </div>
            <a 
              href="/"
              className="px-4 py-2 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              ← На главную
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            📤 Загрузить документ для поиска
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload Zone */}
            <div
              {...getRootProps()}
              className={`
                relative flex flex-col items-center justify-center p-8 
                border-2 border-dashed rounded-xl cursor-pointer transition-all duration-200
                ${isDragActive 
                  ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20' 
                  : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 hover:border-blue-400'
                }
              `}
            >
              <input {...getInputProps()} />
              
              {uploading ? (
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
              ) : isDragActive ? (
                <Upload className="w-12 h-12 text-blue-600" />
              ) : (
                <FileText className="w-12 h-12 text-slate-400" />
              )}
              
              <p className="mt-4 text-center text-slate-700 dark:text-slate-300">
                {uploading 
                  ? 'Загрузка и индексация...' 
                  : isDragActive 
                    ? 'Отпустите файл здесь' 
                    : 'Перетащите PDF или TXT файл'
                }
              </p>
              <p className="mt-2 text-sm text-slate-400">
                или нажмите для выбора
              </p>
            </div>

            {/* Status */}
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <h3 className="font-medium text-slate-900 dark:text-white mb-4">Статус загрузки</h3>
              
              {uploadSuccess && (
                <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                  <div>
                    <p className="font-medium text-green-700 dark:text-green-400">Документ загружен!</p>
                    <p className="text-sm text-green-600 dark:text-green-500">
                      Теперь можно искать по содержимому
                    </p>
                  </div>
                </div>
              )}
              
              {uploadError && (
                <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <XCircle className="w-6 h-6 text-red-600" />
                  <div>
                    <p className="font-medium text-red-700 dark:text-red-400">Ошибка</p>
                    <p className="text-sm text-red-600 dark:text-red-500">{uploadError}</p>
                  </div>
                </div>
              )}
              
              {!uploadSuccess && !uploadError && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 px-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                    <span className="text-sm text-slate-600 dark:text-slate-300">
                      Загружено документов
                    </span>
                    <span className="text-lg font-bold text-slate-900 dark:text-white">
                      {documentCount}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Загрузите документ для индексации и поиска по содержимому
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* VCVI Metrics */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            📊 VCVI Метрики CogniForge
          </h2>
          <MetricsDisplay />
        </section>

        {/* Scenario Cards */}
        <section className="mb-8 space-y-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            📋 Доступные сценарии
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* RAG Pipeline */}
            <ScenarioCard
              title="RAG Pipeline"
              description="Полный цикл работы RAG-системы"
              icon={<Database className="w-6 h-6 text-blue-600" />}
              isActive={activeScenario === 'rag'}
              isRunning={runningScenario === 'rag'}
              onStart={() => handleStart('rag')}
              onStop={handleStop}
              onReset={handleReset}
            >
              <div className="space-y-4">
                {runningScenario === 'rag' && <PipelineVisualizer isRunning={true} />}
                {!runningScenario && activeScenario === 'rag' && (
                  <>
                    <div className="space-y-3">
                      <ScenarioStep number={1} title="Загрузка документа" status="completed" />
                      <ScenarioStep number={2} title="Извлечение текста" status="completed" />
                      <ScenarioStep number={3} title="Chunking (512 tokens)" status="completed" />
                      <ScenarioStep number={4} title="Embeddings (all-MiniLM-L6-v2)" status="completed" />
                      <ScenarioStep number={5} title="FAISS Index" status="completed" />
                    </div>
                    <div className="border-t border-slate-200 dark:border-slate-700 pt-4">
                      <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                        Попробуйте семантический поиск:
                      </p>
                      <DemoSearchPanel 
                        onSearch={handleSearch}
                        placeholder="Введите запрос..."
                      />
                    </div>
                  </>
                )}
                {runningScenario !== 'rag' && activeScenario !== 'rag' && (
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Нажмите "Запустить" для демонстрации RAG pipeline
                  </p>
                )}
              </div>
            </ScenarioCard>

            {/* Due Diligence */}
            <ScenarioCard
              title="Due Diligence Analyzer"
              description="Анализ M&A документов"
              icon={<Briefcase className="w-6 h-6 text-blue-600" />}
              isActive={activeScenario === 'due-diligence'}
              isRunning={runningScenario === 'due-diligence'}
              onStart={() => handleStart('due-diligence')}
              onStop={handleStop}
              onReset={handleReset}
            >
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {['Contracts', 'Reports', 'Financials', 'Legal'].map(tag => (
                    <span key={tag} className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="space-y-3">
                  <ScenarioStep number={1} title="Загрузка документов" status={activeScenario === 'due-diligence' ? 'completed' : 'pending'} />
                  <ScenarioStep number={2} title="Cross-document similarity" status={activeScenario === 'due-diligence' ? 'completed' : 'pending'} />
                  <ScenarioStep number={3} title="Structured extraction" status={activeScenario === 'due-diligence' ? 'completed' : 'pending'} />
                </div>
                {activeScenario === 'due-diligence' && (
                  <div className="border-t border-slate-200 dark:border-slate-700 pt-4">
                    <DemoSearchPanel 
                      onSearch={handleSearch}
                      placeholder="Поиск по ключевым словам..."
                    />
                  </div>
                )}
              </div>
            </ScenarioCard>

            {/* Resume Screening */}
            <ScenarioCard
              title="Resume Screening"
              description="Сравнение кандидатов с вакансией"
              icon={<Users className="w-6 h-6 text-blue-600" />}
              isActive={activeScenario === 'resume'}
              isRunning={runningScenario === 'resume'}
              onStart={() => handleStart('resume')}
              onStop={handleStop}
              onReset={handleReset}
            >
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-1 p-4 bg-slate-100 dark:bg-slate-700 rounded-lg">
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Вакансия</p>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      Python Developer, ML
                    </p>
                    <p className="text-xs text-slate-400 mt-1">5+ лет опыта</p>
                  </div>
                  <div className="flex-1 p-4 bg-slate-100 dark:bg-slate-700 rounded-lg">
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Резюме</p>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      Match Score: 85%
                    </p>
                    <p className="text-xs text-green-600 mt-1">Рекомендован</p>
                  </div>
                </div>
                {activeScenario === 'resume' && (
                  <DemoSearchPanel 
                    onSearch={handleSearch}
                    placeholder="Навыки, опыт, технологии..."
                  />
                )}
              </div>
            </ScenarioCard>

            {/* System Monitoring */}
            <ScenarioCard
              title="System Monitoring"
              description="Observability и health checks"
              icon={<Activity className="w-6 h-6 text-blue-600" />}
              isActive={activeScenario === 'monitoring'}
              isRunning={runningScenario === 'monitoring'}
              onStart={() => handleStart('monitoring')}
              onStop={handleStop}
              onReset={handleReset}
            >
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-sm font-medium text-green-700 dark:text-green-400">PostgreSQL</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-sm font-medium text-green-700 dark:text-green-400">Redis</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-sm font-medium text-green-700 dark:text-green-400">FAISS</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-sm font-medium text-green-700 dark:text-green-400">API</span>
                  </div>
                </div>
                <div className="p-4 bg-slate-100 dark:bg-slate-700 rounded-lg">
                  <p className="text-sm text-slate-500 dark:text-slate-400">Embedding Model</p>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">all-MiniLM-L6-v2 (384 dim)</p>
                </div>
              </div>
            </ScenarioCard>
          </div>
        </section>

        {/* Architecture Diagram */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            🏗️ Архитектура системы
          </h2>
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
            <div className="flex flex-col items-center gap-4">
              {/* Nginx */}
              <div className="flex items-center gap-2 px-6 py-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg border-2 border-purple-300">
                <Database className="w-5 h-5 text-purple-600" />
                <span className="font-medium text-purple-700 dark:text-purple-300">Nginx (port 3000)</span>
              </div>
              <div className="text-slate-400">↓</div>
              {/* Frontend + Backend */}
              <div className="flex gap-4">
                <div className="flex items-center gap-2 px-6 py-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg border-2 border-blue-300">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-blue-700 dark:text-blue-300">Frontend</span>
                </div>
                <div className="flex items-center gap-2 px-6 py-3 bg-green-100 dark:bg-green-900/30 rounded-lg border-2 border-green-300">
                  <Cpu className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-700 dark:text-green-300">Backend</span>
                </div>
              </div>
              {/* Services */}
              <div className="flex flex-wrap justify-center gap-3">
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">PostgreSQL</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Redis</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">FAISS</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Key Takeaways */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            🎓 Ключевые выводы для студентов
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900 dark:text-white">RAG ≠ просто embeddings</h3>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Важна chunking strategy, hybrid search
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Activity className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900 dark:text-white">Observability с первого дня</h3>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Health checks, metrics
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Database className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900 dark:text-white">Docker Compose упрощает деплой</h3>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Single-port architecture
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900 dark:text-white">VCVI считается просто</h3>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    Метрики важнее слов
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}