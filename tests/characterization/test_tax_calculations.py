"""
Comprehensive characterization tests for tax calculation behavior.

These tests document the current behavior of TaxCalculator for all regions:
- US: Dynamic rate (22% ≤$5000, 30% >$5000)
- EU: Fixed 25% rate
- UA: Fixed 19.5% rate
- Default: 20% rate

Tests cover edge cases, bracket thresholds, decimal precision, and integration
with the payroll system. No business logic changes are made; these tests verify
existing output exactly as implemented.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from payroll_calc import (
    TaxCalculator,
    Region,
    Employee,
    EmployeeType,
    PayrollService,
    BonusCalculator,
    Money,
)


# ======================================================
# BASIC TAX CALCULATION TESTS
# ======================================================

class TestTaxCalculatorBasic:
    """Test basic tax calculation functionality."""

    @pytest.fixture
    def tax_calculator(self):
        """Provide a fresh TaxCalculator instance."""
        return TaxCalculator()

    def test_tax_calculation_basic(self, tax_calculator):
        """Verify basic tax calculation formula: income × tax_rate."""
        income = Decimal("1000")
        region = Region.EU  # Fixed 25% for simplicity

        taxes = tax_calculator.calculate(region, income)

        # Expected: 1000 × 0.25 = 250.00
        expected = Decimal("250.00")
        assert taxes == expected

    def test_tax_calculation_returns_decimal(self, tax_calculator):
        """Verify tax calculation returns Decimal type."""
        income = Decimal("5000")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        assert isinstance(taxes, Decimal)

    def test_tax_calculation_zero_income(self, tax_calculator):
        """Verify tax calculation with zero income."""
        income = Decimal("0")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 0 × 0.25 = 0.00
        assert taxes == Decimal("0.00")

    def test_tax_calculation_large_income(self, tax_calculator):
        """Verify tax calculation with large income."""
        income = Decimal("1000000")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 1000000 × 0.25 = 250000.00
        expected = Decimal("250000.00")
        assert taxes == expected


# ======================================================
# US REGION TAX TESTS
# ======================================================

class TestUSRegionTaxCalculation:
    """Test US-specific tax calculation with income brackets."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_us_tax_rate_low_income_threshold(self, tax_calculator):
        """Verify US tax rate for income at low bracket threshold ($5000)."""
        income = Decimal("5000")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # At exactly 5000, should use 22% rate (≤ 5000)
        # 5000 × 0.22 = 1100.00
        expected = Decimal("1100.00")
        assert taxes == expected

    def test_us_tax_rate_below_threshold(self, tax_calculator):
        """Verify US tax rate for income below $5000 threshold."""
        income = Decimal("4999")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # 4999 × 0.22 = 1099.78
        expected = Decimal("1099.78")
        assert taxes == expected

    def test_us_tax_rate_above_threshold(self, tax_calculator):
        """Verify US tax rate for income above $5000 threshold."""
        income = Decimal("5001")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # Above 5000, use 30% rate
        # 5001 × 0.30 = 1500.30
        expected = Decimal("1500.30")
        assert taxes == expected

    def test_us_tax_rate_just_above_threshold(self, tax_calculator):
        """Verify tax rate change just above $5000 threshold."""
        income_below = Decimal("5000")
        income_above = Decimal("5000.01")
        region = Region.US

        taxes_below = tax_calculator.calculate(region, income_below)
        taxes_above = tax_calculator.calculate(region, income_above)

        # Below: 5000 × 0.22 = 1100.00
        # Above: 5000.01 × 0.30 = 1500.003 → 1500.00
        assert taxes_below == Decimal("1100.00")
        assert taxes_above == Decimal("1500.00")
        assert taxes_above > taxes_below

    def test_us_low_bracket_rate(self, tax_calculator):
        """Verify US low bracket rate is 22%."""
        income = Decimal("1000")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # 1000 × 0.22 = 220.00
        expected = Decimal("220.00")
        assert taxes == expected

    def test_us_high_bracket_rate(self, tax_calculator):
        """Verify US high bracket rate is 30%."""
        income = Decimal("10000")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # 10000 × 0.30 = 3000.00
        expected = Decimal("3000.00")
        assert taxes == expected

    def test_us_threshold_exactly_5000_01(self, tax_calculator):
        """Verify threshold boundary: exactly $5000.01 uses 30%."""
        income = Decimal("5000.01")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # 5000.01 × 0.30 = 1500.003 → 1500.00 (rounded)
        expected = Decimal("1500.00")
        assert taxes == expected

    def test_us_bracket_difference_illustration(self, tax_calculator):
        """Illustrate the tax difference at the bracket boundary."""
        income = Decimal("5000")
        region = Region.US

        # Same income, but conceptually different rates
        # To show the rate difference, use two incomes
        income_below = Decimal("5000")
        income_above = Decimal("6000")

        taxes_below = tax_calculator.calculate(region, income_below)  # 22%
        taxes_above = tax_calculator.calculate(region, income_above)  # 30%

        # 5000 × 0.22 = 1100
        # 6000 × 0.30 = 1800
        # Difference: 700

        assert taxes_below == Decimal("1100.00")
        assert taxes_above == Decimal("1800.00")
        assert taxes_above - taxes_below == Decimal("700.00")


