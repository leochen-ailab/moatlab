import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useAnalysisStore } from "../stores/analysisStore";
import AnalysisSearch from "../components/analysis/AnalysisSearch";
import AnalysisReport from "../components/analysis/AnalysisReport";
import Spinner from "../components/common/Spinner";

export default function AnalysisPage() {
  const {
    ticker,
    mode,
    result,
    loading,
    error,
    setTicker,
    setMode,
    analyze,
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
    </div>
  );
}
