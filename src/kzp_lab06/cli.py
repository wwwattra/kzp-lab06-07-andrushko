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
