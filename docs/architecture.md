# QuestShift architecture

Lead view of the system as deployed for a facilitated 60-minute team-building run.

## Context

```text
                    ┌─────────────────────────────────────────┐
                    │              OpenShift project           │
  facilitators      │                                         │
  + party  ──Route──┤  questshift-ui (nginx + React/Phaser)   │
                    │           │ REST + WebSocket            │
                    │           ▼                             │
                    │  questshift-engine (Quarkus 21)         │
                    │     ├─ Session + campaign state         │
                    │     ├─ CommandEvaluator                 │
                    │     └─ LLMService ──HTTP /v1/chat...──► │
                    │                         questshift-llm  │
                    │                         vLLM + Granite  │
                    │                         nvidia.com/gpu:1│
                    │                                         │
                    │  PVC: model weights                     │
                    │  ConfigMap/volume: campaign YAML        │
                    └─────────────────────────────────────────┘
```

One OpenShift deployment **is** one party. There is no multi-tenant session router in v1.

## Repos and runtime mapping

| Repo | Artifact | Runtime |
| --- | --- | --- |
| `questshift-ui` | static SPA | nginx container |
| `questshift-engine` | Quarkus JVM (native later) | Java 21 container |
| `questshift-campaigns` | YAML files | mounted into the engine |
| `questshift-gitops` | Deployment, Service, Route, ConfigMap, PVC | OpenShift |
| `questshift` | docs only | — |

## Game loop

1. `POST /api/sessions` loads `campaign-devops-dungeon.yaml` and creates `GameSession`.
2. Engine asks `LLMService` for a Game Master turn. The model **must** return a JSON object:

   ```json
   {
     "narrative": "The shell golem blocks the gate...",
     "puzzle_type": "linux",
     "expected_command_pattern": "grep.*rune",
     "hint": "Pipes remember what eyes forget.",
     "canvas_event": "focus_room"
   }
   ```

3. Authored campaign rooms are the source of truth for `puzzle_type` and `expected_command_pattern`. The LLM supplies narration and optional hint flavor. If vLLM is down, the engine falls back to the YAML text so the hour can still run.
4. Players submit a command. `CommandEvaluator` scores it, updates flags/inventory, and emits a canvas event.
5. `StateSerializer` can dump or restore the session as YAML or JSON.

## LLM contract

- **Serving:** vLLM OpenAI-compatible API only (no Ollama in this design).
- **Model:** `ibm-granite/granite-3.1-8b-instruct`
- **Hardware:** NVIDIA L4 24GB, `nvidia.com/gpu: 1`
- **Client:** `LLMService` in the engine, configurable base URL via ConfigMap

Prompts pin a 60-minute arc, forbid breaking character, and demand a single JSON object (optionally fenced). The Java client parses the first JSON object in the completion.

## Challenge engine

The terminal is **simulated**. Commands are not executed against the workshop cluster.

`CommandEvaluator` applies, in order:

1. Campaign `expected_command_pattern` (regular expression)
2. Puzzle-type checkers (Linux pipelines, Ansible task shape, `oc`/`kubectl` verbs, Java snippet repair)
3. Optional `forbidden_patterns` from the room (catches the known-broken command)

Pass → room complete, loot granted, Phaser node unlocks. Fail → hint counter increments; Game Master can narrate a miss.

## State

`GameSession` persists:

- party members (display name + seat id)
- current room
- inventory and skills
- puzzle completion flags
- elapsed campaign time

Storage in v1 is in-memory plus export/import files. A PVC-backed file dump is the restart story until a real database is justified.

## UI

Dual panel:

- **Panel A** — Phaser 2D board: seats as avatars, five dungeon nodes, status gems
- **Panel B** — retro terminal: Game Master log, command prompt, seat chips

Voice is out of scope for v1.

## Why this split

Campaign authors edit YAML without a Java rebuild. Platform engineers iterate GPU and Routes without a UI release. The engine stays the only writer of game truth.
