"""Python-звіт про спортивні тренування (КЗП, ЛР6, варіант 2)."""

from .analysis import make_summary
from .errors import DataError
from .loader import load_records

__all__ = ["DataError", "load_records", "make_summary"]
__version__ = "0.1.0"
