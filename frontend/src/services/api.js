import { DEMO_DASHBOARD, DEMO_HISTORY, DEMO_USER } from "./demoData";

const API_BASE = (import.meta.env?.VITE_API_URL || import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const authHeaders = () => {
  const token = localStorage.getItem("emotrack_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};
const parse = async (res, fallback) => {
  if (res.ok) return res.json();
  const body = await res.json().catch(() => ({}));
  throw new Error(body.detail || fallback);
};

export async function checkBackendHealth() {
  try { const res = await fetch(`${API_BASE}/health`); return { connected: res.ok, data: res.ok ? await res.json() : null }; }
  catch { return { connected: false }; }
}
export async function apiLogin(email, password) {
  return parse(await fetch(`${API_BASE}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) }), "Login failed");
}
export async function apiRegister(data) {
  return parse(await fetch(`${API_BASE}/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) }), "Registration failed");
}
export async function apiGetDashboard(isDemoMode = false) {
  if (isDemoMode) return DEMO_DASHBOARD;
  return parse(await fetch(`${API_BASE}/dashboard`, { headers: authHeaders() }), "Dashboard fetch failed");
}
export async function apiAnalyzeEntry(text) {
  return parse(await fetch(`${API_BASE}/analysis`, { method: "POST", headers: { "Content-Type": "application/json", ...authHeaders() }, body: JSON.stringify({ text }) }), "Analysis failed. Please make sure the backend is running.");
}
export async function apiStartSession(text) {
  return parse(await fetch(`${API_BASE}/analysis/session/start`, { method: "POST", headers: { "Content-Type": "application/json", ...authHeaders() }, body: JSON.stringify({ text }) }), "Failed to start conversation session.");
}
export async function apiRespondSession(sessionId, text) {
  return parse(await fetch(`${API_BASE}/analysis/session/${sessionId}/respond`, { method: "POST", headers: { "Content-Type": "application/json", ...authHeaders() }, body: JSON.stringify({ text }) }), "Failed to send follow-up response.");
}
export async function apiFinalizeSession(sessionId) {
  return parse(await fetch(`${API_BASE}/analysis/session/${sessionId}/finalize`, { method: "POST", headers: { "Content-Type": "application/json", ...authHeaders() } }), "Failed to finalize session.");
}

export async function apiGetHistory(filters = {}, isDemoMode = false) {
  if (isDemoMode) {
    let items = [...DEMO_HISTORY];
    if (filters.emotion && filters.emotion !== "All") items = items.filter(item => item.primary_emotion.toLowerCase() === filters.emotion.toLowerCase());
    if (filters.stress && filters.stress !== "All") items = items.filter(item => item.stress_level.toLowerCase() === filters.stress.toLowerCase());
    const total = items.length, offset = filters.offset || 0, limit = filters.limit || total;
    return { total, items: items.slice(offset, offset + limit) };
  }
  const query = new URLSearchParams();
  ["emotion", "stress", "limit", "offset"].forEach(key => { if (filters[key] !== undefined) query.set(key, filters[key]); });
  return parse(await fetch(`${API_BASE}/analysis/history?${query}`, { headers: authHeaders() }), "History fetch failed");
}
export async function apiGetTrends(isDemoMode = false, period = "30d") {
  if (isDemoMode) {
    return {
      wellness_trend: DEMO_DASHBOARD.weekly_trend.map(item => ({ date: item.day, score: item.score })),
      stress_trend: [
        { date: "Mon", level: "Low", numeric: 1 },
        { date: "Tue", level: "Low", numeric: 1 },
        { date: "Wed", level: "Moderate", numeric: 2 },
        { date: "Thu", level: "Low", numeric: 1 },
        { date: "Fri", level: "Low", numeric: 1 },
        { date: "Sat", level: "Low", numeric: 1 }
      ],
      emotion_distribution: Object.fromEntries(DEMO_DASHBOARD.emotion_distribution.map(item => [item.emotion, item.percentage])),
      entries_analyzed: DEMO_HISTORY.length
    };
  }
  return parse(await fetch(`${API_BASE}/analysis/trends?period=${period}`, { headers: authHeaders() }), "Trends fetch failed");
}
export async function apiDeleteHistory() {
  return parse(await fetch(`${API_BASE}/analysis/history`, { method: "DELETE", headers: authHeaders() }), "Could not delete history");
}
export async function apiUpdatePreferences(save_history) {
  return parse(await fetch(`${API_BASE}/auth/preferences`, { method: "PATCH", headers: { "Content-Type": "application/json", ...authHeaders() }, body: JSON.stringify({ save_history }) }), "Could not update privacy preference");
}

export async function apiSaveRecommendations(items) {
  return parse(await fetch(`${API_BASE}/analysis/recommendations/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ items })
  }), "Failed to save recommendations");
}

export async function apiGetSavedRecommendations() {
  return parse(await fetch(`${API_BASE}/analysis/recommendations`, {
    headers: authHeaders()
  }), "Failed to load saved recommendations");
}

export async function apiDeleteSavedRecommendation(recId) {
  return parse(await fetch(`${API_BASE}/analysis/recommendations/${recId}`, {
    method: "DELETE",
    headers: authHeaders()
  }), "Failed to delete recommendation");
}

export async function apiToggleSavedRecommendation(recId) {
  return parse(await fetch(`${API_BASE}/analysis/recommendations/${recId}/toggle`, {
    method: "PATCH",
    headers: authHeaders()
  }), "Failed to toggle recommendation status");
}

export async function apiVerifyEmail(token) {
  return parse(await fetch(`${API_BASE}/auth/verify-email?token=${encodeURIComponent(token)}`), "Failed to verify email");
}

export async function apiResendVerification() {
  return parse(await fetch(`${API_BASE}/auth/resend-verification`, {
    method: "POST",
    headers: authHeaders()
  }), "Failed to resend verification email");
}

export async function apiChangePassword(current_password, new_password, confirm_password) {
  return parse(await fetch(`${API_BASE}/auth/change-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ current_password, new_password, confirm_password })
  }), "Failed to change password");
}

export async function apiUpdateProfile(payload) {
  return parse(await fetch(`${API_BASE}/auth/profile`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }), "Failed to update profile");
}

export async function apiSubmitFeedback(analysisId, feedback) {
  return parse(await fetch(`${API_BASE}/analysis/${analysisId}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ feedback })
  }), "Failed to submit reflection feedback");
}

export { DEMO_USER };
