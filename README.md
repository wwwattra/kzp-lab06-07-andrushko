# ООП-звіт про спортивні тренування (Python, ЛР7, варіант 2)

Пакет `kzp_lab07` читає `data/input.csv` (заголовок `date,kind,duration,distance,pulse`),
перетворює рядки на об'єкти `Running` / `Cycling` (базовий клас `Training` з `@property`),
обчислює навантаження через спільний метод `load()` і формує звіт, сумісний із ЛР6.

```text
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
.venv\Scripts\ruff check .
.venv\Scripts\ruff format --check .
.venv\Scripts\python -m build --wheel
.venv\Scripts\python -m kzp_lab07.cli data\input.csv reports\summary.txt
```

Коди завершення CLI: `0` - успіх, `2` - помилка вхідних даних. Звіт - у `REPORT.md`.
