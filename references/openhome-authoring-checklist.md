# OpenHome Ability Authoring Checklist

Use this checklist before packaging or opening an OpenHome Abilities PR.

## Product fit

- Ability does something the base LLM cannot do alone: API, hardware, audio, persistence, live context, or multi-step workflow.
- Behavior-only changes are handled in the Agent description prompt, not as an Ability.
- Trigger phrases match natural spoken language and avoid broad false positives.

## Required files and structure

- Folder name uses hyphens only.
- `main.py`, `README.md`, and `__init__.py` exist.
- Community PR path is `community/your-ability-name/`.
- PR base branch is `dev`, not `main`.

## SDK compliance

- Class extends `MatchingCapability`.
- Class has `worker: AgentWorker = None`.
- Class has `capability_worker: CapabilityWorker = None`.
- Class contains `#{{register capability}}`.
- `call()` sets `self.worker`, sets `self.capability_worker`, and launches one top-level coroutine with `self.worker.session_tasks.create(...)`.
- Interactive `main.py` calls `self.capability_worker.resume_normal_flow()` on every exit path.
- `text_to_text_response()` is not awaited.

## Blocked patterns

- No `print()`; use `self.worker.editor_logging_handler`.
- No raw `open()`; use CapabilityWorker file helpers.
- No `asyncio.sleep()`; use `self.worker.session_tasks.sleep()`.
- No `asyncio.create_task()`; use `self.worker.session_tasks.create()`.
- No `redis`, `user_config`, `exec()`, `eval()`, `pickle`, `dill`, `shelve`, `marshal`, `assert`, or `hashlib.md5()`.
- No hardcoded real API keys.

## Voice UX

- Spoken responses are one or two natural sentences.
- Slow work has filler speech before the call.
- Destructive or external actions require confirmation.
- Exit phrases are checked before intent routing.
- Error paths speak a short recovery message and log details.

## Persistence

- File and key names are namespaced to the Ability.
- JSON persistence uses delete-then-write or explicit replacement mode.
- `.md` persistent files are only used for context intended to enter Agent prompts.

## Verification

```bash
python3 scripts/validate_openhome_ability.py community/your-ability-name
python3 validate_ability.py community/your-ability-name/
```

Then zip and test in `https://app.openhome.com/dashboard/abilities` with Live Editor.
