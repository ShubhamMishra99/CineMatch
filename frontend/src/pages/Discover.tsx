import React, { useState, useEffect } from "react";
import { 
  Search, Sliders, RefreshCcw, Globe
} from "lucide-react";
import type { MovieRecommendation, RecommendResponse, MovieDetails } from "../types";
import { MovieCard } from "../components/MovieCard";
import { TasteProfileSummary } from "../components/TasteProfileSummary";
import { RecommendationControls } from "../components/RecommendationControls";
import { ExplainabilityDrawer } from "../components/ExplainabilityDrawer";
import { RecommendationPipeline } from "../components/RecommendationPipeline";
import { LoadingExperience } from "../components/LoadingExperience";
import { Toast } from "../components/Toast";

interface DiscoverProps {
  favoriteGenres: string[];
  likedMovieIds: number[];
  onboardingMood: string;
  onResetOnboarding: () => void;
}

const API_BASE_URL = "http://localhost:8000/api";

const SUGGESTIONS = [
  { text: "Mind-bending sci-fi", query: "mind-bending sci-fi space travel", emoji: "🧠" },
  { text: "Emotional but hopeful", query: "emotional but hopeful drama", emoji: "❤️" },
  { text: "Dark psych thriller", query: "dark psychological thriller mystery", emoji: "😱" },
  { text: "Hidden gem < 2 hours", query: "hidden gem movie under 2 hours", emoji: "💎" },
  { text: "Epic space adventure", query: "epic space adventure interstellar travel", emoji: "🚀" }
];

