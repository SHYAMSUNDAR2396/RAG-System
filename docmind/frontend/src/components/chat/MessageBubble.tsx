import { Message } from '@/types';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAppStore } from '@/lib/store';

export function MessageBubble({ message }: { message: Message }) {
  const { setHighlightedSourceIndex } = useAppStore();
  const isUser = message.role === 'user';

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div 
        className={cn(
          "max-w-[85%] rounded-2xl px-5 py-4",
          isUser 
            ? "bg-indigo-600 text-white shadow-sm" 
            : "bg-white border border-slate-200 shadow-sm text-slate-800"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm prose-slate max-w-none prose-p:leading-relaxed prose-pre:bg-slate-50 prose-pre:border prose-pre:border-slate-200">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
            {message.isStreaming && <span className="inline-block w-2 h-4 bg-indigo-500 animate-pulse ml-1 align-middle" />}
          </div>
        )}

        {/* Source Badges */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
            <span className="text-xs text-slate-400 font-medium py-1">Sources:</span>
            {message.sources.map((source, idx) => (
              <button
                key={idx}
                onMouseEnter={() => setHighlightedSourceIndex(idx)}
                onMouseLeave={() => setHighlightedSourceIndex(null)}
                className="text-xs font-medium px-2 py-1 bg-slate-50 hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 border border-slate-200 rounded-md transition-colors"
              >
                [{idx + 1}] {source.filename}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
