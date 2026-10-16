import React, { useEffect, useState } from "react";
import { useApp } from "../context/AppContext";
import { TrendingUp } from "lucide-react";
import { TrendChart } from "../components/TrendChart";
import { apiGetTrends } from "../services/api";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";

const periods = [["7d", "7 Days"], ["30d", "30 Days"], ["3m", "3 Months"], ["6m", "6 Months"], ["1y", "1 Year"]];
export function Trends() {
  const { isDemoMode, historyTotal } = useApp();
  const [period, setPeriod] = useState("30d");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { setData(null); setError(""); apiGetTrends(isDemoMode, period).then(setData).catch(e => setError(e.message)); }, [isDemoMode, period]);
  const wellness = data?.wellness_trend?.map(d => ({ day: d.date, score: d.score })) || [];
  const stress = data?.stress_trend || [];
  const distribution = data?.emotion_distribution || {};
  const entries = data?.entries_analyzed ?? historyTotal;
  return <div className="max-w-6xl mx-auto space-y-8 pb-16">
    <div><div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-100 text-xs font-semibold text-brand-700 mb-3"><TrendingUp className="w-3.5 h-3.5"/>Longitudinal Progress</div><h1 className="text-3xl font-extrabold text-slate-900">Emotional & Wellness Trends</h1><p className="text-sm text-slate-500 mt-1">Charts use daily, weekly, or monthly averages so they remain readable as history grows.</p></div>
    <div className="flex flex-wrap gap-2">{periods.map(([value, label]) => <button key={value} onClick={() => setPeriod(value)} className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all ${period === value ? "bg-brand-600 text-white border-brand-600 shadow-xs" : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"}`}>{label}</button>)}</div>
    {error && <div className="p-4 rounded-xl bg-rose-50 text-rose-700 text-sm">{error}</div>}
    {!error && entries < 3 && <div className="p-6 rounded-2xl bg-white border border-slate-200 text-sm text-slate-600">Not enough data for a trend yet. Complete at least 3 reflections to establish a meaningful pattern.</div>}
    <section className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs"><h2 className="text-base font-bold">Wellness trend</h2><p className="text-xs text-slate-400 mt-1">Average wellness indicator for each displayed period</p><TrendChart data={wellness} height={220}/></section>
    <section className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs"><h2 className="text-base font-bold">Stress pattern</h2><p className="text-xs text-slate-400 mt-1">Dominant stress level in each displayed period</p><div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 mt-5">{stress.map(pt => <div key={pt.date} className="p-3 rounded-xl bg-slate-50 text-center"><span className={`inline-block w-2.5 h-2.5 rounded-full ${pt.level === "High" ? "bg-rose-500" : pt.level === "Moderate" ? "bg-amber-400" : "bg-emerald-500"}`}/><p className="font-bold text-xs mt-2">{pt.level}</p><p className="text-[11px] text-slate-400 mt-1">{pt.date}</p></div>)}</div>{!stress.length && <p className="text-sm text-slate-400 mt-5">No reflections in this period.</p>}</section>
    <section className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs"><h2 className="text-base font-bold">Emotion distribution</h2><p className="text-xs text-slate-400 mt-1">Across {entries || 0} reflection{entries === 1 ? "" : "s"} in this period</p><div className="space-y-3 mt-5">{Object.entries(distribution).map(([emotion, percent]) => <div key={emotion}><div className="flex justify-between text-xs font-semibold"><span>{emotion}</span><span className="text-slate-500">{percent}%</span></div><div className="h-2.5 bg-slate-100 rounded-full mt-1"><div className="h-full bg-brand-500 rounded-full" style={{width: `${percent}%`}}/></div></div>)}{!Object.keys(distribution).length && <p className="text-sm text-slate-400">No emotion data in this period.</p>}</div></section>
    <SafetyDisclaimer />
  </div>;
}
