# QuestShift API contract (v1)

Matches `questshift-engine` as implemented. Do not invent extra routes unless this file names them.

Engine GitHub: https://github.com/NA-FSI-Services/questshift-engine  
Engine local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-engine`

Base URL local: `http://localhost:8080`. Cluster: nginx proxies `/api/` and `/ws/` to `questshift-engine:8080`. CORS is open in v1 (`quarkus.http.cors.origins=*`).

JSON field names on Java beans are **camelCase** unless noted. Campaign YAML uses **snake_case** for puzzle fields (`puzzle_type`, `expected_command_pattern`). Jackson maps those onto `Campaign.Room`.

## REST

`GameResource` is `@Path("/api")`, JSON in/out unless noted.

### `GET /api/campaigns`

Returns `Collection<Campaign>` currently loaded by `CampaignLibrary`. Each room includes authored `guardian` (`id`, `title`, `sprite`) for the locked north challenge door, plus `clues`. Puzzle fields stay snake_case as in YAML (`puzzle_type`).

### `POST /api/sessions`

Starts one party. Body optional. Many `active` parties may exist in the same engine process; each Start allocates a new unique `joinCode`. There is no 409 `party_active`.

```json
{
  "campaignId": "devops-dungeon",
  "party": [{ "name": "Ada", "seatId": "guardian" }]
}
```

Missing/blank `campaignId` → `questshift.campaigns.default-id` (`devops-dungeon`). `party` is required and must contain **1–8** members. Each member needs a non-blank `name` (alias, unique in the party, case-insensitive) and a cosmetic `seatId` (`guardian` \| `automancer` \| `ranger` \| `artificer`). Same seat may be chosen more than once. There are **no** placeholder members. Response: `GameSession` after the opening GM turn, including `joinCode`. Invalid party → **400** `invalid_party`.

### `GET /api/sessions/{id}`

Live snapshot. `{id}` is the session UUID **or** the human-readable `joinCode` (case-insensitive, e.g. `THORN-GOLEM` → `thorn-golem`). 404 `NotFoundException` if missing. Side effect: `tickElapsed()` while `status` is `active`; if the hour has elapsed, `status` becomes `expired`. `complete` and `expired` skip the tick (clock stays frozen; `complete` also keeps `adventureSummary`). Lookup alone does **not** add a party member.

### `POST /api/sessions/{id}/party`

Adds one player to the live party. `{id}` is the UUID **or** `joinCode`. Body:

```json
{ "name": "Linus", "seatId": "automancer" }
```

Response: `GameSession`. Alias uniqueness is case-insensitive. Same seat as another player is allowed. Cap **8**. Posting an alias that is already in the party is **idempotent** (200, original `seatId` kept — no character/alias change after join). Duplicate *new* alias → **409** `alias_taken`. Ninth player → **409** `party_full`. Session not `active` → **409** `party_not_active`. Blank alias or unknown `seatId` → **400** `invalid_party`.

### `DELETE /api/sessions/{id}/party?name={alias}`

Removes that alias from the party. `{id}` is the UUID **or** `joinCode`. Unknown alias is **idempotent** (200, party unchanged). Blank `name` → **400** `invalid_party`. The hour stays in memory so others can keep playing; this is abandon, not delete. After a successful leave the engine fans the JSON snapshot on `/ws/sessions/{sessionId}`.

### `DELETE /api/sessions/{id}`

Destroys the party for everyone. `{id}` is the UUID **or** `joinCode`. Response **204** with no body. Unknown id → **404**. Drops in-memory state and every WebSocket attached to that hour. Later `GET /api/sessions/{id}` is 404.

### `POST /api/sessions/{id}/presence`

Walk, enter a room, or pick up a YAML clue. `{id}` is the UUID **or** `joinCode`. Body:

```json
{
  "name": "Ada",
  "mapX": 120,
  "mapY": 276,
  "viewedRoomId": "room-01-broken-shell",
  "pickupClueId": "shell-log"
}
```

