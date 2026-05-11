import pytest
from decimal import Decimal
from payroll_calc import (
    Employee,
    EmployeeType,
    Region,
    PayrollResult,
    Money,
    HourlyStrategy,
    SalaryStrategy,
    ContractStrategy,
    TaxCalculator,
    BonusCalculator,
    PayrollService,
    PayrollReportGenerator,
    PayrollStrategyFactory
)


# ======================================================
# MONEY UTILITIES TESTS
# ======================================================

class TestMoney:
    """Test Money.round() method"""

    def test_round_basic_half_up(self):
        """Test basic rounding with ROUND_HALF_UP"""
        assert Money.round(Decimal("10.125")) == Decimal("10.12")

    def test_round_exact_two_decimals(self):
        """Test value that is already at two decimals"""
        assert Money.round(Decimal("10.50")) == Decimal("10.50")

    def test_round_zero(self):
        """Test rounding zero"""
        assert Money.round(Decimal("0")) == Decimal("0.00")

    def test_round_large_number(self):
        """Test rounding large numbers"""
        assert Money.round(Decimal("10000.126")) == Decimal("10000.13")

    def test_round_small_number(self):
        """Test rounding very small numbers"""
        assert Money.round(Decimal("0.001")) == Decimal("0.00")

    def test_round_half_up_behavior(self):
        """Test ROUND_HALF_UP behavior specifically"""
        assert Money.round(Decimal("0.015")) == Decimal("0.02")
        assert Money.round(Decimal("0.025")) == Decimal("0.03")

    def test_round_negative_values(self):
        """Test rounding negative values"""
        assert Money.round(Decimal("-10.125")) == Decimal("-10.12")


# ======================================================
# EMPLOYEE DATACLASS TESTS
# ======================================================

