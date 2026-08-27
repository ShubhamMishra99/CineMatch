import React from "react";
import { User, Users, MessageSquare, Tag, Award, ShieldAlert, Film, ArrowRight } from "lucide-react";

export const RecommendationPipeline: React.FC = () => {
  const steps = [
    {
      id: "taste",
      icon: <User size={18} />,
      label: "Your Taste",
      sub: "Preference Vector",
      tooltipTitle: "Taste Vectoring",
      tooltipText: "Calculates user preference signals based on favorite genres and movies liked during onboarding.",
      accented: false
    },
    {
      id: "collaborative",
      icon: <Users size={18} />,
      label: "Similar Viewers",
      sub: "Funk SVD Latent Matrix",
      tooltipTitle: "Collaborative Filtering",
      tooltipText: "Predicts user ratings using low-rank matrix decomposition trained on millions of community interactions.",
      accented: false
    },
    {
      id: "intent",
      icon: <MessageSquare size={18} />,
      label: "Semantic Intent",
      sub: "SBERT Embeddings",
      tooltipTitle: "Natural Language Understanding",
      tooltipText: "Encodes natural language queries into semantic vectors using Sentence-BERT to compute movie query similarities.",
      accented: false
    },
    {
      id: "content",
      icon: <Tag size={18} />,
      label: "Movie Content",
      sub: "Metadata Soup TF-IDF",
      tooltipTitle: "Content Similarity Mapping",
      tooltipText: "Compares content metadata (overview, director, cast, keywords) using TF-IDF cosine similarity metrics.",
      accented: false
    },
    {
      id: "ranking",
      icon: <Award size={18} />,
      label: "Hybrid Ranking",
      sub: "Bayesian Prior Weights",
      tooltipTitle: "Weighted Score Aggregation",
      tooltipText: "Aggregates and ranks all candidates using dynamically adjusted weight ratios and Bayesian movie quality priors.",
      accented: true
    },
    {
      id: "diversity",
      icon: <ShieldAlert size={18} />,
      label: "Diversity Filter",
      sub: "MMR Re-Ranking",
      tooltipTitle: "Maximal Marginal Relevance",
      tooltipText: "Tastes-similarity re-ranking to filter out highly redundant movies and introduce exploratory gems.",
      accented: false
    },
    {
      id: "recommendations",
      icon: <Film size={18} />,
      label: "CineMatch Output",
      sub: "Explainable Playlist",
      tooltipTitle: "Explainable Output",
      tooltipText: "Delivers the final diverse playlist of personalized recommendations, complete with confidence scores.",
      accented: true
    }
  ];

  return (
    <div className="system-logic-visualizer fade-in">
      <h3 className="section-title" style={{ borderLeftColor: "var(--accent-secondary)" }}>
        How CineMatch Thinks
      </h3>
      <p style={{ fontSize: "13.5px", color: "var(--text-secondary)", marginTop: "4px" }}>
        CineMatch AI processes user signals through a multi-stage hybrid recommendation pipeline to generate highly personalized suggestions:
      </p>

      <div className="pipeline-nodes-wrapper">
        {steps.map((step, idx) => (
          <React.Fragment key={step.id}>
            {/* Step Node */}
            <div className={`pipeline-node ${step.accented ? "accented" : ""}`}>
              <div className="pipeline-node-icon">{step.icon}</div>
              <div className="pipeline-node-label">{step.label}</div>
              <div className="pipeline-node-sub">{step.sub}</div>

              {/* Interactive Tooltip */}
              <div className="pipeline-tooltip">
                <div className="pipeline-tooltip-title">{step.tooltipTitle}</div>
                <div>{step.tooltipText}</div>
              </div>
            </div>

            {/* Separating Arrow */}
            {idx < steps.length - 1 && (
              <div className="pipeline-arrow">
                <ArrowRight size={14} />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
