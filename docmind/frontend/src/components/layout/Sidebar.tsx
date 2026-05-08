import { useAppStore } from '@/lib/store';
import { cn, generateId } from '@/lib/utils';
import { UploadDropzone } from '../documents/UploadDropzone';
import { DocumentCard } from '../documents/DocumentCard';
import { RetrievalSelector } from '../settings/RetrievalSelector';
import { Sparkles, FileText, LogOut, Plus, MessageSquare } from 'lucide-react';
import { useSession, signOut } from 'next-auth/react';
import { ScrollArea } from '../ui/scroll-area';
import { useEffect, useState, useRef } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

export function Sidebar({ className }: { className?: string }) {
  const { documents, setDocuments } = useAppStore();
  const { data: session } = useSession();
  const [chats, setChats] = useState<{ id: string }[]>([]);
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Load documents on mount
  useEffect(() => {
    api.getDocuments().then(setDocuments).catch(console.error);
  }, [setDocuments]);

  // Load chats
  useEffect(() => {
    if (session?.user?.email) {
      api.listSessions(session.user.email).then(setChats).catch(console.error);
    }
  }, [session?.user?.email]);

  const handleNewChat = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      const doc = await api.uploadDocument(file);
      setDocuments([...documents, doc]);
      
      // Start new chat
      const sessionId = generateId();
      router.push(`/chat/${sessionId}`);
    } catch (err) {
      console.error('Failed to upload document for new chat', err);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className={cn("bg-slate-900 text-white flex flex-col", className)}>
      <div className="p-4 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h1 className="font-semibold text-lg tracking-tight">DocMind</h1>
        </div>
        <button 
          onClick={handleNewChat}
          disabled={isUploading}
          className="flex items-center justify-center p-2 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white transition-colors disabled:opacity-50"
          title="New Chat (Upload Document)"
        >
          {isUploading ? (
            <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
          ) : (
            <Plus className="w-4 h-4" />
          )}
        </button>
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          onChange={handleFileChange}
          accept=".pdf,.txt,.docx"
        />
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 flex flex-col gap-6">
          {/* Chats Section */}
          <div className="flex flex-col gap-3">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Recent Chats
            </h2>
            <div className="flex flex-col gap-1">
              {chats.length === 0 ? (
                <div className="text-xs text-slate-500 italic">No recent chats</div>
              ) : (
                chats.map(chat => (
                  <button 
                    key={chat.id} 
                    onClick={() => router.push(`/chat/${chat.id}`)}
                    className="flex items-center gap-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800 p-2 rounded-md transition-colors text-left truncate"
                  >
                    <MessageSquare className="w-4 h-4 shrink-0" />
                    <span className="truncate">{chat.id}</span>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="h-px bg-slate-800" />

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

      <div className="p-4 text-xs text-slate-500 border-t border-slate-800 flex flex-col gap-2">
        {session?.user && (
          <div className="flex items-center justify-between bg-slate-800/50 p-2 rounded-lg mb-2">
            <span className="text-slate-300 truncate pr-2" title={session.user.email || ''}>
              {session.user.email}
            </span>
            <button 
              onClick={() => signOut()}
              className="text-slate-400 hover:text-red-400 p-1"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
        <div className="text-center">Powered by Gemini + ChromaDB</div>
      </div>
    </div>
  );
}
