"""
Unit tests for ContractStrategy.calculate() method.

Tests cover:
- Standard contract payment return
- Various contract payment amounts (small, medium, large)
- Decimal precision and rounding
- Edge cases (zero contract, very high contract amounts)
- Contract payment verification across different scenarios
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock
from src.strategies import ContractStrategy


@pytest.fixture
def contract_strategy():
    """Fixture providing an instance of ContractStrategy."""
    return ContractStrategy()


@pytest.fixture
def mock_employee():
    """Fixture providing a mock employee object with contract_amount."""
    employee = Mock()
    employee.contract_amount = Decimal("0")
    return employee


class TestBasicContractCalculation:
    """Tests for basic contract payment calculation."""

    def test_calculate_returns_contract_amount(self, contract_strategy, mock_employee):
        """Test that calculate() returns the contract amount."""
        mock_employee.contract_amount = Decimal("5000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("5000.00")

    def test_calculate_returns_exact_contract_amount(self, contract_strategy, mock_employee):
        """Test that the exact contract amount is returned without modification."""
        mock_employee.contract_amount = Decimal("7500.75")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("7500.75")

    def test_calculate_with_typical_project_contract(self, contract_strategy, mock_employee):
        """Test with a typical project-based contract amount."""
        mock_employee.contract_amount = Decimal("10000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("10000.00")

    def test_calculate_with_different_contract_amounts(self, contract_strategy, mock_employee):
        """Test calculate() with various contract payment amounts."""
        test_contracts = [
            Decimal("2500.00"),
            Decimal("5000.50"),
            Decimal("8750.00"),
            Decimal("15000.25"),
        ]

        for contract_amount in test_contracts:
            mock_employee.contract_amount = contract_amount
            result = contract_strategy.calculate(mock_employee)
            assert result == contract_amount


class TestContractAmountVariations:
    """Tests for different contract payment amounts and ranges."""

    def test_calculate_with_small_contract(self, contract_strategy, mock_employee):
        """Test with a small contract amount."""
        mock_employee.contract_amount = Decimal("1000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("1000.00")

    def test_calculate_with_freelance_hourly_equivalent_contract(self, contract_strategy, mock_employee):
        """Test with freelance hourly equivalent contract."""
        mock_employee.contract_amount = Decimal("3000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("3000.00")

    def test_calculate_with_medium_contract(self, contract_strategy, mock_employee):
        """Test with medium contract amount."""
        mock_employee.contract_amount = Decimal("7500.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("7500.00")

    def test_calculate_with_large_contract(self, contract_strategy, mock_employee):
        """Test with a large contract amount."""
        mock_employee.contract_amount = Decimal("25000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("25000.00")

    def test_calculate_with_enterprise_contract(self, contract_strategy, mock_employee):
        """Test with enterprise-level contract amount."""
        mock_employee.contract_amount = Decimal("100000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("100000.00")

    def test_calculate_with_major_project_contract(self, contract_strategy, mock_employee):
        """Test with major project contract amount."""
        mock_employee.contract_amount = Decimal("500000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("500000.00")


class TestDecimalPrecisionInContracts:
    """Tests for decimal precision and rounding behavior in contract payments."""

    def test_calculate_with_two_decimal_places(self, contract_strategy, mock_employee):
        """Test with standard two decimal place precision."""
        mock_employee.contract_amount = Decimal("5000.50")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("5000.50")

    def test_calculate_with_one_decimal_place(self, contract_strategy, mock_employee):
        """Test with one decimal place precision."""
        mock_employee.contract_amount = Decimal("5000.5")

        result = contract_strategy.calculate(mock_employee)

        # Money.round should handle conversion to two decimal places
        assert result == Decimal("5000.50")

    def test_calculate_with_whole_number_contract(self, contract_strategy, mock_employee):
        """Test with whole number contract (no decimal places)."""
        mock_employee.contract_amount = Decimal("5000")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("5000.00")

    def test_calculate_preserves_decimal_precision(self, contract_strategy, mock_employee):
        """Test that decimal precision is preserved in calculation."""
        mock_employee.contract_amount = Decimal("7250.75")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("7250.75")

    def test_calculate_with_various_cent_values(self, contract_strategy, mock_employee):
        """Test with various cent values."""
        test_contracts = [
            Decimal("5000.01"),
            Decimal("5000.10"),
            Decimal("5000.99"),
            Decimal("5000.05"),
        ]

        for contract_amount in test_contracts:
            mock_employee.contract_amount = contract_amount
            result = contract_strategy.calculate(mock_employee)
            assert result == contract_amount


class TestContractRounding:
    """Tests for rounding behavior when Money.round is applied."""

    def test_calculate_rounds_contract_to_cents(self, contract_strategy, mock_employee):
        """Test that contract amount is rounded to nearest cent."""
        # Test with three decimal places - should round to two
        mock_employee.contract_amount = Decimal("5000.125")

        result = contract_strategy.calculate(mock_employee)

        # Money.round uses ROUND_HALF_UP, so .125 rounds to .13
        assert result == Decimal("5000.13")

    def test_calculate_rounds_down_correctly(self, contract_strategy, mock_employee):
        """Test rounding down of fractional cents."""
        mock_employee.contract_amount = Decimal("5000.121")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("5000.12")

    def test_calculate_rounds_up_correctly(self, contract_strategy, mock_employee):
        """Test rounding up of fractional cents."""
        mock_employee.contract_amount = Decimal("5000.129")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("5000.13")

    def test_calculate_rounds_half_up(self, contract_strategy, mock_employee):
        """Test ROUND_HALF_UP behavior for .5 values."""
        mock_employee.contract_amount = Decimal("5000.125")

        result = contract_strategy.calculate(mock_employee)

        # ROUND_HALF_UP rounds .125 to .13
        assert result == Decimal("5000.13")

    def test_calculate_with_many_decimal_places(self, contract_strategy, mock_employee):
        """Test with many decimal places to verify rounding."""
        mock_employee.contract_amount = Decimal("5000.123456789")

        result = contract_strategy.calculate(mock_employee)

        # Should round to two decimal places
        assert result == Decimal("5000.12")


class TestEdgeCasesForContracts:
    """Tests for edge cases and boundary conditions."""

    def test_calculate_with_zero_contract(self, contract_strategy, mock_employee):
        """Test with zero contract amount."""
        mock_employee.contract_amount = Decimal("0.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("0.00")

    def test_calculate_with_zero_contract_no_decimals(self, contract_strategy, mock_employee):
        """Test with zero contract without decimal notation."""
        mock_employee.contract_amount = Decimal("0")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("0.00")

    def test_calculate_with_very_small_contract(self, contract_strategy, mock_employee):
        """Test with very small contract amount (1 cent)."""
        mock_employee.contract_amount = Decimal("0.01")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("0.01")

    def test_calculate_with_minimum_contract(self, contract_strategy, mock_employee):
        """Test with minimum viable contract amount."""
        mock_employee.contract_amount = Decimal("100.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("100.00")

    def test_calculate_with_large_contract_amount(self, contract_strategy, mock_employee):
        """Test with very large contract amount."""
        mock_employee.contract_amount = Decimal("999999.99")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("999999.99")

    def test_calculate_with_multi_million_contract(self, contract_strategy, mock_employee):
        """Test with multi-million dollar contract."""
        mock_employee.contract_amount = Decimal("10000000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("10000000.00")

    def test_calculate_with_negative_contract(self, contract_strategy, mock_employee):
        """Test with negative contract amount (refund or adjustment scenario)."""
        mock_employee.contract_amount = Decimal("-1000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("-1000.00")


class TestReturnTypeAndImmutability:
    """Tests for return type and data integrity."""

    def test_calculate_returns_decimal_type(self, contract_strategy, mock_employee):
        """Test that calculate() returns a Decimal type."""
        mock_employee.contract_amount = Decimal("5000.00")

        result = contract_strategy.calculate(mock_employee)

        assert isinstance(result, Decimal)

    def test_calculate_does_not_modify_employee_contract(self, contract_strategy, mock_employee):
        """Test that calculate() does not modify the employee's contract_amount."""
        original_contract = Decimal("5000.00")
        mock_employee.contract_amount = original_contract

        contract_strategy.calculate(mock_employee)

        assert mock_employee.contract_amount == original_contract

    def test_calculate_multiple_calls_return_same_value(self, contract_strategy, mock_employee):
        """Test that multiple calls with same contract return identical results."""
        mock_employee.contract_amount = Decimal("7500.50")

        result1 = contract_strategy.calculate(mock_employee)
        result2 = contract_strategy.calculate(mock_employee)
        result3 = contract_strategy.calculate(mock_employee)

        assert result1 == result2 == result3

    def test_calculate_independence_between_contractors(self, contract_strategy):
        """Test that calculations for different contractors are independent."""
        contractor1 = Mock()
        contractor1.contract_amount = Decimal("5000.00")

        contractor2 = Mock()
        contractor2.contract_amount = Decimal("15000.00")

        result1 = contract_strategy.calculate(contractor1)
        result2 = contract_strategy.calculate(contractor2)

        assert result1 == Decimal("5000.00")
        assert result2 == Decimal("15000.00")


