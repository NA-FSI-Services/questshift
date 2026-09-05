# Contributing to QuestShift

You are welcome to open issues and pull requests against any QuestShift repository in [NA-FSI-Services](https://github.com/NA-FSI-Services).

## Where to change what

| Change | Repository |
| --- | --- |
| Architecture, this guide | `questshift` |
| REST/WebSocket, evaluator, LLM client | `questshift-engine` |
| Canvas, terminal, client API | `questshift-ui` |
| Rooms, narration, expected patterns | `questshift-campaigns` |
| OpenShift, vLLM, GPU, Routes | `questshift-gitops` |

Track work on the [QuestShift project board](https://github.com/orgs/NA-FSI-Services/projects/3).

## Rules of the road

1. Apache License 2.0 on every repo. Do not add a second license.
2. Keep the Game Master output schema stable. If you add a field, make it optional.
3. Campaign YAML is the puzzle source of truth. Do not hide win conditions only in LLM prompts.
4. Do not execute player commands on the cluster in v1.
5. One party per deployment until the engine grows a session router.

## Dev loop

Engine: Java 21, `./mvnw quarkus:dev` in `questshift-engine`.

UI: Node 22+, `npm install && npm run dev` in `questshift-ui`.

Campaigns: edit YAML, restart the engine or hit the reload endpoint.

GitOps: `./install.sh` against a 4.20+ cluster (`oc apply -k k8s/` is fallback only).
