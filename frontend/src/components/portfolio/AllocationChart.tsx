import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { useNavigate } from "react-router-dom";
import type { Position } from "../../types/portfolio";

const COLORS = [
  "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
  "#06b6d4", "#ec4899", "#84cc16", "#f97316", "#6366f1",
];

interface Props {
  positions: Position[];
}

export default function AllocationChart({ positions }: Props) {
  const navigate = useNavigate();

  if (positions.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h2 className="text-sm text-gray-500 mb-3">持仓分布</h2>
        <p className="text-gray-500 text-sm">暂无持仓数据</p>
      </div>
    );
  }

  const data = positions.map((p) => ({
    name: p.ticker,
    value: p.market_value,
    shares: p.shares,
  }));

  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
      <h2 className="text-sm text-gray-500 mb-3">持仓分布</h2>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            dataKey="value"
            cursor="pointer"
            onClick={(entry) => navigate(`/analysis?ticker=${entry.name}`)}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
            itemStyle={{ color: "#e5e7eb" }}
            formatter={(value, name, entry) => {
              const v = Number(value);
              const pct = ((v / total) * 100).toFixed(1);
              const shares = (entry?.payload as { shares?: number })?.shares ?? 0;
              return [`$${v.toLocaleString("en-US", { minimumFractionDigits: 2 })} (${pct}%) · ${shares} 股`, String(name)];
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
