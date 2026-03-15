from moatlab.channels.formatter import format_analysis, truncate


def test_truncate_long_text():
    long_text = "x" * 50
    out = truncate(long_text, max_chars=10)
    assert out.startswith("x" * 10)
    assert "已截断" in out


def test_format_analysis_contains_sections():
    text = format_analysis(
        "AAPL",
        {
            "decision": "持有",
            "moat": "强",
            "management": "优秀",
            "financial": "稳健",
            "valuation": "偏贵",
        },
        max_chars_per_section=20,
    )
    assert "📊 AAPL 价值投资分析" in text
    assert "━━ 投资决策 ━━" in text
    assert "━━ 护城河分析 ━━" in text
