import React from "react";
import { Info } from "lucide-react";

interface ExplainabilityPanelProps {
  score: number;
  explanation: string;
  breakdown: {
    content: number;
    collaborative: number;
    semantic: number;
    genre: number;
    quality: number;
    popularity: number;
  };
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  score,
  explanation,
  breakdown
}) => {
  // Format percentage contribution
  const formatPercent = (val: number) => {
    return `${Math.round(val * 100)}%`;
  };

  const factors = [
    { key: "content", label: "Content Similarity", colorClass: "content", value: breakdown.content },
    { key: "collaborative", label: "Viewer Patterns", colorClass: "collaborative", value: breakdown.collaborative },
    { key: "semantic", label: "Query Relevancy", colorClass: "semantic", value: breakdown.semantic },
    { key: "genre", label: "Genre Match", colorClass: "genre", value: breakdown.genre },
    { key: "quality", label: "Movie Quality", colorClass: "quality", value: breakdown.quality },
    { key: "popularity", label: "Trending Signal", colorClass: "popularity", value: breakdown.popularity }
  ];

  // Filter factors to show only active signals (value > 0.01)
  const activeFactors = factors.filter((f) => f.value > 0.01);

  return (
    <div className="explain-panel">
      <div className="explain-header">
        <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <Info size={14} />
          Recommendation Factors ({Math.round(score * 100)}% Match)
        </span>
      </div>
      
      <div className="explain-bar-container">
        {activeFactors.map((factor) => (
          <div key={factor.key} className="explain-row">
            <div className="explain-label">{factor.label}</div>
            <div className="explain-track">
              <div 
                className={`explain-fill ${factor.colorClass}`} 
                style={{ width: `${factor.value * 100}%` }}
              ></div>
            </div>
            <div className="explain-percent">{formatPercent(factor.value)}</div>
          </div>
        ))}
      </div>
      
      <p style={{ fontSize: "12px", color: "#f3f4f6", marginTop: "14px", lineHeight: "1.4", borderLeft: "2px solid #e50914", paddingLeft: "8px" }}>
        {explanation}
      </p>
    </div>
  );
};
