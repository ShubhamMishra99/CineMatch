# CineMatch AI - Test Cases & Failure Scenarios

This document outlines successful test scenarios, known failure cases, and architectural limitations of the recommendation engine.

---

## 1. Success Scenarios

### Case 1: Personalized Science Fiction Match
- **User Profile**:
  - Liked Movies: *Interstellar* (109487), *Inception* (79132)
  - Favorite Genres: `["Science Fiction"]`
- **Search Query**: "Mind-bending space exploration"
- **Expected Behavior**:
  - The system builds a User Preference Vector centered around space travel and cognitive science fiction.
  - The semantic recommender parses the query, boosting movies with keywords like "space", "dilations", "future".
  - Collaborative SVD predicts high affinity for titles commonly rated by viewers of Christopher Nolan films.
  - **Results**: Recommends movies like *Arrival*, *Contact*, *2001: A Space Odyssey*, or *The Matrix*.
  - **Why it makes sense**: The SBERT model matches description overviews semantically, and the hybrid ranker combines this with SVD user factor weights.

### Case 2: Comedy Filter Extraction
- **User Profile**:
  - Favorite Genres: `["Comedy", "Romance"]`
- **Search Query**: "Something light and funny for tonight under 2 hours"
- **Expected Behavior**:
  - The semantic parser detects the keywords "funny" (mood: funny) and "under 2 hours" (duration: short).
  - Movies with runtime < 100 minutes get a $+0.08$ score boost.
  - Comedy movies with humor descriptions get a $+0.05$ score boost.
  - Collaborative scores are down-weighted since this is a highly specific search.
  - **Results**: Recommends short, popular comedies or rom-coms like *Toy Story*, *Liar Liar*, or *Groundhog Day*.
  - **Why it makes sense**: Structured regex keyword filters extract constraints (short length, comedy genre) and apply soft boosts to ensure criteria are satisfied.

### Case 3: Cold Start Onboarding
- **User Profile**:
  - Liked Movies: `[]` (Empty)
  - Favorite Genres: `["Action", "Thriller"]`
  - Preference: "Hidden gems"
- **Search Query**: `None`
- **Expected Behavior**:
  - The system detects a history length of 0 and selects the `COLD_START_WEIGHTS` strategy.
  - Collaborative filtering weight is set to $0.0$ (avoiding empty latent factors).
  - Content-based, genre match, and quality weights are scaled.
  - The "hidden gems" selection filters for items with high quality scores ($>0.7$) and low popularity scores ($<0.15$).
  - **Results**: Recommends highly-rated but lesser-known thrillers or action movies.
  - **Why it makes sense**: Eliminating SVD weights and relying on quality priors + onboarding genre vectors prevents cold-start failures.

---

## 2. Failure Scenarios & Limitations

### Scenario A: Vague or Ambiguous Query
- **Input Query**: "something good" or "a movie"
- **Problem**: The query has no semantic specificity or filter indicators.
- **System Behavior**: The semantic similarity matches description words randomly (or gets low scores across the board).
- **Mitigation**: The hybrid ranker redistributes weights. Since the query score is flat, the system relies on the user's rating history, favorite genres, and popularity/quality priors.

### Scenario B: Sparse Movie Metadata
- **Problem**: A newly added movie has an overview of only 4 words (e.g. "A fun movie about cars") and no keywords.
- **System Behavior**: Content-based and semantic match scores will be artificially low because TF-IDF/SBERT representations lack text density.
- **Mitigation**: The SVD collaborative filtering signal and popularity/quality priors can still surface the movie once users start rating it, compensating for weak metadata.

### Scenario C: Niche or Highly Unusual Taste
- **Problem**: A user likes *Toy Story* but also *The Texas Chainsaw Massacre*. These items are rarely rated together in the dataset, creating sparse latent factors.
- **System Behavior**: SVD latent factors cannot reconcile these contradictory user preferences, resulting in weak collaborative matching.
- **Mitigation**: The content-based recommender evaluates content profiles independently. It will recommend a mix of family animation and horror titles, and MMR diversity re-ranking will ensure both genres are represented in the final list.

### Scenario D: Filter Bubbles
- **Problem**: Over time, a user who likes 3 action movies gets recommended only action movies, trapping them in a feedback loop.
- **System Behavior**: Content-based recommendations overspecialize.
- **Mitigation**: MMR (Maximal Marginal Relevance) re-ranking. By raising the diversity mode to "Exploratory" (diversity lambda $= 0.2$), the system penalizes similarity between recommended movies, forcing a diverse selection of genres and themes.
