import React, { useState, useEffect } from "react";
import { Loader2, Check } from "lucide-react";

interface LoadingExperienceProps {
  onFinish?: () => void;
}

export const LoadingExperience: React.FC<LoadingExperienceProps> = ({ onFinish }) => {
  const [activeStep, setActiveStep] = useState<number>(0);

  const steps = [
    "Analyzing your preferences",
    "Finding similar movies",
    "Understanding your request",
    "Ranking candidates",
    "Adding discovery and diversity"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          if (onFinish) {
            // Trigger completion callback after a small delay
            setTimeout(onFinish, 200);
          }
          return prev;
        }
      });
    }, 250); // Progress every 250ms

    return () => clearInterval(interval);
  }, [onFinish, steps.length]);

  return (
    <div className="loading-overlay glass-panel fade-in">
      <h3 className="loading-title">Understanding your movie taste...</h3>
      
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

      {activeStep === steps.length - 1 && (
        <p style={{ fontSize: "13px", color: "var(--match-green)", fontWeight: "600", marginTop: "12px" }}>
          Your recommendations are ready.
        </p>
      )}
    </div>
  );
};
