---
name: openhome-ability-authoring
description: Build OpenHome Ability projects for voice agents.
version: 0.1.0
license: MIT
compatibility: Agent Skills format; designed for AI coding agents with filesystem, terminal, web, and git access.
metadata:
  hermes:
    tags: [OpenHome, Voice, Agents, DevKit]
  author: r0b0tlab
  source: https://github.com/openhome-dev/abilities
---

# OpenHome Ability Authoring

Use this skill to build, review, validate, package, or contribute OpenHome Abilities for OpenHome voice agents and DevKit workflows. It does not replace dashboard Live Editor testing, hardware testing, or maintainer review for Marketplace publishing. Bundled helper scripts are Python stdlib only; generated Ability runtime code should use the OpenHome SDK imports and documented `CapabilityWorker` methods.

## When to Use

- User asks to build an OpenHome Ability, OpenHome Skill, OpenHome plugin, or DevKit voice workflow.
- User asks to make something compatible with `openhome-dev/abilities`, `app.openhome.com`, or an OpenHome kit.
- User asks to review, fix, validate, zip, publish, or submit an Ability PR.
- User mentions `MatchingCapability`, `CapabilityWorker`, `resume_normal_flow`, trigger words, Live Editor, or OpenClaw-style templates.
- User wants an Agent Skills / `agentskills.io` package that teaches agents how to work with OpenHome.

## Prerequisites

- OpenHome dashboard account: `https://app.openhome.com`.
- Runtime testing access: `https://app.openhome.com/dashboard/abilities` → Abilities → Add Custom Ability → Live Editor.
- For contributions: fork `https://github.com/openhome-dev/abilities`; all PRs target `dev`, not `main`.
- For API-key settings: `https://app.openhome.com/dashboard/settings`.
- Local static work: Python 3 stdlib only for the bundled scripts.
- Hermes usage: invoke commands through the `terminal` tool; inspect files with `read_file`; locate files with `search_files`; make targeted edits with `patch`; fetch source docs with `web_extract`.

## How to Run

From this skill directory, invoke through the `terminal` tool:

```bash
python3 scripts/scaffold_openhome_ability.py community/my-ability --class-name MyAbilityCapability --title "My Ability" --author "@yourusername" --triggers "my ability" "open my ability"
python3 scripts/validate_openhome_ability.py community/my-ability
python3 scripts/validate_agent_skill.py .
```

For an OpenHome repository contribution, work from `openhome-dev/abilities` or a fork:

```bash
git fetch upstream
git checkout dev
git pull upstream dev
git checkout -b add-your-ability-name dev
cp -r templates/basic-template community/your-ability-name
python3 validate_ability.py community/your-ability-name/
git add community/your-ability-name/
git commit -m "Add your-ability-name community ability"
git push origin add-your-ability-name
```

Package for dashboard upload from the parent of the Ability folder:

```bash
zip -r your-ability-name.zip your-ability-name
```

## Quick Reference

- Source repo: `https://github.com/openhome-dev/abilities`
- Dashboard: `https://app.openhome.com`
- Abilities: `https://app.openhome.com/dashboard/abilities`
- Settings/API keys: `https://app.openhome.com/dashboard/settings`
- Contribution path: `community/your-ability-name/`
- Required files: `main.py`, `README.md`, `__init__.py`
- Required branch flow: `ability/your-ability-name` or `add-your-ability-name` → PR base `dev` → maintainer promotion to `main`
- Template copy: `cp -r templates/basic-template community/your-ability-name`
- OpenHome validator: `python3 validate_ability.py community/your-ability-name/`
- Register tag: `#{{register capability}}`
- Runtime imports: `MatchingCapability`, `AgentWorker`, `CapabilityWorker`
- Required class attrs: `worker: AgentWorker = None`, `capability_worker: CapabilityWorker = None`
- Launch async logic: `self.worker.session_tasks.create(self.run())`
- Sleep in Ability: `await self.worker.session_tasks.sleep(2.0)`
- Speak: `await self.capability_worker.speak("...")`
- Listen: `await self.capability_worker.user_response()`
- Full utterance: `await self.capability_worker.wait_for_complete_transcription()`
- Speak + listen: `await self.capability_worker.run_io_loop("...")`
- Confirmation: `await self.capability_worker.run_confirmation_loop("...")`
- LLM response, synchronous: `self.capability_worker.text_to_text_response(prompt, history=[], system_prompt="")`
- Trigger/session context: `self.capability_worker.get_full_message_history()`
- DevKit action: `await self.capability_worker.send_devkit_action("led-on")`
- Local command bridge, OpenClaw-style: `await self.capability_worker.exec_local_command(command, target_id=None, timeout=10.0)`
- Persist key-value: `create_key`, `update_key`, `delete_key`, `get_all_keys`, `get_single_key`
- Persist files: `check_if_file_exists`, `write_file`, `read_file`, `delete_file`, `get_user_data_file_names`
- Always exit interactive skills: `self.capability_worker.resume_normal_flow()`
- Blocked in Ability code: `print()`, raw `open()`, `redis`, `user_config`, `exec()`, `eval()`, `pickle`, `dill`, `shelve`, `marshal`, `asyncio.sleep()`, `asyncio.create_task()`, `assert`, `hashlib.md5()`

## Procedure

1. Decide whether an Ability is warranted.
   - Build an Ability only when the Agent must do something beyond normal LLM conversation: call an API, control hardware, play audio, persist data, inspect live context, or run a multi-step voice workflow.
   - If the request is only tone, role, refusal policy, language, or persona behavior, change the Agent description prompt instead.

