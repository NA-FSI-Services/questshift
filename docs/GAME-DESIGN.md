# QuestShift game design (v1)

One campaign, one hour, five rooms. Source of truth for puzzles is campaign YAML, not this prose.

Campaign file:

- GitHub: https://github.com/NA-FSI-Services/questshift-campaigns/blob/main/campaigns/campaign-devops-dungeon.yaml
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns/campaigns/campaign-devops-dungeon.yaml`

## Arc (60 minutes)

Campaign id `devops-dungeon`. Title: **The Cluster That Forgot Its Name**. Premise: the workshop cluster woke unnamed — labels gone, pods looping, playbooks bound to the wrong hosts, a Java resource silent. Restore the name `thorn-ash-oak-iron` or the hour is lost.

| Minute | Beat | Room id | Puzzle | Loot |
| --- | --- | --- | --- | --- |
| 0–4 | Quest lobby: pick the shipped campaign, a cosmetic seat, and a unique alias. Kenney music bed. Then GM leans on a cracked Route. | — | — | — |
| 4–14 | The Broken Shell | `room-01-broken-shell` | `linux` pipeline | `rune-thorn` **THORN** |
| 14–24 | The Playbook of Binding | `room-02-playbook-of-binding` | `ansible` play | `rune-ash` **ASH** |
| 24–36 | The Pod That Would Not Wake | `room-03-pod-that-would-not-wake` | `openshift` probe | `rune-oak` **OAK** |
| 36–46 | The Cursed Servlet | `room-04-cursed-servlet` | `java` snippet | `rune-iron` **IRON** |
| 46–54 | The Operator's Throne | `room-05-operators-throne` | `openshift` annotate | `cluster-name` |
| 54–60 | Debrief + export YAML | — | — | — |

Win: all five `puzzleCompletion` flags true; throne accepted the annotation; the clock **stops**; Panel B shows an adventure recap (most questions, most commands, first accepted command per room); party exports session YAML. Fail: hour ends with the boss unsolved (`expired`, clock capped). Export still works so the next party can resume.

## Cosmetic seats

| Seat id | Title | Color | Traditional vibe |
| --- | --- | --- | --- |
| `guardian` | Guardian | `#3d7a4a` | Linux tinkerer |
| `automancer` | Automancer | `#c45c26` | Ansible hand |
| `ranger` | Cluster Ranger | `#2a6f97` | OpenShift ranger |
| `artificer` | Artificer | `#7b4ea3` | Java artificer |

Anyone may **solve** any room when they hold the Game Master floor (`turnName`). The engine does not gate puzzles by `seatId`. Typing is sequential: only the holder may `POST /api/sessions/{id}/commands`. WebSocket currently stamps seat `shared` and must not bypass the floor. One engine process hosts many parties; players share a `joinCode` (`thorn-golem`) so a second browser can join without YAML import. Start may create `iron-ward` while `throne-ward` is still in memory. Each player picks a cosmetic seat and a **unique alias** (max 8 people) **in the quest lobby** before Start or Join. Same seat may be shared. Suggested aliases, first unused:

| Seat | Suggestions (in order) |
| --- | --- |
| `guardian` | Ada, Briar, Helm, Ward, Oak, Granite, Bastion, Aegis |
| `automancer` | Linus, Ember, Forge, Glyph, Spark, Pipe, Playbook, Ansible |
| `ranger` | Kelsey, Moss, Trail, Vault, Torch, Cluster, Route, Probe |
| `artificer` | James, Cipher, Rune, Shard, Tome, Servlet, Quark, Loom |

Submitted commands for the **current room** appear on a shared board (alias, seat, command, pass/fail) via `session.commandLog`. Each row’s `narrative` is the Game Master reply to that `name`. Ada and Linus can both ask in one room and every browser can tell which reply is which, including after refresh. A room-opening line is a scene beat on `gmLog` (`roomId` + `narrative`, no alias) — Start, and the opening of the next room — and is not stored as the previous passer’s question. `lastNarrative` is only the latest line. YAML still scores; the LLM still narrates only. Other rooms’ attempts and scene beats stay on the session but are not shown until the party is scoring that room. They do not leak onto the overworld dump.

## Respect for turns

The Game Master grants **the floor**. Only one living party member may type a question or command at a time. Seats stay cosmetic: turn order is `partyMembers` join order, not `seatId`. Walking, occupancy, and chest dialogs are **not** gated.

