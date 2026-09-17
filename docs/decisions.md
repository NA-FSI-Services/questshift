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
| Play mode | One OpenShift stack (one Route); many in-memory parties per engine |
| Join | Human-readable `joinCode` (two dungeon words). Start always creates a new hour. Members via `POST /api/sessions/{id}/party`. Leave `DELETE …/party?name=`. Delete `DELETE /api/sessions/{id}`. |
| Seats | Cosmetic avatars; any player may solve any puzzle |
| TTS | Deferred (text-only v1) |
| Native image | Later; JVM first |
| Puzzle source of truth | Campaign YAML; LLM narrates only; YAML fallback if vLLM is down |
| Terminal | Simulated; never execute player `oc` / Ansible / Linux / Java on the cluster |
| Agent docs | Canonical specs under `docs/` in this repo; thin `AGENTS.md` + `CLAUDE.md` pointers in the other four |
| Filenames | `AGENTS.md` and `CLAUDE.md` at every repo root (tools auto-load) |
| Install on OpenShift | `./install.sh` (GitOps Application); Ansible under `install/` |
| Install credentials | Existing cluster-admin `oc login`. Installer does not take API URLs or tokens. Workshop clusters stay out of git. |
| Granite weights | Red Hat AI services ModelCar OCI image, copied by a Tekton PipelineRun onto PVC `questshift-llm-cache`. No Hugging Face token. No MinIO/S3. vLLM remains the Game Master runtime. |
| GPU MachineSet | If NFD sees no NVIDIA GPU, clone `g6.4xlarge` (L4) from the first MachineSet. `--no-add-gpu-nodes` opts out. Rendered YAML is gitignored. |
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

## Granite weights — ModelCar, not Hugging Face (2026-09-15)

v1 still serves **IBM Granite 3.2 8B Instruct** through the existing **vLLM Deployment**. The change is only how the weights arrive on the GPU node.

**Choice:** copy weights once from the Red Hat AI services ModelCar catalog image `quay.io/redhat-ai-services/modelcar-catalog:granite-3.2-8b-instruct` onto PVC `questshift-llm-cache`. vLLM loads `/models` offline (`HF_HUB_OFFLINE=1`) and advertises `--served-model-name ibm-granite/granite-3.2-8b-instruct` so the engine ConfigMap does not change. Facilitators no longer set `QUESTSHIFT_HF_TOKEN` or create secret `questshift-hf`.

**Rejected**

