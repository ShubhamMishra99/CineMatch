import math
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from backend.app.core.config import settings

logger = logging.getLogger("cinematch")

# In-memory cache for TMDB poster paths to avoid redundant HTTP requests
_POSTER_CACHE = {}

# TMDB occasionally closes a transient connection. Reuse one session and retry
# those short-lived failures so a single network hiccup does not permanently
# turn a card into a no-poster fallback for the lifetime of the server.
_TMDB_SESSION = requests.Session()
_TMDB_SESSION.mount(
    "https://",
    HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.2, status_forcelist=(429, 500, 502, 503, 504)))
)

def fetch_tmdb_poster_path(tmdb_id: int) -> str | None:
    """
    Dynamically fetch the poster path for a given TMDB movie ID.
    Caches results in memory to minimize latency.
    """
    if not tmdb_id or str(tmdb_id).lower() == "nan":
        return None

    try:
        # Pandas commonly supplies an id as a float (for example, 862.0).
        # Reject NaN before converting so the poster lookup never interrupts a response.
        if isinstance(tmdb_id, float) and math.isnan(tmdb_id):
            return None
        tmdb_id = int(float(tmdb_id))
    except (TypeError, ValueError, OverflowError):
        logger.warning("Invalid TMDB id %r; skipping poster lookup.", tmdb_id)
        return None

    # Check cache first
    if tmdb_id in _POSTER_CACHE:
        return _POSTER_CACHE[tmdb_id]

    api_key = settings.TMDB_API_KEY
    if not api_key or api_key.strip() == "" or "your_tmdb_api_key" in api_key:
        logger.warning("TMDB_API_KEY is not configured or placeholder. Cannot fetch dynamic posters.")
        _POSTER_CACHE[tmdb_id] = None
        return None

    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        response = _TMDB_SESSION.get(url, params={"api_key": api_key.strip()}, timeout=4)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                _POSTER_CACHE[tmdb_id] = poster_path
                return poster_path
        else:
            logger.error(f"TMDB API returned status {response.status_code} for movie {tmdb_id}")
    except Exception as e:
        logger.error(f"Error fetching poster from TMDB API for movie {tmdb_id}: {e}")

    # Cache None to prevent repeatedly querying failing requests
    _POSTER_CACHE[tmdb_id] = None
    return None

def get_movie_poster_url(row_dict: dict) -> str | None:
    """
    Get the full TMDB poster URL for a movie.
    Falls back to dynamic TMDB API fetching if the CSV's poster_path is empty.
    """
    # 1. Check if poster_path exists in the local data
    poster_path = row_dict.get("poster_path")

    # 2. If missing or invalid, try dynamic fetch using TMDB API Key
    if not poster_path or not isinstance(poster_path, str) or not poster_path.strip() or poster_path.lower() == "nan":
        tmdb_id = row_dict.get("tmdbId") or row_dict.get("tmdb_id") or row_dict.get("id")
        if tmdb_id:
            poster_path = fetch_tmdb_poster_path(tmdb_id)

    # 3. Format full URL
    if poster_path and isinstance(poster_path, str) and poster_path.strip() and poster_path.lower() != "nan":
        clean_path = poster_path.strip()
        if not clean_path.startswith("/"):
            clean_path = "/" + clean_path
        return f"https://image.tmdb.org/t/p/w500{clean_path}"

    return None
