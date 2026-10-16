// frontend/src/pages/Analyze.jsx
import React, { useState } from "react";
import { useApp } from "../context/AppContext";
import { Sparkles, PenLine, RotateCcw, ArrowRight, ShieldCheck, Heart, MessageSquare, Send, CheckCircle2, HelpCircle } from "lucide-react";
import { DEMO_PRESETS } from "../services/demoData";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";
import { apiStartSession, apiRespondSession, apiFinalizeSession } from "../services/api";

export function Analyze() {
  const { runAnalysis, completeSessionAnalysis, isAnalyzing, isDemoMode, setCurrentPage, leaveDemoForRegistration } = useApp();
  const [text, setText] = useState("");
  const [selectedMood, setSelectedMood] = useState(null);
  
  // Multi-Turn Conversational Session State
  const [activeSession, setActiveSession] = useState(null);
  const [followUpText, setFollowUpText] = useState("");
  const [isSubmittingFollowUp, setIsSubmittingFollowUp] = useState(false);
  const [dialogueTurns, setDialogueTurns] = useState([]);

  const moodPills = [
    { label: "Happy", emoji: "😊" },
    { label: "Okay", emoji: "😐" },
    { label: "Low", emoji: "😔" },
    { label: "Stressed", emoji: "😰" },
    { label: "Frustrated", emoji: "😡" }
  ];

  const handlePresetSelect = (presetText) => {
    setText(presetText);
  };

  const handleStartAnalysis = async (conversational = true) => {
    if (!text.trim() || text.length < 5) {
      alert("Please write at least a sentence before analyzing.");
      return;
    }

    if (!conversational) {
      runAnalysis(text);
      return;
    }

    setIsSubmittingFollowUp(true);
    try {
      const res = await apiStartSession(text);
      if (res.is_completed) {
        completeSessionAnalysis(res);
      } else {
        setActiveSession(res);
        setDialogueTurns([
          {
            turn: 1,
            user: text,
            assistant: res.next_question,
            interpretation: res.initial_interpretation,
            acknowledgment: res.correction_acknowledgment
          }
        ]);
      }
    } catch (e) {
      console.warn("Session start fallback to standard analysis:", e);
      runAnalysis(text);
    } finally {
      setIsSubmittingFollowUp(false);
    }
  };

  const handleSendFollowUp = async () => {
    if (!followUpText.trim() || !activeSession) return;
    setIsSubmittingFollowUp(true);
    try {
      const res = await apiRespondSession(activeSession.session_id, followUpText);
      if (res.is_completed) {
        completeSessionAnalysis(res);
      } else {
        setDialogueTurns(prev => [
          ...prev,
          {
            turn: res.turn_count,
            user: followUpText,
            assistant: res.next_question,
            acknowledgment: res.correction_acknowledgment
          }
        ]);
        setActiveSession(res);
        setFollowUpText("");
      }
    } catch (e) {
      alert("Error responding: " + e.message);
    } finally {
      setIsSubmittingFollowUp(false);
    }
  };

  const handleFinalizeEarly = async () => {
    if (!activeSession) return;
    setIsSubmittingFollowUp(true);
    try {
      const res = await apiFinalizeSession(activeSession.session_id);
      completeSessionAnalysis(res);
    } catch (e) {
      alert("Error finalizing session: " + e.message);
    } finally {
      setIsSubmittingFollowUp(false);
    }
  };

  if (isDemoMode) return <div className="max-w-4xl mx-auto space-y-6 pb-12"><div><h1 className="text-3xl font-extrabold text-slate-900">Sample reflections</h1><p className="text-sm text-slate-500 mt-1">Demo mode is read-only. These examples show the kinds of reflections EmoTrack can analyze.</p></div><div className="space-y-3">{DEMO_PRESETS.map((p) => <div key={p.title} className="bg-white border border-slate-200 rounded-2xl p-5"><p className="font-bold text-slate-800">{p.title}</p><p className="text-sm text-slate-600 italic mt-2">“{p.text}”</p></div>)}</div><button onClick={leaveDemoForRegistration} className="px-5 py-3 rounded-xl bg-indigo-600 text-white font-bold text-sm">Want to analyze your own thoughts? Create an account →</button><SafetyDisclaimer /></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header (Section 15) */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-100 text-xs font-semibold text-brand-700 mb-3">
          <PenLine className="w-3.5 h-3.5" />
          <span>Conversational Self-Reflection Journal</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          How are you feeling today?
        </h1>
        <p className="text-sm sm:text-base text-slate-500 mt-2 max-w-2xl leading-relaxed">
          Write freely. EmoTrack engages in empathetic multi-turn inquiry to clarify nuances, resolve sarcasm, and accurately assess emotional wellness.
        </p>
      </div>

      {/* Main Journal Writing Box (Disabled if session is active in conversation) */}
      {!activeSession ? (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-md shadow-slate-100 relative">
          <textarea
            rows={7}
            value={text}
            onChange={(e) => setText(e.target.value.slice(0, 2000))}
            placeholder="I've been really worried about my exams lately. I know I've prepared but I still feel like something will go wrong..."
            className="w-full text-slate-800 text-base sm:text-lg placeholder:text-slate-300 resize-none outline-none leading-relaxed"
          />

          {/* Bottom bar of textarea */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-slate-100 mt-2">
            {/* Section 16: Optional Mood Selection Context */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-semibold text-slate-400">Context:</span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {moodPills.map((m) => (
                  <button
                    key={m.label}
                    type="button"
                    onClick={() => setSelectedMood(selectedMood === m.label ? null : m.label)}
                    className={`text-xs px-2.5 py-1 rounded-full border transition-all flex items-center gap-1 ${
                      selectedMood === m.label
                        ? "bg-brand-600 text-white border-brand-600 shadow-2xs font-semibold"
                        : "bg-slate-50 hover:bg-slate-100 text-slate-600 border-slate-200"
                    }`}
                  >
                    <span>{m.emoji}</span>
                    <span>{m.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between sm:justify-end gap-3 flex-wrap">
              <span className={`text-xs font-mono font-semibold ${text.length > 1800 ? "text-amber-600" : "text-slate-400"}`}>
                {text.length} / 2000
              </span>

              <button
                type="button"
                onClick={() => handleStartAnalysis(false)}
                disabled={isSubmittingFollowUp || isAnalyzing || text.trim().length === 0}
                className="px-4 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-all"
                title="Immediate single-turn classification without follow-up questions"
              >
                Quick Analyze
              </button>

              <button
                type="button"
                onClick={() => handleStartAnalysis(true)}
                disabled={isSubmittingFollowUp || isAnalyzing || text.trim().length === 0}
                className="px-6 py-3 rounded-2xl bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-bold text-sm shadow-md shadow-brand-100 hover:shadow-lg transition-all flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isSubmittingFollowUp ? "Assessing..." : "Start Reflection"}</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Multi-Turn Conversational Dialogue Container */
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-brand-100 shadow-xl shadow-brand-50/50 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-sm">
                AI
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-base">Conversational Emotional Dialogue</h3>
                <p className="text-xs text-slate-500">Turn {activeSession.turn_count} of 4 max</p>
              </div>
            </div>

            {/* Preliminary Indicators */}
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-brand-50 text-brand-700 border border-brand-200">
                {activeSession.rejected_emotions?.length > 0
                  ? `Reassessing: ${activeSession.preliminary_emotion}`
                  : (activeSession.uncertainty_score > 0.40
                      ? `Exploring: ${activeSession.preliminary_emotion} (${Math.round(activeSession.preliminary_confidence * 100)}%)`
                      : `Preliminary: ${activeSession.preliminary_emotion} (${Math.round(activeSession.preliminary_confidence * 100)}%)`)}
              </span>
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
                {activeSession.preliminary_stress} Stress
              </span>
            </div>
          </div>

          {/* Dialogue History */}
          <div className="space-y-4 max-h-96 overflow-y-auto pr-1">
            {dialogueTurns.map((dt, idx) => (
              <div key={idx} className="space-y-3">
                {/* User Bubble */}
                <div className="flex justify-end">
                  <div className="bg-slate-100 text-slate-800 rounded-2xl rounded-tr-xs px-4 py-3 max-w-lg text-sm">
                    <p className="font-semibold text-[11px] text-slate-400 mb-1">Your reflection (Turn {dt.turn})</p>
                    <p>{dt.user}</p>
                  </div>
                </div>

                {/* Assistant Question Bubble */}
                {(dt.interpretation || dt.acknowledgment || dt.assistant) && (
                  <div className="flex justify-start">
                    <div className="bg-brand-50 text-brand-950 border border-brand-100 rounded-2xl rounded-tl-xs px-4 py-3 max-w-lg text-sm space-y-2">
                      <p className="font-semibold text-[11px] text-brand-600 mb-1 flex items-center gap-1">
                        <MessageSquare className="w-3 h-3" />
                        <span>EmoTrack Clarification</span>
                      </p>
                      {dt.acknowledgment && (
                        <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200/80 text-xs text-amber-900 font-medium leading-relaxed">
                          {dt.acknowledgment}
                        </div>
                      )}
                      {dt.interpretation && (
                        <div className="p-2.5 rounded-xl bg-indigo-50/80 border border-indigo-200/70 text-xs text-indigo-900 leading-relaxed">
                          <span className="font-semibold text-[11px] text-indigo-700 block mb-0.5">Initial Assessment Framing:</span>
                          {dt.interpretation}
                        </div>
                      )}
                      {dt.assistant && (
                        <p className="font-medium text-slate-900 leading-relaxed">{dt.assistant}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Follow-up input box */}
          <div className="pt-2 border-t border-slate-100 space-y-3">
            <textarea
              rows={3}
              value={followUpText}
              onChange={(e) => setFollowUpText(e.target.value)}
              placeholder="Clarify what you mean, add more thoughts, or mention if you were being sarcastic..."
              className="w-full text-slate-800 text-sm placeholder:text-slate-400 p-3.5 rounded-2xl bg-slate-50 border border-slate-200 outline-none focus:border-brand-400 focus:bg-white transition-all resize-none"
            />

            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={handleFinalizeEarly}
                disabled={isSubmittingFollowUp}
                className="px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-semibold transition-all"
              >
                Finish Assessment Now →
              </button>

              <button
                type="button"
                onClick={handleSendFollowUp}
                disabled={isSubmittingFollowUp || !followUpText.trim()}
                className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-brand-100 flex items-center gap-2 transition-all"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{isSubmittingFollowUp ? "Refining..." : "Send Reply"}</span>
              </button>
            </div>
          </div>
        </div>
      )}


      {/* Preset Test Prompts for Quick Demo Testing */}
      <div className="bg-slate-50/80 rounded-2xl p-5 border border-slate-200/70">
        <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
          <span>Quick Demo Test Presets (1-Click Fill)</span>
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {DEMO_PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handlePresetSelect(p.text)}
              className="text-left p-3 rounded-xl bg-white hover:bg-indigo-50/50 border border-slate-200/80 hover:border-indigo-200 transition-all text-xs group"
            >
              <p className="font-bold text-slate-800 group-hover:text-indigo-600 mb-1">{p.title}</p>
              <p className="text-slate-500 line-clamp-2 italic">"{p.text}"</p>
            </button>
          ))}
        </div>
      </div>

      <SafetyDisclaimer />
    </div>
  );
}
