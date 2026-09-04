# Claude / Cursor — QuestShift docs repo

Read `AGENTS.md` first.

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/AGENTS.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/AGENTS.md`

Then:

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/docs/ARCHITECTURE-ESSENTIALS.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/ARCHITECTURE-ESSENTIALS.md`

## Hard rules (v1 freeze)

- Name QuestShift. Org NA-FSI-Services. License Apache-2.0.
- Engine: Quarkus 3 + Java 21 (`io.questshift`). UI: Phaser 3 + React + TypeScript.
- LLM: vLLM only, IBM Granite 3.1 8B Instruct, NVIDIA L4 (`nvidia.com/gpu: 1`). No Ollama.
- One party per OpenShift deployment. Seats are cosmetic; any player may solve any puzzle.
- Campaign YAML is puzzle source of truth. LLM narrates only. If vLLM is down, fall back to YAML.
- Terminal is simulated. Never execute player `oc` / Ansible / Linux / Java against the cluster.
- v1 non-goals: TTS, Ollama, multi-party, real command execution, native Quarkus image.
- Specs live under `docs/`. Do not re-litigate product decisions. Do not commit unless asked.
- Never commit secrets to GitHub (HF token, `.env`, kubeconfig, real API keys). Use cluster secret `questshift-hf`.
