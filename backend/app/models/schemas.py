from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class RecommendRequest(BaseModel):
    user_id: int = Field(default=1, description="Numerical user identifier for SVD collaborative matching")
    liked_movie_ids: List[int] = Field(default=[], description="List of movie IDs user has liked in this session")
    disliked_movie_ids: List[int] = Field(default=[], description="List of movie IDs user has disliked in this session")
    favorite_genres: List[str] = Field(default=[], description="User onboarding favorite genres")
    query: Optional[str] = Field(default=None, description="Natural language search query")
    diversity_mode: str = Field(default="balanced", description="MMR diversity configuration: focused, balanced, or exploratory")
    limit: int = Field(default=10, ge=1, le=50, description="Max number of movie recommendations to return")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "liked_movie_ids": [272, 157336],
                "disliked_movie_ids": [19995],
                "favorite_genres": ["Science Fiction", "Thriller"],
                "query": "mind bending sci-fi movie",
                "diversity_mode": "balanced",
                "limit": 10
            }
        }
    }

class MovieRecommendation(BaseModel):
    movie_id: int
    title: str
    overview: Optional[str] = None
    genres: List[str]
    release_year: Optional[str] = None
    runtime: Optional[float] = None
    vote_average: Optional[float] = None
    poster_url: Optional[str] = None
    score: float
    explanation: str
    score_breakdown: Dict[str, float]

class LatencyMetadata(BaseModel):
    ranking: float
    diversity: float
    explanation: float
    total: float

class RecommendResponseMetadata(BaseModel):
    strategy: str
    candidate_count: int
    weights_used: Dict[str, float]
    latency_ms: LatencyMetadata

class RecommendResponse(BaseModel):
    recommendations: List[MovieRecommendation]
    metadata: RecommendResponseMetadata

class FeedbackRequest(BaseModel):
    user_id: int = Field(default=1)
    movie_id: int = Field(..., description="Target movie ID")
    feedback_type: str = Field(..., description="Interaction feedback: 'like', 'dislike', 'save', 'watch'")

class FeedbackResponse(BaseModel):
    status: str
    message: str
    session_profile: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str = Field(..., description="Query for semantic search")
    limit: int = Field(default=10, ge=1, le=50)

class SearchResultMovie(BaseModel):
    movie_id: int
    title: str
    overview: Optional[str] = None
    genres: List[str]
    release_year: Optional[str] = None
    runtime: Optional[float] = None
    vote_average: Optional[float] = None
    poster_url: Optional[str] = None
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultMovie]
    latency_ms: float
