import { useAppStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { MessageBubble } from '../chat/MessageBubble';
import { ChatInput } from '../chat/ChatInput';
import { SuggestedQuestions } from '../chat/SuggestedQuestions';
import { ScrollArea } from '../ui/scroll-area';
import { Button } from '../ui/button';
import { Trash2 } from 'lucide-react';
import { api } from '@/lib/api';
import { useEffect, useRef } from 'react';
import { toast } from 'sonner';

export function ChatPanel({ className }: { className?: string }) {
  const { messages, clearChat, sessionId, isStreaming } = useAppStore();
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleClearChat = async () => {
    try {
      await api.clearSession(sessionId);
      clearChat();
      toast.success('Chat history cleared');
    } catch (e) {
      toast.error('Failed to clear chat');
    }
  };

  // Auto-scroll to bottom reliably
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'auto', block: 'end' });
    } else if (scrollRef.current) {
      // Fallback
      const viewport = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        viewport.scrollTo({ top: viewport.scrollHeight, behavior: 'auto' });
      }
    }
  };

  useEffect(() => {
    // Call immediately to ensure continuous scrolling during fast streaming
    scrollToBottom();
    // Fallback after paint
    const timer = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timer);
  }, [messages, isStreaming]);

  return (
    <div className={cn("flex flex-col relative", className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200">
        <h2 className="font-semibold text-slate-800">Chat Session</h2>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={handleClearChat}
          className="text-slate-500 hover:text-red-600"
          disabled={messages.length === 0 || isStreaming}
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Clear Chat
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea ref={scrollRef} className="flex-1 p-2 md:p-4 pb-0">
        <div className="flex flex-col gap-4 md:gap-6 max-w-3xl mx-auto py-4 w-full">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center mt-20">
              <div className="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center mb-6">
                <span className="text-2xl">✨</span>
              </div>
              <h3 className="text-xl font-medium text-slate-800 mb-2">
                Ask anything about your documents
              </h3>
              <p className="text-slate-500 mb-8 max-w-md">
                DocMind uses advanced RAG strategies to find exactly what you're looking for.
              </p>
              <SuggestedQuestions />
            </div>
          ) : (
            messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-2 md:p-4 bg-white/80 backdrop-blur-sm border-t border-slate-200">
        <div className="max-w-3xl mx-auto w-full">
          <ChatInput />
        </div>
      </div>
    </div>
  );
}
