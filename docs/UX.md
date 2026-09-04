# QuestShift UX (v1)

Dual-panel 16-bit dungeon. Canvas is pixel art; the terminal stays readable.

## Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ QuestShift   The Cluster That Forgot Its Name    [start run] │
├───────────────────────────────────┬──────────────────────────┤
│ Panel A — Phaser canvas           │ Panel B — terminal       │
│ 16-bit rooms, four seats, gems    │ IBM Plex Mono, CRT wash  │
│ loot strip under the board        │ GM log / $ prompt / hint │
└───────────────────────────────────┴──────────────────────────┘
```

- **Panel A:** `src/game/DungeonScene.ts` in `questshift-ui`. Phaser 3 scene `dungeon`. Rooms from campaign `mapX` / `mapY`. Seats as sprites, not colored dots, once the sheet is wired (PLAN phase 2).
- **Panel B:** `src/terminal/TerminalPanel.tsx`. Still the command surface. CRT-like background (`#07110c`) and scanline wash in CSS; **typeface is IBM Plex Mono**, not a 8×8 font. Players must read YAML, `oc`, and Java.

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

Motion: nearest-neighbor scale on sprites (`pixelArt: true` when wiring Phaser). Current room pulses scale 1.0 → 1.15. Completed rooms swap to `gem_complete`. No screen shake, no particle spam. Canvas events (`unlock_room_02` … `campaign_complete`, `focus_room`) drive gem and path updates only.

Title face `UnifrakturMaguntia` is header-only. Body and terminal stay IBM Plex Mono.

## Sprite sheet (Kenney Tiny Dungeon)

Vendored CC0 1.0 sheet. Do not replace with AI-generated images.

| File | Path |
| --- | --- |
| Packed sheet | `questshift-ui/public/assets/kenney/tiny-dungeon/tilemap_packed.png` |
| Grid notes | `questshift-ui/public/assets/kenney/tiny-dungeon/Tilesheet.txt` |
| Kenney license | `questshift-ui/public/assets/kenney/tiny-dungeon/LICENSE.txt` |
| NOTICE | `questshift-ui/public/assets/NOTICE` |

GitHub tree: https://github.com/NA-FSI-Services/questshift-ui/tree/main/public/assets  
Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-ui/public/assets/`

Source: [Kenney Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon) by Kenney.nl. Sheet is **192×176**, **16×16 frames**, **12 columns × 11 rows**, **no spacing** (packed). Phaser:

```ts
this.load.spritesheet("tiny-dungeon", "/assets/kenney/tiny-dungeon/tilemap_packed.png", {
  frameWidth: 16,
  frameHeight: 16,
  spacing: 0,
});
```

Frame index equals Kenney `tile_NNNN` number.

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

### Status gems and loot

| Phaser key | Frame | Kenney tile | Use |
| --- | --- | --- | --- |
| `gem_locked` | 113 | `tile_0113` | Room not yet open (pale vial) |
| `gem_current` | 115 | `tile_0115` | Active room (red vial) |
| `gem_complete` | 114 | `tile_0114` | Solved room (green vial) |
| `gem_hint` | 116 | `tile_0116` | Miss / hint available (blue vial) |
| `loot_thorn` | 29 | `tile_0029` | Rune THORN |
| `loot_ash` | 113 | `tile_0113` | Rune ASH |
| `loot_oak` | 114 | `tile_0114` | Rune OAK |
| `loot_iron` | 116 | `tile_0116` | Rune IRON |

## Terminal (Panel B)

Keep the simulated CRT: dark green well, amber prompt `$`, `GM>` prefix on narrative. Clock shows `elapsedSeconds`. Footer: `export.yaml` plus last hint. Textarea accepts multiline (Shift+Enter); Enter submits. Placeholder: “type a command, YAML, oc, or Java snippet…”. Do not add a mic button.

## Accessibility

- `aria-label="Game canvas"` on Panel A; `aria-live="polite"` on the GM log.
- Command field has a visible label (sr-only is acceptable).
- Seat list in HTML under the canvas so color is not the only cue (`<i>` swatch + title).
- Contrast: IBM Plex Mono on `#07110c` meets readable ops output; do not drop font size below 14px in the log.
