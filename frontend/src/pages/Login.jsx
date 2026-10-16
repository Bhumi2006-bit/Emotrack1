// frontend/src/pages/Login.jsx
import React, { useState } from "react";
import { useApp } from "../context/AppContext";
import { Brain, AlertCircle } from "lucide-react";

export function Login() {
  const { login, setCurrentPage } = useApp();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);
    const res = await login(email.trim().toLowerCase(), password);
    setLoading(false);
    if (!res.success) {
      setError(res.error || "Unable to sign in.");
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center items-center p-4">
      {/* Brand header */}
      <div
        onClick={() => setCurrentPage("landing")}
        className="flex items-center gap-2 mb-8 cursor-pointer group"
      >
        <div className="w-10 h-10 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-100 group-hover:scale-105 transition-transform">
          <Brain className="w-6 h-6" />
        </div>
        <span className="text-2xl font-bold text-slate-900 tracking-tight">EmoTrack</span>
      </div>

      <div className="w-full max-w-md bg-white rounded-3xl p-8 shadow-xl shadow-slate-200/60 border border-slate-100">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Welcome back 👋</h2>
          <p className="text-sm text-slate-500 mt-1">Sign in to review your emotional wellness overview.</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-100 text-xs text-rose-700 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@domain.com"
              required
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-sm outline-none transition-all"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Password
              </label>
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-sm outline-none transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-md shadow-indigo-100 hover:shadow-lg transition-all flex items-center justify-center gap-2 mt-2"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-500">
          Don't have an account?{" "}
          <button
            onClick={() => setCurrentPage("register")}
            className="text-indigo-600 font-semibold hover:underline"
          >
            Create account
          </button>
        </div>
      </div>
    </div>
  );
}
