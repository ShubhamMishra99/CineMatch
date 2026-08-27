from typing import List, Dict, Any, Optional

class ExplanationService:
    def __init__(self, movies_df: Optional[Any] = None):
        self.movies_df = movies_df

    def set_movies_df(self, movies_df: Any):
        self.movies_df = movies_df

    def find_most_similar_liked_movie(self, movie_genres: List[str], liked_movies: List[Dict[str, Any]]) -> Optional[str]:
        """Find the movie in the user's liked list that shares the most genres with the target movie."""
        if not liked_movies or not movie_genres:
            return None
            
        best_title = None
        max_overlap = -1
        
        for liked in liked_movies:
            liked_genres = liked.get("genres", [])
            # Handle potential string-serialized genres
            if isinstance(liked_genres, str):
                try:
                    liked_genres = eval(liked_genres)
                except Exception:
                    liked_genres = []
            
            overlap = len(set(movie_genres).intersection(set(liked_genres)))
            if overlap > max_overlap:
                max_overlap = overlap
                best_title = liked.get("title")
                
        return best_title

    def generate_explanation(
        self,
        movie: Dict[str, Any],
        liked_movies_metadata: List[Dict[str, Any]],
        favorite_genres: List[str],
        query: Optional[str] = None
    ) -> str:
        """
        Translates raw score contributions from the recommender breakdown into a human-readable summary.
        Example breakdown keys: 'content', 'collaborative', 'semantic', 'genre', 'quality', 'popularity'.
        """
        breakdown = movie.get("score_breakdown", {})
        movie_genres = movie.get("genres", [])
        movie_title = movie.get("title", "")
        
        # Sort breakdown categories by their contribution to the score
        sorted_factors = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        top_factor, top_val = sorted_factors[0] if len(sorted_factors) > 0 else ("quality", 1.0)
        second_factor, second_val = sorted_factors[1] if len(sorted_factors) > 1 else ("popularity", 0.0)
        
        reasons = []
        
        # Helper variables
        similar_liked_title = self.find_most_similar_liked_movie(movie_genres, liked_movies_metadata)
        
        # Formulate primary reason
        if top_factor == "content" and similar_liked_title:
            reasons.append(f"it shares similar themes, genres, and style with '{similar_liked_title}' which you liked")
        elif top_factor == "collaborative":
            reasons.append("it is highly rated by viewers who share your movie tastes")
        elif top_factor == "semantic" and query:
            reasons.append(f"it matches your request for a '{query}'")
        elif top_factor == "genre":
            matched_genres = list(set(movie_genres).intersection(set(favorite_genres)))
            if matched_genres:
                genre_str = ", ".join(matched_genres[:2])
                reasons.append(f"it aligns with your interest in {genre_str} movies")
            else:
                reasons.append("it matches your selected genre preferences")
        elif top_factor == "quality":
            reasons.append("it is critically acclaimed and has high ratings in our library")
        elif top_factor == "popularity":
            reasons.append("it is a popular blockbuster trending among viewers")
        else:
            reasons.append("it is one of our top recommended titles today")
            
        # Formulate secondary reason
        if second_factor == "content" and similar_liked_title and top_factor != "content":
            reasons.append(f"matches the style of '{similar_liked_title}'")
        elif second_factor == "collaborative" and top_factor != "collaborative":
            reasons.append("is favored by users with similar viewing patterns")
        elif second_factor == "semantic" and query and top_factor != "semantic":
            reasons.append(f"strongly fits your interest in '{query}'")
        elif second_factor == "genre" and top_factor != "genre":
            matched_genres = list(set(movie_genres).intersection(set(favorite_genres)))
            if matched_genres:
                reasons.append(f"satisfies your taste for {matched_genres[0]}")
            else:
                reasons.append("matches your onboarding tastes")
        elif second_factor == "quality" and top_factor != "quality":
            reasons.append("stands out for its high quality rating")
        elif second_factor == "popularity" and top_factor != "popularity":
            reasons.append("is currently trending")
            
        # Assemble sentence
        if len(reasons) >= 2:
            explanation = f"Recommended because {reasons[0]}, and it {reasons[1]}."
        else:
            explanation = f"Recommended because {reasons[0]}."
            
        # Capitalize first letter
        explanation = explanation[0].upper() + explanation[1:]
        return explanation
