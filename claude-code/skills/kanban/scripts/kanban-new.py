#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Create a new card in Backlog/."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _kanban import (
    KANBAN_ROOT,
    ensure_initialized,
    fail,
    infer_project,
    iter_cards,
    now_id,
    now_iso,
    parse_tags,
    regenerate_board,
    slugify,
    write_card,
)

BODY_TEMPLATE = """## 배경

(이 카드를 만든 이유와 컨텍스트)

## 할 일

- [ ]

## 메모

"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a kanban card in Backlog/.")
    p.add_argument("title", help="Card title")
    p.add_argument("--project", help="Project name (auto-inferred if omitted)")
    p.add_argument("--priority", choices=["high", "med", "low"])
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--due", help="Due date (YYYY-MM-DD)")
    p.add_argument("--epic", help="Parent epic id (YYMMDD-HHMM)")
    p.add_argument("--type", choices=["task", "epic"], default="task")
    p.add_argument("--slug", help="Custom slug (default: derived from title)")
    return p.parse_args()


def unique_slug(base: str) -> str:
    existing = {c.slug for c in iter_cards()}
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"


def main() -> None:
    args = parse_args()
    ensure_initialized()

    project = infer_project(args.project)
    slug = unique_slug(args.slug or slugify(args.title))
    card_id = now_id()

    if any(c.id == card_id for c in iter_cards()):
        # 같은 분(分)에 두 번째 카드: 초까지 더해 충돌 회피
        import datetime as dt
        card_id = dt.datetime.now().strftime("%y%m%d-%H%M%S")

    fm: dict = {
        "id": card_id,
        "created": now_iso(),
        "title": args.title,
        "project": project,
    }
    if args.type == "epic":
        fm["type"] = "epic"
    if args.priority:
        fm["priority"] = args.priority
    if args.tags:
        fm["tags"] = parse_tags(args.tags)
    if args.due:
        fm["due"] = args.due
    if args.epic:
        fm["epic"] = args.epic

    path = KANBAN_ROOT / "Backlog" / f"{slug}.md"
    if path.exists():
        fail(f"file already exists: {path}")
    write_card(path, fm, BODY_TEMPLATE)
    regenerate_board()
    print(f"added: [{card_id}] {args.title} -> Backlog ({project})")
    print(f"file:  {path}")


if __name__ == "__main__":
    main()
