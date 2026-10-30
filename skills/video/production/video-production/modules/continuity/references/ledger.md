# Continuity ledger and review receipt

## Stable entity and state

```yaml
entity: prop-key-01
canonical_reference: {path: design/key-v02.png, version: 2}
description: Brass key; round head; red thread tied to ring.
events:
  - {scene: S02, order: 20, holder: Maya, state: intact, source: script-v03}
  - {scene: S03, order: 30, action: Maya gives key to Jin, source: script-v03}
  - {scene: S04, order: 40, holder: Jin, state: intact, source: script-v03}
unknown: Which pocket Jin uses after S03.
```

Unknown is not a license to invent a canonical detail. If it is invisible and does not affect the action, production can choose within the agreed design; if it changes later action, route it to the story owner.

## Shot inspection

| Unit / version | Expected state | Observed evidence | Verdict / impact |
| --- | --- | --- | --- |
| S03-04 / v02, 00:03.2 | Maya places key in Jin's left hand | Contact-sheet frame shows right hand; transfer interval not played | Needs action inspection; cannot certify hand continuity |
| S04-01 / v01, 00:00.7 | Jin has key with red thread | Red thread absent in close-up | Repair asset/shot; source design/key-v02.png |

Visual identity need not be pixel-identical across lighting or angles. Compare stable features and the requested style; tolerate intentional design variation only when the creative contract allows it.

## Canon change and affected units

```yaml
change_id: C07
authority: script-v04 approved revision
fact: Key transfer now occurs in S05.
replaces: script-v03 S03 exit state
affected:
  - {unit: S03-board, reason: Remove visible handoff}
  - {unit: S04-dialogue, reason: Jin can no longer say he has the key}
  - {unit: S05-blocking, reason: Add new handoff}
unaffected: [S02-exterior]
review_mode: independent
```

Use the project's task tool to record affected dependencies when available. A written list of proposed changes alone does not prove the downstream task state was updated.
