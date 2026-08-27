import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.core.config import settings
from backend.app.recommenders.content_based import ContentBasedRecommender

class DiversityReranker:
    def __init__(self, content_recommender: ContentBasedRecommender):
        self.content_recommender = content_recommender

    def rerank(
        self,
        candidates: List[Dict[str, Any]],
        diversity_mode: str = "balanced",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Re-ranks recommendation candidates using Maximal Marginal Relevance (MMR).
        MMR Score = lambda * relevance_score - (1 - lambda) * max_similarity_to_selected
        """
        # Map mode to lambda (relevance weight)
        # Focused = 1.0 (no diversity penalty)
        # Balanced = 0.5 (equal balance)
        # Exploratory = 0.2 (strong diversity penalty)
        diversity_lambda_map = {
            "focused": 1.0,
            "balanced": 0.5,
            "exploratory": 0.2
        }
        
        lam = diversity_lambda_map.get(diversity_mode.lower(), 0.5)
        
        # If diversity is set to Focused (lambda = 1.0), simply return top limit items
        if lam >= 1.0 or not candidates:
            return candidates[:limit]
            
        # Get content vectors for candidates to compute similarities
        # We will only look at the top 100 candidates to keep calculations very fast (<10ms)
        pool_size = min(100, len(candidates))
        pool = candidates[:pool_size]
        
        selected: List[Dict[str, Any]] = []
        
        # 1. Select the top candidate (purely by relevance) to seed the list
        first_item = pool.pop(0)
        selected.append(first_item)
        
        # Cache vectors for fast lookup
        vector_cache = {}
        for item in pool + [first_item]:
            mid = item["movie_id"]
            vector_cache[mid] = self.content_recommender.get_movie_vector(mid)

        # 2. Select remaining items iteratively using MMR
        while len(selected) < limit and pool:
            best_mmr = -float("inf")
            best_idx = -1
            
            for i, candidate in enumerate(pool):
                mid = candidate["movie_id"]
                relevance = candidate["score"]
                
                c_vec = vector_cache.get(mid)
                if c_vec is None:
                    # If vector is missing, fallback to 0 similarity
                    max_sim = 0.0
                else:
                    # Compute max similarity to any already selected item
                    sims = []
                    for sel_item in selected:
                        sel_mid = sel_item["movie_id"]
                        sel_vec = vector_cache.get(sel_mid)
                        
                        if sel_vec is not None and c_vec is not None:
                            # Cosine similarity between candidate and selected item
                            # Reshape for sklearn
                            sim = cosine_similarity(c_vec.reshape(1, -1), sel_vec.reshape(1, -1))[0][0]
                            sims.append(sim)
                        else:
                            sims.append(0.0)
                    
                    max_sim = max(sims) if sims else 0.0
                
                # MMR Formula: lambda * relevance - (1 - lambda) * max_similarity
                mmr_score = lam * relevance - (1 - lam) * max_sim
                
                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    best_idx = i
            
            if best_idx != -1:
                selected.append(pool.pop(best_idx))
            else:
                break
                
        # If we need more items than were in the MMR pool, fill with remainder of original sorted candidates
        if len(selected) < limit:
            remaining_candidates = [c for c in candidates if c["movie_id"] not in [s["movie_id"] for s in selected]]
            selected.extend(remaining_candidates[:(limit - len(selected))])
            
        return selected
