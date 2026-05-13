"""
Unit tests for TaxCalculator tax rate threshold selection.

Tests focus on:
- Income threshold detection and correct rate selection
- Boundary conditions at threshold values
- Progressive tax rate application (US region)
- Flat rate consistency (EU, UA regions)
- Threshold edge cases (exact, just below, just above)
- Rate selection correctness across income ranges
"""

import pytest
from decimal import Decimal
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


class TestUSThresholdDetection:
    """Tests for US tax rate threshold detection."""

    def test_us_threshold_value_is_5000(self, tax_calculator):
        """Verify that US tax threshold is exactly $5000."""
        assert US_HIGH_TAX_THRESHOLD == Decimal("5000")

    def test_us_low_rate_below_threshold(self, tax_calculator):
        """Test US applies low rate (22%) for income below threshold."""
        income = Decimal("4999.99")

        result = tax_calculator.calculate(Region.US, income)
        expected = income * US_LOW_TAX

        assert result == expected

    def test_us_low_rate_at_threshold(self, tax_calculator):
        """Test US applies low rate (22%) at exactly threshold value."""
        income = Decimal("5000.00")

        result = tax_calculator.calculate(Region.US, income)
        expected = income * US_LOW_TAX

        assert result == expected

    def test_us_high_rate_above_threshold(self, tax_calculator):
        """Test US applies high rate (30%) for income above threshold."""
        income = Decimal("5000.01")

        result = tax_calculator.calculate(Region.US, income)
        expected = income * US_HIGH_TAX

        assert result == expected

    def test_us_threshold_boundary_test(self, tax_calculator):
        """Test the exact threshold boundary condition."""
        below = Decimal("4999.99")
        at = Decimal("5000.00")
        above = Decimal("5000.01")

        tax_below = tax_calculator.calculate(Region.US, below)
        tax_at = tax_calculator.calculate(Region.US, at)
        tax_above = tax_calculator.calculate(Region.US, above)

        # Below and at threshold use low rate
        assert tax_below == below * US_LOW_TAX
        assert tax_at == at * US_LOW_TAX

        # Above threshold uses high rate
        assert tax_above == above * US_HIGH_TAX

    def test_us_rate_changes_at_threshold_plus_one_cent(self, tax_calculator):
        """Test that rate changes exactly one cent above threshold."""
        at_threshold = Decimal("5000.00")
        one_cent_above = Decimal("5000.01")

        tax_at = tax_calculator.calculate(Region.US, at_threshold)
        tax_above = tax_calculator.calculate(Region.US, one_cent_above)

        # At threshold: 5000 * 0.22 = 1100
        assert tax_at == Decimal("1100.00")

        # One cent above: 5000.01 * 0.30 = 1500.003 -> 1500.00
        assert tax_above == Decimal("1500.00")


class TestUSProgressiveTaxRateSelection:
    """Tests for US progressive tax rate selection across income ranges."""

    def test_us_low_income_range_uses_low_rate(self, tax_calculator):
        """Test that all low incomes use 22% rate."""
        low_incomes = [
            Decimal("100.00"),
            Decimal("1000.00"),
            Decimal("2500.00"),
            Decimal("4500.00"),
            Decimal("4999.99"),
        ]

        for income in low_incomes:
            result = tax_calculator.calculate(Region.US, income)
            expected = income * US_LOW_TAX
            assert result == expected, f"Failed for income {income}"

    def test_us_high_income_range_uses_high_rate(self, tax_calculator):
        """Test that all high incomes use 30% rate."""
        high_incomes = [
            Decimal("5000.01"),
            Decimal("6000.00"),
            Decimal("10000.00"),
            Decimal("50000.00"),
            Decimal("100000.00"),
        ]

        for income in high_incomes:
            result = tax_calculator.calculate(Region.US, income)
            expected = income * US_HIGH_TAX
            assert result == expected, f"Failed for income {income}"

    def test_us_threshold_creates_discontinuity(self, tax_calculator):
        """Test that threshold creates a discontinuity in tax amount."""
        just_below = Decimal("4999.99")
        just_above = Decimal("5000.01")

        tax_below = tax_calculator.calculate(Region.US, just_below)
        tax_above = tax_calculator.calculate(Region.US, just_above)

        # Above should have significantly higher tax due to rate change
        assert tax_above > tax_below

    def test_us_low_rate_correctness_with_various_amounts(self, tax_calculator):
        """Verify 22% rate is correctly applied for low income."""
        test_cases = [
            (Decimal("1000.00"), Decimal("220.00")),
            (Decimal("2000.00"), Decimal("440.00")),
            (Decimal("5000.00"), Decimal("1100.00")),
        ]

        for income, expected_tax in test_cases:
            result = tax_calculator.calculate(Region.US, income)
            assert result == expected_tax

    def test_us_high_rate_correctness_with_various_amounts(self, tax_calculator):
        """Verify 30% rate is correctly applied for high income."""
        test_cases = [
            (Decimal("6000.00"), Decimal("1800.00")),
            (Decimal("10000.00"), Decimal("3000.00")),
            (Decimal("20000.00"), Decimal("6000.00")),
        ]

        for income, expected_tax in test_cases:
            result = tax_calculator.calculate(Region.US, income)
            assert result == expected_tax


