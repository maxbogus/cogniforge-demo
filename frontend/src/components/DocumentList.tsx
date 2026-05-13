'use client';

import React from 'react';
import { FileText, Download, Trash2, Eye, Clock, User } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: Date;
  uploadedBy: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  pages?: number;
  tags?: string[];
}

interface DocumentListProps {
  documents: Document[];
  onView?: (doc: Document) => void;
  onDownload?: (doc: Document) => void;
  onDelete?: (doc: Document) => void;
  emptyMessage?: string;
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Б';
  const k = 1024;
  const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onView,
  onDownload,
  onDelete,
  emptyMessage = 'Документы не найдены',
}) => {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="p-4 mb-4 rounded-full bg-navy-100">
          <FileText className="w-8 h-8 text-navy-400" />
        </div>
        <p className="text-navy-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="group flex items-center gap-4 p-4 bg-white border border-navy-200 rounded-xl hover:border-sea-300 hover:shadow-md transition-all duration-200"
        >
          {/* File Icon */}
          <div className="flex-shrink-0 p-3 bg-sea-50 rounded-lg">
            <FileText className="w-6 h-6 text-sea-600" />
          </div>

          {/* Document Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-medium text-navy-800 truncate">{doc.name}</h3>
              <StatusBadge status={doc.status} />
            </div>
            
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-navy-500">
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {formatDate(doc.uploadedAt)}
              </span>
              <span className="flex items-center gap-1">
                <User className="w-4 h-4" />
                {doc.uploadedBy}
              </span>
              <span>{formatFileSize(doc.size)}</span>
              {doc.pages && <span>{doc.pages} стр.</span>}
            </div>

            {/* Tags */}
            {doc.tags && doc.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {doc.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 text-xs rounded-full bg-sea-50 text-sea-700 border border-sea-200"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex-shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {onView && (
              <button
                onClick={() => onView(doc)}
                className="p-2 rounded-lg text-navy-500 hover:text-sea-600 hover:bg-sea-50 transition-colors"
                title="Просмотр"
              >
                <Eye className="w-5 h-5" />
              </button>
            )}
            {onDownload && (
              <button
                onClick={() => onDownload(doc)}
                className="p-2 rounded-lg text-navy-500 hover:text-sea-600 hover:bg-sea-50 transition-colors"
                title="Скачать"
              >
                <Download className="w-5 h-5" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(doc)}
                className="p-2 rounded-lg text-navy-500 hover:text-red-600 hover:bg-red-50 transition-colors"
                title="Удалить"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;
