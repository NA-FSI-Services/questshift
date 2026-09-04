# Decisions

Recorded from the kickoff workshop. Change these in the GitHub Project, then update this file.

| Decision | Choice |
| --- | --- |
| Public name | QuestShift |
| GitHub org | [NA-FSI-Services](https://github.com/NA-FSI-Services) |
| License | Apache License 2.0 |
| Repo layout | `questshift`, `questshift-engine`, `questshift-ui`, `questshift-campaigns`, `questshift-gitops` |
| Engine | Quarkus 3 + Java 21 |
| UI | Phaser 3 + React + TypeScript |
| LLM serving | vLLM only |
| Default model | IBM Granite 3.1 8B Instruct |
| GPU | NVIDIA L4, `nvidia.com/gpu: 1` |
| Play mode | One party per deployment |
| Seats | Cosmetic avatars; any player may solve any puzzle |
| TTS | Deferred (text-only v1) |
| Native image | Later; JVM first |

## Deliberately not in v1

- Browser Web Speech / Piper TTS
- Ollama local sidecar
- Multi-party / multi-tenant matchmaking
- Real execution of `oc`, Ansible, or a login node
- Native Quarkus binary
