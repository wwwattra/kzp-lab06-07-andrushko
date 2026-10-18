# Звіт про спортивні тренування (Python, ЛР6, варіант 2)

Пакет `kzp_lab06` читає `data/input.csv` (UTF-8, заголовок `date,kind,duration,distance,pulse`),
перевіряє рядки, будує звіт за списками, словниками та множинами й записує його у файл.

```text
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest
.venv\Scripts\ruff check .
.venv\Scripts\ruff format --check .
.venv\Scripts\python -m build --wheel
.venv\Scripts\python -m kzp_lab06.cli data\input.csv reports\summary.txt
```

Коди завершення CLI: `0` - успіх, `2` - помилка вхідних даних (повідомлення у stderr).
