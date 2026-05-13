'use client';

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText } from 'lucide-react';

interface DocumentUploadProps {
  onUpload?: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number;
  accept?: Record<string, string[]>;
}

export interface UploadedFile {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUpload,
  maxFiles = 10,
  maxSize = 10 * 1024 * 1024, // 10MB
  accept = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/plain': ['.txt'],
  },
}) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onUpload?.(acceptedFiles);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    maxFiles,
    maxSize,
    accept,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        relative flex flex-col items-center justify-center w-full p-8 
        border-2 border-dashed rounded-xl cursor-pointer transition-all duration-200
        ${
          isDragActive && !isDragReject
            ? 'border-sea-400 bg-sea-50/50'
            : isDragReject
            ? 'border-red-400 bg-red-50/50'
            : 'border-navy-300 bg-navy-50/30 hover:border-sea-400 hover:bg-sea-50/30'
        }
      `}
    >
      <input {...getInputProps()} />
      
      <div
        className={`
          p-4 mb-4 rounded-full transition-colors duration-200
          ${isDragActive && !isDragReject ? 'bg-sea-100' : 'bg-navy-100'}
        `}
      >
        {isDragActive && !isDragReject ? (
          <Upload className="w-8 h-8 text-sea-600" />
        ) : (
          <FileText className="w-8 h-8 text-navy-600" />
        )}
      </div>

      <div className="text-center">
        {isDragActive && !isDragReject ? (
          <p className="text-lg font-medium text-sea-700">
            Отпустите файлы здесь
          </p>
        ) : isDragReject ? (
          <p className="text-lg font-medium text-red-600">
            Некоторые файлы не поддерживаются
          </p>
        ) : (
          <>
            <p className="text-lg font-medium text-navy-700">
              Перетащите файлы сюда
            </p>
            <p className="mt-2 text-sm text-navy-500">
              или нажмите для выбора
            </p>
          </>
        )}
      </div>

      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {['.pdf', '.doc', '.docx', '.txt'].map((ext) => (
          <span
            key={ext}
            className="px-2 py-1 text-xs font-medium rounded bg-navy-100 text-navy-600"
          >
            {ext}
          </span>
        ))}
      </div>

      <p className="mt-4 text-xs text-navy-400">
        Максимум {maxFiles} файлов, до {Math.round(maxSize / 1024 / 1024)} МБ каждый
      </p>
    </div>
  );
};

export default DocumentUpload;
