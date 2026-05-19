import type { DashboardStats } from "@/lib/types";
import { TrendingUp, Users, PhoneCall, Globe } from "lucide-react";

const LANG_LABELS: Record<string, string> = {
  EN: "English",
  HI: "Hindi",
  HINGLISH: "Hinglish",
};

function StatCard({
  title,
  value,
  sub,
  icon: Icon,
  accent,
}: {
  title: string;
  value: string;
  sub?: string;
  icon: React.ElementType;
  accent: string;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-500 font-medium">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        </div>
        <div
          className={`w-9 h-9 rounded-lg flex items-center justify-center ${accent}`}
        >
          <Icon size={16} />
        </div>
      </div>
    </div>
  );
}

export function QueryStats({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <StatCard
        title="Queries Today"
        value={String(stats.total_queries_today)}
        icon={TrendingUp}
        accent="bg-blue-50 text-blue-600"
      />
      <StatCard
        title="Avg Confidence"
        value={`${Math.round(stats.avg_confidence * 100)}%`}
        sub={stats.avg_confidence >= 0.65 ? "Good" : "Needs improvement"}
        icon={Users}
        accent="bg-green-50 text-green-600"
      />
      <StatCard
        title="Handoff Rate"
        value={`${stats.handoff_rate_pct.toFixed(1)}%`}
        sub="Human escalations"
        icon={PhoneCall}
        accent="bg-amber-50 text-amber-600"
      />
      <StatCard
        title="Top Language"
        value={LANG_LABELS[stats.most_common_language] || stats.most_common_language}
        sub={`$${stats.estimated_cost_today_usd.toFixed(5)} spent today`}
        icon={Globe}
        accent="bg-purple-50 text-purple-600"
      />
    </div>
  );
}
