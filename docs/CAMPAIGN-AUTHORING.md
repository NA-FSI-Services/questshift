# Campaign authoring

Campaign YAML is the puzzle source of truth. Granite narrates; it does not invent win conditions. Do **not** hide the solving command only in `game_master.system_prompt` or room `narrative`.

Shipped adventures (two cards; default remains `devops-dungeon`):

| Id | Title | GitHub | Local |
| --- | --- | --- | --- |
| `devops-dungeon` | The Cluster That Forgot Its Name | https://github.com/NA-FSI-Services/questshift-campaigns/blob/main/campaigns/campaign-devops-dungeon.yaml | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns/campaigns/campaign-devops-dungeon.yaml` |
| `ansible-bastion` | The Bastion That Lost Its Runbook | https://github.com/NA-FSI-Services/questshift-campaigns/blob/main/campaigns/campaign-ansible-bastion.yaml | `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns/campaigns/campaign-ansible-bastion.yaml` |

Engine ships classpath copies under `questshift-engine/src/main/resources/campaigns/`. GitOps embeds the same files via ConfigMap generator `k8s/campaigns/`. Change all three together, or local/cluster will drift.

## File shape

```yaml
apiVersion: questshift.io/v1
kind: Campaign
metadata:
  id: devops-dungeon          # CampaignLibrary key (or ansible-bastion)
  title: The Cluster That Forgot Its Name
  durationMinutes: 60
  recommendedPartySize: 4
seats: []                     # cosmetic; ids guardian|automancer|ranger|artificer
story:
  premise: ...
  opening: ...
  clues: []                 # lobby-map chests (overworld x/y); empty viewedRoomId
  winCondition: ...
  failCondition: ...
rooms: []
game_master:
  system_prompt: ...
  output_schema: ...
```

Keep the whole file on a 60-minute arc (~10 min framing, ~8–12 min per room, ~5 min boss + debrief). Post-v1 ships **two** campaigns; do not add a third without a new decision.

## Room contract

Each `Campaign.Room` (Jackson → `io.questshift.campaign.Campaign.Room`):

| Field | Required | Role |
| --- | --- | --- |
| `id` | yes | Stable key (`room-01-broken-shell`) |
| `order` | yes | Integer sequence; `nextRoom` is `order + 1` |
| `title` | yes | Phaser label |
| `mapX`, `mapY` | yes | Panel A overworld coordinates |
| `clues` | yes | List of floor chests **inside this room**. Each needs `id`, `label`, `text`, `x`, `y`. `x` / `y` are interior canvas coordinates. Fragments only — do **not** put a full `accepted_examples` command in `text`. Opening a chest shows a map dialog to **that player only**; it does not dump the text on Panel B. Chests stay on the floor after open. Do not put these on the overworld. |
| `guardian` | yes | `{ id, title, sprite }` for the north challenge door. `sprite` must be one of `guardian_shell`, `guardian_playbook`, `guardian_pod`, `guardian_servlet`, `guardian_throne`. Distinct `id` and `sprite` per room. The guardian is a **cosmetic** sprite on `door_locked` until the puzzle is solved; beating it is the YAML command, not combat. Do not author weapons or battle stats. |
| `miss_beats` | no | Ordered `{ pattern, message }` fails after regex/examples/soft match miss. First matching pattern supplies the GM miss line (YAML wins; no LLM rewrite). Room 1 uses these for a shouted name and a grep without awk. |
| `puzzle_type` | yes | `linux` \| `ansible` \| `openshift` \| `java` |
| `estimatedMinutes` | no | Facilitator pacing |
| `narrative` | yes | YAML fallback GM text |
| `prompt` | yes | Shown to the model as the task |
| `expected_command_pattern` | yes | Java regex, `CASE_INSENSITIVE \| DOTALL`, `.find()` |
| `accepted_examples` | yes | Whitespace-collapsed exact matches |
| `forbidden_patterns` | no | Known-wrong forms; scored **before** pass |
| `hint` | yes | Fallback + miss flavor |
| `success_narrative` | yes | After pass |
| `loot` | no | `{ id, name, kind }` granted on pass |
| `canvas_event` | yes | Phaser event on pass |
| `skills_granted` | no | Flavor strings |
| `requires_loot` | no | Inventory ids that must already be held |
| `sample_output` / `broken_snippet` | no | Ignored by Java; useful for authors and GM context |