class TestEUFlatRateSelection:
    """Tests for EU flat tax rate selection (no threshold effects)."""

    def test_eu_flat_rate_below_us_threshold(self, tax_calculator):
        """Test EU uses 25% rate below US threshold."""
        income = Decimal("3000.00")

        result = tax_calculator.calculate(Region.EU, income)
        expected = income * EU_TAX

        assert result == expected

    def test_eu_flat_rate_at_us_threshold(self, tax_calculator):
        """Test EU uses 25% rate at US threshold value."""
        income = Decimal("5000.00")

        result = tax_calculator.calculate(Region.EU, income)
        expected = income * EU_TAX

        assert result == expected

    def test_eu_flat_rate_above_us_threshold(self, tax_calculator):
        """Test EU uses 25% rate above US threshold."""
        income = Decimal("8000.00")

        result = tax_calculator.calculate(Region.EU, income)
        expected = income * EU_TAX

        assert result == expected

    def test_eu_no_threshold_effect(self, tax_calculator):
        """Test that EU ignores US threshold completely."""
        below_threshold = Decimal("4000.00")
        above_threshold = Decimal("6000.00")

        tax_below = tax_calculator.calculate(Region.EU, below_threshold)
        tax_above = tax_calculator.calculate(Region.EU, above_threshold)

        # Both should scale linearly with income
        assert tax_below == Decimal("1000.00")
        assert tax_above == Decimal("1500.00")

        # Ratio should be exactly the same as income ratio
        assert (tax_above / tax_below) == (above_threshold / below_threshold)


class TestUAFlatRateSelection:
    """Tests for UA flat tax rate selection (no threshold effects)."""

    def test_ua_flat_rate_below_us_threshold(self, tax_calculator):
        """Test UA uses 19.5% rate below US threshold."""
        income = Decimal("3000.00")

        result = tax_calculator.calculate(Region.UA, income)
        expected = income * UA_TAX

        assert result == expected

    def test_ua_flat_rate_at_us_threshold(self, tax_calculator):
        """Test UA uses 19.5% rate at US threshold value."""
        income = Decimal("5000.00")

        result = tax_calculator.calculate(Region.UA, income)
        expected = income * UA_TAX

        assert result == expected

    def test_ua_flat_rate_above_us_threshold(self, tax_calculator):
        """Test UA uses 19.5% rate above US threshold."""
        income = Decimal("8000.00")

        result = tax_calculator.calculate(Region.UA, income)
        expected = income * UA_TAX

        assert result == expected

    def test_ua_no_threshold_effect(self, tax_calculator):
        """Test that UA ignores US threshold completely."""
        below_threshold = Decimal("4000.00")
        above_threshold = Decimal("6000.00")

        tax_below = tax_calculator.calculate(Region.UA, below_threshold)
        tax_above = tax_calculator.calculate(Region.UA, above_threshold)

        # Both should scale linearly with income
        assert tax_below == Decimal("780.00")
        assert tax_above == Decimal("1170.00")

        # Ratio should be exactly the same as income ratio
        assert (tax_above / tax_below) == (above_threshold / below_threshold)


