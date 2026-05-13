"""
Unit tests for HourlyStrategy.calculate() method.

Tests cover:
- Regular hours pay calculation
- Overtime hours pay calculation (1.5x multiplier)
- Weekend hours pay calculation (2x multiplier)
- Combined scenarios with all hour types
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock
from src.strategies import HourlyStrategy
from src.constants import OVERTIME_MULTIPLIER, WEEKEND_MULTIPLIER


@pytest.fixture
def hourly_strategy():
    """Fixture providing an instance of HourlyStrategy."""
    return HourlyStrategy()


@pytest.fixture
def mock_employee():
    """Fixture providing a mock employee object."""
    employee = Mock()
    employee.hourly_rate = Decimal("20.00")
    employee.worked_hours = Decimal("0")
    employee.overtime_hours = Decimal("0")
    employee.weekend_hours = Decimal("0")
    return employee


class TestRegularHours:
    """Tests for regular hours pay calculation."""

    def test_calculate_base_pay_single_hour(self, hourly_strategy, mock_employee):
        """Test pay calculation for 1 regular hour."""
        mock_employee.worked_hours = Decimal("1")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("20.00")

    def test_calculate_base_pay_multiple_hours(self, hourly_strategy, mock_employee):
        """Test pay calculation for multiple regular hours."""
        mock_employee.worked_hours = Decimal("8")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("160.00")

    def test_calculate_base_pay_fractional_hours(self, hourly_strategy, mock_employee):
        """Test pay calculation for fractional hours."""
        mock_employee.worked_hours = Decimal("5.5")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("110.00")

    def test_calculate_base_pay_zero_hours(self, hourly_strategy, mock_employee):
        """Test pay calculation when no regular hours worked."""
        mock_employee.worked_hours = Decimal("0")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("0.00")

    def test_calculate_base_pay_varying_hourly_rates(self, hourly_strategy, mock_employee):
        """Test pay calculation with different hourly rates."""
        mock_employee.hourly_rate = Decimal("25.50")
        mock_employee.worked_hours = Decimal("10")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("255.00")


class TestOvertimeHours:
    """Tests for overtime hours pay calculation (1.5x multiplier)."""

    def test_calculate_overtime_pay_single_hour(self, hourly_strategy, mock_employee):
        """Test overtime pay calculation for 1 overtime hour."""
        mock_employee.overtime_hours = Decimal("1")

        result = hourly_strategy._calculate_overtime_pay(mock_employee)

        expected = Decimal("20.00") * Decimal("1") * OVERTIME_MULTIPLIER
        assert result == expected

    def test_calculate_overtime_pay_multiple_hours(self, hourly_strategy, mock_employee):
        """Test overtime pay calculation for multiple overtime hours."""
        mock_employee.overtime_hours = Decimal("5")

        result = hourly_strategy._calculate_overtime_pay(mock_employee)

        expected = Decimal("20.00") * Decimal("5") * OVERTIME_MULTIPLIER
        assert result == expected

    def test_calculate_overtime_pay_fractional_hours(self, hourly_strategy, mock_employee):
        """Test overtime pay calculation for fractional overtime hours."""
        mock_employee.overtime_hours = Decimal("2.5")

        result = hourly_strategy._calculate_overtime_pay(mock_employee)

        expected = Decimal("20.00") * Decimal("2.5") * OVERTIME_MULTIPLIER
        assert result == expected

    def test_calculate_overtime_pay_zero_hours(self, hourly_strategy, mock_employee):
        """Test overtime pay when no overtime hours worked."""
        mock_employee.overtime_hours = Decimal("0")

        result = hourly_strategy._calculate_overtime_pay(mock_employee)

        assert result == Decimal("0.00")

    def test_overtime_multiplier_applied(self, hourly_strategy, mock_employee):
        """Test that overtime multiplier (1.5x) is correctly applied."""
        mock_employee.overtime_hours = Decimal("2")

        result = hourly_strategy._calculate_overtime_pay(mock_employee)
        base_calculation = Decimal("20.00") * Decimal("2")

        assert result == base_calculation * OVERTIME_MULTIPLIER
        assert result == Decimal("60.00")


class TestWeekendHours:
    """Tests for weekend hours pay calculation (2x multiplier)."""

    def test_calculate_weekend_pay_single_hour(self, hourly_strategy, mock_employee):
        """Test weekend pay calculation for 1 weekend hour."""
        mock_employee.weekend_hours = Decimal("1")

        result = hourly_strategy._calculate_weekend_pay(mock_employee)

        expected = Decimal("20.00") * Decimal("1") * WEEKEND_MULTIPLIER
        assert result == expected

    def test_calculate_weekend_pay_multiple_hours(self, hourly_strategy, mock_employee):
        """Test weekend pay calculation for multiple weekend hours."""
        mock_employee.weekend_hours = Decimal("4")

        result = hourly_strategy._calculate_weekend_pay(mock_employee)

        expected = Decimal("20.00") * Decimal("4") * WEEKEND_MULTIPLIER
        assert result == expected

    def test_calculate_weekend_pay_fractional_hours(self, hourly_strategy, mock_employee):
        """Test weekend pay calculation for fractional weekend hours."""
        mock_employee.weekend_hours = Decimal("3.5")

        result = hourly_strategy._calculate_weekend_pay(mock_employee)

        expected = Decimal("20.00") * Decimal("3.5") * WEEKEND_MULTIPLIER
        assert result == expected

    def test_calculate_weekend_pay_zero_hours(self, hourly_strategy, mock_employee):
        """Test weekend pay when no weekend hours worked."""
        mock_employee.weekend_hours = Decimal("0")

        result = hourly_strategy._calculate_weekend_pay(mock_employee)

        assert result == Decimal("0.00")

    def test_weekend_multiplier_applied(self, hourly_strategy, mock_employee):
        """Test that weekend multiplier (2x) is correctly applied."""
        mock_employee.weekend_hours = Decimal("3")

        result = hourly_strategy._calculate_weekend_pay(mock_employee)
        base_calculation = Decimal("20.00") * Decimal("3")

        assert result == base_calculation * WEEKEND_MULTIPLIER
        assert result == Decimal("120.00")


class TestCombinedHours:
    """Tests for combined hours scenarios."""

    def test_calculate_with_all_hour_types(self, hourly_strategy, mock_employee):
        """Test calculate() with regular, overtime, and weekend hours combined."""
        mock_employee.worked_hours = Decimal("8")
        mock_employee.overtime_hours = Decimal("2")
        mock_employee.weekend_hours = Decimal("4")

        # Mock Money.round to return input as-is for testing
        with pytest.mock.patch('src.strategies.Money.round', side_effect=lambda x: x):
            result = hourly_strategy.calculate(mock_employee)

        base_pay = Decimal("8") * Decimal("20.00")  # 160
        overtime_pay = Decimal("2") * Decimal("20.00") * OVERTIME_MULTIPLIER  # 60
        weekend_pay = Decimal("4") * Decimal("20.00") * WEEKEND_MULTIPLIER  # 160
        expected = base_pay + overtime_pay + weekend_pay

        assert result == expected

    def test_calculate_with_only_regular_hours(self, hourly_strategy, mock_employee):
        """Test calculate() with only regular hours."""
        mock_employee.worked_hours = Decimal("8")
        mock_employee.overtime_hours = Decimal("0")
        mock_employee.weekend_hours = Decimal("0")

        with pytest.mock.patch('src.strategies.Money.round', side_effect=lambda x: x):
            result = hourly_strategy.calculate(mock_employee)

        expected = Decimal("8") * Decimal("20.00")
        assert result == expected

    def test_calculate_with_only_overtime_hours(self, hourly_strategy, mock_employee):
        """Test calculate() with only overtime hours."""
        mock_employee.worked_hours = Decimal("0")
        mock_employee.overtime_hours = Decimal("5")
        mock_employee.weekend_hours = Decimal("0")

        with pytest.mock.patch('src.strategies.Money.round', side_effect=lambda x: x):
            result = hourly_strategy.calculate(mock_employee)

        expected = Decimal("5") * Decimal("20.00") * OVERTIME_MULTIPLIER
        assert result == expected

    def test_calculate_with_only_weekend_hours(self, hourly_strategy, mock_employee):
        """Test calculate() with only weekend hours."""
        mock_employee.worked_hours = Decimal("0")
        mock_employee.overtime_hours = Decimal("0")
        mock_employee.weekend_hours = Decimal("6")

        with pytest.mock.patch('src.strategies.Money.round', side_effect=lambda x: x):
            result = hourly_strategy.calculate(mock_employee)

        expected = Decimal("6") * Decimal("20.00") * WEEKEND_MULTIPLIER
        assert result == expected

    def test_calculate_with_zero_hours(self, hourly_strategy, mock_employee):
        """Test calculate() when employee worked zero hours."""
        mock_employee.worked_hours = Decimal("0")
        mock_employee.overtime_hours = Decimal("0")
        mock_employee.weekend_hours = Decimal("0")

        with pytest.mock.patch('src.strategies.Money.round', side_effect=lambda x: x):
            result = hourly_strategy.calculate(mock_employee)

        assert result == Decimal("0")


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_large_number_of_hours(self, hourly_strategy, mock_employee):
        """Test with large number of hours."""
        mock_employee.worked_hours = Decimal("168")  # Full week

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("3360.00")

    def test_very_high_hourly_rate(self, hourly_strategy, mock_employee):
        """Test with very high hourly rate."""
        mock_employee.hourly_rate = Decimal("500.00")
        mock_employee.worked_hours = Decimal("10")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("5000.00")

    def test_very_low_hourly_rate(self, hourly_strategy, mock_employee):
        """Test with very low hourly rate."""
        mock_employee.hourly_rate = Decimal("0.50")
        mock_employee.worked_hours = Decimal("10")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("5.00")

    def test_high_precision_decimal_values(self, hourly_strategy, mock_employee):
        """Test with high precision decimal values."""
        mock_employee.hourly_rate = Decimal("20.75")
        mock_employee.worked_hours = Decimal("7.33")

        result = hourly_strategy._calculate_base_pay(mock_employee)

        assert result == Decimal("20.75") * Decimal("7.33")

    def test_overtime_weekend_hours_combined(self, hourly_strategy, mock_employee):
        """Test calculation with both overtime and weekend hours."""
        mock_employee.hourly_rate = Decimal("25.00")
        mock_employee.overtime_hours = Decimal("3")
        mock_employee.weekend_hours = Decimal("2")

        overtime_pay = hourly_strategy._calculate_overtime_pay(mock_employee)
        weekend_pay = hourly_strategy._calculate_weekend_pay(mock_employee)

        expected_overtime = Decimal("25.00") * Decimal("3") * OVERTIME_MULTIPLIER
        expected_weekend = Decimal("25.00") * Decimal("2") * WEEKEND_MULTIPLIER

        assert overtime_pay == expected_overtime
        assert weekend_pay == expected_weekend
