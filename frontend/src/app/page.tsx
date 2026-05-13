'use client'

import { useState, useCallback, useEffect } from 'react'
import { 
  FileText, 
  Activity, 
  CheckCircle2,
  XCircle,
  Upload,
  Loader2,
  Search
} from 'lucide-react'
import { getSystemInfo, getHealth, uploadDocument, searchDocuments } from '@/lib/api'
import { useDropzone } from 'react-dropzone'

interface SystemInfo {
  system: {
    name: string
    version: string
    environment: string
    debug: boolean
  }
  resources: {
    max_file_size: number
    supported_formats: string[]
    embedding_model: string
    vector_dimensions: number
    similarity_threshold: number
    document_count: number
  }
  services: {
    database: string
    cache: string
    vector_store: string
    document_processing: string
  }
}

interface HealthStatus {
  status: string
  timestamp: string
  version: string
  database: boolean
  cache: boolean
  services?: {
    database?: { status: string; message?: string }
    redis?: { status: string; message?: string }
  }
}

interface SearchResult {
  document_id: string
  filename: string
  similarity: number
  chunk_text: string
  page_number?: number
}

interface DescriptionRow {
  parameter: string
  value: string | number
  description: string
}

export default function DashboardPage() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Upload state
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    async function fetchData() {
      try {
        const [info, healthData] = await Promise.all([
          getSystemInfo(),
          getHealth()
        ])
        setSystemInfo(info)
        setHealth(healthData)
      } catch (err) {
        setError('Failed to load system data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    
    setUploading(true)
    setUploadError(null)
    setUploadSuccess(false)
    
    try {
      const file = acceptedFiles[0]
      await uploadDocument(file)
      setUploadSuccess(true)
      // Refresh data after upload
      const info = await getSystemInfo()
      setSystemInfo(info)
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Ошибка при загрузке')
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

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    setSearching(true)
    try {
      const results = await searchDocuments(searchQuery, 5)
      setSearchResults(results)
    } catch (err) {
      console.error('Search error:', err)
    } finally {
      setSearching(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
          <p className="mt-4 text-slate-500">Loading...</p>
        </div>
      </div>
    )
  }

  // Build description table data from API
  const descriptionRows: DescriptionRow[] = [
    { parameter: 'Documents', value: systemInfo?.resources.document_count ?? 0, description: 'Загружено документов' },
    { parameter: 'Embedding', value: systemInfo?.resources.embedding_model ?? 'all-MiniLM-L6-v2', description: 'Модель эмбеддингов' },
    { parameter: 'Vector Dim', value: systemInfo?.resources.vector_dimensions ?? 384, description: 'Размерность вектора' },
    { parameter: 'Similarity', value: systemInfo?.resources.similarity_threshold ?? 0.7, description: 'Порог похожести' },
    { parameter: 'PostgreSQL', value: health?.database ? 'Active' : 'Inactive', description: 'База данных' },
    { parameter: 'Redis', value: health?.cache ? 'Active' : 'Inactive', description: 'Кэш и сессии' },
    { parameter: 'FAISS', value: health?.status === 'healthy' ? 'Active' : 'Inactive', description: 'Векторное хранилище' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                🎓 CogniForge
              </h1>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                RAG Document Intelligence
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 rounded-full">
                <Activity className="w-4 h-4 text-green-600 dark:text-green-400" />
                <span className="text-sm font-medium text-green-700 dark:text-green-400">
                  {health?.status === 'healthy' ? 'Operational' : 'Issues'}
                </span>
              </div>
              <a 
                href="http://localhost:3000/api/docs"
                target="_blank"
                className="px-4 py-2 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                📖 API Docs
              </a>
              <a 
                href="/demo"
                className="px-4 py-2 text-sm text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                📋 Demo →
              </a>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            📤 Upload Document
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
                  ? 'Processing...' 
                  : isDragActive 
                    ? 'Drop file here' 
                    : 'Drag PDF or TXT file'
                }
              </p>
              <p className="mt-2 text-sm text-slate-400">
                or click to select
              </p>
            </div>

            {/* Status */}
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <h3 className="font-medium text-slate-900 dark:text-white mb-4">Upload Status</h3>
              
              {uploadSuccess && (
                <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                  <div>
                    <p className="font-medium text-green-700 dark:text-green-400">Document uploaded!</p>
                    <p className="text-sm text-green-600 dark:text-green-500">
                      Ready for semantic search
                    </p>
                  </div>
                </div>
              )}
              
              {uploadError && (
                <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <XCircle className="w-6 h-6 text-red-600" />
                  <div>
                    <p className="font-medium text-red-700 dark:text-red-400">Error</p>
                    <p className="text-sm text-red-600 dark:text-red-500">{uploadError}</p>
                  </div>
                </div>
              )}
              
              {!uploadSuccess && !uploadError && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 px-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                    <span className="text-sm text-slate-600 dark:text-slate-300">
                      Documents loaded
                    </span>
                    <span className="text-lg font-bold text-slate-900 dark:text-white">
                      {systemInfo?.resources.document_count ?? 0}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Upload document for indexing and content search
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Search Panel */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            🔍 Semantic Search
          </h2>
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
            <div className="flex gap-4 mb-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Enter search query..."
                className="flex-1 px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400"
              />
              <button
                onClick={handleSearch}
                disabled={searching}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
              >
                {searching ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                Search
              </button>
            </div>
            
            {searchResults.length > 0 && (
              <div className="space-y-4">
                <p className="text-sm text-slate-500">Found: {searchResults.length}</p>
                {searchResults.map((result, idx) => (
                  <div key={idx} className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        {result.filename}
                      </span>
                      <span className="text-sm text-blue-600 dark:text-blue-400">
                        {Math.round(result.similarity * 100)}% match
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3">
                      {result.chunk_text}
                    </p>
                  </div>
                ))}
              </div>
            )}
            
            {searchQuery && searchResults.length === 0 && !searching && (
              <p className="text-sm text-slate-500">Upload document and try search</p>
            )}
          </div>
        </section>

        {/* Description Table */}
        <section>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            📊 System Configuration
          </h2>
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-50 dark:bg-slate-700/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Parameter</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                {descriptionRows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-white">
                      {row.parameter}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 dark:text-blue-400 font-medium">
                      {row.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
                      {row.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  )
}