from fastapi import APIRouter, HTTPException, Request, status
import logging
from backend.app.models.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter()
logger = logging.getLogger("cinematch")

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: Request, payload: FeedbackRequest):
    """
    Register a user feedback interaction (e.g. like, dislike, save, watch) for telemetry.
    Returns status confirmation and mock session profile update representation.
    """
    try:
        # Log the feedback interaction for metrics/evaluation tracking
        logger.info(
            f"User Feedback: user_id={payload.user_id}, "
            f"movie_id={payload.movie_id}, "
            f"feedback_type='{payload.feedback_type}'"
        )
        
        # Build message and mock confirmation status
        return {
            "status": "success",
            "message": f"Successfully registered feedback '{payload.feedback_type}' for movie {payload.movie_id}",
            "session_profile": {
                "user_id": payload.user_id,
                "last_active_movie_id": payload.movie_id,
                "last_action": payload.feedback_type
            }
        }
    except Exception as e:
        logger.exception("An error occurred during feedback registration:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user feedback. Please check server logs."
        )
