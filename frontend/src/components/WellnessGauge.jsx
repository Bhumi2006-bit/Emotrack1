// frontend/src/components/WellnessGauge.jsx
import React from "react";

export function WellnessGauge({ score = 72, status = "Balanced", message, size = 180 }) {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  // Arc calculation for 270 degree gauge or 360 circle
  const progress = Math.min(100, Math.max(0, score));
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  // Color selection based on score/status
  let strokeColor = "#6366F1"; // indigo/balanced
  let badgeColor = "bg-indigo-50 text-indigo-700 border-indigo-200";

  if (score >= 70 || status === "Positive Pattern") {
    strokeColor = "#10B981"; // emerald
    badgeColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (score < 50 || status === "Needs Attention") {
    strokeColor = "#F59E0B"; // amber
    badgeColor = "bg-amber-50 text-amber-700 border-amber-200";
  }

  return (
    <div className="flex flex-col items-center justify-center p-2 text-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#F1F5F9"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Animated Progress Stroke */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Score & Status */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-4xl font-extrabold text-slate-900 tracking-tight">{score}</span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">/ 100</span>
        </div>
      </div>

      <div className="mt-4 flex flex-col items-center">
        <span className={`text-xs font-bold px-3 py-1 rounded-full border ${badgeColor} uppercase tracking-wider`}>
          {status}
        </span>
        {message && (
          <p className="text-xs text-slate-500 mt-2 max-w-xs leading-relaxed">
            {message}
          </p>
        )}
      </div>
    </div>
  );
}
