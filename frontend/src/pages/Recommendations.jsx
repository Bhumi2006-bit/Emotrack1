import React from "react";
import { Sprout } from "lucide-react";
import { useApp } from "../context/AppContext";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";

export function Recommendations() {
  const { historyList, currentAnalysis, setCurrentPage, isDemoMode } = useApp();
  const analysis = currentAnalysis || historyList?.[0];
  const recommendations = analysis?.recommendations || [];
  return <div className="max-w-5xl mx-auto space-y-8 pb-16"><div><div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-xs font-semibold text-emerald-700 mb-3"><Sprout className="w-3.5 h-3.5"/>Contextual suggestions</div><h1 className="text-3xl font-extrabold text-slate-900">Your Recommendations</h1><p className="text-sm text-slate-500 mt-1">Suggestions are selected from the emotion, stress, and topic signals in your latest reflection.</p></div>{analysis ? <><div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-sm text-slate-600">Based on: <span className="italic">“{analysis.input_text}”</span></div><div className="grid grid-cols-1 md:grid-cols-3 gap-4">{recommendations.map((recommendation, index) => { const parts = typeof recommendation === "string" ? recommendation.split(":") : [recommendation.title, recommendation.description]; return <article key={index} className="bg-white p-6 rounded-3xl border border-slate-200"><span className="w-7 h-7 flex items-center justify-center rounded-lg bg-indigo-100 text-indigo-700 text-xs font-bold">{index + 1}</span><h2 className="font-bold text-slate-900 mt-4">{parts[0]}</h2><p className="text-sm text-slate-500 leading-relaxed mt-2">{parts.slice(1).join(":") || "A gentle next step for today."}</p></article>; })}</div></> : <div className="p-7 rounded-3xl bg-white border border-slate-200 text-sm text-slate-600">{isDemoMode ? "Sample recommendations appear with each sample reflection." : <>Write a reflection first and EmoTrack will offer context-aware suggestions. <button onClick={() => setCurrentPage("analyze")} className="text-indigo-600 font-bold">Write a reflection →</button></>}</div>}<SafetyDisclaimer /></div>;
}
