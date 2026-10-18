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
