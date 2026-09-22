# QuestShift architecture essentials

Agents read this first, then the repo-local `AGENTS.md`. Full system:

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE.md`

## Context

```text
                    ┌─────────────────────────────────────────┐
                    │              OpenShift project           │
  facilitators      │                                         │
  + party  ──Route──┤  questshift-ui (nginx + React/Phaser)   │
                    │           │ REST + WebSocket            │
                    │           ▼                             │
                    │  questshift-engine (Quarkus 3 / Java 21)│
                    │     ├─ Session + campaign state         │
                    │     ├─ CommandEvaluator                 │
                    │     └─ LLMService ──HTTP /v1/chat...──► │
                    │                         questshift-llm  │
                    │                         vLLM + Granite  │
                    │                         nvidia.com/gpu:1│
                    │  PVC: model weights                     │
                    │  ConfigMap: campaign YAML               │
                    └─────────────────────────────────────────┘
```

One OpenShift stack (one Route) hosts **many** in-memory parties. No extra Route or session router. A second browser looks up `GET /api/sessions/{joinCode}` then `POST /api/sessions/{id}/party`. A second Start creates another hour. Leave is `DELETE /api/sessions/{id}/party?name=…`; delete is `DELETE /api/sessions/{id}` (204). Submitted commands persist on `session.commandLog` so every client in the same scoring room sees alias, seat, command, pass/fail, and the Game Master `narrative` addressed to that alias. Scene beats live on `gmLog` with no alias. REST commands fan that snapshot on `/ws/sessions/{id}` to every open socket; the 1s `GET` remains a fallback. Only `session.turnName` may type; the Game Master (engine) rotates the floor after each scored attempt and announces the holder. Clearing the throne freezes the clock and writes `adventureSummary` (most questions, most commands, first accepted command per room). Walk positions and YAML clue pickups use `POST /api/sessions/{id}/presence`; they never score a puzzle and are **not** turn-gated. Chest text is a private map dialog for the opener, and only on the **current layer**: `story.clues` on the overworld (`viewedRoomId` empty), that room’s `clues` inside. Leave closes the dialog. Panel B shows lobby copy or the viewed room’s `narrative`, not another room’s dump. Panel A shows **people**: unique alias beside each Kenney seat sprite, same-layer walkers at last `mapX` / `mapY` (offset if stacked), and occupancy on a room doorway when someone is inside so you do not have to enter The Broken Shell to know Linus is there. `currentRoomId` still gates scoring. Live walks fan out the existing `/ws/sessions/{id}` snapshot to every open socket for that party; the 1s `GET` remains a fallback.

## Hard rules

1. Campaign YAML is the puzzle source of truth. The LLM narrates only.
2. If vLLM is down or `%dev`, fall back to authored YAML text. The hour still runs.
3. Terminal is **simulated**. Never execute player `oc`, Ansible, Linux, or Java against the cluster.
4. Serving is **vLLM only**. Model: `ibm-granite/granite-3.2-8b-instruct`. GPU: NVIDIA L4, `nvidia.com/gpu: 1`. No Ollama.
5. Seats (Guardian, Automancer, Cluster Ranger, Artificer) are cosmetic. Any player may solve any puzzle **when they hold the floor**. The Game Master grants `turnName`; only that alias may type. Walking and chests stay free.
6. v1 is JVM. Game Master stays text (no TTS). Kenney CC0 SFX play on Panel A map events. A Kenney CC0 music bed loops in the quest lobby and quieter in-run (mute control; duck under quest-complete). One OpenShift Route; many in-memory parties. No native image or extra Routes.
7. Never commit secrets to GitHub. Granite weights come from the ModelCar catalog via a Tekton PipelineRun (no Hugging Face token, no MinIO). Workshop API URLs, tokens, kubeconfigs, and CA certs stay in a local `oc` session or gitignored `.env`. See [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).

## Where code lives

| Concern | Repo | Code |
| --- | --- | --- |
| REST / WS / evaluator / LLM | `questshift-engine` | `io.questshift.*` |
| Phaser board + React terminal | `questshift-ui` | `src/game`, `src/terminal` |
| Adventure YAML | `questshift-campaigns` | `campaigns/*.yaml` |
| OpenShift + vLLM | `questshift-gitops` | `k8s/` via `./install.sh` |
| Specs | `questshift` | `docs/` |

Quality gates (format, lint/PMD analog, coverage, hook, GitHub Actions) live in each repo. Map: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).

## Game Master JSON

The model must return one JSON object (optionally fenced). The engine **keeps** the room's `expected_command_pattern` from YAML.

```json
{
  "narrative": "The shell golem blocks the gate...",
  "puzzle_type": "linux",
  "expected_command_pattern": "grep.*rune",
  "hint": "Pipes remember what eyes forget.",
  "canvas_event": "focus_room"
}
```

## YAML wins

`CommandEvaluator` scores `forbidden_patterns`, then `expected_command_pattern` / `accepted_examples`, then puzzle-type soft checks. Do not hide win conditions only in prompts. `LLMService` may flavor `narrative` and `hint`; it must not invent a new puzzle type or rewrite the regex. The GM user prompt includes the speaker alias, the player submission, and the first `accepted_examples` as private coaching on a **scored attempt** (YAML still scores). Scene beats name no player. Advancing to the next room is a scene beat: the previous win is not sent as that room's first attempt. After that answer the engine rotates `turnName` (join order, not Granite) and the narrative announces who has the floor.

Each challenge room has two interior doors: a locked north door with that room's YAML `guardian` (a **cosmetic** Kenney sprite) until the puzzle is solved, and an always-open south door back to the lobby. Beat the guardian with the YAML command (not combat). After a pass, the open north door enters the next YAML room (`order + 1`) if that room is unlocked. The hour is escape-room role-play: walk, authored clues, simulated terminal. Sprite keys and coordinates: [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`).
