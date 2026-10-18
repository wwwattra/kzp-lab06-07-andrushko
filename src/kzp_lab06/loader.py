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
