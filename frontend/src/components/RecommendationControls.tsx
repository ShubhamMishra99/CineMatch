import React from "react";
import { X, RefreshCcw, Heart, ThumbsDown, Bookmark } from "lucide-react";

interface RecommendationControlsProps {
  isOpen: boolean;
  onClose: () => void;
  diversityMode: string;
  setDiversityMode: (mode: string) => void;
  favoriteGenres: string[];
  onToggleGenre: (genre: string) => void;
  onResetProfile: () => void;
  isColdStart: boolean;
  setIsColdStart: (isColdStart: boolean) => void;
  likedCount: number;
  dislikedCount: number;
  savedCount: number;
}

const ALL_GENRES = [
  "Action", "Adventure", "Animation", "Comedy", "Crime", 
  "Drama", "Fantasy", "Horror", "Mystery", "Romance", 
  "Science Fiction", "Thriller"
];

export const RecommendationControls: React.FC<RecommendationControlsProps> = ({
  isOpen,
  onClose,
  diversityMode,
  setDiversityMode,
  favoriteGenres,
  onToggleGenre,
  onResetProfile,
  isColdStart,
  setIsColdStart,
  likedCount,
  dislikedCount,
  savedCount
}) => {
  const discoveryStyles = [
    { id: "focused", name: "Focused", desc: "Highest relevance, similar patterns", icon: "🎯" },
    { id: "balanced", name: "Balanced", desc: "Balanced relevance & discovery", icon: "⚖️" },
    { id: "exploratory", name: "Exploratory", desc: "Unexpected variety & diversity", icon: "🚀" }
  ];

  return (
    <div className={`drawer-overlay ${isOpen ? "open" : ""}`} onClick={onClose}>
      <div className="drawer-content" onClick={(e) => e.stopPropagation()}>
        {/* Drawer Header */}
        <div className="drawer-header">
          <div>
            <h2 className="drawer-title">Tune recommendations</h2>
            <p className="drawer-subtitle">Personalize candidate ranking & diversity filters</p>
          </div>
          <button className="drawer-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Discovery Style */}
        <div>
          <h3 className="drawer-section-title">Discovery Style</h3>
          <div className="discovery-styles-grid">
            {discoveryStyles.map((style) => {
              const isSelected = diversityMode === style.id;
              return (
                <div 
                  key={style.id}
                  className={`discovery-style-option ${isSelected ? "selected" : ""}`}
                  onClick={() => setDiversityMode(style.id)}
                >
                  <span style={{ fontSize: "20px" }}>{style.icon}</span>
                  <span className="style-name">{style.name}</span>
                  <span className="style-desc">{style.desc}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Genre Filters */}
        <div>
          <h3 className="drawer-section-title">Filter Genres</h3>
          <div className="drawer-genres-flex">
            {ALL_GENRES.map((g) => {
              const isSelected = favoriteGenres.includes(g);
              return (
                <div 
                  key={g} 
                  className={`drawer-genre-bubble ${isSelected ? "selected" : ""}`}
                  onClick={() => onToggleGenre(g)}
                >
                  {g}
                </div>
              );
            })}
          </div>
        </div>

        {/* Profiles / Advanced Settings */}
        <div>
          <h3 className="drawer-section-title">Engine Profile</h3>
          
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Cold Start Selector */}
            <div style={{ display: "flex", alignItems: "center", justifyItems: "center", justifyContent: "space-between" }}>
              <div>
                <span style={{ fontSize: "14px", fontWeight: "700", display: "block" }}>Cold Profile Mode</span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>Reset onboarding liked list weights</span>
              </div>
              <input 
                type="checkbox" 
                checked={isColdStart}
                onChange={(e) => setIsColdStart(e.target.checked)}
                style={{ width: "18px", height: "18px", cursor: "pointer", accentColor: "var(--accent-primary)" }}
              />
            </div>
            
            {/* Reset taste profile */}
            <div style={{ display: "flex", alignItems: "center", justifyItems: "center", justifyContent: "space-between", borderTop: "1px solid var(--border-glass)", paddingTop: "16px" }}>
              <div>
                <span style={{ fontSize: "14px", fontWeight: "700", display: "block" }}>Reset Profile Taste</span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>Redo the taste preferences setup</span>
              </div>
              <button className="secondary-btn" onClick={onResetProfile} style={{ height: "36px", fontSize: "12px", padding: "0 12px" }}>
                <RefreshCcw size={12} /> Reset
              </button>
            </div>
          </div>
        </div>

        {/* Quick Stats Summary */}
        <div style={{ borderTop: "1px solid var(--border-glass)", paddingTop: "20px" }}>
          <h3 className="drawer-section-title" style={{ marginBottom: "12px" }}>Session statistics</h3>
          <div style={{ display: "flex", gap: "12px", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", color: "var(--text-secondary)" }}>
              <Heart size={14} color="#ef4444" fill="rgba(239, 68, 68, 0.15)" /> Likes: <strong>{likedCount}</strong>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", color: "var(--text-secondary)" }}>
              <ThumbsDown size={14} color="#f97316" fill="rgba(249, 115, 22, 0.15)" /> Dislikes: <strong>{dislikedCount}</strong>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", color: "var(--text-secondary)" }}>
              <Bookmark size={14} color="#3b82f6" fill="rgba(59, 130, 246, 0.15)" /> Saved: <strong>{savedCount}</strong>
            </div>
          </div>
        </div>

        {/* Close Button / Save */}
        <div className="drawer-footer">
          <button className="accent-btn" onClick={onClose} style={{ width: "100%" }}>
            Apply preferences
          </button>
        </div>
      </div>
    </div>
  );
};
