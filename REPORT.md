# Звіт до лабораторної роботи №7

з дисципліни «Кросплатформні засоби програмування», тема «Об'єктно-орієнтована обробка даних у Python». Варіант 2. Спортивні тренування.
Виконав: студент групи КІ-302 Андрушко А. І. Прийняв: Олексів М. В.

## Тема, номер і варіант

Лабораторна робота № 7 «Об'єктно-орієнтована обробка даних у Python». Варіант 2 – «Спортивні тренування»: базовий клас Training, підтипи Running і Cycling, спільна операція load() за пульсом або дистанцією, підсумок – навантаження за видом. ОС – Windows 10 (64-bit), Python 3.12.10.

Посилання на GitHub-репозиторій: https://github.com/[ваш-логін]/kzp-lab-andrushko (каталог або гілка lab07), Git-тег v0.2.0-py.

## Стан до і після

*Таблиця 1 – Словникова модель ЛР6 → об'єктна модель ЛР7*

| До роботи | Після роботи |
|---|---|
| dict[str, object] для запису | екземпляр Running або Cycling |
| перевірки в loader | перевірки у властивостях і конструкторі |
| доступ record["duration"] | властивість training.duration |
| одна функція для всіх записів | підтипи з різною формулою load() |
| словник підсумку | незмінний @dataclass(frozen=True) ReportSummary |

CSV-поля та перші 11 рядків звіту залишилися такими самими, як у ЛР6; додано розділ навантаження за видом і найбільше навантаження.

## Модель

Training.__init__ встановлює date і kind (лише читання, порожні значення відхиляються) та присвоює duration, distance, pulse через setter-и властивостей. Інваріанти: тривалість і дистанція невід'ємні, пульс у діапазоні 30–250. Setter записує внутрішнє поле _duration, а не властивість, щоб не викликати себе рекурсивно. Спеціальні методи: __str__ для читача («2026-09-01 біг, 45 хв»), __repr__ для діагностики, __eq__ порівнює однакові підтипи за повним станом і повертає NotImplemented для несумісного типу. Оскільки об'єкт змінюваний, __hash__ = None. Впорядкування – через key=Training.sort_key (довші першими, далі за датою).

*Лістинг 1 – src/kzp_lab07/models.py*

