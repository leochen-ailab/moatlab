import type { AnalysisMode } from "../../types/analysis";

const modes: { value: AnalysisMode; label: string }[] = [
  { value: "full", label: "全面分析" },
  { value: "moat", label: "护城河" },
  { value: "management", label: "管理层" },
  { value: "financial", label: "财务" },
  { value: "valuation", label: "估值" },
];

interface Props {
  ticker: string;
  mode: AnalysisMode;
  loading: boolean;
  onTickerChange: (t: string) => void;
  onModeChange: (m: AnalysisMode) => void;
  onSubmit: () => void;
}

export default function AnalysisSearch({
  ticker,
  mode,
  loading,
  onTickerChange,
  onModeChange,
  onSubmit,
}: Props) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") onSubmit();
  };

  return (
    <div className="space-y-4 mb-6">
      <div className="flex gap-3">
        <input
          type="text"
          value={ticker}
          onChange={(e) => onTickerChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入股票代码，如 AAPL"
          className="flex-1 bg-gray-900 border border-gray-700 rounded px-4 py-2.5 text-white focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={onSubmit}
          disabled={!ticker || loading}
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:opacity-50"
        >
          {loading ? "分析中..." : "开始分析"}
        </button>
      </div>

      <div className="flex gap-1">
        {modes.map((m) => (
          <button
            key={m.value}
            onClick={() => onModeChange(m.value)}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              mode === m.value
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700"
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>
    </div>
  );
}
