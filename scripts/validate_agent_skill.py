#!/usr/bin/env python3
"""Validate core Agent Skills structure for this repository.

This is intentionally stdlib-only. It checks the required SKILL.md file,
frontmatter boundaries, name/description constraints, and directory-name match
from https://agentskills.io/specification.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^(?!-)(?!.*--)[a-z0-9-]{1,64}(?<!-)$")


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def top_level_frontmatter_fields(frontmatter: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = unquote(value.strip())
    return fields


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"Missing required file: {skill_file}"]

    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter at byte 0")
        return errors

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        errors.append("SKILL.md must close frontmatter with a line containing ---")
        return errors

    frontmatter = parts[0][4:]
    body = parts[1].strip()
    fields = top_level_frontmatter_fields(frontmatter)

    name = fields.get("name", "")
    description = fields.get("description", "")
    compatibility = fields.get("compatibility", "")

    if not name:
        errors.append("Missing required frontmatter field: name")
    elif not NAME_RE.match(name):
        errors.append("name must be 1-64 chars, lowercase letters/numbers/hyphens, no leading/trailing/consecutive hyphens")
    elif skill_dir.name != name:
        errors.append(f"name must match parent directory: expected {skill_dir.name!r}, found {name!r}")

    if not description:
        errors.append("Missing required frontmatter field: description")
    elif len(description) > 1024:
        errors.append("description must be <=1024 characters")

    if compatibility and len(compatibility) > 500:
        errors.append("compatibility must be <=500 characters")

    if not body:
        errors.append("SKILL.md body must not be empty")

    return errors


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate_skill(target)
    print(f"Validating Agent Skill: {target}")
    if errors:
        for error in errors:
            print(f"  ERROR: {error}")
        return 1
    print("  OK: Agent Skill structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
