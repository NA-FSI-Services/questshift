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
| TTS | Deferred (Game Master stays text; no Web Speech) |
| Map SFX | Kenney CC0 clips on door / room enter / chest / quest complete |
| Music bed | Kenney CC0 Music Loops (`bgm_lobby`, quieter `bgm_dungeon`); mute persists for the tab; duck under quest-complete |
| Pre-run | Dedicated quest lobby (campaign picker + character/alias); dual panel only after Start/Join/restore |
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
| Look | 16-bit pixel dungeon; Kenney Tiny Dungeon CC0 sheet plus Kenney RPG Audio / Music Jingles SFX in `questshift-ui/public/assets/` |
| Dual panel | Panel A Phaser pixel canvas; Panel B CRT-like terminal in IBM Plex Mono |
| Session restore | Terminal footer file picker (`import.yaml`) posts to existing `POST /api/sessions/import` |
| Phase 1 proof | QuarkusTest submits all five YAML `accepted_examples` then export/import; no live facilitator pass |
| Kenney sheet load | Packed `tilemap_packed.png` is 192×176; Phaser `spacing: 0`. Ignore `Tilesheet.txt` 1px gap |
| Phase 2 board | Full Kenney tilemap: fill Panel A with `floor` / `wall`, wooden gates at `mapX` / `mapY` (`lobby_gate` for current, locked, and resolved rooms), plus gems, seat sprites, and `focus` reticle. No `path` / `path_rocks` snake. Not a polyline of circles. Interior doors use `door` / `door_locked` (tiles 45 / 21). |
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

**Choice:** Panel A is a walkable overworld. Party `currentRoomId` still gates which puzzle can be **solved**. Players may enter the current room or completed rooms only. Presence is `POST /api/sessions/{id}/presence` with `{ name, mapX, mapY, viewedRoomId, pickupClueId? }`. Clues are YAML fragments in floor chests. Opening a chest shows a map dialog to **that player only**; the chest stays on the floor so every player can still open it. `partyMembers[].foundClues` tracks who opened what. Session `foundClues` is the export union. WASD only while the canvas is focused. Phaser `src/game/**` stays coverage-excluded; movement/unlock/clue-reach lives in `src/map.ts`.

**Rejected**

- **Overloading `POST /party` with positions.** Join is join; walk is presence.
- **Per-player `currentRoomId` for scoring.** One party, one scoring room.
- **Entering locked future rooms.** The hour stays sequential.
- **Full winning commands as clue text.** Fragments feed a private map dialog; regex still wins.
- **Dumping chest text on the shared terminal.** Only the opener reads the well.

## Layer-scoped map dialogs (2026-09-22)

