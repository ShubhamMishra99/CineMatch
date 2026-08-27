import React from "react";
import { X, Check, Info } from "lucide-react";
import type { MovieRecommendation } from "../types";

interface ExplainabilityDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  movie: MovieRecommendation | null;
}

export const ExplainabilityDrawer: React.FC<ExplainabilityDrawerProps> = ({
  isOpen,
  onClose,
  movie
}) => {
  if (!movie) return null;

  const matchPercent = Math.round(movie.score * 100);
  const breakdown = movie.score_breakdown;

  const factors = [
    { key: "content", label: "Your Taste Profile", colorClass: "content", value: breakdown.content },
    { key: "collaborative", label: "Similar Viewer Patterns", colorClass: "collaborative", value: breakdown.collaborative },
    { key: "semantic", label: "Semantic Search Intent", colorClass: "semantic", value: breakdown.semantic },
    { key: "genre", label: "Genre Preference Match", colorClass: "genre", value: breakdown.genre },
    { key: "quality", label: "Movie Quality Factor", colorClass: "quality", value: breakdown.quality },
    { key: "popularity", label: "Trending & Popularity", colorClass: "popularity", value: breakdown.popularity }
  ];

  // Filter factors to show only active signals (value > 0.01)
  const activeFactors = factors.filter((f) => f.value > 0.01);

  return (
    <div className={`drawer-overlay ${isOpen ? "open" : ""}`} onClick={onClose}>
      <div className="drawer-content explainability-scroll" onClick={(e) => e.stopPropagation()}>
        
        {/* Drawer Header */}
        <div className="drawer-header">
          <div>
            <h2 className="drawer-title">Why CineMatch Picked This</h2>
            <p className="drawer-subtitle">{movie.title}</p>
          </div>
          <button className="drawer-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Match Percentage Badge Panel */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "var(--bg-tertiary)", padding: "16px", borderRadius: "12px", border: "1px solid var(--border-glass)" }}>
          <span style={{ fontSize: "14px", fontWeight: "700", color: "var(--text-secondary)" }}>Overall Match Quality</span>
          <span className="movie-card-badge match" style={{ position: "static", fontSize: "14px", padding: "6px 12px" }}>
            {matchPercent}% Match
          </span>
        </div>

        {/* Natural Language Explanation */}
        <div>
          <h3 className="drawer-section-title">Recommendation summary</h3>
          <div className="explain-summary-card">
            {movie.explanation || "This movie matches your preferences based on collaborative signals, genres, and quality."}
          </div>
        </div>

        {/* Signal Weight Contribution */}
        <div>
          <h3 className="drawer-section-title">Signal contribution breakdown</h3>
          <div className="explain-progress-section">
            {activeFactors.map((factor) => (
              <div key={factor.key} className="explain-progress-bar-row">
                <div className="explain-bar-labels">
                  <span>{factor.label}</span>
                  <span>{Math.round(factor.value * 100)}%</span>
                </div>
                <div className="explain-bar-track">
                  <div 
                    className={`explain-bar-fill-bar ${factor.colorClass}`}
                    style={{ width: `${factor.value * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Explainability Checkmarks list */}
        <div>
          <h3 className="drawer-section-title">Preference Alignment Checklist</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {breakdown.genre > 0.05 && (
              <div className="explain-bullet-point">
                <Check className="tick" size={16} />
                <span>Matches your favorite genres ({movie.genres.slice(0, 2).join(" & ")})</span>
              </div>
            )}
            {breakdown.content > 0.05 && (
              <div className="explain-bullet-point">
                <Check className="tick" size={16} />
                <span>Similar in thematic properties to films you liked</span>
              </div>
            )}
            {breakdown.semantic > 0.05 && (
              <div className="explain-bullet-point">
                <Check className="tick" size={16} />
                <span>Corresponds to your natural-language intent request</span>
              </div>
            )}
            {breakdown.collaborative > 0.05 && (
              <div className="explain-bullet-point">
                <Check className="tick" size={16} />
                <span>Favored by viewers with similar movie profiles</span>
              </div>
            )}
            <div className="explain-bullet-point">
              <Check className="tick" size={16} />
              <span>Ranked with Maximal Marginal Relevance for playlist diversity</span>
            </div>
          </div>
        </div>

        {/* Confidence rating */}
        <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "20px", display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "13px", color: "var(--text-secondary)" }}>
          <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Info size={14} /> Recommendation Confidence
          </span>
          <strong style={{ color: "var(--match-green)", textTransform: "uppercase" }}>High</strong>
        </div>

        {/* Drawer Action */}
        <div className="drawer-footer">
          <button className="accent-btn" onClick={onClose} style={{ width: "100%" }}>
            Close factors
          </button>
        </div>
      </div>
    </div>
  );
};