`name` must already be in `partyMembers`. `viewedRoomId` empty (or omitted) means the overworld. A non-empty id must be the party’s `currentRoomId` or a completed room — locked future rooms are refused. `pickupClueId` is optional; when set, that clue must belong to `viewedRoomId` and is appended to **that member’s** `foundClues` (idempotent). Session `foundClues` is the union of those ids for export. The fragment is not a shared terminal dump — the opener’s UI shows a map dialog, and the chest stays on the floor. Response: `GameSession`. This does **not** change `currentRoomId` or score a puzzle.

Panel A derives walkers and room occupancy from `partyMembers` (`name`, `mapX`, `mapY`, `viewedRoomId`). There is **no** occupancy REST route. After a successful presence update, the engine fans the same JSON snapshot out on the existing WebSocket (see below). Clients that are not subscribed still see the new positions on the next `GET /api/sessions/{id}` (the 1s poll).

Unknown alias, unknown room, locked room, or unknown clue → **400** `invalid_presence`. Session not `active` → **409** `party_not_active`. Blank alias → **400** `invalid_presence`.

### `POST /api/sessions/{id}/commands`

```json
{ "command": "grep -i rune /var/log/quest.log | awk '{print $NF}'", "seatId": "guardian", "name": "Ada" }
```

Response `CommandResult`:

```json
{
  "passed": true,
  "message": "The dungeon accepts the command.",
  "command": "grep -i rune /var/log/quest.log | awk '{print $NF}'",
  "seatId": "guardian",
  "session": { }
}
```

`session` is the updated `GameSession`. `seatId` and optional `name` (alias) are recorded on the result and appended to `session.commandLog` for the **current room**. They do not gate the puzzle. Blank `name` is filled from the first party member with that `seatId`, else `shared`. Clearing the throne sets `status: complete`, freezes `elapsedSeconds`, and writes `adventureSummary`. Session not `active` → **409** `party_not_active`.

### `GET /api/sessions/{id}/export?format=yaml|json`

Default `format=yaml`. Body is serialized `GameSession`. Content-Type `application/yaml` or `application/json`.

### `POST /api/sessions/import?format=yaml|json`

Raw body is YAML or JSON. If `format` is omitted, serializer sniffs `---` / `id:` / `campaignId:` as YAML, else JSON. Restores into the in-memory map (assigns a new `id` if blank; assigns a `joinCode` if blank). An imported `active` snapshot sits beside other live parties. Response: `GameSession`.

There is **no** campaign-reload HTTP route in v1. YAML changes need an engine restart.

## WebSocket

`GameSocket` `@ServerEndpoint("/ws/sessions/{sessionId}")`. `{sessionId}` is the session UUID (clients already have it from REST). Do not invent a second socket path.

| Event | Payload |
| --- | --- |
| On open | JSON snapshot (`export(..., "json")`) |
| Client text frame | Treated as a **command string** (not JSON). Engine calls `submit(sessionId, command, "shared")`. Presence is **not** sent as a socket frame. |
| Server reply after command | JSON snapshot after evaluate, to the sender. Seat on this path is always `"shared"`. Prefer REST commands when you need a real `seatId` and alias. |
| After `POST /api/sessions/{id}/presence` | Same JSON `GameSession` snapshot to **every** open `/ws/sessions/{sessionId}` for that party (walk, enter/leave room, clue pickup). `{id}` on the POST may be UUID or `joinCode`; fan-out is keyed by the `GameSession`. |

Live Panel A walks use this fan-out so other browsers do not wait for the 1s poll. The poll remains a valid fallback when no socket is open (UI occupancy can ship against GET before the engine child lands). Socket payloads are the same `GameSession` JSON, including `partyMembers` (`mapX` / `mapY` / `viewedRoomId` / `foundClues`), `commandLog`, and session `foundClues`.

Do not add a presence opcode, a second WebSocket, or an occupancy REST route.

## Game Master JSON

Produced by `LLMService` (vLLM) or YAML fallback. Shape:

```json
{
  "narrative": "string",
  "puzzle_type": "linux|ansible|openshift|java",
  "expected_command_pattern": "string",
  "hint": "string",
  "canvas_event": "string"
}
```

