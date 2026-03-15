import { useEffect, useState } from "react";
import { usePortfolioStore } from "../stores/portfolioStore";
import PortfolioSummary from "../components/portfolio/PortfolioSummary";
import AllocationChart from "../components/portfolio/AllocationChart";
import TopMovers from "../components/dashboard/TopMovers";
import QuickActions from "../components/dashboard/QuickActions";
import TradeDrawer from "../components/portfolio/TradeDrawer";
import Spinner from "../components/common/Spinner";
import { showToast } from "../components/common/Toast";

export default function DashboardPage() {
  const { data, performance, loading, error, fetchPortfolio, fetchPerformance, buy, sell } =
    usePortfolioStore();

  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    fetchPortfolio();
    fetchPerformance();
  }, [fetchPortfolio, fetchPerformance]);

  const handleTrade = async (req: Parameters<typeof buy>[0], action: "buy" | "sell") => {
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
      <h1 className="text-2xl font-bold mb-6">仪表盘</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading && !data ? (
        <Spinner text="正在加载仪表盘..." />
      ) : (
        <div className="space-y-6">
          {data && <PortfolioSummary data={data} />}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {data && <AllocationChart positions={data.positions} />}
            {performance && <TopMovers performance={performance} />}
          </div>

          <QuickActions onOpenTrade={() => setDrawerOpen(true)} />
        </div>
      )}

      <TradeDrawer
        open={drawerOpen}
        defaultTicker=""
        defaultAction="buy"
        onClose={() => setDrawerOpen(false)}
        onSubmit={(req, action) => handleTrade(req, action)}
      />
    </div>
  );
}
