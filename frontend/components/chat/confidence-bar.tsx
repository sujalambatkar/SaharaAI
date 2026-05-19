const THRESHOLD = 0.65;

export function ConfidenceBar({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const isLow = confidence < THRESHOLD;

  return (
    <div className="mt-1.5 w-full">
      <div className="flex items-center justify-between mb-0.5">
        <span className="text-[10px] text-gray-400">Confidence</span>
        <span
          className={`text-[10px] font-medium ${isLow ? "text-red-500" : "text-green-600"}`}
        >
          {pct}%
        </span>
      </div>
      <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isLow ? "bg-red-400" : "bg-green-500"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
