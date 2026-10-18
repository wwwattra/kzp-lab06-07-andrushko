# Звіт до лабораторної роботи №6

з дисципліни «Кросплатформні засоби програмування», тема «Обробка даних засобами Python». Варіант 2. Спортивні тренування.
Виконав: студент групи КІ-302 Андрушко А. І. Прийняв: Олексів М. В.

## Тема, номер і варіант

Лабораторна робота № 6 «Обробка даних засобами Python». Варіант 2 – «Спортивні тренування». ОС – Windows 10 (64-bit), Python 3.12.10, pytest 9.1.1, ruff 0.17.1, build 1.6.1.

Посилання на GitHub-репозиторій: https://github.com/[ваш-логін]/kzp-lab-andrushko (каталог або гілка lab06), Git-тег v0.1.0-py.

## Мета роботи

Створити Python-пакет kzp_lab06, який читає CSV через csv.DictReader, перетворює текстові поля на типізовані значення, будує звіт за списками, словниками й множинами, записує його у файл через with і Path.open, обробляє помилки без голого except із збереженням першопричини, має CLI, тести pytest, перевірку ruff і збирається у wheel.

## Формат CSV

Файл data/input.csv у UTF-8 із заголовком date,kind,duration,distance,pulse. Типи після перетворення: date – str (ISO YYYY-MM-DD), kind – str (нормалізований через strip), duration – int, distance – float, pulse – int (додатний). Від'ємні значення заборонені. Порожній файл або файл лише із заголовком дають порожній список записів і звіт «Записів: 0». Поле з комою записується в лапках, наприклад 2026-09-03,"біг, інтервали",40,6.0,165.

*Лістинг 1 – Вхідні дані data/input.csv*

```text
date,kind,duration,distance,pulse
2026-09-01,біг,45,8.5,148
2026-09-02,велосипед,90,32.0,132
2026-09-03,"біг, інтервали",40,6.0,165
2026-09-05,біг,30,5.2,140
2026-09-06,велосипед,60,21.5,128
2026-09-08,біг,75,12.8,145
2026-09-08,велосипед,120,41.3,138
2026-09-10,біг,45,10.0,152
```

Набір містить 8 записів, дубльований вид «біг» (перевірка множини), граничне значення duration = 45 (входить у відбір), запис 40 хв (не входить) і текст із комою. Поріг відбору threshold = 45 хв; порожній результат відбору перевіряється тестом із порогом 200. Пошкоджений файл data/broken.csv містить нечислову тривалість «дев'яносто».

## Структура модулів

*Таблиця 1 – Модулі пакета src/kzp_lab06*

| Модуль | Відповідальність |
|---|---|
| errors.py | клас DataError(ValueError) |
| loader.py | читання CSV, перевірка заголовка, перетворення типів, помилки з номером рядка |
| analysis.py | відбір, множина видів, словник агрегатів, середнє, максимум, make_summary |
| reporting.py | детермінований текст звіту й запис через with |
| cli.py | argparse, коди завершення 0/2, UTF-8 для stdout/stderr |
| __init__.py | мінімальний публічний API та версія |

loader не друкує звіт, analysis не відкриває файли, reporting не читає CSV. Точка входу захищена if __name__ == "__main__":, тому імпорт модуля в тестах не запускає програму.

*Лістинг 2 – src/kzp_lab06/loader.py*

