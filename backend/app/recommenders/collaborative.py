import numpy as np
import pandas as pd
import pickle
from typing import List, Dict, Tuple, Optional

class CollaborativeRecommender:
    def __init__(self, k: int = 20, lr: float = 0.005, reg: float = 0.02):
        self.k = k
        self.lr = lr
        self.reg = reg
        
        # Latent factor factors & biases
        self.global_bias = 3.5
        self.user_biases = {}
        self.movie_biases = {}
        self.user_factors = None # shape: (U, K)
        self.movie_factors = None # shape: (I, K)
        
        # ID mappings
        self.user_to_idx = {}
        self.idx_to_user = {}
        self.movie_to_idx = {}
        self.idx_to_movie = {}
        
        # Keep list of unique movie ids
        self.all_movie_ids = []

    def fit(self, ratings_df: pd.DataFrame, epochs: int = 15, verbose: bool = True):
        """Train standard Funk SVD on the user-item interaction matrix."""
        print("Initializing SVD training data mappings...")
        unique_users = ratings_df["userId"].unique()
        unique_movies = ratings_df["movieId"].unique()
        
        self.all_movie_ids = list(unique_movies)
        
        self.user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
        self.idx_to_user = {idx: uid for uid, idx in self.user_to_idx.items()}
        self.movie_to_idx = {mid: idx for idx, mid in enumerate(unique_movies)}
        self.idx_to_movie = {idx: mid for mid, idx in self.movie_to_idx.items()}
        
        U = len(unique_users)
        I = len(unique_movies)
        
        # Initialize biases
        self.global_bias = float(ratings_df["rating"].mean())
        
        # Initialize bias dicts for all known items
        self.user_biases = {uid: 0.0 for uid in unique_users}
        self.movie_biases = {mid: 0.0 for mid in unique_movies}
        
        # Initialize latent matrices
        self.user_factors = np.random.normal(0, 0.1, (U, self.k))
        self.movie_factors = np.random.normal(0, 0.1, (I, self.k))
        
        # Extract columns as numpy arrays for speed
        users = ratings_df["userId"].map(self.user_to_idx).values
        movies = ratings_df["movieId"].map(self.movie_to_idx).values
        ratings = ratings_df["rating"].values
        
        print(f"Training Funk SVD with {U} users, {I} movies, {len(ratings)} interactions...")
        
        for epoch in range(epochs):
            # Shuffle indices
            indices = np.arange(len(ratings))
            np.random.shuffle(indices)
            
            squared_errors = []
            
            for idx in indices:
                u_idx = users[idx]
                i_idx = movies[idx]
                r = ratings[idx]
                
                uid = self.idx_to_user[u_idx]
                mid = self.idx_to_movie[i_idx]
                
                bu = self.user_biases[uid]
                bi = self.movie_biases[mid]
                
                p_u = self.user_factors[u_idx]
                q_i = self.movie_factors[i_idx]
                
                # Predict
                r_pred = self.global_bias + bu + bi + np.dot(p_u, q_i)
                err = r - r_pred
                squared_errors.append(err ** 2)
                
                # Update biases
                self.user_biases[uid] += self.lr * (err - self.reg * bu)
                self.movie_biases[mid] += self.lr * (err - self.reg * bi)
                
                # Update latent factors
                self.user_factors[u_idx] += self.lr * (err * q_i - self.reg * p_u)
                self.movie_factors[i_idx] += self.lr * (err * p_u - self.reg * q_i)
                
            rmse = np.sqrt(np.mean(squared_errors))
            if verbose and (epoch + 1) % 5 == 0:
                print(f"Epoch {epoch + 1}/{epochs} - Train RMSE: {rmse:.4f}")
                
        print("Funk SVD model training finished.")

    def predict(self, user_id: int, movie_id: int) -> float:
        """
        Predict ratings for a user-movie pair.
        Conceptual formula: prediction = global_bias + user_bias + movie_bias + (user_latent dot movie_latent).
        Supports cold-starts for new users/movies gracefully.
        """
        bu = self.user_biases.get(user_id, 0.0)
        bi = self.movie_biases.get(movie_id, 0.0)
        
        u_idx = self.user_to_idx.get(user_id)
        i_idx = self.movie_to_idx.get(movie_id)
        
        prediction = self.global_bias + bu + bi
        
        # If both user and movie are known, include latent factor interaction
        if u_idx is not None and i_idx is not None:
            prediction += np.dot(self.user_factors[u_idx], self.movie_factors[i_idx])
            
        # Clip to valid rating range [0.5, 5.0]
        return max(0.5, min(5.0, prediction))

    def recommend(
        self, 
        user_id: int, 
        liked_ids: List[int], 
        disliked_ids: List[int], 
        limit: int = 100
    ) -> List[Tuple[int, float]]:
        """
        Recommend movies for a user by scoring all items.
        Returns a list of (movieId, collaborative_score) where score is scaled between 0 and 1.
        """
        # If user is a complete cold-start user (no history in model), return 0 collaborative score
        is_new_user = user_id not in self.user_to_idx
        
        # Exclude watched or interacting movies
        exclude_ids = set(liked_ids + disliked_ids)
        
        recommendations = []
        for mid in self.all_movie_ids:
            if mid in exclude_ids:
                continue
                
            if is_new_user:
                # Cold start user gets collaborative score based only on movie bias (offset around 0.5)
                # Max collaborative bias is typically small, let's map it cleanly
                bi = self.movie_biases.get(mid, 0.0)
                # Map to [0, 1] range around global bias
                score = (self.global_bias + bi) / 5.0
            else:
                pred = self.predict(user_id, mid)
                score = pred / 5.0 # Normalize 1-5 stars rating to [0.0, 1.0]
                
            recommendations.append((mid, float(score)))
            
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]

    def save(self, filepath: str):
        """Save SVD weights to a file."""
        data = {
            "k": self.k,
            "lr": self.lr,
            "reg": self.reg,
            "global_bias": self.global_bias,
            "user_biases": self.user_biases,
            "movie_biases": self.movie_biases,
            "user_factors": self.user_factors,
            "movie_factors": self.movie_factors,
            "user_to_idx": self.user_to_idx,
            "movie_to_idx": self.movie_to_idx,
            "idx_to_user": self.idx_to_user,
            "idx_to_movie": self.idx_to_movie,
            "all_movie_ids": self.all_movie_ids
        }
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
        print(f"Collaborative model saved to {filepath}")

    def load(self, filepath: str):
        """Load SVD weights from a file."""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
            
        self.k = data["k"]
        self.lr = data["lr"]
        self.reg = data["reg"]
        self.global_bias = data["global_bias"]
        self.user_biases = data["user_biases"]
        self.movie_biases = data["movie_biases"]
        self.user_factors = data["user_factors"]
        self.movie_factors = data["movie_factors"]
        self.user_to_idx = data["user_to_idx"]
        self.movie_to_idx = data["movie_to_idx"]
        self.idx_to_user = data["idx_to_user"]
        self.idx_to_movie = data["idx_to_movie"]
        self.all_movie_ids = data["all_movie_ids"]
        print(f"Collaborative model loaded from {filepath}")
