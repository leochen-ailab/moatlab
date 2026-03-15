import { useState } from "react";
import { useNavigate } from "react-router-dom";

interface Props {
  onOpenTrade: () => void;
}

export default function QuickActions({ onOpenTrade }: Props) {
  const navigate = useNavigate();
  const [ticker, setTicker] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim()) {
      navigate(`/analysis?ticker=${ticker.trim().toUpperCase()}`);
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
      <h2 className="text-sm text-gray-500 mb-3">快捷入口</h2>
      <div className="flex gap-3">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <input
            type="text"
            placeholder="输入股票代码，如 AAPL"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={!ticker.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm rounded font-medium"
          >
            分析
          </button>
        </form>
        <button
          onClick={onOpenTrade}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded font-medium"
        >
          买入
        </button>
      </div>
    </div>
  );
}
