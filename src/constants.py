from decimal import Decimal

OVERTIME_MULTIPLIER = Decimal("1.5")
WEEKEND_MULTIPLIER = Decimal("2")

US_LOW_TAX = Decimal("0.22")
US_HIGH_TAX = Decimal("0.30")
EU_TAX = Decimal("0.25")
UA_TAX = Decimal("0.195")
DEFAULT_TAX = Decimal("0.20")

US_HIGH_TAX_THRESHOLD = Decimal("5000")

SALARY_QUARTERLY_BONUS = Decimal("500")
HOURLY_YEARLY_BONUS = Decimal("200")