| Beat | Who holds `turnName` |
| --- | --- |
| Start | The first Start alias. Opening GM prose names them. |
| After a scored attempt (pass or fail) | Engine answers that speaker, then **rotates** to the next alias in `partyMembers` (circular). Solo parties keep the floor. |
| Next-room scene beat | Keep the current holder if they are still in the party; otherwise the first remaining member. |
| Join | New alias waits; they are appended and receive the floor on a later rotation. |
| Leave / abandon of the holder | Immediately grant the next remaining member. |
| `complete` / `expired` | Prompt stays disabled; `turnName` is frozen for export. |

The LLM does **not** pick the next speaker and must not rewrite `turnName`. Granite (or YAML fallback) **announces** the grant (“Linus, the floor is yours.”). That announcement is a scene beat (see [questshift#32](https://github.com/NA-FSI-Services/questshift/issues/32) and tracker [questshift#36](https://github.com/NA-FSI-Services/questshift/issues/36)): it names the holder in the prose. `POST /api/sessions/{id}/commands` from anyone else is **409** `not_your_turn`. Presence stays unrestricted.

## Walkable map

Panel A is a walkable Kenney overworld. Each challenge room is a wooden gate (`lobby_gate` for the current room, locked rooms, and resolved rooms). Do not paint a hard-floor snake between rooms. Each player moves their own seat sprite (WASD or arrows while the canvas is focused). `currentRoomId` still gates which puzzle the engine will **score**; walking does not change it. A player may **enter** the current room or any completed room, not a locked future room.

Map dialogs are **layer-scoped**. On the overworld (`viewedRoomId` empty), YAML `story.clues` sit on the floor as chests at overworld coordinates (hour rules, which gate is open, premise fragments — never a winning command). Inside a room, that room’s `clues` sit on the interior floor. A player may open only the layer they are on; a Shell chest is a no-op on the lobby and in The Playbook. Leave through the south lobby door (or enter a different room) closes the open dialog. Opening one shows an emerging dialog **on that player's map only** (IBM Plex Mono). The fragment never lands on Panel B and other browsers do not receive the text. The chest stays on the floor so every player can still open it. Pickup appends the `id` to that member's `foundClues` (session `foundClues` is the union for export) but does not hide the sprite. The Broken Shell chests stay in `room-01-broken-shell` (filesystem tree, the log leaf that contains `rune=THORN`, and a grep/awk man page — never the full winning command). Regex / `accepted_examples` remain the scorer.

Panel B flavor follows the same layer: lobby copy (`story.opening` / premise) on the overworld; that room’s `narrative` while inside. Leaving drops the interior dump. Shared `commandLog` stays filtered to `currentRoomId` (scoring) even if the walker is on the lobby.

Every challenge room has **two interior doors**:

| Door | Sprite | Where | Rule |
| --- | --- | --- | --- |
| Lobby | `door` | South `(450, 470)` | Always open. Esc, click, or E on it returns to the overworld. |
| Challenge | `door_locked` + YAML `guardian`, then `door` | North `(450, 70)` | Locked with that room's **cosmetic** guardian sprite until `puzzleCompletion[roomId]`. Beat it by solving the YAML puzzle in the terminal — not combat. After a pass, the guardian vanishes and the north door shows open (`door`). Click it, or E / Enter on it, to enter the next YAML room (`order + 1`) if that room is unlocked. The south lobby door and overworld gates still work. The throne has no successor. |

Do not put the guardian on the lobby door. The sprite is cosmetic; there is no battle, weapon, or HP. The hour is escape-room role-play. Named keys and coordinates: [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`).

Overworld spawn is 56px south of the current room node (inside the 64px enter radius), so a four-seat party stacks on the same pixel. E or Enter enters a nearby unlocked room, takes an open north challenge door into the next room, or picks a nearby clue **on the current layer**. Esc or the south lobby door returns to the overworld and closes any open map dialog. Keyboard is ignored while the terminal is focused so typing `oc` is not stolen. Panel A plays Kenney CC0 SFX on those map beats (door, threshold step, chest latch, room-complete jingle). A Kenney CC0 music bed loops in the quest lobby (`bgm_lobby`) and quieter during the hour (`bgm_dungeon`), with a mute control; duck under the room-complete jingle. Named keys: [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`). The Game Master stays text; this is not TTS. Do not add WASD footsteps.

### Where is Linus? (Panel A occupancy)

Panel A shows **people**, not only your own sprite. Every party member has a **visible unique alias** next to their Kenney seat sprite. Seat color and sprite are not enough: two Guardians must still read as Ada and Briar. Seats stay cosmetic; drawing is not gated by `seatId`.

| You are | Linus is | Where you look |
| --- | --- | --- |
| Overworld (`viewedRoomId` empty) | Overworld | Walker: Kenney sprite at last presence `mapX` / `mapY`, alias beside it |
| Same interior (`viewedRoomId` matches) | Same interior | Walker: sprite + alias at last interior `mapX` / `mapY` |
| Overworld | Inside The Broken Shell (`viewedRoomId` = that room) | Occupancy on that **doorway** (alias, and a small seat sprite if there is room). You do not enter the room to know Linus is there. |
| Inside a room | Overworld or another interior | Overworld occupancy is N/A until you leave. Only walkers who share your interior are drawn. |

Same-layer members (both overworld, or both in the same `viewedRoomId`) draw at last presence `mapX` / `mapY`. If two would overlap (distance under 24px, including stacked spawn), offset later members in `partyMembers` order by 16px right, wrapping down after four, so two sprites are distinguishable. Do not hide one sprite on top of another.

Presence stays `POST /api/sessions/{id}/presence`. No occupancy REST route. Walking, entering, and clue pickup never change `currentRoomId` and never score a puzzle. Live walks **and scored commands** use the existing `/ws/sessions/{id}` snapshot so every party member sees the shared board; the 1s `GET` remains a fallback. Drawing rules: [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`).

## Game Master voice

Terse fantasy Dungeon Master who also knows ops. Stay in character. Never dump the full `expected_command_pattern` unless the party is stuck (failed attempt + hint). Always one JSON object. Do not invent a `puzzle_type`. Do not rewrite the regex. Sample register: “Sixty minutes. Five rooms. The cluster forgot its name. You will remind it.”

System prompt lives on `game_master.system_prompt` in the campaign YAML.

## Fail / hint loop

1. The player who holds `turnName` submits text (pipeline, playbook, `oc`/`kubectl`, or Java). Anyone else is refused (`not_your_turn`). After the GM answers, the floor rotates (solo keeps it).
2. Evaluator rejects empty input, missing boss loot, or `forbidden_patterns` (example: bare `cat` on the log; `/readyz`; `greeting.toUpperCase`; `/helo`). Authored `miss_beats` fire after a pass miss: a shouted `THORN` is not filesystem evidence; a grep without awk is too long.
3. Pass → success narrative, loot, `canvas_event`, next room (or `status: complete` after the throne). The winning `commandLog` row keeps an addressed `narrative` (the success beat). The GM turn that opens the **next** room is a scene beat on `gmLog` with no alias: do not send the previous winning command (or that room's `accepted_examples`) as if they were an attempt at the new puzzle, and do not store that opening on the passer’s row. Completing the throne freezes `elapsedSeconds` and writes `adventureSummary` from `commandLog`. The throne’s own reply stays on that passer’s row.
4. Fail → `hintCount++`, miss beat from LLM (or YAML `hint` / evaluator message on fallback). The speaker does **not** keep the floor: the GM grants the next alias so the table takes turns. Solo retries immediately. No HP, no permadeath, no lockout. The GM prompt includes the speaker’s alias, the player submission, and the first `accepted_examples` as **private** coaching so Granite can address that player (a “Hello” from Ada should get a Game Master line asking for a command / YAML / `oc` / Java snippet). Do not invent a traveler who was not named. Never dump the winning command unless they asked for a hint after a fail, and do not rewrite `expected_command_pattern`. Authored `miss_beats` still skip the LLM; their `message` is that row’s `narrative`.
5. Soft match exists as a second chance when the regex misses a reasonable alias; still never execute the command.

## Loot runes

Room order is the name of the cluster:

| Order | Rune | Inventory id | How it drops |
| --- | --- | --- | --- |
| 1 | **THORN** | `rune-thorn` | grep/awk the log; shell golem yields |
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

| Room | Guardian (`sprite`) | Player-facing job |
| --- | --- | --- |
| Broken Shell | Shell golem (`guardian_shell`) | Extract the last field on the `rune` line from `/var/log/quest.log`. Chests teach the tree, the log leaf, and grep/awk. The golem rejects a shouted name. |
| Playbook | Bound familiar (`guardian_playbook`) | `hosts: dungeon`, `gather_facts: true`, named `copy`/`template` to `/etc/questshift/name` |
| Pod | Crashing-wizard ghost (`guardian_pod`) | `oc`/`kubectl set probe` HTTP GET `/healthz` on `pod/crashing-wizard` in `dungeon` |
| Servlet | Cursed servlet-slime (`guardian_servlet`) | Repair the Quarkus resource; no null `greeting` |
| Throne | Nameless wraith (`guardian_throne`) | Annotate namespace `dungeon` with the four-rune name |
