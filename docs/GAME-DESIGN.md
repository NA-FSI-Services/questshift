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

Anyone may submit the solving command for any room. The engine does not gate puzzles by `seatId`. WebSocket currently stamps seat `shared`. One engine process is one party; players share a `joinCode` (`thorn-golem`) so a second browser can join without YAML import. Each player picks a cosmetic seat and a **unique alias** (max 8 people). Same seat may be shared. Suggested aliases, first unused:

| Seat | Suggestions (in order) |
| --- | --- |
| `guardian` | Ada, Briar, Helm, Ward, Oak, Granite, Bastion, Aegis |
| `automancer` | Linus, Ember, Forge, Glyph, Spark, Pipe, Playbook, Ansible |
| `ranger` | Kelsey, Moss, Trail, Vault, Torch, Cluster, Route, Probe |
| `artificer` | James, Cipher, Rune, Shard, Tome, Servlet, Quark, Loom |

Submitted commands for the **current room** appear on a shared board (alias, seat, command, pass/fail) via `session.commandLog`. YAML still scores; the LLM still narrates only. Other rooms’ attempts stay on the session but are not shown until the party is in that room.

## Walkable map

Panel A is a walkable Kenney overworld. Each player moves their own seat sprite (WASD or arrows while the canvas is focused). `currentRoomId` still gates which puzzle the engine will **score**; walking does not change it. A player may **enter** the current room or any completed room, not a locked future room.

Inside a room, YAML `clues` sit on the floor. Picking one appends its `id` to party-shared `foundClues` and shows the fragment on Panel B. Clues are authored snippets (`grep -i rune`, `hosts: dungeon`), never the full winning command. Regex / `accepted_examples` remain the scorer.

Overworld spawn is 56px south of the current room node (inside the 64px enter radius), so a four-seat party stacks on the same pixel. E or Enter enters a nearby unlocked room or picks a nearby clue. Esc or the south door returns to the overworld. Keyboard is ignored while the terminal is focused so typing `oc` is not stolen.

### Where is Linus? (Panel A occupancy)

Panel A shows **people**, not only your own sprite. Every party member has a **visible unique alias** next to their Kenney seat sprite. Seat color and sprite are not enough: two Guardians must still read as Ada and Briar. Seats stay cosmetic; drawing is not gated by `seatId`.

| You are | Linus is | Where you look |
| --- | --- | --- |
| Overworld (`viewedRoomId` empty) | Overworld | Walker: Kenney sprite at last presence `mapX` / `mapY`, alias beside it |
| Same interior (`viewedRoomId` matches) | Same interior | Walker: sprite + alias at last interior `mapX` / `mapY` |
| Overworld | Inside The Broken Shell (`viewedRoomId` = that room) | Occupancy on that **room icon** (alias, and a small seat sprite if there is room). You do not enter the room to know Linus is there. |
| Inside a room | Overworld or another interior | Overworld occupancy is N/A until you leave. Only walkers who share your interior are drawn. |

Same-layer members (both overworld, or both in the same `viewedRoomId`) draw at last presence `mapX` / `mapY`. If two would overlap (distance under 24px, including stacked spawn), offset later members in `partyMembers` order by 16px right, wrapping down after four, so two sprites are distinguishable. Do not hide one sprite on top of another.

Presence stays `POST /api/sessions/{id}/presence`. No occupancy REST route. Walking, entering, and clue pickup never change `currentRoomId` and never score a puzzle. Live walks use the existing `/ws/sessions/{id}` snapshot; the 1s `GET` remains a fallback. Drawing rules: [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`).

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
