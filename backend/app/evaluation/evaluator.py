import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import train_test_split
from backend.app.recommenders.content_based import ContentBasedRecommender
from backend.app.recommenders.collaborative import CollaborativeRecommender
from backend.app.recommenders.hybrid import HybridRanker
from backend.app.recommenders.semantic import SemanticRecommender
from backend.app.evaluation.metrics import precision_at_k, recall_at_k, ndcg_at_k, catalog_coverage, intra_list_diversity

class Evaluator:
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()
        self.catalog_size = len(movies_df)
        
        # Split ratings (80/20 split)
        print("Creating train/test interaction splits...")
        self.train_ratings, self.test_ratings = train_test_split(
            self.ratings_df, test_size=0.2, random_state=42
        )
        
        # Identify users with enough interactions in both train and test splits for validation
        user_counts_train = self.train_ratings.groupby("userId")["movieId"].count()
        user_counts_test = self.test_ratings.groupby("userId")["movieId"].count()
        
        # Test users are those who liked at least 3 movies in train and have at least 3 test movies
        # We define a "like" as rating >= 4.0
        train_likes = self.train_ratings[self.train_ratings["rating"] >= 4.0]
        test_likes = self.test_ratings[self.test_ratings["rating"] >= 4.0]
        
        valid_train_users = set(train_likes["userId"].unique())
        valid_test_users = set(test_likes["userId"].unique())
        
        self.eval_users = list(valid_train_users.intersection(valid_test_users))
        print(f"Total evaluation users available: {len(self.eval_users)}")
        
        # Setup models
        self.content_rec = ContentBasedRecommender()
        self.collaborative_rec = CollaborativeRecommender()
        self.semantic_rec = SemanticRecommender(self.content_rec)
        
        # Initialize content recommender
        self.content_rec.load_data(self.movies_df)
        
        # Build cache of movie content vectors for diversity calculation
        self.movie_vectors = {}
        for idx, row in self.movies_df.iterrows():
            mid = row["movieId"]
            self.movie_vectors[mid] = self.content_rec.get_movie_vector(mid)

    def evaluate_popularity_baseline(self, test_users: List[int], k: int = 10) -> Dict[str, float]:
        """Evaluate Popularity Baseline (recommends top popular movies)."""
        print("Evaluating Popularity Baseline...")
        start_time = time.time()
        
        # Precompute top popular movies excluding those user rated in train
        popular_movies = self.movies_df.nlargest(100, "popularity_score")["movieId"].tolist()
        
        all_recs = []
        precisions, recalls, ndcgs, diversities = [], [], [], []
        
        for uid in test_users:
            # Get user training movies to exclude them
            user_train_movies = set(self.train_ratings[self.train_ratings["userId"] == uid]["movieId"])
            user_test_likes = set(self.test_ratings[(self.test_ratings["userId"] == uid) & (self.test_ratings["rating"] >= 4.0)]["movieId"])
            
            # Recommendation: top popular movies user hasn't rated in training
            recs = [mid for mid in popular_movies if mid not in user_train_movies][:k]
            all_recs.append(recs)
            
            # Calculate metrics
            precisions.append(precision_at_k(recs, user_test_likes, k))
            recalls.append(recall_at_k(recs, user_test_likes, k))
            ndcgs.append(ndcg_at_k(recs, user_test_likes, k))
            diversities.append(intra_list_diversity(recs, self.movie_vectors))
            
        latency = ((time.time() - start_time) / len(test_users)) * 1000
        
        return {
            "Precision@K": float(np.mean(precisions)),
            "Recall@K": float(np.mean(recalls)),
            "NDCG@K": float(np.mean(ndcgs)),
            "Coverage": float(catalog_coverage(all_recs, self.catalog_size)),
            "Diversity": float(np.mean(diversities)),
            "Latency (ms)": latency
        }

    def evaluate_content_baseline(self, test_users: List[int], k: int = 10) -> Dict[str, float]:
        """Evaluate Content-Based Baseline."""
        print("Evaluating Content-Based...")
        start_time = time.time()
        
        all_recs = []
        precisions, recalls, ndcgs, diversities = [], [], [], []
        
        for uid in test_users:
            user_train = self.train_ratings[self.train_ratings["userId"] == uid]
            liked_train_ids = user_train[user_train["rating"] >= 4.0]["movieId"].tolist()
            disliked_train_ids = user_train[user_train["rating"] < 3.0]["movieId"].tolist()
            
            user_test_likes = set(self.test_ratings[(self.test_ratings["userId"] == uid) & (self.test_ratings["rating"] >= 4.0)]["movieId"])
            
            # Generate recommendations
            recs_tuples = self.content_rec.recommend(liked_train_ids, disliked_train_ids, [], limit=k)
            recs = [mid for mid, _ in recs_tuples]
            all_recs.append(recs)
            
            # Calculate metrics
            precisions.append(precision_at_k(recs, user_test_likes, k))
            recalls.append(recall_at_k(recs, user_test_likes, k))
            ndcgs.append(ndcg_at_k(recs, user_test_likes, k))
            diversities.append(intra_list_diversity(recs, self.movie_vectors))
            
        latency = ((time.time() - start_time) / len(test_users)) * 1000
        
        return {
            "Precision@K": float(np.mean(precisions)),
            "Recall@K": float(np.mean(recalls)),
            "NDCG@K": float(np.mean(ndcgs)),
            "Coverage": float(catalog_coverage(all_recs, self.catalog_size)),
            "Diversity": float(np.mean(diversities)),
            "Latency (ms)": latency
        }

    def evaluate_collaborative_baseline(self, test_users: List[int], k: int = 10) -> Dict[str, float]:
        """Evaluate Collaborative Filtering SVD."""
        print("Evaluating Collaborative Filtering...")
        
        # Train SVD on training set only
        svd = CollaborativeRecommender()
        svd.fit(self.train_ratings, epochs=20, verbose=False)
        
        start_time = time.time()
        all_recs = []
        precisions, recalls, ndcgs, diversities = [], [], [], []
        
        for uid in test_users:
            user_train = self.train_ratings[self.train_ratings["userId"] == uid]
            liked_train_ids = user_train[user_train["rating"] >= 4.0]["movieId"].tolist()
            disliked_train_ids = user_train[user_train["rating"] < 3.0]["movieId"].tolist()
            
            user_test_likes = set(self.test_ratings[(self.test_ratings["userId"] == uid) & (self.test_ratings["rating"] >= 4.0)]["movieId"])
            
            # Generate recommendations
            recs_tuples = svd.recommend(uid, liked_train_ids, disliked_train_ids, limit=k)
            recs = [mid for mid, _ in recs_tuples]
            all_recs.append(recs)
            
            # Calculate metrics
            precisions.append(precision_at_k(recs, user_test_likes, k))
            recalls.append(recall_at_k(recs, user_test_likes, k))
            ndcgs.append(ndcg_at_k(recs, user_test_likes, k))
            diversities.append(intra_list_diversity(recs, self.movie_vectors))
            
        latency = ((time.time() - start_time) / len(test_users)) * 1000
        
        return {
            "Precision@K": float(np.mean(precisions)),
            "Recall@K": float(np.mean(recalls)),
            "NDCG@K": float(np.mean(ndcgs)),
            "Coverage": float(catalog_coverage(all_recs, self.catalog_size)),
            "Diversity": float(np.mean(diversities)),
            "Latency (ms)": latency
        }

    def evaluate_hybrid(self, test_users: List[int], k: int = 10) -> Dict[str, float]:
        """Evaluate Hybrid Recommender (combines all models)."""
        print("Evaluating Hybrid Recommender...")
        
        # Train SVD on training set only
        svd = CollaborativeRecommender()
        svd.fit(self.train_ratings, epochs=20, verbose=False)
        
        hybrid = HybridRanker(self.content_rec, svd, self.semantic_rec)
        hybrid.load_data(self.movies_df)
        
        start_time = time.time()
        all_recs = []
        precisions, recalls, ndcgs, diversities = [], [], [], []
        
        for uid in test_users:
            user_train = self.train_ratings[self.train_ratings["userId"] == uid]
            liked_train_ids = user_train[user_train["rating"] >= 4.0]["movieId"].tolist()
            disliked_train_ids = user_train[user_train["rating"] < 3.0]["movieId"].tolist()
            
            user_test_likes = set(self.test_ratings[(self.test_ratings["userId"] == uid) & (self.test_ratings["rating"] >= 4.0)]["movieId"])
            
            # Recommend
            recs_dicts, _, _ = hybrid.recommend(
                user_id=uid,
                liked_ids=liked_train_ids,
                disliked_ids=disliked_train_ids,
                favorite_genres=[],
                query=None,
                limit=k
            )
            recs = [item["movie_id"] for item in recs_dicts[:k]]
            all_recs.append(recs)
            
            # Calculate metrics
            precisions.append(precision_at_k(recs, user_test_likes, k))
            recalls.append(recall_at_k(recs, user_test_likes, k))
            ndcgs.append(ndcg_at_k(recs, user_test_likes, k))
            diversities.append(intra_list_diversity(recs, self.movie_vectors))
            
        latency = ((time.time() - start_time) / len(test_users)) * 1000
        
        return {
            "Precision@K": float(np.mean(precisions)),
            "Recall@K": float(np.mean(recalls)),
            "NDCG@K": float(np.mean(ndcgs)),
            "Coverage": float(catalog_coverage(all_recs, self.catalog_size)),
            "Diversity": float(np.mean(diversities)),
            "Latency (ms)": latency
        }

    def run_comparison(self, sample_size: int = 100) -> pd.DataFrame:
        """Run standard evaluation split comparison across 4 configurations."""
        # Restrict test users to sample size to keep execution time fast (<10s)
        np.random.seed(42)
        test_users = list(np.random.choice(self.eval_users, min(sample_size, len(self.eval_users)), replace=False))
        print(f"Running evaluation metrics simulation across {len(test_users)} sample users...")
        
        results = {}
        
        results["Popularity"] = self.evaluate_popularity_baseline(test_users)
        results["Content-Based"] = self.evaluate_content_baseline(test_users)
        results["Collaborative"] = self.evaluate_collaborative_baseline(test_users)
        results["Hybrid"] = self.evaluate_hybrid(test_users)
        
        df = pd.DataFrame(results).T
        return df
