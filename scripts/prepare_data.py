import os
import zipfile
import urllib.request
import pandas as pd
import json
import numpy as np

# Define directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")

# URLs for datasets
MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
TMDB_MOVIES_URL = "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/master/tmdb_5000_movies.csv"

# Alternative URLs for TMDB Credits (since it's a 40MB file, some repos might use Git LFS)
TMDB_CREDITS_URLS = [
    "https://raw.githubusercontent.com/helenasloane/Movie-Recommender/master/tmdb_5000_credits.csv",
    "https://raw.githubusercontent.com/harshitcodes/tmdb_movie_data_analysis/master/tmdb_5000_credits.csv",
    "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/master/tmdb_5000_credits.csv"
]

def create_directories():
    """Create data directories if they don't exist."""
    for directory in [RAW_DIR, PROCESSED_DIR, SAMPLE_DIR]:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory ensured: {directory}")

def is_lfs_pointer(filepath):
    """Check if the downloaded file is just a Git LFS pointer."""
    if not os.path.exists(filepath):
        return False
    # If the file size is very small, it's likely an LFS pointer
    if os.path.getsize(filepath) < 5000:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            if "version https://git-lfs" in first_line:
                return True
    return False

def download_file(url, filepath):
    """Download a file from a URL to a local filepath if it doesn't exist."""
    if not os.path.exists(filepath):
        print(f"Downloading {url} to {filepath}...")
        try:
            urllib.request.urlretrieve(url, filepath)
            print("Download complete.")
            return True
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    else:
        print(f"File already exists: {filepath}")
        return True

def download_credits_file(filepath):
    """Try downloading from alternative URLs and verify it's not an LFS pointer."""
    if os.path.exists(filepath) and not is_lfs_pointer(filepath):
        print(f"Credits file already exists: {filepath}")
        return True

    if os.path.exists(filepath):
        os.remove(filepath) # Remove LFS pointer if it was downloaded previously

    for url in TMDB_CREDITS_URLS:
        print(f"Trying to download credits from {url}...")
        success = download_file(url, filepath)
        if success:
            if is_lfs_pointer(filepath):
                print(f"Warning: Downloaded file from {url} is a Git LFS pointer. Removing and trying next...")
                os.remove(filepath)
            else:
                print("Successfully downloaded valid credits dataset.")
                return True
    return False

