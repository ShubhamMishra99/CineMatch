from fastapi import APIRouter, HTTPException, Request, status
import time
import logging
import pandas as pd
from backend.app.models.schemas import SearchRequest, SearchResponse

router = APIRouter()
logger = logging.getLogger("cinematch")

@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: Request, payload: SearchRequest):
    """
    Search the catalog semantically. Returns movies matching the natural language query,
    prioritized by cosine description similarity and boosted by keyword-based filters.
    """
    rec_service = getattr(request.app.state, "rec_service", None)
    if not rec_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation engine is not fully initialized."
        )
        
    start_time = time.time()
    try:
        # Call Semantic Recommender directly
        recommendations = rec_service.semantic_recommender.recommend(
            query=payload.query,
            limit=payload.limit
        )
        
        results = []
        for movie_id, score in recommendations:
            # Retrieve movie metadata
            movie_row = rec_service.movies_df[rec_service.movies_df["movieId"] == movie_id]
            if movie_row.empty:
                continue
                
            row = movie_row.iloc[0]
            
            # Genres
            genres_list = row.get("genres", [])
            if isinstance(genres_list, str):
                try:
                    genres_list = eval(genres_list)
                except Exception:
                    genres_list = []
                    
            # Poster full url (handling pandas NaN values)
            poster_path = row.get("poster_path")
            if poster_path and isinstance(poster_path, str) and poster_path.strip() and poster_path.lower() != "nan":
                clean_path = poster_path.strip()
                if not clean_path.startswith("/"):
                    clean_path = "/" + clean_path
                poster_url = f"https://image.tmdb.org/t/p/w500{clean_path}"
            else:
                poster_url = None
            
            results.append({
                "movie_id": movie_id,
                "title": row["title"],
                "overview": row["overview"] if not pd.isna(row["overview"]) else None,
                "genres": genres_list,
                "release_year": row["release_date"].split("-")[0] if row["release_date"] and not pd.isna(row["release_date"]) else None,
                "runtime": float(row["runtime"]) if not pd.isna(row["runtime"]) else None,
                "vote_average": float(row["vote_average"]) if not pd.isna(row["vote_average"]) else None,
                "poster_url": poster_url,
                "score": round(score, 4)
            })
            
        latency = (time.time() - start_time) * 1000
        
        logger.info(f"Semantic search: query='{payload.query}', results={len(results)}, latency_ms={latency:.2f}")
        
        return {
            "query": payload.query,
            "results": results,
            "latency_ms": round(latency, 2)
        }
        
    except Exception as e:
        logger.exception("An error occurred during semantic search:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while executing the search query. Please check server logs."
        )
