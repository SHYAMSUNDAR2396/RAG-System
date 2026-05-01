import { redirect } from 'next/navigation';
import { generateId } from '@/lib/utils';

export default function Home() {
  // Automatically generate a new session ID and redirect to the chat workspace
  const sessionId = generateId();
  redirect(`/chat/${sessionId}`);
}