class TestThresholdRateConsistency:
    """Tests for consistent rate selection across multiple calls."""

    def test_us_threshold_consistent_across_calls(self, tax_calculator):
        """Test US threshold rate selection remains consistent."""
        below = Decimal("3000.00")
        above = Decimal("7000.00")

        # Multiple calls should always use same rate
        for _ in range(3):
            result_below = tax_calculator.calculate(Region.US, below)
            result_above = tax_calculator.calculate(Region.US, above)

            assert result_below == below * US_LOW_TAX
            assert result_above == above * US_HIGH_TAX

    def test_threshold_selection_independent_of_other_calls(self, tax_calculator):
        """Test that threshold selection doesn't depend on call order."""
        income_low = Decimal("3000.00")
        income_high = Decimal("7000.00")

        # Call in one order
        result1_low = tax_calculator.calculate(Region.US, income_low)
        result1_high = tax_calculator.calculate(Region.US, income_high)

        # Call in reverse order
        result2_high = tax_calculator.calculate(Region.US, income_high)
        result2_low = tax_calculator.calculate(Region.US, income_low)

        # Results should match regardless of call order
        assert result1_low == result2_low
        assert result1_high == result2_high


class TestThresholdEdgeCases:
    """Tests for edge cases around threshold values."""

    def test_threshold_with_very_small_amounts(self, tax_calculator):
        """Test threshold behavior with amounts just off threshold."""
        near_below = Decimal("4999.999")
        near_above = Decimal("5000.001")

        result_below = tax_calculator.calculate(Region.US, near_below)
        result_above = tax_calculator.calculate(Region.US, near_above)

        # Below uses low rate
        assert result_below == near_below * US_LOW_TAX
        # Above uses high rate
        assert result_above == near_above * US_HIGH_TAX

    def test_threshold_one_microsecond_below(self, tax_calculator):
        """Test threshold with amount just barely below."""
        income = Decimal("4999.9999999999")

        result = tax_calculator.calculate(Region.US, income)

        # Should use low rate
        assert result == income * US_LOW_TAX

    def test_threshold_one_microsecond_above(self, tax_calculator):
        """Test threshold with amount just barely above."""
        income = Decimal("5000.0000000001")

        result = tax_calculator.calculate(Region.US, income)

        # Should use high rate
        assert result == income * US_HIGH_TAX

    def test_threshold_exact_multiple(self, tax_calculator):
        """Test threshold with exact multiples of threshold value."""
        one_threshold = Decimal("5000.00")
        two_thresholds = Decimal("10000.00")

        result_one = tax_calculator.calculate(Region.US, one_threshold)
        result_two = tax_calculator.calculate(Region.US, two_thresholds)

        # One threshold uses low rate
        assert result_one == one_threshold * US_LOW_TAX
        # Two thresholds (above threshold) uses high rate
        assert result_two == two_thresholds * US_HIGH_TAX


class TestThresholdComparisonAcrossRegions:
    """Tests comparing threshold behavior across different regions."""

    def test_regions_use_different_thresholds(self, tax_calculator):
        """Test that only US has threshold, EU and UA don't."""
        income = Decimal("5000.00")

        tax_us_at = tax_calculator.calculate(Region.US, income)
        tax_eu_at = tax_calculator.calculate(Region.EU, income)
        tax_ua_at = tax_calculator.calculate(Region.UA, income)

        # US at threshold: 5000 * 0.22 = 1100
        assert tax_us_at == Decimal("1100.00")
        # EU at same income: 5000 * 0.25 = 1250
        assert tax_eu_at == Decimal("1250.00")
        # UA at same income: 5000 * 0.195 = 975
        assert tax_ua_at == Decimal("975.00")

    def test_us_threshold_doesnt_affect_eu_or_ua(self, tax_calculator):
        """Test that crossing US threshold doesn't affect EU/UA calculations."""
        just_below = Decimal("4999.99")
        just_above = Decimal("5000.01")

        # EU should have proportional increase
        eu_below = tax_calculator.calculate(Region.EU, just_below)
        eu_above = tax_calculator.calculate(Region.EU, just_above)

        # Difference should be proportional to income difference
        income_diff = just_above - just_below
        expected_tax_diff = income_diff * EU_TAX
        actual_tax_diff = eu_above - eu_below

        assert actual_tax_diff == expected_tax_diff