# ======================================================
# EU REGION TAX TESTS
# ======================================================

class TestEURegionTaxCalculation:
    """Test EU-specific tax calculation with fixed rate."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_eu_tax_rate_fixed_25_percent(self, tax_calculator):
        """Verify EU uses fixed 25% tax rate."""
        income = Decimal("1000")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 1000 × 0.25 = 250.00
        expected = Decimal("250.00")
        assert taxes == expected

    def test_eu_tax_rate_consistent_low_income(self, tax_calculator):
        """Verify EU 25% rate applies to low income."""
        income = Decimal("100")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 100 × 0.25 = 25.00
        expected = Decimal("25.00")
        assert taxes == expected

    def test_eu_tax_rate_consistent_high_income(self, tax_calculator):
        """Verify EU 25% rate applies to high income."""
        income = Decimal("100000")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 100000 × 0.25 = 25000.00
        expected = Decimal("25000.00")
        assert taxes == expected

    def test_eu_tax_rate_at_threshold(self, tax_calculator):
        """Verify EU rate at $5000 threshold (should still be 25%)."""
        income = Decimal("5000")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 5000 × 0.25 = 1250.00 (no bracket change in EU)
        expected = Decimal("1250.00")
        assert taxes == expected

    def test_eu_tax_rate_above_threshold(self, tax_calculator):
        """Verify EU rate above $5000 threshold (should still be 25%)."""
        income = Decimal("10000")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 10000 × 0.25 = 2500.00
        expected = Decimal("2500.00")
        assert taxes == expected

    def test_eu_no_bracket_calculation(self, tax_calculator):
        """Verify EU has no income bracket logic."""
        # EU uses same rate regardless of income
        incomes = [Decimal("1000"), Decimal("5000"), Decimal("10000")]
        region = Region.EU

        tax_rates = []
        for income in incomes:
            taxes = tax_calculator.calculate(region, income)
            rate = taxes / income
            tax_rates.append(rate)

        # All should be 0.25
        assert all(rate == Decimal("0.25") for rate in tax_rates)


# ======================================================
# UA REGION TAX TESTS
# ======================================================

class TestUARegionTaxCalculation:
    """Test UA-specific tax calculation with fixed rate."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_ua_tax_rate_fixed_19_5_percent(self, tax_calculator):
        """Verify UA uses fixed 19.5% tax rate."""
        income = Decimal("1000")
        region = Region.UA

        taxes = tax_calculator.calculate(region, income)

        # 1000 × 0.195 = 195.00
        expected = Decimal("195.00")
        assert taxes == expected

    def test_ua_tax_rate_consistent_low_income(self, tax_calculator):
        """Verify UA 19.5% rate applies to low income."""
        income = Decimal("100")
        region = Region.UA

        taxes = tax_calculator.calculate(region, income)

        # 100 × 0.195 = 19.50
        expected = Decimal("19.50")
        assert taxes == expected

    def test_ua_tax_rate_consistent_high_income(self, tax_calculator):
        """Verify UA 19.5% rate applies to high income."""
        income = Decimal("100000")
        region = Region.UA

        taxes = tax_calculator.calculate(region, income)

        # 100000 × 0.195 = 19500.00
        expected = Decimal("19500.00")
        assert taxes == expected

    def test_ua_tax_rate_at_threshold(self, tax_calculator):
        """Verify UA rate at $5000 threshold (should still be 19.5%)."""
        income = Decimal("5000")
        region = Region.UA

        taxes = tax_calculator.calculate(region, income)

        # 5000 × 0.195 = 975.00
        expected = Decimal("975.00")
        assert taxes == expected

    def test_ua_tax_rate_above_threshold(self, tax_calculator):
        """Verify UA rate above $5000 threshold (should still be 19.5%)."""
        income = Decimal("10000")
        region = Region.UA

        taxes = tax_calculator.calculate(region, income)

        # 10000 × 0.195 = 1950.00
        expected = Decimal("1950.00")
        assert taxes == expected

    def test_ua_no_bracket_calculation(self, tax_calculator):
        """Verify UA has no income bracket logic."""
        # UA uses same rate regardless of income
        incomes = [Decimal("1000"), Decimal("5000"), Decimal("10000")]
        region = Region.UA

        tax_rates = []
        for income in incomes:
            taxes = tax_calculator.calculate(region, income)
            rate = taxes / income
            tax_rates.append(rate)

        # All should be 0.195
        assert all(rate == Decimal("0.195") for rate in tax_rates)


