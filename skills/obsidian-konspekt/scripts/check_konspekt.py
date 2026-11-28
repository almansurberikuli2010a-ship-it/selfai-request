#!/usr/bin/env python3
"""Проверяет конспекты уроков в папке Obsidian.

- Каждое число (год, дата, век) из конспектов должно быть в учебнике.
- В конспекте не должно быть таблиц: он пишется текстом.
- Отдельно печатает годы из учебника, которых нет ни в одном конспекте:
  «возможно пропущено». Это подсказка, решает человек.

Имена и термины скрипт не проверяет: у них меняются окончания.

Запуск:
    python3 check_konspekt.py <папка с конспектами> <учебник> [<учебник> ...]
Учебник — только те параграфы, по которым сделаны конспекты.
Код выхода 0 — проблем нет, 1 — есть.
"""
import re
import sys
from pathlib import Path

COMMENT = re.compile(r"<!--.*?-->", re.S)
# Ссылки на страницы и параграфы: «стр. 45», «с. 45», «§ 12», «45-бет», «бет 45», «б. 45».
REFS = re.compile(
    r"(?:стр\.?|с\.|§|бет|б\.)\s*\d+(?:\s*[–—-]\s*\d+)?"
    r"|\d+(?:\s*[–—-]\s*\d+)?\s*[-–]?\s*бет(?:тер)?",
    re.I,
)
NUMBER = re.compile(r"\d{2,}")
YEAR = re.compile(r"(?<!\d)(?:[5-9]\d\d|1\d{3}|20\d\d)(?!\d)")
ROMAN = re.compile(r"\b[IVXLC]{2,7}\b")


def clean(text):
    return REFS.sub(" ", COMMENT.sub(" ", text))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    folder = Path(sys.argv[1])
    source = clean("\n".join(Path(p).read_text(encoding="utf-8") for p in sys.argv[2:]))
    source_numbers = set(NUMBER.findall(source))
    source_roman = set(ROMAN.findall(source))
    source_paths = {Path(p).resolve() for p in sys.argv[2:]}

    notes = [p for p in sorted(folder.rglob("*.md")) if p.resolve() not in source_paths]
    if not notes:
        print("В папке нет ни одного конспекта.")
        return 1

    problems = []
    all_text = ""
    for note in notes:
        text = clean(note.read_text(encoding="utf-8"))
        all_text += "\n" + text
        name = note.relative_to(folder)
        for n in sorted(set(NUMBER.findall(text)) - source_numbers):
            problems.append(f"{name}: числа {n} нет в учебнике.")
        for r in sorted(set(ROMAN.findall(text)) - source_roman):
            problems.append(f"{name}: века {r} нет в учебнике.")
        if re.search(r"^\s*\|.*\|\s*$", text, re.M):
            problems.append(f"{name}: есть таблица, а конспект пишется текстом.")

    print(f"Конспектов: {len(notes)}.")
    missed = sorted(set(YEAR.findall(source)) - set(NUMBER.findall(all_text)))
    if missed:
        print("Возможно пропущено (годы есть в учебнике, но не в конспектах): " + ", ".join(missed))
    if problems:
        print(f"Проблем: {len(problems)}")
        for p in problems:
            print("- " + p)
        return 1
    print("Проблем нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
