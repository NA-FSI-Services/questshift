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

## Local layout

Clone siblings under one parent directory:

```text
questshift/
  questshift/
  questshift-engine/
  questshift-ui/
  questshift-campaigns/
  questshift-gitops/
```

Then see [docs/architecture.md](docs/architecture.md) and each repo README.

## Locked decisions

- **Name:** QuestShift
- **Engine:** Quarkus 3 + Java 21
- **UI:** Phaser 3 + React + TypeScript
- **LLM:** vLLM only, IBM Granite 3.1 8B Instruct, NVIDIA L4 (`nvidia.com/gpu: 1`)
- **Play mode:** one party per deployment, cosmetic seats, shared canvas + terminal
- **License:** Apache-2.0
