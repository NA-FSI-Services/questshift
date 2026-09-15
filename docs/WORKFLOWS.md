# QuestShift workflows (v1)

How humans and agents run the stack. Committed `%dev` and `%test` keep the LLM **off**. An untracked `application-local.properties` overlay can enable live narration in `quarkus:dev` only.

## Layout

Sibling clones, then open `QuestShift.code-workspace` from the parent directory.

```text
/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/
  QuestShift.code-workspace
  questshift/                 docs
  questshift-engine/          Quarkus
  questshift-ui/              Vite + Phaser
  questshift-campaigns/       YAML
  questshift-gitops/          kustomize
```

## Engine — `./mvnw quarkus:dev`

Java 21, Maven 3.9+. From `questshift-engine`:

```bash
./mvnw quarkus:dev
```

Listens on `http://localhost:8080`. Swagger: `/q/swagger-ui`. Health: `/q/health/ready`.

`application.properties`:

- `questshift.campaigns.dir=../questshift-campaigns/campaigns`
- `%dev.questshift.llm.enabled=false` ← YAML narration, no live LLM unless an untracked overlay overrides `%dev.*`
- `%test.questshift.llm.enabled=false`

Tests: `./mvnw test` (surefire: `*Test.java`). Quality gate: `./mvnw verify` (Spotless, PMD max 0 medium+ violations, failsafe `*IT.java`, JaCoCo 80% line / 70% branch). Format: `./mvnw spotless:apply`. Engine pre-commit: `./.githooks/install` then commit; it runs `./mvnw -Ppre-commit verify` (same gates minus ITs). Engine PRs to `main`: GitHub Actions workflow **Quality** (`./mvnw verify`). Map: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`). Phase 1 proof is `GameResourceTest.acceptedExamplesClearTheHourThenExportImport` (LLM off). A live facilitator regex pass is not required to close Phase 1.

Phase 3 (live GM narration): copy `questshift-engine/application-local.properties.example` to gitignored `application-local.properties`. Set `%dev.questshift.llm.enabled=true` plus `base-url`, `model`, and `api-key` for an OpenAI-compatible server. Committed defaults stay **vLLM** + `ibm-granite/granite-3.2-8b-instruct` and `questshift.llm.api-key=none`. Cluster ConfigMap is the workshop runtime. Do not commit the overlay. `LLMServiceTest` proves GM JSON keeps the YAML regex and HTTP errors fall back to YAML without calling a real endpoint.

## UI — `npm run dev`

Node 22+. Engine already on `:8080`. From `questshift-ui`:

```bash
npm install
npm run dev
```

Vite on `http://localhost:5173` proxies `/api` → `http://127.0.0.1:8080` and `/ws` → `ws://127.0.0.1:8080` (IPv4, so another process bound to `*:8080` does not steal the API).

Quality: `npm run verify` (Prettier, ESLint, Vitest ≥ 80% lines / 70% branches). Pre-commit: `./.githooks/install`. PRs to `main`: GitHub Actions **Quality** / **Format, lint, coverage**. Map: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).

## Campaign edit + reload

1. Edit `questshift-campaigns/campaigns/campaign-devops-dungeon.yaml`.
2. Restart the engine. `CampaignLibrary` loads YAML **once** into a map; there is no reload endpoint.
3. Start a **new** session (`POST /api/sessions`). Existing sessions keep old room data in memory.

Keep a classpath copy in `questshift-engine/src/main/resources/campaigns/` in sync when you change the canonical file, or local-only runs that miss the sibling dir will serve stale rooms.

Quality: `./verify.sh` in `questshift-campaigns` (yamllint, ruff, pytest-cov). Pre-commit: `./.githooks/install`. Contract details: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).

## Export / import session

```bash
# YAML dump
curl -s "http://localhost:8080/api/sessions/$ID/export?format=yaml" -o run.yaml

# restore
curl -s -X POST "http://localhost:8080/api/sessions/import?format=yaml" \
  --data-binary @run.yaml -H 'Content-Type: application/yaml'
```

UI: Panel B **export.yaml** downloads `questshift-{id}.yaml`. **import.yaml** is a file picker that posts the file to `POST /api/sessions/import` (works with or without a live session).

## Secrets — never commit to GitHub

v1 secrets live in the cluster (or an untracked local file), never in git.

