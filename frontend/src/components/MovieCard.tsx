import React, { useState } from "react";
import { Heart, ThumbsDown, Bookmark, Star, Calendar, Clock, HelpCircle, Eye } from "lucide-react";
import type { MovieRecommendation } from "../types";
import { MoviePoster } from "./MoviePoster";

interface MovieCardProps {
  movie: MovieRecommendation;
  isLiked: boolean;
  isDisliked: boolean;
  isSaved: boolean;
  onFeedback: (movieId: number, type: "like" | "dislike" | "save") => void;
  onOpenDetails: (movieId: number) => void;
  onOpenExplainability: (movie: MovieRecommendation) => void;
}

export const MovieCard: React.FC<MovieCardProps> = ({
  movie,
  isLiked,
  isDisliked,
  isSaved,
  onFeedback,
  onOpenDetails,
  onOpenExplainability
}) => {
  const [isFading, setIsFading] = useState<boolean>(false);
  const matchPercent = Math.round(movie.score * 100);

  const handleDislikeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsFading(true);
    // Let the animation play out before updating state
    setTimeout(() => {
      onFeedback(movie.movie_id, "dislike");
    }, 400);
  };

  const handleLikeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFeedback(movie.movie_id, "like");
  };

  const handleSaveClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFeedback(movie.movie_id, "save");
  };

  const handleExplainClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onOpenExplainability(movie);
  };

  return (
    <div 
      className={`movie-card-container ${isFading ? "movie-card-fadeout" : ""}`}
      onClick={() => onOpenDetails(movie.movie_id)}
    >
      {/* Badges Overlay */}
      <div className="movie-card-badges">
        <div className="movie-card-badge match">
          {matchPercent}% Match
        </div>
        {movie.vote_average && (
          <div className="movie-card-badge rating">
            <Star size={11} fill="var(--rating-gold)" stroke="none" />
            {movie.vote_average.toFixed(1)}
          </div>
        )}
      </div>

      {/* Main Poster Visual */}
      <MoviePoster 
        title={movie.title}
        genres={movie.genres}
        posterUrl={movie.poster_url}
        className="movie-card-poster"
      />

      {/* Cinematic Hover Overlay */}
      <div className="movie-card-overlay">
        <h3 className="movie-overlay-title">{movie.title}</h3>
        
        <div className="movie-overlay-meta">
          {movie.release_year && (
            <span style={{ display: "flex", alignItems: "center", gap: "3px" }}>
              <Calendar size={11} /> {movie.release_year}
            </span>
          )}
          {movie.runtime && (
            <span style={{ display: "flex", alignItems: "center", gap: "3px" }}>
              <Clock size={11} /> {movie.runtime} min
            </span>
          )}
        </div>

        <div className="movie-overlay-genres">
          {movie.genres.slice(0, 3).join(" • ")}
        </div>

        <p className="movie-overlay-overview">
          {movie.overview ? movie.overview : "No description available."}
        </p>

        {/* Hover quick actions */}
        <div className="movie-overlay-actions">
          <div className="feedback-btn-group">
            <button 
              className={`circle-btn ${isLiked ? "liked" : ""}`}
              onClick={handleLikeClick}
              title="Like movie"
            >
              <Heart size={14} fill={isLiked ? "#ef4444" : "none"} />
            </button>
            <button 
              className={`circle-btn ${isDisliked ? "disliked" : ""}`}
              onClick={handleDislikeClick}
              title="Not interested"
            >
              <ThumbsDown size={14} fill={isDisliked ? "#f97316" : "none"} />
            </button>
            <button 
              className={`circle-btn ${isSaved ? "saved" : ""}`}
              onClick={handleSaveClick}
              title="Save to watchlist"
            >
              <Bookmark size={14} fill={isSaved ? "#3b82f6" : "none"} />
            </button>
          </div>

          <div style={{ display: "flex", gap: "6px" }}>
            <button 
              className="circle-btn" 
              onClick={handleExplainClick}
              title="Why recommended?"
              style={{ color: "var(--accent-primary)", borderColor: "rgba(229, 9, 20, 0.2)" }}
            >
              <HelpCircle size={14} />
            </button>
            <button 
              className="circle-btn" 
              onClick={() => onOpenDetails(movie.movie_id)}
              title="View details"
              style={{ color: "var(--accent-secondary)", borderColor: "rgba(14, 165, 233, 0.2)" }}
            >
              <Eye size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