## Challenge doors and guardians

Every challenge room has two interior doors. Author them in `narrative` / `success_narrative`; Panel A draws them from this contract (coordinates in [UX.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/UX.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/UX.md`)):

1. **Lobby door (south).** Always open (`door`). Returns to the overworld. Never put the guardian on this door.
2. **Challenge door (north).** Locked (`door_locked`) with `guardian.sprite` until `puzzleCompletion[roomId]`. After a pass, the guardian is gone and the north door shows open (`door`). That open door enters the next YAML room (`order + 1`) when that room is unlocked. The throne has no successor. Sequential scoring still goes through YAML; the lobby remains an alternate path.

v1 *The Cluster That Forgot Its Name* guardians:

| Room | `guardian.id` | `sprite` |
| --- | --- | --- |
| The Broken Shell | `shell-golem` | `guardian_shell` |
| The Playbook of Binding | `bound-familiar` | `guardian_playbook` |
| The Pod That Would Not Wake | `crashing-wizard-ghost` | `guardian_pod` |
| The Cursed Servlet | `servlet-slime` | `guardian_servlet` |
| The Operator's Throne | `nameless-wraith` | `guardian_throne` |

`ansible-bastion` reuses the same five Kenney `guardian_*` sprite keys with new titles (no new art). Do not hide the win only in the guardian's flavor text. Regex + `accepted_examples` still score.

## Ansible room contract (`ansible-bastion`)

Every room in *The Bastion That Lost Its Runbook* uses `puzzle_type: ansible`. Scoring stays **simulated**: the party types playbook YAML into Panel B; the engine never runs `ansible-playbook`, never calls AWS, and never talks to Automation Controller. Put wins in `expected_command_pattern` + `accepted_examples`; put cursed forms in `forbidden_patterns`.

| Order | Room (draft id) | Teaching beat | Scorer notes |
| --- | --- | --- | --- |
| 1 | The Courier's Vault (`room-01-couriers-vault`) | Copy / template files | `hosts` + named task + `ansible.builtin.copy` or `template` (or short `copy`/`template`) writing a known `dest` (e.g. `/etc/questshift/bastion.conf`). Forbid nameless tasks and wrong `dest`. |
| 2 | The Chapel of Common Services (`room-02-chapel-of-services`) | Packages + services | `package` / `yum` / `dnf` **and** `service` with `state` / `enabled` for a common daemon (e.g. `nginx` or `chronyd`). Forbid start-only without a package task. |
| 3 | The Gate of Whispered Cidrs (`room-03-gate-of-cidrs`) | Network resources | `ansible.posix.firewalld` **or** `amazon.aws.ec2_security_group` allowing a documented port/CIDR. Forbid open `0.0.0.0/0` on SSH when teaching least privilege. |
| 4 | The Drifted Cloudforge (`room-04-drifted-cloudforge`) | AWS components | `amazon.aws` module(s) (e.g. S3 bucket + tag, or EC2 instance tag). **Text only** — no live AWS. |
| 5 | The Controller's Throne (`room-05-controllers-throne`) | Boss playbook | Short multi-task play (optional `block` / `handlers`) that restores Controller name *Aether*; `requires_loot` prior runes (QUILL → LAMP → GATE → SIGIL). |

Loot rune ids land in the YAML. Accept FQCN and short module names in the regex when facilitators reasonably type either. Never put AWS keys, AAP tokens, or kubeconfigs in clue text or `accepted_examples`.

## Clues (layer-scoped map dialogs)

Dialogs belong to **one layer**. A player may open and read only the layer they are on. Empty `viewedRoomId` is the in-run Kenney overworld (the lobby map after Start), not the pre-run Start screen.

| Layer | YAML | Coordinates | Panel B flavor |
| --- | --- | --- | --- |
| Overworld (`viewedRoomId` empty) | `story.clues` | Overworld `x` / `y` (same space as room `mapX` / `mapY`) | `story.opening` (and premise) — not a challenge room’s `narrative` |
| Interior (`viewedRoomId` = that room) | that room’s `clues` | Interior canvas `x` / `y` | that room’s `narrative` |
| Leave through the south lobby door | close the open dialog | — | drop the interior dump; return to lobby copy |

`story.clues` is required. Author at least one lobby chest (hour rules, which gate is open, premise fragments — never a winning command). Keep each room’s existing chests on that room. Do not reuse a room clue `id` on the lobby. Do not place room-1 log fragments on the overworld.

Each room still needs at least one `clues` entry. `text` is what a **private map dialog** shows after that player opens the chest (`/var/log/quest.log` tree, `hosts: dungeon`). Unique `id`s across the campaign, including lobby. Opening a chest never scores the puzzle, never copies the fragment onto the shared terminal, and never removes the chest from the floor. Do not open a dialog whose layer is not the current `viewedRoomId`. Shared `commandLog` stays the current scoring room; it is not a map dialog.

## Regex + accepted examples

Write **one obvious intended command** plus a regex that still accepts reasonable aliases (`oc` vs `kubectl`, `grep -i` vs `grep`). Put that intended command in `accepted_examples` so a copy-paste from the authoring doc always passes.

`CommandEvaluator` pass path:

1. Reject empty
2. Reject if `requires_loot` missing from inventory
3. Reject if any `forbidden_patterns` matches
4. Pass if regex **or** an accepted example matches
5. Else puzzle-type soft match
6. Else first matching `miss_beats` pattern (authored miss line)
7. Else generic fail

If the regex is invalid Java, the engine falls back to a case-insensitive `contains` on the pattern string — do not rely on that. Test examples with `CommandEvaluatorTest` or a local session.

## Forbidden patterns

Use these to block the known-broken command the room is teaching against:

- Room 1: `^\s*cat\s+/var/log/quest\.log\s*$`
- Room 3: `/readyz`
- Room 4: `greeting\.toUpperCase`, `/helo`

Forbidden beats a regex pass. Do not list the winning command here.

## Miss beats (authored guardian lines)

Optional `miss_beats` run **after** a pass check fails. Use them when a near-miss needs a specific line instead of the generic hint:

- Room 1 name-only (`THORN`, `rune=THORN`): the shell golem rejects a shouted name with no filesystem evidence.
- Room 1 grep without awk: the resolved line is too long; only part of it is relevant.

The engine copies that `message` onto the attempt’s `commandLog.narrative` (addressed to `name`) and onto `lastNarrative` / `lastHint`. It does not ask vLLM to rewrite it.

## YAML wins (authoring rule)

- Put the win in `expected_command_pattern` and `accepted_examples`.
- Put the miss in `forbidden_patterns` and `hint`.
- `system_prompt` may say “never reveal the full pattern unless they asked for a hint after a fail.” It must **not** be the only place the answer lives. The engine also sends the player submission and the first `accepted_examples` to the LLM as private coaching so the Game Master can react in character (greetings still need a solving command). Do not dump that example in `narrative`.
- `LLMService` copies YAML `puzzle_type` and regex onto the GM turn even if the model hallucinates new ones.

## Seats

Do not add `required_seat` or class checks. Blurbs already say anyone may solve any room **when they hold the Game Master floor**. Turn order is `partyMembers` join order (`turnName`), not a YAML `required_seat`. Do not hide the floor grant only in `system_prompt`; the engine owns `turnName` and YAML fallback still announces it.

## Validate locally

From `questshift-campaigns`: `python3 -m pip install -r requirements-dev.txt && ./verify.sh`. That yamllints the adventures, runs ruff, and checks the contract above (`tools/campaign.py`: two campaigns `devops-dungeon` + `ansible-bastion`, five rooms each, cosmetic seats, compiling regexes, `story.clues`, per-room `guardian` and `clues`, unique clue ids, no secret-looking text). Pre-commit: `./.githooks/install`. Full quality map: [QUALITY.md](https://github.com/NA-FSI-Services/questshift/blob/main/docs/QUALITY.md) (local `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/QUALITY.md`).
