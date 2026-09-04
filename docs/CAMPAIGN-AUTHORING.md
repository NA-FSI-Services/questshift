# Campaign authoring (v1)

Campaign YAML is the puzzle source of truth. Granite narrates; it does not invent win conditions. Do **not** hide the solving command only in `game_master.system_prompt` or room `narrative`.

Canonical adventure:

- GitHub: https://github.com/NA-FSI-Services/questshift-campaigns/blob/main/campaigns/campaign-devops-dungeon.yaml
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns/campaigns/campaign-devops-dungeon.yaml`

Engine also ships a classpath copy at `questshift-engine/src/main/resources/campaigns/campaign-devops-dungeon.yaml`. GitOps embeds the same file via ConfigMap generator `k8s/campaigns/`. Change all three together, or local/cluster will drift.

## File shape

```yaml
apiVersion: questshift.io/v1
kind: Campaign
metadata:
  id: devops-dungeon          # CampaignLibrary key
  title: The Cluster That Forgot Its Name
  durationMinutes: 60
  recommendedPartySize: 4
seats: []                     # cosmetic; ids guardian|automancer|ranger|artificer
story:
  premise: ...
  opening: ...
  winCondition: ...
  failCondition: ...
rooms: []
game_master:
  system_prompt: ...
  output_schema: ...
```

Keep the whole file on a 60-minute arc (~10 min framing, ~8–12 min per room, ~5 min boss + debrief). v1 ships this one campaign only.

## Room contract

Each `Campaign.Room` (Jackson → `io.questshift.campaign.Campaign.Room`):

| Field | Required | Role |
| --- | --- | --- |
| `id` | yes | Stable key (`room-01-broken-shell`) |
| `order` | yes | Integer sequence; `nextRoom` is `order + 1` |
| `title` | yes | Phaser label |
| `mapX`, `mapY` | yes | Panel A coordinates |
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

## Regex + accepted examples

Write **one obvious intended command** plus a regex that still accepts reasonable aliases (`oc` vs `kubectl`, `grep -i` vs `grep`). Put that intended command in `accepted_examples` so a copy-paste from the authoring doc always passes.

`CommandEvaluator` pass path:

1. Reject empty
2. Reject if `requires_loot` missing from inventory
3. Reject if any `forbidden_patterns` matches
4. Pass if regex **or** an accepted example matches
5. Else puzzle-type soft match (last resort)

If the regex is invalid Java, the engine falls back to a case-insensitive `contains` on the pattern string — do not rely on that. Test examples with `CommandEvaluatorTest` or a local session.

## Forbidden patterns

Use these to block the known-broken command the room is teaching against:

- Room 1: `^\s*cat\s+/var/log/quest\.log\s*$`
- Room 3: `/readyz`
- Room 4: `greeting\.toUpperCase`, `/helo`

Forbidden beats a regex pass. Do not list the winning command here.

## YAML wins (authoring rule)

- Put the win in `expected_command_pattern` and `accepted_examples`.
- Put the miss in `forbidden_patterns` and `hint`.
- `system_prompt` may say “never reveal the full pattern unless they asked for a hint after a fail.” It must **not** be the only place the answer lives.
- `LLMService` copies YAML `puzzle_type` and regex onto the GM turn even if the model hallucinates new ones.

## Seats

Do not add `required_seat` or class checks. Blurbs already say anyone may solve any room.
