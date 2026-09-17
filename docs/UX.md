# QuestShift UX (v1)

Dual-panel 16-bit dungeon. Canvas is pixel art; the terminal stays readable.

## Layout

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ QuestShift  The Cluster That Forgot Its Name  [start] [join thorn-golem] │
│             [YAML fallback — Game Master unreachable]                    │
├────────────────────────────────────────────┬─────────────────────────────┤
│ Panel A — Phaser canvas                    │ Panel B — terminal          │
│ 16-bit rooms, four seats, gems             │ IBM Plex Mono, CRT wash     │
│ loot strip under the board                 │ GM log / $ prompt / hint    │
│ (HTML + Phaser loot_* sprites)             │                             │
└────────────────────────────────────────────┴─────────────────────────────┘
```

Empty topbar: four **character** buttons, an **alias** field (suggested from the selected seat, skipping names already in a looked-up party), **start 60-minute run**, plus **Join code** / **Join**. Panel A/B stay visible — not a lobby screen. After Start, those party actions collapse into a **Party {joinCode}** dropdown: **Copy code**, **Switch party** (type another code such as `iron-ward`), **new party**, **Abandon party**, and **Delete party** (danger zone: type the join code). Session restore only reapplies an `active` stored party. Character and alias stay yours until you switch or abandon.

- **Panel A:** `src/game/DungeonScene.ts` in `questshift-ui`. Phaser 3 scene `dungeon`. Fill the canvas with `floor` / `wall` tiles, then place rooms at campaign `mapX` / `mapY`. Seat sprites **walk** (WASD / arrows while the canvas is focused). `focus` marks the current scoring room. E / Enter enters a nearby unlocked room or opens a nearby `clue` chest (clicking the room, chest, or south lobby door also works); Esc or the south lobby door leaves the interior. Door, room, chest, and quest SFX use named Kenney CC0 keys (below). Opening a chest shows an emerging IBM Plex Mono dialog on **that** canvas only — teammates do not see the text on Panel B — and the chest stays on the floor so they can still open it. Every challenge room has **two interior doors**: a south `door` always open back to the lobby, and a north challenge door (`door_locked` plus that room’s YAML `guardian` until the puzzle is solved; `door` after). Draw `loot_*` sprites on the canvas as inventory runes appear; keep the HTML inventory line under the board. Every party member (including you) shows a unique **alias** next to their Kenney seat sprite. Same-layer walkers draw at last presence `mapX` / `mapY`; overlapping sprites offset. Overworld occupancy marks who is inside each named room. Movement math lives in `src/map.ts` (Vitest); occupancy / label / offset / private-clue helpers follow the same pattern. Phaser `src/game/**` stays coverage-excluded.
- **Panel B:** `src/terminal/TerminalPanel.tsx`. Still the command surface. CRT-like background (`#07110c`) and scanline wash in CSS; **typeface is IBM Plex Mono**, not a 8×8 font. Players must read YAML, `oc`, and Java. When a player is inside a room, the log shows that room’s authored `narrative`. Chest fragments stay on the map dialog. The GM log is followed by the **shared room board**: each attempt in the current scoring room shows alias, seat, command, and accepted/failed. Other rooms’ attempts stay on the session but are hidden until the party is scoring that room. The 1s `GET` poll is a fallback; live walks use the existing `/ws/sessions/{id}` `GameSession` snapshot. Both carry `commandLog`, `foundClues`, `partyMembers` positions, and per-member `foundClues`.

On viewports under 960px, stack Panel A above Panel B.

## Palette and motion

CSS tokens in `src/index.css`:

| Token | Hex | Use |
| --- | --- | --- |
| `--bg` | `#070a09` | Page |
| `--panel` | `#101714` | Canvas well |
| `--ink` | `#d7eadb` | Body |
| `--muted` | `#7f9a86` | Secondary |
| `--accent` | `#8fe0a4` | Title, GM text |
| `--amber` | `#e0b25a` | Clock, loot, prompt |
| `--term` | `#07110c` | Terminal chrome |
| `--fail` | `#d96a4a` | Error banner |

Seat colors from campaign YAML (cosmetic): Guardian `#3d7a4a`, Automancer `#c45c26`, Cluster Ranger `#2a6f97`, Artificer `#7b4ea3`.

Motion: nearest-neighbor scale on sprites (`pixelArt: true`). Display tiles at **3×** (48px). Current room pulses 1.0 → 1.15. Completed rooms swap to `gem_complete`. After a miss, the current room shows `gem_hint` until the next pass or room change. No screen shake, no particle spam. Canvas events (`unlock_room_02` … `campaign_complete`, `focus_room`) drive gem and focus updates and the `quest_complete` SFX — do not paint the event name as debug text on the canvas.

Title face `UnifrakturMaguntia` is header-only. Body and terminal stay IBM Plex Mono.

## Sprite sheet (Kenney Tiny Dungeon)

Vendored CC0 1.0 sheet. Do not replace with AI-generated images.

| File | Path |
| --- | --- |
| Packed sheet | `questshift-ui/public/assets/kenney/tiny-dungeon/tilemap_packed.png` |
| Grid notes | `questshift-ui/public/assets/kenney/tiny-dungeon/Tilesheet.txt` |
| Kenney license | `questshift-ui/public/assets/kenney/tiny-dungeon/LICENSE.txt` |
| NOTICE | `questshift-ui/public/assets/NOTICE` |
| SFX clips | `questshift-ui/public/assets/kenney/sfx/` |
| SFX license | `questshift-ui/public/assets/kenney/sfx/LICENSE.txt` |

GitHub tree: https://github.com/NA-FSI-Services/questshift-ui/tree/main/public/assets  
Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-ui/public/assets/`

Source: [Kenney Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon) by Kenney.nl. Sheet is **192×176**, **16×16 frames**, **12 columns × 11 rows**, **no spacing** (packed). Kenney’s `Tilesheet.txt` describes a 1px-gapped sheet; the vendored file is the packed PNG (confirmed 192×176), so Phaser `spacing` is **0**. Phaser:

```ts
this.load.spritesheet("tiny-dungeon", "/assets/kenney/tiny-dungeon/tilemap_packed.png", {
  frameWidth: 16,
  frameHeight: 16,
  spacing: 0,
});
```

Frame index equals Kenney `tile_NNNN` number. Phaser must use the **Canvas** renderer (`type: Phaser.CANVAS`): the packed PNG is 8-bit colormap and WebGL uploads it as a blank texture.

## Sprite keys

Load atlas key `tiny-dungeon`. Named keys below are what `DungeonScene` must use.

### Rooms (five dungeon nodes)

| Phaser key | Frame | Kenney tile | Room |
| --- | --- | --- | --- |
| `room_01_broken_shell` | 29 | `tile_0029` | The Broken Shell (wall rune) |
| `room_02_playbook` | 56 | `tile_0056` | The Playbook of Binding (tome) |
| `room_03_pod` | 80 | `tile_0080` | The Pod That Would Not Wake (ladder/tracks) |
| `room_04_servlet` | 54 | `tile_0054` | The Cursed Servlet (workbench) |
| `room_05_throne` | 72 | `tile_0072` | The Operator's Throne (chair) |
| `floor` | 48 | `tile_0048` | Sand floor fill |
| `wall` | 28 | `tile_0028` | Stone brick |
| `focus` | 60 | `tile_0060` | Current-room reticle |

### Seats (cosmetic avatars)

| Phaser key | Frame | Kenney tile | Seat id |
| --- | --- | --- | --- |
| `seat_automancer` | 84 | `tile_0084` | `automancer` — purple wizard |
| `seat_artificer` | 86 | `tile_0086` | `artificer` — brown apron |
| `seat_ranger` | 87 | `tile_0087` | `ranger` — Cluster Ranger |
| `seat_guardian` | 96 | `tile_0096` | `guardian` — helmed knight |

### Clues and interior

| Phaser key | Frame | Kenney tile | Use |
| --- | --- | --- | --- |
| `clue` | 89 | `tile_0089` | YAML clue chest; stays on the floor after open |
| `door` | 52 | `tile_0052` | Open interior door: south lobby exit (always), and north challenge door after the room is solved |
| `door_locked` | 6 | `tile_0006` | North challenge door while the room is unsolved |
| `guardian_shell` | 97 | `tile_0097` | Broken Shell golem; bars the north door until that puzzle is solved |
| `guardian_playbook` | 98 | `tile_0098` | Playbook of Binding familiar |
| `guardian_pod` | 100 | `tile_0100` | Pod That Would Not Wake ghost |
| `guardian_servlet` | 108 | `tile_0108` | Cursed Servlet slime |
| `guardian_throne` | 121 | `tile_0121` | Operator's Throne wraith |

The interior room title is IBM Plex Mono `--amber` (`#e0b25a`) on a `--bg` (`#070a09`) well so it reads on `wall` tiles. Interior spawn is `(450, 360)`. The **south lobby door** is `(450, 470)` and is always open; Esc, E while standing on it, or clicking it returns to the overworld. The **north challenge door** is `(450, 70)`. While `puzzleCompletion[roomId]` is false, draw `door_locked` there and the room’s YAML `guardian` sprite at `(450, 118)`. Beating the guardian is solving the YAML puzzle in the terminal (regex / `accepted_examples`) — not a combat system. After a pass, the guardian vanishes and the north door uses `door` (open, cosmetic; the next scoring room is still reached from the lobby). Overworld spawn is the current room node, 56px south (inside the 64px enter radius). Because that spawn stacks, Panel A must offset overlapping sprites.

Chest pickup opens a local dialog on the canvas (label + `text`, IBM Plex Mono). Esc / E / click the well closes it. The chest **stays on the floor** so every player can still click it; the dialog is still private to the opener. `partyMembers[].foundClues` records who opened what for export. It does not hide sprites. Opening plays `chest_open`.

### Status gems and loot

| Phaser key | Frame | Kenney tile | Use |
| --- | --- | --- | --- |
| `gem_locked` | 113 | `tile_0113` | Room not yet open (pale vial) |
| `gem_current` | 115 | `tile_0115` | Active room (red vial) |
| `gem_complete` | 114 | `tile_0114` | Solved room (green vial) |
| `gem_hint` | 116 | `tile_0116` | Current room after a miss (`passed=false`); clear on pass or room change |
| `loot_thorn` | 29 | `tile_0029` | Rune THORN — draw when `rune-thorn` is in inventory |
| `loot_ash` | 113 | `tile_0113` | Rune ASH — draw when `rune-ash` is in inventory |
| `loot_oak` | 114 | `tile_0114` | Rune OAK — draw when `rune-oak` is in inventory |
| `loot_iron` | 116 | `tile_0116` | Rune IRON — draw when `rune-iron` is in inventory |

## Sound effects (Kenney CC0)

Short map cues only. Game Master copy stays text; no TTS, mic, or Web Speech. Phaser loads OGG then WAV so Safari can play the same clip. Audio unlocks on the first canvas click or key (browser autoplay). Missing files fail open — the board still works. Named keys below are what `DungeonScene` must use (`src/sounds.ts`).

| Phaser key | Event | Pack | Kenney file | What you hear |
| --- | --- | --- | --- | --- |
| `sfx_door_open` | Opening a door (enter from the overworld, or leave through the south lobby door) | [RPG Audio](https://kenney.nl/assets/rpg-audio) | `doorOpen_1.ogg` | Heavy wooden dungeon door swinging on iron fittings, latch scrape, ~0.9s |
| `sfx_room_enter` | Entering a room (280ms after the door) | [RPG Audio](https://kenney.nl/assets/rpg-audio) | `footstep00.ogg` | One boot on stone as you cross the threshold, ~0.25s |
| `sfx_quest_complete` | Completing a room (`puzzleCompletion` flips true) | [Music Jingles](https://kenney.nl/assets/music-jingles) | `jingles_NES03.ogg` | Short 8-bit rising victory arpeggio, ~0.6s |
| `sfx_chest_open` | Opening a YAML clue chest | [RPG Audio](https://kenney.nl/assets/rpg-audio) | `metalLatch.ogg` | Metal hasp click on a wooden chest, ~0.26s |

Vendored copies (renamed): `questshift-ui/public/assets/kenney/sfx/{door_open,room_enter,quest_complete,chest_open}.{ogg,wav}`. GitHub tree: https://github.com/NA-FSI-Services/questshift-ui/tree/main/public/assets/kenney/sfx  
Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-ui/public/assets/kenney/sfx/`

Door and chest cues are **local** (your sprite). Quest complete is **party-wide** (every client hears it when the shared `puzzleCompletion` map gains a room). Session restore primes already-complete rooms so it does not replay five jingles. Do not add music beds, footsteps on WASD, or spoken GM lines.

## Party occupancy on Panel A

Panel A answers “where is Linus?” without a second REST route. Read `session.partyMembers` (`name`, `seatId`, `mapX`, `mapY`, `viewedRoomId`). Empty `viewedRoomId` is the overworld. Do not gate drawing by cosmetic `seatId`.

**Alias labels.** Every member on the current layer (you included) has a unique alias next to their `seat_*` sprite. Use IBM Plex Mono in `--ink` (`#d7eadb`) with a dark stroke or well so the name reads on `floor` tiles. Do not use UnifrakturMaguntia on the board. Color and Kenney sprite are not enough: two Guardians with no names look like one avatar.

**Same layer (walkers).** Draw a member as a walker when their `viewedRoomId` matches yours (both empty, or both the same room id) at last presence `mapX` / `mapY`. If two walkers are within 24px, offset later members in `partyMembers` order by 16px on X, wrapping to +16px Y after four, so stacked spawn still shows two sprites. Extract occupancy / label / offset helpers to Vitest (same pattern as `src/map.ts`); Phaser `src/game/**` stays coverage-excluded.

**Overworld occupancy.** While you are on the overworld, members whose `viewedRoomId` is a room id do **not** vanish. Mark that room icon: cluster their aliases (and a small `seat_*` sprite if space) north of the room so the 64px enter radius stays clickable. Example: Linus entered The Broken Shell → occupancy on `room_01_broken_shell`, not a walker on the sand. You do not enter the room to know they exist. If more than three occupants, stack aliases; do not omit a name.

**Interior view.** While you are inside a room, draw only walkers who share that `viewedRoomId`. Overworld occupancy is N/A until you leave (Esc or the south lobby door). Teammates in a different room or on the overworld are not drawn on the interior.

**Live vs poll.** Subscribe to `/ws/sessions/{id}` for `GameSession` snapshots so walks move without waiting. The 1s `GET /api/sessions/{id}` remains a valid fallback (and is enough for the UI child before engine fan-out). Presence stays `POST /api/sessions/{id}/presence`. No occupancy endpoint.

Where-is-Linus table: [GAME-DESIGN.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/GAME-DESIGN.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/GAME-DESIGN.md`). Snapshot fan-out: [API-CONTRACT.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/API-CONTRACT.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/API-CONTRACT.md`).

## Terminal (Panel B)

Keep the simulated CRT: dark green well, amber prompt `$`, `GM>` prefix on narrative. Clock shows `elapsedSeconds` and the UI polls `GET /api/sessions/{id}` once a second while a run is live. When `status` is `complete` (or `expired`), freeze the clock and suffix **stopped**. After the throne is cleared, Panel B shows an adventure recap from `adventureSummary.prose`: who asked the most questions, who tried the most commands, and who sent the first accepted command for each room. The prompt disables. Footer: `export.yaml`, `import.yaml` (file picker; restores via `POST /api/sessions/import`), plus last hint. Textarea accepts multiline (Shift+Enter); Enter submits. Placeholder: “type a command, YAML, oc, or Java snippet…”. Do not add a mic button.

When `session.yamlFallback` is true (vLLM down, `%dev`, or HTTP ≥ 300), show **YAML fallback — Game Master unreachable** in `--fail` (`#d96a4a`) on the top bar (`role="status"`) and again next to the clock. Hide it when the engine narrates through vLLM. Text plus color; do not rely on the chip color alone. The hour still runs on authored YAML.

## Accessibility

- `aria-label="Game canvas"` on Panel A; canvas `tabindex="0"` so WASD is not captured while the terminal is focused. `aria-live="polite"` on the GM log.
- Command field has a visible label (sr-only is acceptable).
- Seat list in HTML under the canvas so color is not the only cue (`<i>` swatch + title). Canvas alias labels are the sprite cue: two players who share a seat still read as different people.
- Contrast: IBM Plex Mono on `#07110c` meets readable ops output; do not drop font size below 14px in the log.
- SFX are extra confirmation of gems, interiors, and chest dialogs. The hour is playable muted; browsers stay silent until the canvas is clicked or a walk key is pressed.
