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

    if mode in (AnalysisMode.full, AnalysisMode.financial):
        _run_financial(ticker)

    if mode in (AnalysisMode.full, AnalysisMode.valuation):
        _run_valuation(ticker)


def _run_financial(ticker: str):
    """Run financial analysis agent."""
    from moatlab.agents.financial import FinancialAgent

    console.print("\n[bold cyan]━━━ 财务分析 ━━━[/bold cyan]\n")
    with console.status("[bold green]正在分析财务数据..."):
        agent = FinancialAgent()
        result = agent.analyze(ticker)
    console.print(Markdown(result))


def _run_valuation(ticker: str):
    """Run valuation analysis agent."""
    from moatlab.agents.valuation import ValuationAgent

    console.print("\n[bold cyan]━━━ 估值分析 ━━━[/bold cyan]\n")
    with console.status("[bold green]正在计算内在价值..."):
        agent = ValuationAgent()
        result = agent.analyze(ticker)
    console.print(Markdown(result))


@app.command()
def screen():
    """Screen stocks based on value investing criteria."""
    console.print("[yellow]筛选功能将在 Phase 2 实现。[/yellow]")


if __name__ == "__main__":
    app()
