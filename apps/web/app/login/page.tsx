'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('approver@investops.ai');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email);
      router.push('/workflow');
    } catch (err: any) {
      setError('Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full border border-outline-variant bg-surface-container-lowest rounded-lg p-8 shadow-2xl flex flex-col gap-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-on-surface">Onyx Operations</h1>
          <p className="text-xs text-on-surface-variant uppercase tracking-wider font-mono mt-1">
            Institutional Login
          </p>
        </div>

        {error && <div className="p-3 bg-error-container/30 border border-error/50 text-error text-xs rounded text-center">{error}</div>}

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-mono text-on-surface-variant mb-1 uppercase">
              Select Institutional Role / Email
            </label>
            <select
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface-container-low border border-outline-variant rounded px-3 py-2 text-xs text-on-surface focus:outline-none focus:border-secondary font-mono"
            >
              <option value="approver@investops.ai">Approver / PM (approver@investops.ai)</option>
              <option value="analyst@investops.ai">Research Analyst (analyst@investops.ai)</option>
              <option value="trader@investops.ai">Execution Trader (trader@investops.ai)</option>
              <option value="auditor@investops.ai">Compliance Auditor (auditor@investops.ai)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-secondary-container text-on-secondary-container font-semibold rounded text-xs hover:bg-secondary-container/80 transition-colors mt-2"
          >
            {loading ? 'Authenticating...' : 'Sign In to Operations Control Plane'}
          </button>
        </form>
      </div>
    </div>
  );
}
