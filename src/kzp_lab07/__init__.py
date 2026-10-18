"""Об'єктно-орієнтований звіт про спортивні тренування (КЗП, ЛР7, варіант 2)."""

from .errors import DataError
from .models import Cycling, ReportSummary, Running, Training

__all__ = ["Cycling", "DataError", "ReportSummary", "Running", "Training"]
__version__ = "0.2.0"
