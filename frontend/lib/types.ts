export type LanguageDetected = "EN" | "HI" | "HINGLISH";

export interface ChatResponse {
  answer: string;
  language_detected: LanguageDetected;
  confidence: number;
  sources: string[];
  handoff_triggered: boolean;
  retrieval_mode_used: string;
  estimated_cost_usd: number;
  trace_url: string | null;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  metadata?: ChatResponse;
}

export interface DailyMetric {
  date: string;
  cost_usd: number;
  query_count: number;
}

export interface DashboardStats {
  total_queries_today: number;
  avg_confidence: number;
  handoff_rate_pct: number;
  most_common_language: LanguageDetected;
  estimated_cost_today_usd: number;
  queries_by_language: Record<string, number>;
  recent_queries: RecentQuery[];
}

export interface RecentQuery {
  query: string;
  language: LanguageDetected;
  confidence: number;
  handoff: boolean;
  created_at: string;
}

export interface DashboardResponse {
  stats: DashboardStats;
  daily_metrics: DailyMetric[];
  current_retrieval_mode: string;
}