```text
"""Читання CSV і перетворення рядків на типізовані записи."""

import csv
from pathlib import Path

from .errors import DataError

REQUIRED_FIELDS = ("date", "kind", "duration", "distance", "pulse")

def _parse_number(row: dict[str, str], field: str, row_number: int, kind: type) -> float | int:
    """Перетворює поле на число та додає номер рядка і назву поля до помилки."""
    try:
        value = kind(row[field])
    except (KeyError, TypeError, ValueError) as error:
        raise DataError(f"Рядок {row_number}: поле {field} має бути числом") from error
    if value < 0:
        raise DataError(f"Рядок {row_number}: поле {field} не може бути від'ємним")
    return value

def parse_row(row: dict[str, str], row_number: int) -> dict[str, object]:
    """Перевіряє один рядок CSV і повертає запис із типізованими значеннями."""
    date = (row.get("date") or "").strip()
    kind = (row.get("kind") or "").strip()
    if not date:
        raise DataError(f"Рядок {row_number}: поле date порожнє")
    if not kind:
        raise DataError(f"Рядок {row_number}: поле kind порожнє")
    pulse = _parse_number(row, "pulse", row_number, int)
    if pulse == 0:
        raise DataError(f"Рядок {row_number}: поле pulse має бути додатним")
    return {
        "date": date,
        "kind": kind,
        "duration": _parse_number(row, "duration", row_number, int),
        "distance": float(_parse_number(row, "distance", row_number, float)),
        "pulse": pulse,
    }

def load_records(path: Path) -> list[dict[str, object]]:
    """Читає CSV у UTF-8 і повертає список перевірених записів."""
    try:
        # newline="" передає керування роздільниками рядків модулю csv.
        with path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames is None:
                return []
            if tuple(reader.fieldnames) != REQUIRED_FIELDS:
                raise DataError(
                    f"Некоректний заголовок CSV: {reader.fieldnames}, "
                    f"очікується {list(REQUIRED_FIELDS)}"
                )
            return [parse_row(row, row_number) for row_number, row in enumerate(reader, start=2)]
    except OSError as error:
        raise DataError(f"Не вдалося прочитати файл: {path}") from error
```

## Перетворення даних

Список зберігає записи в порядку файла (list[dict[str, object]]). Відбір – list comprehension [record for record in records if int(record["duration"]) >= minimum]. Множина видів – set comprehension {str(record["kind"]) for record in records}. Словник агрегатів – dict comprehension {kind: sum(...) for kind in sorted(kinds)}. Сортування ключів робить порядок незалежним від вхідного файла.

*Лістинг 3 – src/kzp_lab06/analysis.py*

```text
"""Обчислення над записами тренувань."""

from collections.abc import Iterable

MIN_DURATION = 45

def long_trainings(
    records: Iterable[dict[str, object]], minimum: int = MIN_DURATION
) -> list[dict[str, object]]:
    """Повертає тренування тривалістю не менше заданої кількості хвилин."""
    return [record for record in records if int(record["duration"]) >= minimum]

def kinds(records: Iterable[dict[str, object]]) -> set[str]:
    """Повертає множину унікальних видів тренувань."""
    return {str(record["kind"]) for record in records}

def distance_by_kind(records: list[dict[str, object]]) -> dict[str, float]:
    """Обчислює сумарну дистанцію за видом у стабільному порядку ключів."""
    return {
        kind: sum(float(record["distance"]) for record in records if record["kind"] == kind)
        for kind in sorted(kinds(records))
    }

def average_pulse(records: list[dict[str, object]]) -> float:
    """Повертає середній пульс або 0.0 для порожнього набору."""
    if not records:
        return 0.0
    return sum(int(record["pulse"]) for record in records) / len(records)

def longest_training(records: list[dict[str, object]]) -> dict[str, object] | None:
    """Повертає найдовше тренування (перше за порядком при рівності) або None."""
    return max(records, key=lambda record: int(record["duration"]), default=None)

def make_summary(
    records: list[dict[str, object]],
    *metrics: str,
    minimum_duration: int = MIN_DURATION,
    **labels: str,
) -> dict[str, object]:
    """Формує підсумок і довільні суми метрик для тренувань від minimum_duration хвилин."""
    for metric in metrics:
        if records and any(metric not in record for record in records):
            raise ValueError(f"Невідома метрика: {metric}")
    selected = long_trainings(records, minimum_duration)
    result: dict[str, object] = {
        "count": len(records),
        "selected": len(selected),
        "kinds": kinds(records),
        "distance_by_kind": distance_by_kind(records),
        "average_pulse": average_pulse(records),
        "longest": longest_training(records),
    }
    for metric in metrics:
        result[labels.get(metric, metric)] = sum(float(record[metric]) for record in selected)
    return result
```

