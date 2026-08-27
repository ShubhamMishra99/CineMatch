import re
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.core.config import settings
from backend.app.recommenders.content_based import ContentBasedRecommender

class SemanticRecommender:
    def __init__(self, content_recommender: ContentBasedRecommender):
        self.content_recommender = content_recommender
        self.movies_df = None
        self.dense_model = None
        
        # Heuristic rules for keyword filter detection
        self.genre_keywords = {
            "action": ["action", "fight", "explosion", "shoot", "adventure"],
            "adventure": ["adventure", "quest", "explore", "journey", "travel"],
            "animation": ["animation", "cartoon", "animated", "anime", "disney", "pixar"],
            "comedy": ["comedy", "funny", "laugh", "hilarious", "humor", "lighthearted"],
            "crime": ["crime", "police", "detective", "heist", "mafia", "gangster"],
            "documentary": ["documentary", "real life", "true story", "biography"],
            "drama": ["drama", "emotional", "sad", "tearjerker", "intense", "relationship"],
            "family": ["family", "kids", "children", "disney"],
            "fantasy": ["fantasy", "magic", "sword", "wizard", "elf", "myth"],
            "history": ["history", "historical", "war", "biography", "period drama"],
            "horror": ["horror", "scary", "ghost", "monster", "creepy", "blood"],
            "music": ["music", "musical", "song", "singer", "band"],
            "mystery": ["mystery", "puzzle", "solve", "whodunit", "secret"],
            "romance": ["romance", "romantic", "love", "date", "relationship"],
            "science fiction": ["sci-fi", "science fiction", "space", "alien", "robot", "future", "time travel"],
            "thriller": ["thriller", "suspense", "tension", "psychological", "mystery"],
            "war": ["war", "soldier", "battle", "military"],
            "western": ["western", "cowboy", "sheriff", "horse"]
        }

    def load_data(self, movies_df: pd.DataFrame):
        self.movies_df = movies_df.copy()
        
        # Loading SentenceTransformer also installs/loads PyTorch, which exceeds
        # the memory available on common free hosting plans. TF-IDF remains a
        # fully functional semantic-search fallback and is the safe default.
        if settings.ENABLE_SEMANTIC_MODEL and self.content_recommender.use_dense:
            try:
                from sentence_transformers import SentenceTransformer
                print("Loading SentenceTransformer model for query encoding...")
                self.dense_model = SentenceTransformer("all-MiniLM-L6-v2")
                print("Dense query encoder loaded.")
            except Exception as e:
                print(f"Failed to load dense query encoder: {e}. Falling back to TF-IDF search.")
                self.dense_model = None
        else:
            print("Using lightweight TF-IDF semantic search.")

    def extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract structured keyword heuristics from the natural language query."""
        query_lower = query.lower()
        filters = {
            "genres": [],
            "duration": None,  # "short" (<100m) or "long" (>130m)
            "period": None,    # "recent" (>=2010) or "classic" (<2000)
            "popularity": None, # "popular" or "hidden_gem"
            "mood": []          # "funny", "dark", "emotional"
        }
        
        # Detect genres
        for genre, keywords in self.genre_keywords.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', query_lower):
                    filters["genres"].append(genre.title())
                    break
                    
        # Detect duration limits
        if any(w in query_lower for w in ["short", "quick", "under 2 hours", "under 100 mins"]):
            filters["duration"] = "short"
        elif any(w in query_lower for w in ["long", "epic", "marathon", "over 2 hours"]):
            filters["duration"] = "long"
            
        # Detect period limits
        if any(w in query_lower for w in ["recent", "new", "modern", "latest", "contemporary"]):
            filters["period"] = "recent"
        elif any(w in query_lower for w in ["classic", "old", "vintage", "retro"]):
            filters["period"] = "classic"
            
        # Detect popularity / niche limits
        if any(w in query_lower for w in ["popular", "famous", "blockbuster", "well known", "hit"]):
            filters["popularity"] = "popular"
        elif any(w in query_lower for w in ["hidden gem", "niche", "underrated", "unknown", "obscure"]):
            filters["popularity"] = "hidden_gem"
            
        # Detect moods
        if any(w in query_lower for w in ["funny", "hilarious", "comedy", "laugh", "humorous"]):
            filters["mood"].append("funny")
        if any(w in query_lower for w in ["dark", "psychological", "creepy", "scary", "disturbing"]):
            filters["mood"].append("dark")
        if any(w in query_lower for w in ["emotional", "sad", "moving", "touching", "tearjerker"]):
            filters["mood"].append("emotional")
            
        return filters

    def recommend(self, query: str, limit: int = 100) -> List[Tuple[int, float]]:
        """
        Calculates cosine similarity between query and all movie descriptions.
        Applies heuristic filters as soft boosts to the base semantic score.
        """
        if not query or self.movies_df is None:
            return []
            
        # 1. Base Semantic Similarity Score
        if self.dense_model and self.content_recommender.use_dense:
            # Dense SBERT Query encoding
            query_vector = self.dense_model.encode([query])[0].reshape(1, -1)
            # Normalize vector
            norm_q = np.linalg.norm(query_vector)
            if norm_q > 0:
                query_vector = query_vector / norm_q
            scores = cosine_similarity(query_vector, self.content_recommender.embeddings)[0]
            # Map cosine similarity [-1, 1] to [0, 1]
            scores = (scores + 1.0) / 2.0
        else:
            # TF-IDF query encoding fallback
            query_vector = self.content_recommender.vectorizer.transform([query])
            scores = cosine_similarity(query_vector, self.content_recommender.tfidf_matrix)[0]

        # 2. Extract and Apply Soft Heuristic Filters
        filters = self.extract_filters(query)
        
        recommendations = []
        for idx, row in self.movies_df.iterrows():
            movie_id = row["movieId"]
            base_score = float(scores[idx])
            
            # Apply soft boosts for heuristic filters (max +0.1 per matching filter, capped at 1.0)
            boost = 0.0
            
            # Genre boost (+0.05 per matching genre in query)
            movie_genres = row.get("genres", [])
            if isinstance(movie_genres, str):
                movie_genres = eval(movie_genres)
            if filters["genres"] and movie_genres:
                matched_genres = set(movie_genres).intersection(set(filters["genres"]))
                boost += 0.05 * len(matched_genres)
                
            # Duration boost
            runtime = row.get("runtime", 120.0)
            if filters["duration"] == "short" and runtime < 100:
                boost += 0.08
            elif filters["duration"] == "long" and runtime > 130:
                boost += 0.08
                
            # Period boost
            release_date = str(row.get("release_date", ""))
            try:
                year = int(release_date.split("-")[0]) if release_date else 2000
                if filters["period"] == "recent" and year >= 2010:
                    boost += 0.08
                elif filters["period"] == "classic" and year < 2000:
                    boost += 0.08
            except Exception:
                pass
                
            # Popularity boost
            pop_score = row.get("popularity_score", 0.1)
            qual_score = row.get("quality_score", 0.5)
            if filters["popularity"] == "popular" and pop_score > 0.3:
                boost += 0.08
            elif filters["popularity"] == "hidden_gem" and pop_score < 0.15 and qual_score > 0.7:
                boost += 0.10
                
            # Mood boost
            movie_overview = str(row.get("overview", "")).lower()
            if "funny" in filters["mood"] and any(w in movie_overview for w in ["funny", "laugh", "comic", "hilarious", "humor"]):
                boost += 0.05
            if "dark" in filters["mood"] and any(w in movie_overview for w in ["dark", "grim", "psychological", "creepy", "horror"]):
                boost += 0.05
            if "emotional" in filters["mood"] and any(w in movie_overview for w in ["emotional", "touching", "sad", "moving", "melodrama"]):
                boost += 0.05
                
            final_score = min(1.0, base_score + boost)
            recommendations.append((movie_id, final_score))
            
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]