class TestEmployee:
    """Test Employee dataclass"""

    def test_employee_creation_hourly(self):
        """Test creating an hourly employee"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.00"),
            worked_hours=Decimal("160")
        )
        assert emp.id == "EMP-001"
        assert emp.name == "John Doe"
        assert emp.employee_type == EmployeeType.HOURLY
        assert emp.region == Region.US
        assert emp.hourly_rate == Decimal("25.00")

    def test_employee_creation_salary(self):
        """Test creating a salaried employee"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU,
            monthly_salary=Decimal("5000.00")
        )
        assert emp.employee_type == EmployeeType.SALARY
        assert emp.monthly_salary == Decimal("5000.00")

    def test_employee_creation_contract(self):
        """Test creating a contract employee"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA,
            contract_amount=Decimal("10000.00")
        )
        assert emp.employee_type == EmployeeType.CONTRACT
        assert emp.contract_amount == Decimal("10000.00")

    def test_employee_frozen_immutability(self):
        """Test that Employee is immutable"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US
        )
        with pytest.raises(AttributeError):
            emp.name = "Jane Doe"

    def test_employee_default_zero_values(self):
        """Test that numeric fields default to zero"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US
        )
        assert emp.hourly_rate == Decimal("0")
        assert emp.monthly_salary == Decimal("0")
        assert emp.contract_amount == Decimal("0")
        assert emp.worked_hours == Decimal("0")
        assert emp.overtime_hours == Decimal("0")
        assert emp.weekend_hours == Decimal("0")
        assert emp.performance_bonus == Decimal("0")


# ======================================================
# PAYROLL STRATEGY TESTS
# ======================================================

class TestHourlyStrategy:
    """Test HourlyStrategy calculation"""

    def test_basic_hourly_calculation(self):
        """Test basic hourly pay without overtime or weekend"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.00"),
            worked_hours=Decimal("160")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("4000.00")

    def test_hourly_with_overtime(self):
        """Test hourly pay with overtime (1.5x multiplier)"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.00"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        # 160 * 25 + 10 * 25 * 1.5 = 4000 + 375 = 4375
        assert result == Decimal("4375.00")

    def test_hourly_with_weekend(self):
        """Test hourly pay with weekend hours (2x multiplier)"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.00"),
            worked_hours=Decimal("160"),
            weekend_hours=Decimal("5")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        # 160 * 25 + 5 * 25 * 2 = 4000 + 250 = 4250
        assert result == Decimal("4250.00")

    def test_hourly_with_overtime_and_weekend(self):
        """Test hourly pay with both overtime and weekend"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.00"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        # 160 * 25 + 10 * 25 * 1.5 + 5 * 25 * 2 = 4000 + 375 + 250 = 4625
        assert result == Decimal("4625.00")

    def test_hourly_zero_hours(self):
        """Test hourly calculation with no hours worked"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25.00"),
            worked_hours=Decimal("0")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("0.00")

    def test_hourly_zero_rate(self):
        """Test hourly calculation with zero hourly rate"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("0"),
            worked_hours=Decimal("160")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("0.00")

    def test_hourly_rounding(self):
        """Test that hourly calculation rounds properly"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("10.33"),
            worked_hours=Decimal("3")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        # 3 * 10.33 = 30.99
        assert result == Decimal("30.99")

    def test_hourly_with_fractional_hours(self):
        """Test hourly calculation with fractional hours"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("20.00"),
            worked_hours=Decimal("10.5"),
            overtime_hours=Decimal("2.5")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        # 10.5 * 20 + 2.5 * 20 * 1.5 = 210 + 75 = 285
        assert result == Decimal("285.00")


class TestSalaryStrategy:
    """Test SalaryStrategy calculation"""

    def test_salary_basic(self):
        """Test basic salary calculation"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU,
            monthly_salary=Decimal("5000.00")
        )
        strategy = SalaryStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("5000.00")

    def test_salary_zero(self):
        """Test salary calculation with zero salary"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU,
            monthly_salary=Decimal("0")
        )
        strategy = SalaryStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("0.00")

    def test_salary_ignores_other_fields(self):
        """Test that salary calculation ignores hourly/contract fields"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU,
            monthly_salary=Decimal("5000.00"),
            hourly_rate=Decimal("100.00"),
            worked_hours=Decimal("1000")
        )
        strategy = SalaryStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("5000.00")

    def test_salary_rounding(self):
        """Test that salary is properly rounded"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU,
            monthly_salary=Decimal("5000.125")
        )
        strategy = SalaryStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("5000.12")


class TestContractStrategy:
    """Test ContractStrategy calculation"""

    def test_contract_basic(self):
        """Test basic contract amount calculation"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA,
            contract_amount=Decimal("10000.00")
        )
        strategy = ContractStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("10000.00")

    def test_contract_zero(self):
        """Test contract calculation with zero amount"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA,
            contract_amount=Decimal("0")
        )
        strategy = ContractStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("0.00")

    def test_contract_ignores_other_fields(self):
        """Test that contract calculation ignores hourly/salary fields"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA,
            contract_amount=Decimal("10000.00"),
            hourly_rate=Decimal("100.00"),
            monthly_salary=Decimal("5000.00")
        )
        strategy = ContractStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("10000.00")

    def test_contract_rounding(self):
        """Test that contract amount is properly rounded"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA,
            contract_amount=Decimal("10000.255")
        )
        strategy = ContractStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("10000.26")


# ======================================================
# STRATEGY FACTORY TESTS
# ======================================================

class TestPayrollStrategyFactory:
    """Test PayrollStrategyFactory"""

    def test_factory_creates_hourly_strategy(self):
        """Test factory creates correct strategy for hourly"""
        strategy = PayrollStrategyFactory.create(EmployeeType.HOURLY)
        assert isinstance(strategy, HourlyStrategy)

    def test_factory_creates_salary_strategy(self):
        """Test factory creates correct strategy for salary"""
        strategy = PayrollStrategyFactory.create(EmployeeType.SALARY)
        assert isinstance(strategy, SalaryStrategy)

    def test_factory_creates_contract_strategy(self):
        """Test factory creates correct strategy for contract"""
        strategy = PayrollStrategyFactory.create(EmployeeType.CONTRACT)
        assert isinstance(strategy, ContractStrategy)


# ======================================================
# TAX CALCULATOR TESTS
# ======================================================

class TestTaxCalculator:
    """Test TaxCalculator"""

    def test_us_tax_high_income(self):
        """Test US tax rate for income > $5000 (30%)"""
        calc = TaxCalculator()
        result = calc.calculate(Region.US, Decimal("6000"))
        # 6000 * 0.30 = 1800
        assert result == Decimal("1800.00")

    def test_us_tax_low_income(self):
        """Test US tax rate for income <= $5000 (22%)"""
        calc = TaxCalculator()
        result = calc.calculate(Region.US, Decimal("5000"))
        # 5000 * 0.22 = 1100
        assert result == Decimal("1100.00")

    def test_us_tax_boundary_below(self):
        """Test US tax rate just below $5000 boundary"""
        calc = TaxCalculator()
        result = calc.calculate(Region.US, Decimal("4999.99"))
        # 4999.99 * 0.22 = 1099.9978, rounds to 1100.00
        assert result == Decimal("1100.00")

    def test_us_tax_boundary_above(self):
        """Test US tax rate just above $5000 boundary"""
        calc = TaxCalculator()
        result = calc.calculate(Region.US, Decimal("5000.01"))
        # 5000.01 * 0.30 = 1500.003, rounds to 1500.00
        assert result == Decimal("1500.00")

    def test_eu_tax_rate(self):
        """Test EU tax rate (25%)"""
        calc = TaxCalculator()
        result = calc.calculate(Region.EU, Decimal("1000"))
        assert result == Decimal("250.00")

    def test_ua_tax_rate(self):
        """Test UA tax rate (19.5%)"""
        calc = TaxCalculator()
        result = calc.calculate(Region.UA, Decimal("1000"))
        # 1000 * 0.195 = 195.00
        assert result == Decimal("195.00")

    def test_tax_zero_income(self):
        """Test tax calculation with zero income"""
        calc = TaxCalculator()
        result = calc.calculate(Region.US, Decimal("0"))
        assert result == Decimal("0.00")

    def test_tax_rounding(self):
        """Test that tax is properly rounded"""
        calc = TaxCalculator()
        result = calc.calculate(Region.EU, Decimal("100.01"))
        # 100.01 * 0.25 = 25.0025, rounds to 25.00
        assert result == Decimal("25.00")

    def test_tax_rounding_half_up(self):
        """Test tax rounding uses ROUND_HALF_UP"""
        calc = TaxCalculator()
        result = calc.calculate(Region.EU, Decimal("100.06"))
        # 100.06 * 0.25 = 25.015, rounds to 25.02
        assert result == Decimal("25.02")


# ======================================================
# BONUS CALCULATOR TESTS
# ======================================================

class TestBonusCalculator:
    """Test BonusCalculator"""

    def test_hourly_yearly_bonus_only(self):
        """Test that hourly employees get $200 yearly bonus"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        assert result == Decimal("200.00")

    def test_salary_quarterly_bonus_only(self):
        """Test that salaried employees get $500 quarterly bonus"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        assert result == Decimal("500.00")

    def test_contract_no_bonus(self):
        """Test that contract employees get no bonus"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        assert result == Decimal("0.00")

    def test_hourly_with_performance_bonus(self):
        """Test hourly employee with additional performance bonus"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            performance_bonus=Decimal("100")
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        # 200 + 100 = 300
        assert result == Decimal("300.00")

    def test_salary_with_performance_bonus(self):
        """Test salaried employee with additional performance bonus"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU,
            performance_bonus=Decimal("250")
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        # 500 + 250 = 750
        assert result == Decimal("750.00")

    def test_contract_with_performance_bonus(self):
        """Test contract employee with performance bonus"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA,
            performance_bonus=Decimal("500")
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        # Only performance bonus is applied
        assert result == Decimal("500.00")

    def test_bonus_zero_performance(self):
        """Test bonus with zero performance bonus"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            performance_bonus=Decimal("0")
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        assert result == Decimal("200.00")


