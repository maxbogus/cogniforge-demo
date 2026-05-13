'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Search, X, Filter, SlidersHorizontal } from 'lucide-react';

interface SearchBarProps {
  onSearch?: (query: string) => void;
  onFilter?: (filters: SearchFilters) => void;
  placeholder?: string;
  className?: string;
  debounceMs?: number;
  showFilters?: boolean;
}

export interface SearchFilters {
  type?: string;
  status?: string;
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
}

const defaultFilters: SearchFilters = {
  type: undefined,
  status: undefined,
  dateFrom: undefined,
  dateTo: undefined,
  tags: [],
};

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  onFilter,
  placeholder = 'Поиск документов...',
  className = '',
  debounceMs = 300,
  showFilters = true,
}) => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>(defaultFilters);
  const [showFilterPanel, setShowFilterPanel] = useState(false);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch?.(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs, onSearch]);

  const handleClear = useCallback(() => {
    setQuery('');
    onSearch?.('');
  }, [onSearch]);

  const handleFilterChange = useCallback(
    (key: keyof SearchFilters, value: SearchFilters[keyof SearchFilters]) => {
      const newFilters = { ...filters, [key]: value };
      setFilters(newFilters);
      onFilter?.(newFilters);
    },
    [filters, onFilter]
  );

  const handleClearFilters = useCallback(() => {
    setFilters(defaultFilters);
    onFilter?.(defaultFilters);
  }, [onFilter]);

  const activeFiltersCount = Object.entries(filters).filter(
    ([key, value]) => value !== undefined && (key !== 'tags' || (Array.isArray(value) && value.length > 0))
  ).length;

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Main Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
          <Search className="w-5 h-5 text-navy-400" />
        </div>
        
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="
            w-full pl-12 pr-12 py-3 
            bg-white border border-navy-200 rounded-xl
            text-navy-800 placeholder:text-navy-400
            focus:outline-none focus:ring-2 focus:ring-sea-400 focus:border-transparent
            transition-all duration-200
          "
        />

        {/* Clear Button */}
        {query && (
          <button
            onClick={handleClear}
            className="absolute inset-y-0 right-0 flex items-center pr-4 text-navy-400 hover:text-navy-600"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Filter Toggle Button */}
        {showFilters && (
          <button
            onClick={() => setShowFilterPanel(!showFilterPanel)}
            className={`
              absolute right-12 top-1/2 -translate-y-1/2 p-1.5 rounded-lg
              transition-colors duration-200
              ${showFilterPanel || activeFiltersCount > 0
                ? 'text-sea-600 bg-sea-50'
                : 'text-navy-400 hover:text-navy-600 hover:bg-navy-50'
              }
            `}
          >
            <div className="relative">
              <SlidersHorizontal className="w-5 h-5" />
              {activeFiltersCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 flex items-center justify-center text-xs font-medium text-white bg-sea-600 rounded-full">
                  {activeFiltersCount}
                </span>
              )}
            </div>
          </button>
        )}
      </div>

      {/* Filter Panel */}
      {showFilters && showFilterPanel && (
        <div className="p-4 bg-navy-50 rounded-xl border border-navy-200 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-navy-700 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Фильтры
            </h3>
            {activeFiltersCount > 0 && (
              <button
                onClick={handleClearFilters}
                className="text-sm text-sea-600 hover:text-sea-700"
              >
                Сбросить все
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Document Type */}
            <div>
              <label className="block text-sm font-medium text-navy-600 mb-1.5">
                Тип документа
              </label>
              <select
                value={filters.type || ''}
                onChange={(e) => handleFilterChange('type', e.target.value || undefined)}
                className="
                  w-full px-3 py-2 
                  bg-white border border-navy-200 rounded-lg
                  text-navy-700 focus:outline-none focus:ring-2 focus:ring-sea-400
                "
              >
                <option value="">Все типы</option>
                <option value="pdf">PDF</option>
                <option value="doc">Word</option>
                <option value="txt">Текст</option>
                <option value="image">Изображение</option>
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-navy-600 mb-1.5">
                Статус
              </label>
              <select
                value={filters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
                className="
                  w-full px-3 py-2 
                  bg-white border border-navy-200 rounded-lg
                  text-navy-700 focus:outline-none focus:ring-2 focus:ring-sea-400
                "
              >
                <option value="">Все статусы</option>
                <option value="pending">Ожидает</option>
                <option value="processing">Обрабатывается</option>
                <option value="completed">Завершено</option>
                <option value="error">Ошибка</option>
              </select>
            </div>

            {/* Date Range */}
            <div>
              <label className="block text-sm font-medium text-navy-600 mb-1.5">
                Период
              </label>
              <div className="flex gap-2">
                <input
                  type="date"
                  value={filters.dateFrom?.toISOString().split('T')[0] || ''}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value ? new Date(e.target.value) : undefined)}
                  className="
                    w-full px-3 py-2 
                    bg-white border border-navy-200 rounded-lg
                    text-navy-700 focus:outline-none focus:ring-2 focus:ring-sea-400
                  "
                />
                <input
                  type="date"
                  value={filters.dateTo?.toISOString().split('T')[0] || ''}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value ? new Date(e.target.value) : undefined)}
                  className="
                    w-full px-3 py-2 
                    bg-white border border-navy-200 rounded-lg
                    text-navy-700 focus:outline-none focus:ring-2 focus:ring-sea-400
                  "
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Tags */}
      {activeFiltersCount > 0 && !showFilterPanel && (
        <div className="flex flex-wrap gap-2">
          {filters.type && (
            <span className="inline-flex items-center gap-1 px-3 py-1 text-sm rounded-full bg-sea-100 text-sea-700 border border-sea-200">
              Тип: {filters.type}
              <button onClick={() => handleFilterChange('type', undefined)} className="hover:text-sea-900">
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          )}
          {filters.status && (
            <span className="inline-flex items-center gap-1 px-3 py-1 text-sm rounded-full bg-sea-100 text-sea-700 border border-sea-200">
              Статус: {filters.status}
              <button onClick={() => handleFilterChange('status', undefined)} className="hover:text-sea-900">
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          )}
          {filters.dateFrom && (
            <span className="inline-flex items-center gap-1 px-3 py-1 text-sm rounded-full bg-sea-100 text-sea-700 border border-sea-200">
              С: {filters.dateFrom.toLocaleDateString('ru-RU')}
              <button onClick={() => handleFilterChange('dateFrom', undefined)} className="hover:text-sea-900">
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          )}
          {filters.dateTo && (
            <span className="inline-flex items-center gap-1 px-3 py-1 text-sm rounded-full bg-sea-100 text-sea-700 border border-sea-200">
              По: {filters.dateTo.toLocaleDateString('ru-RU')}
              <button onClick={() => handleFilterChange('dateTo', undefined)} className="hover:text-sea-900">
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
