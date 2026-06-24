# Voice Skill Starter

![Community](https://img.shields.io/badge/OpenHome-Community-orange?style=flat-square)
![Author](https://img.shields.io/badge/Author-%40yourusername-lightgrey?style=flat-square)

## What It Does

Voice Skill Starter is a scaffold for an OpenHome Ability. Replace `handle_request()` in `main.py` with real API, DevKit, persistence, audio, or workflow logic before publishing.

## Suggested Trigger Words

- "voice skill starter"
- "open voice skill"

## Setup

1. Zip this folder.
2. Open `https://app.openhome.com/dashboard/abilities`.
3. Choose Add Custom Ability and upload the zip.
4. Set the trigger words above in the dashboard.
5. Test in Live Editor before sharing.

## How It Works

OpenHome routes a trigger phrase to `main.py`. The Ability reads recent trigger context with `get_full_message_history()`, speaks a short filler line, runs `handle_request()`, speaks a concise result, and always returns control with `resume_normal_flow()`.

## Example Conversation

> **User:** "voice skill starter"
> **AI:** "One sec, checking that."
> **AI:** "Done."
