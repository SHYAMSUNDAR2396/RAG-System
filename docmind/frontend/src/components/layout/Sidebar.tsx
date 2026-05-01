import { useAppStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { UploadDropzone } from '../documents/UploadDropzone';
import { DocumentCard } from '../documents/DocumentCard';
import { RetrievalSelector } from '../settings/RetrievalSelector';
import { Sparkles, FileText } from 'lucide-react';
import { ScrollArea } from '../ui/scroll-area';
import { useEffect } from 'react';
import { api } from '@/lib/api';

export function Sidebar({ className }: { className?: string }) {
  const { documents, setDocuments } = useAppStore();

  // Load documents on mount
  useEffect(() => {
    api.getDocuments().then(setDocuments).catch(console.error);
  }, [setDocuments]);

  return (
    <div className={cn("bg-slate-900 text-white flex flex-col", className)}>
      <div className="p-4 flex items-center gap-2 border-b border-slate-800">
        <Sparkles className="w-5 h-5 text-indigo-400" />
        <h1 className="font-semibold text-lg tracking-tight">DocMind</h1>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 flex flex-col gap-6">
          {/* Documents Section */}
          <div className="flex flex-col gap-3">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Documents
            </h2>
            <UploadDropzone />
            
            <div className="flex flex-col gap-2 mt-2">
              {documents.length === 0 ? (
                <div className="text-sm text-slate-500 flex flex-col items-center justify-center p-6 border border-dashed border-slate-800 rounded-lg">
                  <FileText className="w-8 h-8 mb-2 opacity-20" />
                  No documents yet
                </div>
              ) : (
                documents.map((doc) => (
                  <DocumentCard key={doc.doc_id} document={doc} />
                ))
              )}
            </div>
          </div>

          <div className="h-px bg-slate-800" />

          {/* Settings Section */}
          <div className="flex flex-col gap-3">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Retrieval Settings
            </h2>
            <RetrievalSelector />
          </div>
        </div>
      </ScrollArea>

      <div className="p-4 text-xs text-slate-500 border-t border-slate-800 text-center">
        Powered by Gemini + ChromaDB
      </div>
    </div>
  );
}
