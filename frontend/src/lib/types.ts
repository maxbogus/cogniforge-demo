/**
 * Shared TypeScript types for Cogniforge API
 */

export interface Document {
  id: string;
  filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  chunk_count: number | null;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  uploaded_at: string;
  processed_at: string | null;
}

export interface SearchResult {
  document_id: string;
  filename: string;
  content: string;
  score: number;
  chunk_index: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  processing_time_ms: number;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  database: boolean;
  redis: boolean;
  faiss: boolean;
  details?: string;
}

export interface SystemInfo {
  version: string;
  api_version: string;
  environment: string;
  total_documents: number;
  total_chunks: number;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}