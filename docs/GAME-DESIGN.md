# QuestShift game design (v1)

One campaign, one hour, five rooms. Source of truth for puzzles is campaign YAML, not this prose.

Campaign file:

- GitHub: https://github.com/NA-FSI-Services/questshift-campaigns/blob/main/campaigns/campaign-devops-dungeon.yaml
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns/campaigns/campaign-devops-dungeon.yaml`

## Arc (60 minutes)

Campaign id `devops-dungeon`. Title: **The Cluster That Forgot Its Name**. Premise: the workshop cluster woke unnamed — labels gone, pods looping, playbooks bound to the wrong hosts, a Java resource silent. Restore the name `thorn-ash-oak-iron` or the hour is lost.

| Minute | Beat | Room id | Puzzle | Loot |
| --- | --- | --- | --- | --- |
| 0–4 | Opening. GM leans on a cracked Route. Seats chosen (cosmetic). | — | — | — |
| 4–14 | The Broken Shell | `room-01-broken-shell` | `linux` pipeline | `rune-thorn` **THORN** |
| 14–24 | The Playbook of Binding | `room-02-playbook-of-binding` | `ansible` play | `rune-ash` **ASH** |
| 24–36 | The Pod That Would Not Wake | `room-03-pod-that-would-not-wake` | `openshift` probe | `rune-oak` **OAK** |
| 36–46 | The Cursed Servlet | `room-04-cursed-servlet` | `java` snippet | `rune-iron` **IRON** |
| 46–54 | The Operator's Throne | `room-05-operators-throne` | `openshift` annotate | `cluster-name` |
| 54–60 | Debrief + export YAML | — | — | — |

Win: all five `puzzleCompletion` flags true; throne accepted the annotation; party exports session YAML. Fail: hour ends with the boss unsolved. Export still works so the next party can resume.

## Cosmetic seats

| Seat id | Title | Color | Traditional vibe |
| --- | --- | --- | --- |
| `guardian` | Guardian | `#3d7a4a` | Linux tinkerer |
| `automancer` | Automancer | `#c45c26` | Ansible hand |
| `ranger` | Cluster Ranger | `#2a6f97` | OpenShift ranger |
| `artificer` | Artificer | `#7b4ea3` | Java artificer |

Anyone may submit the solving command for any room. The engine does not gate puzzles by `seatId`. WebSocket currently stamps seat `shared`.

## Game Master voice

Terse fantasy Dungeon Master who also knows ops. Stay in character. Never dump the full `expected_command_pattern` unless the party is stuck (failed attempt + hint). Always one JSON object. Do not invent a `puzzle_type`. Do not rewrite the regex. Sample register: “Sixty minutes. Five rooms. The cluster forgot its name. You will remind it.”

System prompt lives on `game_master.system_prompt` in the campaign YAML.

## Fail / hint loop

1. Player submits text (pipeline, playbook, `oc`/`kubectl`, or Java).
2. Evaluator rejects empty input, missing boss loot, or `forbidden_patterns` (example: bare `cat` on the log; `/readyz`; `greeting.toUpperCase`; `/helo`).
3. Pass → success narrative, loot, `canvas_event`, next room (or `status: complete` after the throne).
4. Fail → `hintCount++`, miss beat from LLM (or YAML `hint` on fallback), party retries. No HP, no permadeath, no lockout.
5. Soft match exists as a second chance when the regex misses a reasonable alias; still never execute the command.

## Loot runes

Room order is the name of the cluster:

| Order | Rune | Inventory id | How it drops |
| --- | --- | --- | --- |
| 1 | **THORN** | `rune-thorn` | grep/awk the log; golem yields |
| 2 | **ASH** | `rune-ash` | Named Ansible task writes `/etc/questshift/name` |
| 3 | **OAK** | `rune-oak` | Liveness probe `/healthz` on `crashing-wizard` |
| 4 | **IRON** | `rune-iron` | GET `/hello` returns `QuestShift lives` |

Boss requires all four ids in inventory, then:

```text
oc annotate namespace dungeon questshift/name=thorn-ash-oak-iron
```

Trophy loot: `cluster-name` (*The Remembered Name*). Skills granted along the way (`piping`, `ansible-bind`, `oc-probe`, `java-rest`, `naming`) are flavor for the GM; they do not unlock rooms.

## Room intents (do not treat as win conditions)

Win conditions are regex + examples in YAML. This table is flavor only.

| Room | Player-facing job |
| --- | --- |
| Broken Shell | Extract the last field on the `rune` line from `/var/log/quest.log` |
| Playbook | `hosts: dungeon`, `gather_facts: true`, named `copy`/`template` to `/etc/questshift/name` |
| Pod | `oc`/`kubectl set probe` HTTP GET `/healthz` on `pod/crashing-wizard` in `dungeon` |
| Servlet | Repair the Quarkus resource; no null `greeting` |
| Throne | Annotate namespace `dungeon` with the four-rune name |
