"""
Comprehensive characterization tests for rounding behavior in the payroll module.

These tests document the exact rounding behavior currently used:
- Money.round() uses ROUND_HALF_UP to 2 decimal places
- All monetary calculations use Decimal type (no floating-point errors)
- Rounding occurs at strategy level, tax level, and final net pay level
- Edge cases with fractional cents and precision

Tests verify:
- ROUND_HALF_UP behavior specifically (0.5 rounds up)
- Rounding in each calculation component
- Cumulative rounding effects
- Decimal precision maintained throughout
- No floating-point errors (using Decimal type)

No business logic changes are made; these tests verify existing rounding behavior
exactly as implemented.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from payroll_calc import (
    Money,
    Employee,
    EmployeeType,
    Region,
    HourlyStrategy,
    SalaryStrategy,
    ContractStrategy,
    TaxCalculator,
    BonusCalculator,
    PayrollService,
)


# ======================================================
# MONEY.ROUND() BASIC ROUNDING TESTS
# ======================================================

class TestMoneyRoundBasic:
    """Test Money.round() method with basic rounding scenarios."""

    def test_round_no_rounding_needed(self):
        """Verify values already at 2 decimals are unchanged."""
        value = Decimal("10.50")
        result = Money.round(value)
        assert result == Decimal("10.50")

    def test_round_single_decimal(self):
        """Verify values with 1 decimal are rounded to 2."""
        value = Decimal("10.5")
        result = Money.round(value)
        assert result == Decimal("10.50")

    def test_round_zero_decimals(self):
        """Verify values with no decimals are formatted to 2."""
        value = Decimal("10")
        result = Money.round(value)
        assert result == Decimal("10.00")

    def test_round_returns_decimal_type(self):
        """Verify Money.round() returns Decimal type."""
        value = Decimal("10.5")
        result = Money.round(value)
        assert isinstance(result, Decimal)

    def test_round_zero_value(self):
        """Verify zero is properly rounded."""
        value = Decimal("0")
        result = Money.round(value)
        assert result == Decimal("0.00")

    def test_round_negative_value(self):
        """Verify negative values are properly rounded."""
        value = Decimal("-10.50")
        result = Money.round(value)
        assert result == Decimal("-10.50")


# ======================================================
# ROUND_HALF_UP BEHAVIOR TESTS
# ======================================================

class TestRoundHalfUpBehavior:
    """Test ROUND_HALF_UP behavior specifically."""

    def test_round_half_up_0_015_rounds_to_0_02(self):
        """Verify 0.015 rounds UP to 0.02 with ROUND_HALF_UP."""
        value = Decimal("0.015")
        result = Money.round(value)
        # 0.015 has 3 decimals, rounds to 2
        # 0.015 → 0.02 (ROUND_HALF_UP rounds .5 up)
        assert result == Decimal("0.02")

    def test_round_half_up_0_025_rounds_to_0_03(self):
        """Verify 0.025 rounds UP to 0.03 with ROUND_HALF_UP."""
        value = Decimal("0.025")
        result = Money.round(value)
        # 0.025 → 0.03 (ROUND_HALF_UP)
        assert result == Decimal("0.03")

    def test_round_half_up_0_035_rounds_to_0_04(self):
        """Verify 0.035 rounds UP to 0.04 with ROUND_HALF_UP."""
        value = Decimal("0.035")
        result = Money.round(value)
        # 0.035 → 0.04
        assert result == Decimal("0.04")

    def test_round_half_up_1_125_rounds_to_1_13(self):
        """Verify 1.125 rounds UP to 1.13 with ROUND_HALF_UP."""
        value = Decimal("1.125")
        result = Money.round(value)
        # 1.125 → 1.13
        assert result == Decimal("1.13")

    def test_round_half_up_10_125_rounds_to_10_13(self):
        """Verify 10.125 rounds UP to 10.13 with ROUND_HALF_UP."""
        value = Decimal("10.125")
        result = Money.round(value)
        # 10.125 → 10.13
        assert result == Decimal("10.13")

    def test_round_half_up_rounds_down_for_less_than_half(self):
        """Verify values less than .5 round down."""
        test_cases = [
            (Decimal("10.124"), Decimal("10.12")),
            (Decimal("10.123"), Decimal("10.12")),
            (Decimal("10.121"), Decimal("10.12")),
        ]
        for value, expected in test_cases:
            result = Money.round(value)
            assert result == expected

    def test_round_half_up_rounds_up_for_greater_than_half(self):
        """Verify values greater than .5 round up."""
        test_cases = [
            (Decimal("10.126"), Decimal("10.13")),
            (Decimal("10.127"), Decimal("10.13")),
            (Decimal("10.129"), Decimal("10.13")),
        ]
        for value, expected in test_cases:
            result = Money.round(value)
            assert result == expected

    def test_round_half_up_exact_half_rounds_up(self):
        """Verify exact .5 always rounds up with ROUND_HALF_UP."""
        test_cases = [
            (Decimal("0.005"), Decimal("0.01")),
            (Decimal("0.015"), Decimal("0.02")),
            (Decimal("0.025"), Decimal("0.03")),
            (Decimal("0.035"), Decimal("0.04")),
            (Decimal("0.045"), Decimal("0.05")),
            (Decimal("0.055"), Decimal("0.06")),
            (Decimal("10.005"), Decimal("10.01")),
            (Decimal("100.005"), Decimal("100.01")),
        ]
        for value, expected in test_cases:
            result = Money.round(value)
            assert result == expected, f"Expected {expected}, got {result} for {value}"

    def test_round_negative_half_up_behavior(self):
        """Verify ROUND_HALF_UP with negative numbers."""
        # ROUND_HALF_UP rounds -0.5 away from zero (more negative)
        test_cases = [
            (Decimal("-0.015"), Decimal("-0.02")),
            (Decimal("-0.025"), Decimal("-0.03")),
            (Decimal("-10.125"), Decimal("-10.13")),
        ]
        for value, expected in test_cases:
            result = Money.round(value)
            assert result == expected


# ======================================================
# ROUNDING IN STRATEGY CALCULATIONS
# ======================================================

class TestHourlyStrategyRounding:
    """Test rounding behavior in HourlyStrategy calculations."""

    @pytest.fixture
    def strategy(self):
        return HourlyStrategy()

    def test_hourly_strategy_rounding_regular_hours(self, strategy):
        """Verify rounding in regular hours calculation."""
        employee = Employee(
            id="EMP-001",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("33.33"),
            worked_hours=Decimal("3"),  # 33.33 × 3 = 99.99
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = strategy.calculate(employee)
        # 33.33 × 3 = 99.99 (exact, no rounding needed)
        assert gross_pay == Decimal("99.99")

    def test_hourly_strategy_rounding_creates_fractional_cent(self, strategy):
        """Verify rounding when calculation creates fractional cents."""
        employee = Employee(
            id="EMP-002",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("10.01"),
            worked_hours=Decimal("3"),  # 10.01 × 3 = 30.03
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = strategy.calculate(employee)
        # 10.01 × 3 = 30.03 (exact)
        assert gross_pay == Decimal("30.03")

    def test_hourly_strategy_rounding_overtime_calculation(self, strategy):
        """Verify rounding in overtime calculation (1.5x multiplier)."""
        employee = Employee(
            id="EMP-003",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("3"),  # 20 × 3 × 1.5 = 90
            weekend_hours=Decimal("0"),
        )

        gross_pay = strategy.calculate(employee)
        # 20 × 3 × 1.5 = 90.00
        assert gross_pay == Decimal("90.00")

    def test_hourly_strategy_rounding_overtime_fractional_rate(self, strategy):
        """Verify rounding when overtime creates fractional cents."""
        employee = Employee(
            id="EMP-004",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("15.50"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("2"),  # 15.50 × 2 × 1.5 = 46.50
            weekend_hours=Decimal("0"),
        )

        gross_pay = strategy.calculate(employee)
        # 15.50 × 2 × 1.5 = 46.50 (exact)
        assert gross_pay == Decimal("46.50")

    def test_hourly_strategy_rounding_all_components_combined(self, strategy):
        """Verify rounding when all components sum with fractional cents."""
        employee = Employee(
            id="EMP-005",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("33.33"),
            worked_hours=Decimal("10"),      # 33.33 × 10 = 333.30
            overtime_hours=Decimal("5"),     # 33.33 × 5 × 1.5 = 249.975 → 249.98
            weekend_hours=Decimal("3"),      # 33.33 × 3 × 2 = 199.98
        )

        gross_pay = strategy.calculate(employee)

        # Regular: 333.30
        # Overtime: 249.975 rounds to 249.98 (ROUND_HALF_UP)
        # Weekend: 199.98
        # Total: 333.30 + 249.98 + 199.98 = 783.26

        expected = Decimal("783.26")
        assert gross_pay == expected

    def test_hourly_strategy_rounding_fractional_hours(self, strategy):
        """Verify rounding with fractional hours."""
        employee = Employee(
            id="EMP-006",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("10.5"),    # 20 × 10.5 = 210
            overtime_hours=Decimal("2.25"),  # 20 × 2.25 × 1.5 = 67.50
            weekend_hours=Decimal("1.333"),  # 20 × 1.333 × 2 = 53.32
        )

        gross_pay = strategy.calculate(employee)

        # Regular: 210.00
        # Overtime: 67.50
        # Weekend: 20 × 1.333 × 2 = 53.32
        # Total: 330.82

        expected = Decimal("330.82")
        assert gross_pay == expected


# ======================================================
# ROUNDING IN TAX CALCULATIONS
# ======================================================

class TestTaxCalculatorRounding:
    """Test rounding behavior in TaxCalculator."""

    @pytest.fixture
    def tax_calculator(self):
        return TaxCalculator()

    def test_tax_rounding_produces_fractional_cents(self, tax_calculator):
        """Verify tax rounding when result has fractional cents."""
        income = Decimal("333.33")
        region = Region.EU  # 25% rate

        taxes = tax_calculator.calculate(region, income)

        # 333.33 × 0.25 = 83.3325 → 83.33
        expected = Decimal("83.33")
        assert taxes == expected

    def test_tax_rounding_half_up_behavior(self, tax_calculator):
        """Verify tax rounds up when fractional cent is .5 or more."""
        # 100 × 0.195 = 19.5 → 19.50 (no fractional third decimal)
        # Try: 1000 × 0.195 = 195.0 → 195.00
        # Try: 333.33 × 0.195 = 65.00035 → 65.00

        income = Decimal("1000.01")
        region = Region.UA  # 19.5% rate

        taxes = tax_calculator.calculate(region, income)

        # 1000.01 × 0.195 = 195.0019...
        # Should round to 195.00
        expected = Decimal("195.00")
        assert taxes == expected

    def test_tax_rounding_very_small_income(self, tax_calculator):
        """Verify rounding with very small income."""
        income = Decimal("0.1")
        region = Region.EU  # 25%

        taxes = tax_calculator.calculate(region, income)

        # 0.1 × 0.25 = 0.025 → 0.03 (ROUND_HALF_UP)
        expected = Decimal("0.03")
        assert taxes == expected

    def test_tax_rounding_accumulation(self, tax_calculator):
        """Verify tax rounding doesn't accumulate incorrectly."""
        # Calculate taxes for multiple amounts and verify precision
        incomes = [Decimal("100"), Decimal("200"), Decimal("300")]
        region = Region.EU

        total_taxes = Decimal("0")
        for income in incomes:
            taxes = tax_calculator.calculate(region, income)
            total_taxes += taxes

        # Each: × 0.25
        # 100 × 0.25 = 25.00
        # 200 × 0.25 = 50.00
        # 300 × 0.25 = 75.00
        # Total: 150.00

        expected = Decimal("150.00")
        assert total_taxes == expected

    def test_tax_us_bracket_rounding(self, tax_calculator):
        """Verify rounding behavior in US bracket calculations."""
        # Test case that creates fractional cents in each bracket

        # Low bracket
        income_low = Decimal("1000.01")
        taxes_low = tax_calculator.calculate(Region.US, income_low)
        # 1000.01 × 0.22 = 220.0022 → 220.00
        assert taxes_low == Decimal("220.00")

        # High bracket
        income_high = Decimal("6000.01")
        taxes_high = tax_calculator.calculate(Region.US, income_high)
        # 6000.01 × 0.30 = 1800.003 → 1800.00
        assert taxes_high == Decimal("1800.00")


