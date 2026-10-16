// frontend/src/pages/History.jsx
import React, { useEffect, useState } from "react";
import { useApp } from "../context/AppContext";
import { BookOpen, Filter, Search, Eye, Calendar, X, Activity, Brain, ArrowUpRight } from "lucide-react";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";

export function History() {
  const { historyList, historyTotal, loadHistory, setCurrentAnalysis, setCurrentPage } = useApp();
  const [emotionFilter, setEmotionFilter] = useState("All");
  const [stressFilter, setStressFilter] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const emotions = ["All", "Joy", "Neutral", "Sadness", "Fear", "Anger", "Surprise", "Disgust"];
  const stressLevels = ["All", "Low", "Moderate", "High"];

  useEffect(() => {
    loadHistory({ emotion: emotionFilter, stress: stressFilter, limit: pageSize, offset: (page - 1) * pageSize });
  }, [emotionFilter, stressFilter, page]);

  const filtered = (historyList || []).filter((item) => {
    if (emotionFilter !== "All" && item.primary_emotion.toLowerCase() !== emotionFilter.toLowerCase()) {
      return false;
    }
    if (stressFilter !== "All" && item.stress_level.toLowerCase() !== stressFilter.toLowerCase()) {
      return false;
    }
    if (searchTerm.trim() && !item.input_text.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  const handleOpenDetail = (entry) => {
    setSelectedEntry(entry);
  };

  const handleFullResultView = (entry) => {
    setCurrentAnalysis(entry);
    setCurrentPage("result");
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Page Header (Section 27) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Your Analysis History</h1>
          <p className="text-sm text-slate-500 mt-1">Review past reflections and longitudinal progression.</p>
        </div>
        <div className="text-xs font-semibold text-slate-500 bg-white px-3 py-1.5 rounded-xl border border-slate-200 self-start sm:self-auto">
          {historyTotal} entries recorded
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center gap-4 justify-between">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search entries by keywords..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-200 focus:border-brand-600 outline-none"
          />
        </div>

        {/* Dropdowns */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <Filter className="w-3.5 h-3.5" />
            <span>Filters:</span>
          </div>

          <select
            value={emotionFilter}
            onChange={(e) => { setEmotionFilter(e.target.value); setPage(1); }}
            className="text-xs px-3 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 outline-none focus:border-brand-600"
          >
            {emotions.map((e) => (
              <option key={e} value={e}>
                {e === "All" ? "All Emotions" : e}
              </option>
            ))}
          </select>

          <select
            value={stressFilter}
            onChange={(e) => { setStressFilter(e.target.value); setPage(1); }}
            className="text-xs px-3 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 outline-none focus:border-brand-600"
          >
            {stressLevels.map((s) => (
              <option key={s} value={s}>
                {s === "All" ? "All Stress Levels" : `${s} Stress`}
              </option>
            ))}
          </select>
        </div>
      </div>

      {historyTotal > 0 && (
        <div className="flex flex-col sm:flex-row gap-3 items-center justify-between text-xs text-slate-500">
          <span>Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, historyTotal)} of {historyTotal}</span>
          <div className="flex gap-2"><button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="px-3 py-2 rounded-lg bg-white border border-slate-200 disabled:opacity-40">Previous</button><button disabled={page * pageSize >= historyTotal} onClick={() => setPage(p => p + 1)} className="px-3 py-2 rounded-lg bg-white border border-slate-200 disabled:opacity-40">Next</button></div>
        </div>
      )}

      {/* History Table / Cards (Section 27) */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200/80 text-slate-400 uppercase tracking-wider font-bold">
                <th className="py-3.5 px-6">Date</th>
                <th className="py-3.5 px-6">Reflection Snippet</th>
                <th className="py-3.5 px-6">Emotion</th>
                <th className="py-3.5 px-6">Stress</th>
                <th className="py-3.5 px-6">Wellness</th>
                <th className="py-3.5 px-6 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-4 px-6 font-medium text-slate-700 whitespace-nowrap">
                    {item.date || item.created_at?.slice(0, 10)}
                  </td>
                  <td className="py-4 px-6 text-slate-600 max-w-xs truncate italic">
                    "{item.input_text}"
                  </td>
                  <td className="py-4 px-6 whitespace-nowrap">
                    <span className="font-bold text-slate-800 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200">
                      {item.primary_emotion} {Math.round(item.emotion_confidence * 100)}%
                    </span>
                  </td>
                  <td className="py-4 px-6 whitespace-nowrap">
                    <span
                      className={`font-bold px-2.5 py-1 rounded-full border text-[11px] ${
                        item.stress_level === "High"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : item.stress_level === "Moderate"
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : "bg-emerald-50 text-emerald-700 border-emerald-200"
                      }`}
                    >
                      {item.stress_level}
                    </span>
                  </td>
                  <td className="py-4 px-6 whitespace-nowrap">
                    <span className="font-extrabold text-slate-900 text-sm">{item.wellness_score}</span>
                    <span className="text-slate-400 text-[10px] ml-1">/ 100</span>
                  </td>
                  <td className="py-4 px-6 text-right whitespace-nowrap">
                    <button
                      onClick={() => handleOpenDetail(item)}
                      className="px-3 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-600 hover:text-white text-indigo-700 font-semibold border border-indigo-200/80 transition-all text-xs inline-flex items-center gap-1"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>View</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <div className="py-16 text-center text-slate-400 text-xs">
            No reflections found matching the selected filters.
          </div>
        )}
      </div>

      {/* History Detail Modal (Section 28) */}
      {selectedEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl max-w-xl w-full p-7 border border-slate-100 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
            <button
              onClick={() => setSelectedEntry(null)}
              className="absolute top-5 right-5 p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
              <Calendar className="w-3.5 h-3.5" />
              <span>{selectedEntry.created_at || selectedEntry.date}</span>
            </div>

            <h3 className="text-lg font-bold text-slate-900 mb-4">Analysis Detail</h3>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 italic mb-5 leading-relaxed">
              "{selectedEntry.input_text}"
            </div>

            <div className="grid grid-cols-3 gap-3 mb-5 text-center text-xs">
              <div className="p-3 rounded-xl bg-indigo-50/70 border border-indigo-100">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Emotion</span>
                <span className="font-extrabold text-indigo-900 text-sm mt-0.5 block">{selectedEntry.primary_emotion}</span>
                <span className="text-indigo-600 text-[10px] font-semibold">{Math.round(selectedEntry.emotion_confidence * 100)}%</span>
              </div>
              <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-100">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Stress</span>
                <span className="font-extrabold text-amber-900 text-sm mt-0.5 block">{selectedEntry.stress_level}</span>
                <span className="text-amber-600 text-[10px] font-semibold">{Math.round(selectedEntry.stress_confidence * 100)}%</span>
              </div>
              <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-100">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Wellness</span>
                <span className="font-extrabold text-emerald-900 text-sm mt-0.5 block">{selectedEntry.wellness_score}</span>
                <span className="text-emerald-700 text-[10px] font-semibold">{selectedEntry.wellness_status}</span>
              </div>
            </div>

            {selectedEntry.insight && (
              <div className="mb-4 text-xs text-slate-600 leading-relaxed">
                <strong className="text-slate-800 block mb-1">AI Observation:</strong>
                {selectedEntry.insight}
              </div>
            )}

            <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={() => handleFullResultView(selectedEntry)}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-700 inline-flex items-center gap-1"
              >
                <span>Open in full result view</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setSelectedEntry(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <SafetyDisclaimer />
    </div>
  );
}
