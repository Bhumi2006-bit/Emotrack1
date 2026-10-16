// frontend/src/components/AnalysisLoading.jsx
import React from "react";
import { CheckCircle2, CircleDot, Circle, Loader2, Sparkles } from "lucide-react";

export function AnalysisLoading({ step = 0 }) {
  const pipelineSteps = [
    { title: "Processing language", desc: "Tokenization & contextual sequence parsing" },
    { title: "Detecting emotional patterns", desc: "Evaluating 7-class emotional probabilities" },
    { title: "Estimating stress level", desc: "Analyzing cognitive strain & perceived urgency markers" },
    { title: "Generating wellness insights", desc: "Synthesizing multi-entry stability indicators" },
    { title: "Preparing recommendations", desc: "Context-filtering gentle, supportive next steps" }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-md p-4">
      <div className="bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-md w-full p-8 relative overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Subtle decorative background gradient */}
        <div className="absolute -top-16 -right-16 w-40 h-40 bg-indigo-100 rounded-full blur-3xl opacity-60 pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-40 h-40 bg-violet-100 rounded-full blur-3xl opacity-60 pointer-events-none" />

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-md shadow-indigo-100">
            <Loader2 className="w-5 h-5 animate-spin" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Analyzing your entry...</h3>
            <p className="text-xs text-slate-500">Multi-layer Agentic pipeline in progress</p>
          </div>
        </div>

        {/* Steps List */}
        <div className="space-y-4 relative">
          {/* Vertical connecting line */}
          <div className="absolute left-3.5 top-3 bottom-3 w-0.5 bg-slate-100 -z-0" />

          {pipelineSteps.map((s, idx) => {
            const isCompleted = idx < step;
            const isCurrent = idx === step;
            const isPending = idx > step;

            return (
              <div key={idx} className="flex items-start gap-3.5 relative z-10">
                <div className="mt-0.5">
                  {isCompleted ? (
                    <div className="w-7 h-7 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-xs">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  ) : isCurrent ? (
                    <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-sm shadow-indigo-200 animate-pulse">
                      <CircleDot className="w-4 h-4" />
                    </div>
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center">
                      <Circle className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>

                <div className="flex-1">
                  <p className={`text-sm font-semibold leading-tight ${isCurrent ? "text-indigo-950 font-bold" : (isCompleted ? "text-slate-800" : "text-slate-400")}`}>
                    {s.title}
                  </p>
                  <p className={`text-xs mt-0.5 ${isCurrent ? "text-indigo-600" : "text-slate-400"}`}>
                    {s.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-7 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
          <span>EmoTrack Agentic Pipeline</span>
          <span className="font-semibold text-slate-600">{Math.min(100, Math.round(((step + 1) / 5) * 100))}%</span>
        </div>
      </div>
    </div>
  );
}
