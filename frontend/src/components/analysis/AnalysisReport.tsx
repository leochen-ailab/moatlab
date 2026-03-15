import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { AnalysisResult } from "../../types/analysis";

const sectionLabels: Record<string, string> = {
  moat: "护城河分析",
  management: "管理层分析",
  financial: "财务分析",
  valuation: "估值分析",
  decision: "投资决策",
};

const sectionOrder = ["decision", "moat", "management", "financial", "valuation"];

interface Props {
  result: AnalysisResult;
  isFullMode: boolean;
}

export default function AnalysisReport({ result, isFullMode }: Props) {
  // 全面模式：分章节展示；单项模式：直接展示 result 字段
  if (!isFullMode) {
    const content = result.result || Object.values(result)[0] || "";
    return <MarkdownBlock content={content} />;
  }

  // 全面模式：按 sectionOrder 分章节
  return (
    <div className="space-y-3">
      {sectionOrder.map((key) => {
        const content = result[key];
        if (!content) return null;
        return (
          <CollapsibleSection
            key={key}
            title={sectionLabels[key] || key}
            defaultOpen={key === "decision"}
          >
            <MarkdownBlock content={content} />
          </CollapsibleSection>
        );
      })}
    </div>
  );
}

function CollapsibleSection({
  title,
  defaultOpen = false,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-900 hover:bg-gray-800 text-left"
      >
        <span className="font-medium">{title}</span>
        <span className="text-gray-500 text-sm">{open ? "收起" : "展开"}</span>
      </button>
      {open && <div className="px-4 py-4 border-t border-gray-800">{children}</div>}
    </div>
  );
}

function MarkdownBlock({ content }: { content: string }) {
  return (
    <div className="prose prose-invert prose-sm max-w-none">
      <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
    </div>
  );
}
