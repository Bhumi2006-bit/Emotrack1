// frontend/src/components/Navbar.jsx
import React from "react";
import { useApp } from "../context/AppContext";
import { User, Menu } from "lucide-react";

export function Navbar({ onMobileMenuToggle }) {
  const { user, isLoggedIn, isDemoMode, dashboardData, setCurrentPage } = useApp();
  const streak = dashboardData?.streak_days ?? user?.streak_days ?? 0;

  return (
    <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 px-4 sm:px-6 flex items-center justify-between">
      {/* Left Mobile Menu Trigger */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMobileMenuToggle}
          className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="hidden sm:flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Platform</span>
          <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
            Wellness AI v1.0
          </span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3 sm:gap-4">
        {isDemoMode && <span className="text-xs font-semibold text-brand-700 bg-brand-50 border border-brand-100 px-2.5 py-1 rounded-full">Read-only demo</span>}

        {isLoggedIn ? (
          <>
            {/* User Profile Dropdown Pill */}
            <div
              onClick={() => setCurrentPage("profile")}
              className="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-full hover:bg-slate-100 cursor-pointer border border-transparent hover:border-slate-200 transition-all"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-white font-semibold text-xs shadow-sm">
                {user?.name ? user.name[0].toUpperCase() : "?"}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-semibold text-slate-800 leading-tight">{user?.name || "Account"}</p>
                <p className="text-[10px] text-slate-500 font-medium">{streak ? `${streak}-day streak 🔥` : "No streak yet"}</p>
              </div>
            </div>
          </>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage("login")}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg hover:bg-slate-100"
            >
              Sign In
            </button>
            <button
              onClick={() => setCurrentPage("register")}
              className="text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 px-3.5 py-1.5 rounded-lg shadow-sm"
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
