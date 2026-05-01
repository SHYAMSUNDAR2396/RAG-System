// Types mirroring backend schemas

export type RetrievalMode = 'similarity' | 'mmr' | 'multi_query' | 'rrf' | 'hybrid_rerank';

export interface Document {
  doc_id: string;
  filename: string;
  chunk_count: number;
  uploaded_at: string;
}

export interface SourceChunk {
  filename: string;
  chunk_preview: string;
  chunk_index: number;
  relevance_score: number;
}

export interface Message {
  id: string; // client-side only
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceChunk[];
  isStreaming?: boolean;
}

export interface ChatEvent {
  token?: string;
  done: boolean;
  sources?: SourceChunk[];
  error?: string;
}

export interface Settings {
  retrieval_mode: RetrievalMode;
  chunk_size: number;
  chunk_overlap: number;
  k: number;
}

export interface HealthResponse {
  status: string;
  chroma_doc_count: number;
  model: string;
}
