import React, { useState } from 'react';
import { Scale, Lock, Mail, ArrowRight, UserPlus, LogIn, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface LoginPageProps {
  onLoginSuccess: (user: any) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('counsel@lexintel.ai');
  const [password, setPassword] = useState('lexintel2025');
  const [fullName, setFullName] = useState('Lead Legal Counsel');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let res;
      if (isRegister) {
        res = await api.register(email, password, fullName);
      } else {
        res = await api.login(email, password);
      }
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060913] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-sky-400 p-0.5 mx-auto mb-4 shadow-xl shadow-blue-500/20">
            <div className="w-full h-full bg-[#070b14] rounded-[14px] flex items-center justify-center">
              <Scale className="w-6 h-6 text-blue-400" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-white font-['Cinzel',serif]">LEXINTEL AI</h2>
          <p className="text-xs text-slate-400 mt-1">Multi-Agent Legal Intelligence Workspace</p>
        </div>

        <div className="legal-card p-8 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
            <h3 className="text-lg font-bold text-white">
              {isRegister ? 'Register Counsel Account' : 'Counsel Sign In'}
            </h3>
            <button
              onClick={() => { setIsRegister(!isRegister); setError(null); }}
              className="text-xs text-blue-400 hover:text-blue-300 font-semibold"
            >
              {isRegister ? 'Already registered? Login' : 'Create new account'}
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Full Name & Title</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  required
                  placeholder="e.g. Eleanor Vance Esq."
                  className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  placeholder="counsel@lexintel.ai"
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-blue-500/25 transition-all flex items-center justify-center gap-2 mt-6 disabled:opacity-50"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : isRegister ? (
                <>
                  <UserPlus className="w-4 h-4" />
                  <span>Create Account</span>
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  <span>Enter Platform</span>
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Access */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 text-center">
            <span className="text-[11px] text-slate-400 block mb-2">
              For Quick Academic Evaluation:
            </span>
            <button
              type="button"
              onClick={() => {
                setEmail('counsel@lexintel.ai');
                setPassword('lexintel2025');
              }}
              className="text-xs text-blue-400 hover:underline font-mono"
            >
              Auto-fill Preloaded Demo Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};