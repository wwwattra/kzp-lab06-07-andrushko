"""Тести звіту та CLI."""

from pathlib import Path

from kzp_lab06.cli import main
from kzp_lab06.reporting import write_report

DATA = Path(__file__).resolve().parent.parent / "data"


def test_write_report_utf8(tmp_path: Path) -> None:
    """Перевіряє запис і читання UTF-8 звіту, зокрема створення каталогу."""
    output = tmp_path / "reports" / "report.txt"
    write_report(output, "Готово: біг\n")
    assert output.read_text(encoding="utf-8") == "Готово: біг\n"


def test_cli_success(tmp_path: Path) -> None:
    """Перевіряє успішний код завершення та вміст звіту."""
    output = tmp_path / "summary.txt"
    assert main([str(DATA / "input.csv"), str(output)]) == 0
    text = output.read_text(encoding="utf-8")
    assert "Записів: 8" in text
    assert "Середній пульс: 143.50" in text
    assert "біг, інтервали" in text


def test_cli_error_code(tmp_path: Path, capsys) -> None:
    """Перевіряє ненульовий код і повідомлення в stderr для пошкодженого CSV."""
    output = tmp_path / "summary.txt"
    assert main([str(DATA / "broken.csv"), str(output)]) == 2
    assert "Рядок 3" in capsys.readouterr().err
    assert not output.exists()
