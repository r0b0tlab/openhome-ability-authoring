# Source Notes

This skill was derived from public OpenHome and Agent Skills material.

## OpenHome Abilities

- Repository: `https://github.com/openhome-dev/abilities`
- Contribution rules: fork, branch from `dev`, add community Abilities under `community/`, validate, PR to `dev`.
- Runtime classes: `MatchingCapability`, `AgentWorker`, `CapabilityWorker`.
- Required register tag: `#{{register capability}}` or equivalent underscore form accepted by validator.
- Dashboard testing: `https://app.openhome.com/dashboard/abilities`.
- API key settings: `https://app.openhome.com/dashboard/settings`.

## OpenClaw template lessons

- `exec_local_command(command: str | dict, target_id: str | None = None, timeout: float = 10.0)` bridges a voice Ability to local computer automation.
- Local execution needs validation, confirmation, timeout handling, and short spoken summaries.
- Treat OpenClaw as an integration pattern, not a production Ability to deploy unchanged.

## Agent Skills format

- Skill directory contains required `SKILL.md`.
- `name` is lowercase alphanumeric plus hyphens, <=64 chars, and matches the directory.
- `description` is required and <=1024 chars.
- Optional `scripts/`, `references/`, `assets/`, and other directories can support the skill.