# ======================================================
# PAYROLL SERVICE INTEGRATION TESTS
# ======================================================

class TestPayrollService:
    """Test PayrollService end-to-end calculations"""

    def test_hourly_full_calculation(self):
        """Test complete payroll calculation for hourly employee"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("160"),
            overtime_hours=Decimal("10"),
            weekend_hours=Decimal("5"),
            performance_bonus=Decimal("150")
        )
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )
        result = service.calculate_payroll(emp)

        # Gross pay: 160*25 + 10*25*1.5 + 5*25*2 = 4000 + 375 + 250 = 4625
        assert result.gross_pay == Decimal("4625.00")
        # Bonuses: 200 (yearly) + 150 (performance) = 350
        assert result.bonuses == Decimal("350.00")
        # Taxable income: 4625 + 350 = 4975
        # Tax: 4975 * 0.22 = 1094.50
        assert result.taxes == Decimal("1094.50")
        # Net: 4975 - 1094.50 = 3880.50
        assert result.net_pay == Decimal("3880.50")
        assert result.employee_id == "EMP-001"

    def test_salary_full_calculation(self):
        """Test complete payroll calculation for salaried employee"""
        emp = Employee(
            id="EMP-002",
            name="Jane Smith",
            employee_type=EmployeeType.SALARY,
            region=Region.EU,
            monthly_salary=Decimal("5000"),
            performance_bonus=Decimal("200")
        )
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )
        result = service.calculate_payroll(emp)

        # Gross: 5000
        assert result.gross_pay == Decimal("5000.00")
        # Bonuses: 500 (quarterly) + 200 (performance) = 700
        assert result.bonuses == Decimal("700.00")
        # Taxable income: 5000 + 700 = 5700
        # Tax: 5700 * 0.25 = 1425
        assert result.taxes == Decimal("1425.00")
        # Net: 5700 - 1425 = 4275
        assert result.net_pay == Decimal("4275.00")

    def test_contract_full_calculation(self):
        """Test complete payroll calculation for contract employee"""
        emp = Employee(
            id="EMP-003",
            name="Bob Contract",
            employee_type=EmployeeType.CONTRACT,
            region=Region.UA,
            contract_amount=Decimal("10000"),
            performance_bonus=Decimal("500")
        )
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )
        result = service.calculate_payroll(emp)

        # Gross: 10000
        assert result.gross_pay == Decimal("10000.00")
        # Bonuses: 0 (no type bonus) + 500 (performance) = 500
        assert result.bonuses == Decimal("500.00")
        # Taxable income: 10000 + 500 = 10500
        # Tax: 10500 * 0.195 = 2047.50
        assert result.taxes == Decimal("2047.50")
        # Net: 10500 - 2047.50 = 8452.50
        assert result.net_pay == Decimal("8452.50")

    def test_us_tax_threshold_boundary_in_payroll(self):
        """Test US tax threshold crossing in full payroll calculation"""
        # Create scenario where income crosses the $5000 threshold
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("200")
        )
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )
        result = service.calculate_payroll(emp)

        # Gross: 200 * 25 = 5000
        assert result.gross_pay == Decimal("5000.00")
        # Bonuses: 200 (yearly)
        assert result.bonuses == Decimal("200.00")
        # Taxable income: 5000 + 200 = 5200
        # Tax: 5200 * 0.30 = 1560 (uses high rate because > 5000)
        assert result.taxes == Decimal("1560.00")
        # Net: 5200 - 1560 = 3640
        assert result.net_pay == Decimal("3640.00")

    def test_zero_gross_pay(self):
        """Test payroll with zero gross pay"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("0"),
            worked_hours=Decimal("0")
        )
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )
        result = service.calculate_payroll(emp)

        assert result.gross_pay == Decimal("0.00")
        assert result.bonuses == Decimal("200.00")
        assert result.taxes == Decimal("44.00")  # 200 * 0.22
        assert result.net_pay == Decimal("156.00")  # 200 - 44

    def test_large_payroll_calculation(self):
        """Test payroll with large numbers"""
        emp = Employee(
            id="EMP-999",
            name="Executive",
            employee_type=EmployeeType.SALARY,
            region=Region.US,
            monthly_salary=Decimal("50000"),
            performance_bonus=Decimal("10000")
        )
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )
        result = service.calculate_payroll(emp)

        # Gross: 50000
        assert result.gross_pay == Decimal("50000.00")
        # Bonuses: 500 (quarterly) + 10000 (performance) = 10500
        assert result.bonuses == Decimal("10500.00")
        # Taxable income: 50000 + 10500 = 60500
        # Tax: 60500 * 0.30 = 18150
        assert result.taxes == Decimal("18150.00")
        # Net: 60500 - 18150 = 42350
        assert result.net_pay == Decimal("42350.00")


