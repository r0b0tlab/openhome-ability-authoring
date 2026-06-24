# OpenHome Ability Authoring Agent Skill

A portable `agentskills.io`-compatible skill for AI agents that need to build, review, validate, package, or contribute OpenHome Abilities for OpenHome voice agents and DevKit workflows.

This repository is itself an Agent Skill directory: the required `SKILL.md` lives at the repo root, with helper scripts, templates, and references beside it.

## Install

Clone or download this repository into any Agent Skills-compatible client skill directory:

```bash
git clone https://github.com/r0b0tlab/openhome-ability-authoring.git
```

For Hermes Agent, copy the folder into `~/.hermes/skills/software-development/openhome-ability-authoring/` or install it through the Hermes skill manager.

## What it contains

- `SKILL.md` — the agent-facing procedure for OpenHome Ability work.
- `scripts/scaffold_openhome_ability.py` — creates a compliant starter Ability folder.
- `scripts/validate_openhome_ability.py` — static checks mirroring the OpenHome contribution validator.
- `scripts/validate_agent_skill.py` — validates this Agent Skill against core `agentskills.io` structure rules.
- `templates/voice-skill/` — a copyable OpenHome voice-skill starter.
- `references/openhome-authoring-checklist.md` — compact review checklist.

## Quick start

```bash
python3 scripts/validate_agent_skill.py .
python3 scripts/scaffold_openhome_ability.py community/my-ability --class-name MyAbilityCapability --title "My Ability" --author "@yourusername" --triggers "my ability" "open my ability"
python3 scripts/validate_openhome_ability.py community/my-ability
```

Then zip the generated Ability folder and upload it in OpenHome:

```bash
cd community
zip -r my-ability.zip my-ability
```

Open `https://app.openhome.com/dashboard/abilities`, choose Add Custom Ability, upload the zip, set trigger words, and test in Live Editor.

## Source basis

This skill is grounded in the public OpenHome Abilities repo, contributor guidelines, validator, CapabilityWorker reference, patterns cookbook, and OpenClaw template:

- `https://github.com/openhome-dev/abilities`
- `https://github.com/openhome-dev/abilities/blob/dev/CONTRIBUTING.md`
- `https://github.com/openhome-dev/abilities/blob/dev/validate_ability.py`
- `https://github.com/openhome-dev/abilities/blob/dev/docs/capability-worker.md`
- `https://github.com/openhome-dev/abilities/blob/dev/docs/patterns.md`
- `https://github.com/openhome-dev/abilities/tree/dev/templates/openclaw`
- `https://agentskills.io/specification`

## License

MIT. See `LICENSE`.
