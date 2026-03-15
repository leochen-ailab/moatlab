import { useScreenerStore } from "../stores/screenerStore";
import ScreenerForm from "../components/screener/ScreenerForm";
import ScreenerResults from "../components/screener/ScreenerResults";
import Spinner from "../components/common/Spinner";

export default function ScreenerPage() {
  const { result, loading, error } = useScreenerStore();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">股票筛选</h1>

      <ScreenerForm />

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading && <Spinner text="正在筛选..." />}

      {result && !loading && <ScreenerResults result={result} />}
    </div>
  );
}
