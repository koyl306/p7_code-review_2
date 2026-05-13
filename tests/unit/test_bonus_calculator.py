"""
Unit tests for BonusCalculator.calculate() method.

Tests cover:
- Quarterly bonus calculation (salary employees only)
- Yearly bonus calculation (hourly employees only)
- Performance bonus calculation
- Combined bonus calculations
- Different employee types (SALARY, HOURLY, CONTRACT)
- Decimal precision and rounding
- Edge cases (zero bonuses, high bonuses)
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock
from src.payroll import BonusCalculator
from src.constants import (
    SALARY_QUARTERLY_BONUS,
    HOURLY_YEARLY_BONUS,
)


# Mock enums for testing
class EmployeeType:
    """Mock EmployeeType enum."""
    SALARY = "SALARY"
    HOURLY = "HOURLY"
    CONTRACT = "CONTRACT"


@pytest.fixture
def bonus_calculator():
    """Fixture providing an instance of BonusCalculator."""
    return BonusCalculator()


@pytest.fixture
def mock_employee():
    """Fixture providing a mock employee object."""
    employee = Mock()
    employee.employee_type = EmployeeType.SALARY
    employee.performance_bonus = Decimal("0")
    return employee


class TestQuarterlyBonusCalculation:
    """Tests for quarterly bonus calculation."""

    def test_quarterly_bonus_for_salary_employee(self, bonus_calculator, mock_employee):
        """Test quarterly bonus is returned for salary employee."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        assert result == SALARY_QUARTERLY_BONUS

    def test_quarterly_bonus_value_is_500(self, bonus_calculator, mock_employee):
        """Verify quarterly bonus for salary employee is $500."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("500.00")

    def test_quarterly_bonus_not_for_hourly_employee(self, bonus_calculator, mock_employee):
        """Test quarterly bonus is not returned for hourly employee."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        # Should not include quarterly bonus (500)
        assert result != Decimal("500.00")

    def test_quarterly_bonus_not_for_contract_employee(self, bonus_calculator, mock_employee):
        """Test quarterly bonus is not returned for contract employee."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        # Should not include quarterly bonus (500)
        assert result != Decimal("500.00")

    def test_quarterly_bonus_only_for_salary_type(self, bonus_calculator, mock_employee):
        """Test quarterly bonus is exclusively for salary employee type."""
        employee_types = [EmployeeType.SALARY, EmployeeType.HOURLY, EmployeeType.CONTRACT]

        for emp_type in employee_types:
            mock_employee.employee_type = emp_type
            mock_employee.performance_bonus = Decimal("0")

            result = bonus_calculator.calculate(mock_employee)

            if emp_type == EmployeeType.SALARY:
                assert result == Decimal("500.00")
            else:
                assert result != Decimal("500.00")


class TestYearlyBonusCalculation:
    """Tests for yearly bonus calculation."""

    def test_yearly_bonus_for_hourly_employee(self, bonus_calculator, mock_employee):
        """Test yearly bonus is returned for hourly employee."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        assert result == HOURLY_YEARLY_BONUS

    def test_yearly_bonus_value_is_200(self, bonus_calculator, mock_employee):
        """Verify yearly bonus for hourly employee is $200."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("200.00")

    def test_yearly_bonus_not_for_salary_employee(self, bonus_calculator, mock_employee):
        """Test yearly bonus is not returned for salary employee."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        # Should not include yearly bonus (200)
        assert result != Decimal("200.00")

    def test_yearly_bonus_not_for_contract_employee(self, bonus_calculator, mock_employee):
        """Test yearly bonus is not returned for contract employee."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("0")

        result = bonus_calculator.calculate(mock_employee)

        # Should not include yearly bonus (200)
        assert result != Decimal("200.00")

    def test_yearly_bonus_only_for_hourly_type(self, bonus_calculator, mock_employee):
        """Test yearly bonus is exclusively for hourly employee type."""
        employee_types = [EmployeeType.SALARY, EmployeeType.HOURLY, EmployeeType.CONTRACT]

        for emp_type in employee_types:
            mock_employee.employee_type = emp_type
            mock_employee.performance_bonus = Decimal("0")

            result = bonus_calculator.calculate(mock_employee)

            if emp_type == EmployeeType.HOURLY:
                assert result == Decimal("200.00")
            else:
                assert result != Decimal("200.00")


class TestPerformanceBonusCalculation:
    """Tests for performance bonus calculation."""

    def test_performance_bonus_alone(self, bonus_calculator, mock_employee):
        """Test performance bonus calculation without other bonuses."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("500.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("500.00")

    def test_performance_bonus_zero(self, bonus_calculator, mock_employee):
        """Test with zero performance bonus."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("0.00")

    def test_performance_bonus_positive_amount(self, bonus_calculator, mock_employee):
        """Test with positive performance bonus."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("1000.50")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("1000.50")

    def test_performance_bonus_small_amount(self, bonus_calculator, mock_employee):
        """Test with small performance bonus."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("50.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("50.00")

    def test_performance_bonus_large_amount(self, bonus_calculator, mock_employee):
        """Test with large performance bonus."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("10000.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("10000.00")

    def test_performance_bonus_for_all_employee_types(self, bonus_calculator, mock_employee):
        """Test that performance bonus is added for all employee types."""
        performance_amount = Decimal("500.00")
        employee_types = [EmployeeType.SALARY, EmployeeType.HOURLY, EmployeeType.CONTRACT]

        for emp_type in employee_types:
            mock_employee.employee_type = emp_type
            mock_employee.performance_bonus = performance_amount

            result = bonus_calculator.calculate(mock_employee)

            # Performance bonus should be included for all types
            assert performance_amount in [result, result - SALARY_QUARTERLY_BONUS, result - HOURLY_YEARLY_BONUS]


