import React, { useState, useEffect } from "react";
import { Loader2, Check } from "lucide-react";

interface LoadingExperienceProps {
  onFinish?: () => void;
}

export const LoadingExperience: React.FC<LoadingExperienceProps> = ({ onFinish }) => {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [messageIndex, setMessageIndex] = useState<number>(0);

  const steps = [
    "Analyzing your preferences",
    "Finding similar movies",
    "Understanding your request",
    "Ranking candidates",
    "Adding discovery and diversity"
  ];

  const funnyMessages = [
    "Let’s arrange some popcorn and pretend we’re movie critics for 10 seconds.",
    "Tiny spoiler: the perfect pick is already doing a dramatic entrance.",
    "Your ideal watchlist is warming up faster than a microwave popcorn bag.",
    "We’re matching vibes, not just genres — very important cinema science.",
    "One more second and the movie gods will reveal the perfect night watch.",
    "Great taste detected. We’re now filtering out the boring ones with ruthless precision.",
    "Snack break approved: we’re almost there, and the recommendation is becoming legendary."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          if (onFinish) {
            setTimeout(onFinish, 250);
          }
          return prev;
        }
      });
    }, 260);

    return () => clearInterval(interval);
  }, [onFinish, steps.length]);

  useEffect(() => {
    const messageTimer = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % funnyMessages.length);
    }, 1600);

    return () => clearInterval(messageTimer);
  }, [funnyMessages.length]);

  // Poster downloads can outlive the recommendation request. Keep the visual
  // progress just short of complete until the parent removes this loader after
  // every poster has settled.
  const progress = Math.min(((activeStep + 1) / steps.length) * 100, 90);

  return (
    <div className="loading-overlay glass-panel fade-in">
      <h3 className="loading-title">Understanding your movie taste...</h3>

      <div style={{ marginBottom: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", color: "var(--text-secondary)", fontSize: "12px" }}>
          <span>Loading your perfect watchlist</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div style={{ width: "100%", height: "10px", background: "rgba(255,255,255,0.08)", borderRadius: "999px", overflow: "hidden", border: "1px solid rgba(255,255,255,0.08)" }}>
          <div
            style={{
              width: `${progress}%`,
              height: "100%",
              borderRadius: "999px",
              background: "linear-gradient(90deg, #ef4444 0%, #f59e0b 40%, #22c55e 100%)",
              transition: "width 0.3s ease"
            }}
          />
        </div>
      </div>

      <div className="loading-steps-list">
        {steps.map((step, idx) => {
          const isCompleted = idx < activeStep;
          const isActive = idx === activeStep;

          return (
            <div
              key={idx}
              className={`loading-step-item ${isCompleted ? "completed" : ""} ${isActive ? "active" : ""}`}
            >
              <div className="loading-step-status-icon">
                {isCompleted ? (
                  <Check size={10} strokeWidth={3} />
                ) : isActive ? (
                  <Loader2 size={10} className="spinning" />
                ) : (
                  <span>•</span>
                )}
              </div>
              <span>{step}</span>
            </div>
          );
        })}
      </div>

      <div
        style={{
          marginTop: "18px",
          padding: "12px 14px",
          borderRadius: "12px",
          border: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(255,255,255,0.02)",
          color: "var(--text-secondary)",
          fontSize: "14px",
          lineHeight: "1.5",
          minHeight: "48px",
          display: "flex",
          alignItems: "center"
        }}
      >
        <span style={{ marginRight: "8px" }}>🎬</span>
        <span>{funnyMessages[messageIndex]}</span>
      </div>

      {activeStep === steps.length - 1 && (
        <p style={{ fontSize: "13px", color: "var(--text-secondary)", fontWeight: "600", marginTop: "12px" }}>
          Finalizing movie posters...
        </p>
      )}
    </div>
  );
};
