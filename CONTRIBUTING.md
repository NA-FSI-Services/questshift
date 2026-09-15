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

Engine: Java 21, `./mvnw quarkus:dev` in `questshift-engine`. Enable the quality hook once with `./.githooks/install`. PRs to `main` run Spotless, PMD, tests, and JaCoCo via GitHub Actions (`quality.yml`).

UI: Node 22+, `npm install && npm run dev` in `questshift-ui`. Quality: `npm run verify` (Prettier, ESLint, Vitest coverage). Hook: `./.githooks/install`.

Campaigns: edit YAML, then restart the engine (no reload endpoint in v1). Quality: `./verify.sh` (yamllint, ruff, pytest-cov).

GitOps: `oc login` as cluster-admin, then `./install.sh` against a 4.20+ cluster (`oc apply -k k8s/` is fallback only). Keep cluster API URLs and tokens out of git. Quality: `./verify.sh` (yamllint, ruff, shellcheck, kustomize, pytest-cov).

Docs: `./verify.sh` (ruff + spec checker). Each repo's PRs to `main` run workflow **Quality**; mark that check required so a red run cannot merge.

Full tool map, thresholds, and what each checker enforces: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).
