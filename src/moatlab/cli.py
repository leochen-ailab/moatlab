import logging
from datetime import date
from enum import Enum

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

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


# ── Portfolio commands ──────────────────────────────────────────────────

portfolio_app = typer.Typer(help="Portfolio management — track holdings and P&L")
app.add_typer(portfolio_app, name="portfolio")


@portfolio_app.command("add")
def portfolio_add(
    ticker: str = typer.Argument(help="Stock ticker, e.g. AAPL"),
    shares: float = typer.Option(..., "--shares", "-n", help="Number of shares"),
    price: float = typer.Option(..., "--price", "-p", help="Purchase price per share (USD)"),
    trade_date: str = typer.Option(None, "--date", "-d", help="Trade date (YYYY-MM-DD), default today"),
    notes: str = typer.Option("", "--notes", help="Notes for this trade"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Record a stock purchase (buy/add shares)."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    from moatlab.tools.portfolio import add_position

    trade_date = trade_date or date.today().isoformat()
    result = add_position(ticker.upper(), shares, price, trade_date, notes)

    if result["status"] == "success":
        pos = result["position"]
        console.print(Panel(
            f"[green]✓ 买入成功[/green]\n"
            f"{pos['ticker']}  {shares} 股 @ ${price:.2f}\n"
            f"当前持仓: {pos['shares']} 股  均价: ${pos['avg_cost']:.2f}  总成本: ${pos['total_cost']:.2f}",
            style="green",
        ))
    else:
        console.print(f"[red]错误: {result}[/red]")


@portfolio_app.command("sell")
def portfolio_sell(
    ticker: str = typer.Argument(help="Stock ticker, e.g. AAPL"),
    shares: float = typer.Option(..., "--shares", "-n", help="Number of shares to sell"),
    price: float = typer.Option(..., "--price", "-p", help="Sale price per share (USD)"),
    trade_date: str = typer.Option(None, "--date", "-d", help="Trade date (YYYY-MM-DD), default today"),
    notes: str = typer.Option("", "--notes", help="Notes for this trade"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Record a stock sale (sell/reduce shares)."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    from moatlab.tools.portfolio import sell_position

    trade_date = trade_date or date.today().isoformat()
    result = sell_position(ticker.upper(), shares, price, trade_date, notes)

    if result["status"] == "success":
        console.print(Panel(
            f"[yellow]✓ 卖出成功[/yellow]\n"
            f"{ticker.upper()}  {shares} 股 @ ${price:.2f}",
            style="yellow",
        ))
    else:
        console.print(f"[red]错误: {result.get('message', result)}[/red]")


@portfolio_app.command("list")
def portfolio_list(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Show all current holdings with real-time P&L."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    from moatlab.tools.portfolio import get_portfolio

    console.print(Panel("[bold]MoatLab 持仓概览[/bold]", style="blue"))

    with console.status("[bold green]正在获取实时数据..."):
        data = get_portfolio()

    if not data["positions"]:
        console.print("[dim]暂无持仓[/dim]")
        return

    table = Table(title="当前持仓")
    table.add_column("股票", style="bold")
    table.add_column("股数", justify="right")
    table.add_column("均价", justify="right")
    table.add_column("现价", justify="right")
    table.add_column("市值", justify="right")
    table.add_column("盈亏", justify="right")
    table.add_column("盈亏%", justify="right")

    for pos in data["positions"]:
        pnl_style = "green" if pos["pnl"] >= 0 else "red"
        table.add_row(
            pos["ticker"],
            f"{pos['shares']:.0f}",
            f"${pos['avg_cost']:.2f}",
            f"${pos['current_price']:.2f}",
            f"${pos['market_value']:,.2f}",
            f"[{pnl_style}]${pos['pnl']:,.2f}[/{pnl_style}]",
            f"[{pnl_style}]{pos['pnl_pct']:+.1f}%[/{pnl_style}]",
        )

    console.print(table)
    console.print(
        f"\n总成本: ${data['total_cost']:,.2f}  "
        f"总市值: ${data['total_market_value']:,.2f}  "
        f"总回报: [{'green' if data['total_return'] >= 0 else 'red'}]"
        f"${data['total_return']:,.2f} ({data['total_return_pct']:+.1f}%)"
        f"[/{'green' if data['total_return'] >= 0 else 'red'}]"
    )


@portfolio_app.command("review")
def portfolio_review(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """AI-driven portfolio review — check if investment thesis still holds."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    from moatlab.agents.portfolio import PortfolioAgent

    console.print(Panel("[bold]MoatLab 持仓回顾[/bold]", style="blue"))
    console.print("\n[bold cyan]━━━ AI 持仓回顾 ━━━[/bold cyan]\n")

    with console.status("[bold green]正在分析持仓..."):
        agent = PortfolioAgent()
        result = agent.manage("请回顾我当前的持仓组合，检查每个持仓的投资逻辑是否仍然成立，给出整体评估和建议。")

    console.print(Markdown(result))


@portfolio_app.command("history")
def portfolio_history(
    ticker: str = typer.Option(None, "--ticker", "-t", help="Filter by ticker"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max records to show"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Show transaction history."""
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

    from moatlab.tools.portfolio import get_transaction_history

    data = get_transaction_history(ticker, limit)

    if not data["transactions"]:
        console.print("[dim]暂无交易记录[/dim]")
        return

    table = Table(title=f"交易记录{f' — {ticker.upper()}' if ticker else ''}")
    table.add_column("日期")
    table.add_column("操作")
    table.add_column("股票", style="bold")
    table.add_column("股数", justify="right")
    table.add_column("价格", justify="right")
    table.add_column("备注")

    for txn in data["transactions"]:
        action_style = "green" if txn["action"] == "buy" else "yellow"
        action_label = "买入" if txn["action"] == "buy" else "卖出"
        table.add_row(
            txn["date"],
            f"[{action_style}]{action_label}[/{action_style}]",
            txn["ticker"],
            f"{txn['shares']:.0f}",
            f"${txn['price']:.2f}",
            txn.get("notes", ""),
        )

    console.print(table)


@app.command(name="server")
def server(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Bind host"),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
):
    """Start the MoatLab Web API server."""
    import uvicorn

    console.print(Panel(
        f"[bold]MoatLab Web API[/bold]\n"
        f"http://{host}:{port}\n"
        f"Docs: http://{host}:{port}/docs",
        style="blue",
    ))
    uvicorn.run("moatlab.server:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
