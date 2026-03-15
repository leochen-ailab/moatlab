import { useState, useEffect, useRef } from "react";
import type { AnalysisMode } from "../../types/analysis";

const modes: { value: AnalysisMode; label: string }[] = [
  { value: "full", label: "全面分析" },
  { value: "moat", label: "护城河" },
  { value: "management", label: "管理层" },
  { value: "financial", label: "财务" },
  { value: "valuation", label: "估值" },
];

interface SearchResult {
  ticker: string;
  name: string;
  name_cn: string;
  sector: string;
  match_score: number;
}

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
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Debounced search
  useEffect(() => {
    if (!ticker || ticker.length < 2) {
      setSearchResults([]);
      setShowSuggestions(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const response = await fetch(`/api/search/stocks?q=${encodeURIComponent(ticker)}&limit=10`);
        if (response.ok) {
          const data = await response.json();
          setSearchResults(data.results || []);
          setShowSuggestions(data.results.length > 0);
        }
      } catch (error) {
        console.error("Search failed:", error);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [ticker]);

  // Click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      if (selectedIndex >= 0 && searchResults[selectedIndex]) {
        selectResult(searchResults[selectedIndex]);
      } else {
        onSubmit();
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, searchResults.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, -1));
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  };

  const selectResult = (result: SearchResult) => {
    onTickerChange(result.ticker);
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  return (
    <div className="space-y-4 mb-6">
      <div className="flex gap-3 relative">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={ticker}
            onChange={(e) => onTickerChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => searchResults.length > 0 && setShowSuggestions(true)}
            placeholder="输入股票代码或公司名，如 AAPL 或 苹果"
            className="w-full bg-gray-900 border border-gray-700 rounded px-4 py-2.5 text-white focus:outline-none focus:border-blue-500"
          />
          {isSearching && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="w-4 h-4 border-2 border-gray-600 border-t-blue-500 rounded-full animate-spin" />
            </div>
          )}

          {showSuggestions && searchResults.length > 0 && (
            <div
              ref={suggestionsRef}
              className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-700 rounded shadow-lg max-h-80 overflow-y-auto"
            >
              {searchResults.map((result, index) => (
                <button
                  key={result.ticker}
                  onClick={() => selectResult(result)}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-700 transition-colors ${
                    index === selectedIndex ? "bg-gray-700" : ""
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-white font-medium">{result.ticker}</div>
                      <div className="text-sm text-gray-400">
                        {result.name_cn || result.name}
                      </div>
                    </div>
                    {result.sector && (
                      <div className="text-xs text-gray-500">{result.sector}</div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
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
