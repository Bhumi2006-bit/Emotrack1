// frontend/src/pages/Register.jsx
import React, { useState } from "react";
import { useApp } from "../context/AppContext";
import { Brain, ShieldAlert, ArrowRight, AlertCircle } from "lucide-react";

export function Register() {
  const { setCurrentPage, register } = useApp();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [age, setAge] = useState("21");
  const [underageWarning, setUnderageWarning] = useState("");
  const [disclaimerChecked, setDisclaimerChecked] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAgeChange = (val) => {
    setAge(val);
    const parsed = parseInt(val, 10);
    if (!isNaN(parsed) && parsed < 18) {
      setUnderageWarning(
        "EmoTrack is currently designed for individuals aged 18 and older. If you are under 18, please speak with a trusted adult, school counselor, or healthcare professional."
      );
    } else {
      setUnderageWarning("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!name.trim() || name.trim().length < 2) {
      setError("Please enter your full name.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("Please enter a valid email address (e.g., name@example.com).");
      return;
    }

    const parsedAge = parseInt(age, 10);
    if (isNaN(parsedAge) || parsedAge < 18) {
      setError(
        "EmoTrack is currently designed for individuals aged 18 and older. If you are under 18, please speak with a trusted adult, school counselor, or healthcare professional."
      );
      return;
    }

    if (parsedAge > 125) {
      setError("Please enter a realistic age.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!disclaimerChecked) {
      setError("Please acknowledge the non-diagnostic wellness notice to register.");
      return;
    }

    setLoading(true);
    try {
      await register({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password,
        age: parsedAge,
        accepted_disclaimer: true
      });
    } catch (err) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
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
          <h2 className="text-2xl font-bold text-slate-900">Create an Account</h2>
          <p className="text-sm text-slate-500 mt-1">Begin tracking your longitudinal emotional wellness.</p>
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
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-sm outline-none transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-sm outline-none transition-all"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-sm outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Confirm
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-sm outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Age (Minimum 18)
              </label>
              <span className="text-[11px] font-medium text-indigo-600">
                Adult wellness monitor
              </span>
            </div>
            <input
              type="number"
              min="1"
              max="120"
              value={age}
              onChange={(e) => handleAgeChange(e.target.value)}
              placeholder="e.g. 21"
              required
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 text-sm outline-none transition-all"
            />
          </div>

          {underageWarning && (
            <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 text-xs text-amber-900 leading-relaxed flex items-start gap-2.5">
              <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-amber-950 mb-0.5">Eligibility Notice</p>
                <p>{underageWarning}</p>
              </div>
            </div>
          )}

          {/* Section 8 Mandatory Disclaimer */}
          <div className="p-3.5 rounded-2xl bg-indigo-50/60 border border-indigo-100 flex items-start gap-3 mt-2">
            <input
              type="checkbox"
              id="disclaimer"
              checked={disclaimerChecked}
              onChange={(e) => setDisclaimerChecked(e.target.checked)}
              className="mt-1 w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 cursor-pointer"
            />
            <label htmlFor="disclaimer" className="text-xs text-slate-600 leading-snug cursor-pointer select-none">
              I understand that EmoTrack provides wellness insights and is not a medical diagnostic service.
            </label>
          </div>

          <button
            type="submit"
            disabled={loading || !disclaimerChecked || Boolean(underageWarning) || parseInt(age, 10) < 18}
            className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:text-slate-500 disabled:shadow-none disabled:cursor-not-allowed text-white font-bold text-sm shadow-md shadow-indigo-100 hover:shadow-lg transition-all flex items-center justify-center gap-2 mt-4"
          >
            {loading ? "Registering..." : "Create Account"}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-500">
          Already have an account?{" "}
          <button
            onClick={() => setCurrentPage("login")}
            className="text-indigo-600 font-semibold hover:underline"
          >
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}
