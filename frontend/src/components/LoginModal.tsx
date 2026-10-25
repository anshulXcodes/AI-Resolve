import React, { useState } from 'react';
import { ShieldCheck, Lock, User, AlertCircle, ArrowLeft, KeyRound, Check } from 'lucide-react';
import { apiService } from '../services/api';
import { UserSession } from '../types';

interface LoginModalProps {
  portalRole: 'admin' | 'tester';
  onLoginSuccess: (session: UserSession) => void;
  onCancel: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({
  portalRole,
  onLoginSuccess,
  onCancel
}) => {
  const isAdmin = portalRole === 'admin';
  const defaultUser = isAdmin ? 'admin_resolve' : 'tester_resolve';
  const defaultPass = isAdmin ? 'MapleFox47' : 'OrbitPanda82';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fillDemoCredentials = () => {
    setUsername(defaultUser);
    setPassword(defaultPass);
    setError(null);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError('Please enter both username and password.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const resp = await apiService.login(username.trim(), password);
      if (resp.user.role !== portalRole) {
        setError(`You logged in as ${resp.user.role}, but ${portalRole} privileges are required for this portal.`);
        return;
      }
      onLoginSuccess(resp.user);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || 
        'Invalid credentials. Please verify your demo credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-md w-full border border-slate-200 shadow-2xl p-7 sm:p-8 space-y-6 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-red-700 to-rose-600 text-white flex items-center justify-center mx-auto shadow-md shadow-red-600/20">
            {isAdmin ? <ShieldCheck className="w-6 h-6" /> : <Lock className="w-6 h-6" />}
          </div>
          <h2 className="text-2xl font-black text-slate-900">
            {isAdmin ? 'Admin Portal Login' : 'Testing Portal Login'}
          </h2>
          <p className="text-xs text-slate-500">
            {isAdmin 
              ? 'Authorized maintenance management & duplicate triage access' 
              : 'n8n workflow diagnostics, benchmark metrics & Notion sync'}
          </p>
        </div>

        {/* Demo Credentials Helper Pill */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1">
              <KeyRound className="w-3.5 h-3.5 text-red-600" />
              <span>Demo Credentials</span>
            </span>
            <button
              type="button"
              onClick={fillDemoCredentials}
              className="text-[11px] font-bold text-red-700 hover:text-red-800 bg-red-50 hover:bg-red-100 px-2 py-0.5 rounded-md transition-colors"
            >
              Autofill Credentials
            </button>
          </div>
          <div className="font-mono text-xs text-slate-700 space-y-0.5 bg-white p-2 rounded-xl border border-slate-200/80">
            <div><span className="text-slate-400">ID:</span> <span className="font-bold">{defaultUser}</span></div>
            <div><span className="text-slate-400">PW:</span> <span className="font-bold">{defaultPass}</span></div>
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
              <User className="w-3.5 h-3.5 text-slate-400" />
              <span>User ID</span>
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={defaultUser}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:border-red-600 focus:ring-2 focus:ring-red-600/20 outline-none transition-all"
              autoComplete="username"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
              <Lock className="w-3.5 h-3.5 text-slate-400" />
              <span>Password</span>
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:border-red-600 focus:ring-2 focus:ring-red-600/20 outline-none transition-all"
              autoComplete="current-password"
              required
            />
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="pt-2 space-y-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-lg shadow-slate-900/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <span>Enter {isAdmin ? 'Admin' : 'Testing'} Portal</span>
              )}
            </button>

            <button
              type="button"
              onClick={onCancel}
              className="w-full py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold text-xs flex items-center justify-center space-x-1.5 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Portal Selection</span>
            </button>
          </div>
        </form>

        <p className="text-[11px] text-center text-slate-400">
          Demo authentication verified against backend environment variables.
        </p>
      </div>
    </div>
  );
};