class TestCombinedBonusCalculation:
    """Tests for combined bonus calculations."""

    def test_salary_employee_quarterly_plus_performance(self, bonus_calculator, mock_employee):
        """Test salary employee with quarterly and performance bonuses."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("300.00")

        result = bonus_calculator.calculate(mock_employee)

        expected = SALARY_QUARTERLY_BONUS + Decimal("300.00")
        assert result == expected

    def test_salary_employee_quarterly_with_zero_performance(self, bonus_calculator, mock_employee):
        """Test salary employee with quarterly bonus and zero performance bonus."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == SALARY_QUARTERLY_BONUS

    def test_hourly_employee_yearly_plus_performance(self, bonus_calculator, mock_employee):
        """Test hourly employee with yearly and performance bonuses."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("400.00")

        result = bonus_calculator.calculate(mock_employee)

        expected = HOURLY_YEARLY_BONUS + Decimal("400.00")
        assert result == expected

    def test_hourly_employee_yearly_with_zero_performance(self, bonus_calculator, mock_employee):
        """Test hourly employee with yearly bonus and zero performance bonus."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == HOURLY_YEARLY_BONUS

    def test_contract_employee_performance_only(self, bonus_calculator, mock_employee):
        """Test contract employee receives only performance bonus."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("750.00")

        result = bonus_calculator.calculate(mock_employee)

        # Contract employees should only get performance bonus
        assert result == Decimal("750.00")

    def test_contract_employee_no_bonuses(self, bonus_calculator, mock_employee):
        """Test contract employee with no bonuses."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("0.00")