After parse, Java keeps **room YAML** `expectedCommandPattern`. Fallback sets `canvas_event` to `focus_room` if the model omits it. Room YAML may use richer events (`unlock_room_02` … `unlock_room_05`, `campaign_complete`); those are applied on **pass** from `Campaign.Room.canvasEvent`.

`%dev` and `%test` set `questshift.llm.enabled=false` → always YAML fallback.

## Session YAML / JSON fields

`StateSerializer` writes `GameSession` as-is (JavaTime ISO-8601, no timestamps-as-numbers, YAML without `---`).

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | UUID |
| `joinCode` | string | Two dungeon words, hyphenated, lowercase (`thorn-golem`). Unique in this engine process. Lookup is case-insensitive. |
| `campaignId` | string | `devops-dungeon` |
| `status` | string | `active`, `complete`, or `expired` (hour reached `durationMinutes`) |
| `currentRoomId` | string | e.g. `room-01-broken-shell` |
| `startedAt` | instant | ISO-8601 |
| `elapsedSeconds` | long | wall time since `startedAt` while `status` is `active`. Frozen when `complete` or `expired` (expired caps at `durationMinutes`) |
| `partyMembers` | list | `{ name, seatId, mapX, mapY, viewedRoomId, foundClues }`. Max 8. Aliases unique; seats cosmetic. `viewedRoomId` empty = overworld. Positions are last presence. `foundClues` are YAML clue ids **this alias** opened. Panel A keeps those chests on the floor so every player can still open them; the dialog is only on that client. |
| `foundClues` | string list | Union of member pickups for export. Fragments only; they do not pass the evaluator. |
| `inventory` | string list | loot ids (`rune-thorn`, …) |
| `skills` | string list | flavor (`piping`, …) |
| `puzzleCompletion` | map | room id → boolean |
| `hintCount` | int | miss counter |
| `lastNarrative` | string | last GM prose |
| `lastHint` | string | last hint |
| `lastCanvasEvent` | string | last canvas event |
| `yamlFallback` | boolean | `true` when the last GM turn used campaign YAML because vLLM was disabled, unreachable, or returned HTTP ≥ 300 |
| `commandLog` | list | `{ roomId, name, seatId, command, passed, message }`. Attempts in this hour. Panel B shows the **current scoring room** only. Attribution only; seats do not gate scoring. |
| `adventureSummary` | object or null | Set when `status` is `complete`. `{ mostQuestions, mostQuestionsCount, mostCommands, mostCommandsCount, stages[{ roomId, roomTitle, name }], prose }`. Questions are chatter/misses that are not command-like; commands are ops snippets (and any pass). `stages` is the first passer per room in campaign order. |

Example YAML fragment:

```yaml
id: 11111111-2222-3333-4444-555555555555
joinCode: thorn-golem
campaignId: devops-dungeon
status: active
currentRoomId: room-02-playbook-of-binding
elapsedSeconds: 780
partyMembers:
  - name: Ada
    seatId: guardian
    mapX: 120
    mapY: 276
    viewedRoomId: ""
    foundClues:
      - shell-log
inventory:
  - rune-thorn
skills:
  - piping
puzzleCompletion:
  room-01-broken-shell: true
  room-02-playbook-of-binding: false
hintCount: 1
lastNarrative: The golem cracks.
lastHint: The golem hates cat-only answers.
lastCanvasEvent: unlock_room_02
yamlFallback: true
commandLog:
  - roomId: room-01-broken-shell
    name: Ada
    seatId: guardian
    command: cat /var/log/quest.log
    passed: false
    message: The dungeon rejects the command.
foundClues:
  - shell-log
```

## Errors

Unknown session or unknown join code → 404. Duplicate alias on `POST …/party` → 409 `alias_taken`. Party already has 8 members → 409 `party_full`. Missing Start party, blank alias, or unknown `seatId` → 400 `invalid_party`. Presence with unknown alias, locked room, or unknown clue → 400 `invalid_presence`. Presence or a command while the hour is not `active` → 409 `party_not_active`. Unknown `campaignId` on start → 500 wrapping `IllegalArgumentException("Unknown campaign: …")`. Invalid import body → 500 wrapping `IllegalArgumentException`. Keep these stable; do not add auth in v1.
