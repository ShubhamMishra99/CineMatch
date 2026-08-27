import numpy as np
from typing import List, Set, Any
from sklearn.metrics.pairwise import cosine_similarity

def precision_at_k(recommended: List[Any], ground_truth: Set[Any], k: int) -> float:
    """Calculate Precision@K = (relevant recommended items) / K."""
    if not recommended or not ground_truth or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in ground_truth)
    return hits / k

def recall_at_k(recommended: List[Any], ground_truth: Set[Any], k: int) -> float:
    """Calculate Recall@K = (relevant recommended items) / (total relevant items)."""
    if not recommended or not ground_truth or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in ground_truth)
    return hits / len(ground_truth)

def ndcg_at_k(recommended: List[Any], ground_truth: Set[Any], k: int) -> float:
    """
    Calculate NDCG@K (Normalized Discounted Cumulative Gain) using binary relevance.
    NDCG@K = DCG@K / IDCG@K
    """
    if not recommended or not ground_truth or k <= 0:
        return 0.0
        
    rec_k = recommended[:k]
    dcg = 0.0
    for i, item in enumerate(rec_k):
        if item in ground_truth:
            dcg += 1.0 / np.log2(i + 2) # i+2 because rank starts at 1, so index i corresponds to rank i+1
            
    idcg = 0.0
    for i in range(min(k, len(ground_truth))):
        idcg += 1.0 / np.log2(i + 2)
        
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg

def catalog_coverage(all_recommendations: List[List[Any]], catalog_size: int) -> float:
    """Calculate Catalog Coverage = percentage of unique recommended items across all users."""
    if not all_recommendations or catalog_size <= 0:
        return 0.0
    unique_rec_items = set(item for rec_list in all_recommendations for item in rec_list)
    return len(unique_rec_items) / catalog_size

def intra_list_diversity(recommended: List[Any], content_vectors_dict: dict) -> float:
    """
    Calculate Intra-List Diversity = average pairwise dissimilarity (1 - cosine similarity)
    among recommended items in the list.
    """
    if len(recommended) <= 1:
        return 0.0
        
    # Gather vectors
    vectors = []
    for item in recommended:
        vec = content_vectors_dict.get(item)
        if vec is not None:
            vectors.append(vec)
            
    if len(vectors) <= 1:
        return 0.0
        
    # Calculate pairwise similarities
    # shape: (N, N)
    sims = cosine_similarity(np.array(vectors))
    
    # Extract upper triangle (excluding diagonal)
    n = len(vectors)
    dissimilarities = []
    for i in range(n):
        for j in range(i + 1, n):
            dissimilarities.append(1.0 - sims[i, j])
            
    return float(np.mean(dissimilarities)) if dissimilarities else 0.0
