# QuestShift v1 plan

Phased work for the frozen v1 product only. Scaffold already exists in the five public repos. There are no TTS, Ollama, native-image, or multi-party phases.

Board: https://github.com/orgs/NA-FSI-Services/projects/3

## Phase 0 — scaffold (done)

Five repos, Apache-2.0, Quarkus 3.39 / Java 21 engine, Phaser 3 + React UI, campaign YAML, OpenShift kustomize with vLLM + L4 placeholders. Agent specs and Cursor rules land in this phase’s docs pass.

Exit: clones under the parent `questshift/` workspace run as separate git roots.

## Phase 1 — local engine + UI loop

Engine and UI already talk over Vite’s `/api` proxy. Finish the dry-run hour **with LLM disabled** (`%dev`).

- `./mvnw quarkus:dev` in `questshift-engine` (campaigns sibling dir).
- `npm run dev` in `questshift-ui`.
- Start session, submit the five `accepted_examples`, export YAML, import YAML, confirm inventory and `puzzleCompletion`.
- Keep evaluator tests green (`CommandEvaluatorTest`, `StateSerializerTest`).

Exit: a facilitator can clear *The Cluster That Forgot Its Name* on localhost with YAML narration.

## Phase 2 — CC0 sprites wired into Phaser

Sheet is vendored at `questshift-ui/public/assets/kenney/tiny-dungeon/tilemap_packed.png`. Replace `Arc` placeholders in `DungeonScene` with named keys from [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`): five rooms, four seats, status gems. `pixelArt: true`. Canvas events still only restyle nodes.

Exit: Panel A reads as a 16-bit dungeon; Panel B stays IBM Plex Mono.

## Phase 3 — live vLLM

Point `questshift.llm.base-url` at a reachable vLLM serving `ibm-granite/granite-3.1-8b-instruct`. Enable `questshift.llm.enabled=true` **outside** `%dev` (or override in a `%prod`-style profile). Kill vLLM mid-room and confirm YAML fallback. Do not add Ollama.

Exit: GM JSON narrates; regex still comes from YAML; fallback still wins the hour.

## Phase 4 — OpenShift apply

`oc new-project questshift`, Hugging Face secret `questshift-hf`, `oc apply -k k8s/` from `questshift-gitops`. GPU operator + NVIDIA L4 already on the node. Publish JVM and nginx images to the in-cluster registry (placeholders today). Route → UI → engine → vLLM. One party.

Exit: facilitated 60-minute run on the workshop cluster, export/import survives a pod bounce via PVC `questshift-session-export`.

## Explicitly not scheduled

TTS, Ollama, native Quarkus, multi-party matchmaking, real command execution, extra campaigns, a database.