```text
"""Класи предметної області: тренування, підтипи, протокол і підсумок."""

from dataclasses import dataclass
from typing import Protocol

class Loaded(Protocol):
    """Протокол об'єктів, що вміють обчислювати навантаження."""

    def load(self) -> float:
        """Повертає навантаження в умовних балах."""
        ...

class Training:
    """Базове тренування з перевіреним спільним станом."""

    def __init__(self, date: str, kind: str, duration: int, distance: float, pulse: int) -> None:
        """Створює тренування; значення перевіряються у setter-ах властивостей."""
        if not date or not date.strip():
            raise ValueError("Дата не може бути порожньою")
        if not kind or not kind.strip():
            raise ValueError("Вид не може бути порожнім")
        self._date = date.strip()
        self._kind = kind.strip()
        self.duration = duration
        self.distance = distance
        self.pulse = pulse

    @property
    def date(self) -> str:
        """Повертає дату у форматі YYYY-MM-DD (лише читання)."""
        return self._date

    @property
    def kind(self) -> str:
        """Повертає вид тренування (лише читання)."""
        return self._kind

    @property
    def duration(self) -> int:
        """Повертає тривалість у хвилинах."""
        return self._duration

    @duration.setter
    def duration(self, value: int) -> None:
        """Встановлює невід'ємну тривалість."""
        # Записуємо внутрішнє поле, а не властивість, щоб не викликати setter рекурсивно.
        if value < 0:
            raise ValueError("Тривалість не може бути від'ємною")
        self._duration = value

    @property
    def distance(self) -> float:
        """Повертає дистанцію в кілометрах."""
        return self._distance

    @distance.setter
    def distance(self, value: float) -> None:
        """Встановлює невід'ємну дистанцію."""
        if value < 0:
            raise ValueError("Дистанція не може бути від'ємною")
        self._distance = float(value)

    @property
    def pulse(self) -> int:
        """Повертає середній пульс."""
        return self._pulse

    @pulse.setter
    def pulse(self, value: int) -> None:
        """Встановлює пульс у фізично допустимому діапазоні 30-250."""
        if not 30 <= value <= 250:
            raise ValueError("Пульс має бути в діапазоні 30-250")
        self._pulse = value

    def load(self) -> float:
        """Оголошує операцію навантаження для підтипів."""
        raise NotImplementedError

    def sort_key(self) -> tuple[int, str]:
        """Повертає ключ впорядкування: довші тренування першими, далі за датою."""
        return (-self.duration, self.date)

    def _state(self) -> tuple[str, str, int, float, int]:
        """Повертає кортеж стану для порівняння."""
        return (self.date, self.kind, self.duration, self.distance, self.pulse)

    def __str__(self) -> str:
        """Повертає коротке подання для читача."""
        return f"{self.date} {self.kind}, {self.duration} хв"

    def __repr__(self) -> str:
        """Повертає діагностичне подання об'єкта."""
        return (
            f"{type(self).__name__}(date={self.date!r}, kind={self.kind!r}, "
            f"duration={self.duration!r}, distance={self.distance!r}, pulse={self.pulse!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Порівнює тренування одного підтипу за повним станом."""
        if not isinstance(other, Training):
            return NotImplemented
        return type(self) is type(other) and self._state() == other._state()

    __hash__ = None  # Об'єкт змінюваний через setter-и, тому не використовується як ключ.

class Running(Training):
    """Біг: навантаження залежить від тривалості та пульсу."""

    def load(self) -> float:
        """Обчислює навантаження: хвилини · пульс / 100."""
        return self.duration * self.pulse / 100

class Cycling(Training):
    """Велосипед: навантаження залежить від дистанції та тривалості."""

    def load(self) -> float:
        """Обчислює навантаження: км · 1.5 + хвилини · 0.5."""
        return self.distance * 1.5 + self.duration * 0.5

@dataclass(frozen=True)
class ReportSummary:
    """Незмінний підсумок обробки тренувань."""

    count: int
    selected: int
    average_pulse: float
    total_load: float

def best_by_load(items: list[Loaded]) -> Loaded | None:
    """Повертає об'єкт із найбільшим навантаженням або None для порожнього списку."""
    # Функція знає лише про load(), тому новий підтип не потребує змін тут.
    return max(items, key=lambda item: item.load(), default=None)
```

## Dataclass

ReportSummary(count, selected, average_pulse, total_load) оголошено @dataclass(frozen=True): автоматично створено __init__, __repr__, __eq__, а спроба змінити поле кидає FrozenInstanceError. Це просте незмінне значення результату, тому dataclass доречніший за звичайний клас; для Training обрано звичайний клас, бо він має setter-валідацію та підтипи.

## Підтипи та протокол

*Таблиця 2 – Формули спільної операції load()*

| Підтип | Вид у CSV | load(), бали |
|---|---|---|
| Running | «біг», «біг, інтервали» | тривалість · пульс / 100 |
| Cycling | «велосипед» | 1.5 · км + 0.5 · тривалість |

Протокол Loaded(Protocol) описує один метод load() -> float. Функція best_by_load(items: list[Loaded]) викликає лише item.load() і не перевіряє клас – це качина типізація: новий підтип із методом load() працюватиме без змін. super() не потрібен у підтипах, бо вони не додають полів і використовують __init__ базового класу.

## Модулі

*Таблиця 3 – Модулі пакета src/kzp_lab07*

| Модуль | Призначення |
|---|---|
| models.py | Training, Running, Cycling, Loaded, ReportSummary, best_by_load |
| loader.py | CSV → об'єкти: factory build_training обирає підтип за kind один раз |
| analysis.py | відбір, множина, агрегати, load_by_kind, make_summary – без isinstance |
| reporting.py | текст звіту, сумісний з ЛР6, і запис через with |
| errors.py | DataError |
| cli.py | аргументи, коди 0/2 |