def extract_zip(zip_path, extract_to):
    """Extract a zip file to a directory."""
    print(f"Extracting {zip_path} to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

def safe_parse_json(val):
    """Safely parse a JSON string or return empty list/dict."""
    if pd.isna(val) or not isinstance(val, str):
        return []
    try:
        return json.loads(val)
    except Exception:
        return []

def extract_director(crew_list):
    """Extract the name of the director from crew list."""
    for member in crew_list:
        if member.get("job") == "Director":
            return member.get("name")
    return None

def process_data():
    """Download, clean, merge, and split data for recommendation."""
    create_directories()

    # Paths
    ml_zip_path = os.path.join(RAW_DIR, "ml-latest-small.zip")
    tmdb_movies_path = os.path.join(RAW_DIR, "tmdb_5000_movies.csv")
    tmdb_credits_path = os.path.join(RAW_DIR, "tmdb_5000_credits.csv")

    # Download datasets
    download_file(MOVIELENS_URL, ml_zip_path)
    download_file(TMDB_MOVIES_URL, tmdb_movies_path)
    has_credits = download_credits_file(tmdb_credits_path)

    # Extract MovieLens
    extract_zip(ml_zip_path, RAW_DIR)
    ml_extracted_folder = os.path.join(RAW_DIR, "ml-latest-small")

    # Load MovieLens Data
    print("Loading MovieLens ratings and links...")
    links_df = pd.read_csv(os.path.join(ml_extracted_folder, "links.csv"))
    ratings_df = pd.read_csv(os.path.join(ml_extracted_folder, "ratings.csv"))

    # Load TMDB Data
    print("Loading TMDB movies...")
    tmdb_movies_df = pd.read_csv(tmdb_movies_path)

    # Clean and parse TMDB JSON columns
    print("Parsing JSON columns (genres, keywords)...")
    tmdb_movies_df["genres_parsed"] = tmdb_movies_df["genres"].apply(safe_parse_json).apply(lambda x: [g["name"] for g in x])
    tmdb_movies_df["keywords_parsed"] = tmdb_movies_df["keywords"].apply(safe_parse_json).apply(lambda x: [k["name"] for k in x])

    if has_credits:
        print("Loading TMDB credits...")
        try:
            tmdb_credits_df = pd.read_csv(tmdb_credits_path)
            tmdb_credits_df["cast_parsed"] = tmdb_credits_df["cast"].apply(safe_parse_json).apply(lambda x: [c["name"] for c in x[:3]])
            tmdb_credits_df["crew_parsed"] = tmdb_credits_df["crew"].apply(safe_parse_json)
            tmdb_credits_df["director"] = tmdb_credits_df["crew_parsed"].apply(extract_director)

            # Merge TMDB movies and credits
            print("Merging TMDB movies and credits...")
            tmdb_df = pd.merge(
                tmdb_movies_df[["id", "title", "overview", "genres_parsed", "keywords_parsed", "popularity", "vote_average", "vote_count", "release_date", "runtime"]],
                tmdb_credits_df[["movie_id", "cast_parsed", "director"]],
                left_on="id",
                right_on="movie_id",
                how="inner"
            ).drop(columns=["movie_id"])
        except Exception as e:
            print(f"Error reading credits dataset: {e}. Falling back to metadata-only...")
            has_credits = False

    if not has_credits:
        print("Warning: Running pipeline without credits metadata (cast/director will be empty).")
        tmdb_df = tmdb_movies_df[["id", "title", "overview", "genres_parsed", "keywords_parsed", "popularity", "vote_average", "vote_count", "release_date", "runtime"]].copy()
        tmdb_df["cast_parsed"] = [[] for _ in range(len(tmdb_df))]
        tmdb_df["director"] = None

    # Map to MovieLens links
    # Clean links_df tmdbId: drop NaNs and convert to int
    links_clean = links_df.dropna(subset=["tmdbId"]).copy()
    links_clean["tmdbId"] = links_clean["tmdbId"].astype(int)

    # Merge MovieLens links with TMDB metadata
    print("Merging MovieLens and TMDB on TMDB ID...")
    movies_merged = pd.merge(
        links_clean[["movieId", "tmdbId"]],
        tmdb_df,
        left_on="tmdbId",
        right_on="id",
        how="inner"
    )
    print(f"Merged movies count: {len(movies_merged)}")

    # Filter ratings: keep only ratings for movies we have metadata for
    ratings_filtered = ratings_df[ratings_df["movieId"].isin(movies_merged["movieId"])].copy()
    print(f"Filtered ratings count: {len(ratings_filtered)}")
    print(f"Unique users: {ratings_filtered['userId'].nunique()}")
    print(f"Unique movies with ratings: {ratings_filtered['movieId'].nunique()}")

    # Add default poster paths (using TMDB IDs for fallback URL formatting, e.g. /somepath)
    # We will generate a synthetic poster path using TMDB ID if not present, but wait,
    # we can also fetch from TMDB if a key is provided. Let's write the code for API enrichment:
    api_key = os.environ.get("TMDB_API_KEY", "")
    movies_merged["poster_path"] = None

    if api_key:
        print("TMDB API Key found. Fetching poster paths from TMDB API...")
        import urllib.request
        import time
        
        # We only fetch poster paths for the movies we need
        count = 0
        for idx, row in movies_merged.iterrows():
            tmdb_id = row["tmdbId"]
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}"
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    res_data = json.loads(response.read().decode())
                    poster_path = res_data.get("poster_path")
                    movies_merged.at[idx, "poster_path"] = poster_path
                    count += 1
            except Exception as e:
                # Silently ignore and continue, fallback to None
                pass
            
            # Rate limiting safety
            time.sleep(0.1)
            if count % 100 == 0 and count > 0:
                print(f"Fetched poster paths for {count} movies...")
        print(f"Finished fetching. Successfully got {count} poster paths.")
    else:
        print("No TMDB_API_KEY found in environment. Poster paths will be generated dynamically on frontend or use placeholders.")

    # Log poster mapping coverage statistics
    total_movies = len(movies_merged)
    valid_posters = movies_merged["poster_path"].notna().sum()
    fallback_posters = total_movies - valid_posters
    coverage_pct = (valid_posters / total_movies) * 100 if total_movies > 0 else 0.0
    
    print("\n" + "="*50)
    print("POSTER MAPPING COVERAGE REPORT")
    print(f"Total movies processed: {total_movies}")
    print(f"Movies with valid poster URLs: {valid_posters}")
    print(f"Movies using fallback posters: {fallback_posters}")
    print(f"Poster coverage percentage: {coverage_pct:.2f}%")
    print("="*50 + "\n")

    # Save processed files
    print("Saving processed data files...")
    movies_metadata_path = os.path.join(PROCESSED_DIR, "movies_metadata.csv")
    ratings_processed_path = os.path.join(PROCESSED_DIR, "ratings.csv")

    # Serialize list columns to JSON strings so we can read them back properly in pandas
    movies_to_save = movies_merged.copy()
    movies_to_save["genres"] = movies_to_save["genres_parsed"].apply(json.dumps)
    movies_to_save["keywords"] = movies_to_save["keywords_parsed"].apply(json.dumps)
    movies_to_save["cast"] = movies_to_save["cast_parsed"].apply(json.dumps)
    movies_to_save.drop(columns=["genres_parsed", "keywords_parsed", "cast_parsed"], inplace=True)

    movies_to_save.to_csv(movies_metadata_path, index=False)
    ratings_filtered.to_csv(ratings_processed_path, index=False)
    print(f"Saved: {movies_metadata_path}")
    print(f"Saved: {ratings_processed_path}")

    # Generate sample dataset (top 500 popular movies and their ratings)
    print("Creating sample dataset of top 500 popular movies...")
    top_500_ids = movies_merged.nlargest(500, "popularity")["movieId"]
    sample_movies = movies_to_save[movies_to_save["movieId"].isin(top_500_ids)]
    sample_ratings = ratings_filtered[ratings_filtered["movieId"].isin(top_500_ids)]

    sample_movies_path = os.path.join(SAMPLE_DIR, "movies_metadata.csv")
    sample_ratings_path = os.path.join(SAMPLE_DIR, "ratings.csv")

    sample_movies.to_csv(sample_movies_path, index=False)
    sample_ratings.to_csv(sample_ratings_path, index=False)
    print(f"Saved sample: {sample_movies_path} ({len(sample_movies)} movies)")
    print(f"Saved sample: {sample_ratings_path} ({len(sample_ratings)} ratings)")
    print("Data preparation pipeline completed successfully!")

if __name__ == "__main__":
    process_data()
