import axios from "axios";
import type { ChatResponse, DashboardResponse } from "./types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

export async function sendMessage(
  query: string,
  retrieval_mode?: string
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>("/chat", {
    query,
    ...(retrieval_mode ? { retrieval_mode } : {}),
  });
  return response.data;
}

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await api.get<DashboardResponse>("/dashboard");
  return response.data;
}

export async function updateRetrievalMode(
  mode: "dense_only" | "hybrid"
): Promise<void> {
  await api.patch("/dashboard/retrieval-mode", { mode });
}