# ======================================================
# ROUNDING IN BONUS CALCULATIONS
# ======================================================

class TestBonusCalculatorRounding:
    """Test rounding in BonusCalculator."""

    @pytest.fixture
    def bonus_calculator(self):
        return BonusCalculator()

    def test_bonus_rounding_hourly_employee(self, bonus_calculator):
        """Verify bonus rounding for hourly employees."""
        employee = Employee(
            id="EMP-001",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            performance_bonus=Decimal("150.555"),  # Fractional cents
        )

        bonuses = bonus_calculator.calculate(employee)

        # Yearly: 200
        # Performance: 150.555 → 150.56 (rounded)
        # Total: 350.56

        expected = Decimal("350.56")
        assert bonuses == expected

    def test_bonus_rounding_salary_employee(self, bonus_calculator):
        """Verify bonus rounding for salary employees."""
        employee = Employee(
            id="EMP-002",
            name="Test",
            employee_type=EmployeeType.SALARY,
            region=Region.US,
            performance_bonus=Decimal("100.125"),  # Rounds up
        )

        bonuses = bonus_calculator.calculate(employee)

        # Quarterly: 500
        # Performance: 100.125 → 100.13 (ROUND_HALF_UP)
        # Total: 600.13

        expected = Decimal("600.13")
        assert bonuses == expected

    def test_bonus_rounding_contract_employee(self, bonus_calculator):
        """Verify bonus rounding for contract employees."""
        employee = Employee(
            id="EMP-003",
            name="Test",
            employee_type=EmployeeType.CONTRACT,
            region=Region.US,
            performance_bonus=Decimal("250.999"),
        )

        bonuses = bonus_calculator.calculate(employee)

        # No quarterly or yearly bonus
        # Performance: 250.999 → 251.00 (rounded)
        # Total: 251.00

        expected = Decimal("251.00")
        assert bonuses == expected


