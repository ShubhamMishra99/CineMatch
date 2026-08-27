# CineMatch AI - Product & Engineering Comparison

This document provides a comparative analysis of **CineMatch AI** against enterprise streaming recommendation architectures (such as Netflix and Spotify).

---

## 1. Summary Comparison Table

| Feature Dimension | CineMatch AI (Current Architecture) | Enterprise Recommender (Netflix/Spotify) |
| :--- | :--- | :--- |
| **Dataset Scale** | ~3,500 movies, ~70,000 ratings | Millions of items, Billions of ratings |
| **Model Training** | Scheduled offline script (Funk SVD + SBERT) | Real-time streaming updates + nightly Deep Learning |
| **Candidate Retrieval** | Local memory lookup (<5ms) | Distributed vector search (FAISS, Milvus) |
| **Feature Store** | Stateless memory load | Real-time feature store (Feast, Hopsworks) |
| **Latency Budget** | <50ms (average total request time) | <100ms budget across 100+ microservices |
| **Feedback Loop** | Session-level in-memory feedback | Real-time event streaming (Kafka, Flink) |
| **Explainability** | Relative scoring contribution charts | Implicit explanations ("Because you watched X...") |

---

## 2. Structural Similarities

1. **Multi-Signal Personalization**: Both architectures utilize a blend of collaborative user patterns, content features (genre, keywords), and search queries.
2. **Two-Stage Architecture**: CineMatch AI employs candidate generation (retrieving the top 300 candidates) followed by scoring/re-ranking (hybrid weights and MMR diversity), mirroring the standard industrial **Retrieval -> Ranking** paradigm.
3. **Feedback loops**: Clicks, likes, and dislikes immediately alter subsequent recommendations.
4. **Diversity Re-ranking**: Both systems actively diversify recommendations (Netflix carousel diversity, CineMatch AI MMR lambda) to avoid recommending near-identical movies.

---

## 3. Key Differences & Scale Constraints

1. **Model Complexity**: Netflix uses deep neural networks (e.g., autoencoders, sequence models) for ranking, whereas CineMatch AI uses Funk SVD matrix factorization combined with modular linear combination weights.
2. **Streaming Event Engine**: Netflix feeds every click, hover, and scroll through Apache Kafka to update feature tables instantly. CineMatch AI stores session preferences in local storage, which are passed back in the `/api/recommend` payload.
3. **Vector Database Retrieval**: For semantic queries, CineMatch AI performs in-memory cosine similarities using numpy. At scale, this is replaced by approximate nearest neighbor (ANN) indexes like FAISS.

---

## 4. What We Would Build Next (Future Roadmap)

With more development time, the following features would be implemented:

1. **Approximate Nearest Neighbor (ANN) Indexing**:
   - Integrate **FAISS** or **ScaNN** to query 100k+ movie embeddings in sub-millisecond times.
2. **Learn-to-Rank (LTR) Model**:
   - Replace linear hybrid weights with a supervised machine learning model (e.g. XGBoost/LightGBM) trained on historical user clickthrough rates.
3. **Real-time Event Streaming**:
   - Setup **Apache Kafka** and **Apache Flink** to capture user interaction events and dynamically recalculate latent factors.
4. **Contextual Recommendations**:
   - Include external context signals (time of day, device type, user location, weekend vs weekday) into the ranking features.
5. **Redis Caching**:
   - Cache user profiles and generated recommendations to achieve sub-10ms response latencies for returning visitors.
6. **Multi-Armed Bandits (MAB)**:
   - Implement epsilon-greedy or Thompson sampling models to dynamically balance exploitation (popular/similar movies) with exploration (discover new titles).
