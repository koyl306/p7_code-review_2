from abc import ABC, abstractmethod
from decimal import Decimal


class PayrollStrategy(ABC):

    @abstractmethod
    def calculate(self, employee):
        pass