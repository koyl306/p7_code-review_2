from abc import ABC, abstractmethod
from decimal import Decimal


class PayrollStrategy(ABC):

    @abstractmethod
    def calculate(self, employee):
        pass

class HourlyStrategy(PayrollStrategy):

    def calculate(self, employee):

        base_pay = self._calculate_base_pay(employee)

        overtime_pay = self._calculate_overtime_pay(employee)

        weekend_pay = self._calculate_weekend_pay(employee)

        total = (
            base_pay
            + overtime_pay
            + weekend_pay
        )

        return Money.round(total)

    def _calculate_base_pay(self, employee):
        return (
            employee.hourly_rate
            * employee.worked_hours
        )

    def _calculate_overtime_pay(self, employee):
        return (
            employee.hourly_rate
            * employee.overtime_hours
            * OVERTIME_MULTIPLIER
        )

    def _calculate_weekend_pay(self, employee):
        return (
            employee.hourly_rate
            * employee.weekend_hours
            * WEEKEND_MULTIPLIER
        )