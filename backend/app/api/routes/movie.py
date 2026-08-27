from fastapi import APIRouter, HTTPException, Request, status
import pandas as pd
from typing import Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter()

class MovieDetailsResponse(BaseModel):
    movie_id: int
    title: str
    overview: Optional[str] = None
    genres: list
    keywords: list
    cast: list
    director: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[float] = None
    vote_average: Optional[float] = None
    popularity: Optional[float] = None
    poster_url: Optional[str] = None

@router.get("/movie/{movie_id}", response_model=MovieDetailsResponse)
async def get_movie_details(request: Request, movie_id: int):
    """Retrieve detailed metadata for a specific movie ID."""
    rec_service = getattr(request.app.state, "rec_service", None)
    if not rec_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation engine is not fully initialized."
        )
        
    movie_row = rec_service.movies_df[rec_service.movies_df["movieId"] == movie_id]
    if movie_row.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} not found."
        )
        
    row = movie_row.iloc[0]
    
    # Parse lists from string JSONs
    def load_field(field_name):
        val = row.get(field_name, [])
        if isinstance(val, str):
            try:
                import json
                return json.loads(val)
            except Exception:
                return []
        elif isinstance(val, list):
            return val
        return []

    genres = load_field("genres")
    keywords = load_field("keywords")
    cast = load_field("cast")
    
    # Poster full url (handling pandas NaN values)
    poster_path = row.get("poster_path")
    if poster_path and isinstance(poster_path, str) and poster_path.strip() and poster_path.lower() != "nan":
        clean_path = poster_path.strip()
        if not clean_path.startswith("/"):
            clean_path = "/" + clean_path
        poster_url = f"https://image.tmdb.org/t/p/w500{clean_path}"
    else:
        poster_url = None
    
    return {
        "movie_id": movie_id,
        "title": row["title"],
        "overview": row["overview"] if not pd.isna(row["overview"]) else None,
        "genres": genres,
        "keywords": keywords,
        "cast": cast,
        "director": row["director"] if not pd.isna(row["director"]) else None,
        "release_date": row["release_date"] if not pd.isna(row["release_date"]) else None,
        "runtime": float(row["runtime"]) if not pd.isna(row["runtime"]) else None,
        "vote_average": float(row["vote_average"]) if not pd.isna(row["vote_average"]) else None,
        "popularity": float(row["popularity"]) if not pd.isna(row["popularity"]) else None,
        "poster_url": poster_url
    }
