import type { PortfolioData } from "../../types/portfolio";

export default function PortfolioSummary({ data }: { data: PortfolioData }) {
  const totalReturn = data.total_return ?? (data.total_market_value - data.total_cost);
  const returnColor =
    totalReturn >= 0 ? "text-green-400" : "text-red-400";

  const cards = [
    { label: "总市值", value: `$${data.total_market_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}` },
    { label: "总成本", value: `$${data.total_cost.toLocaleString("en-US", { minimumFractionDigits: 2 })}` },
    {
      label: "总回报",
      value: `$${totalReturn.toLocaleString("en-US", { minimumFractionDigits: 2 })}`,
      sub: `${(data.total_return_pct ?? 0) >= 0 ? "+" : ""}${(data.total_return_pct ?? 0).toFixed(1)}%`,
      color: returnColor,
    },
    { label: "持仓数", value: String(data.positions.length) },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {cards.map((c) => (
        <div
          key={c.label}
          className="bg-gray-900 border border-gray-800 rounded-lg p-4"
        >
          <div className="text-xs text-gray-500 mb-1">{c.label}</div>
          <div className={`text-xl font-bold ${c.color ?? "text-white"}`}>
            {c.value}
          </div>
          {c.sub && (
            <div className={`text-sm ${c.color}`}>{c.sub}</div>
          )}
        </div>
      ))}
    </div>
  );
}
