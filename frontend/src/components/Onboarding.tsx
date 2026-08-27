import React, { useState } from "react";
import { Film, Check, ArrowRight, ArrowLeft } from "lucide-react";
import { MoviePoster } from "./MoviePoster";

interface OnboardingProps {
  onComplete: (selections: {
    favoriteGenres: string[];
    likedMovieIds: number[];
    preference: string;
    moodQuery: string;
  }) => void;
}

// 12 Highly Popular seed movies with verified 200 OK TMDB poster paths
const SEED_MOVIES = [
  { id: 79132, title: "Inception", genres: ["Sci-Fi", "Thriller", "Action"], posterUrl: "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg" },
  { id: 109487, title: "Interstellar", genres: ["Sci-Fi", "Drama", "Adventure"], posterUrl: "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg" },
  { id: 2571, title: "The Matrix", genres: ["Sci-Fi", "Action"], posterUrl: "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg" },
  { id: 58559, title: "The Dark Knight", genres: ["Action", "Crime", "Drama"], posterUrl: "https://image.tmdb.org/t/p/w500/1hRoyzDtpgMU7Dz4JF22RANzQO7.jpg" },
  { id: 296, title: "Pulp Fiction", genres: ["Thriller", "Crime"], posterUrl: "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg" },
  { id: 356, title: "Forrest Gump", genres: ["Drama", "Comedy", "Romance"], posterUrl: "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg" },
  { id: 2959, title: "Fight Club", genres: ["Drama", "Thriller"], posterUrl: "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg" },
  { id: 318, title: "The Shawshank Redemption", genres: ["Drama", "Crime"], posterUrl: "https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg" },
  { id: 260, title: "Star Wars: A New Hope", genres: ["Adventure", "Sci-Fi", "Action"], posterUrl: "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg" },
  { id: 4993, title: "The Fellowship of the Ring", genres: ["Adventure", "Fantasy", "Action"], posterUrl: "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg" },
  { id: 1721, title: "Titanic", genres: ["Drama", "Romance"], posterUrl: "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg" },
  { id: 72998, title: "Avatar", genres: ["Action", "Adventure", "Fantasy", "Sci-Fi"], posterUrl: "https://image.tmdb.org/t/p/w500/vL5LR6WdxWPjLPFRLe133jXWsh5.jpg" }
];

const GENRES = [
  "Action", "Adventure", "Animation", "Comedy", "Crime", 
  "Drama", "Fantasy", "Horror", "Mystery", "Romance", 
  "Science Fiction", "Thriller"
];

const PREFERENCES = [
  { id: "popular", label: "Popular Blockbusters", desc: "Mainstream hits favored by the crowd" },
  { id: "hidden_gems", label: "Hidden Gems", desc: "Highly rated movies with fewer views" },
  { id: "acclaimed", label: "Critically Acclaimed", desc: "Top award winners and artistic triumphs" },
  { id: "recent", label: "Recent Releases", desc: "Modern selections from recent years" },
  { id: "surprising", label: "Surprise Me", desc: "Eclectic selections outside typical lists" }
];

