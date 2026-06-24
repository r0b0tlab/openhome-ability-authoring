#!/usr/bin/env python3
"""Create a compliant starter OpenHome Ability folder."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAIN_TEMPLATE = '''import json
from src.agent.capability import MatchingCapability
from src.main import AgentWorker
from src.agent.capability_worker import CapabilityWorker

TITLE = {title!r}
EXIT_WORDS = (
    "done", "exit", "stop", "quit", "bye", "goodbye",
    "never mind", "cancel", "no thanks", "nothing else",
)
SYSTEM_PROMPT = """
You are the spoken response layer for an OpenHome Ability.
Return one or two natural spoken sentences.
No markdown, no lists, no raw JSON, no code blocks.
If the request needs real integration, explain the next action briefly.
""".strip()


class {class_name}(MatchingCapability):
    worker: AgentWorker = None
    capability_worker: CapabilityWorker = None

    #{{{{register capability}}}}

    def call(self, worker: AgentWorker):
        self.worker = worker
        self.capability_worker = CapabilityWorker(self.worker)
        self.worker.session_tasks.create(self.run())

    async def run(self):
        try:
            user_input = self.get_trigger_context()
            if not user_input:
                user_input = await self.capability_worker.run_io_loop(
                    "What should I help with?"
                )

            if self.is_exit(user_input):
                await self.capability_worker.speak("Okay, handing you back.")
                return

            await self.capability_worker.speak("One sec, checking that.")
            response = self.handle_request(user_input)
            await self.capability_worker.speak(self.clean_for_voice(response))
        except Exception as exc:
            self.worker.editor_logging_handler.error(f"{{TITLE}} failed: {{exc}}")
            await self.capability_worker.speak(
                "Something went wrong. Check the ability logs."
            )
        finally:
            self.capability_worker.resume_normal_flow()

    def get_trigger_context(self) -> str:
        try:
            history = self.capability_worker.get_full_message_history() or []
        except Exception as exc:
            self.worker.editor_logging_handler.warning(
                f"Could not read message history: {{exc}}"
            )
            return ""

        for item in reversed(history):
            if item.get("role") == "user" and item.get("content"):
                return str(item["content"])
        return ""

    def is_exit(self, user_input: str) -> bool:
        lower = (user_input or "").lower()
        return any(word in lower for word in EXIT_WORDS)

    def handle_request(self, user_input: str) -> str:
        """Replace this method with API, DevKit, file, or workflow logic."""
        prompt = (
            f"Ability: {{TITLE}}\n"
            f"User request: {{user_input}}\n"
            "Draft the next spoken response."
        )
        return self.capability_worker.text_to_text_response(
            prompt,
            history=[],
            system_prompt=SYSTEM_PROMPT,
        )

    def clean_for_voice(self, text: str) -> str:
        cleaned = (text or "").replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                for key in ("spoken", "message", "response", "answer"):
                    if parsed.get(key):
                        cleaned = str(parsed[key])
                        break
        except json.JSONDecodeError:
            pass
        return " ".join(cleaned.split())[:500] or "Done."
'''

README_TEMPLATE = '''# {title}

![Community](https://img.shields.io/badge/OpenHome-Community-orange?style=flat-square)
![Author](https://img.shields.io/badge/Author-{author_badge}-lightgrey?style=flat-square)

## What It Does

{title} is a starter OpenHome Ability. Replace `handle_request()` in `main.py` with real API, DevKit, persistence, audio, or workflow logic before publishing.

## Suggested Trigger Words
{trigger_lines}

## Setup

1. Zip this folder.
2. Open `https://app.openhome.com/dashboard/abilities`.
3. Choose Add Custom Ability and upload the zip.
4. Set the trigger words above in the dashboard.
5. Test in Live Editor before sharing.

## How It Works

OpenHome routes a trigger phrase to `main.py`. The Ability reads recent trigger context with `get_full_message_history()`, speaks a short filler line, runs `handle_request()`, speaks a concise result, and always returns control with `resume_normal_flow()`.

## Example Conversation

> **User:** "{example_trigger}"
> **AI:** "One sec, checking that."
> **AI:** "Done."

## Development Notes

- Keep `#{{register capability}}` unchanged.
- Keep responses short because this is voice-first.
- Use `self.worker.editor_logging_handler` instead of `print()`.
- Use `self.worker.session_tasks.sleep()` instead of `asyncio.sleep()`.
- Use CapabilityWorker storage helpers instead of raw `open()` in Ability code.
- Add confirmation before destructive or external actions.
'''


def slug_to_class(slug: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[-_\s]+", slug) if part) + "Capability"


def valid_class_name(name: str) -> bool:
    return bool(re.match(r"^[A-Z][A-Za-z0-9_]*$", name))


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold an OpenHome Ability folder")
    parser.add_argument("ability_dir", help="Output directory, e.g. community/my-ability")
    parser.add_argument("--class-name", help="Capability class name, e.g. MyAbilityCapability")
    parser.add_argument("--title", required=True, help="Human title for README and spoken context")
    parser.add_argument("--author", default="@yourusername", help="README author badge text")
    parser.add_argument("--triggers", nargs="+", default=["my ability"], help="Suggested dashboard trigger phrases")
    parser.add_argument("--force", action="store_true", help="Overwrite files if they already exist")
    args = parser.parse_args()

    ability_dir = Path(args.ability_dir)
    if re.search(r"[_ ]", ability_dir.name):
        print("ERROR: Ability folder name must use hyphens, not spaces or underscores", file=sys.stderr)
        return 1

    class_name = args.class_name or slug_to_class(ability_dir.name)
    if not valid_class_name(class_name):
        print(f"ERROR: Invalid class name: {class_name}", file=sys.stderr)
        return 1

    ability_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        ability_dir / "main.py": MAIN_TEMPLATE.format(class_name=class_name, title=args.title),
        ability_dir / "README.md": README_TEMPLATE.format(
            title=args.title,
            author_badge=args.author.replace("@", "%40"),
            trigger_lines="\n".join(f'- "{trigger}"' for trigger in args.triggers),
            example_trigger=args.triggers[0],
        ),
        ability_dir / "__init__.py": "\n",
    }

    for path, content in outputs.items():
        if path.exists() and not args.force:
            print(f"ERROR: Refusing to overwrite existing file without --force: {path}", file=sys.stderr)
            return 1
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path}")

    print("next: python3 scripts/validate_openhome_ability.py " + str(ability_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
