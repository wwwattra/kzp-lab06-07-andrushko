"""Тести класів, властивостей, dataclass і спеціальних методів."""

import dataclasses

import pytest

from kzp_lab07.models import Cycling, ReportSummary, Running, best_by_load


def test_property_setter_accepts_boundaries() -> None:
    """Перевіряє коректне, нульове та граничні значення setter-ів."""
    run = Running("2026-09-01", "біг", 45, 8.5, 148)
    run.duration = 0
    run.pulse = 30
    assert run.duration == 0
    run.pulse = 250
    assert run.pulse == 250


def test_property_setter_rejects_invalid() -> None:
    """Перевіряє відхилення помилкових значень."""
    run = Running("2026-09-01", "біг", 45, 8.5, 148)
    with pytest.raises(ValueError):
        run.duration = -1
    with pytest.raises(ValueError):
        run.pulse = 251
    with pytest.raises(ValueError):
        Cycling("2026-09-02", "велосипед", 90, -1.0, 132)
    with pytest.raises(ValueError):
        Running("", "біг", 45, 8.5, 148)


def test_readonly_properties() -> None:
    """Перевіряє, що дату й вид не можна перезаписати."""
    run = Running("2026-09-01", "біг", 45, 8.5, 148)
    with pytest.raises(AttributeError):
        run.kind = "велосипед"


def test_summary_is_frozen_and_comparable() -> None:
    """Перевіряє незмінність і рівність frozen dataclass."""
    summary = ReportSummary(8, 6, 143.5, 549.6)
    assert summary == ReportSummary(8, 6, 143.5, 549.6)
    with pytest.raises(dataclasses.FrozenInstanceError):
        summary.count = 3


def test_str_repr_eq() -> None:
    """Перевіряє текстові подання та рівність за станом і підтипом."""
    first = Running("2026-09-01", "біг", 45, 8.5, 148)
    assert str(first) == "2026-09-01 біг, 45 хв"
    assert repr(first) == (
        "Running(date='2026-09-01', kind='біг', duration=45, distance=8.5, pulse=148)"
    )
    assert first == Running("2026-09-01", "біг", 45, 8.5, 148)
    assert first != Cycling("2026-09-01", "біг", 45, 8.5, 148)
    assert first.__eq__("рядок") is NotImplemented


def test_subtypes_have_different_load() -> None:
    """Перевіряє різні формули спільної операції load()."""
    run = Running("2026-09-01", "біг", 60, 10.0, 150)
    bike = Cycling("2026-09-01", "велосипед", 60, 10.0, 150)
    assert run.load() == pytest.approx(90.0)
    assert bike.load() == pytest.approx(45.0)


def test_protocol_function_works_with_both_subtypes() -> None:
    """Перевіряє duck typing: функція не знає конкретного класу."""
    run = Running("2026-09-01", "біг", 60, 10.0, 150)
    bike = Cycling("2026-09-08", "велосипед", 120, 41.3, 138)
    # 41.3 * 1.5 + 120 * 0.5 = 121.95 > 60 * 150 / 100 = 90.0
    assert best_by_load([run, bike]) is bike
    assert best_by_load([run]) is run
    assert best_by_load([]) is None


def test_sort_key_orders_longest_first() -> None:
    """Перевіряє впорядкування через key."""
    items = [
        Running("2026-09-05", "біг", 30, 5.2, 140),
        Cycling("2026-09-08", "велосипед", 120, 41.3, 138),
        Running("2026-09-01", "біг", 45, 8.5, 148),
    ]
    assert [item.duration for item in sorted(items, key=lambda item: item.sort_key())] == [
        120,
        45,
        30,
    ]
