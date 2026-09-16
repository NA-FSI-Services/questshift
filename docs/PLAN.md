# QuestShift v1 plan

Phased work for the frozen v1 product only. Scaffold already exists in the five public repos. There are no TTS, Ollama, native-image, or multi-party-matchmaking phases. One-party join codes (many browsers, one hour) are in v1.

Board: https://github.com/orgs/NA-FSI-Services/projects/3

## Phase 0 — scaffold (done)

Five repos, Apache-2.0, Quarkus 3.39 / Java 21 engine, Phaser 3 + React UI, campaign YAML, OpenShift kustomize with vLLM + L4 placeholders. Agent specs and Cursor rules land in this phase’s docs pass.

Exit: clones under the parent `questshift/` workspace run as separate git roots.

## Quality gates (ongoing)

Not a separate phase. Every repo keeps format + static analysis + coverage, a repo-local pre-commit hook, and GitHub Actions **Quality** on `main`. PMD is Java-only (engine); UI uses ESLint, Python repos use ruff. Map, thresholds, and checkers: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`). Day-to-day commands: [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).

## Phase 1 — local engine + UI loop (done)

Engine and UI talk over Vite’s `/api` proxy. The dry-run hour is proven **with LLM disabled** (`%dev` / `%test`).

- `./mvnw quarkus:dev` in `questshift-engine` (campaigns sibling dir).
- `npm run dev` in `questshift-ui`.
- Start session, submit the five `accepted_examples`, export YAML, import YAML, confirm inventory and `puzzleCompletion`.
- Evaluator tests stay green (`CommandEvaluatorTest`, `StateSerializerTest`, `GameResourceTest`).

Exit (met): `./mvnw test` includes `%test` `@QuarkusTest` `GameResourceTest.acceptedExamplesClearTheHourThenExportImport` — starts `devops-dungeon` with LLM off, submits each room’s authored `accepted_examples`, then export/import YAML (inventory + `puzzleCompletion`). A live facilitator regex pass is **not** required to close this phase ([campaigns#1](https://github.com/NA-FSI-Services/questshift-campaigns/issues/1) stays workshop prep).

## Phase 2 — CC0 sprites wired into Phaser (done)

Sheet is vendored at `questshift-ui/public/assets/kenney/tiny-dungeon/tilemap_packed.png`. Fill Panel A with Kenney `floor` / `wall` tiles, then place room sprites, four seat sprites, status gems, the `focus` reticle, and `loot_*` sprites as runes drop. Keep the HTML inventory strip under the canvas. Named keys: [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`). `pixelArt: true`, display scale **3×** (48px), `Phaser.CANVAS` (packed sheet is 8-bit colormap). Canvas events still only restyle nodes (no shake, no particles).

Board: [questshift#4](https://github.com/NA-FSI-Services/questshift/issues/4) (tracker), [ui#1](https://github.com/NA-FSI-Services/questshift-ui/issues/1) (wire `DungeonScene`), [ui#4](https://github.com/NA-FSI-Services/questshift-ui/issues/4) (named-key → frame Vitest). Phaser `src/game/**` stays coverage-excluded; CI proof is the key map.

Exit (met): Panel A reads as a 16-bit dungeon; Panel B stays IBM Plex Mono.

## Phase 3 — live vLLM (done)

Point `questshift.llm.base-url` at a reachable OpenAI-compatible server. Workshop freeze is **vLLM** serving `ibm-granite/granite-3.2-8b-instruct`. Enable the LLM via untracked `application-local.properties` (`%dev.questshift.llm.*`) or the cluster ConfigMap — committed `%dev`/`%test` stay off and `questshift.llm.api-key` stays `none`. Kill the endpoint mid-room (or return HTTP ≥ 300) and confirm YAML fallback. Do not add Ollama.

Board: [questshift#5](https://github.com/NA-FSI-Services/questshift/issues/5) (tracker), [engine#4](https://github.com/NA-FSI-Services/questshift-engine/issues/4) (stubbed client). [questshift#1](https://github.com/NA-FSI-Services/questshift/issues/1) stays the real NVIDIA L4 / Granite 3.2 check.

Exit (met): GM JSON narrates through `LLMService`; room `expected_command_pattern` still comes from YAML (`accepted_examples` still score); unreachable endpoint falls back to authored YAML so the hour still runs. `./mvnw test` never calls a live server.

## Phase 4 — OpenShift apply

Set up OpenShift 4.20+. Log in as cluster-admin (`oc whoami` must succeed) and keep that cluster’s API URL, token, and CA in a local kubeconfig / gitignored `.env` — never in git. From `questshift-gitops` run `./install.sh` (or `./install.sh --install-operators`). The script refuses to run without an existing `oc` session, checks hardware, installs GitOps / NFD / NVIDIA GPU / RHOAI / OpenShift Pipelines if needed, and syncs `k8s/` through OpenShift GitOps. Granite 3.2 8B Instruct is copied from the ModelCar catalog by a Tekton PipelineRun (no Hugging Face token, no MinIO). Publish JVM and nginx images to the in-cluster registry (placeholders today). One party.

Exit: facilitated 60-minute run on the workshop cluster, export/import survives a pod bounce via PVC `questshift-session-export`.

## One-party join (in v1)

Many browsers on the same hour. Shareable `joinCode`; second Start is 409 while `active`. Joiners add a unique alias via `POST /api/sessions/{id}/party` (cap 8). Shared room board is `session.commandLog`. Walkable map + YAML clues: [questshift#10](https://github.com/NA-FSI-Services/questshift/issues/10). Tracker: [questshift#6](https://github.com/NA-FSI-Services/questshift/issues/6).

## Explicitly not scheduled

TTS, Ollama, native Quarkus, multi-party matchmaking across deployments, real command execution, extra campaigns, a database.
