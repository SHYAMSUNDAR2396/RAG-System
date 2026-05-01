import { useState, useRef, useEffect } from 'react';
import { useAppStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { ArrowUp, Loader2 } from 'lucide-react';

export function ChatInput() {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { 
    sessionId, 
    isStreaming, 
    setIsStreaming, 
    addMessage, 
    appendToMessage, 
    updateMessage,
    setCurrentSources,
    retrievalMode
  } = useAppStore();

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = async () => {
    if (!input.trim() || isStreaming) return;

    const question = input.trim();
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    // 1. Add user message
    addMessage({ role: 'user', content: question });

    // 2. Add empty assistant message skeleton
    const assistantMsgId = addMessage({ 
      role: 'assistant', 
      content: '', 
      isStreaming: true 
    });

    setIsStreaming(true);

    try {
      // 3. Consume SSE stream
      const stream = api.streamChat(sessionId, question, retrievalMode);
      
      for await (const event of stream) {
        if (event.token) {
          appendToMessage(assistantMsgId, event.token);
        }
        
        if (event.done) {
          if (event.error) {
            updateMessage(assistantMsgId, { 
              content: `**Error:** ${event.error}`, 
              isStreaming: false 
            });
          } else {
            updateMessage(assistantMsgId, { 
              isStreaming: false,
              sources: event.sources 
            });
            if (event.sources) {
              setCurrentSources(event.sources);
            }
          }
        }
      }
    } catch (e: any) {
      updateMessage(assistantMsgId, { 
        content: `**Error:** ${e.message || 'Connection failed'}`, 
        isStreaming: false 
      });
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="relative flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-2xl p-2 shadow-sm focus-within:ring-2 focus-within:ring-indigo-100 focus-within:border-indigo-300 transition-all">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          className="min-h-[44px] max-h-[120px] resize-none border-0 bg-transparent focus-visible:ring-0 px-3 py-3 text-base shadow-none"
          disabled={isStreaming}
        />
        <Button 
          size="icon"
          className="h-10 w-10 shrink-0 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white"
          onClick={handleSubmit}
          disabled={!input.trim() || isStreaming}
        >
          {isStreaming ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <ArrowUp className="w-5 h-5" />
          )}
        </Button>
      </div>
      
      <div className="flex items-center gap-2 px-2">
        <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full uppercase tracking-wider">
          {retrievalMode.replace('_', ' ')}
        </span>
        <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full uppercase tracking-wider">
          Title & AI Summarization Chunking
        </span>
      </div>
    </div>
  );
}
