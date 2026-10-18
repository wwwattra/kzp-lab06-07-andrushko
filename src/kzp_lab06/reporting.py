"""Формування та запис текстового звіту."""

from pathlib import Path


def format_report(summary: dict[str, object]) -> str:
    """Форматує підсумок у детермінований текстовий звіт."""
    lines = [
        "Звіт: спортивні тренування",
        f"Записів: {summary['count']}",
        f"Тренувань від 45 хв: {summary['selected']}",
        f"Види тренувань: {'; '.join(sorted(summary['kinds']))}",
        "Сумарна дистанція за видом, км:",
    ]
    for kind, distance in sorted(summary["distance_by_kind"].items()):
        lines.append(f"  {kind}: {distance:.2f}")
    lines.append(f"Середній пульс: {summary['average_pulse']:.2f}")
    longest = summary["longest"]
    if longest is None:
        lines.append("Найдовше тренування: немає даних")
    else:
        lines.append(
            f"Найдовше тренування: {longest['date']} {longest['kind']}, {longest['duration']} хв"
        )
    if "minutes_long" in summary:
        lines.append(f"Сумарний час тренувань від 45 хв: {summary['minutes_long']:.0f} хв")
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Створює каталог і записує звіт у файл UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)