**Choice:** Map dialogs belong to the current layer. Overworld (`viewedRoomId` empty) reads `story.clues` only, at overworld `x` / `y`. An interior reads that room’s `clues` only. Leave or enter another room closes the open dialog. Panel B shows lobby copy (`story.opening`) or that room’s `narrative` — not another room’s dump. Pickup is still `POST /api/sessions/{id}/presence`; empty `viewedRoomId` may pick a lobby id and still refuses room ids. Chests stay on the floor; text stays private to the opener; pickup never scores. Tracker: [questshift#21](https://github.com/NA-FSI-Services/questshift/issues/21) (spec [#22](https://github.com/NA-FSI-Services/questshift/issues/22), campaigns [#23](https://github.com/NA-FSI-Services/questshift/issues/23), UI [#24](https://github.com/NA-FSI-Services/questshift/issues/24) [#25](https://github.com/NA-FSI-Services/questshift/issues/25), engine [#26](https://github.com/NA-FSI-Services/questshift/issues/26)). Follow-on to [questshift#10](https://github.com/NA-FSI-Services/questshift/issues/10). This is the in-run Kenney lobby map, not the pre-run Start screen in [questshift#16](https://github.com/NA-FSI-Services/questshift/issues/16).

**Rejected**

- **Flattening every room’s chests onto Panel A.** Each layer has its own authored set.
- **Opening a foreign-layer chest id** (Playbook from the Shell, or `shell-log` from the lobby).
- **Refusing all pickups when `viewedRoomId` is empty.** That blocked lobby clues.
- **A new REST route for lobby pickup.** Presence grows only by allowing `story.clues` on the overworld.
- **Dumping chest `text` or another room’s `narrative` on Panel B** after you leave through the south door.
- **TTS.**

## Party aliases and room occupancy (2026-09-16)

**Choice:** Panel A shows people. Every member has a visible unique alias next to their Kenney seat sprite. Same-layer walkers draw at last presence `mapX` / `mapY`; overlapping sprites offset. If Linus is inside The Broken Shell and you are on the overworld, occupancy on that room icon shows he is there — you do not enter to know. Inside a room, only walkers who share that interior are drawn. Presence stays `POST /api/sessions/{id}/presence`. Live walks fan out the existing `/ws/sessions/{id}` `GameSession` snapshot; the 1s `GET` is a fallback. No new REST routes. Seats stay cosmetic. Tracker: [questshift#11](https://github.com/NA-FSI-Services/questshift/issues/11), spec [questshift#12](https://github.com/NA-FSI-Services/questshift/issues/12).

**Rejected**

- **Sprite and seat color without an alias.** Two Guardians look like one avatar.
- **Hiding a player who entered a room from everyone still on the overworld.** Occupancy belongs on the room icon.
- **A second occupancy REST route or a second WebSocket.** Presence POST plus the existing snapshot is enough.
- **Gating who is drawn by cosmetic `seatId`.**
- **Per-player scoring rooms.** `currentRoomId` still gates the puzzle; walking still does not solve it.

## Kenney map SFX, not TTS (2026-09-17)

**Choice:** Panel A plays four short Kenney CC0 clips (RPG Audio + Music Jingles) on door, room enter, chest, and room complete. Game Master narration stays text. No Web Speech, Piper, or spoken GM lines. A Kenney CC0 **music bed** was added later (see **Quest lobby and Kenney music bed**). WASD footsteps stay out.

**Rejected**

- **TTS / Web Speech for GM copy.** Still deferred. SFX are map confirmation, not voice.
- **AI-generated audio or a second audio license.** Same Kenney CC0 exception as the sprite sheet.
- **WASD footsteps.** Too noisy for a facilitated hour.

Named keys: [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`).

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

**Choice:** Start requires 1–8 real members (no placeholders). Joiners `POST /api/sessions/{id}/party` with `{ name, seatId }`. Aliases are unique (case-insensitive); seats may repeat; cap **8**; pick once (same alias again is idempotent). Suggested names are per-seat lists in [GAME-DESIGN.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/GAME-DESIGN.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/GAME-DESIGN.md`). Picker lives in the **quest lobby** (see **Quest lobby and Kenney music bed** below). The 2026-09-16 topbar picker is superseded.

**Rejected**

- **Four placeholder party members on empty Start.** Silent duplicate labels.
- **One player per seat.** Seats stay cosmetic.
- **Overloading Start with `joinCode` to add a member.**
- **Changing alias or seat after join.**

## Shared command board (2026-09-16)

**Choice:** persist `commandLog` on `GameSession` (alias, seat, command, pass/fail, room). REST GET, the 1s poll, WebSocket snapshot, and export all carry the same rows. `POST /api/sessions/{id}/commands` fans that snapshot to every open `/ws/sessions/{id}` so every browser in the party sees the attempt and GM prose without waiting. Panel B shows the **current room** only. No new route.

**Rejected**

- **WebSocket-only flashes.** Lost after refresh.
- **A second live channel.** The existing snapshot is enough.
- **Showing every room’s attempts at once.** The board is the room the party is in.

## Challenge doors and guardians (2026-09-17)

**Choice:** Every challenge room has two interior doors. South is the lobby door, always open (`door` at `(450, 470)`); Esc / click / E on it returns to the overworld. North is the challenge door: `door_locked` plus that room’s YAML `guardian` until the puzzle is solved, then an open `door` with no guardian. Beating the guardian is the YAML command in the terminal, not a combat system. Distinct Kenney sprites per room (`guardian_shell` / `guardian_playbook` / `guardian_pod` / `guardian_servlet` / `guardian_throne`). Author `guardian: { id, title, sprite }` on every room. After a pass, the open north door enters the next YAML room (see 2026-09-22).

**Rejected**

- **Guardian on the south lobby door.** Players must always be able to leave.
- **A real combat minigame.** YAML regex still wins. The sprite is cosmetic. The hour is escape-room role-play (walk, clues, simulated terminal), not a battle.

## North door to the next challenge (2026-09-22)

**Choice:** After `puzzleCompletion[roomId]`, the north `door` is a real exit into the next YAML room (`order + 1`) when that room is already unlocked (`currentRoomId` after the pass, or completed). Click it, or E / Enter while standing on it. Presence still sets `viewedRoomId` and still refuses locked future rooms. The south lobby door still returns to the overworld; overworld gates still work. The throne has no successor — its open north door is a no-op. Scoring still only advances via YAML. The guardian sprite stays cosmetic (not combat).

**Rejected**

- **Forcing a lobby hop after every pass.** The north door is the sequential path; the lobby remains an alternate.
- **Auto-moving the whole party when anyone solves.** Only the walker who uses the door changes `viewedRoomId`.
- **Skipping YAML unlock.** The next room must already be `currentRoomId` or completed.

## No combat (2026-09-22)

**Choice:** Reaffirm 2026-09-17. Tracker [questshift#27](https://github.com/NA-FSI-Services/questshift/issues/27) and children [#28](https://github.com/NA-FSI-Services/questshift/issues/28)–[#31](https://github.com/NA-FSI-Services/questshift/issues/31) (defend-the-solver, floor weapons, presence combat, Phaser intercept) are **closed not planned**. The north-door `guardian` is a cosmetic Kenney sprite. Beating it is the YAML command. Do not add weapons, HP, knockback, or a second player holding a golem while someone types.

**Rejected**

- **Battle / weapon pickup / intercept minigame.** Out of product. Escape-room role-play only.

## Lobby gates (2026-09-22)

**Choice:** Every overworld node uses `lobby_gate` (tile 9), including the current scoring room. Drop the `path` / `path_rocks` snake. `focus`, status gems, and the current-room pulse still mark which gate scores. Walking and YAML scoring are unchanged.

**Rejected**

- **`lobby_gate_open` on the active gate.** Same closed door as locked and resolved rooms.
- **A painted trail between rooms.** The lobby is `floor` / `wall` fill plus gates.

## Game Master addressee (2026-09-22)

**Choice:** Two kinds of Game Master turn. A **scene beat** (Start, or the opening of the next room) appends `gmLog` as `{ roomId, narrative }` with no alias. An **attempt reply** (`POST /api/sessions/{id}/commands`, including authored `miss_beats`) stamps `narrative` on that `commandLog` row. `name` is the addressee — the same `resolveAlias` the board already uses. `lastNarrative` stays the latest line and is not the history. Replies stay on the shared scoring-room board. The LLM prompt includes the speaker alias and must not rewrite `expected_command_pattern`. Export and import carry `narrative` and `gmLog`. Spec: [API-CONTRACT.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/API-CONTRACT.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/API-CONTRACT.md`), [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`). Tracker [questshift#32](https://github.com/NA-FSI-Services/questshift/issues/32) (spec [#33](https://github.com/NA-FSI-Services/questshift/issues/33), engine [#34](https://github.com/NA-FSI-Services/questshift/issues/34), UI [#35](https://github.com/NA-FSI-Services/questshift/issues/35)).

**Rejected**

- **One session-wide `lastNarrative` as the only GM history.** Refresh dropped every reply but the last, and none of them named who asked.
- **Storing the next-room opening on the passer’s `commandLog` row.** That beat is to the room.
- **A private whisper, or a new REST route.** Ada still sees Linus’s reply. Chest dialogs stay the private channel.
- **Letting Granite invent a traveler or rewrite the regex.** YAML still scores.

## Respect for turns (2026-09-22)

**Choice:** The Game Master grants **the floor**. Persist `turnName` on `GameSession`. Only that alias may `POST /api/sessions/{id}/commands`. After a scored attempt (pass or fail) the engine rotates to the next `partyMembers` alias (circular; solo keeps the floor) and the GM prose announces the grant. Start grants the first Start alias. Joiners wait. Leave of the holder grants the next remaining member. Import restores `turnName` if that alias is still in the party. Presence, walking, occupancy, and chest dialogs stay ungated. Seats stay cosmetic; YAML still scores; no extra REST route. Tracker [questshift#36](https://github.com/NA-FSI-Services/questshift/issues/36) (spec [#37](https://github.com/NA-FSI-Services/questshift/issues/37), engine [#38](https://github.com/NA-FSI-Services/questshift/issues/38), UI [#39](https://github.com/NA-FSI-Services/questshift/issues/39)); follow-on to GM addressee [questshift#32](https://github.com/NA-FSI-Services/questshift/issues/32). The LLM does **not** pick the speaker.

**Rejected**

- **Everyone types at once.** Parallel questions bury who the GM is answering ([questshift#32](https://github.com/NA-FSI-Services/questshift/issues/32)).
- **Granite choosing `turnName`.** YAML fallback must still rotate.
- **Gating walk / chests / occupancy by turn.** Escape-room movement stays free.
- **Gating by `seatId`.** Seats stay cosmetic.
- **A second “pass the floor” REST route.** Rotation is automatic after each GM answer.
- **WebSocket text frames scoring as `shared`.** That path must not bypass the floor.

## Quest lobby and Kenney music bed (2026-09-22)

**Choice:** Thaw the dedicated lobby and a Kenney CC0 music bed for playtesting. Tracker [questshift#16](https://github.com/NA-FSI-Services/questshift/issues/16) (spec [#17](https://github.com/NA-FSI-Services/questshift/issues/17), lobby UI [#18](https://github.com/NA-FSI-Services/questshift/issues/18), character picker [#19](https://github.com/NA-FSI-Services/questshift/issues/19), music [#20](https://github.com/NA-FSI-Services/questshift/issues/20)). Before this browser is in a party, show a React **quest lobby** (not dual-panel play). Cards come from existing `GET /api/campaigns`; v1 shipped **one** card (`devops-dungeon`). Character + unique alias move into that lobby. Start/Join still hit `POST /api/sessions` and `GET` + `POST …/party`. After Start, collapse to **Party {joinCode}**; switch / new party return to the lobby. Named looping beds `bgm_lobby` (`Wacky Waiting.ogg`) and quieter `bgm_dungeon` (`Infinite Descent.ogg`) from Kenney Music Loops 1.1. Unlock on first click/key. Mute persists for the tab. Duck under `sfx_quest_complete`. HTMLAudio plays the bed so Phaser need not be mounted. Extra Routes, TTS, and seat-gated puzzles stay frozen. A second campaign card is post-v1 (see **Second campaign ansible-bastion**).

**Rejected**

- **Keeping Start/Join on an empty topbar in front of Panel A/B.** Playtesting needed a pre-run pick.
- **Authoring a second campaign YAML in the same lobby thaw.** Deferred to post-v1 ([questshift#40](https://github.com/NA-FSI-Services/questshift/issues/40)).
- **A second OpenShift Route or session router.**
- **TTS / mic / WASD footsteps.**
- **AI audio or a second music license.** Kenney CC0 only.

## Second campaign `ansible-bastion` (2026-09-23)

**Choice:** Post-v1 ships a second 60-minute card, `ansible-bastion` (*The Bastion That Lost Its Runbook*), beside default `devops-dungeon`. Lobby lists both from `GET /api/campaigns`. Five rooms, all `puzzle_type: ansible` (copy/template → package+service → firewall/SG → AWS module → Controller *Aether* boss). Simulated terminal only; YAML regex + `accepted_examples` score; never execute `ansible-playbook` or call AWS/AAP. Reuse Kenney `guardian_*` sprites with new titles. Tracker: [questshift#40](https://github.com/NA-FSI-Services/questshift/issues/40) (spec [#41](https://github.com/NA-FSI-Services/questshift/issues/41)). Authoring: [CAMPAIGN-AUTHORING.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/CAMPAIGN-AUTHORING.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/CAMPAIGN-AUTHORING.md`).

**Rejected**

- **Live AWS API or Automation Controller from engine or browser.** Still simulated text.
- **Hiding wins only in `system_prompt`.** Regex + examples remain the scorer.
- **Combat / new Routes / TTS.** Unchanged freezes.
- **An open-ended campaign library.** Exactly two shipped cards for now; default stays `devops-dungeon`.
