import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { reviewPortfolio } from "../../api/portfolio";
import Spinner from "../common/Spinner";

export default function PortfolioReview() {
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleReview = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await reviewPortfolio();
      setResult(res.result);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {!loading && !result && (
        <div className="text-center py-12">
          <p className="text-gray-400 mb-4">
            AI 将逐一检查每个持仓的投资逻辑，评估集中度风险，并给出再平衡建议。
          </p>
          <button
            onClick={handleReview}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded font-medium"
          >
            开始回顾
          </button>
        </div>
      )}

      {loading && <Spinner text="正在分析您的持仓..." />}

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm">
          {error}
          <button
            onClick={handleReview}
            className="ml-3 underline hover:no-underline"
          >
            重试
          </button>
        </div>
      )}

      {result && (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <div className="prose prose-invert prose-sm max-w-none">
            <Markdown remarkPlugins={[remarkGfm]}>{result}</Markdown>
          </div>
          <div className="mt-6 pt-4 border-t border-gray-800">
            <button
              onClick={handleReview}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded font-medium"
            >
              重新回顾
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
