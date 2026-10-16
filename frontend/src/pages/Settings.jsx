import React, { useState } from "react";
import { useApp } from "../context/AppContext";
import { Shield, Download, Trash2, Check, AlertTriangle } from "lucide-react";
import { apiDeleteHistory, apiUpdatePreferences } from "../services/api";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";

export function Settings() {
  const { user, historyList, loadDashboard, loadHistory, isDemoMode, setCurrentPage } = useApp();
  const [saveHistory, setSaveHistory] = useState(user?.save_history ?? true);
  const [exported, setExported] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const exportData = () => {
    const payload = { account: { name: user?.name, email: user?.email }, reflections: historyList };
    const anchor = document.createElement("a"); anchor.href = `data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(payload, null, 2))}`; anchor.download = "emotrack_data.json"; anchor.click();
    setExported(true); setTimeout(() => setExported(false), 2500);
  };
  const deleteHistory = async () => {
    if (isDemoMode || !window.confirm("Delete all of your saved reflections? This cannot be undone.")) return;
    setDeleting(true);
    try { await apiDeleteHistory(); await loadHistory(); await loadDashboard(); } finally { setDeleting(false); }
  };
  const toggleSaving = async () => {
    const next = !saveHistory;
    if (isDemoMode) return;
    await apiUpdatePreferences(next);
    setSaveHistory(next);
  };
  return <div className="max-w-4xl mx-auto space-y-8 pb-16">
    <div><h1 className="text-3xl font-extrabold text-slate-900">Settings</h1><p className="text-sm text-slate-500 mt-1">Manage your account and personal data.</p></div>
    <section className="bg-white p-7 rounded-3xl border border-slate-200/80">
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-slate-900">Account</h2>
        <button onClick={() => setCurrentPage("profile")} className="text-xs font-semibold text-indigo-600 hover:underline">
          Manage in Profile →
        </button>
      </div>
      <dl className="mt-4 space-y-3 text-sm">
        <div className="flex justify-between gap-4"><dt className="text-slate-500">Name</dt><dd className="font-medium">{user?.name || "—"}</dd></div>
        <div className="flex justify-between gap-4"><dt className="text-slate-500">Email</dt><dd className="font-medium flex items-center gap-2"><span>{user?.email || "—"}</span>{user?.is_email_verified ? <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">Verified</span> : <span className="text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">Unverified</span>}</dd></div>
        <div className="flex justify-between gap-4"><dt className="text-slate-500">Age</dt><dd className="font-medium">{user?.age || 18} years old (Eligible 18+)</dd></div>
      </dl>
    </section>
    <section className="bg-white p-7 rounded-3xl border border-slate-200/80"><div className="flex items-center gap-2"><Shield className="w-5 h-5 text-emerald-600"/><h2 className="font-bold text-slate-900">Privacy & Data</h2></div><div className="mt-4 py-3 flex justify-between items-center text-sm border-b border-slate-100"><div><p className="font-semibold">Save reflection history</p><p className="text-xs text-slate-500 mt-1">Keep entries to build your personal trends.</p></div><button onClick={toggleSaving} disabled={isDemoMode} className={`w-12 h-6 rounded-full relative disabled:opacity-50 ${saveHistory ? "bg-indigo-600" : "bg-slate-300"}`}><span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full ${saveHistory ? "right-0.5" : "left-0.5"}`}/></button></div><div className="mt-5 flex flex-col sm:flex-row gap-3"><button onClick={exportData} className="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold flex items-center justify-center gap-2">{exported ? <Check className="w-4 h-4 text-emerald-600"/> : <Download className="w-4 h-4"/>}{exported ? "Exported" : "Export my data"}</button><button onClick={deleteHistory} disabled={deleting || isDemoMode} className="px-5 py-2.5 rounded-xl border border-rose-200 bg-rose-50 text-rose-700 disabled:opacity-50 text-sm font-semibold flex items-center justify-center gap-2"><Trash2 className="w-4 h-4"/>{isDemoMode ? "Sample history is protected" : deleting ? "Deleting…" : "Delete my history"}</button></div></section>
    <section className="bg-slate-50 p-6 rounded-3xl border border-slate-200"><div className="flex gap-2 items-center"><AlertTriangle className="w-5 h-5 text-amber-500"/><h2 className="font-bold">About EmoTrack</h2></div><p className="text-sm text-slate-600 mt-3">Version 1.0 · EmoTrack supports self-reflection and is not a medical diagnostic service.</p></section>
    <SafetyDisclaimer />
  </div>;
}
