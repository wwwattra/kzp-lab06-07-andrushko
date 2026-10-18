"""Класи предметної області: тренування, підтипи, протокол і підсумок."""

from dataclasses import dataclass
from typing import Protocol


class Loaded(Protocol):
    """Протокол об'єктів, що вміють обчислювати навантаження."""

    def load(self) -> float:
        """Повертає навантаження в умовних балах."""
        ...


class Training:
    """Базове тренування з перевіреним спільним станом."""

    def __init__(self, date: str, kind: str, duration: int, distance: float, pulse: int) -> None:
        """Створює тренування; значення перевіряються у setter-ах властивостей."""
        if not date or not date.strip():
            raise ValueError("Дата не може бути порожньою")
        if not kind or not kind.strip():
            raise ValueError("Вид не може бути порожнім")
        self._date = date.strip()
        self._kind = kind.strip()
        self.duration = duration
        self.distance = distance
        self.pulse = pulse

    @property
    def date(self) -> str:
        """Повертає дату у форматі YYYY-MM-DD (лише читання)."""
        return self._date

    @property
    def kind(self) -> str:
        """Повертає вид тренування (лише читання)."""
        return self._kind

    @property
    def duration(self) -> int:
        """Повертає тривалість у хвилинах."""
        return self._duration

    @duration.setter
    def duration(self, value: int) -> None:
        """Встановлює невід'ємну тривалість."""
        # Записуємо внутрішнє поле, а не властивість, щоб не викликати setter рекурсивно.
        if value < 0:
            raise ValueError("Тривалість не може бути від'ємною")
        self._duration = value

    @property
    def distance(self) -> float:
        """Повертає дистанцію в кілометрах."""
        return self._distance

    @distance.setter
    def distance(self, value: float) -> None:
        """Встановлює невід'ємну дистанцію."""
        if value < 0:
            raise ValueError("Дистанція не може бути від'ємною")
        self._distance = float(value)

    @property
    def pulse(self) -> int:
        """Повертає середній пульс."""
        return self._pulse

    @pulse.setter
    def pulse(self, value: int) -> None:
        """Встановлює пульс у фізично допустимому діапазоні 30-250."""
        if not 30 <= value <= 250:
            raise ValueError("Пульс має бути в діапазоні 30-250")
        self._pulse = value

    def load(self) -> float:
        """Оголошує операцію навантаження для підтипів."""
        raise NotImplementedError

    def sort_key(self) -> tuple[int, str]:
        """Повертає ключ впорядкування: довші тренування першими, далі за датою."""
        return (-self.duration, self.date)

    def _state(self) -> tuple[str, str, int, float, int]:
        """Повертає кортеж стану для порівняння."""
        return (self.date, self.kind, self.duration, self.distance, self.pulse)

    def __str__(self) -> str:
        """Повертає коротке подання для читача."""
        return f"{self.date} {self.kind}, {self.duration} хв"

    def __repr__(self) -> str:
        """Повертає діагностичне подання об'єкта."""
        return (
            f"{type(self).__name__}(date={self.date!r}, kind={self.kind!r}, "
            f"duration={self.duration!r}, distance={self.distance!r}, pulse={self.pulse!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Порівнює тренування одного підтипу за повним станом."""
        if not isinstance(other, Training):
            return NotImplemented
        return type(self) is type(other) and self._state() == other._state()

    __hash__ = None  # Об'єкт змінюваний через setter-и, тому не використовується як ключ.


class Running(Training):
    """Біг: навантаження залежить від тривалості та пульсу."""

    def load(self) -> float:
        """Обчислює навантаження: хвилини · пульс / 100."""
        return self.duration * self.pulse / 100


class Cycling(Training):
    """Велосипед: навантаження залежить від дистанції та тривалості."""

    def load(self) -> float:
        """Обчислює навантаження: км · 1.5 + хвилини · 0.5."""
        return self.distance * 1.5 + self.duration * 0.5


@dataclass(frozen=True)
class ReportSummary:
    """Незмінний підсумок обробки тренувань."""

    count: int
    selected: int
    average_pulse: float
    total_load: float


def best_by_load(items: list[Loaded]) -> Loaded | None:
    """Повертає об'єкт із найбільшим навантаженням або None для порожнього списку."""
    # Функція знає лише про load(), тому новий підтип не потребує змін тут.
    return max(items, key=lambda item: item.load(), default=None)
