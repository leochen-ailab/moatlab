import { Link } from "react-router-dom";
import type { Performance } from "../../types/portfolio";

interface Props {
  performance: Performance;
}

export default function TopMovers({ performance }: Props) {
  const winners = performance.winners ?? [];
  const losers = performance.losers ?? [];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h2 className="text-sm text-gray-500 mb-3">赢家 TOP 3</h2>
        {winners.length === 0 ? (
          <p className="text-gray-500 text-sm">暂无数据</p>
        ) : (
          <ul className="space-y-3">
            {winners.slice(0, 3).map((p) => (
              <li key={p.ticker} className="flex items-center justify-between">
                <Link
                  to={`/analysis?ticker=${p.ticker}`}
                  className="text-blue-400 hover:underline font-medium"
                >
                  {p.ticker}
                </Link>
                <div className="text-right">
                  <span className="text-green-400 text-sm font-medium">
                    +${p.pnl.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-green-400 text-xs ml-2">
                    +{p.pnl_pct.toFixed(1)}%
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h2 className="text-sm text-gray-500 mb-3">输家 TOP 3</h2>
        {losers.length === 0 ? (
          <p className="text-gray-500 text-sm">暂无数据</p>
        ) : (
          <ul className="space-y-3">
            {losers.slice(0, 3).map((p) => (
              <li key={p.ticker} className="flex items-center justify-between">
                <Link
                  to={`/analysis?ticker=${p.ticker}`}
                  className="text-blue-400 hover:underline font-medium"
                >
                  {p.ticker}
                </Link>
                <div className="text-right">
                  <span className="text-red-400 text-sm font-medium">
                    ${p.pnl.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-red-400 text-xs ml-2">
                    {p.pnl_pct.toFixed(1)}%
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