# ======================================================
# TAX RATE COMPARISON TESTS
# ======================================================

class TestTaxRateComparison:
    """Compare tax rates across regions."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_tax_rates_at_same_income_all_regions(self, tax_calculator):
        """Compare tax amounts for same income across regions."""
        income = Decimal("10000")

        us_taxes = tax_calculator.calculate(Region.US, income)    # 30%
        eu_taxes = tax_calculator.calculate(Region.EU, income)    # 25%
        ua_taxes = tax_calculator.calculate(Region.UA, income)    # 19.5%

        # US: 10000 × 0.30 = 3000.00
        # EU: 10000 × 0.25 = 2500.00
        # UA: 10000 × 0.195 = 1950.00

        assert us_taxes == Decimal("3000.00")
        assert eu_taxes == Decimal("2500.00")
        assert ua_taxes == Decimal("1950.00")

        # Verify ordering: US > EU > UA
        assert us_taxes > eu_taxes > ua_taxes

    def test_tax_burden_ranking(self, tax_calculator):
        """Verify tax burden ranking across regions (highest to lowest)."""
        incomes = [Decimal("1000"), Decimal("5000"), Decimal("10000")]

        for income in incomes:
            us = tax_calculator.calculate(Region.US, income)
            eu = tax_calculator.calculate(Region.EU, income)
            ua = tax_calculator.calculate(Region.UA, income)

            # For low income (≤5000): US 22% < EU 25% < UA... wait that's wrong
            # Actually: US 22% < UA 19.5% < EU 25% (for low income)
            # For high income (>5000): US 30% > EU 25% > UA 19.5%

            if income <= Decimal("5000"):
                # Low bracket: US 22% < UA 19.5%? No, 22% > 19.5%
                # US 22% < EU 25%? Yes
                # UA 19.5% < EU 25%? Yes
                assert us < eu
                assert ua < eu
            else:
                # High bracket: US 30% > EU 25% > UA 19.5%
                assert us > eu > ua

    def test_us_bracket_threshold_unique(self, tax_calculator):
        """Verify only US region has income bracket logic."""
        low_income = Decimal("4000")
        high_income = Decimal("6000")

        # US changes rate at threshold
        us_low = tax_calculator.calculate(Region.US, low_income)      # 22%
        us_high = tax_calculator.calculate(Region.US, high_income)    # 30%
        us_low_rate = us_low / low_income
        us_high_rate = us_high / high_income
        assert us_low_rate != us_high_rate  # Rates differ

        # EU doesn't change rate
        eu_low = tax_calculator.calculate(Region.EU, low_income)      # 25%
        eu_high = tax_calculator.calculate(Region.EU, high_income)    # 25%
        eu_low_rate = eu_low / low_income
        eu_high_rate = eu_high / high_income
        assert eu_low_rate == eu_high_rate == Decimal("0.25")  # Same rate

        # UA doesn't change rate
        ua_low = tax_calculator.calculate(Region.UA, low_income)      # 19.5%
        ua_high = tax_calculator.calculate(Region.UA, high_income)    # 19.5%
        ua_low_rate = ua_low / low_income
        ua_high_rate = ua_high / high_income
        assert ua_low_rate == ua_high_rate == Decimal("0.195")  # Same rate


# ======================================================
# DECIMAL PRECISION AND ROUNDING TESTS
# ======================================================

class TestTaxCalculationPrecision:
    """Test decimal precision and rounding in tax calculations."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_tax_calculation_rounding_half_up(self, tax_calculator):
        """Verify tax calculation uses ROUND_HALF_UP."""
        income = Decimal("333.33")  # 333.33 × 0.195 = 65.00035 → 65.00
        region = Region.UA

        taxes = tax_calculator.calculate(region, income)

        # Should round to 2 decimal places
        assert taxes == Decimal("65.00")

    def test_tax_calculation_precise_decimal_handling(self, tax_calculator):
        """Verify tax calculation handles precise decimal values."""
        income = Decimal("1234.56")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 1234.56 × 0.25 = 308.64
        expected = Decimal("308.64")
        assert taxes == expected

    def test_tax_calculation_fractional_cents_rounding(self, tax_calculator):
        """Verify fractional cents are rounded correctly."""
        income = Decimal("1000.01")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # 1000.01 × 0.22 = 220.0022 → 220.00
        # Rounded to 2 decimal places
        assert len(str(taxes).split('.')[-1]) <= 2  # Max 2 decimals

    def test_tax_calculation_no_floating_point_errors(self, tax_calculator):
        """Verify no floating-point precision errors."""
        income = Decimal("0.1") + Decimal("0.2")  # 0.3
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # Should be exactly 0.075, rounded to 0.08
        # Using Decimal, so no floating-point errors
        expected = Money.round(Decimal("0.3") * Decimal("0.25"))
        assert taxes == expected

    def test_tax_calculation_consistent_rounding_large_amounts(self, tax_calculator):
        """Verify rounding consistency with large amounts."""
        income = Decimal("999999.99")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # Should have exactly 2 decimal places
        assert taxes == Decimal("249999.9975").quantize(Decimal("0.01"))

    def test_tax_calculation_very_small_income(self, tax_calculator):
        """Verify tax calculation with very small income."""
        income = Decimal("0.01")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 0.01 × 0.25 = 0.0025 → 0.00
        expected = Decimal("0.00")
        assert taxes == expected

    def test_tax_calculation_minimal_nonzero_tax(self, tax_calculator):
        """Verify minimal non-zero tax is calculated correctly."""
        income = Decimal("0.1")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 0.1 × 0.25 = 0.025 → 0.03 (ROUND_HALF_UP)
        expected = Decimal("0.03")
        assert taxes == expected


