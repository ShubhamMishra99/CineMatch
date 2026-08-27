import React from "react";
import { User, MessageSquare, Tag, Users, Award, ShieldAlert, ArrowRight } from "lucide-react";

export const SystemLogicVisualizer: React.FC = () => {
  return (
    <div className="system-logic-visualizer">
      <h2 className="section-title" style={{ borderLeftColor: "#00adb5" }}>
        How the System Works
      </h2>
      <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "20px" }}>
        CineMatch AI processes user signals through a multi-stage recommendation pipeline:
      </p>
      
      <div className="logic-steps">
        <div className="logic-step-card">
          <User size={20} color="#3b82f6" />
          <div>User Taste Vector</div>
          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>Liked/Disliked History</span>
        </div>
        
        <div className="logic-arrow"><ArrowRight size={18} /></div>
        
        <div className="logic-step-card">
          <MessageSquare size={20} color="#06b6d4" />
          <div>Semantic Intent</div>
          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>SBERT Query Similarity</span>
        </div>
        
        <div className="logic-arrow"><ArrowRight size={18} /></div>
        
        <div className="logic-step-card">
          <Tag size={20} color="#10b981" />
          <div>Content Similarity</div>
          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>Metadata Soup TF-IDF</span>
        </div>
        
        <div className="logic-arrow"><ArrowRight size={18} /></div>
        
        <div className="logic-step-card">
          <Users size={20} color="#a855f7" />
          <div>Collaborative Filter</div>
          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>Funk SVD Latent Matrix</span>
        </div>
        
        <div className="logic-arrow"><ArrowRight size={18} /></div>
        
        <div className="logic-step-card">
          <Award size={20} color="#f5c518" />
          <div>Quality/Popularity</div>
          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>Bayesian Ratings Prior</span>
        </div>
        
        <div className="logic-arrow"><ArrowRight size={18} /></div>
        
        <div className="logic-step-card">
          <ShieldAlert size={20} color="#f97316" />
          <div>MMR Diversity</div>
          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>Maximal Marginal Relevance</span>
        </div>
        
        <div className="logic-arrow"><ArrowRight size={18} /></div>
        
        <div className="logic-step-card result">
          <FilmIcon size={20} />
          <div style={{ color: "var(--accent-primary)", fontWeight: "bold" }}>Diverse Playlist</div>
          <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>Explainable Output</span>
        </div>
      </div>
    </div>
  );
};

// Helper simple FilmIcon since lucide-react Film is already imported elsewhere
const FilmIcon = ({ size }: { size: number }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="#e50914" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
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