*Лістинг 2 – src/kzp_lab07/loader.py*

```text
"""Читання CSV і перетворення рядків на об'єкти-тренування."""

import csv
from pathlib import Path

from .errors import DataError
from .models import Cycling, Running, Training

REQUIRED_FIELDS = ("date", "kind", "duration", "distance", "pulse")

def build_training(row: dict[str, str], row_number: int) -> Training:
    """Перетворює CSV-рядок на відповідний підтип тренування."""
    kind = (row.get("kind") or "").strip()
    common: dict[str, object] = {"date": row.get("date") or "", "kind": kind}
    for field, convert in (("duration", int), ("distance", float), ("pulse", int)):
        try:
            common[field] = convert(row[field])
        except (KeyError, TypeError, ValueError) as error:
            raise DataError(f"Рядок {row_number}: поле {field} має бути числом") from error
    # Вибір підтипу виконується один раз на межі завантаження.
    if kind.startswith("біг"):
        factory = Running
    elif kind.startswith("велосипед"):
        factory = Cycling
    else:
        raise DataError(f"Рядок {row_number}: невідомий вид тренування: {kind!r}")
    try:
        return factory(**common)
    except (TypeError, ValueError) as error:
        raise DataError(f"Рядок {row_number}: {error}") from error

def load_trainings(path: Path) -> list[Training]:
    """Читає CSV у UTF-8 і повертає список об'єктів-тренувань."""
    try:
        with path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames is None:
                return []
            if tuple(reader.fieldnames) != REQUIRED_FIELDS:
                raise DataError(
                    f"Некоректний заголовок CSV: {reader.fieldnames}, "
                    f"очікується {list(REQUIRED_FIELDS)}"
                )
            return [build_training(row, number) for number, row in enumerate(reader, start=2)]
    except OSError as error:
        raise DataError(f"Не вдалося прочитати файл: {path}") from error
```

*Лістинг 3 – src/kzp_lab07/analysis.py*

```text
"""Обчислення над об'єктами тренувань без перевірок конкретного підтипу."""

from .models import ReportSummary, Training, best_by_load

MIN_DURATION = 45

def long_trainings(trainings: list[Training], minimum: int = MIN_DURATION) -> list[Training]:
    """Повертає тренування тривалістю не менше заданої кількості хвилин."""
    return [training for training in trainings if training.duration >= minimum]

def kinds(trainings: list[Training]) -> set[str]:
    """Повертає множину унікальних видів."""
    return {training.kind for training in trainings}

def distance_by_kind(trainings: list[Training]) -> dict[str, float]:
    """Обчислює сумарну дистанцію за видом у стабільному порядку."""
    return {
        kind: sum(training.distance for training in trainings if training.kind == kind)
        for kind in sorted(kinds(trainings))
    }

def load_by_kind(trainings: list[Training]) -> dict[str, float]:
    """Обчислює поліморфне навантаження за видом через спільний метод load()."""
    return {
        kind: sum(training.load() for training in trainings if training.kind == kind)
        for kind in sorted(kinds(trainings))
    }

def average_pulse(trainings: list[Training]) -> float:
    """Повертає середній пульс або 0.0 для порожнього набору."""
    if not trainings:
        return 0.0
    return sum(training.pulse for training in trainings) / len(trainings)

def longest_training(trainings: list[Training]) -> Training | None:
    """Повертає найдовше тренування (перше за ключем сортування) або None."""
    ordered = sorted(trainings, key=Training.sort_key)
    return ordered[0] if ordered else None

def make_summary(trainings: list[Training], minimum_duration: int = MIN_DURATION) -> dict:
    """Формує підсумок звіту; ключі сумісні зі словниковою версією ЛР6."""
    selected = long_trainings(trainings, minimum_duration)
    return {
        "count": len(trainings),
        "selected": len(selected),
        "kinds": kinds(trainings),
        "distance_by_kind": distance_by_kind(trainings),
        "average_pulse": average_pulse(trainings),
        "longest": longest_training(trainings),
        "minutes_long": float(sum(training.duration for training in selected)),
        "load_by_kind": load_by_kind(trainings),
        "best": best_by_load(trainings),
        "summary": ReportSummary(
            count=len(trainings),
            selected=len(selected),
            average_pulse=average_pulse(trainings),
            total_load=sum(training.load() for training in trainings),
        ),
    }
```

