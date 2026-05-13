from abc import ABC, abstractmethod
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
            return SALARY_QUARTERLY_BONUS

        return Decimal("0")

    def _yearly_bonus(self, employee: Employee) -> Decimal:
        if employee.employee_type == EmployeeType.HOURLY:
            return HOURLY_YEARLY_BONUS

        return Decimal("0")


class PayrollStrategyFactory:

    @staticmethod
    def create(employee_type: EmployeeType) -> PayrollStrategy:

        strategies = {
            EmployeeType.HOURLY: HourlyStrategy(),
            EmployeeType.SALARY: SalaryStrategy(),
            EmployeeType.CONTRACT: ContractStrategy(),
        }

        return strategies[employee_type]


class PayrollService:

    def __init__(
        self,
        strategies,
        tax_calculator,
        bonus_calculator
    ):
        self.strategies = strategies
        self.tax_calculator = tax_calculator
        self.bonus_calculator = bonus_calculator