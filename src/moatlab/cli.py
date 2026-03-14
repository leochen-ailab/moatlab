import typer

app = typer.Typer(
    name="moatlab",
    help="MoatLab — Personal value investing system (Buffett/Duan Yongping style)",
)


@app.command()
def analyze(
    ticker: str = typer.Argument(help="Stock ticker symbol, e.g. AAPL"),
):
    """Deep analysis of a stock using value investing principles."""
    typer.echo(f"[MoatLab] Analyzing {ticker}... (not yet implemented)")


@app.command()
def screen():
    """Screen stocks based on value investing criteria."""
    typer.echo("[MoatLab] Screening... (not yet implemented)")


if __name__ == "__main__":
    app()
