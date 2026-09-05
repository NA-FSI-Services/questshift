# QuestShift

A one-hour, AI-driven dungeon for software developers.

The party shares a Phaser map and a retro terminal. A Granite-backed Game Master narrates. Players solve Linux, Ansible, OpenShift, and Java puzzles. Seats have fantasy names and avatars; **any player can solve any puzzle**.

**GitHub Project:** [QuestShift](https://github.com/orgs/NA-FSI-Services/projects/3)

## Repositories

| Repo | Role |
| --- | --- |
| [questshift](https://github.com/NA-FSI-Services/questshift) | Architecture, decisions, contributor map |
| [questshift-engine](https://github.com/NA-FSI-Services/questshift-engine) | Quarkus 3 / Java 21 session engine |
| [questshift-ui](https://github.com/NA-FSI-Services/questshift-ui) | Phaser 3 + React dual-panel UI |
| [questshift-campaigns](https://github.com/NA-FSI-Services/questshift-campaigns) | Adventure YAML |
| [questshift-gitops](https://github.com/NA-FSI-Services/questshift-gitops) | OpenShift + vLLM on NVIDIA L4 |

All repositories are public under the [Apache License 2.0](LICENSE).

## How a session runs

1. A facilitator deploys one QuestShift stack on OpenShift (one party per deployment).
2. Players pick cosmetic seats: Guardian, Automancer, Cluster Ranger, Artificer.
3. The Game Master walks a 60-minute, five-room campaign.
4. Commands are typed in the shared terminal and scored by the Java evaluator.
5. Session state can be exported/imported as YAML or JSON so a cluster bounce does not wipe the run.

Voice / TTS is deferred. v1 is text-only.

## Install on OpenShift

1. Set up an OpenShift **4.20+** cluster (NVIDIA L4 worker, cluster-admin).
2. Run the installer in [questshift-gitops](https://github.com/NA-FSI-Services/questshift-gitops):

```bash
oc login --server=https://api.CLUSTER:6443
cd questshift-gitops
./install.sh
```

Use `./install.sh --install-operators` to install missing GitOps / NFD / NVIDIA GPU / OpenShift AI operators without prompting. Full contract: [docs/INSTALL.md](docs/INSTALL.md).

## Local layout

Clone siblings under one parent directory, then open the Cursor workspace:

```text
questshift/
  QuestShift.code-workspace
  questshift/
  questshift-engine/
  questshift-ui/
  questshift-campaigns/
  questshift-gitops/
```

In Cursor: **File → Open Workspace from File…** and choose `QuestShift.code-workspace` (or [QuestShift.code-workspace](QuestShift.code-workspace) in this repo). That loads all five git repos as one multi-root project.

## Documentation

Canonical specs live in this repo. Agents: read `AGENTS.md`, then [ARCHITECTURE-ESSENTIALS.md](docs/ARCHITECTURE-ESSENTIALS.md).

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

The kickoff filename `docs/architecture.md` is the same file as `ARCHITECTURE.md` on macOS APFS (case-insensitive). Git records `ARCHITECTURE.md`.

Also: [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md).

## Locked decisions

- **Name:** QuestShift
- **Engine:** Quarkus 3 + Java 21
- **UI:** Phaser 3 + React + TypeScript
- **LLM:** vLLM only, IBM Granite 3.1 8B Instruct, NVIDIA L4 (`nvidia.com/gpu: 1`)
- **Play mode:** one party per deployment, cosmetic seats, shared canvas + terminal
- **License:** Apache-2.0
