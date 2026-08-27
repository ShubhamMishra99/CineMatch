from fastapi import APIRouter, HTTPException, Request, status
import logging
from backend.app.models.schemas import RecommendRequest, RecommendResponse

router = APIRouter()
logger = logging.getLogger("cinematch")

@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(request: Request, payload: RecommendRequest):
    """
    Generate personalized recommendations based on:
    - Favorite genres
    - Liked / disliked history
    - Search queries
    - Collaborative SVD
    - MMR diversity
    """
    rec_service = getattr(request.app.state, "rec_service", None)
    if not rec_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation engine is not fully initialized."
        )
        
    try:
        # Generate recommendations
        results = rec_service.get_recommendations(
            user_id=payload.user_id,
            liked_movie_ids=payload.liked_movie_ids,
            disliked_movie_ids=payload.disliked_movie_ids,
            favorite_genres=payload.favorite_genres,
            query=payload.query,
            diversity_mode=payload.diversity_mode,
            limit=payload.limit
        )
        
        # Log request summary
        logger.info(
            f"Recommendations generated: user_id={payload.user_id}, "
            f"liked_count={len(payload.liked_movie_ids)}, "
            f"query='{payload.query}', "
            f"strategy={results['metadata']['strategy']}, "
            f"latency_ms={results['metadata']['latency_ms']['total']}"
        )
        
        return results
        
    except Exception as e:
        logger.exception("An error occurred during recommendation generation:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating recommendations. Please check server logs."
        )
