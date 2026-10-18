"""Обчислення над об'єктами тренувань без перевірок конкретного підтипу."""

from .models import ReportSummary, Training, best_by_load

MIN_DURATION = 45


def long_trainings(trainings: list[Training], minimum: int = MIN_DURATION) -> list[Training]:
    """Повертає тренування тривалістю не менше заданої кількості хвилин."""
    return [training for training in trainings if training.duration >= minimum]


def kinds(trainings: list[Training]) -> set[str]:
    """Повертає множину унікальних видів."""
    return {training.kind for training in trainings}


def distance_by_kind(trainings: list[Training]) -> dict[str, float]:
    """Обчислює сумарну дистанцію за видом у стабільному порядку."""
    return {
        kind: sum(training.distance for training in trainings if training.kind == kind)
        for kind in sorted(kinds(trainings))
    }


def load_by_kind(trainings: list[Training]) -> dict[str, float]:
    """Обчислює поліморфне навантаження за видом через спільний метод load()."""
    return {
        kind: sum(training.load() for training in trainings if training.kind == kind)
        for kind in sorted(kinds(trainings))
    }


def average_pulse(trainings: list[Training]) -> float:
    """Повертає середній пульс або 0.0 для порожнього набору."""
    if not trainings:
        return 0.0
    return sum(training.pulse for training in trainings) / len(trainings)


def longest_training(trainings: list[Training]) -> Training | None:
    """Повертає найдовше тренування (перше за ключем сортування) або None."""
    ordered = sorted(trainings, key=Training.sort_key)
    return ordered[0] if ordered else None


def make_summary(trainings: list[Training], minimum_duration: int = MIN_DURATION) -> dict:
    """Формує підсумок звіту; ключі сумісні зі словниковою версією ЛР6."""
    selected = long_trainings(trainings, minimum_duration)
    return {
        "count": len(trainings),
        "selected": len(selected),
        "kinds": kinds(trainings),
        "distance_by_kind": distance_by_kind(trainings),
        "average_pulse": average_pulse(trainings),
        "longest": longest_training(trainings),
        "minutes_long": float(sum(training.duration for training in selected)),
        "load_by_kind": load_by_kind(trainings),
        "best": best_by_load(trainings),
        "summary": ReportSummary(
            count=len(trainings),
            selected=len(selected),
            average_pulse=average_pulse(trainings),
            total_load=sum(training.load() for training in trainings),
        ),
    }
