import os
import time
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.api.routes import recommend, search, feedback, health, movie
from backend.app.services.recommendation_service import RecommendationService

# Initialize logger
logger = setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="Explainable, hybrid, and diverse movie recommendation engine backend.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"  # Allow all for deployment staging/testing compatibility
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(recommend.router, prefix="/api", tags=["recommendations"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(movie.router, prefix="/api", tags=["movies"])
app.include_router(health.router, prefix="/api", tags=["health"])

@app.on_event("startup")
async def startup_event():
    """Load models and metadata during FastAPI server startup."""
    logger.info("Starting CineMatch AI server...")
    
    # Check if we should use sample dataset (for faster testing/memory limit environments)
    # Default is False, meaning load the full processed dataset
    use_sample = os.environ.get("USE_SAMPLE_DATASET", "False").lower() == "true"
    
    rec_service = RecommendationService(use_sample=use_sample)
    try:
        rec_service.initialize()
        app.state.rec_service = rec_service
        logger.info("Recommendation service initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize recommendation service: {e}", exc_info=True)
        # Store an empty service or None, endpoints will degrade gracefully or show service unavailable
        app.state.rec_service = rec_service

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down CineMatch AI server...")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to measure HTTP request execution latency."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to intercept unhandled exceptions and hide stack trace details."""
    logger.exception(f"Unhandled exception occurred during request {request.url}:")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please consult the system logs."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
