import { useScreenerStore } from "../../stores/screenerStore";
import { SECTOR_MAP, SECTORS_CN } from "../../constants/sectors";

export default function ScreenerForm() {
  const { criteria, setCriteria, screen, loading } = useScreenerStore();

  const hasCriteria =
    criteria.roe_min != null ||
    criteria.debt_to_equity_max != null ||
    criteria.gross_margin_min != null ||
    criteria.pe_max != null ||
    (criteria.sector && criteria.sector.length > 0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    screen();
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6">
      <h2 className="text-lg font-semibold mb-4">筛选条件</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-xs text-gray-500 mb-1">最低 ROE (%)</label>
          <input
            type="number"
            step="0.1"
            placeholder="如 15"
            value={criteria.roe_min ?? ""}
            onChange={(e) =>
              setCriteria({ roe_min: e.target.value ? Number(e.target.value) : undefined })
            }
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">最高负债率</label>
          <input
            type="number"
            step="0.01"
            placeholder="如 0.5"
            value={criteria.debt_to_equity_max ?? ""}
            onChange={(e) =>
              setCriteria({ debt_to_equity_max: e.target.value ? Number(e.target.value) : undefined })
            }
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">最低毛利率 (%)</label>
          <input
            type="number"
            step="0.1"
            placeholder="如 40"
            value={criteria.gross_margin_min ?? ""}
            onChange={(e) =>
              setCriteria({ gross_margin_min: e.target.value ? Number(e.target.value) : undefined })
            }
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">最高 PE</label>
          <input
            type="number"
            step="0.1"
            placeholder="如 25"
            value={criteria.pe_max ?? ""}
            onChange={(e) =>
              setCriteria({ pe_max: e.target.value ? Number(e.target.value) : undefined })
            }
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">行业</label>
          <select
            value={criteria.sector ?? ""}
            onChange={(e) =>
              setCriteria({ sector: e.target.value || undefined })
            }
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="">全部行业</option>
            {SECTORS_CN.map((cn) => (
              <option key={cn} value={SECTOR_MAP[cn]}>{cn}</option>
            ))}
          </select>
        </div>
      </div>
      <button
        type="submit"
        disabled={!hasCriteria || loading}
        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm rounded font-medium"
      >
        {loading ? "筛选中..." : "开始筛选"}
      </button>
    </form>
  );
}
