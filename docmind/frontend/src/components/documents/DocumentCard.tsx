import { Document } from '@/types';
import { useAppStore } from '@/lib/store';
import { api } from '@/lib/api';
import { FileText, Trash2, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

export function DocumentCard({ document }: { document: Document }) {
  const { removeDocument } = useAppStore();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await api.deleteDocument(document.doc_id);
      removeDocument(document.doc_id);
      toast.success(`${document.filename} removed`);
    } catch (e: any) {
      toast.error(`Failed to delete: ${e.message}`);
      setIsDeleting(false);
    }
  };

  return (
    <div className="group flex items-start gap-3 p-3 bg-slate-800/50 hover:bg-slate-800 rounded-xl border border-slate-700/50 transition-colors">
      <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
        <FileText className="w-4 h-4" />
      </div>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-200 truncate" title={document.filename}>
          {document.filename}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-[10px] bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded font-mono">
            {document.chunk_count} chunks
          </span>
          <span className="text-[10px] text-slate-500 uppercase tracking-wider">
            {document.strategy}
          </span>
        </div>
      </div>
      
      <button 
        onClick={handleDelete}
        disabled={isDeleting}
        className="w-7 h-7 rounded-md flex items-center justify-center text-slate-500 hover:bg-red-500/10 hover:text-red-400 transition-colors disabled:opacity-50 opacity-0 group-hover:opacity-100"
      >
        {isDeleting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
      </button>
    </div>
  );
}