class TestContractPaymentScenarios:
    """Tests for realistic contract payment scenarios."""

    def test_calculate_monthly_retainer_contract(self, contract_strategy, mock_employee):
        """Test with monthly retainer contract amount."""
        mock_employee.contract_amount = Decimal("3000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("3000.00")

    def test_calculate_project_milestone_payment(self, contract_strategy, mock_employee):
        """Test with project milestone payment amount."""
        mock_employee.contract_amount = Decimal("12500.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("12500.00")

    def test_calculate_software_development_contract(self, contract_strategy, mock_employee):
        """Test with typical software development contract."""
        mock_employee.contract_amount = Decimal("50000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("50000.00")

    def test_calculate_consulting_engagement(self, contract_strategy, mock_employee):
        """Test with consulting engagement contract."""
        mock_employee.contract_amount = Decimal("25000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("25000.00")

    def test_calculate_short_term_contract(self, contract_strategy, mock_employee):
        """Test with short-term contract amount."""
        mock_employee.contract_amount = Decimal("2000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("2000.00")

    def test_calculate_long_term_contract(self, contract_strategy, mock_employee):
        """Test with long-term contract amount."""
        mock_employee.contract_amount = Decimal("150000.00")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("150000.00")

    def test_calculate_fractional_contract_payment(self, contract_strategy, mock_employee):
        """Test with fractional cent contract payment."""
        mock_employee.contract_amount = Decimal("5555.55")

        result = contract_strategy.calculate(mock_employee)

        assert result == Decimal("5555.55")


class TestComparisonWithOtherStrategies:
    """Tests comparing ContractStrategy with other payment strategies."""

    def test_contract_strategy_simplicity(self, contract_strategy, mock_employee):
        """Test that ContractStrategy is simple like SalaryStrategy."""
        mock_employee.contract_amount = Decimal("7500.00")

        # ContractStrategy should just return the contract amount
        result = contract_strategy.calculate(mock_employee)

        assert result == mock_employee.contract_amount

    def test_contract_strategy_no_multiplication(self, contract_strategy, mock_employee):
        """Test that ContractStrategy doesn't perform multiplication like HourlyStrategy."""
        mock_employee.contract_amount = Decimal("5000.00")

        result = contract_strategy.calculate(mock_employee)

        # Should be exactly the contract amount, not multiplied by hours or rates
        assert result == Decimal("5000.00")

    def test_contract_payment_independence_from_hours(self, contract_strategy, mock_employee):
        """Test that contract payment is independent of hours worked."""
        mock_employee.contract_amount = Decimal("10000.00")
        mock_employee.worked_hours = Decimal("100")

        result = contract_strategy.calculate(mock_employee)

        # Should return contract amount regardless of hours
        assert result == Decimal("10000.00")


class TestContractStrategyConsistency:
    """Tests for consistency and reliability of ContractStrategy."""

    def test_calculate_deterministic_results(self, contract_strategy, mock_employee):
        """Test that identical inputs always produce identical outputs."""
        mock_employee.contract_amount = Decimal("6500.75")

        results = [contract_strategy.calculate(mock_employee) for _ in range(5)]

        # All results should be identical
        assert all(r == Decimal("6500.75") for r in results)

    def test_calculate_with_different_strategy_instances(self, mock_employee):
        """Test that different strategy instances produce identical results."""
        strategy1 = ContractStrategy()
        strategy2 = ContractStrategy()

        mock_employee.contract_amount = Decimal("8000.00")

        result1 = strategy1.calculate(mock_employee)
        result2 = strategy2.calculate(mock_employee)

        assert result1 == result2
