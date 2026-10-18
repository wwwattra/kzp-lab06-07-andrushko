"""Тести функцій аналізу."""

import pytest

from kzp_lab06.analysis import (
    average_pulse,
    distance_by_kind,
    kinds,
    long_trainings,
    longest_training,
    make_summary,
)

RECORDS = [
    {"date": "2026-09-01", "kind": "біг", "duration": 45, "distance": 8.5, "pulse": 148},
    {"date": "2026-09-02", "kind": "велосипед", "duration": 90, "distance": 32.0, "pulse": 132},
    {"date": "2026-09-05", "kind": "біг", "duration": 30, "distance": 5.2, "pulse": 140},
]


def test_filter_includes_boundary() -> None:
    """Перевіряє, що 45 хв входить у відбір, а 30 - ні."""
    assert [record["date"] for record in long_trainings(RECORDS)] == ["2026-09-01", "2026-09-02"]


def test_filter_can_return_empty_result() -> None:
    """Перевіряє явний порожній результат відбору."""
    assert long_trainings(RECORDS, minimum=200) == []


def test_set_removes_duplicates() -> None:
    """Перевіряє, що множина видів не містить дублікатів."""
    assert kinds(RECORDS) == {"біг", "велосипед"}


def test_distance_by_kind_is_deterministic() -> None:
    """Перевіряє значення і порядок ключів словника агрегатів."""
    result = distance_by_kind(list(reversed(RECORDS)))
    assert list(result) == ["біг", "велосипед"]
    assert result["біг"] == pytest.approx(13.7)


def test_average_and_longest() -> None:
    """Перевіряє середній пульс і найдовше тренування."""
    assert average_pulse(RECORDS) == pytest.approx(140.0)
    assert longest_training(RECORDS)["kind"] == "велосипед"


def test_empty_input() -> None:
    """Перевіряє поведінку на порожньому вході."""
    summary = make_summary([], "duration")
    assert summary["count"] == 0
    assert summary["distance_by_kind"] == {}
    assert summary["average_pulse"] == 0.0
    assert summary["longest"] is None
    assert summary["duration"] == 0.0


def test_make_summary_args_defaults_and_kwargs() -> None:
    """Перевіряє *args, типовий параметр і **kwargs."""
    summary = make_summary(RECORDS, "duration", "distance", duration="Хвилини", distance="Км")
    assert summary["selected"] == 2
    assert summary["Хвилини"] == 135.0
    assert summary["Км"] == pytest.approx(40.5)
    strict = make_summary(RECORDS, "duration", minimum_duration=60)
    assert strict["duration"] == 90.0


def test_unknown_metric_rejected() -> None:
    """Перевіряє явну помилку для невідомої метрики."""
    with pytest.raises(ValueError, match="Невідома метрика"):
        make_summary(RECORDS, "speed")
