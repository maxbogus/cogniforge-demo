'use client'

import { useState } from 'react'
import { Search, FileText, Database, Loader2 } from 'lucide-react'

interface SearchResult {
  document_id: string
  filename: string
  similarity: number
  chunk_text: string
  page_number?: number
}

interface DemoSearchPanelProps {
  onSearch: (query: string) => Promise<SearchResult[]>
  placeholder?: string
}

export function DemoSearchPanel({ 
  onSearch, 
  placeholder = "Введите запрос для семантического поиска..." 
}: DemoSearchPanelProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const searchResults = await onSearch(query)
      setResults(searchResults)
    } catch (err) {
      setError('Ошибка при поиске. Попробуйте снова.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 dark:text-white placeholder-slate-400"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-600 text-white font-medium rounded-lg transition-colors disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Поиск'}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Найдено результатов: {results.length}
          </p>
          
          {results.map((result, index) => (
            <div 
              key={`${result.document_id}-${index}`}
              className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium text-slate-900 dark:text-white">
                    {result.filename}
                  </span>
                  {result.page_number && (
                    <span className="text-xs text-slate-400">
                      стр. {result.page_number}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`
                    px-2 py-1 text-xs font-medium rounded-full
                    ${result.similarity >= 0.8 
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                      : result.similarity >= 0.7 
                        ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' 
                        : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                    }
                  `}>
                    {result.similarity.toFixed(2)}
                  </span>
                  <Database className="w-4 h-4 text-slate-400" />
                </div>
              </div>
              
              <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-3">
                {result.chunk_text}
              </p>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && !loading && query && (
        <div className="text-center py-8 text-slate-500 dark:text-slate-400">
          <Search className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>Ничего не найдено. Попробуйте изменить запрос.</p>
        </div>
      )}
    </div>
  )
}