export const Discover: React.FC<DiscoverProps> = ({
  favoriteGenres: initialGenres,
  likedMovieIds: initialLiked,
  onboardingMood,
  onResetOnboarding
}) => {
  // Profile settings state
  const [favoriteGenres, setFavoriteGenres] = useState<string[]>(initialGenres);
  const [likedIds, setLikedIds] = useState<number[]>(initialLiked);
  const [dislikedIds, setDislikedIds] = useState<number[]>([]);
  const [savedIds, setSavedIds] = useState<number[]>([]);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState<string>(onboardingMood || "");
  const [activeTab, setActiveTab] = useState<string>("discover");
  
  // Tuning drawer state
  const [diversityMode, setDiversityMode] = useState<string>("balanced");
  const [isColdStart, setIsColdStart] = useState<boolean>(initialLiked.length === 0);
  const [isTuningOpen, setIsTuningOpen] = useState<boolean>(false);
  
  // Explainability drawer state
  const [isExplainOpen, setIsExplainOpen] = useState<boolean>(false);
  const [explainMovie, setExplainMovie] = useState<MovieRecommendation | null>(null);

  // Toast notifications state
  const [toasts, setToasts] = useState<Array<{ id: number; message: string }>>([]);

  // API recommendations states
  const [recommendations, setRecommendations] = useState<MovieRecommendation[]>([]);
  const [metadata, setMetadata] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [pipelineLoading, setPipelineLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Details Modal states
  const [selectedMovieId, setSelectedMovieId] = useState<number | null>(null);
  const [movieDetails, setMovieDetails] = useState<MovieDetails | null>(null);
  const [detailsLoading, setDetailsLoading] = useState<boolean>(false);

  // Sync cold start state if likes change
  useEffect(() => {
    setIsColdStart(likedIds.length === 0);
  }, [likedIds]);

  // Show a toast message
  const showToast = (message: string) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message }]);
  };

  // Close toast by ID
  const removeToast = (id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Load recommendations from backend
  const fetchRecommendations = async (queryText?: string, showPipeline = false) => {
    setLoading(true);
    if (showPipeline) {
      setPipelineLoading(true);
    }
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: 1, // Default test user
          liked_movie_ids: likedIds,
          disliked_movie_ids: dislikedIds,
          favorite_genres: favoriteGenres,
          query: queryText !== undefined ? queryText : (searchQuery || null),
          diversity_mode: diversityMode,
          limit: 12
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to fetch recommendations from the server.");
      }
      
      const data: RecommendResponse = await response.json();
      setRecommendations(data.recommendations);
      setMetadata(data.metadata);
    } catch (err: any) {
      console.error(err);
      setError("Could not connect to CineMatch AI backend. Make sure the FastAPI server is running.");
    } finally {
      setLoading(false);
      if (!showPipeline) {
        setPipelineLoading(false);
      }
    }
  };

  // Fetch recommendations on settings change
  useEffect(() => {
    fetchRecommendations(undefined, false);
  }, [likedIds, dislikedIds, favoriteGenres, diversityMode]);

  // Trigger search submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRecommendations(searchQuery, true);
  };

  // Suggestion chips handler
  const handleSuggestionClick = (suggestion: typeof SUGGESTIONS[0]) => {
    setSearchQuery(suggestion.query);
    fetchRecommendations(suggestion.query, true);
    showToast(`Searching for "${suggestion.text}"...`);
  };

  // Movie action feedbacks handler
  const handleFeedback = async (movieId: number, type: "like" | "dislike" | "save") => {
    try {
      // 1. Submit interaction feedback to backend
      await fetch(`${API_BASE_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: 1, movie_id: movieId, feedback_type: type })
      });
      
      // 2. Update local state triggers recommendations updates
      if (type === "like") {
        setLikedIds([...likedIds.filter((id) => id !== movieId), movieId]);
        setDislikedIds(dislikedIds.filter((id) => id !== movieId));
        showToast("Added to liked preferences.");
      } else if (type === "dislike") {
        setDislikedIds([...dislikedIds.filter((id) => id !== movieId), movieId]);
        setLikedIds(likedIds.filter((id) => id !== movieId));
        showToast("Got it. We'll tune your recommendations.");
      } else if (type === "save") {
        if (savedIds.includes(movieId)) {
          setSavedIds(savedIds.filter((id) => id !== movieId));
          showToast("Removed from watchlist.");
        } else {
          setSavedIds([...savedIds, movieId]);
          showToast("Saved to watchlist.");
        }
      }
    } catch (err) {
      console.error("Error registering feedback", err);
      showToast("Error updating feedback.");
    }
  };

  // Fetch movie details modal
  const handleCardClick = async (movieId: number) => {
    setSelectedMovieId(movieId);
    setDetailsLoading(true);
    setMovieDetails(null);
    try {
      const response = await fetch(`${API_BASE_URL}/movie/${movieId}`);
      if (!response.ok) throw new Error("Failed to load movie details.");
      const data = await response.json();
      setMovieDetails(data);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailsLoading(false);
    }
  };

  // Open Explainability Drawer
  const handleOpenExplainability = (movie: MovieRecommendation) => {
    setExplainMovie(movie);
    setIsExplainOpen(true);
  };

  // Genres selection drawer toggling
  const handleToggleGenre = (genre: string) => {
    if (favoriteGenres.includes(genre)) {
      setFavoriteGenres(favoriteGenres.filter(g => g !== genre));
    } else {
      setFavoriteGenres([...favoriteGenres, genre]);
    }
  };

  // Handle Cold start settings updates
  const handleSetColdStart = (val: boolean) => {
    if (val) {
      setLikedIds([]);
      showToast("Tuned engine profile to cold start.");
    } else {
      setLikedIds([79132]); // Seed with inception
      showToast("Tuned engine profile to warm user.");
    }
  };

  return (
    <div className="app-container">
      {/* Premium Top Navigation Bar */}
      <header className="app-header">
        <a className="logo-container" href="/">
          <FilmIcon size={22} />
          <div className="logo-text">CineMatch <span>AI</span></div>
        </a>

        {/* Center navigation links */}
        <nav className="header-nav">
          <span className={`nav-link ${activeTab === "discover" ? "active" : ""}`} onClick={() => setActiveTab("discover")}>Discover</span>
          <span className={`nav-link ${activeTab === "for-you" ? "active" : ""}`} onClick={() => setActiveTab("for-you")}>For You</span>
          <span className={`nav-link ${activeTab === "search" ? "active" : ""}`} onClick={() => setActiveTab("search")}>Search</span>
          <span className={`nav-link`} onClick={() => {
            const el = document.getElementById("pipeline-section");
            if (el) el.scrollIntoView({ behavior: "smooth" });
          }}>How It Works</span>
        </nav>
        
        {/* Right side settings */}
        <div className="header-right">
          <div className="taste-nav-chip">
            Your Taste
          </div>
          <button className="secondary-btn" onClick={() => setIsTuningOpen(true)} style={{ height: "38px", fontSize: "13px", padding: "0 14px" }}>
            <Sliders size={14} />
            Tune
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-content">
        
        {/* Cinematic Hero AI Search */}
        <section className="hero-section">
          <span className="hero-eyebrow">Powered by Hybrid AI</span>
          <h1 className="hero-title">Find your next <span>unforgettable</span> movie.</h1>
          
          <p className="hero-subtitle">
            Tell CineMatch what you're in the mood for. Our hybrid recommendation engine combines your taste, movie similarity, collaborative signals, semantic understanding, and diversity-aware ranking.
          </p>
          
          <form className="search-wrapper" onSubmit={handleSearchSubmit}>
            <input 
              type="text" 
              className="search-input-box" 
              placeholder="Describe the perfect movie for tonight..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="search-submit-btn" type="submit">
              <Search size={20} />
            </button>
          </form>

          {/* Status indicators */}
          <div className="ai-status-indicator">
            <span className="status-dot"></span>
            <span>AI recommendation engine ready</span>
          </div>
          
          {/* Elegant prompt cards */}
          <div className="prompt-chips-container">
            {SUGGESTIONS.map((suggestion) => (
              <div 
                key={suggestion.text} 
                className="prompt-suggestion-card" 
                onClick={() => handleSuggestionClick(suggestion)}
              >
                <span className="emoji">{suggestion.emoji}</span>
                <span>{suggestion.text}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Personalized Taste Profile Summary Panel */}
        <TasteProfileSummary 
          favoriteGenres={favoriteGenres} 
          preference={metadata?.strategy || "popular"} 
        />

        {/* Recommendations Workspace */}
        <div className="dashboard-grid">
          
          {/* Picked for You Recommendations list */}
          <section className="recommendations-container">
            <div className="recommendations-title-row">
              <div>
                <h2 className="section-title">
                  {searchQuery ? "Recommended from Search" : "Picked for you"}
                </h2>
                <p className="section-subtitle">
                  Ranked using your taste profile and live recommendation signals.
                </p>
              </div>
              
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                {metadata && (
                  <span style={{ fontSize: "13px", color: "var(--text-muted)", fontFamily: "var(--font-display)", fontWeight: "600" }}>
                    Found {metadata.candidate_count} candidates ({metadata.latency_ms.total}ms)
                  </span>
                )}
                
                <button className="secondary-btn" onClick={() => setIsTuningOpen(true)} style={{ height: "36px", fontSize: "13px", padding: "0 14px", borderRadius: "10px" }}>
                  <Sliders size={13} />
                  Tune Recommendations
                </button>
              </div>
            </div>

            {error && (
              <div className="glass-panel" style={{ padding: "30px", borderLeft: "4px solid var(--accent-primary)", marginBottom: "30px" }}>
                <p style={{ fontWeight: "700", fontSize: "16px", marginBottom: "8px" }}>Backend Connection Offline</p>
                <p style={{ color: "var(--text-secondary)", fontSize: "14px", lineHeight: "1.5" }}>{error}</p>
                <button className="accent-btn" onClick={() => fetchRecommendations()} style={{ marginTop: "16px", height: "38px", fontSize: "13px", borderRadius: "8px" }}>
                  <Globe size={14} /> Retry Connection
                </button>
              </div>
            )}

            {/* loading state */}
            {pipelineLoading ? (
              <div style={{ padding: "40px 0" }}>
                <LoadingExperience onFinish={() => setPipelineLoading(false)} />
              </div>
            ) : loading ? (
              <div className="recommendations-grid">
                {Array.from({ length: 6 }).map((_, idx) => (
                  <div key={idx} className="skeleton-card">
                    <div className="skeleton-poster"></div>
                    <div className="skeleton-body">
                      <div className="skeleton-text title"></div>
                      <div className="skeleton-text meta"></div>
                      <div className="skeleton-text desc"></div>
                      <div className="skeleton-text desc-short"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : recommendations.length === 0 && !error ? (
              <div className="glass-panel" style={{ padding: "80px 40px", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: "16px" }}>
                <InfoIcon size={44} color="var(--text-secondary)" />
                <h3 style={{ fontSize: "18px", fontWeight: "800", fontFamily: "var(--font-display)" }}>No Recommendations Found</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "14px", maxWidth: "420px", textAlign: "center", lineHeight: "1.6" }}>
                  We couldn't find any recommendations matching your active preferences. Try resetting your search filters or adding more favorite genres.
                </p>
              </div>
            ) : (
              <div className="recommendations-grid fade-in">
                {recommendations.map((movie) => {
                  const isLiked = likedIds.includes(movie.movie_id);
                  const isDisliked = dislikedIds.includes(movie.movie_id);
                  const isSaved = savedIds.includes(movie.movie_id);

                  return (
                    <MovieCard 
                      key={movie.movie_id}
                      movie={movie}
                      isLiked={isLiked}
                      isDisliked={isDisliked}
                      isSaved={isSaved}
                      onFeedback={handleFeedback}
                      onOpenDetails={handleCardClick}
                      onOpenExplainability={handleOpenExplainability}
                    />
                  );
                })}
              </div>
            )}

            {/* Interactive recommendation pipeline visualization */}
            <div id="pipeline-section">
              <RecommendationPipeline />
            </div>
          </section>
        </div>
      </main>

      {/* Floating Preferences Drawer */}
      <RecommendationControls 
        isOpen={isTuningOpen}
        onClose={() => setIsTuningOpen(false)}
        diversityMode={diversityMode}
        setDiversityMode={setDiversityMode}
        favoriteGenres={favoriteGenres}
        onToggleGenre={handleToggleGenre}
        onResetProfile={onResetOnboarding}
        isColdStart={isColdStart}
        setIsColdStart={handleSetColdStart}
        likedCount={likedIds.length}
        dislikedCount={dislikedIds.length}
        savedCount={savedIds.length}
      />

      {/* Explainability Drawer */}
      <ExplainabilityDrawer 
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        movie={explainMovie}
      />

      {/* Movie Details Modal */}
      <div className={`modal-overlay ${selectedMovieId ? "open" : ""}`} onClick={() => setSelectedMovieId(null)}>
        <div className="modal-content glass-panel" onClick={(e) => e.stopPropagation()}>
          <button className="modal-close-btn" onClick={() => setSelectedMovieId(null)}>
            X
          </button>
          
          {detailsLoading ? (
            <div style={{ gridColumn: "span 2", display: "flex", justifyContent: "center", padding: "80px" }}>
              <RefreshCcw className="spinning" size={32} color="var(--accent-primary)" />
            </div>
          ) : movieDetails ? (
            <>
              <div>
                <img 
                  src={movieDetails.poster_url || "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?auto=format&fit=crop&w=500&q=80"}
                  alt={movieDetails.title}
                  className="modal-poster"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?auto=format&fit=crop&w=500&q=80";
                  }}
                />
              </div>
              
              <div className="modal-info">
                <h1 className="modal-title">{movieDetails.title}</h1>
                
                <div className="modal-meta-row">
                  {movieDetails.release_date && (
                    <div className="modal-meta-item">
                      <span>📅</span> {movieDetails.release_date}
                    </div>
                  )}
                  {movieDetails.runtime && (
                    <div className="modal-meta-item">
                      <span>⏱️</span> {movieDetails.runtime} min
                    </div>
                  )}
                  {movieDetails.vote_average && (
                    <div className="modal-meta-item" style={{ color: "var(--rating-gold)" }}>
                      <span>⭐</span> {movieDetails.vote_average.toFixed(1)} / 10
                    </div>
                  )}
                </div>

                <div className="modal-genres">
                  {movieDetails.genres.map((g) => (
                    <span key={g} className="genre-tag">{g}</span>
                  ))}
                </div>

                <p className="modal-overview">
                  {movieDetails.overview || "No description overview available."}
                </p>

                <div className="credits-box">
                  {movieDetails.director && (
                    <div className="credit-row">
                      <strong>Director:</strong> <span>{movieDetails.director}</span>
                    </div>
                  )}
                  {movieDetails.cast && movieDetails.cast.length > 0 && (
                    <div className="credit-row">
                      <strong>Cast:</strong> <span>{movieDetails.cast.join(", ")}</span>
                    </div>
                  )}
                  {movieDetails.keywords && movieDetails.keywords.length > 0 && (
                    <div className="credit-row" style={{ fontSize: "12px" }}>
                      <strong>Keywords:</strong> <span style={{ color: "var(--text-muted)" }}>{movieDetails.keywords.slice(0, 8).join(", ")}</span>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div style={{ gridColumn: "span 2", textAlign: "center", padding: "40px" }}>
              Failed to load movie metadata details.
            </div>
          )}
        </div>
      </div>

      {/* Toast Alert Notifications */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <Toast 
            key={toast.id}
            message={toast.message}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </div>
  );
};

// Helper SVG Icons
const FilmIcon = ({ size }: { size: number }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="#e50914" 
    strokeWidth="2.5" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    style={{ filter: "drop-shadow(0 0 6px rgba(229, 9, 20, 0.4))" }}
  >
    <rect width="18" height="18" x="3" y="3" rx="2"/>
    <path d="M7 3v18"/>
    <path d="M17 3v18"/>
    <path d="M3 7.5h4"/>
    <path d="M3 12h4"/>
    <path d="M3 16.5h4"/>
    <path d="M17 7.5h4"/>
    <path d="M17 12h4"/>
    <path d="M17 16.5h4"/>
  </svg>
);

const InfoIcon = ({ size, color }: { size: number, color?: string }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke={color || "currentColor"} 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 16v-4"/>
    <path d="M12 8h.01"/>
  </svg>
);