export const Onboarding: React.FC<OnboardingProps> = ({ onComplete }) => {
  const [step, setStep] = useState<number>(1);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [selectedMovies, setSelectedMovies] = useState<number[]>([]);
  const [selectedPref, setSelectedPref] = useState<string>("popular");
  const [moodQuery, setMoodQuery] = useState<string>("");

  const toggleGenre = (genre: string) => {
    setSelectedGenres(prev =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  };

  const toggleMovie = (movieId: number) => {
    setSelectedMovies(prev =>
      prev.includes(movieId) ? prev.filter((id) => id !== movieId) : [...prev, movieId]
    );
  };

  const handleNextStep = () => {
    if (step < 3) setStep(step + 1);
  };

  const handlePrevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = () => {
    onComplete({
      favoriteGenres: selectedGenres,
      likedMovieIds: selectedMovies,
      preference: selectedPref,
      moodQuery
    });
  };

  // Progress percentage calculation
  const progressPercent = (step / 3) * 100;

  return (
    <div className="onboarding-screen-widescreen">
      <div className="onboarding-container">
        
        {/* Progress header */}
        <div className="onboarding-progress-bar-wrapper">
          <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }}></div>
          <div className="progress-bar-labels">
            <span className={step >= 1 ? "active" : ""}>1. Genres</span>
            <span className={step >= 2 ? "active" : ""}>2. Favorites</span>
            <span className={step >= 3 ? "active" : ""}>3. Moods</span>
          </div>
        </div>

        {/* STEP 1: Genres Selection */}
        {step === 1 && (
          <div className="onboarding-step-view fade-in">
            <span className="step-counter">Step 1 of 3</span>
            <h1 className="onboarding-title-large">Let's learn your movie taste.</h1>
            <p className="onboarding-subtitle-large">Pick a few genres you enjoy. You can always change these later.</p>
            
            <div className="genres-grid-large">
              {GENRES.map((genre) => {
                const isSelected = selectedGenres.includes(genre);
                return (
                  <div
                    key={genre}
                    className={`genre-card-large ${isSelected ? "selected" : ""}`}
                    onClick={() => toggleGenre(genre)}
                  >
                    <div className="genre-card-overlay"></div>
                    <span className="genre-card-text">{genre}</span>
                    {isSelected && (
                      <span className="genre-selection-tick">
                        <Check size={14} color="#fff" />
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
            
            <div className="onboarding-navigation-row">
              <div></div> {/* Empty spacer */}
              <button 
                className="accent-btn" 
                onClick={handleNextStep}
                disabled={selectedGenres.length === 0}
              >
                Continue to Favorites <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Seed Movies grid */}
        {step === 2 && (
          <div className="onboarding-step-view fade-in">
            <span className="step-counter">Step 2 of 3</span>
            <h1 className="onboarding-title-large">Which of these have you enjoyed?</h1>
            <p className="onboarding-subtitle-large">Choose at least 2 movies so CineMatch can understand your taste.</p>
            
            <div className="seed-movies-grid-large">
              {SEED_MOVIES.map((movie) => {
                const isSelected = selectedMovies.includes(movie.id);
                return (
                  <div
                    key={movie.id}
                    className={`seed-movie-card-large ${isSelected ? "selected" : ""}`}
                    onClick={() => toggleMovie(movie.id)}
                  >
                    <MoviePoster 
                      title={movie.title}
                      genres={movie.genres}
                      posterUrl={movie.posterUrl}
                      className="seed-movie-poster-large"
                    />
                    <div className="seed-movie-overlay">
                      <div className="seed-movie-title">{movie.title}</div>
                    </div>
                    {isSelected && (
                      <div className="seed-movie-selection-indicator">
                        <Check size={14} color="#fff" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            
            <div className="onboarding-navigation-row">
              <button className="secondary-btn" onClick={handlePrevStep}>
                <ArrowLeft size={16} /> Back
              </button>
              <button 
                className="accent-btn" 
                onClick={handleNextStep}
                disabled={selectedMovies.length < 2}
              >
                Continue to Moods <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Goals & Mood Query */}
        {step === 3 && (
          <div className="onboarding-step-view fade-in">
            <span className="step-counter">Step 3 of 3</span>
            <h1 className="onboarding-title-large">What are you looking for today?</h1>
            <p className="onboarding-subtitle-large">Tune your recommendation targets and specify your viewing mood.</p>
            
            <div className="goals-options-container">
              <div className="section-title">Select recommendation goals</div>
              <div className="goals-grid-large">
                {PREFERENCES.map((pref) => {
                  const isSelected = selectedPref === pref.id;
                  return (
                    <div
                      key={pref.id}
                      className={`goal-card-large ${isSelected ? "selected" : ""}`}
                      onClick={() => setSelectedPref(pref.id)}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span className="goal-label">{pref.label}</span>
                        {isSelected && <Check size={16} color="var(--accent-primary)" />}
                      </div>
                      <p className="goal-desc">{pref.desc}</p>
                    </div>
                  );
                })}
              </div>

              <div className="section-title" style={{ marginTop: "40px" }}>What are you in the mood for?</div>
              <div style={{ position: "relative", marginTop: "12px" }}>
                <textarea
                  className="mood-textarea"
                  placeholder="Describe your current vibe... (e.g. An intelligent sci-fi movie that is emotional but not too dark)"
                  value={moodQuery}
                  onChange={(e) => setMoodQuery(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
            
            <div className="onboarding-navigation-row" style={{ marginTop: "40px" }}>
              <button className="secondary-btn" onClick={handlePrevStep}>
                <ArrowLeft size={16} /> Back
              </button>
              <button 
                className="accent-btn" 
                onClick={handleSubmit}
              >
                Generate My Recommendations <Film size={16} />
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
