import { useState, useEffect } from "react";
import { Onboarding } from "./components/Onboarding";
import { Discover } from "./pages/Discover";

interface ProfileState {
  favoriteGenres: string[];
  likedMovieIds: number[];
  preference: string;
  moodQuery: string;
}

export default function App() {
  const [onboarded, setOnboarded] = useState<boolean>(false);
  const [profile, setProfile] = useState<ProfileState>({
    favoriteGenres: [],
    likedMovieIds: [],
    preference: "popular",
    moodQuery: ""
  });
  const [loading, setLoading] = useState<boolean>(true);

  // Check local storage for onboarding session state on startup
  useEffect(() => {
    try {
      const storedProfile = localStorage.getItem("cinematch_profile");
      const storedOnboarded = localStorage.getItem("cinematch_onboarded");
      
      if (storedProfile && storedOnboarded === "true") {
        setProfile(JSON.parse(storedProfile));
        setOnboarded(true);
      }
    } catch (e) {
      console.error("Failed to load local storage profile state:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  // Complete onboarding
  const handleOnboardingComplete = (selections: ProfileState) => {
    setProfile(selections);
    setOnboarded(true);
    try {
      localStorage.setItem("cinematch_profile", JSON.stringify(selections));
      localStorage.setItem("cinematch_onboarded", "true");
    } catch (e) {
      console.error("Failed to write onboarding profile to local storage:", e);
    }
  };

  // Reset onboarding profile
  const handleResetProfile = () => {
    setOnboarded(false);
    setProfile({
      favoriteGenres: [],
      likedMovieIds: [],
      preference: "popular",
      moodQuery: ""
    });
    try {
      localStorage.removeItem("cinematch_profile");
      localStorage.removeItem("cinematch_onboarded");
    } catch (e) {
      console.error("Failed to clear local storage profile state:", e);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#08090c", color: "#f3f4f6" }}>
        <div style={{ fontSize: "16px", fontWeight: "600", fontFamily: "sans-serif" }}>
          Loading CineMatch AI Profile...
        </div>
      </div>
    );
  }

  return (
    <>
      {!onboarded ? (
        <Onboarding onComplete={handleOnboardingComplete} />
      ) : (
        <Discover 
          favoriteGenres={profile.favoriteGenres}
          likedMovieIds={profile.likedMovieIds}
          onboardingMood={profile.moodQuery}
          onResetOnboarding={handleResetProfile}
        />
      )}
    </>
  );
}
