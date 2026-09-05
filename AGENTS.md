# Agent map — QuestShift (docs repo)

Canonical specs live here. Other repos keep thin `AGENTS.md` + `CLAUDE.md` pointers.

Read [ARCHITECTURE-ESSENTIALS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE-ESSENTIALS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE-ESSENTIALS.md`) first, then the **repo-local** `AGENTS.md` for the tree you are editing.

## Spec index

| Spec | GitHub | Local |
| --- | --- | --- |
| PRD | https://github.com/NA-FSI-Services/questshift/blob/main/docs/PRD.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/PRD.md` |
| Architecture | https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE.md` |
| Essentials | https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE-ESSENTIALS.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE-ESSENTIALS.md` |
| UX | https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md` |
| Game design | https://github.com/NA-FSI-Services/questshift/blob/main/docs/GAME-DESIGN.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/GAME-DESIGN.md` |
| API contract | https://github.com/NA-FSI-Services/questshift/blob/main/docs/API-CONTRACT.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/API-CONTRACT.md` |
| Plan | https://github.com/NA-FSI-Services/questshift/blob/main/docs/PLAN.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/PLAN.md` |
| Workflows | https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md` |
| Campaign authoring | https://github.com/NA-FSI-Services/questshift/blob/main/docs/CAMPAIGN-AUTHORING.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/CAMPAIGN-AUTHORING.md` |
| Install | https://github.com/NA-FSI-Services/questshift/blob/main/docs/INSTALL.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/INSTALL.md` |
| Decisions | https://github.com/NA-FSI-Services/questshift/blob/main/docs/decisions.md | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/decisions.md` |

The kickoff filename `docs/architecture.md` is `docs/ARCHITECTURE.md` (same path on macOS APFS).

## Repos

| Repo | GitHub | Local |
| --- | --- | --- |
| docs | https://github.com/NA-FSI-Services/questshift | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift` |
| engine | https://github.com/NA-FSI-Services/questshift-engine | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-engine` |
| ui | https://github.com/NA-FSI-Services/questshift-ui | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-ui` |
| campaigns | https://github.com/NA-FSI-Services/questshift-campaigns | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns` |
| gitops | https://github.com/NA-FSI-Services/questshift-gitops | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-gitops` |

## Coding constraints

- v1 freeze: Quarkus 3 + Java 21, Phaser 3 + React + TypeScript, vLLM + Granite 3.1 8B Instruct on NVIDIA L4. No Ollama, TTS, native image, or multi-party.
- Campaign YAML is puzzle source of truth. LLM narrates only. YAML fallback if vLLM is down.
- Never execute player `oc` / Ansible / Linux / Java against the cluster.
- Seats are cosmetic. One party per deployment.
- Match existing `io.questshift.*` APIs; do not invent routes.
- Cite both GitHub blob URL and local path when mentioning a markdown spec.
- Apache-2.0 on every repo. Do not add a second license except the Kenney CC0 NOTICE for sprites.
- Do not start phase work that PLAN.md marks out of v1.
- Never commit secrets (HF tokens, `.env`, kubeconfigs, real `questshift.llm.api-key`). Cluster secret `questshift-hf` via `oc create secret` only. Details: [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).