class TestThresholdRatePrecedence:
    """Tests to verify income level takes precedence in rate selection."""

    def test_rate_selected_based_on_income_not_other_factors(self, tax_calculator):
        """Test that rate is selected purely based on income."""
        low_income = Decimal("2000.00")
        high_income = Decimal("8000.00")

        # Same region, different incomes should give different rates
        tax_low = tax_calculator.calculate(Region.US, low_income)
        tax_high = tax_calculator.calculate(Region.US, high_income)

        # Calculate what rates were used
        rate_used_low = tax_low / low_income
        rate_used_high = tax_high / high_income

        # Verify correct rates were used
        assert rate_used_low == US_LOW_TAX
        assert rate_used_high == US_HIGH_TAX

    def test_threshold_applies_consistently_same_region(self, tax_calculator):
        """Test that threshold applies consistently within same region."""
        test_pairs = [
            (Decimal("1000.00"), Decimal("2000.00")),
            (Decimal("4000.00"), Decimal("4500.00")),
            (Decimal("4900.00"), Decimal("5100.00")),
        ]

        for low_income, high_income in test_pairs:
            result_low = tax_calculator.calculate(Region.US, low_income)
            result_high = tax_calculator.calculate(Region.US, high_income)

            if low_income < US_HIGH_TAX_THRESHOLD:
                assert result_low == low_income * US_LOW_TAX

            if high_income > US_HIGH_TAX_THRESHOLD:
                assert result_high == high_income * US_HIGH_TAX


class TestThresholdCorrectnessVerification:
    """Tests to verify threshold logic correctness."""

    def test_threshold_comparison_operator_correct(self, tax_calculator):
        """Verify that threshold uses greater-than, not greater-than-or-equal."""
        at_threshold = US_HIGH_TAX_THRESHOLD

        result = tax_calculator.calculate(Region.US, at_threshold)

        # At threshold should use low rate (not greater than)
        assert result == at_threshold * US_LOW_TAX

    def test_threshold_single_cent_behavior(self, tax_calculator):
        """Test single cent changes across threshold."""
        changes = [
            (Decimal("4999.99"), Decimal("5000.00")),
            (Decimal("5000.00"), Decimal("5000.01")),
        ]

        for income1, income2 in changes:
            tax1 = tax_calculator.calculate(Region.US, income1)
            tax2 = tax_calculator.calculate(Region.US, income2)

            # First pair should both use low rate
            if income1 <= Decimal("5000.00") and income2 <= Decimal("5000.00"):
                assert tax1 == income1 * US_LOW_TAX
                assert tax2 == income2 * US_LOW_TAX
            # Second pair should transition to high rate
            elif income2 > Decimal("5000.00"):
                assert tax2 == income2 * US_HIGH_TAX


class TestThresholdRealWorldScenarios:
    """Tests for real-world threshold scenarios."""

    def test_monthly_salary_just_below_threshold(self, tax_calculator):
        """Test monthly salary just below US threshold."""
        monthly_salary = Decimal("4999.00")

        result = tax_calculator.calculate(Region.US, monthly_salary)

        # Should use low rate
        assert result == Decimal("1099.78")

    def test_monthly_salary_just_above_threshold(self, tax_calculator):
        """Test monthly salary just above US threshold."""
        monthly_salary = Decimal("5001.00")

        result = tax_calculator.calculate(Region.US, monthly_salary)

        # Should use high rate
        assert result == Decimal("1500.30")

    def test_quarterly_bonus_threshold_impact(self, tax_calculator):
        """Test quarterly bonus crossing threshold."""
        quarterly_income = Decimal("4000.00")

        result_low = tax_calculator.calculate(Region.US, quarterly_income)

        # Adding to cross threshold
        quarterly_income_with_bonus = Decimal("6000.00")
        result_high = tax_calculator.calculate(Region.US, quarterly_income_with_bonus)

        assert result_low == Decimal("880.00")
        assert result_high == Decimal("1800.00")

    def test_combined_income_analysis(self, tax_calculator):
        """Test threshold effect on combined income."""
        salary = Decimal("4000.00")
        bonus = Decimal("1500.00")
        total = salary + bonus

        # Calculate separately (demonstrates threshold importance)
        tax_salary = tax_calculator.calculate(Region.US, salary)
        tax_combined = tax_calculator.calculate(Region.US, total)

        # Tax on salary: 4000 * 0.22 = 880
        assert tax_salary == Decimal("880.00")
        # Tax on combined: 5500 * 0.30 = 1650
        assert tax_combined == Decimal("1650.00")
