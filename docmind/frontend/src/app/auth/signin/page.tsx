'use client';

import { signIn } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SignIn() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const res = await signIn('credentials', {
      redirect: false,
      email,
      password,
    });

    if (res?.error) {
      setError('Invalid email or password');
    } else {
      router.push('/');
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <div className="p-8 bg-white rounded-2xl shadow-sm border border-slate-200 text-center max-w-sm w-full">
        <h1 className="text-2xl font-bold mb-2">Sign in</h1>
        <p className="text-slate-500 mb-6">Welcome back to DocMind</p>
        
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-left">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input 
              type="email" 
              required
              className="w-full border rounded-lg p-2 focus:outline-indigo-500" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input 
              type="password" 
              required
              className="w-full border rounded-lg p-2 focus:outline-indigo-500" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
            />
          </div>
          <Button type="submit" className="w-full bg-indigo-600 text-white hover:bg-indigo-700 h-10 mt-2">
            Sign In
          </Button>
        </form>
        
        <p className="mt-4 text-sm text-slate-500">
          Don't have an account? <a href="/auth/register" className="text-indigo-600 hover:underline">Register here</a>
        </p>
      </div>
    </div>
  );
}
