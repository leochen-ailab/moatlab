import { useEffect, useState } from "react";
import { usePortfolioStore } from "../stores/portfolioStore";
import PortfolioSummary from "../components/portfolio/PortfolioSummary";
import PositionTable from "../components/portfolio/PositionTable";
import TradeDrawer from "../components/portfolio/TradeDrawer";
import Spinner from "../components/common/Spinner";
import { showToast } from "../components/common/Toast";

export default function PortfolioPage() {
  const { data, loading, error, fetchPortfolio, buy, sell } =
    usePortfolioStore();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTicker, setDrawerTicker] = useState("");
  const [drawerAction, setDrawerAction] = useState<"buy" | "sell">("buy");

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  const openDrawer = (ticker = "", action: "buy" | "sell" = "buy") => {
    setDrawerTicker(ticker);
    setDrawerAction(action);
    setDrawerOpen(true);
  };

  const handleTrade = async (
    req: Parameters<typeof buy>[0],
    action: "buy" | "sell",
  ) => {
    if (action === "buy") {
      await buy(req);
      showToast(`买入 ${req.ticker} 成功`, "success");
    } else {
      await sell(req);
      showToast(`卖出 ${req.ticker} 成功`, "success");
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">持仓管理</h1>
        <button
          onClick={() => openDrawer()}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded font-medium"
        >
          买入
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading && !data ? (
        <Spinner text="正在获取持仓数据..." />
      ) : data ? (
        <>
          <PortfolioSummary data={data} />
          <PositionTable
            positions={data.positions}
            onTrade={(ticker, action) => openDrawer(ticker, action)}
          />
        </>
      ) : null}

      <TradeDrawer
        open={drawerOpen}
        defaultTicker={drawerTicker}
        defaultAction={drawerAction}
        onClose={() => setDrawerOpen(false)}
        onSubmit={handleTrade}
      />
    </div>
  );
}
