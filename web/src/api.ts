const BASE = '/api';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

export interface Domain {
  name: string;
  avg_mastery: number;
  concept_count: number;
  knowledge_count: number;
  memory_count: number;
  has_plan: boolean;
}

export interface Concept {
  concept: string;
  mastery: number;
  confidence: number;
  attempt_count: number;
  correct_count: number;
  mistake_count: number;
}

export interface MasteryData {
  concepts: Concept[];
  weak_count: number;
  due_count: number;
  weak_concepts: string[];
}

export interface KnowledgeFile {
  name: string;
  size: number;
  content: string;
}

export interface MemoryResult {
  content: string;
  type: string;
  importance: number;
  score: number;
  entities: string[];
}

export interface TraceItem {
  trace_id: string;
  user_input: string;
  intent: string;
  agent: string;
  status: string;
  started_at: string;
  ended_at?: string;
  error?: string;
}

export const api = {
  getDomains: () => fetchJSON<Domain[]>('/domains'),

  getPlan: (domain: string) => fetchJSON<{ content: string }>(`/domains/${encodeURIComponent(domain)}/plan`),

  getKnowledge: (domain: string) =>
    fetchJSON<{ files: KnowledgeFile[]; summary: string }>(`/domains/${encodeURIComponent(domain)}/knowledge`),

  getMastery: (domain: string) => fetchJSON<MasteryData>(`/domains/${encodeURIComponent(domain)}/mastery`),

  getMemoryStats: (domain: string) =>
    fetchJSON<{ total: number; by_type: Record<string, number> }>(`/domains/${encodeURIComponent(domain)}/memory/stats`),

  searchMemory: (domain: string, query: string, top_k = 5) =>
    fetchJSON<MemoryResult[]>(`/domains/${encodeURIComponent(domain)}/memory/search`, {
      method: 'POST',
      body: JSON.stringify({ query, top_k }),
    }),

  addKnowledge: (domain: string, content: string) =>
    fetchJSON<{ id: string; message: string }>(`/domains/${encodeURIComponent(domain)}/knowledge`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  chat: (domain: string, message: string, mode = 'free') =>
    fetchJSON<{ reply: string; context_count: number; weak_concepts: string[] }>(
      `/domains/${encodeURIComponent(domain)}/chat`,
      { method: 'POST', body: JSON.stringify({ message, mode }) },
    ),

  getTraces: (limit = 30) => fetchJSON<TraceItem[]>(`/traces?limit=${limit}`),

  getTrace: (id: string) => fetchJSON<{ trace: any; evaluation: any }>(`/traces/${id}`),

  health: () => fetchJSON<{ status: string; version: string }>('/health'),
};
