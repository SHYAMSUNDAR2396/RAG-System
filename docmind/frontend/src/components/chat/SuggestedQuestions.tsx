import { useAppStore } from '@/lib/store';
import { api } from '@/lib/api';
import { Sparkles } from 'lucide-react';

const FALLBACK_QUESTIONS = [
  "What are the main topics discussed in these documents?",
  "Can you summarize the key findings?",
  "What is the most important conclusion?"
];

export function SuggestedQuestions() {
  const { documents, addMessage, setIsStreaming, sessionId, appendToMessage, updateMessage, setCurrentSources, retrievalMode } = useAppStore();

  // Generate questions based on document titles if available
  let questions = [...FALLBACK_QUESTIONS];
  if (documents.length > 0) {
    const docNames = documents.map(d => d.filename.replace(/\.[^/.]+$/, ""));
    if (docNames.length === 1) {
      questions = [
        `What is ${docNames[0]} about?`,
        `Summarize the key points in ${docNames[0]}`,
        `What are the conclusions of ${docNames[0]}?`
      ];
    }
  }

  const handleQuestionClick = async (question: string) => {
    addMessage({ role: 'user', content: question });
    const assistantMsgId = addMessage({ role: 'assistant', content: '', isStreaming: true });
    setIsStreaming(true);

    try {
      const stream = api.streamChat(sessionId, question, retrievalMode);
      for await (const event of stream) {
        if (event.token) appendToMessage(assistantMsgId, event.token);
        if (event.done) {
          if (event.error) {
            updateMessage(assistantMsgId, { content: `**Error:** ${event.error}`, isStreaming: false });
          } else {
            updateMessage(assistantMsgId, { isStreaming: false, sources: event.sources });
            if (event.sources) setCurrentSources(event.sources);
          }
        }
      }
    } catch (e: any) {
      updateMessage(assistantMsgId, { content: `**Error:** ${e.message}`, isStreaming: false });
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-center gap-2 max-w-lg">
      {questions.map((q, i) => (
        <button
          key={i}
          onClick={() => handleQuestionClick(q)}
          className="flex items-center gap-2 text-sm text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 px-4 py-2 rounded-full transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5" />
          {q}
        </button>
      ))}
    </div>
  );
}
