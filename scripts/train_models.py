import os
import pandas as pd
import numpy as np
import json
import pickle
import sys

# Add backend directory to sys.path to enable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.app.recommenders.collaborative import CollaborativeRecommender
from backend.app.core.config import settings

def main():
    print("=== CineMatch AI Model Training Pipeline ===")
    
    # Define directories
    processed_dir = settings.PROCESSED_DATA_DIR
    model_dir = settings.MODEL_DIR
    
    movies_path = os.path.join(processed_dir, "movies_metadata.csv")
    ratings_path = os.path.join(processed_dir, "ratings.csv")
    
    if not os.path.exists(movies_path) or not os.path.exists(ratings_path):
        print("Error: Processed data files not found. Please run scripts/prepare_data.py first.")
        sys.exit(1)
        
    # 1. Load data
    print("Loading data...")
    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)
    
    # 2. Train Collaborative Filtering (SVD)
    print("\n--- Training Collaborative Filtering (Funk SVD) ---")
    svd = CollaborativeRecommender(k=20, lr=0.005, reg=0.02)
    # Train for 20 epochs
    svd.fit(ratings_df, epochs=20, verbose=True)
    
    # Save SVD model
    svd_model_path = os.path.join(model_dir, "collaborative_model.pkl")
    svd.save(svd_model_path)
    
    # 3. Generate Semantic Embeddings (Sentence Transformers)
    print("\n--- Generating Content Semantic Embeddings ---")
    
    # Parse lists from string JSONs
    movies_df["genres"] = movies_df["genres"].apply(lambda x: json.loads(x) if isinstance(x, str) else [])
    movies_df["keywords"] = movies_df["keywords"].apply(lambda x: json.loads(x) if isinstance(x, str) else [])
    movies_df["cast"] = movies_df["cast"].apply(lambda x: json.loads(x) if isinstance(x, str) else [])
    
    # Build text soup for semantic embedding
    def get_semantic_text(row):
        title = str(row.get("title", ""))
        overview = str(row.get("overview", ""))
        genres = " ".join(row.get("genres", []))
        keywords = " ".join(row.get("keywords", []))
        return f"{title}. {overview} Genres: {genres}. Keywords: {keywords}."

    movies_df["semantic_text"] = movies_df.apply(get_semantic_text, axis=1)
    
    embedding_saved = False
    try:
        print("Checking if 'sentence-transformers' is installed...")
        from sentence_transformers import SentenceTransformer
        
        print("Loading sentence-transformers/all-MiniLM-L6-v2...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        print("Generating dense semantic embeddings (this may take a few minutes)...")
        texts = movies_df["semantic_text"].tolist()
        
        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
        
        # Save embeddings
        embeddings_path = os.path.join(model_dir, "movie_embeddings.npy")
        np.save(embeddings_path, embeddings)
        print(f"Dense embeddings saved successfully to {embeddings_path} (shape: {embeddings.shape})")
        embedding_saved = True
        
    except ImportError:
        print("\nNotice: 'sentence-transformers' is not installed.")
        print("Skipping dense embedding generation. Recommender will fall back to TF-IDF cosine similarity.")
    except Exception as e:
        print(f"\nError during dense embedding generation: {e}")
        print("Skipping dense embedding generation. Recommender will fall back to TF-IDF cosine similarity.")
        
    print("\n=== Model Training Pipeline Finished successfully! ===")
    if embedding_saved:
        print("Artifacts generated: Funk SVD weights & Sentence Transformer embeddings.")
    else:
        print("Artifacts generated: Funk SVD weights only (TF-IDF fallback enabled).")

if __name__ == "__main__":
    main()
