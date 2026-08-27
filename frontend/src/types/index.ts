export interface MovieRecommendation {
  movie_id: number;
  title: string;
  overview: string | null;
  genres: string[];
  release_year: string | null;
  runtime: number | null;
  vote_average: number | null;
  poster_url: string | null;
  score: number;
  explanation: string;
  score_breakdown: {
    content: number;
    collaborative: number;
    semantic: number;
    genre: number;
    quality: number;
    popularity: number;
  };
}

export interface LatencyMetadata {
  ranking: number;
  diversity: number;
  explanation: number;
  total: number;
}

export interface RecommendResponseMetadata {
  strategy: string;
  candidate_count: number;
  weights_used: Record<string, number>;
  latency_ms: LatencyMetadata;
}

export interface RecommendResponse {
  recommendations: MovieRecommendation[];
  metadata: RecommendResponseMetadata;
}

export interface SearchResultMovie {
  movie_id: number;
  title: string;
  overview: string | null;
  genres: string[];
  release_year: string | null;
  runtime: number | null;
  vote_average: number | null;
  poster_url: string | null;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultMovie[];
  latency_ms: number;
}

export interface MovieDetails {
  movie_id: number;
  title: string;
  overview: string | null;
  genres: string[];
  keywords: string[];
  cast: string[];
  director: string | null;
  release_date: string | null;
  runtime: number | null;
  vote_average: number | null;
  popularity: number | null;
  poster_url: string | null;
}
