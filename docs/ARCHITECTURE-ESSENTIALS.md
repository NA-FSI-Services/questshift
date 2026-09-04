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

One OpenShift deployment **is** one party. No multi-tenant session router in v1.

## Hard rules

1. Campaign YAML is the puzzle source of truth. The LLM narrates only.
2. If vLLM is down or `%dev`, fall back to authored YAML text. The hour still runs.
3. Terminal is **simulated**. Never execute player `oc`, Ansible, Linux, or Java against the cluster.
4. Serving is **vLLM only**. Model: `ibm-granite/granite-3.1-8b-instruct`. GPU: NVIDIA L4, `nvidia.com/gpu: 1`. No Ollama.
5. Seats (Guardian, Automancer, Cluster Ranger, Artificer) are cosmetic. Any player may solve any puzzle.
6. v1 is JVM, text-only, one party. No TTS, native image, or multi-party.
7. Never commit secrets to GitHub. Hugging Face token is cluster secret `questshift-hf` (`oc create secret`); git may reference the name only. See [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).

## Where code lives

| Concern | Repo | Code |
| --- | --- | --- |
| REST / WS / evaluator / LLM | `questshift-engine` | `io.questshift.*` |
| Phaser board + React terminal | `questshift-ui` | `src/game`, `src/terminal` |
| Adventure YAML | `questshift-campaigns` | `campaigns/*.yaml` |
| OpenShift + vLLM | `questshift-gitops` | `k8s/` |
| Specs | `questshift` | `docs/` |

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

`CommandEvaluator` scores `forbidden_patterns`, then `expected_command_pattern` / `accepted_examples`, then puzzle-type soft checks. Do not hide win conditions only in prompts. `LLMService` may flavor `narrative` and `hint`; it must not invent a new puzzle type or rewrite the regex.
