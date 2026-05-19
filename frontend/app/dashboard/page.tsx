"use client";

import { useEffect, useState, useCallback } from "react";
import { fetchDashboard } from "@/lib/api";
import type { DashboardResponse } from "@/lib/types";
import { QueryStats } from "@/components/dashboard/query-stats";
import { CostChart } from "@/components/dashboard/cost-chart";
import { RetrievalModeToggle } from "@/components/dashboard/retrieval-mode-toggle";
import { RefreshCw, MessageSquare } from "lucide-react";
import Link from "next/link";

const REFRESH_INTERVAL_MS = 30_000;

export default function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const result = await fetchDashboard();
      setData(result);
      setLastRefresh(new Date());
      setError(null);
    } catch {
      setError("Could not reach the backend. Is it running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [load]);

  return (
    <div className="min-h-screen bg-sahara-cream">
      {/* Header */}
      <header className="bg-white border-b border-sahara-sand shadow-sm px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-sahara-saffron flex items-center justify-center text-white font-bold text-sm">
            S
          </div>
          <div>
            <h1 className="font-semibold text-gray-900 text-sm">
              SaharaAI Dashboard
            </h1>
            <p className="text-xs text-gray-500">
              Cost & query analytics — auto-refreshes every 30s
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-[10px] text-gray-400">
              Updated {lastRefresh.toLocaleTimeString("en-IN")}
            </span>
          )}
          <button
            onClick={load}
            className="text-gray-400 hover:text-sahara-saffron transition-colors"
            aria-label="Refresh"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
          <Link
            href="/chat"
            className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-sahara-saffron transition-colors"
          >
            <MessageSquare size={14} />
            Chat
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}

        {data ? (
          <>
            <QueryStats stats={data.stats} />
            <CostChart data={data.daily_metrics} />
            <RetrievalModeToggle
              currentMode={data.current_retrieval_mode}
              onModeChange={(mode) =>
                setData((prev) =>
                  prev ? { ...prev, current_retrieval_mode: mode } : prev
                )
              }
            />

            {/* Recent queries table */}
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Recent Queries (Today)
              </h3>
              {data.stats.recent_queries.length === 0 ? (
                <p className="text-sm text-gray-400">No queries yet today.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-left text-gray-400 border-b border-gray-50">
                        <th className="pb-2 font-medium">Query</th>
                        <th className="pb-2 font-medium">Lang</th>
                        <th className="pb-2 font-medium">Conf.</th>
                        <th className="pb-2 font-medium">Handoff</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.stats.recent_queries.map((q, i) => (
                        <tr
                          key={i}
                          className="border-b border-gray-50 hover:bg-gray-50"
                        >
                          <td className="py-2 text-gray-700 max-w-[200px] truncate pr-4">
                            {q.query}
                          </td>
                          <td className="py-2">
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-gray-100 text-gray-600">
                              {q.language}
                            </span>
                          </td>
                          <td className="py-2 text-gray-600">
                            {Math.round(q.confidence * 100)}%
                          </td>
                          <td className="py-2">
                            {q.handoff ? (
                              <span className="text-amber-600 font-medium">
                                Yes
                              </span>
                            ) : (
                              <span className="text-green-600">No</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        ) : (
          !error && (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
              Loading dashboard...
            </div>
          )
        )}
      </main>
    </div>
  );
}
