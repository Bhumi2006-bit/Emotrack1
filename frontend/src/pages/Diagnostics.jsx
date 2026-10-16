// frontend/src/pages/Diagnostics.jsx
/**
 * Standalone Developer Diagnostics & Model Audit View
 * Completely isolated from normal user experience.
 * Used exclusively for grading, thesis defense, and technical evaluation.
 */
import React from "react";
import { useApp } from "../context/AppContext";
import { Brain, ArrowLeft, ShieldAlert } from "lucide-react";

export function Diagnostics() {
  const { currentAnalysis, setCurrentPage } = useApp();

  if (!currentAnalysis) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center space-y-4">
        <h2 className="text-xl font-bold text-slate-800">Developer Diagnostics</h2>
        <p className="text-sm text-slate-500">No active analysis session loaded for diagnostics inspection.</p>
        <button
          onClick={() => setCurrentPage("analyze")}
          className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold"
        >
          Perform an Analysis First
        </button>
      </div>
    );
  }

  const emotion = currentAnalysis.emotion || {
    label: currentAnalysis.primary_emotion || "Neutral",
    confidence: currentAnalysis.emotion_confidence || 0.85
  };

  const trace = currentAnalysis.execution_trace || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentPage("result")}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Normal Results</span>
        </button>
        <span className="text-xs font-mono font-bold text-purple-700 bg-purple-50 border border-purple-200 px-3 py-1 rounded-full">
          Internal Evaluation Mode
        </span>
      </div>

      <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5 text-purple-700 font-bold text-base">
          <Brain className="w-5 h-5 text-purple-600" />
          <span>Model Architecture & Calibration Audit</span>
        </div>
        <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs font-mono text-slate-600 space-y-2">
          <p><strong>Emotion Classifier:</strong> Weighted Soft-Voting Ensemble (RoBERTa + 1D CNN [0.45], BERT-base [0.35], Hartmann DistilRoBERTa [0.20])</p>
          <p><strong>Calibration:</strong> Temperature Scaling T=1.25 on softmax logits</p>
          <p><strong>Stress Classifier:</strong> Supervised TF-IDF + Logistic Regression trained on Dreaddit Reddit Dataset</p>
          <p><strong>Attribution Method:</strong> Feature Occlusion Attribution Sensitivity (Marginal probability delta upon token removal)</p>
          <p><strong>Target Class:</strong> {emotion.label} (Marginal Confidence: {Math.round((emotion.confidence || 0.5) * 100)}%)</p>
        </div>
      </div>

      {trace.length > 0 && (
        <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">
              Agentic Orchestrator Execution Log ({trace.length} steps)
            </h3>
            <span className="font-mono text-xs text-slate-400">Deterministic Bounded Loop</span>
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {trace.map((tr, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 font-mono text-xs space-y-1">
                <div className="flex justify-between text-indigo-700 font-bold">
                  <span>[{tr.agent_name || "Agent"}] {tr.action_type}</span>
                  <span className="text-slate-400 font-normal">
                    {new Date((tr.timestamp || 0) * 1000).toLocaleTimeString()}
                  </span>
                </div>
                {tr.thought && <p className="text-slate-600 font-sans italic text-xs">💭 {tr.thought}</p>}
                {tr.details && (
                  <p className="text-slate-500 text-[11px] break-all">
                    {JSON.stringify(tr.details)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
