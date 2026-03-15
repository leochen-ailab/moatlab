from moatlab.channels.commands import parse_command


def test_parse_help_command():
    assert parse_command("帮助").type == "help"
    assert parse_command("help").type == "help"


def test_parse_analyze_command_uppercase_ticker():
    command = parse_command("analyze aapl")
    assert command.type == "analyze"
    assert command.ticker == "AAPL"


def test_parse_analyze_command_without_space():
    command = parse_command("分析AAPL")
    assert command.type == "analyze"
    assert command.ticker == "AAPL"


def test_parse_ticker_only_command():
    command = parse_command("msft")
    assert command.type == "analyze"
    assert command.ticker == "MSFT"


def test_parse_unknown_command():
    command = parse_command("hello world")
    assert command.type == "unknown"