# ======================================================
# REPORT GENERATOR TESTS
# ======================================================

class TestPayrollReportGenerator:
    """Test PayrollReportGenerator"""

    def test_generate_single_employee_report(self):
        """Test report generation for single employee"""
        result = PayrollResult(
            employee_id="EMP-001",
            gross_pay=Decimal("4625.00"),
            bonuses=Decimal("350.00"),
            taxes=Decimal("1094.50"),
            net_pay=Decimal("3880.50")
        )
        report = PayrollReportGenerator.generate([result])

        assert "EMP-001" in report
        assert "4625.00" in report
        assert "350.00" in report
        assert "1094.50" in report
        assert "3880.50" in report
        assert "Gross Pay:" in report
        assert "Bonuses:" in report
        assert "Taxes:" in report
        assert "Net Pay:" in report

    def test_generate_multiple_employee_report(self):
        """Test report generation for multiple employees"""
        results = [
            PayrollResult(
                employee_id="EMP-001",
                gross_pay=Decimal("4625.00"),
                bonuses=Decimal("350.00"),
                taxes=Decimal("1094.50"),
                net_pay=Decimal("3880.50")
            ),
            PayrollResult(
                employee_id="EMP-002",
                gross_pay=Decimal("5000.00"),
                bonuses=Decimal("700.00"),
                taxes=Decimal("1425.00"),
                net_pay=Decimal("4275.00")
            )
        ]
        report = PayrollReportGenerator.generate(results)

        assert "EMP-001" in report
        assert "EMP-002" in report
        assert report.count("Employee ID:") == 2

    def test_generate_empty_report(self):
        """Test report generation with empty list"""
        report = PayrollReportGenerator.generate([])
        assert report == "\n"

    def test_report_format_consistency(self):
        """Test that report maintains consistent formatting"""
        result = PayrollResult(
            employee_id="TEST-123",
            gross_pay=Decimal("1000.00"),
            bonuses=Decimal("100.00"),
            taxes=Decimal("200.00"),
            net_pay=Decimal("900.00")
        )
        report = PayrollReportGenerator.generate([result])

        lines = report.split("\n")
        # Verify the structure contains expected fields
        report_content = "\n".join(lines)
        assert "Employee ID: TEST-123" in report_content
        assert "Gross Pay: $1000.00" in report_content
        assert "Bonuses: $100.00" in report_content
        assert "Taxes: $200.00" in report_content
        assert "Net Pay: $900.00" in report_content


