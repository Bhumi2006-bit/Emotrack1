// frontend/src/pages/Landing.jsx
import React from "react";
import { useApp } from "../context/AppContext";
import {
  Sparkles,
  ArrowRight,
  Brain,
  Activity,
  LineChart,
  Lightbulb,
  HeartHandshake,
  CheckCircle2,
  Workflow,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";

export function Landing() {
  const { startDemo, setCurrentPage } = useApp();

  const features = [
    {
      title: "1. Emotion Analysis",
      desc: "Analyze the emotional tone of your thoughts across 7 contextual categories without simplistic keyword rules.",
      icon: Brain,
      color: "text-indigo-600 bg-indigo-50"
    },
    {
      title: "2. Stress Detection",
      desc: "Identify linguistic patterns associated with different levels of perceived cognitive strain and urgency.",
      icon: Activity,
      color: "text-rose-600 bg-rose-50"
    },
    {
      title: "3. Wellness Tracking",
      desc: "Track your wellness indicators over multi-entry time horizons instead of looking at a single isolated moment.",
      icon: LineChart,
      color: "text-emerald-600 bg-emerald-50"
    },
    {
      title: "4. Personalized Recommendations",
      desc: "Receive gentle, context-aware suggestions categorized into calm, academic workload, and restorative routines.",
      icon: HeartHandshake,
      color: "text-amber-600 bg-amber-50"
    },
    {
      title: "5. AI Insights",
      desc: "Discover recurring emotional patterns, work themes, and longitudinal shifts across your written reflections.",
      icon: Lightbulb,
      color: "text-violet-600 bg-violet-50"
    },
    {
      title: "6. Progress Dashboard",
      desc: "Visualize trends, history, and emotional distributions in one calm, non-judgmental workspace.",
      icon: Sparkles,
      color: "text-blue-600 bg-blue-50"
    }
  ];

  const steps = [
    { num: "01", title: "Write", desc: "Share what you're thinking or feeling in your private journal." },
    { num: "02", title: "Analyze", desc: "AI models evaluate emotional and stress-related linguistic patterns." },
    { num: "03", title: "Understand", desc: "View emotions, stress level, wellness indicators, and longitudinal trends." },
    { num: "04", title: "Take Action", desc: "Receive gentle, personalized self-care recommendations for your day." }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#F8FAFC] via-white to-[#F8FAFC] text-slate-800">
      {/* Top Bar for Landing */}
      <header className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-100">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <span className="font-bold text-xl text-slate-900 tracking-tight">EmoTrack</span>
            <span className="block text-[10px] font-semibold text-slate-400 tracking-wider uppercase -mt-1">Wellness Platform</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentPage("login")}
            className="text-sm font-semibold text-slate-600 hover:text-slate-900 px-4 py-2 rounded-xl hover:bg-slate-100 transition-colors"
          >
            Sign In
          </button>
          <button
            onClick={startDemo}
            className="text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-5 py-2.5 rounded-xl shadow-md shadow-indigo-100 transition-all hover:shadow-lg"
          >
            Explore Demo
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-6 pt-12 pb-20 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        {/* Left Column */}
        <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-xs font-semibold text-indigo-700">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Powered Emotional Wellness & Self-Reflection</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
            Understand your emotions. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
              Track your wellness.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-600 max-w-xl mx-auto lg:mx-0 leading-relaxed">
            EmoTrack uses AI-powered emotion and stress analysis to help you understand patterns in your thoughts, monitor your emotional wellness, and receive personalized self-care recommendations.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
            <button
              onClick={() => setCurrentPage("register")}
              className="w-full sm:w-auto px-7 py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-xl shadow-indigo-200 hover:shadow-2xl transition-all flex items-center justify-center gap-2 group"
            >
              <span>Start Your Journey</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={startDemo}
              className="w-full sm:w-auto px-7 py-3.5 rounded-2xl bg-white hover:bg-slate-50 text-slate-800 font-semibold text-sm border border-slate-200/90 shadow-xs hover:border-slate-300 transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-indigo-500" />
              <span>Explore Demo (Instant Access)</span>
            </button>
          </div>

          <div className="pt-2 text-xs text-slate-400 flex items-center justify-center lg:justify-start gap-4">
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Non-diagnostic framing</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Longitudinal patterns</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Agentic AI workflow</span>
          </div>
        </div>

        {/* Right Column: Hero Visual Card (Section 3 of Blueprint) */}
        <div className="lg:col-span-5 flex justify-center">
          <div className="w-full max-w-sm bg-white rounded-3xl p-7 shadow-2xl shadow-indigo-100 border border-slate-100 relative">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Today's Wellness</p>
                <p className="text-sm font-bold text-slate-800">Self-Reflection Indicator</p>
              </div>
              <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
            </div>

            {/* Score & Indicator */}
            <div className="py-6 text-center">
              <div className="text-6xl font-extrabold text-slate-900 tracking-tight">72</div>
              <div className="w-16 h-1 bg-indigo-500 mx-auto my-2.5 rounded-full" />
              <div className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase tracking-wider">
                Balanced
              </div>
            </div>

            {/* Sub-metrics */}
            <div className="grid grid-cols-2 gap-3 p-3.5 rounded-2xl bg-slate-50 border border-slate-100 text-xs">
              <div>
                <p className="text-slate-400 font-medium">Emotion</p>
                <p className="font-bold text-slate-800 text-sm mt-0.5">Joy <span className="text-indigo-600 font-semibold text-xs">82%</span></p>
              </div>
              <div>
                <p className="text-slate-400 font-medium">Stress</p>
                <p className="font-bold text-slate-800 text-sm mt-0.5">Low <span className="text-emerald-600 font-semibold text-xs">18%</span></p>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span className="text-emerald-600 font-bold flex items-center gap-1">
                ↑ 8% from last week
              </span>
              <span>Based on 24 entries</span>
            </div>
          </div>
        </div>
      </section>

      {/* Section 4: Features */}
      <section className="max-w-6xl mx-auto px-6 py-20 border-t border-slate-100">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="text-xs font-bold uppercase tracking-wider text-indigo-600 mb-2">Comprehensive Features</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            One platform. A complete emotional wellness journey.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <div
                key={i}
                className="bg-white p-7 rounded-3xl border border-slate-200/70 shadow-xs hover:shadow-xl hover:border-indigo-100 transition-all duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-5 ${f.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">{f.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Section 5: How It Works */}
      <section className="max-w-6xl mx-auto px-6 py-20 border-t border-slate-100 bg-slate-50/50 rounded-3xl my-10">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="text-xs font-bold uppercase tracking-wider text-indigo-600 mb-2">Simple Reflection Flow</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            How EmoTrack Works
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((st, idx) => (
            <div key={idx} className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs relative">
              <span className="text-3xl font-black text-indigo-100 absolute top-4 right-4">{st.num}</span>
              <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white font-bold text-xs flex items-center justify-center mb-4">
                {st.num}
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1.5">{st.title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{st.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Section 6: AI Pipeline Architecture */}
      <section className="max-w-6xl mx-auto px-6 py-20 border-t border-slate-100">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="text-xs font-bold uppercase tracking-wider text-indigo-600 mb-2">Technical Rigor</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Powered by a Multi-Layer AI Pipeline
          </h2>
          <p className="text-sm text-slate-500 mt-2">
            Structured workflow coordinating fine-tuned Transformer classification, stress evaluation, and LangGraph multi-agent synthesis.
          </p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/80 p-8 shadow-lg max-w-3xl mx-auto text-xs">
          <div className="space-y-4">
            <div className="p-3 bg-slate-50 rounded-xl font-mono text-center font-bold text-slate-700 border border-slate-200">
              USER JOURNAL REFLECTION
            </div>
            <div className="text-center text-slate-400 font-mono">↓</div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 bg-indigo-50/70 border border-indigo-100 rounded-xl text-center">
                <p className="font-bold text-indigo-900">Emotion Model</p>
                <p className="text-[11px] text-indigo-700">7-Class Transformer</p>
              </div>
              <div className="p-3 bg-rose-50/70 border border-rose-100 rounded-xl text-center">
                <p className="font-bold text-rose-900">Stress Classifier</p>
                <p className="text-[11px] text-rose-700">Cognitive Strain & Urgency</p>
              </div>
              <div className="p-3 bg-emerald-50/70 border border-emerald-100 rounded-xl text-center">
                <p className="font-bold text-emerald-900">History & Trend</p>
                <p className="text-[11px] text-emerald-700">Multi-Entry Window (≥ 3)</p>
              </div>
            </div>
            <div className="text-center text-slate-400 font-mono">↓</div>
            <div className="p-3 bg-violet-50/80 border border-violet-200 rounded-xl text-center">
              <p className="font-bold text-violet-950">Wellness Indicator & Trend Engine</p>
              <p className="text-[11px] text-violet-700">Non-Diagnostic Score (0–100) & Pattern Trajectory</p>
            </div>
            <div className="text-center text-slate-400 font-mono">↓</div>
            <div className="p-3 bg-amber-50/80 border border-amber-200 rounded-xl text-center">
              <p className="font-bold text-amber-950">LangGraph Agentic Orchestrator</p>
              <p className="text-[11px] text-amber-700">Planner → Analysis → Insight → Recommendation → Explainer</p>
            </div>
            <div className="text-center text-slate-400 font-mono">↓</div>
            <div className="p-3 bg-slate-900 text-white rounded-xl font-mono text-center font-bold">
              PERSONALIZED RESULT & DASHBOARD
            </div>
          </div>
        </div>
      </section>

      {/* Safety Notice Banner */}
      <section className="max-w-4xl mx-auto px-6 pb-20">
        <SafetyDisclaimer />
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-100 py-8 text-center text-xs text-slate-400">
        <p>© 2026 EmoTrack AI. Built for self-reflection and personal wellness tracking.</p>
      </footer>
    </div>
  );
}
