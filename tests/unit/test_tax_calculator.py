"""
Unit tests for TaxCalculator.calculate() method.

Tests cover:
- US region tax calculation (progressive: 22% under $5000, 30% above)
- EU region tax calculation (flat 25%)
- UA (Ukraine) region tax calculation (flat 19.5%)
- Default tax rate (20%)
- Various income levels and edge cases
- Decimal precision and rounding
- Tax rate threshold behavior
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock
from src.payroll import TaxCalculator
from src.constants import (
    US_LOW_TAX,
    US_HIGH_TAX,
    EU_TAX,
    UA_TAX,
    DEFAULT_TAX,
    US_HIGH_TAX_THRESHOLD,
)


# Mock enums for testing
class Region:
    """Mock Region enum."""
    US = "US"
    EU = "EU"
    UA = "UA"


@pytest.fixture
def tax_calculator():
    """Fixture providing an instance of TaxCalculator."""
    return TaxCalculator()


class TestUSRegionTaxCalculation:
    """Tests for US region tax calculation with progressive tax rates."""

    def test_calculate_us_tax_below_threshold(self, tax_calculator):
        """Test US tax calculation below $5000 threshold (22% rate)."""
        income = Decimal("3000.00")

        result = tax_calculator.calculate(Region.US, income)

        expected = income * US_LOW_TAX
        assert result == expected

    def test_calculate_us_tax_at_threshold(self, tax_calculator):
        """Test US tax calculation at exactly $5000 threshold."""
        income = Decimal("5000.00")

        result = tax_calculator.calculate(Region.US, income)

        # At threshold, uses low rate (22%)
        expected = income * US_LOW_TAX
        assert result == expected

    def test_calculate_us_tax_just_above_threshold(self, tax_calculator):
        """Test US tax calculation just above $5000 threshold."""
        income = Decimal("5000.01")

        result = tax_calculator.calculate(Region.US, income)

        # Above threshold, uses high rate (30%)
        expected = income * US_HIGH_TAX
        assert result == expected

    def test_calculate_us_tax_above_threshold(self, tax_calculator):
        """Test US tax calculation well above $5000 threshold (30% rate)."""
        income = Decimal("8000.00")

        result = tax_calculator.calculate(Region.US, income)

        expected = income * US_HIGH_TAX
        assert result == expected

    def test_calculate_us_tax_with_low_income(self, tax_calculator):
        """Test US tax calculation with minimal income."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.US, income)

        expected = income * US_LOW_TAX
        assert result == expected

    def test_calculate_us_tax_with_high_income(self, tax_calculator):
        """Test US tax calculation with high income."""
        income = Decimal("50000.00")

        result = tax_calculator.calculate(Region.US, income)

        expected = income * US_HIGH_TAX
        assert result == expected

    def test_calculate_us_tax_low_rate_correctness(self, tax_calculator):
        """Verify US low tax rate is 22%."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.US, income)

        assert result == Decimal("220.00")

    def test_calculate_us_tax_high_rate_correctness(self, tax_calculator):
        """Verify US high tax rate is 30%."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.US, income)

        # Just use low income to verify rate, then test with high
        high_income = Decimal("10000.00")
        result_high = tax_calculator.calculate(Region.US, high_income)
        assert result_high == Decimal("3000.00")

    def test_calculate_us_tax_threshold_exact_value(self, tax_calculator):
        """Test US tax threshold is exactly $5000."""
        below_threshold = Decimal("4999.99")
        at_threshold = Decimal("5000.00")
        above_threshold = Decimal("5000.01")

        result_below = tax_calculator.calculate(Region.US, below_threshold)
        result_at = tax_calculator.calculate(Region.US, at_threshold)
        result_above = tax_calculator.calculate(Region.US, above_threshold)

        # Below and at threshold use low rate
        assert result_below == below_threshold * US_LOW_TAX
        assert result_at == at_threshold * US_LOW_TAX
        # Above threshold uses high rate
        assert result_above == above_threshold * US_HIGH_TAX