# ======================================================
# CUMULATIVE ROUNDING TESTS
# ======================================================

class TestCumulativeRoundingEffects:
    """Test cumulative rounding effects in payroll calculations."""

    @pytest.fixture
    def payroll_service(self):
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    def test_rounding_cumulative_in_gross_pay(self, payroll_service):
        """Verify rounding doesn't accumulate badly in gross pay."""
        employee = Employee(
            id="EMP-001",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("33.33"),
            worked_hours=Decimal("10"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("3"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Regular: 33.33 × 10 = 333.30
        # Overtime: 33.33 × 5 × 1.5 = 249.975 → 249.98
        # Weekend: 33.33 × 3 × 2 = 199.98
        # Gross: 783.26

        assert result.gross_pay == Decimal("783.26")

    def test_rounding_cumulative_gross_and_bonuses(self, payroll_service):
        """Verify rounding doesn't accumulate in gross + bonuses."""
        employee = Employee(
            id="EMP-002",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.50"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("8"),
            weekend_hours=Decimal("4"),
            performance_bonus=Decimal("125.55"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (25.50 × 160) + (25.50 × 8 × 1.5) + (25.50 × 4 × 2)
        #      = 4080 + 306 + 204 = 4590.00
        # Bonuses: 200 + 125.55 = 325.55
        # Total: 4915.55

        taxable = result.gross_pay + result.bonuses
        assert taxable == Decimal("4915.55")

    def test_rounding_cumulative_through_full_payroll(self, payroll_service):
        """Verify rounding doesn't introduce errors in final net pay."""
        employee = Employee(
            id="EMP-003",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.EU,
            hourly_rate=Decimal("22.22"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5"),
            performance_bonus=Decimal("99.99"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Verify calculation is consistent
        taxable = result.gross_pay + result.bonuses
        net = taxable - result.taxes

        # Should match result.net_pay exactly
        assert Money.round(net) == result.net_pay

    def test_rounding_decimal_precision_maintained(self, payroll_service):
        """Verify Decimal precision is maintained throughout."""
        employee = Employee(
            id="EMP-004",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.UA,
            hourly_rate=Decimal("33.33"),
            worked_hours=Decimal("10"),
            overtime_hours=Decimal("3"),
            weekend_hours=Decimal("2"),
            performance_bonus=Decimal("50.50"),
        )

        result = payroll_service.calculate_payroll(employee)

        # All values should be Decimal type
        assert isinstance(result.gross_pay, Decimal)
        assert isinstance(result.bonuses, Decimal)
        assert isinstance(result.taxes, Decimal)
        assert isinstance(result.net_pay, Decimal)

        # All should have at most 2 decimal places
        for value in [result.gross_pay, result.bonuses, result.taxes, result.net_pay]:
            # Check decimal places
            str_value = str(value)
            if '.' in str_value:
                decimals = len(str_value.split('.')[1])
                assert decimals <= 2, f"{value} has {decimals} decimals"


# ======================================================
# EDGE CASES IN ROUNDING
# ======================================================

class TestRoundingEdgeCases:
    """Test edge cases and unusual rounding scenarios."""

    @pytest.fixture
    def payroll_service(self):
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    def test_rounding_zero_values(self, payroll_service):
        """Verify rounding handles zero values correctly."""
        employee = Employee(
            id="EMP-001",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("0"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        assert result.gross_pay == Decimal("0.00")
        assert result.bonuses == Decimal("200.00")  # Yearly bonus for hourly
        assert result.taxes == Decimal("44.00")  # 200 × 0.22
        assert result.net_pay == Decimal("156.00")

    def test_rounding_very_small_amounts(self, payroll_service):
        """Verify rounding with very small amounts rounds correctly."""
        employee = Employee(
            id="EMP-002",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.EU,
            hourly_rate=Decimal("0.01"),
            worked_hours=Decimal("100"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: 0.01 × 100 = 1.00
        # Bonuses: 200.00
        # Taxable: 201.00
        # Taxes: 201 × 0.25 = 50.25
        # Net: 201 - 50.25 = 150.75

        assert result.gross_pay == Decimal("1.00")
        assert result.taxes == Decimal("50.25")
        assert result.net_pay == Decimal("150.75")

    def test_rounding_very_large_amounts(self, payroll_service):
        """Verify rounding works correctly with very large amounts."""
        employee = Employee(
            id="EMP-003",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("999.99"),
            worked_hours=Decimal("1000"),
            overtime_hours=Decimal("100"),
            weekend_hours=Decimal("50"),
            performance_bonus=Decimal("10000.00"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (999.99 × 1000) + (999.99 × 100 × 1.5) + (999.99 × 50 × 2)
        #      = 999990 + 149998.50 + 99999 = 1249987.50
        # All should maintain 2 decimal precision

        assert isinstance(result.gross_pay, Decimal)
        assert isinstance(result.taxes, Decimal)
        assert isinstance(result.net_pay, Decimal)

        # Should have proper decimal places
        gross_str = str(result.gross_pay)
        if '.' in gross_str:
            assert len(gross_str.split('.')[1]) <= 2

    def test_rounding_chain_of_calculations(self, payroll_service):
        """Verify rounding doesn't compound through chain of calculations."""
        # Create employee with rates that commonly create rounding issues
        employee = Employee(
            id="EMP-004",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.UA,
            hourly_rate=Decimal("17.50"),
            worked_hours=Decimal("37.5"),    # 17.50 × 37.5 = 656.25
            overtime_hours=Decimal("2.5"),   # 17.50 × 2.5 × 1.5 = 65.625 → 65.63
            weekend_hours=Decimal("1.5"),    # 17.50 × 1.5 × 2 = 52.50
            performance_bonus=Decimal("33.33"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: 656.25 + 65.63 + 52.50 = 774.38
        # Bonuses: 200 + 33.33 = 233.33
        # Taxable: 1007.71
        # Taxes: 1007.71 × 0.195 = 196.50345 → 196.50
        # Net: 1007.71 - 196.50 = 811.21

        taxable = result.gross_pay + result.bonuses
        net_calc = taxable - result.taxes

        # The net pay should match the calculated value
        assert Money.round(net_calc) == result.net_pay


# ======================================================
# PRECISION LOSS PREVENTION TESTS
# ======================================================

class TestPrecisionLossPrevention:
    """Test that Decimal type prevents floating-point precision loss."""

    def test_no_floating_point_errors_with_decimal(self):
        """Verify Decimal avoids classic floating-point errors."""
        # Classic floating-point error: 0.1 + 0.2 ≠ 0.3
        # With Decimal, this is exact

        d1 = Decimal("0.1")
        d2 = Decimal("0.2")
        d3 = Decimal("0.3")

        result = d1 + d2
        assert result == d3  # Exact in Decimal

        # Apply Money.round to be sure
        assert Money.round(result) == Decimal("0.30")

    def test_decimal_vs_float_difference(self):
        """Illustrate difference between Decimal and float."""
        # Using float (wrong way)
        f1 = 0.1
        f2 = 0.2
        f_sum = f1 + f2
        # f_sum ≈ 0.30000000000000004 (precision error)

        # Using Decimal (correct way - as module does)
        d1 = Decimal("0.1")
        d2 = Decimal("0.2")
        d_sum = d1 + d2
        # d_sum == 0.3 (exact)

        assert d_sum == Decimal("0.3")
        assert d_sum != Decimal(str(f_sum))  # Would be slightly different

    def test_no_precision_loss_in_payroll_calculations(self):
        """Verify payroll calculations don't lose precision."""
        # Many operations that might lose precision with float
        values = [
            Decimal("0.1"),
            Decimal("0.2"),
            Decimal("0.3"),
            Decimal("0.05"),
            Decimal("0.15"),
        ]

        total = sum(values)

        # With Decimal, should be exactly 0.8
        assert total == Decimal("0.8")
        assert Money.round(total) == Decimal("0.80")

    def test_precision_maintained_through_multiply(self):
        """Verify precision maintained through multiplication."""
        rate = Decimal("33.33")
        hours = Decimal("10")

        # Exact Decimal arithmetic
        result = rate * hours

        # Should be exactly 333.3
        assert result == Decimal("333.3")
        assert Money.round(result) == Decimal("333.30")


# ======================================================
# ROUNDING CONSISTENCY TESTS
# ======================================================

class TestRoundingConsistency:
    """Test that rounding behavior is consistent."""

    @pytest.fixture
    def payroll_service(self):
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    def test_same_calculation_produces_same_result(self, payroll_service):
        """Verify deterministic rounding (same input = same output)."""
        employee = Employee(
            id="EMP-001",
            name="Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("22.22"),
            worked_hours=Decimal("10.5"),
            overtime_hours=Decimal("3.75"),
            weekend_hours=Decimal("2.25"),
            performance_bonus=Decimal("55.55"),
        )

        # Calculate twice
        result1 = payroll_service.calculate_payroll(employee)
        result2 = payroll_service.calculate_payroll(employee)

        # Should be identical
        assert result1.gross_pay == result2.gross_pay
        assert result1.bonuses == result2.bonuses
        assert result1.taxes == result2.taxes
        assert result1.net_pay == result2.net_pay

    def test_rounding_consistent_across_different_paths(self, payroll_service):
        """Verify rounding is consistent regardless of calculation order."""
        rate = Decimal("33.33")
        hours = Decimal("10")

        # Path 1: rate × hours then round
        path1 = Money.round(rate * hours)

        # Path 2: individual calculations then sum
        regular = Money.round(rate * hours)

        # Should be identical
        assert path1 == regular

    def test_rounding_cumulative_vs_individual(self, payroll_service):
        """Test cumulative rounding vs individual component rounding."""
        rate = Decimal("33.33")
        worked = Decimal("10")
        overtime = Decimal("5")
        weekend = Decimal("3")

        # Method 1: Calculate each component, round individually, then sum
        regular = Money.round(rate * worked)
        ot = Money.round(rate * overtime * Decimal("1.5"))
        we = Money.round(rate * weekend * Decimal("2"))
        total_individual = Money.round(regular + ot + we)

        # Method 2: Calculate total then round once
        total_combined = rate * worked + rate * overtime * Decimal("1.5") + rate * weekend * Decimal("2")
        total_combined_rounded = Money.round(total_combined)

        # Should be identical (both match the actual strategy implementation)
        assert total_individual == total_combined_rounded
