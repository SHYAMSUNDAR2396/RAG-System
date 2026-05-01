import { create } from 'zustand';
import { generateId } from '@/lib/utils';
import { Document, Message, RetrievalMode, SourceChunk } from '@/types';

interface AppState {
  // Session State
  sessionId: string;
  messages: Message[];
  isStreaming: boolean;
  setSessionId: (id: string) => void;

  // Documents
  documents: Document[];
  setDocuments: (docs: Document[]) => void;
  addDocument: (doc: Document) => void;
  removeDocument: (docId: string) => void;

  // Settings
  retrievalMode: RetrievalMode;
  setRetrievalMode: (m: RetrievalMode) => void;

  // Sources (current highlighted/visible)
  currentSources: SourceChunk[];
  setCurrentSources: (sources: SourceChunk[]) => void;
  highlightedSourceIndex: number | null;
  setHighlightedSourceIndex: (idx: number | null) => void;

  // Chat Actions
  addMessage: (msg: Omit<Message, 'id'>) => string;
  appendToMessage: (id: string, token: string) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setIsStreaming: (is: boolean) => void;
  clearChat: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Session
  sessionId: '', // Set on mount
  setSessionId: (id) => set({ sessionId: id }),
  messages: [],
  isStreaming: false,

  // Documents
  documents: [],
  setDocuments: (docs) => set({ documents: docs }),
  addDocument: (doc) => set((state) => ({ documents: [...state.documents, doc] })),
  removeDocument: (docId) => set((state) => ({ 
    documents: state.documents.filter(d => d.doc_id !== docId) 
  })),

  // Settings
  retrievalMode: 'hybrid_rerank',
  setRetrievalMode: (m) => set({ retrievalMode: m }),

  // Sources
  currentSources: [],
  setCurrentSources: (sources) => set({ currentSources: sources }),
  highlightedSourceIndex: null,
  setHighlightedSourceIndex: (idx) => set({ highlightedSourceIndex: idx }),

  // Chat Actions
  addMessage: (msg) => {
    const id = generateId();
    set((state) => ({
      messages: [...state.messages, { ...msg, id }],
    }));
    return id;
  },
  appendToMessage: (id, token) => set((state) => ({
    messages: state.messages.map(msg => 
      msg.id === id ? { ...msg, content: msg.content + token } : msg
    )
  })),
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map(msg => 
      msg.id === id ? { ...msg, ...updates } : msg
    )
  })),
  setIsStreaming: (is) => set({ isStreaming: is }),
  clearChat: () => set({ messages: [], currentSources: [] }),
}));