2. Pick the runtime shape.
   - `main.py` Skill: trigger word starts an on-demand interaction, then exits with `resume_normal_flow()`.
   - `background.py` daemon: starts with the session, uses `call(self, worker, background_daemon_mode: bool)`, loops with `session_tasks.sleep()`, and does not call `resume_normal_flow()` inside the daemon loop.
   - Combined: use `main.py` plus `background.py`; coordinate through user-level files or keys because direct cross-Ability calls are not supported.

3. Create the Ability folder.
   - Use hyphen-only names under `community/` for OpenHome PRs.
   - Invoke the bundled scaffold through the `terminal` tool:
     ```bash
     python3 scripts/scaffold_openhome_ability.py community/your-ability-name --class-name YourAbilityCapability --title "Your Ability" --author "@yourusername" --triggers "trigger phrase" "another trigger"
     ```
   - If working inside `openhome-dev/abilities`, copying `templates/basic-template` is also acceptable:
     ```bash
     cp -r templates/basic-template community/your-ability-name
     ```

4. Implement the SDK skeleton before feature code.
   - Class extends `MatchingCapability`.
   - Include `worker: AgentWorker = None` and `capability_worker: CapabilityWorker = None`.
   - Keep `#{{register capability}}` in the class.
   - In `call()`, set `self.worker`, set `self.capability_worker = CapabilityWorker(self.worker)`, and launch exactly one top-level coroutine with `self.worker.session_tasks.create(...)`.
   - Wrap interactive `run()` logic with `try/except/finally` and call `self.capability_worker.resume_normal_flow()` in `finally`.

5. Read trigger context and route intent.
   - Trigger words are configured in the dashboard, not in code.
   - Do not create or edit `config.json`; OpenHome manages it at runtime.
   - Use `get_full_message_history()` to recover what the user said before activation.
   - Prefer LLM JSON classification for messy voice input; strip markdown fences before `json.loads()`.

6. Design voice UX.
   - Keep each `speak()` call to one or two spoken sentences.
   - Add filler before slow calls: “One sec, checking that.”
   - Confirm destructive, costly, or external actions with `run_confirmation_loop()`.
   - Check exit phrases before processing: `done`, `exit`, `stop`, `quit`, `bye`, `never mind`, `cancel`, `no thanks`.
   - Read all spoken strings out loud before shipping.

7. Use approved I/O and persistence APIs.
   - Use `self.worker.editor_logging_handler.info/error/warning`; never `print()`.
   - Use `self.worker.session_tasks.sleep()` and `self.worker.session_tasks.create()`; never raw `asyncio.sleep()` or `asyncio.create_task()`.
   - Use CapabilityWorker file helpers; never raw `open()` in Ability code.
   - For JSON files, delete first then write with replacement semantics; `write_file` defaults to append behavior in the OpenHome file API.
   - Namespace user-level files and keys, for example `your_ability_prefs.json`, not `prefs.json`.

8. Add a README that matches OpenHome review expectations.
   - Include title, community/author badges, what it does, suggested trigger words, setup, how it works, and an example conversation.
   - Document every required API key or external account with placeholders only.
   - Keep example spoken responses natural; the user is listening, not reading.

9. Validate statically.
   - From this skill repo:
     ```bash
     python3 scripts/validate_openhome_ability.py community/your-ability-name
     ```
   - From `openhome-dev/abilities`:
     ```bash
     python3 validate_ability.py community/your-ability-name/
     ```
   - Fix every error before runtime testing.

10. Test in OpenHome.
    - Zip the Ability folder.
    - Open `https://app.openhome.com/dashboard/abilities`.
    - Use Add Custom Ability, upload the zip, set trigger words, and test in Live Editor.
    - Test safe success, invalid input, slow/timeout behavior, user saying stop, and every error path.

11. Publish or contribute.
    - Public standalone repo: keep `SKILL.md` at repo root for Agent Skills compatibility; include `scripts/`, `templates/`, and `references/`.
    - OpenHome community PR: branch from `dev`, submit files only under `community/your-ability-name/`, commit, push, and open the PR against `dev`.

## Pitfalls

- PRs to `main` are rejected; OpenHome contributions target `dev`.
- `official/` is OpenHome-maintained; community submissions go under `community/`.
- The dashboard owns trigger words and `config.json`; hardcoding either in the Ability is a design error.
- Missing `resume_normal_flow()` leaves the Agent silent after the Ability runs.
- `text_to_text_response()` is synchronous; do not `await` it.
- OpenClaw-style `exec_local_command()` can run local actions with user permissions; add validation and confirmation before destructive requests.
- Raw `open()` is blocked in Ability code even though helper scripts and validators may use normal filesystem APIs.
- Long spoken responses fail voice UX; use progressive disclosure instead of dumping data.
- Direct cross-Ability calls and direct Ability chaining are not supported; return to normal flow and share state through storage if needed.
- Persistent `.md` files may be injected into Agent prompt context; use `.md` only for context you intend the Agent to read.
- Appending to JSON corrupts it; use delete-then-write or explicit replacement mode when available.
- OpenHome runtime imports usually do not resolve outside Live Editor; static validation does not prove hardware/API behavior.

## Verification

Run one command from the skill directory through the `terminal` tool:

```bash
python3 scripts/validate_agent_skill.py . && rm -rf /tmp/openhome-smoke && python3 scripts/scaffold_openhome_ability.py /tmp/openhome-smoke --class-name SmokeCapability --title "Smoke Test" --author "@you" --triggers "smoke test" && python3 scripts/validate_openhome_ability.py /tmp/openhome-smoke
```

It proves the Agent Skills bundle is structurally valid, the scaffold creates required OpenHome files, and the generated Ability passes the bundled OpenHome static checks.
