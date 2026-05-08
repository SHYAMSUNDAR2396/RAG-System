import { Document, RetrievalMode, Settings, HealthResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public detail: string) {
    super(detail);
    this.name = 'ApiError';
  }
}

/**
 * Helper to parse backend error responses
 */
async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = 'An unknown error occurred';
    try {
      const data = await res.json();
      detail = data.detail || data.error || detail;
    } catch {
      // Ignored
    }
    throw new ApiError(detail);
  }
  return res.json() as Promise<T>;
}

// ─── Documents API ────────────────────────────────────────────────────────

export const api = {
  async getDocuments(): Promise<Document[]> {
    const res = await fetch(`${API_URL}/api/documents`);
    const data = await handleResponse<{ documents: Document[] }>(res);
    return data.documents;
  },

  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<Document>(res);
  },

  async deleteDocument(docId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/documents/${docId}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      await handleResponse(res); // throws proper error
    }
  },

  // ─── Settings API ───────────────────────────────────────────────────────

  async getSettings(): Promise<Settings> {
    const res = await fetch(`${API_URL}/api/settings`);
    return handleResponse<Settings>(res);
  },

  async updateSettings(updates: Partial<Settings>): Promise<Settings> {
    const res = await fetch(`${API_URL}/api/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return handleResponse<Settings>(res);
  },

  // ─── Health API ─────────────────────────────────────────────────────────

  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_URL}/api/health`);
    return handleResponse<HealthResponse>(res);
  },

  // ─── Chat API ───────────────────────────────────────────────────────────

  async clearSession(sessionId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/sessions/${sessionId}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      await handleResponse(res);
    }
  },

  async listSessions(userEmail: string): Promise<{ id: string }[]> {
    const res = await fetch(`${API_URL}/api/sessions?user_email=${encodeURIComponent(userEmail)}`);
    return handleResponse<{ id: string }[]>(res);
  },

  /**
   * Stream a chat response using Server-Sent Events (SSE)
   */
  async *streamChat(sessionId: string, question: string, retrievalMode: RetrievalMode, userEmail: string = 'anonymous') {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        session_id: sessionId, 
        question, 
        retrieval_mode: retrievalMode,
        user_email: userEmail 
      }),
    });

    if (!res.ok) {
      await handleResponse(res);
      return;
    }

    if (!res.body) {
      throw new Error('Response body is null');
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      
      // Keep the last partial line in the buffer
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          if (dataStr.trim()) {
            try {
              yield JSON.parse(dataStr);
            } catch (err) {
              console.error('Failed to parse SSE data:', dataStr, err);
            }
          }
        }
      }
    }
  }
};
