import pytest
from decimal import Decimal
from src.payroll_calc import (
    Employee,
    EmployeeType,
    Region,
    PayrollService,
    TaxCalculator,
    BonusCalculator,
    HourlyStrategy,
    Money,
)


class TestHourlyOvertimeCalculation:
    """Characterization tests for hourly employee overtime calculation (1.5x rate)."""

    @pytest.fixture
    def payroll_service(self):
        """Provide a PayrollService instance for testing."""
        return PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

    @pytest.fixture
    def hourly_strategy(self):
        """Provide an HourlyStrategy instance for testing."""
        return HourlyStrategy()

    def test_overtime_calculation_multiplier(self, hourly_strategy):
        """Verify that overtime hours are paid at 1.5x rate."""
        employee = Employee(
            id="EMP-001",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 20 * 10 * 1.5 = 300.00
        expected = Decimal("300.00")

        assert gross_pay == expected, \
            f"Overtime pay should be hourly_rate * overtime_hours * 1.5. " \
            f"Got {gross_pay}, expected {expected}"

    def test_base_pay_plus_overtime(self, hourly_strategy):
        """Verify that base pay and overtime are correctly combined."""
        employee = Employee(
            id="EMP-002",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (25 * 160) + (25 * 10 * 1.5) = 4000 + 375 = 4375.00
        expected = Decimal("4375.00")

        assert gross_pay == expected, \
            f"Gross pay should be base_pay + overtime_pay. " \
            f"Got {gross_pay}, expected {expected}"

    def test_base_pay_plus_overtime_plus_weekend(self, hourly_strategy):
        """Verify that base pay, overtime, and weekend pay are correctly combined."""
        employee = Employee(
            id="EMP-003",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (25 * 160) + (25 * 10 * 1.5) + (25 * 5 * 2) = 4000 + 375 + 250 = 4625.00
        expected = Decimal("4625.00")

        assert gross_pay == expected, \
            f"Gross pay should include base_pay + overtime_pay + weekend_pay. " \
            f"Got {gross_pay}, expected {expected}"

    def test_overtime_only_no_base_hours(self, hourly_strategy):
        """Verify overtime calculation when no base hours worked."""
        employee = Employee(
            id="EMP-004",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("30"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("8"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 30 * 8 * 1.5 = 360.00
        expected = Decimal("360.00")

        assert gross_pay == expected, \
            f"Overtime-only pay should be hourly_rate * overtime_hours * 1.5. " \
            f"Got {gross_pay}, expected {expected}"

    def test_zero_overtime_hours(self, hourly_strategy):
        """Verify calculation when overtime hours are zero."""
        employee = Employee(
            id="EMP-005",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("40"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: 20 * 40 = 800.00
        expected = Decimal("800.00")

        assert gross_pay == expected, \
            f"Pay with no overtime should equal base_pay only. " \
            f"Got {gross_pay}, expected {expected}"

    def test_rounding_with_overtime(self, hourly_strategy):
        """Verify that monetary rounding is correctly applied with overtime."""
        employee = Employee(
            id="EMP-006",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("19.99"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("0"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (19.99 * 160) + (19.99 * 10 * 1.5)
        # = 3198.4 + 299.85 = 3498.25
        expected = Decimal("3498.25")

        assert gross_pay == expected, \
            f"Pay should be rounded to 2 decimal places. " \
            f"Got {gross_pay}, expected {expected}"

    def test_large_overtime_calculation(self, hourly_strategy):
        """Verify overtime calculation with large hour values."""
        employee = Employee(
            id="EMP-007",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("50"),
            worked_hours=Decimal("200"),
            overtime_hours=Decimal("100"),
            weekend_hours=Decimal("50"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (50 * 200) + (50 * 100 * 1.5) + (50 * 50 * 2)
        # = 10000 + 7500 + 5000 = 22500.00
        expected = Decimal("22500.00")

        assert gross_pay == expected, \
            f"Large overtime calculation should be accurate. " \
            f"Got {gross_pay}, expected {expected}"

    def test_full_payroll_with_overtime_us_region(self, payroll_service):
        """Characterization test: Full payroll calculation for hourly employee with overtime in US."""
        employee = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5"),
            performance_bonus=Decimal("150"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross pay: (25 * 160) + (25 * 10 * 1.5) + (25 * 5 * 2)
        # = 4000 + 375 + 250 = 4625.00
        assert result.gross_pay == Decimal("4625.00")

        # Bonuses: Yearly bonus (hourly) 200 + performance bonus 150 = 350.00
        assert result.bonuses == Decimal("350.00")

        # Taxable income: 4625.00 + 350.00 = 4975.00
        # Tax rate for US income <= 5000: 22%
        # Taxes: 4975.00 * 0.22 = 1094.50
        assert result.taxes == Decimal("1094.50")

        # Net pay: 4975.00 - 1094.50 = 3880.50
        assert result.net_pay == Decimal("3880.50")

    def test_full_payroll_with_overtime_eu_region(self, payroll_service):
        """Characterization test: Full payroll calculation for hourly employee with overtime in EU."""
        employee = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.HOURLY,
            region=Region.EU,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("2"),
            performance_bonus=Decimal("100"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross pay: (20 * 160) + (20 * 5 * 1.5) + (20 * 2 * 2)
        # = 3200 + 150 + 80 = 3430.00
        assert result.gross_pay == Decimal("3430.00")

        # Bonuses: Yearly bonus (hourly) 200 + performance bonus 100 = 300.00
        assert result.bonuses == Decimal("300.00")

        # Taxable income: 3430.00 + 300.00 = 3730.00
        # Tax rate for EU: 25%
        # Taxes: 3730.00 * 0.25 = 932.50
        assert result.taxes == Decimal("932.50")

        # Net pay: 3730.00 - 932.50 = 2797.50
        assert result.net_pay == Decimal("2797.50")

    def test_full_payroll_with_overtime_ua_region(self, payroll_service):
        """Characterization test: Full payroll calculation for hourly employee with overtime in UA."""
        employee = Employee(
            id="EMP-003",
            name="Ivan Petrov",
            employee_type=EmployeeType.HOURLY,
            region=Region.UA,
            hourly_rate=Decimal("15"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("8"),
            weekend_hours=Decimal("0"),
            performance_bonus=Decimal("50"),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross pay: (15 * 160) + (15 * 8 * 1.5) + (15 * 0 * 2)
        # = 2400 + 180 + 0 = 2580.00
        assert result.gross_pay == Decimal("2580.00")

        # Bonuses: Yearly bonus (hourly) 200 + performance bonus 50 = 250.00
        assert result.bonuses == Decimal("250.00")

        # Taxable income: 2580.00 + 250.00 = 2830.00
        # Tax rate for UA: 19.5%
        # Taxes: 2830.00 * 0.195 = 552.01 (rounded)
        assert result.taxes == Decimal("552.01")

        # Net pay: 2830.00 - 552.01 = 2277.99
        assert result.net_pay == Decimal("2277.99")

    def test_overtime_decimal_precision(self, hourly_strategy):
        """Verify decimal precision in overtime calculations."""
        employee = Employee(
            id="EMP-008",
            name="Test Employee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("22.50"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("7.5"),
            weekend_hours=Decimal("2.5"),
        )

        gross_pay = hourly_strategy.calculate(employee)
        # Expected: (22.50 * 160) + (22.50 * 7.5 * 1.5) + (22.50 * 2.5 * 2)
        # = 3600 + 253.125 + 112.50 = 3965.625 -> 3965.63 (rounded HALF_UP)
        expected = Decimal("3965.63")

        assert gross_pay == expected, \
            f"Decimal precision should be maintained and rounded correctly. " \
            f"Got {gross_pay}, expected {expected}"

    def test_money_rounding_utility(self):
        """Verify that Money.round() applies ROUND_HALF_UP correctly."""
        # Test standard rounding
        assert Money.round(Decimal("100.125")) == Decimal("100.13")
        assert Money.round(Decimal("100.124")) == Decimal("100.12")
        assert Money.round(Decimal("100.115")) == Decimal("100.12")
        assert Money.round(Decimal("100.005")) == Decimal("100.01")
