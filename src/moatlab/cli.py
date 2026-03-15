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
def screen():
    """Screen stocks based on value investing criteria."""
    console.print("[yellow]筛选功能即将实现。[/yellow]")


if __name__ == "__main__":
    app()