class TestBonusCalculationSalaryVsHourly:
    """Tests comparing salary and hourly employee bonus structures."""

    def test_salary_receives_quarterly_not_yearly(self, bonus_calculator, mock_employee):
        """Test salary employee gets quarterly but not yearly bonus."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        # Should have quarterly (500), not yearly (200)
        assert result == Decimal("500.00")
        assert result != Decimal("200.00")

    def test_hourly_receives_yearly_not_quarterly(self, bonus_calculator, mock_employee):
        """Test hourly employee gets yearly but not quarterly bonus."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        # Should have yearly (200), not quarterly (500)
        assert result == Decimal("200.00")
        assert result != Decimal("500.00")

    def test_salary_has_higher_base_bonus_than_hourly(self, bonus_calculator, mock_employee):
        """Test that salary base bonus is higher than hourly base bonus."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("0.00")
        salary_bonus = bonus_calculator.calculate(mock_employee)

        mock_employee.employee_type = EmployeeType.HOURLY
        hourly_bonus = bonus_calculator.calculate(mock_employee)

        assert salary_bonus > hourly_bonus


class TestBonusCalculationDecimalPrecision:
    """Tests for decimal precision and rounding in bonus calculations."""

    def test_bonus_with_precise_decimals(self, bonus_calculator, mock_employee):
        """Test bonus calculation with precise decimal values."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("123.45")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("123.45")

    def test_combined_bonus_with_decimal_precision(self, bonus_calculator, mock_employee):
        """Test combined bonus with decimal precision."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("123.45")

        result = bonus_calculator.calculate(mock_employee)

        expected = Decimal("500.00") + Decimal("123.45")
        assert result == expected

    def test_bonus_rounding_to_cents(self, bonus_calculator, mock_employee):
        """Test that bonus is rounded to nearest cent."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("123.455")

        result = bonus_calculator.calculate(mock_employee)

        # Should round to two decimal places
        assert result == Decimal("123.46")

    def test_bonus_with_many_decimal_places(self, bonus_calculator, mock_employee):
        """Test bonus calculation with many decimal places."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("234.567891")

        result = bonus_calculator.calculate(mock_employee)

        # Should round to two decimal places
        expected = (Decimal("500.00") + Decimal("234.567891")).quantize(Decimal("0.01"))
        assert result == expected

    def test_bonus_fractional_cents_rounding(self, bonus_calculator, mock_employee):
        """Test bonus rounding with fractional cents."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("100.125")

        result = bonus_calculator.calculate(mock_employee)

        # 200 + 100.125 = 300.125 -> rounds to 300.13
        assert result == Decimal("300.13")


class TestBonusCalculationEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_bonus_with_zero_all_components(self, bonus_calculator, mock_employee):
        """Test bonus calculation with all components zero."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("0.00")

    def test_bonus_with_very_large_performance_bonus(self, bonus_calculator, mock_employee):
        """Test bonus calculation with very large performance bonus."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("50000.00")

        result = bonus_calculator.calculate(mock_employee)

        expected = Decimal("500.00") + Decimal("50000.00")
        assert result == expected

    def test_bonus_with_very_small_performance_bonus(self, bonus_calculator, mock_employee):
        """Test bonus calculation with very small performance bonus."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("0.01")

        result = bonus_calculator.calculate(mock_employee)

        expected = Decimal("200.00") + Decimal("0.01")
        assert result == expected

    def test_bonus_with_negative_performance_bonus(self, bonus_calculator, mock_employee):
        """Test bonus calculation with negative performance bonus (penalty)."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("-100.00")

        result = bonus_calculator.calculate(mock_employee)

        expected = Decimal("500.00") - Decimal("100.00")
        assert result == expected

    def test_bonus_resulting_in_zero_or_negative(self, bonus_calculator, mock_employee):
        """Test bonus that results in zero or negative total."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("-300.00")

        result = bonus_calculator.calculate(mock_employee)

        expected = Decimal("200.00") - Decimal("300.00")
        assert result == expected


class TestBonusReturnTypeAndConsistency:
    """Tests for return type and consistency of bonus calculations."""

    def test_bonus_calculate_returns_decimal_type(self, bonus_calculator, mock_employee):
        """Test that calculate() returns a Decimal type."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("500.00")

        result = bonus_calculator.calculate(mock_employee)

        assert isinstance(result, Decimal)

    def test_bonus_deterministic_results(self, bonus_calculator, mock_employee):
        """Test that identical inputs always produce identical outputs."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("250.00")

        results = [bonus_calculator.calculate(mock_employee) for _ in range(5)]

        expected = Decimal("750.00")
        assert all(r == expected for r in results)

    def test_bonus_multiple_calls_same_result(self, bonus_calculator, mock_employee):
        """Test that multiple calls with same data return same result."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("150.00")

        result1 = bonus_calculator.calculate(mock_employee)
        result2 = bonus_calculator.calculate(mock_employee)
        result3 = bonus_calculator.calculate(mock_employee)

        assert result1 == result2 == result3

    def test_bonus_does_not_modify_employee_data(self, bonus_calculator, mock_employee):
        """Test that calculate() does not modify employee data."""
        original_type = mock_employee.employee_type
        original_performance = mock_employee.performance_bonus

        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("300.00")

        bonus_calculator.calculate(mock_employee)

        # Employee data should remain unchanged
        assert mock_employee.employee_type == EmployeeType.SALARY
        assert mock_employee.performance_bonus == Decimal("300.00")


