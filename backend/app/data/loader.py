import os
import pandas as pd
import numpy as np
import json
from typing import Tuple, Dict, Any
from backend.app.core.config import settings

class DataLoader:
    def __init__(self, use_sample: bool = False):
        self.use_sample = use_sample
        self.movies_df = None
        self.ratings_df = None
        
        # Directory configuration
        self.data_dir = settings.PROCESSED_DATA_DIR if not use_sample else os.path.join(settings.DATA_DIR, "sample")
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load movies and ratings from files."""
        movies_path = os.path.join(self.data_dir, "movies_metadata.csv")
        ratings_path = os.path.join(self.data_dir, "ratings.csv")
        
        if not os.path.exists(movies_path) or not os.path.exists(ratings_path):
            raise FileNotFoundError(
                f"Processed data files not found in {self.data_dir}. "
                "Please run scripts/prepare_data.py first."
            )
            
        print(f"Loading metadata from {movies_path}...")
        self.movies_df = pd.read_csv(movies_path)
        
        print(f"Loading ratings from {ratings_path}...")
        self.ratings_df = pd.read_csv(ratings_path)
        
        # Precompute popularity and quality priors
        self._compute_priors()
        
        return self.movies_df, self.ratings_df

    def _compute_priors(self):
        """Compute and normalize popularity and quality signals for each movie."""
        print("Computing popularity and quality priors...")
        
        # Calculate review counts and averages from the collaborative ratings
        rating_stats = self.ratings_df.groupby("movieId").agg(
            rating_count=("rating", "count"),
            rating_avg=("rating", "mean")
        ).reset_index()
        
        # Merge stats into movies metadata dataframe
        self.movies_df = pd.merge(self.movies_df, rating_stats, on="movieId", how="left")
        
        # Fill NaNs for movies without reviews (if any)
        self.movies_df["rating_count"] = self.movies_df["rating_count"].fillna(0)
        self.movies_df["rating_avg"] = self.movies_df["rating_avg"].fillna(self.ratings_df["rating"].mean() if len(self.ratings_df) > 0 else 3.0)
        
        # 1. Normalize TMDB popularity
        pop_max = self.movies_df["popularity"].max()
        pop_min = self.movies_df["popularity"].min()
        if pop_max > pop_min:
            self.movies_df["popularity_norm"] = (self.movies_df["popularity"] - pop_min) / (pop_max - pop_min)
        else:
            self.movies_df["popularity_norm"] = 0.5
            
        # 2. Normalize Rating Count (Collaborative Popularity)
        count_max = self.movies_df["rating_count"].max()
        count_min = self.movies_df["rating_count"].min()
        if count_max > count_min:
            self.movies_df["rating_count_norm"] = (self.movies_df["rating_count"] - count_min) / (count_max - count_min)
        else:
            self.movies_df["rating_count_norm"] = 0.5
            
        # Combine TMDB popularity and Rating Count for a single Popularity Score (weighted 40/60)
        self.movies_df["popularity_score"] = 0.4 * self.movies_df["popularity_norm"] + 0.6 * self.movies_df["rating_count_norm"]
        
        # 3. Normalize Quality (Average Rating)
        # Use Bayesian average or simple min-max scaling. Let's do a simple min-max scaling
        avg_max = self.movies_df["rating_avg"].max()
        avg_min = self.movies_df["rating_avg"].min()
        if avg_max > avg_min:
            self.movies_df["quality_score"] = (self.movies_df["rating_avg"] - avg_min) / (avg_max - avg_min)
        else:
            self.movies_df["quality_score"] = 0.5
            
        print("Priors computed successfully.")
