#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Validate every card's frontmatter against .schema.json. Exit 1 on errors."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _kanban import (
    ALL_FOLDERS,
    KANBAN_ROOT,
    SCHEMA_PATH,
    ensure_initialized,
    iter_cards,
)


def validate_card(fm: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    props = schema.get("properties", {})
    additional = schema.get("additionalProperties", True)

    for field in required:
        if field not in fm:
            errors.append(f"missing required field: {field}")

    for key, value in fm.items():
        if key not in props:
            if additional is False:
                errors.append(f"unknown field: {key}")
            continue
        spec = props[key]
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{key}: '{value}' not in {spec['enum']}")
        elif "type" in spec:
            t = spec["type"]
            if t == "string" and not isinstance(value, str):
                errors.append(f"{key}: expected string, got {type(value).__name__}")
            elif t == "array" and not isinstance(value, list):
                errors.append(f"{key}: expected array, got {type(value).__name__}")
            elif t == "object" and not isinstance(value, dict):
                errors.append(f"{key}: expected object, got {type(value).__name__}")
        if "pattern" in spec and isinstance(value, str):
            if not re.match(spec["pattern"], value):
                errors.append(f"{key}: '{value}' does not match {spec['pattern']}")
        if "minLength" in spec and isinstance(value, str):
            if len(value) < spec["minLength"]:
                errors.append(f"{key}: too short (min {spec['minLength']})")
    return errors


def main() -> None:
    ensure_initialized()
    if not SCHEMA_PATH.exists():
        print(f"warn: {SCHEMA_PATH} missing — run kanban-init.py", file=sys.stderr)
        sys.exit(1)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    total = 0
    bad = 0
    for card in iter_cards(ALL_FOLDERS):
        total += 1
        errors = validate_card(card.frontmatter, schema)
        if card.column == "Done" and "completed_at" not in card.frontmatter:
            errors.append("Done card missing completed_at")
        if card.column == "Blocked" and "blocked_by" not in card.frontmatter:
            # warn-level: blocked_by is recommended but not required
            print(f"warn: {card.path}: Blocked card missing blocked_by", file=sys.stderr)
        if errors:
            bad += 1
            rel = card.path.relative_to(KANBAN_ROOT)
            for e in errors:
                print(f"FAIL {rel}: {e}")

    if bad:
        print(f"\n{bad}/{total} cards failed validation", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {total} cards valid")


if __name__ == "__main__":
    main()
