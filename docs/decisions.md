# Decisions

Recorded from the kickoff workshop. Change these in the GitHub Project, then update this file.

| Decision | Choice |
| --- | --- |
| Public name | QuestShift |
| GitHub org | [NA-FSI-Services](https://github.com/NA-FSI-Services) |
| License | Apache License 2.0 |
| Repo layout | `questshift`, `questshift-engine`, `questshift-ui`, `questshift-campaigns`, `questshift-gitops` |
| Engine | Quarkus 3 + Java 21 |
| UI | Phaser 3 + React + TypeScript |
| LLM serving | vLLM only |
| Default model | IBM Granite 3.1 8B Instruct |
| GPU | NVIDIA L4, `nvidia.com/gpu: 1` |
| Play mode | One party per deployment |
| Seats | Cosmetic avatars; any player may solve any puzzle |
| TTS | Deferred (text-only v1) |
| Native image | Later; JVM first |
| Puzzle source of truth | Campaign YAML; LLM narrates only; YAML fallback if vLLM is down |
| Terminal | Simulated; never execute player `oc` / Ansible / Linux / Java on the cluster |
| Agent docs | Canonical specs under `docs/` in this repo; thin `AGENTS.md` + `CLAUDE.md` pointers in the other four |
| Filenames | `AGENTS.md` and `CLAUDE.md` at every repo root (tools auto-load) |
| Install on OpenShift | `./install.sh` (GitOps Application); Ansible under `install/` |
| Cursor | Always-on `.cursor/rules/questshift.mdc` in each repo, plus glob rules (Java / TSX / YAML) |
| Look | 16-bit pixel dungeon; Kenney Tiny Dungeon CC0 sheet in `questshift-ui/public/assets/` |
| Dual panel | Panel A Phaser pixel canvas; Panel B CRT-like terminal in IBM Plex Mono |

## Deliberately not in v1

- Browser Web Speech / Piper TTS
- Ollama local sidecar
- Multi-party / multi-tenant matchmaking
- Real execution of **player** `oc`, Ansible, or a login node (facilitator `./install.sh` is cluster bootstrap only)
- Native Quarkus binary
