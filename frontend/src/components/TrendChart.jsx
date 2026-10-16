// frontend/src/components/TrendChart.jsx
import React, { useState } from "react";

export function TrendChart({ data = [], height = 190 }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div className="h-44 flex items-center justify-center text-xs text-slate-400">
        Not enough historical data to plot trend yet.
      </div>
    );
  }

  const width = 500;
  const paddingX = 45;
  const paddingY = 28;
  const plotWidth = width - paddingX * 2;
  const plotHeight = height - paddingY * 2;

  // Strict y-axis range: 0 to 100
  const minY = 0;
  const maxY = 100;

  // Single-point edge case: center point to prevent division by zero
  if (data.length === 1) {
    const single = data[0];
    const score = Math.max(0, Math.min(100, single.score ?? 50));
    const cx = width / 2;
    const cy = paddingY + plotHeight - ((score - minY) / (maxY - minY)) * plotHeight;
    const label = single.day || single.date || "Today";

    return (
      <div className="w-full relative select-none">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
          {/* Grid lines */}
          {[100, 75, 50, 25, 0].map((val) => {
            const y = paddingY + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;
            return (
              <g key={val}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={width - paddingX}
                  y2={y}
                  stroke="#F1F5F9"
                  strokeDasharray="4 4"
                  strokeWidth="1"
                />
                <text
                  x={paddingX - 10}
                  y={y + 3}
                  textAnchor="end"
                  className="text-[10px] fill-slate-300 font-mono font-medium"
                >
                  {val}
                </text>
              </g>
            );
          })}
          {/* Single point */}
          <circle
            cx={cx}
            cy={cy}
            r={6}
            className="fill-brand-600 stroke-white stroke-2 shadow-lg"
          />
          <text
            x={cx}
            y={cy - 12}
            textAnchor="middle"
            className="text-xs font-bold fill-brand-700"
          >
            {score}
          </text>
          <text
            x={cx}
            y={height - 8}
            textAnchor="middle"
            className="text-[11px] font-medium fill-slate-500"
          >
            {label} (First entry recorded)
          </text>
        </svg>
      </div>
    );
  }

  // Multi-point coordinates (safely guarded against zero-division)
  const points = data.map((d, i) => {
    const score = Math.max(0, Math.min(100, d.score ?? 50));
    const x = paddingX + (i / (data.length - 1)) * plotWidth;
    const y = paddingY + plotHeight - ((score - minY) / (maxY - minY)) * plotHeight;
    return { x, y, score, label: d.day || d.date || `Entry ${i + 1}` };
  });

  // Smooth bezier curve path
  const pathD = points.reduce((acc, curr, i, arr) => {
    if (i === 0) return `M ${curr.x} ${curr.y}`;
    const prev = arr[i - 1];
    const cpX = (prev.x + curr.x) / 2;
    return `${acc} C ${cpX} ${prev.y}, ${cpX} ${curr.y}, ${curr.x} ${curr.y}`;
  }, "");

  const areaD = `${pathD} L ${points[points.length - 1].x} ${height - paddingY} L ${points[0].x} ${height - paddingY} Z`;

  // Responsive tick decimation logic
  const shouldShowLabel = (idx) => {
    if (points.length <= 7) return true;
    if (points.length <= 14) return idx % 2 === 0 || idx === points.length - 1;
    if (points.length <= 31) return idx % 5 === 0 || idx === points.length - 1;
    return idx % 10 === 0 || idx === points.length - 1;
  };

  return (
    <div className="w-full relative select-none">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
        <defs>
          <linearGradient id="trendMauveGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#a8397a" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#a8397a" stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Grid lines: 0, 25, 50, 75, 100 */}
        {[100, 75, 50, 25, 0].map((val) => {
          const y = paddingY + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;
          return (
            <g key={val}>
              <line
                x1={paddingX}
                y1={y}
                x2={width - paddingX}
                y2={y}
                stroke="#F1F5F9"
                strokeDasharray="4 4"
                strokeWidth="1"
              />
              <text
                x={paddingX - 10}
                y={y + 3}
                textAnchor="end"
                className="text-[10px] fill-slate-300 font-mono font-medium"
              >
                {val}
              </text>
            </g>
          );
        })}

        {/* Area fill */}
        <path d={areaD} fill="url(#trendMauveGradient)" />

        {/* Smooth line */}
        <path
          d={pathD}
          fill="none"
          stroke="#a8397a"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {points.map((p, idx) => {
          const isHovered = hoveredIndex === idx;
          const showLabel = shouldShowLabel(idx);

          return (
            <g
              key={idx}
              className="cursor-pointer transition-all"
              onMouseEnter={() => setHoveredIndex(idx)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Invisible larger hover target */}
              <circle cx={p.x} cy={p.y} r={14} fill="transparent" />

              {/* Visible dot */}
              <circle
                cx={p.x}
                cy={p.y}
                r={isHovered ? 6 : 4}
                className={`transition-all duration-150 ${
                  isHovered
                    ? "fill-[#a8397a] stroke-white stroke-2 shadow-lg"
                    : "fill-white stroke-[#a8397a] stroke-2"
                }`}
              />

              {/* Decimated date labels */}
              {showLabel && (
                <text
                  x={p.x}
                  y={height - 8}
                  textAnchor="middle"
                  className={`text-[10px] font-medium transition-colors ${
                    isHovered ? "fill-[#a8397a] font-bold" : "fill-slate-400"
                  }`}
                >
                  {p.label}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Floating Tooltip */}
      {hoveredIndex !== null && (
        <div
          className="absolute bg-slate-900 text-white text-xs px-3 py-1.5 rounded-xl shadow-xl pointer-events-none transform -translate-x-1/2 -translate-y-full mb-3 transition-all z-10"
          style={{
            left: `${(points[hoveredIndex].x / width) * 100}%`,
            top: `${(points[hoveredIndex].y / height) * 100}%`
          }}
        >
          <div className="font-medium text-slate-300 text-[10px]">{points[hoveredIndex].label}</div>
          <div className="font-bold text-white text-sm">
            Wellness: {points[hoveredIndex].score}
            <span className="text-[10px] text-slate-400 font-normal"> / 100</span>
          </div>
        </div>
      )}
    </div>
  );
}
