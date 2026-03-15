import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Link } from "react-router-dom";
import type { ScreenResult } from "../../types/screener";

interface Props {
  result: ScreenResult;
}

export default function ScreenerResults({ result }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
      <h2 className="text-lg font-semibold mb-4">筛选结果</h2>
      <div className="prose prose-invert prose-sm max-w-none">
        <Markdown
          remarkPlugins={[remarkGfm]}
          components={{
            // 将 ticker 模式的文本转为可点击链接
            p: ({ children }) => <p>{transformTickers(children)}</p>,
            li: ({ children }) => <li>{transformTickers(children)}</li>,
            td: ({ children }) => <td>{transformTickers(children)}</td>,
          }}
        >
          {result.result}
        </Markdown>
      </div>
    </div>
  );
}

// 匹配大写字母开头的 1-5 字母 ticker（常见美股 ticker 格式）
const TICKER_RE = /\b([A-Z]{1,5})\b/g;

function transformTickers(children: React.ReactNode): React.ReactNode {
  if (typeof children === "string") {
    const parts: React.ReactNode[] = [];
    let last = 0;
    for (const match of children.matchAll(TICKER_RE)) {
      const ticker = match[1];
      const idx = match.index!;
      if (idx > last) parts.push(children.slice(last, idx));
      parts.push(
        <Link
          key={`${ticker}-${idx}`}
          to={`/analysis?ticker=${ticker}`}
          className="text-blue-400 hover:underline"
        >
          {ticker}
        </Link>,
      );
      last = idx + ticker.length;
    }
    if (last < children.length) parts.push(children.slice(last));
    return parts.length > 0 ? <>{parts}</> : children;
  }
  if (Array.isArray(children)) {
    return children.map((child, i) => (
      <span key={i}>{transformTickers(child)}</span>
    ));
  }
  return children;
}