# ======================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ======================================================

class TestTaxCalculationEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_us_threshold_exact_5000(self, tax_calculator):
        """Verify exact threshold value $5000 uses 22% rate."""
        income = Decimal("5000")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # At exactly 5000, should use 22% (≤ 5000)
        expected = Decimal("1100.00")
        assert taxes == expected

    def test_us_threshold_5000_00_01(self, tax_calculator):
        """Verify $5000.00 + $0.01 uses 30% rate."""
        income = Decimal("5000.01")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # Just over 5000 uses 30%
        expected = Decimal("1500.00")
        assert taxes == expected

    def test_us_threshold_4999_99(self, tax_calculator):
        """Verify $4999.99 uses 22% rate."""
        income = Decimal("4999.99")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # Just under 5000 uses 22%
        # 4999.99 × 0.22 = 1099.9978 → 1100.00
        expected = Decimal("1100.00")
        assert taxes == expected

    def test_tax_calculation_very_large_income(self, tax_calculator):
        """Verify tax calculation with very large income."""
        income = Decimal("999999999.99")
        region = Region.US

        taxes = tax_calculator.calculate(region, income)

        # 999999999.99 × 0.30 = 299999999.997 → 299999999.99
        assert taxes == Decimal("299999999.99")

    def test_tax_calculation_very_small_fractional_income(self, tax_calculator):
        """Verify tax calculation with very small fractional income."""
        income = Decimal("0.001")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 0.001 × 0.25 = 0.00025 → 0.00
        expected = Decimal("0.00")
        assert taxes == expected

    def test_tax_with_many_decimal_places(self, tax_calculator):
        """Verify tax calculation rounds to 2 decimal places."""
        income = Decimal("333.333333")
        region = Region.EU

        taxes = tax_calculator.calculate(region, income)

        # 333.333333 × 0.25 = 83.333333... → 83.33
        expected = Decimal("83.33")
        assert taxes == expected


