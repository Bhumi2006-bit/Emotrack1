// frontend/src/components/EmotionDonut.jsx
import React, { useState } from "react";

export function EmotionDonut({ items = [], totalCount = null, size = 190 }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);

  if (!items || items.length === 0) {
    return (
      <div className="h-44 flex items-center justify-center text-xs text-slate-400 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
        No reflection observations recorded yet.
      </div>
    );
  }

  const strokeWidth = 24;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  
  // Calculate total reflections represented if totalCount is provided or infer from items
  const totalReflections = totalCount !== null 
    ? totalCount 
    : items.reduce((acc, it) => acc + (it.count || 0), 0);

  let cumulativePercent = 0;

  // Active item info
  const activeItem = hoveredIdx !== null ? items[hoveredIdx] : null;
  const activeItemCount = activeItem
    ? (activeItem.count !== undefined 
        ? activeItem.count 
        : (totalReflections > 0 ? Math.round((activeItem.percentage / 100) * totalReflections) : null))
    : null;

  const isSingleItem = items.length === 1;

  return (
    <div className="flex flex-col sm:flex-row items-center justify-center gap-6 select-none p-2 overflow-visible">
      {/* SVG Donut */}
      <div className="relative group shrink-0 overflow-visible" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90 overflow-visible">
          {items.map((item, idx) => {
            const pct = Math.max(0, item.percentage || 0);
            const strokeDasharray = `${(pct / 100) * circumference} ${circumference}`;
            const strokeDashoffset = -((cumulativePercent / 100) * circumference);
            cumulativePercent += pct;

            const isHovered = hoveredIdx === idx;
            const isAnyHovered = hoveredIdx !== null;
            const strokeColor = item.color || "#64748B";

            return (
              <circle
                key={idx}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="transparent"
                stroke={strokeColor}
                strokeWidth={isHovered ? strokeWidth + 4 : strokeWidth}
                strokeDasharray={strokeDasharray}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap={isSingleItem || pct >= 99.5 ? "butt" : "round"}
                className="transition-all duration-200 cursor-pointer"
                style={{
                  opacity: isAnyHovered ? (isHovered ? 1.0 : 0.40) : 0.95,
                  filter: isHovered ? "drop-shadow(0 4px 8px rgba(0,0,0,0.18))" : "none"
                }}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              />
            );
          })}
        </svg>

        {/* Dynamic Center Label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center px-3 z-10">
          {activeItem ? (
            <div className="animate-in fade-in zoom-in-95 duration-150">
              <span className="text-2xl font-black text-slate-900 block leading-tight">
                {activeItem.percentage}%
              </span>
              <span 
                className="text-[11px] font-bold uppercase tracking-wider block truncate max-w-[110px]"
                style={{ color: activeItem.color || "#64748B" }}
              >
                {activeItem.emotion}
              </span>
              {activeItemCount !== null && (
                <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">
                  {activeItemCount} {activeItemCount === 1 ? "entry" : "entries"}
                </span>
              )}
            </div>
          ) : (
            <div>
              <span className="text-2xl font-extrabold text-slate-800 block leading-tight">
                {totalReflections > 0 ? totalReflections : items.length}
              </span>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                {totalReflections > 0 ? (totalReflections === 1 ? "Reflection" : "Reflections") : "Emotions"}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Interactive Legend */}
      <div className="grid grid-cols-2 gap-x-3 gap-y-2 text-xs w-full max-w-xs">
        {items.map((item, idx) => {
          const isHovered = hoveredIdx === idx;
          const countDisplay = item.count !== undefined 
            ? item.count 
            : (totalReflections > 0 ? Math.round((item.percentage / 100) * totalReflections) : null);

          return (
            <div
              key={idx}
              className={`flex items-center justify-between p-2 rounded-xl cursor-pointer transition-all border ${
                isHovered
                  ? "bg-slate-50 border-slate-300 shadow-xs scale-[1.02]"
                  : "bg-white/60 border-slate-100/80 hover:bg-slate-50/80"
              }`}
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
            >
              <div className="flex items-center gap-2 truncate pr-1">
                <span
                  className="w-2.5 h-2.5 rounded-full shrink-0 transition-transform"
                  style={{
                    backgroundColor: item.color || "#64748B",
                    transform: isHovered ? "scale(1.25)" : "scale(1)"
                  }}
                />
                <span className={`truncate font-medium ${isHovered ? "text-slate-900 font-bold" : "text-slate-600"}`}>
                  {item.emotion}
                </span>
              </div>
              <div className="text-right shrink-0">
                <span className="font-mono font-bold text-slate-700 text-[11px]">
                  {item.percentage}%
                </span>
                {countDisplay !== null && (
                  <span className="block text-[10px] text-slate-400 font-normal">
                    {countDisplay} {countDisplay === 1 ? "entry" : "entries"}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
