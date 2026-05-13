"""
Unit tests for SalaryStrategy.calculate() method.

Tests cover:
- Standard monthly salary return
- Various salary amounts (low, standard, high)
- Decimal precision and rounding
- Edge cases (zero salary, very high salary)
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock
from src.strategies import SalaryStrategy


@pytest.fixture
def salary_strategy():
    """Fixture providing an instance of SalaryStrategy."""
    return SalaryStrategy()


@pytest.fixture
def mock_employee():
    """Fixture providing a mock employee object with monthly_salary."""
    employee = Mock()
    employee.monthly_salary = Decimal("0")
    return employee


class TestBasicSalaryCalculation:
    """Tests for basic salary calculation."""

    def test_calculate_returns_monthly_salary(self, salary_strategy, mock_employee):
        """Test that calculate() returns the monthly salary."""
        mock_employee.monthly_salary = Decimal("3000.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("3000.00")

    def test_calculate_returns_exact_salary_amount(self, salary_strategy, mock_employee):
        """Test that the exact salary amount is returned without modification."""
        mock_employee.monthly_salary = Decimal("5000.50")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("5000.50")

    def test_calculate_with_standard_monthly_salary(self, salary_strategy, mock_employee):
        """Test with a standard full-time monthly salary."""
        mock_employee.monthly_salary = Decimal("4500.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("4500.00")

    def test_calculate_with_different_salary_amounts(self, salary_strategy, mock_employee):
        """Test calculate() with various salary amounts."""
        test_salaries = [
            Decimal("2000.00"),
            Decimal("3500.75"),
            Decimal("6000.00"),
            Decimal("10000.50"),
        ]

        for salary in test_salaries:
            mock_employee.monthly_salary = salary
            result = salary_strategy.calculate(mock_employee)
            assert result == salary


class TestSalaryAmountVariations:
    """Tests for different salary amounts and ranges."""

    def test_calculate_with_low_salary(self, salary_strategy, mock_employee):
        """Test with a low monthly salary."""
        mock_employee.monthly_salary = Decimal("1500.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("1500.00")

    def test_calculate_with_minimum_wage_level_salary(self, salary_strategy, mock_employee):
        """Test with minimum wage level monthly salary."""
        mock_employee.monthly_salary = Decimal("1200.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("1200.00")

    def test_calculate_with_average_salary(self, salary_strategy, mock_employee):
        """Test with average monthly salary."""
        mock_employee.monthly_salary = Decimal("3500.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("3500.00")

    def test_calculate_with_high_salary(self, salary_strategy, mock_employee):
        """Test with a high monthly salary."""
        mock_employee.monthly_salary = Decimal("15000.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("15000.00")

    def test_calculate_with_very_high_salary(self, salary_strategy, mock_employee):
        """Test with a very high monthly salary."""
        mock_employee.monthly_salary = Decimal("50000.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("50000.00")

    def test_calculate_with_executive_level_salary(self, salary_strategy, mock_employee):
        """Test with executive level monthly salary."""
        mock_employee.monthly_salary = Decimal("100000.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("100000.00")


class TestDecimalPrecision:
    """Tests for decimal precision and rounding behavior."""

    def test_calculate_with_two_decimal_places(self, salary_strategy, mock_employee):
        """Test with standard two decimal place precision."""
        mock_employee.monthly_salary = Decimal("3500.50")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("3500.50")

    def test_calculate_with_one_decimal_place(self, salary_strategy, mock_employee):
        """Test with one decimal place precision."""
        mock_employee.monthly_salary = Decimal("3500.5")

        result = salary_strategy.calculate(mock_employee)

        # Money.round should handle conversion to two decimal places
        assert result == Decimal("3500.50")

    def test_calculate_with_whole_number_salary(self, salary_strategy, mock_employee):
        """Test with whole number salary (no decimal places)."""
        mock_employee.monthly_salary = Decimal("3500")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("3500.00")

    def test_calculate_preserves_decimal_precision(self, salary_strategy, mock_employee):
        """Test that decimal precision is preserved in calculation."""
        mock_employee.monthly_salary = Decimal("4250.75")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("4250.75")

    def test_calculate_with_cent_precision(self, salary_strategy, mock_employee):
        """Test with various cent values."""
        test_salaries = [
            Decimal("3000.01"),
            Decimal("3000.10"),
            Decimal("3000.99"),
            Decimal("3000.05"),
        ]

        for salary in test_salaries:
            mock_employee.monthly_salary = salary
            result = salary_strategy.calculate(mock_employee)
            assert result == salary


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_calculate_with_zero_salary(self, salary_strategy, mock_employee):
        """Test with zero monthly salary."""
        mock_employee.monthly_salary = Decimal("0.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("0.00")

    def test_calculate_with_zero_salary_no_decimals(self, salary_strategy, mock_employee):
        """Test with zero salary without decimal notation."""
        mock_employee.monthly_salary = Decimal("0")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("0.00")

    def test_calculate_with_very_small_salary(self, salary_strategy, mock_employee):
        """Test with very small salary amount."""
        mock_employee.monthly_salary = Decimal("0.01")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("0.01")

    def test_calculate_with_large_salary_amount(self, salary_strategy, mock_employee):
        """Test with very large salary amount."""
        mock_employee.monthly_salary = Decimal("999999.99")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("999999.99")

    def test_calculate_with_million_dollar_salary(self, salary_strategy, mock_employee):
        """Test with million dollar monthly salary."""
        mock_employee.monthly_salary = Decimal("1000000.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("1000000.00")


class TestSalaryRounding:
    """Tests for rounding behavior when Money.round is applied."""

    def test_calculate_rounds_salary_to_cents(self, salary_strategy, mock_employee):
        """Test that salary is rounded to nearest cent."""
        # Test with three decimal places - should round to two
        mock_employee.monthly_salary = Decimal("3500.125")

        result = salary_strategy.calculate(mock_employee)

        # Money.round uses ROUND_HALF_UP, so .125 rounds to .13
        assert result == Decimal("3500.13")

    def test_calculate_rounds_down_correctly(self, salary_strategy, mock_employee):
        """Test rounding down of fractional cents."""
        mock_employee.monthly_salary = Decimal("3500.121")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("3500.12")

    def test_calculate_rounds_up_correctly(self, salary_strategy, mock_employee):
        """Test rounding up of fractional cents."""
        mock_employee.monthly_salary = Decimal("3500.129")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("3500.13")

    def test_calculate_rounds_half_up(self, salary_strategy, mock_employee):
        """Test ROUND_HALF_UP behavior for .5 values."""
        mock_employee.monthly_salary = Decimal("3500.125")

        result = salary_strategy.calculate(mock_employee)

        # ROUND_HALF_UP rounds .125 to .13
        assert result == Decimal("3500.13")

    def test_calculate_handles_negative_salary(self, salary_strategy, mock_employee):
        """Test with negative salary (e.g., refund or deduction scenario)."""
        mock_employee.monthly_salary = Decimal("-500.00")

        result = salary_strategy.calculate(mock_employee)

        assert result == Decimal("-500.00")


class TestReturnTypeAndImmutability:
    """Tests for return type and data integrity."""

    def test_calculate_returns_decimal_type(self, salary_strategy, mock_employee):
        """Test that calculate() returns a Decimal type."""
        mock_employee.monthly_salary = Decimal("3000.00")

        result = salary_strategy.calculate(mock_employee)

        assert isinstance(result, Decimal)

    def test_calculate_does_not_modify_employee_salary(self, salary_strategy, mock_employee):
        """Test that calculate() does not modify the employee's monthly_salary."""
        original_salary = Decimal("3000.00")
        mock_employee.monthly_salary = original_salary

        salary_strategy.calculate(mock_employee)

        assert mock_employee.monthly_salary == original_salary

    def test_calculate_multiple_calls_return_same_value(self, salary_strategy, mock_employee):
        """Test that multiple calls with same salary return identical results."""
        mock_employee.monthly_salary = Decimal("3500.50")

        result1 = salary_strategy.calculate(mock_employee)
        result2 = salary_strategy.calculate(mock_employee)
        result3 = salary_strategy.calculate(mock_employee)

        assert result1 == result2 == result3

    def test_calculate_independence_between_employees(self, salary_strategy):
        """Test that calculations for different employees are independent."""
        employee1 = Mock()
        employee1.monthly_salary = Decimal("3000.00")

        employee2 = Mock()
        employee2.monthly_salary = Decimal("5000.00")

        result1 = salary_strategy.calculate(employee1)
        result2 = salary_strategy.calculate(employee2)

        assert result1 == Decimal("3000.00")
        assert result2 == Decimal("5000.00")


class TestComparisonWithHourlyAndContractStrategies:
    """Tests comparing SalaryStrategy with other strategies for consistency."""

    def test_salary_strategy_simplicity(self, salary_strategy, mock_employee):
        """Test that SalaryStrategy is simpler than hourly strategy."""
        mock_employee.monthly_salary = Decimal("4000.00")

        # SalaryStrategy should just return the monthly salary
        result = salary_strategy.calculate(mock_employee)

        assert result == mock_employee.monthly_salary

    def test_salary_strategy_no_multiplication(self, salary_strategy, mock_employee):
        """Test that SalaryStrategy doesn't perform multiplication like HourlyStrategy."""
        mock_employee.monthly_salary = Decimal("3500.00")

        result = salary_strategy.calculate(mock_employee)

        # Should be exactly the salary, not multiplied by hours or rates
        assert result == Decimal("3500.00")
