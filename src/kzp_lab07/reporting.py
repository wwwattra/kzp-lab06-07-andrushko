"""Формування та запис текстового звіту."""

from pathlib import Path


def format_report(summary: dict) -> str:
    """Форматує підсумок: перші рядки збігаються зі звітом ЛР6, далі - навантаження."""
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
        lines.append(f"Найдовше тренування: {longest}")
    lines.append(f"Сумарний час тренувань від 45 хв: {summary['minutes_long']:.0f} хв")
    lines.append("Навантаження за видом (load), бали:")
    for kind, load in sorted(summary["load_by_kind"].items()):
        lines.append(f"  {kind}: {load:.2f}")
    best = summary["best"]
    lines.append(
        "Найбільше навантаження: немає даних"
        if best is None
        else f"Найбільше навантаження: {best} ({best.load():.2f})"
    )
    return "\n".join(lines) + "\n"


def write_report(path: Path, text: str) -> None:
    """Створює каталог і записує звіт у файл UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(text)
