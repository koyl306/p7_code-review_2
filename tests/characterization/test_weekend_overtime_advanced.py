"""
Advanced characterization tests for weekend and overtime interaction patterns.

These tests specifically verify how weekend hours (2x) and overtime hours (1.5x)
interact in various combinations, documenting the exact calculation behavior
before any potential refactoring.
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
)


# ======================================================
# WEEKEND + OVERTIME ADVANCED INTERACTION TESTS
# ======================================================

class TestWeekendOvertimeInteraction:
    """Advanced tests for interactions between weekend and overtime multipliers."""

    @pytest.fixture
    def hourly_strategy(self):
        return HourlyStrategy()

    def test_equal_hours_weekend_pays_more_than_overtime(self, hourly_strategy):
        """Verify that equal hours weekend (2x) earns more than overtime (1.5x)."""
        employee_weekend = Employee(
            id="EMP-001",
            name="Weekend Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("10"),
        )

        employee_overtime = Employee(
            id="EMP-002",
            name="Overtime Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("0"),
        )

        weekend_gross = hourly_strategy.calculate(employee_weekend)
        overtime_gross = hourly_strategy.calculate(employee_overtime)

        # Weekend: 20 * 10 * 2 = 400
        # Overtime: 20 * 10 * 1.5 = 300
        # Difference: 100 (33.33% more)

        assert weekend_gross == Decimal("400.00")
        assert overtime_gross == Decimal("300.00")
        difference = weekend_gross - overtime_gross
        assert difference == Decimal("100.00")

    def test_hour_ratio_different_rates_same_multiplier(self, hourly_strategy):
        """Verify that multiplier logic is consistent regardless of hour ratios."""
        # To make weekend and overtime pay equal, need different hour ratios
        # 2x * x hours = 1.5x * y hours
        # For hourly_rate of 20:
        # 2x * 20 * 5 = 1.5x * 20 * ?
        # 200 = 300 * ?/?
        # To get 200 with 1.5x: 20 * 1.5 * z = 200 -> z = 6.67

        employee_weekend = Employee(
            id="EMP-003",
            name="Weekend Only",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("5"),
        )

        employee_overtime = Employee(
            id="EMP-004",
            name="Overtime Only",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("6.666666"),
            weekend_hours=Decimal("0"),
        )

        weekend_gross = hourly_strategy.calculate(employee_weekend)
        overtime_gross = hourly_strategy.calculate(employee_overtime)

        # Weekend: 20 * 5 * 2 = 200.00
        # Overtime: 20 * 6.666666 * 1.5 = 200.00 (approximately, with rounding)

        assert weekend_gross == Decimal("200.00")
        assert overtime_gross == Decimal("200.00")

    def test_weekend_overtime_regular_pay_ratios(self, hourly_strategy):
        """Verify the pay ratio between regular, overtime, and weekend hours."""
        base_rate = Decimal("100")  # Use nice round number for clarity

        # 1 hour each
        employee_regular = Employee(
            id="EMP-005",
            name="Regular",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=base_rate,
            worked_hours=Decimal("1"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        employee_overtime = Employee(
            id="EMP-006",
            name="Overtime",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=base_rate,
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("1"),
            weekend_hours=Decimal("0"),
        )

        employee_weekend = Employee(
            id="EMP-007",
            name="Weekend",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=base_rate,
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("1"),
        )

        regular_gross = hourly_strategy.calculate(employee_regular)
        overtime_gross = hourly_strategy.calculate(employee_overtime)
        weekend_gross = hourly_strategy.calculate(employee_weekend)

        # 100 * 1 * 1.0 = 100.00
        # 100 * 1 * 1.5 = 150.00
        # 100 * 1 * 2.0 = 200.00

        assert regular_gross == Decimal("100.00")
        assert overtime_gross == Decimal("150.00")
        assert weekend_gross == Decimal("200.00")

        # Verify ratios
        assert overtime_gross / regular_gross == Decimal("1.5")
        assert weekend_gross / regular_gross == Decimal("2")
        assert weekend_gross / overtime_gross == Decimal("200") / Decimal("150")


# ======================================================
# COMPLEX WEEKEND + OVERTIME SCENARIOS
# ======================================================

class TestComplexWeekendOvertimeScenarios:
    """Test realistic complex scenarios with weekend and overtime hours."""

    @pytest.fixture
    def payroll_service(self):
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    @pytest.fixture
    def hourly_strategy(self):
        return HourlyStrategy()

    def test_full_time_with_weekend_and_overtime(self, hourly_strategy):
        """Test realistic scenario: full-time employee with both weekend and overtime."""
        employee = Employee(
            id="EMP-008",
            name="Busy Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("30"),
            worked_hours=Decimal("160"),  # Full-time month
            overtime_hours=Decimal("12"),  # Some overtime
            weekend_hours=Decimal("8"),    # Some weekend work
        )

        gross_pay = hourly_strategy.calculate(employee)

        # Regular: 30 * 160 = 4800
        # Overtime: 30 * 12 * 1.5 = 540
        # Weekend: 30 * 8 * 2 = 480
        # Total: 5820.00

        expected = Decimal("5820.00")
        assert gross_pay == expected

    def test_high_overtime_heavy_weekend(self, hourly_strategy):
        """Test scenario with heavy overtime AND heavy weekend hours."""
        employee = Employee(
            id="EMP-009",
            name="Overtime and Weekend Worker",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("120"),   # Part-time
            overtime_hours=Decimal("30"),  # Significant overtime
            weekend_hours=Decimal("16"),   # Two full weekend days
        )

        gross_pay = hourly_strategy.calculate(employee)

        # Regular: 25 * 120 = 3000
        # Overtime: 25 * 30 * 1.5 = 1125
        # Weekend: 25 * 16 * 2 = 800
        # Total: 4925.00

        expected = Decimal("4925.00")
        assert gross_pay == expected

    def test_minimal_hours_all_categories(self, hourly_strategy):
        """Test with minimal hours in each category."""
        employee = Employee(
            id="EMP-010",
            name="Minimal Hours",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("50"),
            worked_hours=Decimal("4"),
            overtime_hours=Decimal("2"),
            weekend_hours=Decimal("1"),
        )

        gross_pay = hourly_strategy.calculate(employee)

        # Regular: 50 * 4 = 200
        # Overtime: 50 * 2 * 1.5 = 150
        # Weekend: 50 * 1 * 2 = 100
        # Total: 450.00

        expected = Decimal("450.00")
        assert gross_pay == expected

    def test_weekend_hours_dominate_pay(self, hourly_strategy):
        """Test scenario where weekend hours make up most of gross pay."""
        employee = Employee(
            id="EMP-011",
            name="Weekend Heavy",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("40"),
            worked_hours=Decimal("20"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("40"),  # 40 hours weekend work
        )

        gross_pay = hourly_strategy.calculate(employee)

        # Regular: 40 * 20 = 800
        # Overtime: 40 * 5 * 1.5 = 300
        # Weekend: 40 * 40 * 2 = 3200
        # Total: 4300.00
        # Weekend component: 3200 / 4300 = 74.4%

        expected = Decimal("4300.00")
        assert gross_pay == expected

        # Verify weekend dominates
        weekend_component = Decimal("40") * Decimal("40") * Decimal("2")
        assert weekend_component > (expected / Decimal("2"))


# ======================================================
# PAYROLL SYSTEM INTEGRATION WITH ADVANCED SCENARIOS
# ======================================================

class TestAdvancedPayrollIntegration:
    """Test full payroll system with complex weekend + overtime scenarios."""

    @pytest.fixture
    def payroll_service(self):
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    def test_payroll_full_calculation_with_both(self, payroll_service):
        """Test complete payroll calculation with both weekend and overtime."""
        employee = Employee(
            id="EMP-012",
            name="Complex Payroll",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("35"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("15"),
            weekend_hours=Decimal("10"),
            performance_bonus=Decimal("250"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross: (35 * 160) + (35 * 15 * 1.5) + (35 * 10 * 2)
        #      = 5600 + 787.50 + 700 = 7087.50
        # Bonuses: 200 (yearly) + 250 (performance) = 450.00
        # Taxable: 7087.50 + 450 = 7537.50
        # Tax (30% for > 5000): 7537.50 * 0.30 = 2261.25
        # Net: 7537.50 - 2261.25 = 5276.25

        assert result.gross_pay == Decimal("7087.50")
        assert result.bonuses == Decimal("450.00")
        assert result.taxes == Decimal("2261.25")
        assert result.net_pay == Decimal("5276.25")

    def test_multiregion_with_weekend_overtime(self, payroll_service):
        """Test same hours across different regions."""
        employees = [
            Employee(
                id="EMP-US",
                name="US Worker",
                employee_type=EmployeeType.HOURLY,
                region=Region.US,
                hourly_rate=Decimal("25"),
                worked_hours=Decimal("160"),
                overtime_hours=Decimal("8"),
                weekend_hours=Decimal("6"),
            ),
            Employee(
                id="EMP-EU",
                name="EU Worker",
                employee_type=EmployeeType.HOURLY,
                region=Region.EU,
                hourly_rate=Decimal("25"),
                worked_hours=Decimal("160"),
                overtime_hours=Decimal("8"),
                weekend_hours=Decimal("6"),
            ),
            Employee(
                id="EMP-UA",
                name="UA Worker",
                employee_type=EmployeeType.HOURLY,
                region=Region.UA,
                hourly_rate=Decimal("25"),
                worked_hours=Decimal("160"),
                overtime_hours=Decimal("8"),
                weekend_hours=Decimal("6"),
            ),
        ]

        results = [payroll_service.calculate_payroll(emp) for emp in employees]

        # All should have same gross pay
        gross_pay = Decimal("4300.00")  # (25*160) + (25*8*1.5) + (25*6*2)
        for result in results:
            assert result.gross_pay == gross_pay

        # But different taxes
        us_result, eu_result, ua_result = results

        # US: income 4300 < 5000, so 22% tax = 946.00
        assert us_result.taxes == Decimal("946.00")

        # EU: 25% tax = 1075.00
        assert eu_result.taxes == Decimal("1075.00")

        # UA: 19.5% tax = 837.75 (rounded)
        assert ua_result.taxes == Decimal("837.75")


# ======================================================
# DISTRIBUTION AND PERCENTAGE TESTS
# ======================================================

class TestWeekendOvertimeDistribution:
    """Test the distribution and percentage of pay from different hour types."""

    @pytest.fixture
    def hourly_strategy(self):
        return HourlyStrategy()

    def test_pay_component_breakdown(self, hourly_strategy):
        """Verify the breakdown of pay by hour type."""
        employee = Employee(
            id="EMP-013",
            name="Breakdown Test",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("40"),
            worked_hours=Decimal("100"),
            overtime_hours=Decimal("20"),
            weekend_hours=Decimal("10"),
        )

        gross_pay = hourly_strategy.calculate(employee)

        # Components:
        regular = Decimal("40") * Decimal("100")  # 4000
        overtime = Decimal("40") * Decimal("20") * Decimal("1.5")  # 1200
        weekend = Decimal("40") * Decimal("10") * Decimal("2")  # 800
        total = regular + overtime + weekend  # 6000

        assert gross_pay == total
        assert gross_pay == Decimal("6000.00")

        # Percentages:
        assert regular / total == Decimal("4000") / Decimal("6000")  # ~66.7%
        assert overtime / total == Decimal("1200") / Decimal("6000")  # 20%
        assert weekend / total == Decimal("800") / Decimal("6000")  # ~13.3%

    def test_equal_hour_weights_different_pay(self, hourly_strategy):
        """Verify that equal hours yield different pay due to multipliers."""
        base_rate = Decimal("50")
        hours_each = Decimal("10")

        components = []
        names = ["Regular", "Overtime", "Weekend"]
        worked_vals = [
            (Decimal("10"), Decimal("0"), Decimal("0")),   # Regular
            (Decimal("0"), Decimal("10"), Decimal("0")),   # Overtime
            (Decimal("0"), Decimal("0"), Decimal("10")),   # Weekend
        ]
        multipliers = [Decimal("1"), Decimal("1.5"), Decimal("2")]

        for (worked, overtime, weekend), mult in zip(worked_vals, multipliers):
            emp = Employee(
                id="TEST",
                name="Test",
                employee_type=EmployeeType.HOURLY,
                region=Region.US,
                hourly_rate=base_rate,
                worked_hours=worked,
                overtime_hours=overtime,
                weekend_hours=weekend,
            )
            gross = hourly_strategy.calculate(emp)
            components.append(gross)

        # Should be 500, 750, 1000
        assert components[0] == Decimal("500.00")
        assert components[1] == Decimal("750.00")
        assert components[2] == Decimal("1000.00")

        # Verify relationships
        assert components[1] == components[0] * Decimal("1.5")
        assert components[2] == components[0] * Decimal("2")
