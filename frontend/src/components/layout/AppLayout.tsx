import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "仪表盘" },
  { to: "/portfolio", label: "持仓" },
  { to: "/analysis", label: "分析" },
  { to: "/screener", label: "筛选" },
] as const;

export default function AppLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <nav className="sticky top-0 z-50 bg-gray-900/80 backdrop-blur border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-8">
          <span className="text-lg font-bold tracking-tight text-white">
            MoatLab
          </span>
          <div className="flex gap-1">
            {links.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded text-sm transition-colors ${
                    isActive
                      ? "bg-gray-700 text-white"
                      : "text-gray-400 hover:text-white hover:bg-gray-800"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
