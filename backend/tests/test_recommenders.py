import pytest
import pandas as pd
import numpy as np
import json
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.recommenders.content_based import ContentBasedRecommender
from backend.app.recommenders.collaborative import CollaborativeRecommender
from backend.app.recommenders.semantic import SemanticRecommender
from backend.app.recommenders.hybrid import HybridRanker
from backend.app.recommenders.diversity import DiversityReranker

@pytest.fixture
def mock_movies_df():
    """Create a mock movies dataframe for unit testing."""
    data = [
        {
            "movieId": 1,
            "tmdbId": 101,
            "title": "Interstellar Space Quest",
            "overview": "A mind-bending science fiction movie about space travel and time dilation.",
            "genres": json.dumps(["Science Fiction", "Adventure"]),
            "keywords": json.dumps(["space", "time travel", "wormhole"]),
            "cast": json.dumps(["Matthew McConaughey", "Anne Hathaway"]),
            "director": "Christopher Nolan",
            "popularity": 80.0,
            "vote_average": 8.6,
            "vote_count": 1000,
            "release_date": "2014-11-07",
            "runtime": 169.0,
            "popularity_score": 0.8,
            "quality_score": 0.9,
            "poster_path": "/interstellar.jpg"
        },
        {
            "movieId": 2,
            "tmdbId": 102,
            "title": "The Funny Comedy Show",
            "overview": "A lighthearted funny comedy about a stand-up comedian in New York.",
            "genres": json.dumps(["Comedy"]),
            "keywords": json.dumps(["funny", "stand-up", "jokes"]),
            "cast": json.dumps(["Jerry Seinfeld", "Chris Rock"]),
            "director": "Director Joe",
            "popularity": 40.0,
            "vote_average": 7.0,
            "vote_count": 500,
            "release_date": "2020-05-12",
            "runtime": 92.0,
            "popularity_score": 0.4,
            "quality_score": 0.6,
            "poster_path": "/comedy.jpg"
        },
        {
            "movieId": 3,
            "tmdbId": 103,
            "title": "Dark Psychological Thriller",
            "overview": "A dark psychological thriller about a detective solving a complex crime mystery.",
            "genres": json.dumps(["Thriller", "Mystery", "Crime"]),
            "keywords": json.dumps(["dark", "suspense", "crime", "mystery"]),
            "cast": json.dumps(["Christian Bale", "Gary Oldman"]),
            "director": "Director Jane",
            "popularity": 50.0,
            "vote_average": 8.0,
            "vote_count": 700,
            "release_date": "2008-07-18",
            "runtime": 152.0,
            "popularity_score": 0.5,
            "quality_score": 0.8,
            "poster_path": "/thriller.jpg"
        }
    ]
    return pd.DataFrame(data)

@pytest.fixture
def mock_ratings_df():
    """Create a mock ratings interaction dataframe."""
    data = [
        {"userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 12345},
        {"userId": 1, "movieId": 3, "rating": 4.5, "timestamp": 12346},
        {"userId": 2, "movieId": 2, "rating": 4.0, "timestamp": 12347},
        {"userId": 2, "movieId": 3, "rating": 2.0, "timestamp": 12348},
        {"userId": 3, "movieId": 1, "rating": 4.8, "timestamp": 12349}
    ]
    return pd.DataFrame(data)

def test_content_based_recommender(mock_movies_df):
    rec = ContentBasedRecommender()
    rec.load_data(mock_movies_df)
    
    # User likes Interstellar (movieId=1) and dislikes Comedy (movieId=2)
    user_vector = rec.build_user_preference_vector(liked_ids=[1], disliked_ids=[2])
    
    assert user_vector is not None
    assert len(user_vector) > 0
    
    # Recommend
    recs = rec.recommend(liked_ids=[1], disliked_ids=[2], favorite_genres=["Science Fiction"], limit=2)
    assert len(recs) > 0
    # The top recommendation should not be movieId 1 or 2 (since they are excluded)
    # So it should be movieId 3 (thriller)
    assert recs[0][0] == 3

def test_collaborative_recommender(mock_ratings_df):
    rec = CollaborativeRecommender(k=5)
    rec.fit(mock_ratings_df, epochs=5, verbose=False)
    
    # Predict rating for user 1 and movie 1
    pred = rec.predict(1, 1)
    assert 0.5 <= pred <= 5.0
    
    # Recommend
    recs = rec.recommend(user_id=1, liked_ids=[1], disliked_ids=[], limit=2)
    assert len(recs) > 0
    # Must not contain excluded liked_ids
    assert 1 not in [mid for mid, _ in recs]

def test_semantic_query_filters(mock_movies_df):
    content_rec = ContentBasedRecommender()
    content_rec.load_data(mock_movies_df)
    
    semantic_rec = SemanticRecommender(content_rec)
    semantic_rec.load_data(mock_movies_df)
    
    # Test keyword extraction
    filters = semantic_rec.extract_filters("I want a recent dark psychological thriller under 2 hours")
    
    assert "Thriller" in filters["genres"]
    assert "Crime" not in filters["genres"]
    assert filters["duration"] == "short" # under 2 hours is short
    assert filters["period"] == "recent"
    assert "dark" in filters["mood"]

def test_hybrid_ranking(mock_movies_df, mock_ratings_df):
    content_rec = ContentBasedRecommender()
    content_rec.load_data(mock_movies_df)
    
    collaborative_rec = CollaborativeRecommender(k=5)
    collaborative_rec.fit(mock_ratings_df, epochs=5, verbose=False)
    
    semantic_rec = SemanticRecommender(content_rec)
    semantic_rec.load_data(mock_movies_df)
    
    hybrid = HybridRanker(content_rec, collaborative_rec, semantic_rec)
    hybrid.load_data(mock_movies_df)
    
    recs, strategy, weights = hybrid.recommend(
        user_id=1,
        liked_ids=[1],
        disliked_ids=[2],
        favorite_genres=["Science Fiction"],
        query="space exploration",
        limit=2
    )
    
    assert len(recs) > 0
    assert "score_breakdown" in recs[0]
    # Sum of breakdown values should sum to 1.0 (since they are normalized)
    assert pytest.approx(sum(recs[0]["score_breakdown"].values())) == 1.0

def test_diversity_reranker(mock_movies_df):
    content_rec = ContentBasedRecommender()
    content_rec.load_data(mock_movies_df)
    
    candidates = [
        {"movie_id": 1, "score": 0.9, "score_breakdown": {}},
        {"movie_id": 3, "score": 0.8, "score_breakdown": {}},
        {"movie_id": 2, "score": 0.5, "score_breakdown": {}}
    ]
    
    reranker = DiversityReranker(content_rec)
    
    # Balanced diversity
    reranked = reranker.rerank(candidates, diversity_mode="balanced", limit=2)
    assert len(reranked) == 2
    # Seed (relevance-sorted top item) must remain first
    assert reranked[0]["movie_id"] == 1

def test_api_health():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