## Функції

make_summary(records, *metrics, minimum_duration=45, **labels): metrics усередині – кортеж назв полів для підсумовування, minimum_duration – незмінне типове значення (int, не список), labels – словник підписів для метрик. Невідома метрика відхиляється ValueError. Приклад виклику з CLI: make_summary(records, "duration", duration="minutes_long") – сумарний час тренувань від 45 хв (435 хв).

## Алгоритм аналізу

– відбір: тренування від 45 хв (6 із 8);

– агрегування: сумарна дистанція за видом (distance_by_kind);

– унікальні значення: множина видів (3 види);

– показники звіту варіанта: середній пульс (143.50) і найдовше тренування (120 хв);

– детермінований порядок: sorted для ключів і видів, фіксований формат :.2f.

## Обробка помилок

DataError містить номер рядка (рахуючи заголовок як рядок 1) і назву поля: «Рядок 3: поле duration має бути числом». Першопричина зберігається через raise DataError(...) from error; помилки файлової системи OSError також перетворюються на DataError. Голий except не використано. CLI повертає 0 після успіху та 2 для помилки даних, повідомлення виводиться в stderr.

*Лістинг 4 – src/kzp_lab06/cli.py*

```text
"""Командний рядок: вхідний CSV → текстовий звіт."""

import argparse
import sys
from pathlib import Path

from .analysis import make_summary
from .errors import DataError
from .loader import load_records
from .reporting import format_report, write_report

def _reconfigure_utf8() -> None:
    """Задає UTF-8 для stdout і stderr, бо консоль Windows може мати інше кодування."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

def main(argv: list[str] | None = None) -> int:
    """Обробляє аргументи CLI, будує та записує звіт; повертає код завершення."""
    _reconfigure_utf8()
    parser = argparse.ArgumentParser(description="Звіт про спортивні тренування")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_report", type=Path)
    args = parser.parse_args(argv)
    try:
        records = load_records(args.input_csv)
        summary = make_summary(records, "duration", duration="minutes_long")
        text = format_report(summary)
        write_report(args.output_report, text)
    except DataError as error:
        print(f"Помилка даних: {error}", file=sys.stderr)
        return 2
    print(text, end="")
    print(f"Звіт записано у {args.output_report}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## Файловий звіт

Звіт записується у reports/summary.txt функцією write_report: каталог створюється mkdir(parents=True, exist_ok=True), файл відкривається path.open("w", encoding="utf-8", newline="\n") у блоці with, що гарантує закриття навіть у разі помилки.

*Лістинг 5 – src/kzp_lab06/reporting.py*

```text
"""Формування та запис текстового звіту."""

from pathlib import Path

def format_report(summary: dict[str, object]) -> str:
    """Форматує підсумок у детермінований текстовий звіт."""
    lines = [
        "Звіт: спортивні тренування",
        f"Записів: {summary['count']}",
        f"Тренувань від 45 хв: {summary['selected']}",
        f"Види тренувань: {'; '.join(sorted(summary['kinds']))}",
        "Сумарна дистанція за видом, км:",
    ]
    for kind, distance in sorted(summary["distance_by_kind"].items()):
        lines.append(f"  {kind}: {distance:.2f}")
    lines.append(f"Середній пульс: {summary['average_pulse']:.2f}")
    longest = summary["longest"]
    if longest is None:
        lines.append("Найдовше тренування: немає даних")
    else:
        lines.append(
            f"Найдовше тренування: {longest['date']} {longest['kind']}, {longest['duration']} хв"
        )
    if "minutes_long" in summary:
        lines.append(f"Сумарний час тренувань від 45 хв: {summary['minutes_long']:.0f} хв")
    return "\n".join(lines) + "\n"

