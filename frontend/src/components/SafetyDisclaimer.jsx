// frontend/src/components/SafetyDisclaimer.jsx
import React from "react";
import { ShieldCheck, HeartHandshake } from "lucide-react";

export function SafetyDisclaimer({ compact = false }) {
  if (compact) {
    return (
      <div className="flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] text-slate-500 text-center">
        <ShieldCheck className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
        <span>
          <strong>Non-Diagnostic Notice:</strong> EmoTrack is an AI companion for self-reflection and wellness tracking. It is not a clinical medical service.
        </span>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-5 rounded-2xl bg-indigo-50/60 border border-indigo-100 flex items-start gap-3.5 text-xs text-slate-600 leading-relaxed">
      <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center shrink-0 mt-0.5">
        <HeartHandshake className="w-4 h-4" />
      </div>
      <div>
        <p className="font-semibold text-slate-800 text-sm mb-0.5">Mindful Wellness Notice</p>
        <p className="text-slate-600">
          EmoTrack is designed exclusively for self-reflection and personal wellness pattern tracking.
          It does not provide medical diagnoses, clinical assessments, or replace professional mental health care.
          If you are experiencing severe distress, please consult a qualified healthcare professional.
        </p>
      </div>
    </div>
  );
}
