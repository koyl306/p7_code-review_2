"""
Comprehensive characterization tests for weekend overtime calculations.

These tests document the current behavior of the HourlyStrategy for calculating
weekend pay using the 2x multiplier logic. Tests cover:
- Weekend hours at 2x base rate
- Combination of regular, overtime, and weekend hours
- Edge cases and boundary conditions
- Decimal precision and rounding behavior
- Tax and bonus calculations with weekend pay included

No business logic changes are made; these tests verify existing output exactly.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from payroll_calc import (
    Employee,
    EmployeeType,
    Region,
    PayrollService,
    TaxCalculator,
    BonusCalculator,
    HourlyStrategy,
    Money,
    PayrollStrategyFactory,
)


# ======================================================
# WEEKEND CALCULATION TESTS - CORE BEHAVIOR
# ======================================================

class TestWeekendHoursBasic:
    """Test basic weekend hour calculations using 2x multiplier."""

    @pytest.fixture
    def hourly_strategy(self):
        """Provide an HourlyStrategy instance for testing."""
        return HourlyStrategy()

    def test_weekend_hours_only_2x_multiplier(self, hourly_strategy):
        """Verify weekend hours are paid at 2x base rate."""
        employee = Employee(
            id="EMP-001",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("5"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 20 * 5 * 2 = 200.00
        expected = Decimal("200.00")

        assert gross_pay == expected, \
            f"Weekend pay should be hourly_rate * weekend_hours * 2. " \
            f"Got {gross_pay}, expected {expected}"

    def test_weekend_hours_with_decimal_rate(self, hourly_strategy):
        """Verify weekend calculation works with decimal hourly rates."""
        employee = Employee(
            id="EMP-002",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.50"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("8"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 25.50 * 8 * 2 = 408.00
        expected = Decimal("408.00")

        assert gross_pay == expected

    def test_weekend_hours_single_hour(self, hourly_strategy):
        """Verify calculation works with single weekend hour."""
        employee = Employee(
            id="EMP-003",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("30"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("1"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 30 * 1 * 2 = 60.00
        expected = Decimal("60.00")

        assert gross_pay == expected

    def test_weekend_hours_zero(self, hourly_strategy):
        """Verify calculation with zero weekend hours contributes zero."""
        employee = Employee(
            id="EMP-004",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 20 * 160 = 3200.00
        expected = Decimal("3200.00")

        assert gross_pay == expected


# ======================================================
# WEEKEND + OVERTIME COMBINATION TESTS
# ======================================================

class TestWeekendAndOvertimeCombination:
    """Test weekend hours combined with regular and overtime hours."""

    @pytest.fixture
    def hourly_strategy(self):
        return HourlyStrategy()

    def test_regular_and_weekend_hours(self, hourly_strategy):
        """Verify regular hours (1x) and weekend hours (2x) combine correctly."""
        employee = Employee(
            id="EMP-005",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("4"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (20 * 160) + (20 * 4 * 2) = 3200 + 160 = 3360.00
        expected = Decimal("3360.00")

        assert gross_pay == expected

    def test_overtime_and_weekend_hours(self, hourly_strategy):
        """Verify overtime hours (1.5x) and weekend hours (2x) combine correctly."""
        employee = Employee(
            id="EMP-006",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (20 * 10 * 1.5) + (20 * 5 * 2) = 300 + 200 = 500.00
        expected = Decimal("500.00")

        assert gross_pay == expected

    def test_regular_overtime_and_weekend_hours(self, hourly_strategy):
        """Verify all three categories: regular (1x), overtime (1.5x), weekend (2x)."""
        employee = Employee(
            id="EMP-007",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("8"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (25 * 160) + (25 * 10 * 1.5) + (25 * 8 * 2)
        #         = 4000 + 375 + 400 = 4775.00
        expected = Decimal("4775.00")

        assert gross_pay == expected

    def test_high_weekend_hours_volume(self, hourly_strategy):
        """Verify calculation with high volume of weekend hours."""
        employee = Employee(
            id="EMP-008",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("50"),
            worked_hours=Decimal("80"),
            overtime_hours=Decimal("20"),
            weekend_hours=Decimal("32"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (50 * 80) + (50 * 20 * 1.5) + (50 * 32 * 2)
        #         = 4000 + 1500 + 3200 = 8700.00
        expected = Decimal("8700.00")

        assert gross_pay == expected


# ======================================================
# DECIMAL PRECISION AND ROUNDING TESTS
# ======================================================

class TestWeekendCalculationsPrecision:
    """Test decimal precision and rounding behavior in weekend calculations."""

    @pytest.fixture
    def hourly_strategy(self):
        return HourlyStrategy()

    def test_weekend_hours_with_fractional_hours(self, hourly_strategy):
        """Verify weekend calculation handles fractional hours correctly."""
        employee = Employee(
            id="EMP-009",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("3.5"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 20 * 3.5 * 2 = 140.00
        expected = Decimal("140.00")

        assert gross_pay == expected

    def test_weekend_hours_precise_rounding(self, hourly_strategy):
        """Verify rounding behavior with weekend hours producing fractional cents."""
        employee = Employee(
            id="EMP-010",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("33.33"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("3"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 33.33 * 3 * 2 = 199.98
        expected = Decimal("199.98")

        assert gross_pay == expected

    def test_weekend_hours_rounding_half_up(self, hourly_strategy):
        """Verify ROUND_HALF_UP behavior in weekend calculations."""
        employee = Employee(
            id="EMP-011",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("15.1"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("5.3"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 15.1 * 5.3 * 2 = 160.06
        expected = Decimal("160.06")

        assert gross_pay == expected

    def test_all_hours_fractional(self, hourly_strategy):
        """Verify calculation with fractional hours across all categories."""
        employee = Employee(
            id="EMP-012",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("22.50"),
            worked_hours=Decimal("150.5"),
            overtime_hours=Decimal("8.25"),
            weekend_hours=Decimal("6.75"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (22.50 * 150.5) + (22.50 * 8.25 * 1.5) + (22.50 * 6.75 * 2)
        #         = 3386.25 + 278.4375 + 303.75 = 3968.44 (after rounding)
        expected = Decimal("3968.44")

        assert gross_pay == expected


# ======================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ======================================================

class TestWeekendCalculationsEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def hourly_strategy(self):
        return HourlyStrategy()

    def test_weekend_hours_very_large_value(self, hourly_strategy):
        """Verify calculation handles very large weekend hour volumes."""
        employee = Employee(
            id="EMP-013",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("100"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("500"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 100 * 500 * 2 = 100000.00
        expected = Decimal("100000.00")

        assert gross_pay == expected

    def test_weekend_hours_very_small_rate(self, hourly_strategy):
        """Verify calculation handles very small hourly rates."""
        employee = Employee(
            id="EMP-014",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("0.01"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("100"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 0.01 * 100 * 2 = 2.00
        expected = Decimal("2.00")

        assert gross_pay == expected

    def test_weekend_hours_minimal_fractional(self, hourly_strategy):
        """Verify calculation handles minimal fractional values."""
        employee = Employee(
            id="EMP-015",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0.01"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 20 * 0.01 * 2 = 0.40
        expected = Decimal("0.40")

        assert gross_pay == expected

    def test_weekend_only_no_other_hours(self, hourly_strategy):
        """Verify employee working only weekend hours."""
        employee = Employee(
            id="EMP-016",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("24"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 25 * 24 * 2 = 1200.00
        expected = Decimal("1200.00")

        assert gross_pay == expected


# ======================================================
# PAYROLL SERVICE INTEGRATION TESTS
# ======================================================

class TestWeekendCalculationsWithPayrollService:
    """Test weekend calculations integrated with full payroll service."""

    @pytest.fixture
    def payroll_service(self):
        """Provide a PayrollService instance for testing."""
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    def test_weekend_hours_included_in_gross_pay(self, payroll_service):
        """Verify weekend hours are included in gross pay calculation."""
        employee = Employee(
            id="EMP-017",
            name="John Weekend Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("8"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross pay: (20 * 160) + (20 * 8 * 2) = 3200 + 320 = 3520
        expected_gross = Decimal("3520.00")
        assert result.gross_pay == expected_gross

    def test_weekend_hours_affect_tax_calculation(self, payroll_service):
        """Verify weekend hours increase taxable income."""
        employee = Employee(
            id="EMP-018",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("200"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("10"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (25 * 200) + (25 * 5 * 1.5) + (25 * 10 * 2) = 5000 + 187.50 + 500 = 5687.50
        # Taxable: 5687.50 (no bonuses)
        # US tax rate for income > 5000 is 30%
        # Taxes: 5687.50 * 0.30 = 1706.25
        expected_taxes = Decimal("1706.25")
        assert result.taxes == expected_taxes

    def test_weekend_hours_hourly_bonus_with_overtime(self, payroll_service):
        """Verify hourly bonus is applied with weekend hours."""
        employee = Employee(
            id="EMP-019",
            name="Hourly Bonus Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("4"),
            performance_bonus=Decimal("100"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (20 * 160) + (20 * 5 * 1.5) + (20 * 4 * 2) = 3200 + 150 + 160 = 3510.00
        # Bonuses: 200 (yearly) + 100 (performance) = 300.00
        expected_gross = Decimal("3510.00")
        expected_bonuses = Decimal("300.00")

        assert result.gross_pay == expected_gross
        assert result.bonuses == expected_bonuses

    def test_weekend_hours_net_pay_calculation(self, payroll_service):
        """Verify net pay correctly accounts for weekend hours."""
        employee = Employee(
            id="EMP-020",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.EU,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("10"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (20 * 160) + (20 * 10 * 2) = 3200 + 400 = 3600.00
        # Taxable: 3600.00
        # EU tax rate: 25%
        # Taxes: 3600 * 0.25 = 900.00
        # Net: 3600 - 900 = 2700.00

        expected_gross = Decimal("3600.00")
        expected_taxes = Decimal("900.00")
        expected_net = Decimal("2700.00")

        assert result.gross_pay == expected_gross
        assert result.taxes == expected_taxes
        assert result.net_pay == expected_net


# ======================================================
# MULTI-REGION WEEKEND TESTS
# ======================================================

class TestWeekendCalculationsMultiRegion:
    """Test weekend calculations across different regions."""

    @pytest.fixture
    def payroll_service(self):
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    def test_weekend_hours_us_region(self, payroll_service):
        """Verify weekend calculation with US tax rates."""
        employee = Employee(
            id="EMP-021",
            name="US Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("30"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("6"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (30 * 160) + (30 * 6 * 2) = 4800 + 360 = 5160.00
        # Income > 5000, so 30% tax rate
        # Taxes: 5160 * 0.30 = 1548.00
        # Net: 5160 - 1548 = 3612.00

        assert result.gross_pay == Decimal("5160.00")
        assert result.taxes == Decimal("1548.00")
        assert result.net_pay == Decimal("3612.00")

    def test_weekend_hours_eu_region(self, payroll_service):
        """Verify weekend calculation with EU tax rates."""
        employee = Employee(
            id="EMP-022",
            name="EU Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.EU,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("8"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (25 * 160) + (25 * 5 * 1.5) + (25 * 8 * 2) = 4000 + 187.50 + 400 = 4587.50
        # EU tax rate: 25%
        # Taxes: 4587.50 * 0.25 = 1146.88 (rounded)
        # Net: 4587.50 - 1146.88 = 3440.62

        assert result.gross_pay == Decimal("4587.50")
        assert result.taxes == Decimal("1146.88")
        assert result.net_pay == Decimal("3440.62")

    def test_weekend_hours_ua_region(self, payroll_service):
        """Verify weekend calculation with UA tax rates."""
        employee = Employee(
            id="EMP-023",
            name="UA Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.UA,
            hourly_rate=Decimal("15"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("12"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (15 * 160) + (15 * 10 * 1.5) + (15 * 12 * 2) = 2400 + 225 + 360 = 2985.00
        # UA tax rate: 19.5%
        # Taxes: 2985 * 0.195 = 582.08 (rounded)
        # Net: 2985 - 582.08 = 2402.92

        assert result.gross_pay == Decimal("2985.00")
        assert result.taxes == Decimal("582.08")
        assert result.net_pay == Decimal("2402.92")


# ======================================================
# REPORT GENERATION TESTS
# ======================================================

class TestWeekendCalculationsReportGeneration:
    """Test that weekend calculations are correctly reported."""

    def test_weekend_hours_in_payroll_report(self):
        """Verify weekend hours appear correctly in payroll report."""
        payroll_service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

        employee = Employee(
            id="EMP-024",
            name="Report Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("8"),
            performance_bonus=Decimal("0"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross includes weekend hours: 3200 + 320 = 3520.00
        assert result.gross_pay == Decimal("3520.00")
        assert result.employee_id == "EMP-024"


# ======================================================
# STRATEGY FACTORY INTEGRATION TESTS
# ======================================================

class TestWeekendCalculationsViaFactory:
    """Test weekend calculations through PayrollStrategyFactory."""

    def test_hourly_strategy_from_factory_with_weekend_hours(self):
        """Verify factory creates correct strategy for weekend calculations."""
        strategy = PayrollStrategyFactory.create(EmployeeType.HOURLY)

        employee = Employee(
            id="EMP-025",
            name="Factory Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("8"),
            weekend_hours=Decimal("5"),
        )

        gross_pay = strategy.calculate(employee)

        # Expected: (25 * 160) + (25 * 8 * 1.5) + (25 * 5 * 2) = 4000 + 300 + 250 = 4550.00
        expected = Decimal("4550.00")

        assert gross_pay == expected


# ======================================================
# COMPARISON TESTS - MULTIPLIER VERIFICATION
# ======================================================

class TestWeekendVsOvertimeMultiplier:
    """Verify that weekend (2x) multiplier is distinct from overtime (1.5x)."""

    @pytest.fixture
    def hourly_strategy(self):
        return HourlyStrategy()

    def test_weekend_multiplier_greater_than_overtime(self, hourly_strategy):
        """Verify 2x weekend multiplier is greater than 1.5x overtime."""
        # Same base: $20/hour, same hours worked
        employee_weekend = Employee(
            id="EMP-026",
            name="Weekend Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("10"),
        )

        employee_overtime = Employee(
            id="EMP-027",
            name="Overtime Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("0"),
        )

        weekend_pay = hourly_strategy.calculate(employee_weekend)
        overtime_pay = hourly_strategy.calculate(employee_overtime)

        # Weekend: 20 * 10 * 2 = 400
        # Overtime: 20 * 10 * 1.5 = 300
        assert weekend_pay == Decimal("400.00")
        assert overtime_pay == Decimal("300.00")
        assert weekend_pay > overtime_pay

    def test_weekend_premium_calculation(self, hourly_strategy):
        """Verify weekend pay premium over base rate."""
        base_rate = Decimal("30")
        hours = Decimal("8")

        employee = Employee(
            id="EMP-028",
            name="Premium Check",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=base_rate,
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=hours,
        )

        weekend_gross = hourly_strategy.calculate(employee)

        # Weekend premium: base_rate * hours * 2 = 30 * 8 * 2 = 480
        # This is 100% premium over base rate (base would be 30 * 8 = 240)
        base_pay = base_rate * hours
        premium_pay = weekend_gross

        assert premium_pay == base_pay * Decimal("2")
        assert premium_pay == Decimal("480.00")
