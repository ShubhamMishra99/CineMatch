import React from "react";
import { Sparkles } from "lucide-react";

interface TasteProfileSummaryProps {
  favoriteGenres: string[];
  preference: string;
}

export const TasteProfileSummary: React.FC<TasteProfileSummaryProps> = ({
  favoriteGenres,
  preference
}) => {
  // Generate taste tags based on user selections
  const getTasteChips = () => {
    const chips = [];

    // Map genres
    if (favoriteGenres.includes("Science Fiction") || favoriteGenres.includes("Sci-Fi")) {
      chips.push({ label: "Sci-Fi Explorer", icon: "🎬" });
    }
    if (favoriteGenres.includes("Thriller") || favoriteGenres.includes("Mystery")) {
      chips.push({ label: "Mind-Bending Plots", icon: "🧠" });
    }
    if (favoriteGenres.includes("Drama")) {
      chips.push({ label: "Character-Driven Drama", icon: "🎭" });
    }
    if (favoriteGenres.includes("Comedy")) {
      chips.push({ label: "Lighthearted Comedy", icon: "🍿" });
    }
    if (favoriteGenres.includes("Horror")) {
      chips.push({ label: "Dark Thrills", icon: "😱" });
    }
    if (favoriteGenres.includes("Action") || favoriteGenres.includes("Adventure")) {
      chips.push({ label: "Epic Journeys", icon: "🚀" });
    }

    // Map preference targets
    if (preference === "hidden_gems") {
      chips.push({ label: "Open to Hidden Gems", icon: "💎" });
    } else if (preference === "acclaimed") {
      chips.push({ label: "Critically Acclaimed", icon: "🏆" });
    } else if (preference === "recent") {
      chips.push({ label: "Modern Releases", icon: "🆕" });
    } else if (preference === "popular") {
      chips.push({ label: "Big Blockbusters", icon: "🔥" });
    } else {
      chips.push({ label: "Surprise Seeker", icon: "🎲" });
    }

    // Fallback if empty
    if (chips.length === 0) {
      chips.push({ label: "Movie Aficionado", icon: "🍿" });
    }

    return chips.slice(0, 4); // Limit to 4 chips
  };

  // Generate a tailored text insight based on choices
  const getTasteInsight = () => {
    let style = "well-crafted, engaging";
    if (preference === "hidden_gems") {
      style = "unique, lesser-known cinematic wonders";
    } else if (preference === "acclaimed") {
      style = "masterfully directed, critically praised narratives";
    } else if (preference === "recent") {
      style = "contemporary, modern release stories";
    } else if (preference === "popular") {
      style = "spectacular, popular blockbuster productions";
    }

    let genreFocus = "";
    if (favoriteGenres.length > 0) {
      const displayGenres = favoriteGenres.slice(0, 2).join(" & ");
      genreFocus = ` with a particular emphasis on the elements of ${displayGenres}`;
    }

    return `Based on your selections, CineMatch predicts you appreciate ${style} films${genreFocus}. We've tuned your recommendations accordingly.`;
  };

  const chips = getTasteChips();
  const insight = getTasteInsight();

  return (
    <section className="taste-summary-section fade-in">
      <div className="taste-summary-container">
        <div className="taste-summary-left">
          <div className="taste-greeting">
            <Sparkles size={12} style={{ display: "inline", marginRight: "6px" }} />
            YOUR TASTE PROFILE IS READY
          </div>
          <h2 className="taste-title">Welcome to your discovery room</h2>
          <p className="taste-insight">{insight}</p>
        </div>
        
        <div className="taste-chips-wrapper">
          {chips.map((chip, idx) => (
            <div key={idx} className="taste-summary-chip">
              <span>{chip.icon}</span>
              <span>{chip.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