## Тестування

14 тестів pytest: setter-и для коректного, нульового й граничних значень (30 і 250); відхилення помилкових значень; властивості лише для читання; frozen dataclass і його рівність; __str__, __repr__, __eq__ і NotImplemented; різні формули load(); протокольна функція на обох підтипах і порожньому списку; впорядкування через key; loader створює обидва підтипи; номер рядка й причина помилки; невідомий вид; порожній вхід; рівність дубльованих записів; сумісність звіту з ЛР6; CLI з кодом 2.

Знайдений дефект під час розробки. Перший запуск pytest дав 1 падіння: тест test_protocol_function_works_with_both_subtypes очікував, що найбільше навантаження має біг, але велосипед 41.3 км/120 хв дає 1.5·41.3 + 0.5·120 = 121.95 > 90.0. Помилку було в очікуванні тесту, а не в коді; тест виправлено з поясненням обчислення. Також повідомлення loader уточнено назвою поля («поле duration має бути числом»).

*Лістинг 4 – tests/test_models.py*

```text
"""Тести класів, властивостей, dataclass і спеціальних методів."""

import dataclasses

import pytest

from kzp_lab07.models import Cycling, ReportSummary, Running, best_by_load

def test_property_setter_accepts_boundaries() -> None:
    """Перевіряє коректне, нульове та граничні значення setter-ів."""
    run = Running("2026-09-01", "біг", 45, 8.5, 148)
    run.duration = 0
    run.pulse = 30
    assert run.duration == 0
    run.pulse = 250
    assert run.pulse == 250

def test_property_setter_rejects_invalid() -> None:
    """Перевіряє відхилення помилкових значень."""
    run = Running("2026-09-01", "біг", 45, 8.5, 148)
    with pytest.raises(ValueError):
        run.duration = -1
    with pytest.raises(ValueError):
        run.pulse = 251
    with pytest.raises(ValueError):
        Cycling("2026-09-02", "велосипед", 90, -1.0, 132)
    with pytest.raises(ValueError):
        Running("", "біг", 45, 8.5, 148)

def test_readonly_properties() -> None:
    """Перевіряє, що дату й вид не можна перезаписати."""
    run = Running("2026-09-01", "біг", 45, 8.5, 148)
    with pytest.raises(AttributeError):
        run.kind = "велосипед"

def test_summary_is_frozen_and_comparable() -> None:
    """Перевіряє незмінність і рівність frozen dataclass."""
    summary = ReportSummary(8, 6, 143.5, 549.6)
    assert summary == ReportSummary(8, 6, 143.5, 549.6)
    with pytest.raises(dataclasses.FrozenInstanceError):
        summary.count = 3

def test_str_repr_eq() -> None:
    """Перевіряє текстові подання та рівність за станом і підтипом."""
    first = Running("2026-09-01", "біг", 45, 8.5, 148)
    assert str(first) == "2026-09-01 біг, 45 хв"
    assert repr(first) == (
        "Running(date='2026-09-01', kind='біг', duration=45, distance=8.5, pulse=148)"
    )
    assert first == Running("2026-09-01", "біг", 45, 8.5, 148)
    assert first != Cycling("2026-09-01", "біг", 45, 8.5, 148)
    assert first.__eq__("рядок") is NotImplemented

def test_subtypes_have_different_load() -> None:
    """Перевіряє різні формули спільної операції load()."""
    run = Running("2026-09-01", "біг", 60, 10.0, 150)
    bike = Cycling("2026-09-01", "велосипед", 60, 10.0, 150)
    assert run.load() == pytest.approx(90.0)
    assert bike.load() == pytest.approx(45.0)

def test_protocol_function_works_with_both_subtypes() -> None:
    """Перевіряє duck typing: функція не знає конкретного класу."""
    run = Running("2026-09-01", "біг", 60, 10.0, 150)
    bike = Cycling("2026-09-08", "велосипед", 120, 41.3, 138)
    # 41.3 * 1.5 + 120 * 0.5 = 121.95 > 60 * 150 / 100 = 90.0
    assert best_by_load([run, bike]) is bike
    assert best_by_load([run]) is run
    assert best_by_load([]) is None

def test_sort_key_orders_longest_first() -> None:
    """Перевіряє впорядкування через key."""
    items = [
        Running("2026-09-05", "біг", 30, 5.2, 140),
        Cycling("2026-09-08", "велосипед", 120, 41.3, 138),
        Running("2026-09-01", "біг", 45, 8.5, 148),
    ]
    assert [item.duration for item in sorted(items, key=lambda item: item.sort_key())] == [
        120,
        45,
        30,
    ]
```

