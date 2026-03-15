import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useAnalysisStore } from "../stores/analysisStore";
import type { AnalysisHistoryEntry } from "../stores/analysisStore";
import AnalysisSearch from "../components/analysis/AnalysisSearch";
import AnalysisReport from "../components/analysis/AnalysisReport";
import Spinner from "../components/common/Spinner";

const MODE_LABELS: Record<string, string> = {
  full: "全面",
  moat: "护城河",
  management: "管理层",
  financial: "财务",
  valuation: "估值",
};

export default function AnalysisPage() {
  const {
    ticker,
    mode,
    result,
    loading,
    error,
    history,
    setTicker,
    setMode,
    analyze,
    loadFromHistory,
    clearHistory,
  } = useAnalysisStore();

  const [searchParams] = useSearchParams();

  // URL query 预填 ticker
  useEffect(() => {
    const q = searchParams.get("ticker");
    if (q && q.toUpperCase() !== ticker) {
      setTicker(q);
    }
  }, [searchParams, setTicker, ticker]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">股票分析</h1>

      <AnalysisSearch
        ticker={ticker}
        mode={mode}
        loading={loading}
        onTickerChange={setTicker}
        onModeChange={setMode}
        onSubmit={analyze}
      />

      {error && (
        <div className="p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm mb-4">
          {error}
        </div>
      )}

      {loading && <Spinner text={`正在深度分析 ${ticker}...`} />}

      {result && !loading && (
        <AnalysisReport result={result} isFullMode={mode === "full"} />
      )}

      {/* 分析历史 */}
      {!loading && !result && history.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm text-gray-500">最近分析</h2>
            <button
              onClick={clearHistory}
              className="text-xs text-gray-500 hover:text-gray-400"
            >
              清除历史
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {history.map((entry: AnalysisHistoryEntry, i: number) => (
              <button
                key={`${entry.ticker}-${entry.mode}-${i}`}
                onClick={() => loadFromHistory(entry)}
                className="text-left bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-colors"
              >
                <div className="font-medium text-blue-400">{entry.ticker}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {MODE_LABELS[entry.mode] || entry.mode} · {new Date(entry.timestamp).toLocaleDateString("zh-CN")}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
