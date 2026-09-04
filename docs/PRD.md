# QuestShift product requirements (v1)

A one-hour, AI-narrated DevOps dungeon for a facilitated team of four developers. This document is v1 only. Items not listed here are out of scope.

**Project board:** https://github.com/orgs/NA-FSI-Services/projects/3

## Problem

Workshop teams need a shared, timed exercise that feels like a dungeon crawl and still teaches Linux pipelines, Ansible plays, OpenShift probes, and a Java snippet. Existing labs are solo terminals. QuestShift puts four people on one canvas and one simulated terminal for sixty minutes.

## Users

| Role | Count | Job |
| --- | --- | --- |
| Facilitator | 1 | Deploys the stack, starts the session, keeps time, exports state if the cluster bounces |
| Developers | 4 | Pick cosmetic seats, read the Game Master, type solving commands |

Seats are Guardian, Automancer, Cluster Ranger, and Artificer. They are avatars and colors only. **Any player may solve any puzzle.**

## Journey

1. Facilitator applies one QuestShift stack to one OpenShift project (one party per deployment).
2. Party opens the UI Route. Dual panel: Phaser dungeon (Panel A) and CRT-like terminal (Panel B).
3. Facilitator starts a 60-minute session for campaign `devops-dungeon` (*The Cluster That Forgot Its Name*).
4. Game Master narrates the current room as JSON. Players type a command, playbook, `oc` line, or Java snippet.
5. `CommandEvaluator` scores the input. Pass grants loot and unlocks the next room. Fail increments hints.
6. Five rooms in order. Boss requires runes THORN, ASH, OAK, IRON already in inventory.
7. Party exports session YAML as proof of the run. Import restores after a bounce.

If vLLM is unavailable, the engine uses authored YAML narrative and hints so the hour still completes.

## Functional requirements

### Session

- `POST /api/sessions` creates one in-memory `GameSession` for campaign `devops-dungeon` (or the posted `campaignId`).
- Session tracks party members, current room, inventory, skills, puzzle flags, elapsed seconds, last GM text, and canvas event.
- One party per engine process / OpenShift deployment.

### Game Master JSON

- `LLMService` calls vLLM OpenAI-compatible `/v1/chat/completions` with Granite 3.1 8B Instruct.
- Completion is a single JSON object: `narrative`, `puzzle_type`, `expected_command_pattern`, `hint`, `canvas_event`.
- Engine keeps YAML `puzzle_type` and `expected_command_pattern`. LLM supplies narration and optional hint flavor.

### Evaluator

- Terminal never executes player input on the cluster.
- Score order: empty check → required loot → `forbidden_patterns` → regex or `accepted_examples` → puzzle-type soft match.
- Pass: mark room complete, grant loot/skills, advance room, narrate success. Fail: increment `hintCount`, narrate miss.

### Export / import

- `GET /api/sessions/{id}/export?format=yaml|json` dumps `GameSession`.
- `POST /api/sessions/import` restores YAML or JSON so a restart does not wipe the run.

### Dual panel

- Panel A: Phaser 3 16-bit dungeon — five rooms, four seat sprites, status gems. Kenney Tiny Dungeon sheet in `questshift-ui/public/assets/`.
- Panel B: readable IBM Plex Mono terminal — GM log, command box, seat chips, elapsed clock, export control.

## Success bar

A facilitated party can clear all five rooms of *The Cluster That Forgot Its Name* in **60 minutes**, including when vLLM is down and the engine falls back to campaign YAML.

## Non-goals (v1)

- Browser Web Speech, Piper, or any TTS
- Ollama or any non-vLLM local sidecar
- Multi-party / multi-tenant matchmaking
- Real execution of `oc`, Ansible, Linux, or Java against the workshop cluster
- Native Quarkus image
- Extra campaigns beyond `devops-dungeon`
- A database; v1 is in-memory plus export/import files
- Hiding win conditions only in LLM prompts