*Лістинг 5 – python -m pytest -v*

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\user\kzp-labs\lab07
configfile: pyproject.toml
collected 14 items

tests\test_loader_cli.py ......                                          [ 42%]
tests\test_models.py ........                                            [100%]

============================= 14 passed in 0.11s ==============================
```

## Порівняння звітів

Тест test_report_is_compatible_with_lab06 порівнює перші рядки нового звіту зі збереженим звітом ЛР6 (data/lab06-summary.txt) на тому самому CSV: усі 11 рядків звіту ЛР6 збігаються, зокрема рядок «Найдовше тренування: 2026-09-08 велосипед, 120 хв», який тепер формує метод __str__ об'єкта.

*Лістинг 6 – Повний вивід CLI ЛР7*

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
Навантаження за видом (load), бали:
  біг: 285.75
  біг, інтервали: 66.00
  велосипед: 277.20
Найбільше навантаження: 2026-09-08 велосипед, 120 хв (121.95)
Звіт записано у reports\summary.txt
```

Перевірка навантаження для бігу: 45·148/100 + 30·140/100 + 75·145/100 + 45·152/100 = 66.6 + 42 + 108.75 + 68.4 = 285.75 бала.

## Інфраструктура

*Лістинг 7 – ruff check .*

```text
All checks passed!
```

*Лістинг 8 – ruff format --check .*

```text
10 files already formatted
```

Wheel kzp_training_oop-0.2.0-py3-none-any.whl зібрано python -m build --wheel, встановлено pip install --no-deps в окреме середовище .venv-wheel; CLI з нього повернув код 0 для data\input.csv і код 2 для data\broken.csv («Рядок 3: поле duration має бути числом»). CI (.github/workflows/ci.yml) запускає pytest, ruff і збірку wheel на Ubuntu, Windows і macOS: посилання на запуск і артефакт – після push.

*Лістинг 9 – pyproject.toml*

