"""Тести завантаження, аналізу, сумісності звіту та CLI."""

from pathlib import Path

import pytest

from kzp_lab07.analysis import make_summary
from kzp_lab07.cli import main
from kzp_lab07.errors import DataError
from kzp_lab07.loader import load_trainings
from kzp_lab07.models import Cycling, Running

DATA = Path(__file__).resolve().parent.parent / "data"
HEADER = "date,kind,duration,distance,pulse\n"


def write_csv(tmp_path: Path, body: str) -> Path:
    """Записує тимчасовий CSV у UTF-8."""
    path = tmp_path / "input.csv"
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def test_loader_builds_subtypes() -> None:
    """Перевіряє, що loader створює об'єкти обох підтипів."""
    trainings = load_trainings(DATA / "input.csv")
    assert len(trainings) == 8
    assert {type(training) for training in trainings} == {Running, Cycling}
    assert isinstance(trainings[2], Running)  # "біг, інтервали"


def test_loader_reports_row_number(tmp_path: Path) -> None:
    """Перевіряє номер рядка і причину для помилкового поля та невідомого виду."""
    with pytest.raises(DataError, match="Рядок 2") as info:
        load_trainings(write_csv(tmp_path, "2026-09-01,біг,45,8.5,999\n"))
    assert isinstance(info.value.__cause__, ValueError)
    with pytest.raises(DataError, match="невідомий вид"):
        load_trainings(write_csv(tmp_path, "2026-09-01,плавання,45,1.5,120\n"))
    with pytest.raises(DataError, match="поле duration має бути числом"):
        load_trainings(write_csv(tmp_path, "2026-09-01,біг,сорок,1.5,120\n"))


def test_empty_input(tmp_path: Path) -> None:
    """Перевіряє порожній вхід і підсумок без даних."""
    assert load_trainings(write_csv(tmp_path, "")) == []
    summary = make_summary([])
    assert summary["count"] == 0
    assert summary["longest"] is None
    assert summary["best"] is None
    assert summary["summary"].total_load == 0


def test_duplicates_are_equal() -> None:
    """Перевіряє дубльоване значення для рівності об'єктів."""
    first = Running("2026-09-01", "біг", 45, 8.5, 148)
    trainings = [first, Running("2026-09-01", "біг", 45, 8.5, 148)]
    assert trainings[0] == trainings[1]
    assert trainings.count(first) == 2


def test_report_is_compatible_with_lab06(tmp_path: Path) -> None:
    """Перевіряє, що перші рядки звіту збігаються зі словниковою версією ЛР6."""
    output = tmp_path / "summary.txt"
    assert main([str(DATA / "input.csv"), str(output)]) == 0
    lines = output.read_text(encoding="utf-8").splitlines()
    expected = (DATA / "lab06-summary.txt").read_text(encoding="utf-8").splitlines()
    assert lines[: len(expected)] == expected


def test_cli_error_code(tmp_path: Path, capsys) -> None:
    """Перевіряє ненульовий код для пошкодженого CSV."""
    assert main([str(DATA / "broken.csv"), str(tmp_path / "out.txt")]) == 2
    assert "Рядок 3" in capsys.readouterr().err
