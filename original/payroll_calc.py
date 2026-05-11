from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum


# ======================================================
# ENUMS
# ======================================================

class EmployeeType(Enum):
    HOURLY = "HOURLY"
    SALARY = "SALARY"
    CONTRACT = "CONTRACT"


class Region(Enum):
    US = "US"
    EU = "EU"
    UA = "UA"


# ======================================================
# MONEY UTILITIES
# ======================================================

class Money:
    @staticmethod
    def round(value: Decimal) -> Decimal:
        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )


# ======================================================
# DATA MODELS
# ======================================================

@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    employee_type: EmployeeType
    region: Region

    hourly_rate: Decimal = Decimal("0")
    monthly_salary: Decimal = Decimal("0")
    contract_amount: Decimal = Decimal("0")

    worked_hours: Decimal = Decimal("0")
    overtime_hours: Decimal = Decimal("0")
    weekend_hours: Decimal = Decimal("0")

    performance_bonus: Decimal = Decimal("0")


@dataclass(frozen=True)
class PayrollResult:
    employee_id: str
    gross_pay: Decimal
    bonuses: Decimal
    taxes: Decimal
    net_pay: Decimal


# ======================================================
# STRATEGY PATTERN
# ======================================================

class PayrollStrategy(ABC):

    @abstractmethod
    def calculate(self, employee: Employee) -> Decimal:
        pass


class HourlyStrategy(PayrollStrategy):

    def calculate(self, employee: Employee) -> Decimal:
        base_pay = employee.hourly_rate * employee.worked_hours

        overtime_pay = (
            employee.hourly_rate
            * employee.overtime_hours
            * Decimal("1.5")
        )

        weekend_pay = (
            employee.hourly_rate
            * employee.weekend_hours
            * Decimal("2")
        )

        total = base_pay + overtime_pay + weekend_pay

        return Money.round(total)


class SalaryStrategy(PayrollStrategy):

    def calculate(self, employee: Employee) -> Decimal:
        return Money.round(employee.monthly_salary)


class ContractStrategy(PayrollStrategy):

    def calculate(self, employee: Employee) -> Decimal:
        return Money.round(employee.contract_amount)


# ======================================================
# TAX CALCULATOR
# ======================================================

class TaxCalculator:

    def calculate(
        self,
        region: Region,
        taxable_income: Decimal
    ) -> Decimal:

        tax_rate = self._get_tax_rate(region, taxable_income)

        taxes = taxable_income * tax_rate

        return Money.round(taxes)

    def _get_tax_rate(
        self,
        region: Region,
        income: Decimal
    ) -> Decimal:

        if region == Region.US:
            return Decimal("0.30") if income > Decimal("5000") else Decimal("0.22")

        if region == Region.EU:
            return Decimal("0.25")

        if region == Region.UA:
            return Decimal("0.195")

        return Decimal("0.20")


# ======================================================
# BONUS CALCULATOR
# ======================================================

class BonusCalculator:

    def calculate(self, employee: Employee) -> Decimal:
        quarterly_bonus = self._quarterly_bonus(employee)
        yearly_bonus = self._yearly_bonus(employee)

        total_bonus = (
            quarterly_bonus
            + yearly_bonus
            + employee.performance_bonus
        )

        return Money.round(total_bonus)

    def _quarterly_bonus(self, employee: Employee) -> Decimal:
        if employee.employee_type == EmployeeType.SALARY:
            return Decimal("500")

        return Decimal("0")

    def _yearly_bonus(self, employee: Employee) -> Decimal:
        if employee.employee_type == EmployeeType.HOURLY:
            return Decimal("200")

        return Decimal("0")


# ======================================================
# STRATEGY FACTORY
# ======================================================

class PayrollStrategyFactory:

    @staticmethod
    def create(employee_type: EmployeeType) -> PayrollStrategy:

        strategies = {
            EmployeeType.HOURLY: HourlyStrategy(),
            EmployeeType.SALARY: SalaryStrategy(),
            EmployeeType.CONTRACT: ContractStrategy(),
        }

        return strategies[employee_type]


# ======================================================
# PAYROLL SERVICE
# ======================================================

class PayrollService:

    def __init__(
        self,
        tax_calculator: TaxCalculator,
        bonus_calculator: BonusCalculator
    ):
        self.tax_calculator = tax_calculator
        self.bonus_calculator = bonus_calculator

    def calculate_payroll(
        self,
        employee: Employee
    ) -> PayrollResult:

        strategy = PayrollStrategyFactory.create(
            employee.employee_type
        )

        gross_pay = strategy.calculate(employee)

        bonuses = self.bonus_calculator.calculate(employee)

        taxable_income = gross_pay + bonuses

        taxes = self.tax_calculator.calculate(
            employee.region,
            taxable_income
        )

        net_pay = taxable_income - taxes

        return PayrollResult(
            employee_id=employee.id,
            gross_pay=gross_pay,
            bonuses=bonuses,
            taxes=taxes,
            net_pay=Money.round(net_pay)
        )


# ======================================================
# REPORT GENERATOR
# ======================================================

class PayrollReportGenerator:

    @staticmethod
    def generate(results: list[PayrollResult]) -> str:

        report_lines = []

        for result in results:
            report_lines.append(
                f"""
Employee ID: {result.employee_id}
Gross Pay: ${result.gross_pay}
Bonuses: ${result.bonuses}
Taxes: ${result.taxes}
Net Pay: ${result.net_pay}
----------------------------------------
"""
            )

        return "\n".join(report_lines)


# ======================================================
# USAGE EXAMPLE
# ======================================================

employee = Employee(
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

payroll_service = PayrollService(
    tax_calculator=TaxCalculator(),
    bonus_calculator=BonusCalculator()
)

payroll_result = payroll_service.calculate_payroll(employee)

report = PayrollReportGenerator.generate(
    [payroll_result]
)

print(report)