# ======================================================
# TAX CALCULATION WITH PAYROLL SERVICE INTEGRATION
# ======================================================

class TestTaxCalculationIntegration:
    """Test tax calculation integrated with PayrollService."""

    @pytest.fixture
    def payroll_service(self):
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    def test_payroll_us_low_bracket_taxation(self, payroll_service):
        """Verify full payroll with US low bracket tax."""
        employee = Employee(
            id="EMP-001",
            name="US Low Income",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("10"),
            worked_hours=Decimal("40"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: 10 × 40 = 400
        # Bonuses: 200 (yearly)
        # Taxable: 600 (≤ 5000, so 22% rate)
        # Taxes: 600 × 0.22 = 132.00
        # Net: 600 - 132 = 468.00

        assert result.gross_pay == Decimal("400.00")
        assert result.bonuses == Decimal("200.00")
        assert result.taxes == Decimal("132.00")
        assert result.net_pay == Decimal("468.00")

    def test_payroll_us_high_bracket_taxation(self, payroll_service):
        """Verify full payroll with US high bracket tax."""
        employee = Employee(
            id="EMP-002",
            name="US High Income",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("30"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (30 × 160) + (30 × 10 × 1.5) + (30 × 5 × 2)
        #      = 4800 + 450 + 300 = 5550
        # Bonuses: 200 (yearly)
        # Taxable: 5750 (> 5000, so 30% rate)
        # Taxes: 5750 × 0.30 = 1725.00
        # Net: 5750 - 1725 = 4025.00

        assert result.gross_pay == Decimal("5550.00")
        assert result.bonuses == Decimal("200.00")
        assert result.taxes == Decimal("1725.00")
        assert result.net_pay == Decimal("4025.00")

    def test_payroll_eu_fixed_rate_taxation(self, payroll_service):
        """Verify full payroll with EU fixed 25% tax."""
        employee = Employee(
            id="EMP-003",
            name="EU Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.EU,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("8"),
            weekend_hours=Decimal("4"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (25 × 160) + (25 × 8 × 1.5) + (25 × 4 × 2)
        #      = 4000 + 300 + 200 = 4500
        # Bonuses: 200 (yearly)
        # Taxable: 4700 (25% always)
        # Taxes: 4700 × 0.25 = 1175.00
        # Net: 4700 - 1175 = 3525.00

        assert result.gross_pay == Decimal("4500.00")
        assert result.bonuses == Decimal("200.00")
        assert result.taxes == Decimal("1175.00")
        assert result.net_pay == Decimal("3525.00")

    def test_payroll_ua_fixed_rate_taxation(self, payroll_service):
        """Verify full payroll with UA fixed 19.5% tax."""
        employee = Employee(
            id="EMP-004",
            name="UA Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.UA,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("6"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (20 × 160) + (20 × 10 × 1.5) + (20 × 6 × 2)
        #      = 3200 + 300 + 240 = 3740
        # Bonuses: 200 (yearly)
        # Taxable: 3940 (19.5% always)
        # Taxes: 3940 × 0.195 = 768.30
        # Net: 3940 - 768.30 = 3171.70

        assert result.gross_pay == Decimal("3740.00")
        assert result.bonuses == Decimal("200.00")
        assert result.taxes == Decimal("768.30")
        assert result.net_pay == Decimal("3171.70")

    def test_payroll_us_threshold_boundary_cross(self, payroll_service):
        """Verify tax rate change when crossing $5000 threshold."""
        # Employee just barely stays below threshold
        employee_below = Employee(
            id="EMP-005",
            name="Below Threshold",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("200"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
            performance_bonus=Decimal("0"),
        )

        result_below = payroll_service.calculate_payroll(employee_below)

        # Gross: 20 × 200 = 4000
        # Bonuses: 200
        # Taxable: 4200 (≤ 5000, so 22%)
        # Taxes: 4200 × 0.22 = 924.00

        assert result_below.taxes == Decimal("924.00")

        # Employee crosses threshold
        employee_above = Employee(
            id="EMP-006",
            name="Above Threshold",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("260"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
            performance_bonus=Decimal("0"),
        )

        result_above = payroll_service.calculate_payroll(employee_above)

        # Gross: 20 × 260 = 5200
        # Bonuses: 200
        # Taxable: 5400 (> 5000, so 30%)
        # Taxes: 5400 × 0.30 = 1620.00

        assert result_above.taxes == Decimal("1620.00")

    def test_payroll_with_performance_bonus_affects_taxes(self, payroll_service):
        """Verify performance bonus is included in taxable income."""
        employee = Employee(
            id="EMP-007",
            name="With Bonus",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("180"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
            performance_bonus=Decimal("500"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: 25 × 180 = 4500
        # Bonuses: 200 (yearly) + 500 (performance) = 700
        # Taxable: 4500 + 700 = 5200 (> 5000, so 30%)
        # Taxes: 5200 × 0.30 = 1560.00
        # Net: 5200 - 1560 = 3640.00

        assert result.gross_pay == Decimal("4500.00")
        assert result.bonuses == Decimal("700.00")
        assert result.taxes == Decimal("1560.00")
        assert result.net_pay == Decimal("3640.00")


# ======================================================
# TAX RATE CONSISTENCY TESTS
# ======================================================

class TestTaxRateConsistency:
    """Test tax rate consistency and correctness."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_us_rate_22_percent_for_low_income(self, tax_calculator):
        """Verify 22% rate is applied for US low bracket."""
        test_cases = [
            Decimal("1"),
            Decimal("100"),
            Decimal("1000"),
            Decimal("5000"),
        ]

        for income in test_cases:
            taxes = tax_calculator.calculate(Region.US, income)
            rate = taxes / income
            assert rate == Decimal("0.22"), f"Income {income} should have 22% rate"

    def test_us_rate_30_percent_for_high_income(self, tax_calculator):
        """Verify 30% rate is applied for US high bracket."""
        test_cases = [
            Decimal("5001"),
            Decimal("10000"),
            Decimal("50000"),
            Decimal("100000"),
        ]

        for income in test_cases:
            taxes = tax_calculator.calculate(Region.US, income)
            rate = taxes / income
            assert rate == Decimal("0.30"), f"Income {income} should have 30% rate"

    def test_eu_rate_always_25_percent(self, tax_calculator):
        """Verify EU always applies 25% rate."""
        test_cases = [
            Decimal("1"),
            Decimal("100"),
            Decimal("1000"),
            Decimal("5000"),
            Decimal("10000"),
            Decimal("100000"),
        ]

        for income in test_cases:
            taxes = tax_calculator.calculate(Region.EU, income)
            rate = taxes / income
            assert rate == Decimal("0.25"), f"Income {income} should have 25% rate"

    def test_ua_rate_always_19_5_percent(self, tax_calculator):
        """Verify UA always applies 19.5% rate."""
        test_cases = [
            Decimal("1"),
            Decimal("100"),
            Decimal("1000"),
            Decimal("5000"),
            Decimal("10000"),
            Decimal("100000"),
        ]

        for income in test_cases:
            taxes = tax_calculator.calculate(Region.UA, income)
            rate = taxes / income
            assert rate == Decimal("0.195"), f"Income {income} should have 19.5% rate"
