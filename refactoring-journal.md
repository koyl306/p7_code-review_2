Нижче заповнення бланка на основі твоїх 4 коммітів.

---

## Крок 1: Extract Constants

**Тип**: Extract Constants

**Причина**:
У коді були “магічні числа” (tax rates, multipliers, bonus values), що ускладнювало зміну бізнес-логіки та підвищувало ризик помилок.

**AI допоміг**: так — запропонував винести всі бізнес-значення в `constants.py` і згрупувати їх по доменах (tax, bonus, multipliers)

**Моє рішення**:
Я залишив всі константи в одному файлі замість розбиття по модулях (наприклад `tax_constants.py`, `bonus_constants.py`), щоб:

* не ускладнювати структуру на ранньому етапі
* уникнути overengineering

**Тести**:

* unit тести на `TaxCalculator`
* unit тести на `HourlyStrategy` (перевірка multipliers)
* regression тест: незмінність результатів payroll calculation

**Commit**: `refactor: extract payroll business constants`

---

## Крок 2: Simplify Architecture (No deep modularization)

**Тип**: Move Class / Simplify Structure

**Причина**:
Початковий варіант з великою кількістю папок був надмірно складним для невеликого сервісу. Потрібно було зменшити когнітивну складність структури.

**AI допоміг**: так — запропонував розділення на `models / strategies / calculators`, але я спростив до 3 файлів

**Моє рішення**:
Я свідомо обмежив структуру до:

* `payroll.py`
* `constants.py`
* `strategies.py`

Відмовився від повної папкової архітектури, бо:

* проект невеликий
* часті зміни бізнес-логіки
* важлива швидкість розробки

**Тести**:

* smoke test `PayrollService.calculate_payroll`
* тести стратегій (hourly/salary/contract)
* перевірка правильності DI стратегій

**Commit**: `refactor: simplify architecture without deep module split`

---

## Крок 3: Replace Factory with Dependency Injection

**Тип**: Replace Factory with DI

**Причина**:
`PayrollStrategyFactory` створював жорстке зв’язування і ускладнював тестування та розширення логіки.

**AI допоміг**: так — запропонував повністю прибрати factory і передавати стратегії через constructor injection

**Моє рішення**:
Я:

* залишив словник стратегій у `PayrollService`
* не виніс DI у framework-level container
* відмовився від повного IoC контейнера (зайве для цього масштабу)

Причина:

* простота
* контроль над ініціалізацією

**Тести**:

* unit тест PayrollService з mock strategies
* перевірка правильного вибору стратегії по EmployeeType

**Commit**: `refactor: remove strategy factory and use dependency injection`

---

## Крок 4: Extract Method (Hourly Strategy)

**Тип**: Extract Method

**Причина**:
Метод `calculate` у `HourlyStrategy` був занадто довгий і містив кілька бізнес-правил одразу (base, overtime, weekend pay).

**AI допоміг**: так — запропонував розбити логіку на приватні методи для кожного типу розрахунку

**Моє рішення**:
Я:

* виніс логіку в `_calculate_base_pay`, `_calculate_overtime_pay`, `_calculate_weekend_pay`
* не робив окремі класи для кожного виду оплати (це було б overengineering)

Причина:

* це одна бізнес-логіка (hourly payroll), а не різні домени
* простіше підтримувати в одному класі

**Тести**:

* unit тести на кожен компонент розрахунку:

  * base pay
  * overtime multiplier
  * weekend multiplier
* інтеграційний тест HourlyStrategy.calculate

**Commit**: `refactor: extract hourly calculation methods`

---
