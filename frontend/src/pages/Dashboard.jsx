import React from "react";
import { useApp } from "../context/AppContext";
import { Activity, Brain, Sparkles, BookOpen, Smile, ChevronRight, Flame } from "lucide-react";
import { WellnessGauge } from "../components/WellnessGauge";
import { TrendChart } from "../components/TrendChart";
import { EmotionDonut } from "../components/EmotionDonut";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";

const Metric = ({ label, icon: Icon, value, detail, color }) => (
  <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
    <div className="flex items-center justify-between text-slate-400 mb-2"><span className="text-xs font-semibold uppercase tracking-wider">{label}</span><Icon className={`w-4 h-4 ${color}`} /></div>
    <div className="text-3xl font-extrabold text-slate-900">{value ?? "—"}</div>
    <div className="mt-3 text-xs text-slate-500">{detail}</div>
  </div>
);

export function Dashboard() {
  const { user, dashboardData, setCurrentPage, setCurrentAnalysis, historyList, isDemoMode, leaveDemoForRegistration } = useApp();
  const total = dashboardData?.total_entries ?? 0;
  const hasEntries = total > 0;
  const wellness = dashboardData?.wellness || {};
  const emotion = dashboardData?.emotion || {};
  const stress = dashboardData?.stress || {};
  const trend = dashboardData?.weekly_trend || [];
  const recentList = historyList?.slice(0, 3) || [];
  const streak = dashboardData?.streak_days ?? user?.streak_days ?? 0;
  const firstName = user?.name || "there";

  if (!hasEntries && !isDemoMode) return (
    <div className="max-w-4xl mx-auto py-10 space-y-8">
      <div><h1 className="text-3xl font-extrabold text-slate-900">Welcome, {firstName} 👋</h1><p className="text-slate-500 mt-2">Your wellness journey starts here. You haven't completed your first reflection yet.</p></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Metric label="Wellness" icon={Activity} value="—" detail="After your first reflection" color="text-indigo-500" />
        <Metric label="Emotion" icon={Smile} value="—" detail="After your first reflection" color="text-emerald-500" />
        <Metric label="Stress" icon={Brain} value="—" detail="After your first reflection" color="text-amber-500" />
        <Metric label="Reflections" icon={BookOpen} value="0" detail="No entries yet" color="text-violet-500" />
      </div>
      <div className="p-8 rounded-3xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5">
        <div><h2 className="text-2xl font-bold">Write your first reflection</h2><p className="text-indigo-100 text-sm mt-1">A few honest sentences are enough to begin.</p></div>
        <button onClick={() => setCurrentPage("analyze")} className="px-6 py-3 rounded-xl bg-white text-indigo-700 font-bold text-sm"><Sparkles className="w-4 h-4 inline mr-2" />Write a reflection</button>
      </div>
      <SafetyDisclaimer compact />
    </div>
  );

  return <div className="space-y-8 max-w-7xl mx-auto pb-12">
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div><h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">{isDemoMode ? "Hello there" : `Hello, ${firstName}`} 👋</h1><p className="text-sm text-slate-500 mt-1">{isDemoMode ? "Here's a preview of how EmoTrack works." : "Here's your emotional wellness overview."}</p></div>
      {!isDemoMode && <button onClick={() => setCurrentPage("analyze")} className="px-5 py-3 rounded-2xl bg-indigo-600 text-white font-bold text-sm"><Sparkles className="w-4 h-4 inline mr-2" />Analyze My Thoughts</button>}
    </div>
    {isDemoMode && <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-4 text-sm text-indigo-800">This is read-only sample data. Want to analyze your own thoughts? <button className="font-bold underline" onClick={leaveDemoForRegistration}>Create an account →</button></div>}
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Metric label={isDemoMode ? "Sample Wellness" : "Wellness"} icon={Activity} value={wellness.score} detail={wellness.status || "—"} color="text-indigo-500" />
      <Metric label={isDemoMode ? "Sample Emotion" : "Current Emotion"} icon={Smile} value={emotion.label} detail={emotion.confidence ? `${emotion.confidence}% model confidence` : "—"} color="text-emerald-500" />
      <Metric label="Stress" icon={Brain} value={stress.level} detail={stress.confidence ? `${stress.confidence}% model confidence` : "—"} color="text-amber-500" />
      <Metric label="Reflections" icon={BookOpen} value={total} detail={<span className="inline-flex gap-1 items-center"><Flame className="w-3 h-3 text-amber-500" />{streak ? `${streak}-day streak` : "No streak yet"}</span>} color="text-violet-500" />
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-4 bg-white p-6 rounded-3xl border border-slate-200/80"><h2 className="text-sm font-bold">Wellness Indicator</h2><WellnessGauge score={wellness.score} status={wellness.status} message={wellness.message} size={175}/></div>
      <div className="lg:col-span-8 bg-white p-6 rounded-3xl border border-slate-200/80"><div className="flex justify-between gap-3"><div><h2 className="text-sm font-bold">Wellness Trend</h2><p className="text-xs text-slate-400">Daily average of recent reflections</p></div><button onClick={() => setCurrentPage("trends")} className="text-xs font-bold text-brand-600 hover:text-brand-700">View trends</button></div><TrendChart data={trend} height={180}/>{total < 2 ? <p className="text-xs text-slate-500 pt-3">First reflection recorded — trends will emerge as you add more entries.</p> : wellness.change !== null && <p className="text-xs text-slate-500 pt-3">Wellness shift: <strong className={wellness.change >= 0 ? "text-emerald-600" : "text-rose-600"}>{wellness.change >= 0 ? "+" : ""}{wellness.change} points compared to your previous reflection</strong></p>}</div>
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-5 bg-white p-6 rounded-3xl border border-slate-200/80"><h2 className="text-sm font-bold mb-1">Emotion Distribution</h2><p className="text-xs text-slate-400 mb-5">Across your reflection history</p><EmotionDonut items={dashboardData?.emotion_distribution || []} totalCount={total} size={185}/></div>
      <div className="lg:col-span-7 bg-white p-6 rounded-3xl border border-slate-200/80"><div className="flex justify-between border-b pb-3 mb-4"><div><h2 className="text-sm font-bold">{isDemoMode ? "Sample reflections" : "Recent reflections"}</h2><p className="text-xs text-slate-400">Latest recorded entries</p></div><button onClick={() => setCurrentPage("history")} className="text-xs font-bold text-indigo-600">View all <ChevronRight className="w-3 h-3 inline"/></button></div><div className="space-y-3">{recentList.map(item => <button onClick={() => {setCurrentAnalysis(item); setCurrentPage("result")}} key={item.id} className="w-full text-left p-4 rounded-2xl bg-slate-50 border border-slate-100"><div className="flex justify-between text-xs"><span className="font-bold">{item.primary_emotion} · {item.stress_level} stress</span><span>{item.wellness_score}/100</span></div><p className="text-xs text-slate-600 italic mt-2 truncate">“{item.input_text}”</p></button>)}</div></div>
    </div>
    {isDemoMode ? <div className="p-7 rounded-3xl bg-indigo-600 text-white"><h3 className="text-xl font-bold">Want to analyze your own thoughts?</h3><button onClick={leaveDemoForRegistration} className="mt-3 px-5 py-2.5 bg-white text-indigo-700 rounded-xl font-bold text-sm">Create an account →</button></div> : <div className="p-7 rounded-3xl bg-indigo-600 text-white flex justify-between items-center gap-4"><div><h3 className="text-xl font-bold">How are you feeling right now?</h3><p className="text-indigo-100 text-sm mt-1">Write a reflection whenever you're ready.</p></div><button onClick={() => setCurrentPage("analyze")} className="px-5 py-3 bg-white text-indigo-700 rounded-xl font-bold text-sm">Write a reflection</button></div>}
    <SafetyDisclaimer compact />
  </div>;
}
