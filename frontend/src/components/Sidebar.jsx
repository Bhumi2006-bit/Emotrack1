// frontend/src/components/Sidebar.jsx
import React from "react";
import { useApp } from "../context/AppContext";
import {
  LayoutDashboard,
  Sparkles,
  BookOpen,
  TrendingUp,
  Lightbulb,
  Sprout,
  User,
  Settings,
  LogOut,
  X,
  BrainCircuit
} from "lucide-react";

export function Sidebar({ mobileOpen, onCloseMobile }) {
  const { currentPage, setCurrentPage, logout, isDemoMode } = useApp();

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    ...(!isDemoMode ? [{ id: "analyze", label: "Analyze", icon: Sparkles }] : []),
    { id: "history", label: "History", icon: BookOpen },
    { id: "trends", label: "Trends", icon: TrendingUp },
    { id: "insights", label: "Insights", icon: Lightbulb },
    { id: "recommendations", label: "Recommendations", icon: Sprout },
  ];

  const bottomItems = [
    { id: "profile", label: "Profile", icon: User },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const handleNavClick = (pageId) => {
    setCurrentPage(pageId);
    if (onCloseMobile) onCloseMobile();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-40 lg:hidden"
        />
      )}

      {/* Sidebar Content */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between transition-transform duration-200 ease-in-out ${
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div>
          {/* Logo & Brand */}
          <div className="h-16 px-6 border-b border-slate-100 flex items-center justify-between">
            <div
              onClick={() => handleNavClick("dashboard")}
              className="flex items-center gap-2.5 cursor-pointer group"
            >
              <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-md shadow-brand-100 group-hover:scale-105 transition-transform">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-lg text-slate-900 tracking-tight">EmoTrack</span>
                <span className="block text-[10px] font-medium text-slate-400 -mt-1 tracking-wider uppercase">Wellness AI</span>
              </div>
            </div>
            {/* Close button for mobile */}
            <button
              onClick={onCloseMobile}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Primary Navigation */}
          <nav className="p-4 space-y-1.5">
            <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">Main Menu</p>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${
                    isActive
                      ? "bg-brand-50 text-brand-700 font-semibold shadow-xs"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? "text-brand-600" : "text-slate-400"}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-md bg-brand-100/80 text-brand-700">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Section (Profile, Settings, Logout) */}
        <div className="p-4 border-t border-slate-100 space-y-1.5">
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">Preferences</p>
          {bottomItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2 rounded-xl font-medium text-sm transition-all duration-150 ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700 font-semibold"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}

          <button
            onClick={() => { if (window.confirm("Sign out of EmoTrack?")) logout(); }}
            className="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl font-medium text-sm text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition-colors"
          >
            <LogOut className="w-4 h-4 text-rose-500" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
