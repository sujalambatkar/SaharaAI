"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { DailyMetric } from "@/lib/types";

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
}

export function CostChart({ data }: { data: DailyMetric[] }) {
  const formatted = data.map((d) => ({
    ...d,
    dateLabel: formatDate(d.date),
    cost_usd_display: parseFloat(d.cost_usd.toFixed(5)),
  }));

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">
        Daily Cost & Query Volume (Last 7 Days)
      </h3>
      {formatted.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
          No data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={formatted}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="dateLabel"
              tick={{ fontSize: 11, fill: "#6b7280" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              yAxisId="cost"
              orientation="left"
              tick={{ fontSize: 11, fill: "#6b7280" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `$${v.toFixed(4)}`}
            />
            <YAxis
              yAxisId="count"
              orientation="right"
              tick={{ fontSize: 11, fill: "#6b7280" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                fontSize: 11,
                borderRadius: 8,
                border: "1px solid #e5e7eb",
              }}
              formatter={(value: number, name: string) => {
                if (name === "Cost (USD)") return [`$${value.toFixed(5)}`, name];
                return [value, name];
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line
              yAxisId="cost"
              type="monotone"
              dataKey="cost_usd_display"
              name="Cost (USD)"
              stroke="#FF6B00"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              yAxisId="count"
              type="monotone"
              dataKey="query_count"
              name="Queries"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