| Secret | How it exists | What git may contain |
| --- | --- | --- |
| Hugging Face hub token | `oc create secret generic questshift-hf --from-literal=token=...` | Secret **name** `questshift-hf` and `secretKeyRef` only |
| `questshift.llm.api-key` | default `none` in committed `application.properties`; real keys only in gitignored `application-local.properties` | The word `none`, never a real key |
| Local OpenAI-compatible URL / model | gitignored `application-local.properties` (`%dev.questshift.llm.*`) | Example placeholders in `application-local.properties.example` |
| kubeconfig / cluster API / CA | local `oc login`, `KUBECONFIG`, gitignored `.env` | nothing (no hostnames, tokens, or certs) |

Do:

- Create `questshift-hf` with `./install.sh` (or `oc create secret` on the cluster). Docs may show the placeholder `YOUR_HF_TOKEN` only. Never put the token in git.
- Put local LLM overrides and installer secrets in untracked files (`application-local.properties`, `.env`). Copy `questshift-gitops/.env.example` to `.env`. Those names are gitignored.
- Keep `k8s/` limited to `secretKeyRef` (name + key). Never add a `Secret` manifest with `stringData` or a real token.
- Log in with `oc login` before `./install.sh`. The installer refuses to run without an existing session and does not accept cluster API URLs or tokens as flags.

Do not:

- Commit `.env`, kubeconfigs, `*.pem`, `*.crt`, private keys, Hugging Face tokens, OpenShift API JWTs, lab hostnames, or `Secret` YAML that embeds a token.
- Paste tokens, CA certificates, or a specific workshop API URL into campaign YAML, ConfigMaps, README samples, issues, or session export files.
- Open a PR that changes `questshift.llm.api-key` away from `none`.

If a token is committed, rotate it on Hugging Face / the cluster and purge it from git history before the next push.

## OpenShift install

Cluster install is two steps. See [INSTALL.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/INSTALL.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/INSTALL.md`).

1. Set up OpenShift **4.20+**.
2. `oc login` as cluster-admin (`oc whoami` must succeed). Keep that cluster’s API URL, token, and CA out of git.
3. From `questshift-gitops`: copy `.env.example` to `.env`, set `QUESTSHIFT_HF_TOKEN`, then `./install.sh` (or `./install.sh --install-operators`).

The script checks cluster-admin, worker/GPU/CPU/memory, then OpenShift GitOps, NFD, NVIDIA GPU Operator, and RHOAI. If there is no NVIDIA GPU it clones a GPU MachineSet unless `--no-add-gpu-nodes`. It deploys QuestShift with an Argo CD Application pointing at `k8s/`. Hugging Face token becomes secret `questshift-hf` on the cluster only.

Quality: `./verify.sh` in `questshift-gitops` (yamllint, ruff, shellcheck, kustomize, pytest-cov). Pre-commit: `./.githooks/install`. Freeze checks: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).

Emergency fallback after operators and the secret exist:

```bash
oc apply -k k8s/
```

Images are placeholders (`image-registry.openshift-image-registry.svc:5000/questshift/...`) until CI publishes. LLM pod requests `nvidia.com/gpu: 1`. Engine ConfigMap sets `questshift.llm.enabled: "true"` and `questshift.llm.base-url: http://questshift-llm:8000/v1`.

Route name `questshift` → UI Service. nginx proxies `/api/` and `/ws/` to the engine.

## Simulated terminal

Never pipe player input into `oc`, `ansible-playbook`, a JDK, or a login node. The evaluator is the only scorer.

## Quality gates

Canonical spec: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).

Each repo has format + static analysis + coverage, a repo-local pre-commit hook (`./.githooks/install`), and GitHub Actions workflow **Quality** on PRs/pushes to `main`. Mark the job required so a red run cannot merge. `SKIP_QUESTSHIFT_HOOKS=1` skips lint/coverage; the secret scan still runs. Full bypass: `git commit --no-verify`. Dependabot files weekly GitHub Actions update PRs (`.github/dependabot.yml`); those PRs still run **Quality**.

| Repo | Format / lint | Static analysis | Coverage | Local command |
| --- | --- | --- | --- | --- |
| engine | Spotless (AOSP) | PMD (priority ≤ 3, 0 allowed) | JaCoCo 80% lines / 70% branches | `./mvnw verify` |
| ui | Prettier | ESLint | Vitest 80% lines / 70% branches | `npm run verify` |
| campaigns | yamllint | ruff | pytest-cov 80% on `tools/` | `./verify.sh` |
| gitops | yamllint + shellcheck | ruff | pytest-cov 80% on probe/helpers | `./verify.sh` |
| docs | ruff format | ruff + spec checker | pytest-cov 80% on `tools/` | `./verify.sh` |

PMD is Java-only. Other repos use the stack analog (ESLint or ruff). Campaign YAML and OpenShift manifests stay puzzle/cluster source of truth; the checkers do not execute player commands or talk to a live cluster.