```text
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "kzp-training-oop"
version = "0.2.0"
description = "Object-oriented report for sport trainings (KZP, variant 2)"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.8", "build>=1.2"]

[project.scripts]
kzp-lab07 = "kzp_lab07.cli:main"

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

## GitHub Issues і Pull Request

*Таблиця 4 – План GitHub Issues → зміна → перевірка*

| Issue | Мітка | Зміна | Перевірка |
|---|---|---|---|
| Базовий клас і властивості | feature | Training, setter-и | test_property_* |
| Dataclass підсумку | feature | ReportSummary frozen | test_summary_is_frozen… |
| Підтипи й протокол | feature | Running, Cycling, Loaded | test_subtypes…, test_protocol… |
| Loader → об'єкти | feature | build_training | test_loader_* |
| [bug] Хибне очікування в тесті протоколу | bug | виправлено очікування | pytest зелений |
| Документація ЛР7 | docs | README, docstrings, REPORT | рев'ю PR |

## Академічна доброчесність

Заповніть самостійно: використані інструменти ШІ або твердження, що вони не використовувалися; ролі, запити, прийняті й відхилені рекомендації; власний внесок і підтвердження розуміння всього поданого коду.

## Відповіді на контрольні питання

1. Чим клас відрізняється від екземпляра?

Клас описує структуру й поведінку (Running), екземпляр – конкретний об'єкт із власним станом (Running("2026-09-01", "біг", 45, 8.5, 148)).

2. Яку роль виконує __init__ і що означає self?

__init__ встановлює початковий стан нового екземпляра; self – посилання на поточний екземпляр, передається першим параметром методів.

3. Для чого застосовується @property?

Щоб доступ виглядав як до поля, а читання чи запис виконували метод із перевіркою інваріанта.

4. Чому setter записує у внутрішнє поле, а не у властивість?

self.duration = value усередині setter викликав би той самий setter нескінченно; тому пишемо self._duration.

5. Яку поведінку автоматично додає @dataclass?

__init__, __repr__, __eq__ (а з frozen=True – також заборону присвоєння й __hash__).

6. Навіщо застосовується frozen=True?

Щоб підсумок не можна було змінити після створення й намір незмінності був явним.

7. Чим відрізняються __str__ і __repr__?

__str__ – подання для читача у звіті, __repr__ – однозначне діагностичне подання для розробника.

8. Як __eq__ має поводитися з несумісним типом?

Повертати NotImplemented, щоб Python спробував порівняння з іншого боку або повернув False.

9. Коли сортування через key краще за реалізацію __lt__?

Коли критерій залежить від конкретного звіту, а не є природним порядком сутності; key задається в місці використання.

10. Яку роль виконує super()?

Викликає наступну реалізацію методу в порядку MRO, зазвичай ініціалізацію базового класу.

11. Що таке MRO і чому його потрібно враховувати?

Method Resolution Order – порядок пошуку методів у ієрархії; при множинному успадкуванні super() звертається не обов'язково до прямого батька.

12. Що означає качина типізація?

Важливо, що об'єкт уміє (load()), а не його клас; best_by_load працює з будь-яким таким об'єктом.

13. Яку проблему розв'язує Protocol?

Дає статичний опис очікуваної поведінки для перевірки типів без примусового успадкування.

14. Чому analysis не повинен перевіряти кожен конкретний підтип?

Інакше додавання підтипу вимагало б змін у кожній функції; формула має жити в підтипі.

15. Де має виконуватися перетворення словника на об'єкт?

На межі завантаження – у loader (build_training), щоб analysis отримував лише коректні об'єкти.

16. Чому модулі не повинні запускати CLI під час імпорту?

Імпорт у тестах або іншому коді не має виконувати програму; тому запуск захищено if __name__ == "__main__":.

17. Які властивості об'єктів перевіряються тестами?

Валідація setter-ів, лише-читання, незмінність dataclass, рівність, текстові подання, різна поведінка підтипів і робота через протокол.

18. Для чого потрібні pytest, ruff і wheel?

pytest перевіряє поведінку, ruff – якість і форматування коду, wheel – можливість встановити й запустити пакет.

19. Які крайові випадки має містити тестовий набір?

Порожній вхід, граничні значення setter-а, нульове значення, помилковий рядок CSV, невідомий вид, дубльовані записи.

20. Які результати потрібно задекларувати в REPORT?

Класи, поля, підтипи й формули, старий і новий звіти, результати pytest, ruff, wheel, коди CLI та CI.

## Висновки

Словникові записи ЛР6 перетворено на об'єкти з інкапсульованими властивостями, двома підтипами зі спільною операцією load(), протоколом Loaded і незмінним ReportSummary. Зовнішній звіт сумісний із ЛР6, 14 тестів проходять, ruff чистий, wheel встановлюється й працює. Об'єктна модель може надалі розширюватися власним зберіганням і контекстними менеджерами.

