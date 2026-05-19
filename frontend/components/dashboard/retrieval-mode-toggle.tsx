"use client";

import { useState } from "react";
import { updateRetrievalMode } from "@/lib/api";
import { Zap, Database } from "lucide-react";

interface RetrievalModeToggleProps {
  currentMode: string;
  onModeChange: (mode: string) => void;
}

export function RetrievalModeToggle({
  currentMode,
  onModeChange,
}: RetrievalModeToggleProps) {
  const [loading, setLoading] = useState(false);
  const [localMode, setLocalMode] = useState(currentMode);

  async function handleToggle(mode: "dense_only" | "hybrid") {
    if (mode === localMode || loading) return;
    setLoading(true);
    try {
      await updateRetrievalMode(mode);
      setLocalMode(mode);
      onModeChange(mode);
    } catch {
      // revert on error
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-700">
            Retrieval Mode
          </h3>
          <p className="text-xs text-gray-400 mt-0.5">
            Switch between dense vector search and hybrid (dense + BM25)
          </p>
        </div>
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => handleToggle("dense_only")}
            disabled={loading}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              localMode === "dense_only"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            } disabled:opacity-50`}
          >
            <Database size={12} />
            Dense
          </button>
          <button
            onClick={() => handleToggle("hybrid")}
            disabled={loading}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              localMode === "hybrid"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            } disabled:opacity-50`}
          >
            <Zap size={12} />
            Hybrid
          </button>
        </div>
      </div>
      <p className="text-[10px] text-gray-400 mt-2">
        {localMode === "hybrid"
          ? "Hybrid mode: dense vectors + BM25 sparse search fused with RRF for best recall."
          : "Dense-only mode: pure semantic similarity via cosine distance."}
      </p>
    </div>
  );
}
