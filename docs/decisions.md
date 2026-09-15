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
| Default model | IBM Granite 3.2 8B Instruct |
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
| Install credentials | Existing cluster-admin `oc login`; `QUESTSHIFT_HF_TOKEN` in gitignored `.env`. Installer does not take API URLs or tokens. Workshop clusters stay out of git. |
| Cursor | Always-on `.cursor/rules/questshift.mdc` in each repo, plus glob rules (Java / TSX / YAML) |
| Look | 16-bit pixel dungeon; Kenney Tiny Dungeon CC0 sheet in `questshift-ui/public/assets/` |
| Dual panel | Panel A Phaser pixel canvas; Panel B CRT-like terminal in IBM Plex Mono |
| Session restore | Terminal footer file picker (`import.yaml`) posts to existing `POST /api/sessions/import` |
| Phase 1 proof | QuarkusTest submits all five YAML `accepted_examples` then export/import; no live facilitator pass |
| Kenney sheet load | Packed `tilemap_packed.png` is 192×176; Phaser `spacing: 0`. Ignore `Tilesheet.txt` 1px gap |
| Phase 2 board | Full Kenney tilemap: fill Panel A with `floor` / `wall`, place five rooms at `mapX` / `mapY`, plus gems, seat sprites, and `focus` reticle. Not a polyline of circles. |
| Phase 2 loot | HTML inventory strip stays; also draw `loot_*` sprites on Panel A as runes are collected (e.g. along the bottom of the tilemap) |
| Phase 2 gem_hint | Show `gem_hint` on the current room after a failed command (`passed=false`) until the next pass or room change. No new engine field — UI keeps last command result. |
| Phase 2 sprite scale | 3× (48px tiles), `pixelArt: true`, current-room pulse 1.0 → 1.15 |
| Phase 2 Phaser renderer | `Phaser.CANVAS` — the vendored Kenney packed sheet is an 8-bit colormap PNG; WebGL left Panel A blank |
| Phase 2 proof | Vitest named-key → frame map matches [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md); Phaser canvas stays coverage-excluded. PLAN exit is still visual (Panel A reads as a 16-bit dungeon) |
| Quality gates | Format + static analysis + coverage on every repo; hook + GitHub Actions **Quality** (see [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md), local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`) |

## Deliberately not in v1

- Browser Web Speech / Piper TTS
- Ollama local sidecar
- Multi-party / multi-tenant matchmaking
- Real execution of **player** `oc`, Ansible, or a login node (facilitator `./install.sh` is cluster bootstrap only)
- Native Quarkus binary
