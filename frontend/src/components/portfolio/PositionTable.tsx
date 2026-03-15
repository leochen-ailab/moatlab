import { Link } from "react-router-dom";
import type { Position } from "../../types/portfolio";

interface Props {
  positions: Position[];
  onTrade: (ticker: string, action: "buy" | "sell") => void;
}

export default function PositionTable({ positions, onTrade }: Props) {
  if (positions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        暂无持仓，点击右上角"买入"添加第一笔交易
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800 text-gray-500 text-left">
            <th className="pb-2 font-medium">股票</th>
            <th className="pb-2 font-medium text-right">股数</th>
            <th className="pb-2 font-medium text-right">均价</th>
            <th className="pb-2 font-medium text-right">现价</th>
            <th className="pb-2 font-medium text-right">市值</th>
            <th className="pb-2 font-medium text-right">盈亏</th>
            <th className="pb-2 font-medium text-right">盈亏%</th>
            <th className="pb-2 font-medium text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((p) => {
            const color = p.pnl >= 0 ? "text-green-400" : "text-red-400";
            return (
              <tr
                key={p.ticker}
                className="border-b border-gray-800/50 hover:bg-gray-900/50"
              >
                <td className="py-3">
                  <Link
                    to={`/analysis?ticker=${p.ticker}`}
                    className="font-bold text-white hover:text-blue-400"
                  >
                    {p.ticker}
                  </Link>
                </td>
                <td className="py-3 text-right">{p.shares.toFixed(0)}</td>
                <td className="py-3 text-right">${p.avg_cost.toFixed(2)}</td>
                <td className="py-3 text-right">
                  ${p.current_price.toFixed(2)}
                </td>
                <td className="py-3 text-right">
                  ${p.market_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </td>
                <td className={`py-3 text-right ${color}`}>
                  ${p.pnl.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </td>
                <td className={`py-3 text-right ${color}`}>
                  {p.pnl_pct >= 0 ? "+" : ""}{p.pnl_pct.toFixed(1)}%
                </td>
                <td className="py-3 text-right space-x-2">
                  <button
                    onClick={() => onTrade(p.ticker, "buy")}
                    className="text-xs px-2 py-1 rounded bg-green-900/50 text-green-400 hover:bg-green-900"
                  >
                    加仓
                  </button>
                  <button
                    onClick={() => onTrade(p.ticker, "sell")}
                    className="text-xs px-2 py-1 rounded bg-yellow-900/50 text-yellow-400 hover:bg-yellow-900"
                  >
                    减仓
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
