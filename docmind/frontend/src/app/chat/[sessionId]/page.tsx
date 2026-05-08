'use client';

import { useEffect } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { ChatPanel } from '@/components/layout/ChatPanel';
import { SourcesPanel } from '@/components/layout/SourcesPanel';
import { useAppStore } from '@/lib/store';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function ChatPage({ params }: { params: { sessionId: string } }) {
  const { setSessionId } = useAppStore();
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, router]);

  useEffect(() => {
    if (params.sessionId) {
      setSessionId(params.sessionId);
    }
  }, [params.sessionId, setSessionId]);

  if (status === 'loading' || status === 'unauthenticated') {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

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
