"""Тести завантаження й перевірки CSV."""

from pathlib import Path

import pytest

from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records

HEADER = "date,kind,duration,distance,pulse\n"


def write_csv(tmp_path: Path, body: str) -> Path:
    """Записує тимчасовий CSV у UTF-8."""
    path = tmp_path / "input.csv"
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def test_loads_and_converts_types(tmp_path: Path) -> None:
    """Перевіряє перетворення рядкових полів на int і float."""
    records = load_records(write_csv(tmp_path, "2026-09-01,біг,45,8.5,148\n"))
    assert records == [
        {"date": "2026-09-01", "kind": "біг", "duration": 45, "distance": 8.5, "pulse": 148}
    ]


def test_text_with_comma_is_one_field(tmp_path: Path) -> None:
    """Перевіряє, що поле в лапках із комою не розбивається."""
    records = load_records(write_csv(tmp_path, '2026-09-03,"біг, інтервали",40,6.0,165\n'))
    assert records[0]["kind"] == "біг, інтервали"


def test_empty_file_and_header_only(tmp_path: Path) -> None:
    """Перевіряє порожній файл і файл лише із заголовком."""
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    assert load_records(empty) == []
    assert load_records(write_csv(tmp_path, "")) == []


def test_broken_number_has_row_and_cause(tmp_path: Path) -> None:
    """Перевіряє номер рядка, назву поля та першопричину помилки числа."""
    path = write_csv(tmp_path, "2026-09-01,біг,45,8.5,148\n2026-09-02,біг,багато,5,140\n")
    with pytest.raises(DataError, match="Рядок 3: поле duration") as info:
        load_records(path)
    assert isinstance(info.value.__cause__, ValueError)


def test_negative_and_zero_pulse_rejected(tmp_path: Path) -> None:
    """Перевіряє від'ємне значення та нульовий пульс."""
    with pytest.raises(DataError, match="від'ємним"):
        load_records(write_csv(tmp_path, "2026-09-01,біг,45,-1,148\n"))
    with pytest.raises(DataError, match="pulse має бути додатним"):
        load_records(write_csv(tmp_path, "2026-09-01,біг,45,1,0\n"))


def test_missing_column_rejected(tmp_path: Path) -> None:
    """Перевіряє відсутній стовпець у заголовку."""
    path = tmp_path / "bad.csv"
    path.write_text("date,kind,duration,distance\n2026-09-01,біг,45,8.5\n", encoding="utf-8")
    with pytest.raises(DataError, match="заголовок"):
        load_records(path)


def test_missing_value_in_row_rejected(tmp_path: Path) -> None:
    """Перевіряє відсутнє значення в рядку (рядок коротший за заголовок)."""
    with pytest.raises(DataError, match="Рядок 2"):
        load_records(write_csv(tmp_path, "2026-09-01,біг,45\n"))
    with pytest.raises(DataError, match="kind порожнє"):
        load_records(write_csv(tmp_path, "2026-09-01,,45,8.5,148\n"))


def test_missing_file_wrapped(tmp_path: Path) -> None:
    """Перевіряє, що помилка файлової системи стає DataError із причиною."""
    with pytest.raises(DataError) as info:
        load_records(tmp_path / "missing.csv")
    assert isinstance(info.value.__cause__, OSError)