class TestEURegionTaxCalculation:
    """Tests for EU region tax calculation with flat 25% rate."""

    def test_calculate_eu_tax_standard_income(self, tax_calculator):
        """Test EU tax calculation with standard income."""
        income = Decimal("4000.00")

        result = tax_calculator.calculate(Region.EU, income)

        expected = income * EU_TAX
        assert result == expected

    def test_calculate_eu_tax_low_income(self, tax_calculator):
        """Test EU tax calculation with low income."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.EU, income)

        assert result == Decimal("250.00")

    def test_calculate_eu_tax_high_income(self, tax_calculator):
        """Test EU tax calculation with high income."""
        income = Decimal("10000.00")

        result = tax_calculator.calculate(Region.EU, income)

        assert result == Decimal("2500.00")

    def test_calculate_eu_tax_rate_is_flat(self, tax_calculator):
        """Test that EU tax rate is flat regardless of income level."""
        low_income = Decimal("2000.00")
        medium_income = Decimal("5000.00")
        high_income = Decimal("20000.00")

        result_low = tax_calculator.calculate(Region.EU, low_income)
        result_medium = tax_calculator.calculate(Region.EU, medium_income)
        result_high = tax_calculator.calculate(Region.EU, high_income)

        # All should use 25% rate
        assert result_low == Decimal("500.00")
        assert result_medium == Decimal("1250.00")
        assert result_high == Decimal("5000.00")

    def test_calculate_eu_tax_no_threshold_effect(self, tax_calculator):
        """Test that EU tax ignores US threshold."""
        income_below_us_threshold = Decimal("3000.00")
        income_above_us_threshold = Decimal("10000.00")

        result_below = tax_calculator.calculate(Region.EU, income_below_us_threshold)
        result_above = tax_calculator.calculate(Region.EU, income_above_us_threshold)

        # Both should use same 25% rate
        assert result_below == Decimal("750.00")
        assert result_above == Decimal("2500.00")

    def test_calculate_eu_tax_rate_correctness(self, tax_calculator):
        """Verify EU tax rate is exactly 25%."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.EU, income)

        assert result == Decimal("250.00")


class TestUARegionTaxCalculation:
    """Tests for UA (Ukraine) region tax calculation with flat 19.5% rate."""

    def test_calculate_ua_tax_standard_income(self, tax_calculator):
        """Test UA tax calculation with standard income."""
        income = Decimal("4000.00")

        result = tax_calculator.calculate(Region.UA, income)

        expected = income * UA_TAX
        assert result == expected

    def test_calculate_ua_tax_low_income(self, tax_calculator):
        """Test UA tax calculation with low income."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.UA, income)

        assert result == Decimal("195.00")

    def test_calculate_ua_tax_high_income(self, tax_calculator):
        """Test UA tax calculation with high income."""
        income = Decimal("10000.00")

        result = tax_calculator.calculate(Region.UA, income)

        assert result == Decimal("1950.00")

    def test_calculate_ua_tax_rate_is_flat(self, tax_calculator):
        """Test that UA tax rate is flat regardless of income level."""
        low_income = Decimal("2000.00")
        medium_income = Decimal("5000.00")
        high_income = Decimal("20000.00")

        result_low = tax_calculator.calculate(Region.UA, low_income)
        result_medium = tax_calculator.calculate(Region.UA, medium_income)
        result_high = tax_calculator.calculate(Region.UA, high_income)

        # All should use 19.5% rate
        assert result_low == Decimal("390.00")
        assert result_medium == Decimal("975.00")
        assert result_high == Decimal("3900.00")

    def test_calculate_ua_tax_no_threshold_effect(self, tax_calculator):
        """Test that UA tax ignores US threshold."""
        income_below_us_threshold = Decimal("3000.00")
        income_above_us_threshold = Decimal("10000.00")

        result_below = tax_calculator.calculate(Region.UA, income_below_us_threshold)
        result_above = tax_calculator.calculate(Region.UA, income_above_us_threshold)

        # Both should use same 19.5% rate
        assert result_below == Decimal("585.00")
        assert result_above == Decimal("1950.00")

    def test_calculate_ua_tax_rate_correctness(self, tax_calculator):
        """Verify UA tax rate is exactly 19.5%."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.UA, income)

        assert result == Decimal("195.00")


class TestDefaultTaxCalculation:
    """Tests for default tax rate (20%) for unknown regions."""

    def test_calculate_default_tax_unknown_region(self, tax_calculator):
        """Test default tax calculation for unknown region."""
        income = Decimal("1000.00")

        # Create a mock unknown region
        unknown_region = "UNKNOWN"
        result = tax_calculator.calculate(unknown_region, income)

        expected = income * DEFAULT_TAX
        assert result == expected

    def test_calculate_default_tax_rate_is_20_percent(self, tax_calculator):
        """Verify default tax rate is 20%."""
        income = Decimal("1000.00")
        unknown_region = "UNKNOWN"

        result = tax_calculator.calculate(unknown_region, income)

        assert result == Decimal("200.00")


