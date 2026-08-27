import React, { useState, useEffect } from "react";
import { Film } from "lucide-react";

interface MoviePosterProps {
  title: string;
  genres?: string[];
  posterUrl: string | null;
  className?: string;
}

export const MoviePoster: React.FC<MoviePosterProps> = ({
  title,
  genres = [],
  posterUrl,
  className = ""
}) => {
  const [hasError, setHasError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Reset states if URL changes
  useEffect(() => {
    setHasError(false);
    setLoading(true);
  }, [posterUrl]);

  const renderFallback = () => {
    return (
      <div className="movie-poster-fallback">
        <div className="fallback-glow"></div>
        <div className="fallback-header">
          <Film size={14} color="#e50914" />
          <span className="branding-text">CineMatch AI</span>
        </div>
        <div className="fallback-body">
          <h4 className="fallback-movie-title">{title}</h4>
          {genres.length > 0 && (
            <div className="fallback-movie-genres">
              {genres.slice(0, 2).join(" • ")}
            </div>
          )}
        </div>
        <div className="fallback-footer">
          <div className="fallback-divider"></div>
          <span className="footer-tag">Cinematic Choice</span>
        </div>
      </div>
    );
  };

  return (
    <div className={`movie-poster-container ${className}`}>
      {posterUrl && !hasError ? (
        <>
          {loading && <div className="skeleton-poster absolute-fill"></div>}
          <img
            src={posterUrl}
            alt={title}
            className={`movie-poster-image ${loading ? "hidden" : "visible"}`}
            onLoad={() => setLoading(false)}
            onError={() => {
              setHasError(true);
              setLoading(false);
            }}
          />
        </>
      ) : (
        renderFallback()
      )}
    </div>
  );
};
