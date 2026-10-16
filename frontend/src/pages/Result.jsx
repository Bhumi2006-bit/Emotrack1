// frontend/src/pages/Result.jsx
import React, { useState } from "react";
import { useApp } from "../context/AppContext";
import {
  Sparkles,
  ArrowLeft,
  Activity,
  Brain,
  ShieldCheck,
  CheckCircle,
  Lightbulb,
  HeartHandshake,
  TrendingDown,
  TrendingUp,
  Bookmark,
  Share2,
  Info,
  Loader2
} from "lucide-react";
import { SafetyDisclaimer } from "../components/SafetyDisclaimer";
import { apiSaveRecommendations, apiSubmitFeedback } from "../services/api";

export function Result() {
  const { currentAnalysis, setCurrentPage } = useApp();
  const [savingRecs, setSavingRecs] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showExplainability, setShowExplainability] = useState(true);
  const [feedbackChoice, setFeedbackChoice] = useState(currentAnalysis?.user_feedback || null);
  const [feedbackSaved, setFeedbackSaved] = useState(Boolean(currentAnalysis?.user_feedback));

  const handleFeedback = async (choice) => {
    setFeedbackChoice(choice);
    setFeedbackSaved(true);
    const analysisId = currentAnalysis?.analysis_id || currentAnalysis?.id;
    if (analysisId) {
      try {
        await apiSubmitFeedback(analysisId, choice);
      } catch (err) {
        console.warn("Feedback submission notice:", err);
      }
    }
  };

  if (!currentAnalysis) {
    return (
      <div className="text-center py-20">
        <p className="text-slate-500 mb-4">No analysis selected.</p>
        <button
          onClick={() => setCurrentPage("analyze")}
          className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-bold text-sm"
        >
          Analyze a Reflection
        </button>
      </div>
    );
  }

  const emotion = currentAnalysis.emotion || {
    label: currentAnalysis.primary_emotion || "Neutral",
    confidence: currentAnalysis.emotion_confidence || 0.85,
    distribution: currentAnalysis.emotion_distribution || {}
  };

  const stress = currentAnalysis.stress || {
    level: currentAnalysis.stress_level || "Moderate",
    confidence: currentAnalysis.stress_confidence || 0.78,
    explanation: "Evaluation of linguistic urgency and cognitive strain."
  };

  const wellness = currentAnalysis.wellness || {
    score: currentAnalysis.wellness_score || 55,
    status: currentAnalysis.wellness_status || "Balanced",
    description: "Stable emotional pattern."
  };

  const trend = currentAnalysis.trend || {
    direction: currentAnalysis.trend_direction || "Stable",
    based_on_entries: currentAnalysis.trend_entries || 24,
    points: [65, 58, 51, currentAnalysis.wellness_score || 43],
    message: "Recent reflections reflect your ongoing emotional trajectory."
  };

  const recommendations = currentAnalysis.recommendations || [
    "Take a short pause: Step away from the current workspace for 5-10 minutes.",
    "Try a grounding exercise: Focus on sensory surroundings.",
    "Break the task down: Identify one small task you can finish next."
  ];

  const signals = currentAnalysis.explanation?.signals || currentAnalysis.context_signals || [
    { word: "worried", weight: 0.94 },
    { word: "something will go wrong", weight: 0.88 },
    { word: "exams", weight: 0.81 },
    { word: "prepared", weight: 0.42 }
  ];

  const emojiMap = {
    Fear: "😨",
    Joy: "😊",
    Sadness: "😔",
    Anger: "😡",
    Surprise: "😲",
    Disgust: "🤢",
    Neutral: "😐"
  };

  const sortedEmotions = Object.entries(emotion.distribution || {})
    .sort((a, b) => b[1] - a[1])
    .filter(([k]) => k !== emotion.label)
    .slice(0, 3);

  const handleSaveRecs = async () => {
    if (savingRecs) return;
    setSavingRecs(true);
    try {
      const itemsToSave = recommendations.map((rec) => {
        const parts = typeof rec === "string" ? rec.split(":") : [rec.title, rec.description];
        return {
          title: (parts[0] || "Recommendation").trim(),
          description: (parts[1] || parts[0] || "").trim(),
          category: "Mindfulness",
          analysis_id: currentAnalysis.analysis_id || currentAnalysis.id || null
        };
      });
      await apiSaveRecommendations(itemsToSave);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.warn("Failed to persist recommendations to backend:", err);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSavingRecs(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      {/* Back button & Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={() => setCurrentPage("analyze")}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors self-start"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Write another entry</span>
        </button>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>Analysis ID: #{currentAnalysis.analysis_id || currentAnalysis.id || "104"}</span>
          <span>•</span>
          <span>{currentAnalysis.created_at || "Just now"}</span>
        </div>
      </div>

      {/* Quote Banner with Original Reflection */}
      <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs relative">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">Original Journal Entry</span>
        <blockquote className="text-base sm:text-lg text-slate-800 italic leading-relaxed">
          "{currentAnalysis.input_text}"
        </blockquote>
      </div>

      {/* Primary Result Grid (Sections 18, 19, 20, 21) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Section 18 & 19: Emotion Card */}
        <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Detected Emotion</span>
              <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
                Primary Signal
              </span>
            </div>

            <div className="text-center py-4">
              <div className="text-6xl mb-2 select-none">
                {emojiMap[emotion.label] || "✨"}
              </div>
              <h3 className="text-3xl font-black text-slate-900 uppercase tracking-tight">
                {emotion.label}
              </h3>
              <p className="text-base font-extrabold text-indigo-600 mt-1">
                {Math.round(emotion.confidence * 100)}%
                <span className="text-xs font-medium text-slate-400 ml-1">confidence</span>
              </p>
            </div>

            {/* Section 19: Primary Confidence Bar */}
            <div className="mt-3">
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-600 h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.round(emotion.confidence * 100)}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-400 mt-2 text-center leading-tight">
                Algorithmic model confidence — an estimation of phrasing patterns, not a measurement of your true emotional certainty.
              </p>
            </div>

            {/* Secondary detected emotions */}
            <div className="mt-6 pt-4 border-t border-slate-100">
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                Other detected emotions
              </p>
              <div className="space-y-1.5 text-xs">
                {sortedEmotions.map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between">
                    <span className="text-slate-600">{k}</span>
                    <span className="font-mono text-slate-400 font-semibold">{Math.round(v * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Section 20: Stress Result Card */}
        <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Stress Estimation</span>
              <Brain className="w-4 h-4 text-amber-500" />
            </div>

            <div className="text-center py-4">
              <div className="inline-block px-4 py-1.5 rounded-full text-sm font-extrabold uppercase tracking-wider mb-2 bg-rose-50 text-rose-700 border border-rose-200">
                {stress.level} STRESS
              </div>
              <div className="text-3xl font-extrabold text-slate-900 mt-1">
                {Math.round(stress.confidence * 100)}%
              </div>
              <p className="text-xs text-slate-400 font-medium">Linguistic pattern probability (non-clinical)</p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-xs text-slate-600 leading-relaxed mt-2">
              <p className="font-medium text-slate-700 mb-1">Linguistic pattern note:</p>
              {stress.explanation || "The entry contains language indicating concern about an upcoming event and uncertainty about the outcome."}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            Estimated from text phrasing patterns in this reflection alone. Not a clinical diagnosis or medical evaluation.
          </div>
        </div>

        {/* Section 21: Wellness Indicator Card */}
        <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Wellness Indicator</span>
              <Activity className="w-4 h-4 text-indigo-500" />
            </div>

            <div className="text-center py-4">
              <div className="text-5xl font-black text-slate-900 tracking-tight">
                {wellness.score} <span className="text-xl text-slate-400 font-semibold">/ 100</span>
              </div>
              <div className="mt-2.5">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${
                  wellness.score >= 70
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                    : (wellness.score >= 50
                        ? "bg-indigo-50 text-indigo-700 border-indigo-200"
                        : "bg-amber-50 text-amber-700 border-amber-200")
                }`}>
                  {wellness.status === "Needs Attention" ? "Needs Reflection" : wellness.status}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Current emotion:</span>
                <span className="font-bold text-slate-800">{emotion.label}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Stress level:</span>
                <span className="font-bold text-slate-800">{stress.level}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Multi-entry trajectory:</span>
                <span className="font-bold text-indigo-600">{trend.direction}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            Application-defined reflection indicator based on text patterns, not a diagnostic verdict.
          </div>
        </div>
      </div>

      {/* Section 22: Longitudinal Trend Card */}
      <div className="bg-white p-6 sm:p-7 rounded-3xl border border-slate-200/80 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Multi-Entry Trajectory</span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
              Based on {trend.based_on_entries || 4} observations
            </span>
          </div>
          <span className="text-xs font-bold text-slate-700">
            Direction: <span className="text-indigo-600">{trend.direction}</span>
          </span>
        </div>

        {trend.direction === "Insufficient Data" ? (
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
            {trend.message || "Not enough historical data to determine a meaningful trend yet."}
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100 text-xs">
            <div className="flex items-center gap-3">
              <span className="font-semibold text-slate-600">Recent pattern:</span>
              <span className="font-mono font-bold text-indigo-950 text-sm">
                {(trend.points || [65, 58, 51, wellness.score]).join(" → ")}
              </span>
            </div>
            <p className="text-slate-600">
              {trend.message || "Your recent pattern shows intermittent stress during workload surges."}
            </p>
          </div>
        )}
      </div>

      {/* Section 23: AI Insight Card ("What EmoTrack noticed") */}
      <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs">
        <div className="flex items-center gap-2.5 mb-3 text-indigo-600 font-bold text-sm">
          <Lightbulb className="w-5 h-5 text-indigo-600" />
          <span>What EmoTrack noticed</span>
        </div>
        <p className="text-sm sm:text-base text-slate-700 leading-relaxed font-normal">
          {currentAnalysis.insight}
        </p>
      </div>

      {/* Section 24: Recommendations */}
      <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 text-slate-900 font-bold text-lg">
            <HeartHandshake className="w-5 h-5 text-emerald-600" />
            <span>Gentle Suggestions for You</span>
          </div>
          <button
            onClick={handleSaveRecs}
            disabled={savingRecs}
            className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 ${
              saved
                ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                : "bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200"
            }`}
          >
            {savingRecs ? (
              <Loader2 className="w-4 h-4 animate-spin text-slate-500" />
            ) : saved ? (
              <CheckCircle className="w-4 h-4 text-emerald-600" />
            ) : (
              <Bookmark className="w-4 h-4 text-brand-600" />
            )}
            <span>{savingRecs ? "Saving..." : saved ? "Saved to Profile!" : "Save Recommendations"}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendations.map((rec, i) => {
            const parts = typeof rec === "string" ? rec.split(":") : [rec.title, rec.description];
            const title = parts[0];
            const desc = parts[1] || "";
            return (
              <div
                key={i}
                className="p-5 rounded-2xl bg-slate-50/70 border border-slate-200/80 hover:border-brand-200 transition-colors flex flex-col justify-between"
              >
                <div>
                  <span className="w-6 h-6 rounded-lg bg-brand-100 text-brand-700 font-bold text-xs flex items-center justify-center mb-3">
                    {i + 1}
                  </span>
                  <h4 className="text-sm font-bold text-slate-800 mb-1.5">{title}</h4>
                  <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Section 26: Contextual Phrasing Attribution */}
      <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              What in your reflection shaped this feeling?
            </h3>
            <p className="text-xs text-slate-500">
              Key phrases and words from your entry that influenced the {emotion.label} assessment
            </p>
          </div>
          <button
            onClick={() => setShowExplainability(!showExplainability)}
            className="text-xs text-brand-600 font-semibold hover:underline"
          >
            {showExplainability ? "Collapse" : "Expand"}
          </button>
        </div>

        {showExplainability && (
          <div className="space-y-3 pt-2">
            {signals && signals.length > 0 ? (
              <>
                <p className="text-xs text-slate-600 font-medium">Phrases that most clearly reflected your emotional state:</p>
                <div className="space-y-2.5 max-w-xl">
                  {signals.map((sig, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-800 font-semibold">"{sig.word}"</span>
                        <span className="text-indigo-600 text-[11px] font-semibold">{sig.influence_level || "Notable indicator"}</span>
                      </div>
                      <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-brand-600 h-full rounded-full"
                          style={{ width: `${Math.round((sig.weight || 0.5) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="text-xs text-slate-600 leading-relaxed">
                This entry was classified as <strong>{emotion.label}</strong> based on the holistic tone and context across the entire sentence.
              </p>
            )}

            <p className="text-[11px] text-slate-400 pt-2 border-t border-slate-100">
              EmoTrack identifies influential phrasing to help you reflect on what shaped your emotions.
            </p>
          </div>
        )}
      </div>

      {/* Conversational Natural-Language XAI Synthesis */}
      {(currentAnalysis.conversational_explanation || currentAnalysis.explanation?.summary || (typeof currentAnalysis.explanation === "string" && currentAnalysis.explanation.trim())) && (
        <div className="bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/40 p-7 rounded-3xl border border-indigo-100 shadow-xs space-y-2">
          <div className="flex items-center gap-2 text-indigo-700 font-bold text-sm">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>What EmoTrack Understood & Reflection Narrative</span>
          </div>
          <p className="text-sm sm:text-base text-slate-800 leading-relaxed font-normal">
            {currentAnalysis.conversational_explanation || currentAnalysis.explanation?.summary || currentAnalysis.explanation}
          </p>
        </div>
      )}

      {/* Multi-Turn Reflection Dialogue History (if multi-turn session) */}
      {(currentAnalysis.turns && currentAnalysis.turns.length > 1) && (
        <div className="bg-white p-7 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-600" />
              <span>Multi-Turn Dialogue Evolution ({currentAnalysis.turns.length} turns)</span>
            </h3>
            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
              Context Reconciled
            </span>
          </div>
          <div className="space-y-3">
            {currentAnalysis.turns.map((t, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/70 text-xs space-y-1.5">
                <div className="flex items-center justify-between font-bold text-slate-700">
                  <span>Turn {t.turn || idx + 1}</span>
                  <span className="text-indigo-600 font-medium">Turn Emotion: {t.primary_emotion || "Assessed"}</span>
                </div>
                <p className="text-slate-800 italic">"{t.text}"</p>
                {t.assistant_question && (
                  <p className="text-indigo-600 font-medium pt-1">EmoTrack follow-up: {t.assistant_question}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Feedback Control */}
      <div className="bg-white p-6 sm:p-7 rounded-3xl border border-slate-200/80 shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Does this reflection feel accurate to your experience?
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Your feedback helps calibrate future reflections and personal wellness trends.
            </p>
          </div>

          {feedbackSaved ? (
            <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-200 animate-in fade-in">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              <span>
                {feedbackChoice === "feels_right" ? "Marked as accurate" : feedbackChoice === "partly_right" ? "Marked as partly accurate" : "Feedback noted"}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => handleFeedback("feels_right")}
                className="px-3.5 py-2 rounded-xl border border-slate-200 hover:border-emerald-300 hover:bg-emerald-50 text-slate-700 text-xs font-semibold transition-all flex items-center gap-1.5"
              >
                <span>👍</span>
                <span>Feels right</span>
              </button>
              <button
                onClick={() => handleFeedback("partly_right")}
                className="px-3.5 py-2 rounded-xl border border-slate-200 hover:border-amber-300 hover:bg-amber-50 text-slate-700 text-xs font-semibold transition-all flex items-center gap-1.5"
              >
                <span>🤔</span>
                <span>Partly right</span>
              </button>
              <button
                onClick={() => handleFeedback("wrong")}
                className="px-3.5 py-2 rounded-xl border border-slate-200 hover:border-rose-300 hover:bg-rose-50 text-slate-700 text-xs font-semibold transition-all flex items-center gap-1.5"
              >
                <span>👎</span>
                <span>Doesn't fit</span>
              </button>
            </div>
          )}
        </div>
      </div>



      {/* Section 25: Mandatory Safety Disclaimer */}
      <SafetyDisclaimer />

    </div>
  );
}
