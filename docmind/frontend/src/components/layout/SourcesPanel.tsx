import { useAppStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../ui/scroll-area';
import { FileText, Search, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function SourcesPanel({ className }: { className?: string }) {
  const { currentSources, highlightedSourceIndex } = useAppStore();

  return (
    <div className={cn("flex flex-col", className)}>
      <div className="p-4 border-b border-slate-200 bg-slate-100 flex items-center justify-between">
        <h2 className="font-semibold text-slate-800 flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-500" />
          Sources
        </h2>
        {currentSources.length > 0 && (
          <span className="bg-indigo-100 text-indigo-700 text-xs font-medium px-2 py-1 rounded-full">
            {currentSources.length}
          </span>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 flex flex-col gap-4">
          {currentSources.length === 0 ? (
            <div className="flex flex-col items-center justify-center text-center mt-10">
              <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center mb-4 text-slate-300">
                <Search className="w-6 h-6" />
              </div>
              <p className="text-sm text-slate-500">
                Retrieved sources will appear here when you ask a question.
              </p>
            </div>
          ) : (
            <AnimatePresence>
              {currentSources.map((source, idx) => (
                <motion.div
                  key={`${source.filename}-${idx}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={cn(
                    "bg-white p-4 rounded-xl border transition-all duration-300",
                    highlightedSourceIndex === idx 
                      ? "border-indigo-400 ring-2 ring-indigo-100 shadow-md" 
                      : "border-slate-200 shadow-sm"
                  )}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-indigo-50 text-indigo-600 text-xs font-mono px-1.5 py-0.5 rounded">
                      #{idx + 1}
                    </span>
                    <span className="text-xs font-medium text-slate-600 truncate flex-1">
                      {source.filename}
                    </span>
                  </div>
                  
                  <p className="text-sm text-slate-600 font-mono leading-relaxed bg-slate-50 p-2 rounded-md border border-slate-100">
                    {source.chunk_preview}
                  </p>
                  
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Relevance</span>
                    <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-indigo-500 rounded-full" 
                        style={{ width: `${Math.round(source.relevance_score * 100)}%` }}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
