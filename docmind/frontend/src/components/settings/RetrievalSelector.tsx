import { useAppStore } from '@/lib/store';
import { RetrievalMode } from '@/types';
import { Label } from '../ui/label';

export function RetrievalSelector() {
  const { retrievalMode, setRetrievalMode } = useAppStore();

  const modes: { value: RetrievalMode; label: string; desc: string }[] = [
    { value: 'similarity', label: 'Similarity', desc: 'Basic vector distance' },
    { value: 'mmr', label: 'MMR', desc: 'Max Marginal Relevance' },
    { value: 'multi_query', label: 'Multi-Query', desc: 'LLM query expansion' },
    { value: 'rrf', label: 'RRF', desc: 'Reciprocal Rank Fusion' },
    { value: 'hybrid_rerank', label: 'Advanced RAG', desc: 'Multi-Query + Vector + BM25 + RRF + SBERT Rerank' },
  ];

  return (
    <div className="flex flex-col gap-2 mt-4">
      <Label className="text-xs text-slate-400 font-medium">Retrieval Mode</Label>
      <div className="grid grid-cols-2 gap-1.5">
        {modes.map((m) => (
          <button
            key={m.value}
            onClick={() => setRetrievalMode(m.value)}
            className={`flex flex-col items-start px-3 py-2 rounded-lg border text-left transition-all ${
              retrievalMode === m.value 
                ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-200' 
                : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:bg-slate-800'
            }`}
          >
            <span className="text-sm font-medium">{m.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
