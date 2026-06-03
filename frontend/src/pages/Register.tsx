import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';
import {
  KeyRound,
  Mail,
  User,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Loader2,
  ShieldCheck
} from 'lucide-react';

export const Register: React.FC = () => {
  const navigate = useNavigate();

  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const handleRegister = async (
    e: React.FormEvent<HTMLFormElement>
  ): Promise<void> => {
    e.preventDefault();

    setError(null);
    setLoading(true);

    try {
      await authApi.register({
        name: name.trim(),
        email: email.trim(),
        password,
        role: 'customer'
      });

      setSuccess(true);

      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          'Registration failed. Try a different email.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050814] flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-emerald-500/10 blur-[140px] rounded-full" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-500/10 blur-[140px] rounded-full" />

      <div className="w-full max-w-md relative z-10">
        <div className="glass-card rounded-3xl overflow-hidden border border-slate-800/70 shadow-2xl backdrop-blur-xl">
          <div className="card-glow" />

          {/* Header */}
          <div className="px-8 pt-10 pb-8 text-center border-b border-slate-800/40">
            <div className="mx-auto w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-5">
              <Sparkles className="w-8 h-8 text-emerald-400" />
            </div>

            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">
              Create Account
            </h1>

            <p className="text-slate-400 text-sm mt-2">
              Join Resolve AI and get instant autonomous support
            </p>

            <div className="flex items-center justify-center gap-2 mt-4 text-emerald-400 text-xs font-semibold">
              <ShieldCheck className="w-4 h-4" />
              Secure Customer Registration
            </div>
          </div>

          {/* Form */}
          <form
            onSubmit={handleRegister}
            className="p-8 space-y-6"
          >
            {success && (
              <div className="bg-emerald-950/20 border border-emerald-800/40 text-emerald-400 p-4 rounded-xl text-sm flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 shrink-0" />
                <span>
                  Account created successfully. Redirecting to login...
                </span>
              </div>
            )}

            {error && (
              <div className="bg-rose-950/20 border border-rose-800/40 text-rose-400 p-4 rounded-xl text-sm flex items-start gap-3">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Name */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Full Name
              </label>

              <div className="relative">
                <User className="absolute left-4 top-3.5 w-4 h-4 text-slate-500" />

                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-all"
                />
              </div>
            </div>

            {/* Email */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Email Address
              </label>

              <div className="relative">
                <Mail className="absolute left-4 top-3.5 w-4 h-4 text-slate-500" />

                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="customer@resolveai.com"
                  className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-all"
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Password
              </label>

              <div className="relative">
                <KeyRound className="absolute left-4 top-3.5 w-4 h-4 text-slate-500" />

                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#0d1329]/80 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-all"
                />
              </div>
            </div>

            {/* Create Button */}
            <button
              type="submit"
              disabled={loading || success}
              className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-500/50 text-white py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all shadow-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating Account...
                </>
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            {/* Divider */}
            <div className="relative flex items-center py-1">
              <div className="flex-grow border-t border-slate-800"></div>
              <span className="mx-4 text-[10px] uppercase font-bold tracking-widest text-slate-500">
                or
              </span>
              <div className="flex-grow border-t border-slate-800"></div>
            </div>

            {/* Back Button */}
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="w-full py-3 border border-slate-800 hover:border-slate-700 bg-[#0d1329]/60 hover:bg-[#0d1329] text-slate-300 rounded-xl text-sm font-semibold transition-all"
            >
              Back to Login
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-slate-600 mt-6">
          Powered by Resolve AI • Autonomous Resolution Engine
        </p>
      </div>
    </div>
  );
};