- **Hugging Face Hub + `questshift-hf`.** Extra secret, empty-token crash loops, and a pull path the workshop does not need now that Granite 3.2 is packaged as OCI.
- **RHOAI KServe / dashboard model catalog as the Game Master runtime.** [ARCHITECTURE-ESSENTIALS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE-ESSENTIALS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE-ESSENTIALS.md`) freezes vLLM as the serving process. RHOAI stays a cluster operator prerequisite. The ModelCar image is the same OCI catalog RHOAI uses for weights; we do not switch the hour to an `InferenceService`.
- **`registry.redhat.io/rhelai1/modelcar-granite-3-1-8b-instruct`.** That is the validated Red Hat registry ModelCar, but it is Granite **3.1**. v1 freeze stays on **3.2**. When Red Hat publishes a 3.2 (or later freeze) ModelCar on `registry.redhat.io`, swap the init-container image and keep vLLM.

**Layout:** the ModelCar image stores files at `/models`. The Tekton Task must mount the PVC at a different path (`/pvc`) so it does not hide that tree, then `cp -R` onto the volume (`cp -a` fails: the restricted SCC denies `utime` on the PVC mount root). vLLM mounts the PVC at `/models` after the PipelineRun succeeds (Argo sync-wave 10). Do not pin `fsGroup: 1001`; OpenShift `restricted-v2` assigns the project’s allocated group range and rejects a fixed GID. The PipelineRun must land on the GPU node (`feature.node.kubernetes.io/pci-10de.present`) so the RWO volume is attached where vLLM will run.

## Granite install — Tekton Pipeline, not MinIO (2026-09-15)

**Choice:** OpenShift Pipelines copies ModelCar weights in `PipelineRun/questshift-install-granite` (`k8s/granite-pipeline.yaml`). The installer waits for that run before treating the party as ready. vLLM no longer uses a ModelCar init container (that re-pulled ~16Gi on every Recreate).

**Rejected**

- **MinIO / S3 as the weight store.** ModelCar is already OCI. An S3 bucket would need a `Secret` in git or a facilitator-minted key; the freeze forbids `kind: Secret` in `k8s/`. vLLM still reads `/models` on the PVC.
- **RHOAI Data Science Pipelines (KFP + cluster MinIO).** That stack is for notebook/KServe workflows. Game Master serving stays the vLLM Deployment.
- **Keeping the ModelCar init on `questshift-llm`.** It worked, but every pod restart competed with the GPU node for a 16Gi pull. Tekton runs once; later vLLM restarts reuse the PVC.

## Walkable rooms (2026-09-16)

**Choice:** Panel A is a walkable overworld. Party `currentRoomId` still gates which puzzle can be **solved**. Players may enter the current room or completed rooms only. Presence is `POST /api/sessions/{id}/presence` with `{ name, mapX, mapY, viewedRoomId, pickupClueId? }`. Clues are YAML fragments on the floor; `foundClues` is party-shared. WASD only while the canvas is focused. Phaser `src/game/**` stays coverage-excluded; movement/unlock/clue-reach lives in `src/map.ts`.

**Rejected**

- **Overloading `POST /party` with positions.** Join is join; walk is presence.
- **Per-player `currentRoomId` for scoring.** One party, one scoring room.
- **Entering locked future rooms.** The hour stays sequential.
- **Full winning commands as clue text.** Fragments feed Panel B; regex still wins.

## Party aliases and room occupancy (2026-09-16)

**Choice:** Panel A shows people. Every member has a visible unique alias next to their Kenney seat sprite. Same-layer walkers draw at last presence `mapX` / `mapY`; overlapping sprites offset. If Linus is inside The Broken Shell and you are on the overworld, occupancy on that room icon shows he is there — you do not enter to know. Inside a room, only walkers who share that interior are drawn. Presence stays `POST /api/sessions/{id}/presence`. Live walks fan out the existing `/ws/sessions/{id}` `GameSession` snapshot; the 1s `GET` is a fallback. No new REST routes. Seats stay cosmetic. Tracker: [questshift#11](https://github.com/NA-FSI-Services/questshift/issues/11), spec [questshift#12](https://github.com/NA-FSI-Services/questshift/issues/12).

**Rejected**

- **Sprite and seat color without an alias.** Two Guardians look like one avatar.
- **Hiding a player who entered a room from everyone still on the overworld.** Occupancy belongs on the room icon.
- **A second occupancy REST route or a second WebSocket.** Presence POST plus the existing snapshot is enough.
- **Gating who is drawn by cosmetic `seatId`.**
- **Per-player scoring rooms.** `currentRoomId` still gates the puzzle; walking still does not solve it.

## Deliberately not in v1

- Browser Web Speech / Piper TTS
- Ollama local sidecar
- Multi-party / multi-tenant matchmaking across deployments (many in-memory parties share **one** UI Route; see below)
- Real execution of **player** `oc`, Ansible, or a login node (facilitator `./install.sh` is cluster bootstrap only)
- Native Quarkus binary

## One-party join codes (2026-09-15)

**Choice (superseded 2026-09-16):** one live `active` party per engine process and 409 `party_active` on a second Start. Join codes and `POST /api/sessions/{id}/party` remain. See **Concurrent parties** below.

**Rejected then**

- **`POST /api/sessions/join`.** Lookup stays `GET /api/sessions/{joinCode}`. Adding a person is `POST /api/sessions/{id}/party`.
- **UUID as the share code.** Facilitators need something they can say aloud.

## Concurrent parties (2026-09-16)

**Choice:** many `active` parties per engine process (one OpenShift Route). Start always allocates a new `joinCode`. A browser already on `throne-ward` can type `iron-ward` and switch: leave the old hour (`DELETE /api/sessions/{id}/party?name=…`), then join. **Abandon** leaves without joining another. **Delete** (`DELETE /api/sessions/{id}`, 204) is a danger zone in the UI (type the join code). Import of an `active` snapshot sits beside live hours. No extra OpenShift Route.

**Rejected**

- **Keeping 409 `party_active`.** Blocked a second facilitated hour while the first was still in memory.
- **Hiding Join after restore.** A stored `throne-ward` tab could not reach `iron-ward`.
- **A second UI Route per party.**

## Unique alias + cosmetic character (2026-09-16)

**Choice:** Start requires 1–8 real members (no placeholders). Joiners `POST /api/sessions/{id}/party` with `{ name, seatId }`. Aliases are unique (case-insensitive); seats may repeat; cap **8**; pick once (same alias again is idempotent). Suggested names are per-seat lists in [GAME-DESIGN.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/GAME-DESIGN.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/GAME-DESIGN.md`). Picker lives in the topbar.

**Rejected**

- **Four placeholder party members on empty Start.** Silent duplicate labels.
- **One player per seat.** Seats stay cosmetic.
- **Overloading Start with `joinCode` to add a member.**
- **Changing alias or seat after join.**
- **A dedicated lobby screen.**

## Shared command board (2026-09-16)

**Choice:** persist `commandLog` on `GameSession` (alias, seat, command, pass/fail, room). REST GET, the 1s poll, WebSocket snapshot, and export all carry the same rows. Panel B shows the **current room** only. No new route.

**Rejected**

- **WebSocket-only flashes.** Lost after refresh.
- **A second live channel.** The existing snapshot is enough.
- **Showing every room’s attempts at once.** The board is the room the party is in.
