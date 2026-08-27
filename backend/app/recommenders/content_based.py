import os
import pandas as pd
import numpy as np
import json
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommender:
    def __init__(self):
        self.movies_df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.movie_id_to_idx = {}
        self.idx_to_movie_id = {}
        
        # Dense embeddings (Sentence Transformers)
        self.embeddings = None
        self.use_dense = False

    def load_data(self, movies_df: pd.DataFrame, embeddings: Optional[np.ndarray] = None):
        """Load movies dataframe and pre-calculated embeddings if available."""
        self.movies_df = movies_df.copy()
        
        # Handle parsed columns that are serialized as JSON strings
        for col in ["genres", "keywords", "cast"]:
            if col in self.movies_df.columns:
                self.movies_df[col] = self.movies_df[col].apply(
                    lambda x: json.loads(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
                )
        
        # Setup ID mappings
        self.movie_id_to_idx = {row["movieId"]: idx for idx, row in self.movies_df.iterrows()}
        self.idx_to_movie_id = {idx: row["movieId"] for idx, row in self.movies_df.iterrows()}
        
        # Compute "soup" for TF-IDF vectorizer
        print("Building content metadata soup...")
        def create_soup(row):
            genres = " ".join(row.get("genres", []))
            keywords = " ".join(row.get("keywords", []))
            cast = " ".join(row.get("cast", []))
            director = str(row.get("director", ""))
            overview = str(row.get("overview", ""))
            return f"{overview} {genres} {keywords} {cast} {director}"

        self.movies_df["soup"] = self.movies_df.apply(create_soup, axis=1)
        
        # Fit TF-IDF Vectorizer
        print("Fitting TF-IDF Vectorizer...")
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.movies_df["soup"])
        
        # Setup dense embeddings if provided
        if embeddings is not None and len(embeddings) == len(self.movies_df):
            self.embeddings = embeddings
            self.use_dense = True
            print("Loaded dense semantic embeddings.")
        else:
            self.use_dense = False
            print("Dense embeddings not provided. Relying on TF-IDF baseline.")

    def get_movie_vector(self, movie_id: int) -> np.ndarray:
        """Get the vector representation of a movie (dense or TF-IDF)."""
        idx = self.movie_id_to_idx.get(movie_id)
        if idx is None:
            return None
        
        if self.use_dense:
            return self.embeddings[idx]
        else:
            return self.tfidf_matrix[idx].toarray()[0]

    def build_user_preference_vector(self, liked_ids: List[int], disliked_ids: List[int]) -> np.ndarray:
        """
        Build user preference vector as:
        weighted average of liked movies minus weighted influence of disliked movies.
        """
        vector_dim = self.embeddings.shape[1] if self.use_dense else self.tfidf_matrix.shape[1]
        user_vector = np.zeros(vector_dim)
        
        liked_vectors = []
        for mid in liked_ids:
            vec = self.get_movie_vector(mid)
            if vec is not None:
                liked_vectors.append(vec)
                
        disliked_vectors = []
        for mid in disliked_ids:
            vec = self.get_movie_vector(mid)
            if vec is not None:
                disliked_vectors.append(vec)
                
        # Aggregate liked vectors (weight 1.0)
        if liked_vectors:
            user_vector += np.mean(liked_vectors, axis=0)
            
        # Subtract disliked vectors (weight 0.5 to prevent overpowering)
        if disliked_vectors:
            user_vector -= 0.5 * np.mean(disliked_vectors, axis=0)
            
        return user_vector

    def recommend(
        self, 
        liked_ids: List[int], 
        disliked_ids: List[int], 
        favorite_genres: List[str], 
        limit: int = 100
    ) -> List[Tuple[int, float]]:
        """
        Recommend items based on content similarity to the user preference vector.
        Returns a list of (movieId, similarity_score).
        """
        if not self.movie_id_to_idx:
            return []
            
        # Build user preference vector
        user_vector = self.build_user_preference_vector(liked_ids, disliked_ids)
        
        # If the user profile is empty, fallback to 0 similarity scores for all items
        if np.all(user_vector == 0):
            scores = np.zeros(len(self.movies_df))
        else:
            # Reshape user vector for similarity calculation
            user_vector_reshaped = user_vector.reshape(1, -1)
            
            # Compute similarity
            if self.use_dense:
                # Cosine similarity for dense vectors
                # Normalize user vector
                norm_user = np.linalg.norm(user_vector_reshaped)
                if norm_user > 0:
                    user_vector_norm = user_vector_reshaped / norm_user
                else:
                    user_vector_norm = user_vector_reshaped
                
                scores = cosine_similarity(user_vector_norm, self.embeddings)[0]
            else:
                # Cosine similarity for sparse TF-IDF
                # tfidf_matrix is already normalized
                scores = cosine_similarity(user_vector_reshaped, self.tfidf_matrix)[0]

        # Filter out already liked/disliked items
        exclude_ids = set(liked_ids + disliked_ids)
        
        recommendations = []
        for idx, row in self.movies_df.iterrows():
            movie_id = row["movieId"]
            if movie_id in exclude_ids:
                continue
                
            # Content score normalized between 0 and 1
            content_score = float(scores[idx])
            content_score = max(0.0, min(1.0, (content_score + 1.0) / 2.0)) if self.use_dense else float(content_score)
            
            recommendations.append((movie_id, content_score))
            
        # Sort by content similarity score descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]

    def get_genre_similarity(self, movie_genres: List[str], favorite_genres: List[str]) -> float:
        """Calculate the percentage of favorite genres matching the movie's genres."""
        if not favorite_genres or not movie_genres:
            return 0.0
        
        matched = set(movie_genres).intersection(set(favorite_genres))
        return len(matched) / len(favorite_genres)
