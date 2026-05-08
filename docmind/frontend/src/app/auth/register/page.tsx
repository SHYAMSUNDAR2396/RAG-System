'use client';

import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      const res = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: { "Content-Type": "application/json" }
      });
      
      if (res.ok) {
        // Automatically redirect to signin
        router.push('/auth/signin');
      } else {
        const data = await res.json();
        setError(data.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Connection failed. Please try again later.');
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <div className="p-8 bg-white rounded-2xl shadow-sm border border-slate-200 text-center max-w-sm w-full">
        <h1 className="text-2xl font-bold mb-2">Create Account</h1>
        <p className="text-slate-500 mb-6">Register to save your chat history</p>
        
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
            Register
          </Button>
        </form>
        
        <p className="mt-4 text-sm text-slate-500">
          Already have an account? <a href="/auth/signin" className="text-indigo-600 hover:underline">Sign in</a>
        </p>
      </div>
    </div>
  );
}
