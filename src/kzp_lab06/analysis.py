"""Обчислення над записами тренувань."""

from collections.abc import Iterable

MIN_DURATION = 45


def long_trainings(
    records: Iterable[dict[str, object]], minimum: int = MIN_DURATION
) -> list[dict[str, object]]:
    """Повертає тренування тривалістю не менше заданої кількості хвилин."""
    return [record for record in records if int(record["duration"]) >= minimum]


def kinds(records: Iterable[dict[str, object]]) -> set[str]:
    """Повертає множину унікальних видів тренувань."""
    return {str(record["kind"]) for record in records}


def distance_by_kind(records: list[dict[str, object]]) -> dict[str, float]:
    """Обчислює сумарну дистанцію за видом у стабільному порядку ключів."""
    return {
        kind: sum(float(record["distance"]) for record in records if record["kind"] == kind)
        for kind in sorted(kinds(records))
    }


def average_pulse(records: list[dict[str, object]]) -> float:
    """Повертає середній пульс або 0.0 для порожнього набору."""
    if not records:
        return 0.0
    return sum(int(record["pulse"]) for record in records) / len(records)


def longest_training(records: list[dict[str, object]]) -> dict[str, object] | None:
    """Повертає найдовше тренування (перше за порядком при рівності) або None."""
    return max(records, key=lambda record: int(record["duration"]), default=None)


def make_summary(
    records: list[dict[str, object]],
    *metrics: str,
    minimum_duration: int = MIN_DURATION,
    **labels: str,
) -> dict[str, object]:
    """Формує підсумок і довільні суми метрик для тренувань від minimum_duration хвилин."""
    for metric in metrics:
        if records and any(metric not in record for record in records):
            raise ValueError(f"Невідома метрика: {metric}")
    selected = long_trainings(records, minimum_duration)
    result: dict[str, object] = {
        "count": len(records),
        "selected": len(selected),
        "kinds": kinds(records),
        "distance_by_kind": distance_by_kind(records),
        "average_pulse": average_pulse(records),
        "longest": longest_training(records),
    }
    for metric in metrics:
        result[labels.get(metric, metric)] = sum(float(record[metric]) for record in selected)
    return result
