import logging
from enum import Enum

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

app = typer.Typer(
    name="moatlab",
    help="MoatLab — Personal value investing system (Buffett/Duan Yongping style)",
)


class AnalysisMode(str, Enum):
    full = "full"
    financial = "financial"
    valuation = "valuation"
    moat = "moat"
    management = "management"


@app.command()
def analyze(
    ticker: str = typer.Argument(help="Stock ticker symbol, e.g. AAPL"),
    mode: AnalysisMode = typer.Option(
        AnalysisMode.full, "--mode", "-m", help="Analysis mode"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show debug logs"),
):
    """Deep analysis of a stock using value investing principles."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    ticker = ticker.upper()
    console.print(
        Panel(f"[bold]MoatLab 价值投资分析[/bold]\n股票: {ticker}  模式: {mode.value}",
              style="blue")
    )

    if mode == AnalysisMode.full:
        _run_full(ticker)
    elif mode == AnalysisMode.financial:
        _run_single("财务分析", "正在分析财务数据...", _get_financial, ticker)
    elif mode == AnalysisMode.valuation:
        _run_single("估值分析", "正在计算内在价值...", _get_valuation, ticker)
    elif mode == AnalysisMode.moat:
        _run_single("护城河分析", "正在分析竞争优势...", _get_moat, ticker)
    elif mode == AnalysisMode.management:
        _run_single("管理层分析", "正在评估管理层...", _get_management, ticker)


def _run_single(title: str, status_msg: str, agent_fn, ticker: str):
    """Run a single agent analysis."""
    console.print(f"\n[bold cyan]━━━ {title} ━━━[/bold cyan]\n")
    with console.status(f"[bold green]{status_msg}"):
        result = agent_fn(ticker)
    console.print(Markdown(result))


def _run_full(ticker: str):
    """Run full analysis pipeline via Orchestrator."""
    from moatlab.agents.orchestrator import Orchestrator

    section_titles = {
        "moat": "护城河分析",
        "management": "管理层分析",
        "financial": "财务分析",
        "valuation": "估值分析",
        "decision": "投资决策",
    }

    def on_progress(agent_name: str, status: str):
        console.print(f"  [dim]{agent_name}: {status}[/dim]")

    console.print("\n[bold cyan]━━━ 全链路价值投资分析 ━━━[/bold cyan]\n")
    with console.status("[bold green]正在执行完整分析流程..."):
        orchestrator = Orchestrator()
        reports = orchestrator.analyze(ticker, on_progress=on_progress)

    for key in ["moat", "management", "financial", "valuation", "decision"]:
        title = section_titles.get(key, key)
        console.print(f"\n[bold cyan]━━━ {title} ━━━[/bold cyan]\n")
        console.print(Markdown(reports.get(key, "无数据")))


def _get_financial(ticker: str) -> str:
    from moatlab.agents.financial import FinancialAgent
    return FinancialAgent().analyze(ticker)


def _get_valuation(ticker: str) -> str:
    from moatlab.agents.valuation import ValuationAgent
    return ValuationAgent().analyze(ticker)


def _get_moat(ticker: str) -> str:
    from moatlab.agents.moat import MoatAgent
    return MoatAgent().analyze(ticker)


def _get_management(ticker: str) -> str:
    from moatlab.agents.management import ManagementAgent
    return ManagementAgent().analyze(ticker)


@app.command()
def screen(
    roe_min: float = typer.Option(None, "--roe-min", help="Minimum ROE (decimal), e.g. 0.15"),
    debt_max: float = typer.Option(None, "--debt-max", help="Maximum debt/equity ratio"),
    margin_min: float = typer.Option(None, "--margin-min", help="Minimum gross margin (decimal)"),
    pe_max: float = typer.Option(None, "--pe-max", help="Maximum PE ratio"),
    sector: str = typer.Option(None, "--sector", "-s", help="Filter by sector"),
    criteria: str = typer.Option(None, "--criteria", "-c", help="Natural language criteria"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show debug logs"),
):
    """Screen stocks based on value investing criteria."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    console.print(Panel("[bold]MoatLab 价值投资筛选[/bold]", style="blue"))

    # Build criteria string from options
    parts = []
    if roe_min is not None:
        parts.append(f"ROE ≥ {roe_min*100:.0f}%")
    if debt_max is not None:
        parts.append(f"负债率 ≤ {debt_max}")
    if margin_min is not None:
        parts.append(f"毛利率 ≥ {margin_min*100:.0f}%")
    if pe_max is not None:
        parts.append(f"PE ≤ {pe_max}")
    if sector:
        parts.append(f"行业: {sector}")
    if criteria:
        parts.append(criteria)

    criteria_str = "、".join(parts) if parts else None

    from moatlab.agents.screener import ScreenerAgent

    console.print("\n[bold cyan]━━━ 股票筛选 ━━━[/bold cyan]\n")
    with console.status("[bold green]正在筛选股票..."):
        agent = ScreenerAgent()
        result = agent.screen(criteria_str)
    console.print(Markdown(result))


if __name__ == "__main__":
    app()