class TestBonusCalculationRealWorldScenarios:
    """Tests for real-world bonus scenarios."""

    def test_salary_employee_standard_bonus(self, bonus_calculator, mock_employee):
        """Test standard bonus for salary employee."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("200.00")

        result = bonus_calculator.calculate(mock_employee)

        # $500 quarterly + $200 performance = $700
        assert result == Decimal("700.00")

    def test_hourly_employee_standard_bonus(self, bonus_calculator, mock_employee):
        """Test standard bonus for hourly employee."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("150.00")

        result = bonus_calculator.calculate(mock_employee)

        # $200 yearly + $150 performance = $350
        assert result == Decimal("350.00")

    def test_contractor_excellent_performance(self, bonus_calculator, mock_employee):
        """Test contractor with excellent performance bonus."""
        mock_employee.employee_type = EmployeeType.CONTRACT
        mock_employee.performance_bonus = Decimal("5000.00")

        result = bonus_calculator.calculate(mock_employee)

        assert result == Decimal("5000.00")

    def test_salary_employee_no_performance(self, bonus_calculator, mock_employee):
        """Test salary employee with no performance bonus."""
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = Decimal("0.00")

        result = bonus_calculator.calculate(mock_employee)

        # Only $500 quarterly bonus
        assert result == Decimal("500.00")

    def test_hourly_employee_excellent_performance(self, bonus_calculator, mock_employee):
        """Test hourly employee with excellent performance."""
        mock_employee.employee_type = EmployeeType.HOURLY
        mock_employee.performance_bonus = Decimal("1000.00")

        result = bonus_calculator.calculate(mock_employee)

        # $200 yearly + $1000 performance = $1200
        assert result == Decimal("1200.00")

    def test_employee_bonus_comparison_by_type(self, bonus_calculator, mock_employee):
        """Compare bonuses across employee types with same performance."""
        performance = Decimal("100.00")

        # Salary employee
        mock_employee.employee_type = EmployeeType.SALARY
        mock_employee.performance_bonus = performance
        salary_bonus = bonus_calculator.calculate(mock_employee)

        # Hourly employee
        mock_employee.employee_type = EmployeeType.HOURLY
        hourly_bonus = bonus_calculator.calculate(mock_employee)

        # Contract employee
        mock_employee.employee_type = EmployeeType.CONTRACT
        contract_bonus = bonus_calculator.calculate(mock_employee)

        # Salary: 500 + 100 = 600
        assert salary_bonus == Decimal("600.00")
        # Hourly: 200 + 100 = 300
        assert hourly_bonus == Decimal("300.00")
        # Contract: 0 + 100 = 100
        assert contract_bonus == Decimal("100.00")


class TestBonusCalculationEmployeeTypeLogic:
    """Tests for employee type bonus logic."""

    def test_each_employee_type_gets_correct_bonuses(self, bonus_calculator, mock_employee):
        """Test that each employee type receives correct bonus combination."""
        scenarios = [
            (EmployeeType.SALARY, Decimal("500.00"), Decimal("0.00")),    # quarterly, no yearly
            (EmployeeType.HOURLY, Decimal("0.00"), Decimal("200.00")),    # no quarterly, yearly
            (EmployeeType.CONTRACT, Decimal("0.00"), Decimal("0.00")),    # no quarterly, no yearly
        ]

        mock_employee.performance_bonus = Decimal("0.00")

        for emp_type, expected_quarterly_effect, expected_yearly_effect in scenarios:
            mock_employee.employee_type = emp_type
            result = bonus_calculator.calculate(mock_employee)
            expected = expected_quarterly_effect + expected_yearly_effect
            assert result == expected

    def test_bonus_type_exclusivity(self, bonus_calculator, mock_employee):
        """Test that bonus types are exclusive by employee type."""
        mock_employee.performance_bonus = Decimal("0.00")

        # Salary employee should not get yearly bonus
        mock_employee.employee_type = EmployeeType.SALARY
        salary_result = bonus_calculator.calculate(mock_employee)
        assert salary_result == Decimal("500.00")
        assert HOURLY_YEARLY_BONUS not in [salary_result]

        # Hourly employee should not get quarterly bonus
        mock_employee.employee_type = EmployeeType.HOURLY
        hourly_result = bonus_calculator.calculate(mock_employee)
        assert hourly_result == Decimal("200.00")
        assert SALARY_QUARTERLY_BONUS not in [hourly_result]
