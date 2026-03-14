"""Tests for calculator tools."""

from moatlab.tools.calculator import (
    calculate_dcf,
    calculate_margin_of_safety,
    calculate_owner_earnings,
)


class TestCalculateDCF:
    def test_basic_dcf(self):
        result = calculate_dcf(
            free_cash_flows=[100, 110, 120],
            growth_rate=0.05,
            discount_rate=0.10,
            terminal_growth_rate=0.03,
            projection_years=10,
        )
        assert "intrinsic_value_total" in result
        assert result["intrinsic_value_total"] > 0
        assert result["base_fcf"] == 110.0  # average of 100, 110, 120

    def test_dcf_with_shares(self):
        result = calculate_dcf(
            free_cash_flows=[1_000_000],
            growth_rate=0.05,
            discount_rate=0.10,
            shares_outstanding=100_000,
        )
        assert "intrinsic_value_per_share" in result
        assert result["intrinsic_value_per_share"] > 0

    def test_dcf_negative_fcf(self):
        result = calculate_dcf(free_cash_flows=[-100, -200])
        assert "error" in result

    def test_dcf_empty_fcf(self):
        result = calculate_dcf(free_cash_flows=[])
        assert "error" in result


class TestOwnerEarnings:
    def test_basic(self):
        result = calculate_owner_earnings(
            net_income=1000,
            depreciation=200,
            capex=300,
        )
        # 1000 + 200 - 300 - 0 = 900
        assert result["owner_earnings"] == 900

    def test_with_working_capital(self):
        result = calculate_owner_earnings(
            net_income=1000,
            depreciation=200,
            capex=300,
            working_capital_change=50,
        )
        # 1000 + 200 - 300 - 50 = 850
        assert result["owner_earnings"] == 850


class TestMarginOfSafety:
    def test_sufficient_margin(self):
        result = calculate_margin_of_safety(current_price=70, intrinsic_value=100)
        assert result["margin_of_safety"] == 0.3
        assert "充足" in result["verdict"]

    def test_insufficient_margin(self):
        result = calculate_margin_of_safety(current_price=90, intrinsic_value=100)
        assert result["margin_of_safety"] == 0.1
        assert "不足" in result["verdict"]

    def test_overvalued(self):
        result = calculate_margin_of_safety(current_price=120, intrinsic_value=100)
        assert result["margin_of_safety"] < 0
        assert "不建议" in result["verdict"]

    def test_negative_intrinsic(self):
        result = calculate_margin_of_safety(current_price=50, intrinsic_value=-10)
        assert result["margin_of_safety"] is None
