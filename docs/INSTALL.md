# Install QuestShift (v1)

Two steps. Local `quarkus:dev` / `npm run dev` is a separate developer loop in [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`).

## 1. Set up an OpenShift 4.20+ cluster

Provide a cluster that can host one party:

- OpenShift Container Platform **4.20 or newer**
- At least **one worker** (two recommended: GPU + general)
- **One free NVIDIA GPU** (`nvidia.com/gpu: 1`, L4 class) after the GPU Operator is Ready
- Free worker capacity at least **2300m CPU** and **~17Gi memory** (vLLM 2 CPU / 16Gi request plus engine and UI)
- A default **StorageClass** (50Gi model cache + 1Gi session export)
- One worker **without** `nvidia.com/gpu=NoSchedule` so engine and UI can schedule
- `cluster-admin` login (`oc login`)

QuestShift still serves Granite with the **vLLM Deployment** in gitops `k8s/`. Red Hat OpenShift AI is a required **operator** on the cluster; it does not replace vLLM.

## 2. Run the installation script

From [questshift-gitops](https://github.com/NA-FSI-Services/questshift-gitops) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-gitops`):

```bash
oc login --server=https://api.CLUSTER:6443
cd questshift-gitops
./install.sh
```

Non-interactive (CI / unattended):

```bash
export QUESTSHIFT_HF_TOKEN=...   # never commit this
./install.sh --install-operators
```

Validate only:

```bash
./install.sh --check-only
```

On this machine you need `oc`, `python3`, and `ansible-playbook` (`ansible-core`). The script is Ansible under the hood; `./install.sh` is the only supported entrypoint.

### What the script does

1. **Admin access** — `oc whoami` and `oc auth can-i '*' '*' --all-namespaces`
2. **Hardware** — OpenShift version, worker count, free CPU/memory/GPU, StorageClass, GPU taints
3. **Operators** — Node Feature Discovery, NVIDIA GPU Operator, OpenShift GitOps, Red Hat OpenShift AI. If any CSV is missing it **asks** whether to install. `--install-operators` skips the question and installs them (NFD instance + GPU `ClusterPolicy` included)
4. **GitOps deploy** — creates namespace `questshift`, secret `questshift-hf` from the token (not from git), applies the Argo CD Application that syncs `k8s/` from this repo

Hugging Face token handling matches [WORKFLOWS.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/WORKFLOWS.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/WORKFLOWS.md`): cluster secret only, never a `Secret` YAML in git. Prefer `QUESTSHIFT_HF_TOKEN` over `--hf-token` so the token is not on the process command line.

Argo CD syncs `k8s/` from **git** (`--repo-url` / `--revision`, default `NA-FSI-Services/questshift-gitops` @ `main`), not from an uncommitted working tree.

Emergency fallback if Argo CD is unavailable: `oc apply -k k8s/` still works after the operators and secret exist. Prefer `./install.sh`.