class TestDecimalPrecisionAndRounding:
    """Tests for decimal precision and rounding in tax calculations."""

    def test_calculate_tax_with_precise_decimals(self, tax_calculator):
        """Test tax calculation with precise decimal values."""
        income = Decimal("1234.56")

        result = tax_calculator.calculate(Region.US, income)

        expected = (income * US_LOW_TAX).quantize(Decimal("0.01"))
        assert result == expected

    def test_calculate_tax_rounds_to_cents(self, tax_calculator):
        """Test that tax is rounded to nearest cent."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.EU, income)

        # 1000 * 0.25 = 250.00 (exact, no rounding needed)
        assert result == Decimal("250.00")

    def test_calculate_tax_with_rounding_up(self, tax_calculator):
        """Test tax calculation that requires rounding up."""
        income = Decimal("333.33")

        result = tax_calculator.calculate(Region.EU, income)

        # 333.33 * 0.25 = 83.3325 -> should round to 83.33
        assert result == Decimal("83.33")

    def test_calculate_tax_with_three_decimal_places(self, tax_calculator):
        """Test tax calculation with three decimal places in income."""
        income = Decimal("1000.555")

        result = tax_calculator.calculate(Region.UA, income)

        # Should round to two decimal places
        expected = (income * UA_TAX).quantize(Decimal("0.01"))
        assert result == expected

    def test_calculate_tax_fractional_results(self, tax_calculator):
        """Test tax calculation producing fractional cent results."""
        income = Decimal("1000.00")

        # EU: 1000 * 0.25 = 250.00
        result_eu = tax_calculator.calculate(Region.EU, income)
        assert result_eu == Decimal("250.00")

        # UA: 1000 * 0.195 = 195.00
        result_ua = tax_calculator.calculate(Region.UA, income)
        assert result_ua == Decimal("195.00")


class TestTaxCalculationEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_calculate_tax_with_zero_income(self, tax_calculator):
        """Test tax calculation with zero income."""
        income = Decimal("0.00")

        result_us = tax_calculator.calculate(Region.US, income)
        result_eu = tax_calculator.calculate(Region.EU, income)
        result_ua = tax_calculator.calculate(Region.UA, income)

        assert result_us == Decimal("0.00")
        assert result_eu == Decimal("0.00")
        assert result_ua == Decimal("0.00")

    def test_calculate_tax_with_very_small_income(self, tax_calculator):
        """Test tax calculation with very small income."""
        income = Decimal("0.01")

        result_eu = tax_calculator.calculate(Region.EU, income)

        # 0.01 * 0.25 = 0.0025 -> rounds to 0.00
        assert result_eu == Decimal("0.00")

    def test_calculate_tax_with_very_large_income(self, tax_calculator):
        """Test tax calculation with very large income."""
        income = Decimal("999999.99")

        result_us = tax_calculator.calculate(Region.US, income)
        result_eu = tax_calculator.calculate(Region.EU, income)
        result_ua = tax_calculator.calculate(Region.UA, income)

        expected_us = income * US_HIGH_TAX
        expected_eu = income * EU_TAX
        expected_ua = income * UA_TAX

        assert result_us == expected_us
        assert result_eu == expected_eu
        assert result_ua == expected_ua

    def test_calculate_tax_with_one_cent_income(self, tax_calculator):
        """Test tax calculation with one cent income."""
        income = Decimal("0.01")

        result_us = tax_calculator.calculate(Region.US, income)

        # 0.01 * 0.22 = 0.0022 -> rounds to 0.00
        assert result_us == Decimal("0.00")

    def test_calculate_tax_with_negative_income(self, tax_calculator):
        """Test tax calculation with negative income (refund scenario)."""
        income = Decimal("-1000.00")

        result_us = tax_calculator.calculate(Region.US, income)
        result_eu = tax_calculator.calculate(Region.EU, income)

        expected_us = income * US_LOW_TAX  # Negative is below threshold
        expected_eu = income * EU_TAX

        assert result_us == expected_us
        assert result_eu == expected_eu


class TestRegionComparison:
    """Tests comparing tax calculations across regions."""

    def test_compare_tax_rates_same_income(self, tax_calculator):
        """Compare tax amounts across regions for same income."""
        income = Decimal("1000.00")

        tax_us = tax_calculator.calculate(Region.US, income)
        tax_eu = tax_calculator.calculate(Region.EU, income)
        tax_ua = tax_calculator.calculate(Region.UA, income)

        # US low rate: 22%
        assert tax_us == Decimal("220.00")
        # EU rate: 25%
        assert tax_eu == Decimal("250.00")
        # UA rate: 19.5%
        assert tax_ua == Decimal("195.00")

        # EU should be highest, UA lowest at this income level
        assert tax_eu > tax_us > tax_ua

    def test_compare_tax_rates_high_income(self, tax_calculator):
        """Compare tax amounts at high income level (US threshold crossed)."""
        income = Decimal("10000.00")

        tax_us = tax_calculator.calculate(Region.US, income)
        tax_eu = tax_calculator.calculate(Region.EU, income)
        tax_ua = tax_calculator.calculate(Region.UA, income)

        # US high rate: 30%
        assert tax_us == Decimal("3000.00")
        # EU rate: 25%
        assert tax_eu == Decimal("2500.00")
        # UA rate: 19.5%
        assert tax_ua == Decimal("1950.00")

        # At high income, US is highest
        assert tax_us > tax_eu > tax_ua

    def test_tax_independence_between_regions(self, tax_calculator):
        """Test that calculations for different regions are independent."""
        income = Decimal("5000.00")

        result_us = tax_calculator.calculate(Region.US, income)
        result_eu = tax_calculator.calculate(Region.EU, income)

        # Change first result shouldn't affect second
        assert result_us == Decimal("1100.00")
        assert result_eu == Decimal("1250.00")


class TestTaxReturnTypeAndConsistency:
    """Tests for return type and consistency of tax calculations."""

    def test_calculate_tax_returns_decimal_type(self, tax_calculator):
        """Test that calculate() returns a Decimal type."""
        income = Decimal("1000.00")

        result = tax_calculator.calculate(Region.US, income)

        assert isinstance(result, Decimal)

    def test_calculate_tax_deterministic_results(self, tax_calculator):
        """Test that identical inputs always produce identical outputs."""
        income = Decimal("5000.00")

        results = [tax_calculator.calculate(Region.EU, income) for _ in range(5)]

        # All results should be identical
        assert all(r == Decimal("1250.00") for r in results)

    def test_calculate_tax_multiple_calls_same_result(self, tax_calculator):
        """Test that multiple calls return consistent results."""
        income = Decimal("3500.00")

        result1 = tax_calculator.calculate(Region.UA, income)
        result2 = tax_calculator.calculate(Region.UA, income)
        result3 = tax_calculator.calculate(Region.UA, income)

        assert result1 == result2 == result3


class TestComplexTaxScenarios:
    """Tests for complex real-world tax scenarios."""

    def test_calculate_tax_for_salary_employee_us_low(self, tax_calculator):
        """Test tax for typical salary employee in US earning below threshold."""
        monthly_salary = Decimal("3500.00")

        result = tax_calculator.calculate(Region.US, monthly_salary)

        assert result == Decimal("770.00")

    def test_calculate_tax_for_salary_employee_us_high(self, tax_calculator):
        """Test tax for executive salary employee in US earning above threshold."""
        monthly_salary = Decimal("8000.00")

        result = tax_calculator.calculate(Region.US, monthly_salary)

        assert result == Decimal("2400.00")

    def test_calculate_tax_for_contractor_eu(self, tax_calculator):
        """Test tax for contractor in EU."""
        contract_amount = Decimal("6000.00")

        result = tax_calculator.calculate(Region.EU, contract_amount)

        assert result == Decimal("1500.00")

    def test_calculate_tax_for_freelancer_ua(self, tax_calculator):
        """Test tax for freelancer in Ukraine."""
        freelance_income = Decimal("2500.00")

        result = tax_calculator.calculate(Region.UA, freelance_income)

        assert result == Decimal("487.50")

    def test_calculate_quarterly_tax_us(self, tax_calculator):
        """Test quarterly tax calculation for US employee."""
        quarterly_income = Decimal("12000.00")

        result = tax_calculator.calculate(Region.US, quarterly_income)

        # Above threshold, uses 30%
        assert result == Decimal("3600.00")

    def test_calculate_annual_tax_comparison(self, tax_calculator):
        """Test annual tax across regions for comparison."""
        annual_income = Decimal("48000.00")

        tax_us = tax_calculator.calculate(Region.US, annual_income)
        tax_eu = tax_calculator.calculate(Region.EU, annual_income)
        tax_ua = tax_calculator.calculate(Region.UA, annual_income)

        # US (above threshold): 48000 * 0.30 = 14400
        assert tax_us == Decimal("14400.00")
        # EU: 48000 * 0.25 = 12000
        assert tax_eu == Decimal("12000.00")
        # UA: 48000 * 0.195 = 9360
        assert tax_ua == Decimal("9360.00")
