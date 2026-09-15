# QuestShift quality gates (v1)

Format, static analysis, and coverage on every repo. PMD is Java-only; other repos use the stack analog (ESLint or ruff). Checkers never execute player commands and never talk to a live cluster.

How humans run the gates day to day: [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).

## Shared pattern

Each of the five repos has:

1. A local verify command (format + lint + tests with a coverage floor).
2. A repo-local Git hook at `.githooks/` — enable once per clone with `./.githooks/install` (sets `core.hooksPath`, not a global hook).
3. GitHub Actions workflow **Quality** (`.github/workflows/quality.yml`) on pull requests and pushes to `main`.
4. Dependabot (`.github/dependabot.yml`) opens weekly PRs that bump GitHub Actions used in those workflows. Grouped into one PR per repo. The Quality job still has to pass before merge.
5. Secret scan (`.githooks/check-secrets`): staged files on commit, whole tree in CI. Blocks PEM private keys, Hugging Face `hf_` tokens, GitHub pats, AWS `AKIA` keys, `.env` / kubeconfig / `*.pem` filenames, and a `questshift.llm.api-key` that is not `none`.

Mark the **Quality** job required on `main` so a red run cannot merge. `SKIP_QUESTSHIFT_HOOKS=1` skips lint/coverage only; `.githooks/check-secrets` still runs. Full bypass: `git commit --no-verify`. Local overrides live in gitignored `.githooks/config` (copy `.githooks/config.example`).

| Repo | Format / lint | Static analysis | Coverage | Local command | CI job |
| --- | --- | --- | --- | --- | --- |
| [engine](https://github.com/NA-FSI-Services/questshift-engine) | Spotless (Google Java Format AOSP) | PMD 7, priority ≤ 3, `maxAllowedViolations=0`, `pmd/ruleset.xml` | JaCoCo ≥ 80% lines / 70% branches on `io.questshift.*` | `./mvnw verify` | **Format, PMD, coverage** |
| [ui](https://github.com/NA-FSI-Services/questshift-ui) | Prettier | ESLint | Vitest ≥ 80% lines / 70% branches (excludes Phaser canvas) | `npm run verify` | **Format, lint, coverage** |
| [campaigns](https://github.com/NA-FSI-Services/questshift-campaigns) | yamllint | ruff | pytest-cov ≥ 80% on `tools/` | `./verify.sh` | **Lint, ruff, coverage** |
| [gitops](https://github.com/NA-FSI-Services/questshift-gitops) | yamllint + shellcheck | ruff + `kustomize`/`kubectl kustomize k8s` | pytest-cov ≥ 80% on probe/helpers | `./verify.sh` | **Format, lint, coverage** |
| [docs](https://github.com/NA-FSI-Services/questshift) | ruff format | ruff + spec checker | pytest-cov ≥ 80% on `tools/` | `./verify.sh` | **Format, lint, coverage** |

Python repos: `python3 -m pip install -r requirements-dev.txt` then `./verify.sh`. UI: Node 22+, `npm ci` then `npm run verify`. Engine: Java 21 + Maven wrapper.

## Engine — `questshift-engine`

- Format: `./mvnw spotless:apply` / `spotless:check`.
- Tests: surefire `*Test.java` (unit + `@QuarkusTest`); failsafe `*IT.java` on `./mvnw verify`. `%test.questshift.llm.enabled=false`.
- Pre-commit runs `./mvnw -Ppre-commit verify` (Spotless, unit/`@QuarkusTest`, PMD, JaCoCo; skips ITs). CI runs full `./mvnw verify`.
- Report: `target/jacoco-report/index.html`.
- Phase 1 hour proof: `GameResourceTest.acceptedExamplesClearTheHourThenExportImport` (LLM off).
- Phase 3 CI: `LLMServiceTest` enabled-narrate cases keep YAML `expectedCommandPattern` and fall back on HTTP errors. Do not call a live vLLM in `./mvnw test`.

## UI — `questshift-ui`

- `npm run format:check` (Prettier), `npm run lint` (ESLint), `npm run test:coverage` (Vitest + v8), then production `build`.
- Phaser `src/game/**` is excluded from the coverage floor (canvas). Terminal, REST client, and App shell are in scope.
- `npm run verify` is the merge gate.

## Campaigns — `questshift-campaigns`

`./verify.sh` runs yamllint on `campaigns/`, ruff on `tools/` and `tests/`, pytest-cov, then `python3 -m tools.campaign`.

The campaign checker (`tools/campaign.py`) enforces the v1 authoring contract from [CAMPAIGN-AUTHORING.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/CAMPAIGN-AUTHORING.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/CAMPAIGN-AUTHORING.md`):

- Exactly one YAML, `kind: Campaign`, id `devops-dungeon`, `durationMinutes: 60`, five rooms ordered 1–5.
- Required room fields (`expected_command_pattern`, `accepted_examples`, `hint`, fallback `narrative`, …).
- Regexes compile; seats stay cosmetic (no `required_seat`).
- Rejects secret-looking text (`hf_…`, private keys, `AKIA…`).

YAML remains the puzzle source of truth. This checker does not score player commands; `CommandEvaluator` does that in the engine.

## GitOps — `questshift-gitops`

`./verify.sh` runs ruff on `tools/`, `tests/`, and `install/scripts/`; yamllint on top-level `k8s/*.yaml` and `argocd/`; shellcheck on `install.sh` / `verify.sh` / hooks when `shellcheck` is on `PATH`; `kubectl kustomize k8s` (or `kustomize build k8s`) when those tools exist; pytest-cov; then `python3 -m tools.manifests`.

The freeze checker (`tools/manifests.py`) scans `k8s/`:

- Forbidden: `kind: Secret`, `stringData:`, `ollama`.
- Required: `vllm`, `ibm-granite/granite-3.2-8b-instruct`, `questshift-hf`, `nvidia.com/gpu` request of **1**.

Probe and wait scripts (`install/scripts/cluster_probe.py`, `wait_application.py`, `wait_operator.py`) have unit tests with mocked `oc`. Quality CI does not log into a cluster. Facilitator install remains [INSTALL.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/INSTALL.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/INSTALL.md`).

## Docs — `questshift`

`./verify.sh` runs ruff on `tools/` and `tests/`, pytest-cov, then `python3 -m tools.specs`.

The spec checker (`tools/specs.py`) requires the files in `AGENTS.md` (including this one), rejects token-like strings in markdown, and asserts [ARCHITECTURE-ESSENTIALS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE-ESSENTIALS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE-ESSENTIALS.md`) still names vLLM, Granite 3.2 8B Instruct, `nvidia.com/gpu`, and “No Ollama”. It is not a markdownlint pass over prose or tables.

## What these gates are not

- Not a live OpenShift probe. `./install.sh --check-only` is the cluster check.
- Not player-command execution. The terminal stays simulated.
- Not a second license or a second LLM runtime. No Ollama, TTS, or native-image jobs.
