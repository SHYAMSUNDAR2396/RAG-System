'use client';

import { useEffect } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { ChatPanel } from '@/components/layout/ChatPanel';
import { SourcesPanel } from '@/components/layout/SourcesPanel';
import { useAppStore } from '@/lib/store';

export default function ChatPage({ params }: { params: { sessionId: string } }) {
  const { setSessionId } = useAppStore();

  useEffect(() => {
    if (params.sessionId) {
      setSessionId(params.sessionId);
    }
  }, [params.sessionId, setSessionId]);

  return (
    <div className="flex h-screen w-full bg-white overflow-hidden">
      {/* Sidebar - Settings & Documents */}
      <Sidebar className="w-72 shrink-0 border-r border-slate-200 hidden md:flex flex-col" />

      {/* Main Chat Area */}
      <ChatPanel className="flex-1 min-w-0" />

      {/* Sources Panel */}
      <SourcesPanel className="w-80 shrink-0 border-l border-slate-200 hidden lg:flex flex-col bg-slate-50" />
    </div>
  );
}
