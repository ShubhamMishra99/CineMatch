import os
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from backend.app.core.config import settings
from backend.app.data.loader import DataLoader
from backend.app.recommenders.content_based import ContentBasedRecommender
from backend.app.recommenders.collaborative import CollaborativeRecommender
from backend.app.recommenders.semantic import SemanticRecommender
from backend.app.recommenders.hybrid import HybridRanker
from backend.app.recommenders.diversity import DiversityReranker
from backend.app.services.explanation_service import ExplanationService

class RecommendationService:
    def __init__(self, use_sample: bool = False):
        self.use_sample = use_sample
        self.movies_df = None
        self.ratings_df = None
        
        # Instantiate components
        self.data_loader = DataLoader(use_sample=use_sample)
        self.content_recommender = ContentBasedRecommender()
        self.collaborative_recommender = CollaborativeRecommender()
        self.semantic_recommender = SemanticRecommender(self.content_recommender)
        
        self.hybrid_ranker = HybridRanker(
            self.content_recommender,
            self.collaborative_recommender,
            self.semantic_recommender
        )
        self.diversity_reranker = DiversityReranker(self.content_recommender)
        self.explanation_service = ExplanationService()
        
        self.models_loaded = {
            "content": False,
            "collaborative": False,
            "semantic": False
        }

    def initialize(self):
        """Load datasets and initialize models. Run once during startup."""
        print("=== Initializing Recommendation Service ===")
        start_time = time.time()
        
        # 1. Load Data
        self.movies_df, self.ratings_df = self.data_loader.load_data()
        
        # 2. Initialize Content-Based Recommender (and check for dense embeddings)
        embeddings = None
        embeddings_path = os.path.join(settings.MODEL_DIR, "movie_embeddings.npy")
        if os.path.exists(embeddings_path):
            try:
                embeddings = np.load(embeddings_path)
            except Exception as e:
                print(f"Error loading dense embeddings from {embeddings_path}: {e}")
                
        self.content_recommender.load_data(self.movies_df, embeddings)
        self.models_loaded["content"] = True
        
        # 3. Initialize Collaborative Filtering (SVD)
        svd_model_path = os.path.join(settings.MODEL_DIR, "collaborative_model.pkl")
        if os.path.exists(svd_model_path):
            try:
                self.collaborative_recommender.load(svd_model_path)
                self.models_loaded["collaborative"] = True
            except Exception as e:
                print(f"Error loading collaborative SVD weights: {e}. Running with uninitialized baseline.")
        else:
            print(f"Warning: SVD model file {svd_model_path} not found. Running SVD with dummy weights.")
            
        # 4. Initialize Semantic Recommender
        self.semantic_recommender.load_data(self.movies_df)
        self.models_loaded["semantic"] = True
        
        # 5. Initialize Hybrid and Explanation
        self.hybrid_ranker.load_data(self.movies_df)
        self.explanation_service.set_movies_df(self.movies_df)
        
        duration = time.time() - start_time
        print(f"=== Initialization Complete in {duration:.2f}s ===")

    def get_recommendations(
        self,
        user_id: int,
        liked_movie_ids: List[int],
        disliked_movie_ids: List[int],
        favorite_genres: List[str],
        query: Optional[str] = None,
        diversity_mode: str = "balanced",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Coordinates the full recommendation pipeline:
        1. Generates candidates.
        2. Applies hybrid ranking.
        3. Applies diversity re-ranking (MMR).
        4. Translates scoring into natural explainability.
        5. Tracks Latency metrics.
        """
        start_time = time.time()
        
        # Helper to fetch metadata of movies liked in the session to construct explanations
        liked_movies_metadata = []
        if liked_movie_ids:
            liked_movies_metadata = self.movies_df[self.movies_df["movieId"].isin(liked_movie_ids)].to_dict(orient="records")

        # 1. Candidate Generation & Hybrid Ranking
        t1 = time.time()
        candidates, strategy, weights = self.hybrid_ranker.recommend(
            user_id=user_id,
            liked_ids=liked_movie_ids,
            disliked_ids=disliked_movie_ids,
            favorite_genres=favorite_genres,
            query=query,
            limit=200 # Rank 200 candidates
        )
        ranking_latency = (time.time() - t1) * 1000
        
        candidate_count = len(candidates)

        # 2. Diversity-aware Re-ranking (MMR)
        t2 = time.time()
        reranked_movies = self.diversity_reranker.rerank(
            candidates=candidates,
            diversity_mode=diversity_mode,
            limit=limit
        )
        diversity_latency = (time.time() - t2) * 1000

        # 3. Generate Explainable recommendation texts
        t3 = time.time()
        final_recommendations = []
        for movie in reranked_movies:
            explanation = self.explanation_service.generate_explanation(
                movie=movie,
                liked_movies_metadata=liked_movies_metadata,
                favorite_genres=favorite_genres,
                query=query
            )
            
            # Map poster path to full TMDB asset URL if present (handling pandas NaN values)
            poster_path = movie.get("poster_path")
            if poster_path and isinstance(poster_path, str) and poster_path.strip() and poster_path.lower() != "nan":
                clean_path = poster_path.strip()
                if not clean_path.startswith("/"):
                    clean_path = "/" + clean_path
                poster_url = f"https://image.tmdb.org/t/p/w500{clean_path}"
            else:
                poster_url = None
            
            movie_rec = {
                "movie_id": movie["movie_id"],
                "title": movie["title"],
                "overview": movie["overview"],
                "genres": movie["genres"],
                "release_year": movie["release_date"].split("-")[0] if movie["release_date"] else None,
                "runtime": movie["runtime"],
                "vote_average": movie["vote_average"],
                "poster_url": poster_url,
                "score": round(movie["score"], 4),
                "explanation": explanation,
                "score_breakdown": {k: round(v, 4) for k, v in movie["score_breakdown"].items()}
            }
            final_recommendations.append(movie_rec)
            
        explanation_latency = (time.time() - t3) * 1000
        total_latency = (time.time() - start_time) * 1000

        return {
            "recommendations": final_recommendations,
            "metadata": {
                "strategy": strategy,
                "candidate_count": candidate_count,
                "weights_used": weights,
                "latency_ms": {
                    "ranking": round(ranking_latency, 2),
                    "diversity": round(diversity_latency, 2),
                    "explanation": round(explanation_latency, 2),
                    "total": round(total_latency, 2)
                }
            }
        }
