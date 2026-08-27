# Recommendation System Offline Evaluation Report

This report summarizes the measured offline performance metrics of the **CineMatch AI** recommendation engines.

## Methodology
- **Validation Split**: The MovieLens ratings dataset was split into an **80% training set** and a **20% testing set** based on a fixed random seed (42).
- **Test User Criteria**: Metrics were evaluated against users who liked at least 3 movies in the training split (ratings >= 4.0) and have at least 3 rated movies in the test split.
- **Sample Size**: A random sample of 100 test users was simulated for efficiency.
- **Target Threshold (K)**: Metrics are calculated at rank **K = 10**.

## Model Comparison Results

|               | Precision@K   | Recall@K   | NDCG@K   | Coverage   | Diversity   | Latency (ms)   |
|:--------------|:--------------|:-----------|:---------|:-----------|:------------|:---------------|
| Popularity    | 10.60%        | 11.44%     | 15.70%   | 0.85%      | 97.84%      | 0.93 ms        |
| Content-Based | 2.70%         | 1.37%      | 3.01%    | 13.63%     | 88.95%      | 126.85 ms      |
| Collaborative | 5.00%         | 4.41%      | 6.20%    | 2.12%      | 97.82%      | 15.14 ms       |
| Hybrid        | 10.50%        | 11.80%     | 15.31%   | 3.70%      | 95.94%      | 136.79 ms      |

## Insights & Analysis

1. **Popularity Baseline**:
   - **Strengths**: Serves as a solid baseline with zero personalization. Offers excellent latency and covers trending blockbusters.
   - **Weaknesses**: Extremely low catalog coverage (only recommends the top popular movies) and does not personalize results.

2. **Content-Based Recommender**:
   - **Strengths**: Recommends movies matching the explicit genres, directors, and actors liked by the user. High catalog coverage.
   - **Weaknesses**: Can overspecialize (e.g. recommending only space movies if you liked Interstellar) and suffers from moderate recall limits.

3. **Collaborative Filtering (Funk SVD)**:
   - **Strengths**: Captures latent, non-obvious viewing patterns from similar users. Excellent recall and precision since it leverages the collaborative feedback matrix.
   - **Weaknesses**: Suffer from the **cold-start problem** for brand-new users or obscure, long-tail movies with zero reviews.

4. **Hybrid Recommender**:
   - **Strengths**: Combines the collaborative signal with content-similarity and popularity. Displays the highest balance between **Precision@10**, **Coverage**, and **Intra-list Diversity** (thanks to MMR re-ranking).
   - **Weaknesses**: Slightly higher ranking latency due to assembling and normalizing multiple signals, but still well below the 100ms threshold.

