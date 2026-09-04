# QuestShift architecture

Lead view of the system as deployed for a facilitated 60-minute team-building run. Expands the original kickoff note without changing locked v1 decisions.

The kickoff path `docs/architecture.md` is this file. macOS APFS is case-insensitive, so a separate stub cannot sit beside `ARCHITECTURE.md`. Agents start with `ARCHITECTURE-ESSENTIALS.md`.

Short form for agents:

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE-ESSENTIALS.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE-ESSENTIALS.md`

HTTP/WebSocket shapes:

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/docs/API-CONTRACT.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/API-CONTRACT.md`

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
                    │                                         │
                    │  PVC: model weights                     │
                    │  ConfigMap/volume: campaign YAML        │
                    │  PVC: session export dump               │
                    └─────────────────────────────────────────┘
```

One OpenShift deployment **is** one party. There is no multi-tenant session router in v1. The UI Route proxies `/api/` and `/ws/` to the engine Service.

## Repos and runtime mapping

| Repo | Artifact | Runtime |
| --- | --- | --- |
| `questshift-ui` | static SPA | nginx container; Phaser 3 + React + TypeScript |
| `questshift-engine` | Quarkus JVM | Java 21 container (`io.questshift.*`) |
| `questshift-campaigns` | YAML files | mounted into the engine (`questshift.campaigns.dir`) |
| `questshift-gitops` | Deployment, Service, Route, ConfigMap, PVC | OpenShift |
| `questshift` | docs only | — |

GitHub org: [NA-FSI-Services](https://github.com/NA-FSI-Services). License: Apache-2.0.

## Package map (`io.questshift`)

| Package | Classes | Job |
| --- | --- | --- |
| `io.questshift.api` | `GameResource`, `GameSocket` | REST `/api/*` and WebSocket `/ws/sessions/{sessionId}` |
| `io.questshift.campaign` | `Campaign`, `CampaignLibrary` | Load YAML rooms; default id `devops-dungeon` |
| `io.questshift.engine` | `CommandEvaluator` | Simulated command scoring |
| `io.questshift.llm` | `LLMService` | vLLM client + YAML fallback |
| `io.questshift.session` | `GameSession`, `SessionService`, `StateSerializer` | Live state, export/import |

UI split:

| Path | Panel |
| --- | --- |
| `src/App.tsx` | Dual-panel shell, session start, loot strip |
| `src/game/DungeonScene.ts` | Panel A Phaser board |
| `src/terminal/TerminalPanel.tsx` | Panel B IBM Plex Mono terminal |
| `src/api/client.ts` | REST helpers (`/api/campaigns`, sessions, commands, export) |
| `public/assets/kenney/tiny-dungeon/` | CC0 sprite sheet |

GitOps split: `k8s/llm-deployment.yaml` (vLLM + L4), `game-backend-deployment.yaml`, `game-ui-deployment.yaml`, `configmap.yaml`, `pvc.yaml`, `openshift-route.yaml`, campaign ConfigMap generator.

## Game loop

1. `POST /api/sessions` loads `campaign-devops-dungeon.yaml` (or classpath copy) and creates `GameSession`. Empty party gets four placeholder seats (`guardian`, `automancer`, `ranger`, `artificer`).
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

3. Authored campaign rooms are the source of truth for `puzzle_type` and `expected_command_pattern`. The LLM supplies narration and optional hint flavor. `LLMService.parseTurn` **overwrites** `expectedCommandPattern` with the room regex after parse. If vLLM is down, `%dev`, HTTP ≥ 300, or JSON unparseable, the engine falls back to YAML text so the hour can still run.
4. Players submit a command via REST or a WebSocket text frame. `CommandEvaluator` scores it, updates flags/inventory, and emits a canvas event from the room (`unlock_room_02` … `campaign_complete`) or `focus_room`.
5. `StateSerializer` dumps or restores the session as YAML or JSON.

## LLM contract

- **Serving:** vLLM OpenAI-compatible API only (no Ollama).
- **Model:** `ibm-granite/granite-3.1-8b-instruct`
- **Hardware:** NVIDIA L4 24GB, `nvidia.com/gpu: 1`
- **Client:** `LLMService` in the engine. Base URL `questshift.llm.base-url` (default `http://questshift-llm:8000/v1`). Path appended: `/chat/completions`.
- **Flags:** `questshift.llm.enabled` — **false** in `%dev` and `%test`; true in cluster ConfigMap. Committed `questshift.llm.api-key` is `none`. The Hugging Face hub token is **not** in git: cluster Secret `questshift-hf` created with `oc create secret` (see [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md), local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).
- **Timeout:** `questshift.llm.timeout-seconds` (default 45). Temperature 0.4, `max_tokens` 700.

Prompts pin a 60-minute arc, forbid breaking character, and demand a single JSON object (optionally fenced). The Java client parses the first `{...}` in the completion. `puzzle_type` values: `linux` \| `ansible` \| `openshift` \| `java`.

## Challenge engine

The terminal is **simulated**. Commands are not executed against the workshop cluster.

`CommandEvaluator.evaluate` applies, in order:

1. Empty / blank command → fail
2. Missing `requires_loot` in `GameSession.inventory` → fail
3. Room `forbidden_patterns` (regex, case-insensitive) → fail (“cursed form”)
4. Room `expected_command_pattern` **or** exact `accepted_examples` (whitespace-collapsed) → pass
5. Puzzle-type soft checkers (Linux `grep`+`rune`+`awk`; Ansible `hosts: dungeon` + `gather_facts` + `/etc/questshift/name`; OpenShift `oc`/`kubectl` probe or annotate; Java `@Path("/hello")` + `@GET` + `QuestShift lives` without `greeting.toUpperCase`) → pass
6. Else fail

Pass → room complete, loot ids added, skills granted, Phaser node unlocks via `canvas_event`. Fail → `hintCount` increments; Game Master narrates a miss. Do not hide win conditions only in prompts.

## State

`GameSession` persists in a process-local `ConcurrentHashMap`:

- `id`, `campaignId`, `status` (`active` \| `complete`)
- `currentRoomId`, `startedAt`, `elapsedSeconds`
- party members (display name + seat id)
- `inventory`, `skills`
- `puzzleCompletion` map (room id → boolean)
- `hintCount`
- `lastNarrative`, `lastHint`, `lastCanvasEvent`

Storage in v1 is in-memory plus export/import files. GitOps mounts PVC `questshift-session-export` at `/work/exports` as the restart story until a real database is justified. Import via `POST /api/sessions/import` rehydrates the map.

`CampaignLibrary` loads `*.yaml` from `questshift.campaigns.dir` once; if empty, classpath `campaigns/campaign-devops-dungeon.yaml`. YAML edits require an engine restart in v1 (no reload endpoint).

## UI

Dual panel:

- **Panel A** — Phaser 2D board: Kenney Tiny Dungeon CC0 sheet for rooms, four seats, status gems. Sprite keys in [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`).
- **Panel B** — CRT-like terminal: Game Master log, command prompt, seat chips, elapsed clock. Font is IBM Plex Mono (readable; not a bitmap font).

Voice is out of scope for v1.

Vite (`npm run dev`) proxies `/api` and `/ws` to `localhost:8080`. nginx in cluster does the same against `questshift-engine:8080`.

## Why this split

Campaign authors edit YAML without a Java rebuild. Platform engineers iterate GPU and Routes without a UI release. The engine stays the only writer of game truth.
