// frontend/src/App.jsx
import React, { useState } from "react";
import { AppProvider, useApp } from "./context/AppContext";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { AnalysisLoading } from "./components/AnalysisLoading";

// Pages
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { Analyze } from "./pages/Analyze";
import { Result } from "./pages/Result";
import { History } from "./pages/History";
import { Trends } from "./pages/Trends";
import { Insights } from "./pages/Insights";
import { Recommendations } from "./pages/Recommendations";
import { Profile } from "./pages/Profile";
import { Settings } from "./pages/Settings";
import { Diagnostics } from "./pages/Diagnostics";

// Mobile Bottom Nav Icons (Section 35)
import { LayoutDashboard, Sparkles, BookOpen, Lightbulb, User } from "lucide-react";

function MainLayout() {
  const { currentPage, setCurrentPage, isLoggedIn, isAnalyzing, loadingStep } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // If on public pages
  if (currentPage === "landing" && !isLoggedIn) {
    return <Landing />;
  }
  if (currentPage === "login" && !isLoggedIn) {
    return <Login />;
  }
  if (currentPage === "register" && !isLoggedIn) {
    return <Register />;
  }

  // Render the requested active page
  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "analyze":
        return <Analyze />;
      case "result":
        return <Result />;
      case "history":
        return <History />;
      case "trends":
        return <Trends />;
      case "insights":
        return <Insights />;
      case "recommendations":
        return <Recommendations />;
      case "profile":
        return <Profile />;
      case "settings":
        return <Settings />;
      case "diagnostics":
        return <Diagnostics />;
      default:
        return <Dashboard />;
    }
  };

  const mobileNavItems = [
    { id: "dashboard", label: "Home", icon: LayoutDashboard },
    { id: "analyze", label: "Analyze", icon: Sparkles },
    { id: "history", label: "History", icon: BookOpen },
    { id: "insights", label: "Insights", icon: Lightbulb },
    { id: "profile", label: "Profile", icon: User },
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex">
      {/* Desktop Sidebar */}
      <Sidebar mobileOpen={mobileMenuOpen} onCloseMobile={() => setMobileMenuOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-h-screen">
        <Navbar onMobileMenuToggle={() => setMobileMenuOpen(true)} />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto pb-24 lg:pb-12">
          {renderPage()}
        </main>

        {/* Section 35: Mobile Responsive Bottom Navigation */}
        <nav className="lg:hidden fixed bottom-0 left-0 right-0 h-16 bg-white/95 backdrop-blur-md border-t border-slate-200 z-30 px-3 flex items-center justify-around">
          {mobileNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl transition-colors ${
                  isActive ? "text-indigo-600 font-bold" : "text-slate-400 hover:text-slate-600"
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                <span className="text-[10px] mt-0.5">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* 5-Step Animated Analysis Loading Modal (Section 17) */}
      {isAnalyzing && <AnalysisLoading step={loadingStep} />}
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <MainLayout />
    </AppProvider>
  );
}
