# Install QuestShift (v1)

Two steps. Local `quarkus:dev` / `npm run dev` is a separate developer loop in [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).

Workshop clusters are ephemeral. Every install uses a different API URL, token, and CA. Keep those in a local `oc` session and a gitignored `.env`. Never commit them.

## 1. Set up an OpenShift 4.20+ cluster

Provide a cluster that can host one party:

- OpenShift Container Platform **4.20 or newer**
- At least **one worker** (two recommended: GPU + general). If the cluster has no NVIDIA GPU, `./install.sh` clones a GPU MachineSet (`g6.4xlarge` / L4) unless you pass `--no-add-gpu-nodes`.
- **One free NVIDIA GPU** (`nvidia.com/gpu: 1`, L4 class) after the GPU Operator is Ready
- Free worker capacity at least **2300m CPU** and **~17Gi memory** (vLLM 2 CPU / 16Gi request plus engine and UI)
- A default **StorageClass** (50Gi model cache + 1Gi session export)
- One worker **without** `nvidia.com/gpu=NoSchedule` so engine and UI can schedule
- `cluster-admin` login (`oc login`)

QuestShift still serves Granite with the **vLLM Deployment** in gitops `k8s/`. Red Hat OpenShift AI is a required **operator** on the cluster; it does not replace vLLM.

## 2. Log in as cluster-admin

The installer does **not** take `--server`, `--token`, or other cluster credentials. It uses the current `oc` context and refuses to run if `oc whoami` fails.

```bash
oc login --server=https://api.CLUSTER:6443
oc whoami
```

Optional: point `oc` at a local kubeconfig via `KUBECONFIG` in a gitignored `.env` (copy `questshift-gitops/.env.example`). Do not put the API URL, token, or CA certificate in git.

## 3. Run the installation script

From [questshift-gitops](https://github.com/NA-FSI-Services/questshift-gitops) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-gitops`):

```bash
# oc whoami must already succeed
./install.sh
```

Non-interactive (CI / unattended, still requires an existing `oc` login):

```bash
./install.sh --install-operators
```

Skip cloning a GPU MachineSet (you already have an L4 worker, or you will add one yourself):

```bash
./install.sh --install-operators --no-add-gpu-nodes
```

Validate only:

```bash
./install.sh --check-only
```

On this machine you need `oc`, `python3`, and `ansible-playbook` (`ansible-core`). The script is Ansible under the hood; `./install.sh` is the only supported entrypoint.

### What the script does

1. **Login** — `oc whoami` must succeed, then `oc auth can-i '*' '*' --all-namespaces`
2. **Hardware** — OpenShift version, worker count, free CPU/memory/GPU, StorageClass, GPU taints
3. **Operators** — Node Feature Discovery, NVIDIA GPU Operator, OpenShift GitOps, Red Hat OpenShift AI, OpenShift Pipelines. If any CSV is missing it **asks** whether to install. `--install-operators` skips the question and installs them (NFD instance + GPU `ClusterPolicy` included)
4. **GPU node** — if NFD sees no NVIDIA GPU, clone a GPU MachineSet (`g6.4xlarge`, L4) from the first MachineSet in `openshift-machine-api`, taint it `nvidia.com/gpu=present:NoSchedule`, and wait until `nvidia.com/gpu` is allocatable. Pass `--no-add-gpu-nodes` to skip. The rendered MachineSet stays in `install/.work/` (gitignored).
5. **GitOps deploy** — creates namespace `questshift`, labels it for OpenShift GitOps, applies the Argo CD Application that syncs `k8s/` from this repo. A Tekton `PipelineRun` copies Granite weights from the ModelCar catalog onto PVC `questshift-llm-cache` (no Hugging Face token, no MinIO). vLLM starts after that run succeeds.
6. **UI URL** — prints `https://<route>` so facilitators can open the UI and start a campaign. If the Route is not ready yet, it tells you to run `oc get route questshift -n questshift`.

Argo CD syncs `k8s/` from **git** (`--repo-url` / `--revision`, default `NA-FSI-Services/questshift-gitops` @ `main`), not from an uncommitted working tree.

Emergency fallback if Argo CD is unavailable: `oc apply -k k8s/` still works after the operators exist. Prefer `./install.sh`.

Manifest freeze (no `Secret` YAML, no Ollama, GPU request `1`) is checked by `./verify.sh` in `questshift-gitops`. That gate does not log into a cluster; `--check-only` is the live probe. Details: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).
