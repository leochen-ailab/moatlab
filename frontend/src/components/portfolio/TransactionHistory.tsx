import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { usePortfolioStore } from "../../stores/portfolioStore";
import Spinner from "../common/Spinner";

export default function TransactionHistory() {
  const { history, loading, error, fetchHistory, data } = usePortfolioStore();
  const [filter, setFilter] = useState("");

  // 从持仓数据中提取 ticker 列表用于筛选
  const tickers = data?.positions.map((p) => p.ticker) ?? [];

  useEffect(() => {
    fetchHistory(filter || undefined);
  }, [fetchHistory, filter]);

  if (loading && !history) return <Spinner text="正在获取交易历史..." />;

  return (
    <div>
      {/* 筛选器 */}
      <div className="mb-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
        >
          <option value="">全部股票</option>
          {tickers.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm">
          {error}
        </div>
      )}

      {history && history.transactions.length === 0 ? (
        <p className="text-gray-500 text-sm">暂无交易记录</p>
      ) : history ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-800">
                <th className="pb-2 pr-4">日期</th>
                <th className="pb-2 pr-4">操作</th>
                <th className="pb-2 pr-4">股票</th>
                <th className="pb-2 pr-4 text-right">股数</th>
                <th className="pb-2 pr-4 text-right">价格</th>
                <th className="pb-2">备注</th>
              </tr>
            </thead>
            <tbody>
              {history.transactions.map((tx, i) => (
                <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                  <td className="py-2 pr-4 text-gray-400">{tx.date}</td>
                  <td className="py-2 pr-4">
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded ${
                        tx.action === "buy"
                          ? "bg-green-900/40 text-green-400"
                          : "bg-yellow-900/40 text-yellow-400"
                      }`}
                    >
                      {tx.action === "buy" ? "买入" : "卖出"}
                    </span>
                  </td>
                  <td className="py-2 pr-4">
                    <Link
                      to={`/analysis?ticker=${tx.ticker}`}
                      className="text-blue-400 hover:underline"
                    >
                      {tx.ticker}
                    </Link>
                  </td>
                  <td className="py-2 pr-4 text-right">{tx.shares}</td>
                  <td className="py-2 pr-4 text-right">
                    ${tx.price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-2 text-gray-500">{tx.notes || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
