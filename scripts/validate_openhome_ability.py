#!/usr/bin/env python3
"""Static validator for OpenHome Ability folders.

Mirrors the public openhome-dev/abilities checks for required files, SDK
patterns, blocked imports/patterns, register tag, and common README gaps.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_FILES = ["main.py", "README.md", "__init__.py"]
BLOCKED_IMPORTS = ["redis", "user_config"]
BLOCKED_PATTERNS = [
    (r"\bprint\s*\(", "Use self.worker.editor_logging_handler instead of print()"),
    (r"\basyncio\.sleep\s*\(", "Use self.worker.session_tasks.sleep() instead of asyncio.sleep()"),
    (r"\basyncio\.create_task\s*\(", "Use self.worker.session_tasks.create() instead of asyncio.create_task()"),
    (r"\bexec\s*\(", "exec() is not allowed for security reasons"),
    (r"\beval\s*\(", "eval() is not allowed for security reasons"),
    (r"\bpickle\.", "pickle is not allowed for security reasons"),
    (r"\bdill\.", "dill is not allowed for security reasons"),
    (r"\bshelve\.", "shelve is not allowed for security reasons"),
    (r"\bmarshal\.", "marshal is not allowed for security reasons"),
    (r"\bopen\s*\(", "raw open() is not allowed; use CapabilityWorker file helpers"),
    (r"\bassert\s+", "assert statements are not allowed; use proper error handling"),
    (r"\bhashlib\.md5\s*\(", "MD5 is not allowed; use SHA-256 or stronger"),
]
REQUIRED_PATTERNS = [
    (r"resume_normal_flow\s*\(", "resume_normal_flow() must be called"),
    (r"class\s+\w+.*MatchingCapability", "Class must extend MatchingCapability"),
    (r"def\s+call\s*\(", "Must have a call() method"),
    (r"worker\s*:\s*AgentWorker\s*=\s*None", "Must declare worker: AgentWorker = None"),
    (r"capability_worker\s*:\s*CapabilityWorker\s*=\s*None", "Must declare capability_worker: CapabilityWorker = None"),
]
README_HINTS = [
    "what it does",
    "suggested trigger words",
    "setup",
    "how it works",
    "example conversation",
]


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_dir():
        return [f"Not a directory: {path}"], warnings

    if re.search(r"[_ ]", path.name):
        suggested = re.sub(r"[_ ]+", "-", path.name)
        errors.append(f"Folder name {path.name!r} contains underscores/spaces; use {suggested!r}")

    for filename in REQUIRED_FILES:
        if not (path / filename).is_file():
            errors.append(f"Missing required file: {filename}")

    main_py = path / "main.py"
    if main_py.is_file():
        code = main_py.read_text(encoding="utf-8")
        for blocked in BLOCKED_IMPORTS:
            pattern = rf"(^|\s|,)import\s+{re.escape(blocked)}\b|from\s+{re.escape(blocked)}\b"
            if re.search(pattern, code):
                errors.append(f"Blocked import found: {blocked}")
        for pattern, message in BLOCKED_PATTERNS:
            if re.search(pattern, code):
                errors.append(message)
        for pattern, message in REQUIRED_PATTERNS:
            if not re.search(pattern, code):
                errors.append(message)
        if not re.search(r"#\s?\{\{register[_ ]capability\}\}", code):
            errors.append("Missing register capability tag: #{{register capability}}")
        classes = re.findall(r"^class\s+\w+", code, re.MULTILINE)
        if len(classes) > 1:
            warnings.append(f"Found {len(classes)} classes; one class per main.py is recommended")
        if "text_to_text_response" in code and re.search(r"await\s+[^\n]*text_to_text_response", code):
            errors.append("text_to_text_response() is synchronous; do not await it")

    readme = path / "README.md"
    if readme.is_file():
        lower = readme.read_text(encoding="utf-8").lower()
        for hint in README_HINTS:
            if hint not in lower:
                warnings.append(f"README may be missing section: {hint}")

    return errors, warnings


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_openhome_ability.py <ability-folder> [more-folders...]")
        return 1

    ok = True
    for raw in sys.argv[1:]:
        path = Path(raw).resolve()
        errors, warnings = validate(path)
        print(f"Validating OpenHome Ability: {path}")
        for warning in warnings:
            print(f"  WARN: {warning}")
        for error in errors:
            print(f"  ERROR: {error}")
        if errors:
            ok = False
        else:
            print("  OK: OpenHome static checks passed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
