import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from backend.app.core.config import settings
from backend.app.recommenders.content_based import ContentBasedRecommender
from backend.app.recommenders.collaborative import CollaborativeRecommender
from backend.app.recommenders.semantic import SemanticRecommender

class HybridRanker:
    def __init__(
        self,
        content_recommender: ContentBasedRecommender,
        collaborative_recommender: CollaborativeRecommender,
        semantic_recommender: SemanticRecommender
    ):
        self.content_recommender = content_recommender
        self.collaborative_recommender = collaborative_recommender
        self.semantic_recommender = semantic_recommender
        self.movies_df = None

    def load_data(self, movies_df: pd.DataFrame):
        self.movies_df = movies_df.copy()

    def get_user_strategy(self, liked_ids: List[int], disliked_ids: List[int]) -> Tuple[str, Dict[str, float]]:
        """Determine weight strategy based on user history length."""
        history_length = len(liked_ids) + len(disliked_ids)
        
        if history_length == 0:
            return "cold_start", settings.COLD_START_WEIGHTS.copy()
        elif history_length <= 3:
            return "sparse_history", settings.SPARSE_HISTORY_WEIGHTS.copy()
        else:
            return "hybrid_warm_user", settings.WARM_USER_WEIGHTS.copy()

    def recommend(
        self,
        user_id: int,
        liked_ids: List[int],
        disliked_ids: List[int],
        favorite_genres: List[str],
        query: Optional[str] = None,
        limit: int = 10
    ) -> Tuple[List[Dict[str, Any]], str, Dict[str, float]]:
        """
        Runs the full recommendation pipeline:
        1. Select weights based on history (cold start vs warm).
        2. Get raw scores from active modules.
        3. Normalize and combine scores.
        4. Return recommendations with detailed score breakdowns.
        """
        # 1. Determine Weight Strategy
        strategy, weights = self.get_user_strategy(liked_ids, disliked_ids)
        
        # If no query is provided, semantic score weight should be set to 0.0 and weights redistributed
        if not query:
            weights["semantic"] = 0.0
            
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

        # 2. Candidate Generation (gather top 300 candidates from all recommenders)
        candidate_ids = set()
        
        # Get content-based candidates
        content_candidates = self.content_recommender.recommend(liked_ids, disliked_ids, favorite_genres, limit=300)
        candidate_ids.update([cid for cid, _ in content_candidates])
        
        # Get collaborative candidates
        cf_candidates = self.collaborative_recommender.recommend(user_id, liked_ids, disliked_ids, limit=300)
        candidate_ids.update([cid for cid, _ in cf_candidates])
        
        # Get semantic candidates if query is present
        semantic_candidates = []
        if query:
            semantic_candidates = self.semantic_recommender.recommend(query, limit=300)
            candidate_ids.update([cid for cid, _ in semantic_candidates])
            
        # If the candidate pool is too small (e.g. cold start with no profile), fill with popular movies
        if len(candidate_ids) < 50:
            popular_ids = self.movies_df.nlargest(100, "popularity_score")["movieId"].tolist()
            candidate_ids.update(popular_ids)
            
        # Remove liked/disliked items from candidate pool
        exclude_ids = set(liked_ids + disliked_ids)
        candidate_ids = list(candidate_ids - exclude_ids)

        # 3. Fetch Raw Scores for Candidates
        # Convert candidate lists to dicts for fast lookup
        content_scores_dict = dict(content_candidates)
        cf_scores_dict = dict(cf_candidates)
        semantic_scores_dict = dict(semantic_candidates) if query else {}

        # Pre-filter movies_df to candidates only
        candidates_df = self.movies_df[self.movies_df["movieId"].isin(candidate_ids)].copy()

        # 4. Calculate Combined Hybrid Scores
        scored_candidates = []
        
        for _, row in candidates_df.iterrows():
            movie_id = int(row["movieId"])
            
            # Fetch component scores
            c_score = content_scores_dict.get(movie_id, 0.0)
            cf_score = cf_scores_dict.get(movie_id, 0.0)
            s_score = semantic_scores_dict.get(movie_id, 0.0)
            
            # Genre Match Score
            movie_genres = row.get("genres", [])
            if isinstance(movie_genres, str):
                movie_genres = eval(movie_genres)
            genre_score = self.content_recommender.get_genre_similarity(movie_genres, favorite_genres)
            
            # Prior popularity & quality scores
            quality_score = float(row.get("quality_score", 0.5))
            popularity_score = float(row.get("popularity_score", 0.1))
            
            # Weighted combination
            final_score = (
                weights["content"] * c_score +
                weights["collaborative"] * cf_score +
                weights["semantic"] * s_score +
                weights["genre"] * genre_score +
                weights["quality"] * quality_score +
                weights["popularity"] * popularity_score
            )
            
            # Build detailed breakdown
            score_breakdown = {
                "content": float(weights["content"] * c_score),
                "collaborative": float(weights["collaborative"] * cf_score),
                "semantic": float(weights["semantic"] * s_score),
                "genre": float(weights["genre"] * genre_score),
                "quality": float(weights["quality"] * quality_score),
                "popularity": float(weights["popularity"] * popularity_score)
            }
            
            # Re-normalize breakdown components so they sum to 1.0 (relative contributions to the final score)
            # If final_score is 0, distribute evenly based on active weights
            if final_score > 0:
                score_breakdown_normalized = {k: v / final_score for k, v in score_breakdown.items()}
            else:
                score_breakdown_normalized = {k: weights[k] for k in score_breakdown}
                
            scored_candidates.append({
                "movie_id": movie_id,
                "title": row["title"],
                "overview": row["overview"],
                "genres": movie_genres,
                "release_date": row["release_date"],
                "runtime": float(row["runtime"]) if not pd.isna(row["runtime"]) else None,
                "vote_average": float(row["vote_average"]) if not pd.isna(row["vote_average"]) else None,
                "popularity_score": popularity_score,
                "quality_score": quality_score,
                "score": float(final_score),
                "score_breakdown": score_breakdown_normalized
            })

        # Sort by hybrid score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_candidates, strategy, weights