# ======================================================
# EDGE CASES AND LEGACY BEHAVIOR TESTS
# ======================================================

class TestEdgeCases:
    """Test edge cases and legacy behavior"""

    def test_very_small_decimal_values(self):
        """Test handling of very small decimal values"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("0.01"),
            worked_hours=Decimal("1")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        assert result == Decimal("0.01")

    def test_large_decimal_precision(self):
        """Test handling of large numbers with decimal precision"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("999.99"),
            worked_hours=Decimal("1000.99")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        # 999.99 * 1000.99 = 1000989.0101
        assert result == Decimal("1000989.01")

    def test_negative_hours_edge_case(self):
        """Test behavior with negative hours (legacy behavior characterization)"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("25"),
            worked_hours=Decimal("-10")
        )
        strategy = HourlyStrategy()
        result = strategy.calculate(emp)
        # The system calculates with negative values
        assert result == Decimal("-250.00")

    def test_multiple_bonus_accumulation(self):
        """Test that quarterly and yearly bonuses accumulate correctly"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            performance_bonus=Decimal("100")
        )
        calc = BonusCalculator()
        result = calc.calculate(emp)
        # Should have quarterly (0) + yearly (200) + performance (100) = 300
        # Wait, yearly is 200 for hourly, not quarterly
        assert result == Decimal("300.00")

    def test_tax_boundary_exact_5000(self):
        """Test tax calculation at exact $5000 boundary (legacy behavior)"""
        calc = TaxCalculator()
        result = calc.calculate(Region.US, Decimal("5000"))
        # At exactly 5000, should use the <= rate of 22%
        assert result == Decimal("1100.00")

    def test_payroll_result_immutability(self):
        """Test that PayrollResult is immutable"""
        result = PayrollResult(
            employee_id="EMP-001",
            gross_pay=Decimal("4000"),
            bonuses=Decimal("500"),
            taxes=Decimal("1000"),
            net_pay=Decimal("3500")
        )
        with pytest.raises(AttributeError):
            result.employee_id = "EMP-002"

    def test_rounding_cascade_in_payroll(self):
        """Test that rounding at each step produces final result"""
        emp = Employee(
            id="EMP-001",
            name="John Doe",
            employee_type=EmployeeType.HOURLY,
            region=Region.US,
            hourly_rate=Decimal("10.33"),
            worked_hours=Decimal("3.07")
        )
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )
        result = service.calculate_payroll(emp)

        # Verify final net_pay is properly rounded
        assert result.net_pay == (result.gross_pay + result.bonuses - result.taxes)

    def test_all_regions_in_calculation(self):
        """Test payroll calculation works for all regions"""
        for region in [Region.US, Region.EU, Region.UA]:
            emp = Employee(
                id="EMP-001",
                name="John Doe",
                employee_type=EmployeeType.SALARY,
                region=region,
                monthly_salary=Decimal("1000")
            )
            service = PayrollService(
                tax_calculator=TaxCalculator(),
                bonus_calculator=BonusCalculator()
            )
            result = service.calculate_payroll(emp)

            assert result.net_pay > Decimal("0")
            assert result.taxes > Decimal("0")

    def test_all_employee_types_in_calculation(self):
        """Test payroll calculation works for all employee types"""
        employees = [
            Employee(
                id="EMP-001",
                name="John",
                employee_type=EmployeeType.HOURLY,
                region=Region.US,
                hourly_rate=Decimal("25"),
                worked_hours=Decimal("160")
            ),
            Employee(
                id="EMP-002",
                name="Jane",
                employee_type=EmployeeType.SALARY,
                region=Region.EU,
                monthly_salary=Decimal("5000")
            ),
            Employee(
                id="EMP-003",
                name="Bob",
                employee_type=EmployeeType.CONTRACT,
                region=Region.UA,
                contract_amount=Decimal("10000")
            )
        ]
        service = PayrollService(
            tax_calculator=TaxCalculator(),
            bonus_calculator=BonusCalculator()
        )

        for emp in employees:
            result = service.calculate_payroll(emp)
            assert result.employee_id == emp.id
            assert result.net_pay >= Decimal("0")
