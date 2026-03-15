import { useState, useEffect, useRef } from "react";
import type { AnalysisMode } from "../../types/analysis";

const modes: { value: AnalysisMode; label: string }[] = [
  { value: "full", label: "全面分析" },
  { value: "moat", label: "护城河" },
  { value: "management", label: "管理层" },
  { value: "financial", label: "财务" },
  { value: "valuation", label: "估值" },
];

const SEARCH_HISTORY_KEY = "moatlab-search-history";
const MAX_HISTORY = 10;

// 热门股票
const POPULAR_STOCKS = [
  { ticker: "AAPL", name: "Apple Inc.", name_cn: "苹果" },
  { ticker: "MSFT", name: "Microsoft", name_cn: "微软" },
  { ticker: "GOOGL", name: "Alphabet", name_cn: "谷歌" },
  { ticker: "AMZN", name: "Amazon", name_cn: "亚马逊" },
  { ticker: "TSLA", name: "Tesla", name_cn: "特斯拉" },
  { ticker: "META", name: "Meta", name_cn: "Meta" },
  { ticker: "NVDA", name: "NVIDIA", name_cn: "英伟达" },
  { ticker: "BRK-B", name: "Berkshire Hathaway", name_cn: "伯克希尔" },
];

interface SearchResult {
  ticker: string;
  name: string;
  name_cn: string;
  sector: string;
  match_score: number;
}

interface SearchHistoryItem {
  ticker: string;
  name: string;
  name_cn: string;
  timestamp: number;
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
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Load search history on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(SEARCH_HISTORY_KEY);
      if (stored) {
        setSearchHistory(JSON.parse(stored));
      }
    } catch (error) {
      console.error("Failed to load search history:", error);
    }
  }, []);

  // Save to search history
  const addToHistory = (result: SearchResult) => {
    const newItem: SearchHistoryItem = {
      ticker: result.ticker,
      name: result.name,
      name_cn: result.name_cn,
      timestamp: Date.now(),
    };

    const updated = [
      newItem,
      ...searchHistory.filter((item) => item.ticker !== result.ticker),
    ].slice(0, MAX_HISTORY);

    setSearchHistory(updated);
    try {
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error("Failed to save search history:", error);
    }
  };

  // Clear search history
  const clearHistory = () => {
    setSearchHistory([]);
    try {
      localStorage.removeItem(SEARCH_HISTORY_KEY);
    } catch (error) {
      console.error("Failed to clear search history:", error);
    }
  };

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
    addToHistory(result);
    onTickerChange(result.ticker);
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const selectFromHistory = (item: SearchHistoryItem) => {
    onTickerChange(item.ticker);
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

      {/* Search History */}
      {!ticker && searchHistory.length > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm text-gray-500">最近搜索</h3>
            <button
              onClick={clearHistory}
              className="text-xs text-gray-500 hover:text-gray-400"
            >
              清除
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {searchHistory.map((item) => (
              <button
                key={item.ticker}
                onClick={() => selectFromHistory(item)}
                className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded text-sm text-gray-300 transition-colors"
              >
                <span className="font-medium text-blue-400">{item.ticker}</span>
                {item.name_cn && (
                  <span className="ml-1.5 text-gray-500">
                    {item.name_cn}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Popular Stocks */}
      {!ticker && searchHistory.length === 0 && (
        <div className="mt-4">
          <h3 className="text-sm text-gray-500 mb-2">热门股票</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {POPULAR_STOCKS.map((stock) => (
              <button
                key={stock.ticker}
                onClick={() => onTickerChange(stock.ticker)}
                className="px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm text-left transition-colors"
              >
                <div className="font-medium text-blue-400">{stock.ticker}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {stock.name_cn}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
