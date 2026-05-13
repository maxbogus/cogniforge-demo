'use client'

import { useState, useEffect } from 'react'
import { Search, FileText, Database, Loader2, Eye, X, ChevronDown, ChevronUp } from 'lucide-react'

interface SearchResult {
  document_id: string
  filename: string
  similarity: number
  chunk_text: string
  page_number?: number
}

interface DocumentDetail {
  document_id: string
  filename: string
  extracted_text: string
  chunks: { chunk_id: string; chunk_index: number; text: string; page_number?: number }[]
  created_at: string
  processed_at?: string
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
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null)
  const [documentLoading, setDocumentLoading] = useState(false)
  const [documentError, setDocumentError] = useState<string | null>(null)
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set())

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

  const fetchDocumentDetails = async (documentId: string) => {
    setDocumentLoading(true)
    setDocumentError(null)
    try {
      const response = await fetch(`/api/documents/${documentId}`)
      if (!response.ok) throw new Error('Failed to fetch document')
      const data = await response.json()
      setSelectedDocument(data)
    } catch (err) {
      setDocumentError('Ошибка при загрузке документа')
      console.error(err)
    } finally {
      setDocumentLoading(false)
    }
  }

  const handleViewDocument = (result: SearchResult) => {
    fetchDocumentDetails(result.document_id)
  }

  const closeDocumentViewer = () => {
    setSelectedDocument(null)
    setExpandedChunks(new Set())
  }

  const toggleChunk = (chunkId: string) => {
    setExpandedChunks(prev => {
      const newSet = new Set(prev)
      if (newSet.has(chunkId)) {
        newSet.delete(chunkId)
      } else {
        newSet.add(chunkId)
      }
      return newSet
    })
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
                  <button
                    onClick={() => handleViewDocument(result)}
                    className="p-1.5 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
                    title="Просмотр документа"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
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

      {/* Document Viewer Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  {selectedDocument.filename}
                </h2>
              </div>
              <button
                onClick={closeDocumentViewer}
                className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              >
                <X className="w-5 h-5 text-slate-500" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-4">
              {documentLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
              ) : documentError ? (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400">
                  {documentError}
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Document Info */}
                  <div className="flex gap-4 text-sm text-slate-500 dark:text-slate-400">
                    <span>Chunks: {selectedDocument.chunks?.length || 0}</span>
                    {selectedDocument.created_at && (
                      <span>Создан: {new Date(selectedDocument.created_at).toLocaleDateString('ru-RU')}</span>
                    )}
                  </div>

                  {/* Extracted Text */}
                  {selectedDocument.extracted_text && (
                    <div>
                      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Извлеченный текст
                      </h3>
                      <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg text-sm text-slate-600 dark:text-slate-300 max-h-64 overflow-y-auto">
                        {selectedDocument.extracted_text}
                      </div>
                    </div>
                  )}

                  {/* Chunks List */}
                  {selectedDocument.chunks && selectedDocument.chunks.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Фрагменты документа ({selectedDocument.chunks.length})
                      </h3>
                      <div className="space-y-2">
                        {selectedDocument.chunks.map((chunk) => (
                          <div
                            key={chunk.chunk_id}
                            className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden"
                          >
                            <button
                              onClick={() => toggleChunk(chunk.chunk_id)}
                              className="w-full flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                            >
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
                                  #{chunk.chunk_index + 1}
                                </span>
                                {chunk.page_number && (
                                  <span className="text-xs text-slate-400">
                                    стр. {chunk.page_number}
                                  </span>
                                )}
                              </div>
                              {expandedChunks.has(chunk.chunk_id) ? (
                                <ChevronUp className="w-4 h-4 text-slate-400" />
                              ) : (
                                <ChevronDown className="w-4 h-4 text-slate-400" />
                              )}
                            </button>
                            {expandedChunks.has(chunk.chunk_id) && (
                              <div className="p-3 text-sm text-slate-600 dark:text-slate-300 border-t border-slate-200 dark:border-slate-700">
                                {chunk.text}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
