// frontend/src/context/AppContext.jsx
import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { checkBackendHealth, apiLogin, apiRegister, apiGetDashboard, apiAnalyzeEntry, apiGetHistory } from "../services/api";
import { DEMO_USER, DEMO_HISTORY } from "../services/demoData";

const AppContext = createContext();

export function AppProvider({ children }) {
  // Navigation: landing, login, register, dashboard, analyze, result, history, trends, insights, recommendations, profile, settings
  const [currentPage, setCurrentPageState] = useState(() => {
    const hash = window.location.hash.replace("#/", "").replace("#", "");
    return hash || "landing";
  });

  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("emotrack_user") || "null"); } catch { return null; }
  });
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return localStorage.getItem("emotrack_logged_in") === "true";
  });
  const [isDemoMode, setIsDemoMode] = useState(() => localStorage.getItem("emotrack_demo") === "true");
  const [backendConnected, setBackendConnected] = useState(false);
  
  // Analysis State
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0); // 0 to 4
  const [historyList, setHistoryList] = useState([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [dashboardData, setDashboardData] = useState(null);

  // Sync navigation with browser History API so Chrome Back / Forward buttons work!
  const setCurrentPage = useCallback((page, replace = false) => {
    setCurrentPageState(page);
    const targetHash = `#/${page}`;
    if (window.location.hash !== targetHash) {
      if (replace) {
        window.history.replaceState({ page }, "", targetHash);
      } else {
        window.history.pushState({ page }, "", targetHash);
      }
    }
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      const hash = window.location.hash.replace("#/", "").replace("#", "");
      if (hash) {
        setCurrentPageState(hash);
      } else {
        setCurrentPageState(isLoggedIn ? "dashboard" : "landing");
      }
    };

    window.addEventListener("popstate", handlePopState);
    window.addEventListener("hashchange", handlePopState);
    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.removeEventListener("hashchange", handlePopState);
    };
  }, [isLoggedIn]);

  // Check backend connectivity on mount
  useEffect(() => {
    async function checkHealth() {
      const res = await checkBackendHealth();
      setBackendConnected(res.connected);
    }
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch dashboard when logged in
  useEffect(() => {
    if (isLoggedIn) {
      loadDashboard();
      loadHistory();
    }
  }, [isLoggedIn, isDemoMode]);

  async function loadDashboard() {
    try {
      const data = await apiGetDashboard(isDemoMode);
      setDashboardData(data);
    } catch (e) {
      console.error(e);
      if (!isDemoMode && (e.message?.includes("sign in") || e.message?.includes("token") || e.message?.includes("Session user"))) {
        logout();
      }
    }
  }

  async function loadHistory(filters = {}) {
    try {
      const data = await apiGetHistory({ limit: 20, ...filters }, isDemoMode);
      setHistoryList(data.items || []);
      setHistoryTotal(data.total || 0);
    } catch (e) {
      console.error(e);
    }
  }

  async function login(email, password) {
    try {
      const res = await apiLogin(email, password, isDemoMode);
      setIsDemoMode(false);
      localStorage.removeItem("emotrack_demo");
      setUser(res.user);
      setIsLoggedIn(true);
      localStorage.setItem("emotrack_logged_in", "true");
      localStorage.setItem("emotrack_token", res.access_token);
      localStorage.setItem("emotrack_user", JSON.stringify(res.user));
      setCurrentPage("dashboard");
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  function startDemo() {
    setIsDemoMode(true);
    setUser(DEMO_USER);
    setIsLoggedIn(true);
    localStorage.setItem("emotrack_demo", "true");
    localStorage.setItem("emotrack_logged_in", "true");
    localStorage.setItem("emotrack_user", JSON.stringify(DEMO_USER));
    setCurrentPage("dashboard");
  }

  function logout() {
    setIsLoggedIn(false);
    localStorage.removeItem("emotrack_logged_in");
    localStorage.removeItem("emotrack_token");
    localStorage.removeItem("emotrack_demo");
    localStorage.removeItem("emotrack_user");
    setIsDemoMode(false);
    setUser(null);
    setHistoryList([]);
    setHistoryTotal(0);
    setDashboardData(null);
    setCurrentPage("landing");
  }

  function leaveDemoForRegistration() {
    localStorage.removeItem("emotrack_logged_in");
    localStorage.removeItem("emotrack_demo");
    localStorage.removeItem("emotrack_user");
    setIsLoggedIn(false);
    setIsDemoMode(false);
    setUser(null);
    setHistoryList([]);
    setHistoryTotal(0);
    setDashboardData(null);
    setCurrentPage("register");
  }

  async function runAnalysis(text) {
    setIsAnalyzing(true);
    setLoadingStep(0);

    // 5-step animation sequence matching blueprint Section 17
    const stepDuration = 350;
    for (let i = 1; i <= 4; i++) {
      await new Promise(r => setTimeout(r, stepDuration));
      setLoadingStep(i);
    }

    try {
      if (isDemoMode) throw new Error("Demo mode is read-only. Create an account to analyze your own reflections.");
      const result = await apiAnalyzeEntry(text);
      setCurrentAnalysis(result);
      
      // Prepend to history
      const formatted = {
        id: result.analysis_id || Date.now(),
        created_at: "Just now",
        date: "Today",
        input_text: result.input_text,
        primary_emotion: result.emotion.label,
        emotion_confidence: result.emotion.confidence,
        emotion_distribution: result.emotion.distribution,
        stress_level: result.stress.level,
        stress_confidence: result.stress.confidence,
        wellness_score: result.wellness.score,
        wellness_status: result.wellness.status,
        trend_direction: result.trend.direction,
        trend_entries: result.trend.based_on_entries,
        insight: result.insight,
        recommendations: result.recommendations,
        context_signals: result.explanation?.signals || []
      };
      setHistoryList(prev => [formatted, ...prev]);
      setHistoryTotal(prev => prev + 1);
      await loadDashboard();
      
      await new Promise(r => setTimeout(r, 200));
      setIsAnalyzing(false);
      setCurrentPage("result");
    } catch (err) {
      console.error(err);
      setIsAnalyzing(false);
    }
  }

  async function completeSessionAnalysis(result) {
    setCurrentAnalysis(result);
    if (result.analysis_id) {
      const formatted = {
        id: result.analysis_id,
        created_at: "Just now",
        date: "Today",
        input_text: result.input_text,
        primary_emotion: result.emotion?.label || result.primary_emotion,
        emotion_confidence: result.emotion?.confidence || result.emotion_confidence,
        emotion_distribution: result.emotion?.distribution || result.emotion_distribution,
        stress_level: result.stress?.level || result.stress_level,
        stress_confidence: result.stress?.confidence || result.stress_confidence,
        wellness_score: result.wellness?.score || result.wellness_score,
        wellness_status: result.wellness?.status || result.wellness_status,
        trend_direction: result.trend?.direction || result.trend_direction || "Stable",
        trend_entries: result.trend?.based_on_entries || result.trend_entries || 1,
        insight: result.insight,
        recommendations: result.recommendations,
        context_signals: result.xai_signals || result.explanation?.signals || []
      };
      setHistoryList(prev => [formatted, ...prev]);
      setHistoryTotal(prev => prev + 1);
      await loadDashboard();
    }
    setCurrentPage("result");
  }

  async function register(data) {
    const res = await apiRegister(data);
    setIsDemoMode(false);
    setUser(res.user);
    setIsLoggedIn(true);
    localStorage.setItem("emotrack_logged_in", "true");
    localStorage.setItem("emotrack_token", res.access_token);
    localStorage.setItem("emotrack_user", JSON.stringify(res.user));
    setCurrentPage("dashboard");
  }

  return (
    <AppContext.Provider
      value={{
        currentPage,
        setCurrentPage,
        user,
        setUser,
        isLoggedIn,
        setIsLoggedIn,
        isDemoMode,
        setIsDemoMode,
        backendConnected,
        currentAnalysis,
        setCurrentAnalysis,
        isAnalyzing,
        loadingStep,
        runAnalysis,
        completeSessionAnalysis,
        historyList,
        historyTotal,
        dashboardData,
        loadDashboard,
        loadHistory,
        login,
        register,
        startDemo,
        logout
        ,leaveDemoForRegistration
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  return useContext(AppContext);
}