def write_report(path: Path, text: str) -> None:
    """Створює каталог і записує звіт у файл UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)
```

*Лістинг 6 – Повний вивід CLI (python -m kzp_lab06.cli data\input.csv reports\summary.txt)*

```text
Звіт: спортивні тренування
Записів: 8
Тренувань від 45 хв: 6
Види тренувань: біг; біг, інтервали; велосипед
Сумарна дистанція за видом, км:
  біг: 36.50
  біг, інтервали: 6.00
  велосипед: 94.80
Середній пульс: 143.50
Найдовше тренування: 2026-09-08 велосипед, 120 хв
Сумарний час тренувань від 45 хв: 435 хв
Звіт записано у reports\summary.txt
```

*Лістинг 7 – Помилковий сценарій: data\broken.csv, код завершення 2*

```text
Помилка даних: Рядок 3: поле duration має бути числом
```

## Тестування

19 тестів pytest: перетворення типів; поле з комою; порожній файл і лише заголовок; пошкоджене число з номером рядка й __cause__; від'ємне значення та нульовий пульс; відсутній стовпець; відсутнє значення в рядку й порожній вид; відсутній файл; відбір із межею; порожній результат відбору; множина без дублікатів; детермінований словник; середнє й максимум; порожній вхід; *args/типовий параметр/**kwargs; невідома метрика; запис UTF-8; CLI успіх і помилка.

*Лістинг 8 – python -m pytest -v*

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\user\kzp-labs\lab06
configfile: pyproject.toml
collected 19 items

tests\test_analysis.py ........                                          [ 42%]
tests\test_cli.py ...                                                    [ 57%]
tests\test_loader.py ........                                            [100%]

============================= 19 passed in 0.20s ==============================
```

*Лістинг 9 – tests/test_analysis.py*

```text
"""Тести функцій аналізу."""

import pytest

from kzp_lab06.analysis import (
    average_pulse,
    distance_by_kind,
    kinds,
    long_trainings,
    longest_training,
    make_summary,
)

RECORDS = [
    {"date": "2026-09-01", "kind": "біг", "duration": 45, "distance": 8.5, "pulse": 148},
    {"date": "2026-09-02", "kind": "велосипед", "duration": 90, "distance": 32.0, "pulse": 132},
    {"date": "2026-09-05", "kind": "біг", "duration": 30, "distance": 5.2, "pulse": 140},
]

def test_filter_includes_boundary() -> None:
    """Перевіряє, що 45 хв входить у відбір, а 30 - ні."""
    assert [record["date"] for record in long_trainings(RECORDS)] == ["2026-09-01", "2026-09-02"]

def test_filter_can_return_empty_result() -> None:
    """Перевіряє явний порожній результат відбору."""
    assert long_trainings(RECORDS, minimum=200) == []

def test_set_removes_duplicates() -> None:
    """Перевіряє, що множина видів не містить дублікатів."""
    assert kinds(RECORDS) == {"біг", "велосипед"}

def test_distance_by_kind_is_deterministic() -> None:
    """Перевіряє значення і порядок ключів словника агрегатів."""
    result = distance_by_kind(list(reversed(RECORDS)))
    assert list(result) == ["біг", "велосипед"]
    assert result["біг"] == pytest.approx(13.7)

def test_average_and_longest() -> None:
    """Перевіряє середній пульс і найдовше тренування."""
    assert average_pulse(RECORDS) == pytest.approx(140.0)
    assert longest_training(RECORDS)["kind"] == "велосипед"

def test_empty_input() -> None:
    """Перевіряє поведінку на порожньому вході."""
    summary = make_summary([], "duration")
    assert summary["count"] == 0
    assert summary["distance_by_kind"] == {}
    assert summary["average_pulse"] == 0.0
    assert summary["longest"] is None
    assert summary["duration"] == 0.0

def test_make_summary_args_defaults_and_kwargs() -> None:
    """Перевіряє *args, типовий параметр і **kwargs."""
    summary = make_summary(RECORDS, "duration", "distance", duration="Хвилини", distance="Км")
    assert summary["selected"] == 2
    assert summary["Хвилини"] == 135.0
    assert summary["Км"] == pytest.approx(40.5)
    strict = make_summary(RECORDS, "duration", minimum_duration=60)
    assert strict["duration"] == 90.0

def test_unknown_metric_rejected() -> None:
    """Перевіряє явну помилку для невідомої метрики."""
    with pytest.raises(ValueError, match="Невідома метрика"):
        make_summary(RECORDS, "speed")
```

## Якість та пакетування

*Лістинг 10 – ruff check .*

```text
All checks passed!
```

*Лістинг 11 – ruff format --check .*

```text
10 files already formatted
```

Wheel kzp_training_report-0.1.0-py3-none-any.whl зібрано командою python -m build --wheel і встановлено в окреме чисте середовище без dev-залежностей; CLI з цього середовища дав той самий звіт:

*Лістинг 12 – Перевірка wheel*

```text
python -m venv .venv-wheel
.venv-wheel\Scripts\python -m pip install --no-deps dist\kzp_training_report-0.1.0-py3-none-any.whl
.venv-wheel\Scripts\python -m kzp_lab06.cli data\input.csv reports\summary.txt   # код 0
.venv-wheel\Scripts\python -m kzp_lab06.cli data\broken.csv reports\broken.txt   # код 2
```

*Лістинг 13 – pyproject.toml*

```text
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "kzp-training-report"
version = "0.1.0"
description = "CSV report for sport trainings (KZP, variant 2)"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
    "build>=1.2",
]

[project.scripts]
kzp-lab06 = "kzp_lab06.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
addopts = "-q"
pythonpath = ["src"]

[tool.ruff]
line-length = 100
exclude = ["build", "dist", ".venv", ".venv-*"]

[tool.ruff.lint]
select = ["E", "F", "W", "B", "UP"]
```

## GitHub Actions

Матриця Ubuntu/Windows/macOS: встановлення pip install -e ".[dev]", pytest, ruff check, ruff format --check, збірка wheel і завантаження артефакту. Посилання: запуск CI та wheel-артефакт – після push.

*Лістинг 14 – .github/workflows/ci.yml*

```text
name: Python checks

on:
  push:
  pull_request:

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip
      - name: Install project
        run: python -m pip install -e ".[dev]"
      - name: Test
        run: python -m pytest
      - name: Lint
        run: ruff check .
      - name: Format check
        run: ruff format --check .
      - name: Build wheel
        run: python -m build --wheel
      - name: Upload wheel
        uses: actions/upload-artifact@v4
        with:
          name: kzp-training-report-${{ matrix.os }}-${{ github.run_number }}
          path: dist/*.whl
          if-no-files-found: error
```

## GitHub Issues і Pull Request

*Таблиця 2 – План GitHub Issues → зміна → перевірка*

| Issue | Мітка | Зміна | Перевірка |
|---|---|---|---|
| Завантаження CSV | feature | loader.py, DataError | test_loader.py |
| Аналіз даних | feature | analysis.py, comprehensions | test_analysis.py |
| Звіт і CLI | feature | reporting.py, cli.py | test_cli.py |
| Якість коду | infra | pyproject.toml: ruff, pytest | ruff check/format |
| CI і wheel | infra | ci.yml, build | зелений CI, артефакт |
| Документація ЛР6 | docs | README, docstrings, REPORT | рев'ю PR |

## Академічна доброчесність

Заповніть самостійно: використані інструменти ШІ або твердження, що вони не використовувалися; ролі, запити, прийняті й відхилені рекомендації; власний внесок і підтвердження розуміння всього поданого коду.

## Відповіді на контрольні питання

1. Яку роль виконує pyproject.toml у Python-проєкті?

Описує пакет (назва, версія, мінімальний Python), dev-залежності, точку входу CLI, систему збірки та налаштування pytest і ruff.

2. Навіщо створюється віртуальне середовище?

Щоб ізолювати залежності проєкту від системного Python і відтворювати їх за pyproject.toml; .venv у репозиторій не додається.

3. Чому CSV-файл відкривається з newline=""?

Модуль csv сам обробляє роздільники рядків, зокрема перенесення всередині лапок; інакше Python перетворював би їх заздалегідь.

4. Які типи повертає csv.DictReader без додаткового перетворення?

Словник str → str: усі значення є рядками, числа треба перетворювати явно.

5. Чому split(",") не є коректним CSV-парсером?

Він розірве "біг, інтервали" на два поля й не обробить лапки.

6. Як відрізняються список, словник і множина?

Список упорядкований і допускає повтори; словник зіставляє унікальні ключі зі значеннями; множина зберігає унікальні значення без гарантованого порядку.

7. Коли comprehension робить код зрозумілішим, а коли краще використати цикл?

Для одного прозорого відбору чи перетворення – comprehension; для кількох вкладених умов, побічних ефектів або складного накопичення – звичайний цикл.

8. Що містять *args і **kwargs усередині функції?

*args – кортеж додаткових позиційних аргументів, **kwargs – словник іменованих.

9. Чому змінний об'єкт небезпечний як значення за замовчуванням?

Він створюється один раз під час визначення функції й спільний для всіх викликів, тож зміни «перетікають» між викликами.

10. Як raise ... from error зберігає першопричину?

Записує початковий виняток у __cause__ нового, і traceback показує обидва.

11. Чому завантаження, аналіз і запис звіту розділяються на модулі?

Кожен модуль має одну відповідальність і тестується окремо, наприклад analysis – без файлів.

12. Яку гарантію дає with під час роботи з файлом?

Файл буде закрито після виходу з блоку, навіть якщо виник виняток.

13. Чому звіт має формуватися в детермінованому порядку?

Щоб однаковий вхід давав однаковий текст на будь-якій ОС і тести могли порівнювати рядки.

14. Які випадки повинні бути перевірені для порожнього CSV?

Повністю порожній файл, файл лише із заголовком і поведінка аналізу на порожньому списку (середнє 0.0, найдовше – None).

15. Чим тест поведінки відрізняється від перевірки внутрішньої реалізації?

Перевіряє результат через публічні функції, а не імена внутрішніх змінних, тож не ламається при рефакторингу.

16. Які файли знаходить pytest?

test_*.py або *_test.py і функції test_* у них.

17. Які перевірки виконує ruff?

ruff check – помилки й стиль (правила E, F, W, B, UP), ruff format --check – форматування без зміни файлів.

18. Які коди завершення має CLI для успіху та очікуваної помилки?

0 – успіх, 2 – помилка вхідних даних.

19. Чому в CI запускаються і тести, і аналізатор, і пакетування?

Тести перевіряють поведінку, ruff – якість, а збірка wheel – що пакет можна встановити; кожна перевірка ловить свій клас проблем.

20. Які дані та результати потрібно задекларувати в REPORT?

Заголовок і типи CSV, threshold, приклад даних і повного звіту, коди завершення, результати pytest, ruff, wheel і CI.

## Висновки

Створено Python-пакет із модульним завантаженням CSV, функціями аналізу на списках, словниках, множинах і comprehensions, детермінованим звітом і CLI. 19 тестів pytest проходять, ruff не має зауважень, wheel збирається й працює в чистому середовищі. Наступна робота перенесе обчислення на класи з @property, @dataclass і спеціальними методами.

