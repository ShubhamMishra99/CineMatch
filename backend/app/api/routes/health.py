from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter()

# We will import recommendation_service inside route or use a global dependency
# Since it is a FastAPI app, we can store recommendation_service on the app.state
# We will access it using request.app.state.rec_service

from fastapi import Request

@router.get("/health", response_model=Dict[str, Any])
async def health_check(request: Request):
    """Get the health status and loaded models information."""
    rec_service = getattr(request.app.state, "rec_service", None)
    
    models_loaded = {
        "content": False,
        "collaborative": False,
        "semantic": False
    }
    
    if rec_service:
        models_loaded = rec_service.models_loaded
        
    return {
        "status": "healthy",
        "models_loaded": models_loaded
    }
