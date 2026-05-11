"""
Characterization tests for hourly employee payroll calculations with overtime.

These tests document the current behavior of the HourlyStrategy for calculating
gross pay including overtime (1.5x rate) and weekend work (2x rate).
No business logic changes are made; these tests verify existing output.
"""

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
    PayrollStrategyFactory,
)


class TestHourlyStrategyBasicCalculation:
    """Test basic gross pay calculation for hourly employees."""

    def test_hourly_strategy_basic_hours_only(self):
        """Verify base pay calculation without overtime or weekend hours."""
        employee = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # 160 hours * $25/hour = $4000.00
        assert gross_pay == Decimal("4000.00")

    def test_hourly_strategy_with_overtime(self):
        """Verify overtime pay is calculated at 1.5x rate."""
        employee = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("0"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # Base: 160 hours * $20 = $3200
        # Overtime: 10 hours * $20 * 1.5 = $300
        # Total: $3500.00
        assert gross_pay == Decimal("3500.00")

    def test_hourly_strategy_with_weekend_hours(self):
        """Verify weekend pay is calculated at 2x rate."""
        employee = Employee(
            id="EMP-003",
            name="Bob Johnson",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("15"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("8"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # Base: 160 hours * $15 = $2400
        # Weekend: 8 hours * $15 * 2 = $240
        # Total: $2640.00
        assert gross_pay == Decimal("2640.00")

    def test_hourly_strategy_with_overtime_and_weekend(self):
        """Verify combined overtime and weekend pay calculation."""
        employee = Employee(
            id="EMP-004",
            name="Alice Brown",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # Base: 160 hours * $25 = $4000
        # Overtime: 10 hours * $25 * 1.5 = $375
        # Weekend: 5 hours * $25 * 2 = $250
        # Total: $4625.00
        assert gross_pay == Decimal("4625.00")


class TestHourlyStrategyEdgeCases:
    """Test edge cases and boundary conditions for hourly calculations."""

    def test_hourly_zero_hours(self):
        """Verify behavior when employee works no hours."""
        employee = Employee(
            id="EMP-005",
            name="Charlie Davis",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        assert gross_pay == Decimal("0.00")

    def test_hourly_fractional_hours(self):
        """Verify calculation with fractional hours."""
        employee = Employee(
            id="EMP-006",
            name="Emma Wilson",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("22.50"),
            worked_hours=Decimal("160.5"),
            overtime_hours=Decimal("10.25"),
            weekend_hours=Decimal("5.75"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # Base: 160.5 * 22.50 = 3611.25
        # Overtime: 10.25 * 22.50 * 1.5 = 345.9375
        # Weekend: 5.75 * 22.50 * 2 = 258.75
        # Total: 4215.9375 -> rounded to 4215.94
        assert gross_pay == Decimal("4215.94")

    def test_hourly_high_rate(self):
        """Verify calculation with high hourly rates."""
        employee = Employee(
            id="EMP-007",
            name="Frank Thompson",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("150.00"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("20"),
            weekend_hours=Decimal("10"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # Base: 160 * 150 = 24000
        # Overtime: 20 * 150 * 1.5 = 4500
        # Weekend: 10 * 150 * 2 = 3000
        # Total: 31500.00
        assert gross_pay == Decimal("31500.00")

    def test_hourly_low_rate(self):
        """Verify calculation with minimum wage-like rates."""
        employee = Employee(
            id="EMP-008",
            name="Grace Lee",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("7.25"),
            worked_hours=Decimal("40"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("2"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # Base: 40 * 7.25 = 290
        # Overtime: 5 * 7.25 * 1.5 = 54.375
        # Weekend: 2 * 7.25 * 2 = 29
        # Total: 373.375 -> rounded to 373.38
        assert gross_pay == Decimal("373.38")


class TestHourlyStrategyWithPayrollService:
    """Test hourly employee payroll calculation through the full service."""

    def test_hourly_employee_full_payroll_us_region(self):
        """Verify complete payroll calculation for hourly employee in US region."""
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

        payroll_service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator(),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross Pay: 160*25 + 10*25*1.5 + 5*25*2 = 4000 + 375 + 250 = 4625.00
        assert result.gross_pay == Decimal("4625.00")

        # Bonuses: performance_bonus (150) + yearly_bonus for HOURLY (200)
        assert result.bonuses == Decimal("350.00")

        # Taxable income: 4625 + 350 = 4975 (less than 5000, so 22% tax rate for US)
        # Taxes: 4975 * 0.22 = 1094.50
        assert result.taxes == Decimal("1094.50")

        # Net Pay: 4975 - 1094.50 = 3880.50
        assert result.net_pay == Decimal("3880.50")

    def test_hourly_employee_full_payroll_eu_region(self):
        """Verify complete payroll calculation for hourly employee in EU region."""
        employee = Employee(
            id="EMP-009",
            name="Hans Mueller",
            employee_type=EmployeeType.HOURLY,
            region=Region.EU,
            hourly_rate=Decimal("20"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("5"),
            weekend_hours=Decimal("2"),
            performance_bonus=Decimal("100"),
        )

        payroll_service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator(),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross Pay: 160*20 + 5*20*1.5 + 2*20*2 = 3200 + 150 + 80 = 3430.00
        assert result.gross_pay == Decimal("3430.00")

        # Bonuses: performance_bonus (100) + yearly_bonus for HOURLY (200)
        assert result.bonuses == Decimal("300.00")

        # Taxable income: 3430 + 300 = 3730
        # Taxes (EU): 3730 * 0.25 = 932.50
        assert result.taxes == Decimal("932.50")

        # Net Pay: 3730 - 932.50 = 2797.50
        assert result.net_pay == Decimal("2797.50")

    def test_hourly_employee_full_payroll_ua_region(self):
        """Verify complete payroll calculation for hourly employee in UA region."""
        employee = Employee(
            id="EMP-010",
            name="Vasyl Petrov",
            employee_type=EmployeeType.HOURLY,
            region=Region.UA,
            hourly_rate=Decimal("10"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("8"),
            weekend_hours=Decimal("4"),
            performance_bonus=Decimal("50"),
        )

        payroll_service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator(),
        )

        result = payroll_service.calculate_payroll(employee)

        # Gross Pay: 160*10 + 8*10*1.5 + 4*10*2 = 1600 + 120 + 80 = 1800.00
        assert result.gross_pay == Decimal("1800.00")

        # Bonuses: performance_bonus (50) + yearly_bonus for HOURLY (200)
        assert result.bonuses == Decimal("250.00")

        # Taxable income: 1800 + 250 = 2050
        # Taxes (UA): 2050 * 0.195 = 399.75
        assert result.taxes == Decimal("399.75")

        # Net Pay: 2050 - 399.75 = 1650.25
        assert result.net_pay == Decimal("1650.25")


class TestHourlyStrategyRounding:
    """Test rounding behavior in hourly calculations."""

    def test_hourly_rounding_down(self):
        """Verify rounding behavior with values below .005."""
        employee = Employee(
            id="EMP-011",
            name="Isaac Newton",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("12.33"),
            worked_hours=Decimal("10.11"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # 10.11 * 12.33 = 124.6563 -> rounds to 124.66
        assert gross_pay == Decimal("124.66")

    def test_hourly_rounding_up(self):
        """Verify rounding behavior with values at or above .005."""
        employee = Employee(
            id="EMP-012",
            name="Marie Curie",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("12.37"),
            worked_hours=Decimal("10.11"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # 10.11 * 12.37 = 124.9107 -> rounds to 124.91
        assert gross_pay == Decimal("124.91")

    def test_hourly_rounding_with_overtime_complex(self):
        """Verify rounding with complex calculation involving overtime."""
        employee = Employee(
            id="EMP-013",
            name="Albert Einstein",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("33.33"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("7.5"),
            weekend_hours=Decimal("3.33"),
        )

        strategy = HourlyStrategy()
        gross_pay = strategy.calculate(employee)

        # Base: 160 * 33.33 = 5332.80
        # Overtime: 7.5 * 33.33 * 1.5 = 374.8875
        # Weekend: 3.33 * 33.33 * 2 = 221.7978
        # Total: 5929.4853 -> rounds to 5929.49
        assert gross_pay == Decimal("5929.49")


class TestHourlyStrategyFactoryIntegration:
    """Test that HourlyStrategy is correctly created by factory."""

    def test_strategy_factory_returns_hourly_strategy(self):
        """Verify factory creates HourlyStrategy for HOURLY employee type."""
        strategy = PayrollStrategyFactory.create(EmployeeType.HOURLY)

        assert isinstance(strategy, HourlyStrategy)

    def test_hourly_strategy_instance_reuse(self):
        """Verify factory reuses strategy instances."""
        strategy1 = PayrollStrategyFactory.create(EmployeeType.HOURLY)
        strategy2 = PayrollStrategyFactory.create(EmployeeType.HOURLY)

        # Factory returns the same instance
        assert strategy1 is strategy2


class TestOvertimeRateMultiplier:
    """Specific tests validating the 1.5x overtime multiplier."""

    def test_overtime_multiplier_is_1_5(self):
        """Verify overtime hours use exactly 1.5x rate multiplier."""
        employee_overtime = Employee(
            id="EMP-014",
            name="Test Overtime",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("100"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("1"),
            weekend_hours=Decimal("0"),
        )

        employee_regular = Employee(
            id="EMP-015",
            name="Test Regular",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("150"),  # 100 * 1.5
            worked_hours=Decimal("1"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        strategy = HourlyStrategy()
        overtime_pay = strategy.calculate(employee_overtime)
        regular_pay = strategy.calculate(employee_regular)

        # 1 overtime hour at $100 * 1.5 should equal 1 regular hour at $150
        assert overtime_pay == regular_pay
        assert overtime_pay == Decimal("150.00")

    def test_weekend_multiplier_is_2_0(self):
        """Verify weekend hours use exactly 2.0x rate multiplier."""
        employee_weekend = Employee(
            id="EMP-016",
            name="Test Weekend",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("100"),
            worked_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("1"),
        )

        employee_regular = Employee(
            id="EMP-017",
            name="Test Regular",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("200"),  # 100 * 2
            worked_hours=Decimal("1"),
            overtime_hours=Decimal("0"),
            weekend_hours=Decimal("0"),
        )

        strategy = HourlyStrategy()
        weekend_pay = strategy.calculate(employee_weekend)
        regular_pay = strategy.calculate(employee_regular)

        # 1 weekend hour at $100 * 2 should equal 1 regular hour at $200
        assert weekend_pay == regular_pay
        assert weekend_pay == Decimal("200.00")
