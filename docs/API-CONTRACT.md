# QuestShift API contract (v1)

Matches `questshift-engine` as implemented. Do not invent extra routes unless this file names them.

Engine GitHub: https://github.com/NA-FSI-Services/questshift-engine  
Engine local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-engine`

Base URL local: `http://localhost:8080`. Cluster: nginx proxies `/api/` and `/ws/` to `questshift-engine:8080`. CORS is open in v1 (`quarkus.http.cors.origins=*`).

JSON field names on Java beans are **camelCase** unless noted. Campaign YAML uses **snake_case** for puzzle fields (`puzzle_type`, `expected_command_pattern`). Jackson maps those onto `Campaign.Room`.

## REST

`GameResource` is `@Path("/api")`, JSON in/out unless noted.

### `GET /api/campaigns`

Returns `Collection<Campaign>` currently loaded by `CampaignLibrary`.

### `POST /api/sessions`

Starts one party. Body optional. At most one `active` party exists per engine process. If a live party is already `active` (and the campaign hour has not expired), the engine returns **409** instead of creating a second hour:

```json
{
  "error": "party_active",
  "message": "A party is already running. Join with thorn-golem.",
  "joinCode": "thorn-golem"
}
```

A new Start succeeds when there is no `active` party: empty engine, `status` `complete` or `expired`, or elapsed time has reached the campaign `durationMinutes`.

```json
{
  "campaignId": "devops-dungeon",
  "party": [{ "name": "Ada", "seatId": "guardian" }]
}
```

Missing/blank `campaignId` → `questshift.campaigns.default-id` (`devops-dungeon`). `party` is required and must contain **1–8** members. Each member needs a non-blank `name` (alias, unique in the party, case-insensitive) and a cosmetic `seatId` (`guardian` \| `automancer` \| `ranger` \| `artificer`). Same seat may be chosen more than once. There are **no** placeholder members. Response: `GameSession` after the opening GM turn, including `joinCode`. Invalid party → **400** `invalid_party`.

### `GET /api/sessions/{id}`

Live snapshot. `{id}` is the session UUID **or** the human-readable `joinCode` (case-insensitive, e.g. `THORN-GOLEM` → `thorn-golem`). 404 `NotFoundException` if missing. Side effect: `tickElapsed()`; if the hour has elapsed, `status` becomes `expired`. Lookup alone does **not** add a party member.

### `POST /api/sessions/{id}/party`

Adds one player to the live party. `{id}` is the UUID **or** `joinCode`. Body:

```json
{ "name": "Linus", "seatId": "automancer" }
```

Response: `GameSession`. Alias uniqueness is case-insensitive. Same seat as another player is allowed. Cap **8**. Posting an alias that is already in the party is **idempotent** (200, original `seatId` kept — no character/alias change after join). Duplicate *new* alias → **409** `alias_taken`. Ninth player → **409** `party_full`. Session not `active` → **409** `party_not_active`. Blank alias or unknown `seatId` → **400** `invalid_party`.

### `POST /api/sessions/{id}/commands`

```json
{ "command": "grep -i rune /var/log/quest.log | awk '{print $NF}'", "seatId": "guardian" }
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

`session` is the updated `GameSession`. `seatId` is recorded on the result only; it does not gate the puzzle.

### `GET /api/sessions/{id}/export?format=yaml|json`

Default `format=yaml`. Body is serialized `GameSession`. Content-Type `application/yaml` or `application/json`.

### `POST /api/sessions/import?format=yaml|json`

Raw body is YAML or JSON. If `format` is omitted, serializer sniffs `---` / `id:` / `campaignId:` as YAML, else JSON. Restores into the in-memory map (assigns a new `id` if blank; assigns a `joinCode` if blank). If the imported snapshot would be `active` while another party is already `active`, **409** `party_active` (same body as Start). Response: `GameSession`.

There is **no** campaign-reload HTTP route in v1. YAML changes need an engine restart.

## WebSocket

`GameSocket` `@ServerEndpoint("/ws/sessions/{sessionId}")`.

| Event | Payload |
| --- | --- |
| On open | JSON snapshot (`export(..., "json")`) |
| Client text frame | Treated as a **command string** (not JSON). Engine calls `submit(sessionId, command, "shared")` |
| Server reply | JSON snapshot after evaluate |

Seat on the socket path is always `"shared"`. Prefer REST commands when you need a real `seatId`.

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
| `elapsedSeconds` | long | recomputed on tick/export |
| `partyMembers` | list | `{ name, seatId }`. Max 8. Aliases unique; seats cosmetic. |
| `inventory` | string list | loot ids (`rune-thorn`, …) |
| `skills` | string list | flavor (`piping`, …) |
| `puzzleCompletion` | map | room id → boolean |
| `hintCount` | int | miss counter |
| `lastNarrative` | string | last GM prose |
| `lastHint` | string | last hint |
| `lastCanvasEvent` | string | last canvas event |
| `yamlFallback` | boolean | `true` when the last GM turn used campaign YAML because vLLM was disabled, unreachable, or returned HTTP ≥ 300 |

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
```

## Errors

Unknown session or unknown join code → 404. Second Start (or an `active` import) while a party is `active` → 409 `party_active` with `joinCode`. Duplicate alias on `POST …/party` → 409 `alias_taken`. Party already has 8 members → 409 `party_full`. Missing Start party, blank alias, or unknown `seatId` → 400 `invalid_party`. Unknown `campaignId` on start → 500 wrapping `IllegalArgumentException("Unknown campaign: …")`. Invalid import body → 500 wrapping `IllegalArgumentException`. Keep these stable; do not add auth in v1.
