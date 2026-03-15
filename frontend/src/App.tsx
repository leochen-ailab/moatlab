import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import PortfolioPage from "./pages/PortfolioPage";
import AnalysisPage from "./pages/AnalysisPage";
import ScreenerPage from "./pages/ScreenerPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/screener" element={<ScreenerPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
