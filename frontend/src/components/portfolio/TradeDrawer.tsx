import { useState } from "react";
import type { TradeRequest } from "../../types/portfolio";

interface Props {
  open: boolean;
  defaultTicker?: string;
  defaultAction?: "buy" | "sell";
  onClose: () => void;
  onSubmit: (req: TradeRequest, action: "buy" | "sell") => Promise<void>;
}

export default function TradeDrawer({
  open,
  defaultTicker = "",
  defaultAction = "buy",
  onClose,
  onSubmit,
}: Props) {
  const [action, setAction] = useState<"buy" | "sell">(defaultAction);
  const [ticker, setTicker] = useState(defaultTicker);
  const [shares, setShares] = useState("");
  const [price, setPrice] = useState("");
  const [tradeDate, setTradeDate] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  // 当 props 变化时重置
  useState(() => {
    setAction(defaultAction);
    setTicker(defaultTicker);
  });

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker || !shares || !price) return;
    setSubmitting(true);
    setError("");
    try {
      await onSubmit(
        {
          ticker: ticker.toUpperCase(),
          shares: Number(shares),
          price: Number(price),
          trade_date: tradeDate || undefined,
          notes: notes || undefined,
        },
        action,
      );
      onClose();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* 遮罩 */}
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />
      {/* 抽屉 */}
      <div className="fixed right-0 top-0 h-full w-96 bg-gray-900 border-l border-gray-800 z-50 p-6 overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold">交易</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-white text-xl"
          >
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 买入/卖出切换 */}
          <div className="flex rounded overflow-hidden border border-gray-700">
            <button
              type="button"
              className={`flex-1 py-2 text-sm font-medium ${
                action === "buy"
                  ? "bg-green-600 text-white"
                  : "bg-gray-800 text-gray-400"
              }`}
              onClick={() => setAction("buy")}
            >
              买入
            </button>
            <button
              type="button"
              className={`flex-1 py-2 text-sm font-medium ${
                action === "sell"
                  ? "bg-yellow-600 text-white"
                  : "bg-gray-800 text-gray-400"
              }`}
              onClick={() => setAction("sell")}
            >
              卖出
            </button>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">
              股票代码
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="AAPL"
              required
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">股数</label>
              <input
                type="number"
                value={shares}
                onChange={(e) => setShares(e.target.value)}
                placeholder="100"
                min="1"
                required
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">
                价格 (USD)
              </label>
              <input
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="150.00"
                step="0.01"
                min="0"
                required
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">
              交易日期
            </label>
            <input
              type="date"
              value={tradeDate}
              onChange={(e) => setTradeDate(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">备注</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 resize-none"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className={`w-full py-2 rounded font-medium text-sm text-white ${
              action === "buy"
                ? "bg-green-600 hover:bg-green-700"
                : "bg-yellow-600 hover:bg-yellow-700"
            } disabled:opacity-50`}
          >
            {submitting
              ? "提交中..."
              : action === "buy"
                ? "确认买入"
                : "确认卖出"}
          </button>
        </form>
      </div>
    </>
  );
}
