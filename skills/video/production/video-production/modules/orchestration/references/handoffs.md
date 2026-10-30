# Work packets and checkpoints

Use these fields within the project's existing task system. Do not introduce a competing task database.

## Bounded work packet

```yaml
id: shot-012-lighting
parent: scene-03
objective: Match the approved dusk lighting while preserving the camera and model.
owner: cg
inputs:
  - {id: scene-03-layout, version: 4, path: assets/scene-03/layout-v04.blend}
  - {id: dusk-look, version: 2, path: design/dusk-v02.png}
depends_on: [scene-03-layout]
write_scope: [work/shot-012/lighting-v01]
deliverables: [source scene, hero frame, change note]
acceptance: Same silhouette and framing; highlight shape matches look reference.
review_mode: independent
external_actions: none
```

Brief workers in normal concise prose plus the relevant packet. Do not forward all project history. The worker returns artifact paths, actual input versions, checks and blockers; the owner verifies the receipt before merging shared state.

## Production checkpoint

```yaml
updated_at: "2026-10-16T10:00:00+08:00"
brief_version: 3
accepted: [script-v03, design-v02, scene-01-edit-v02]
active:
  - {unit: shot-012, stage: external-render, provider_job: job-123, status: running}
needs_recheck: [scene-03-edit-v01]
decisions: [Narrator remains offscreen; blue jacket is canonical.]
missing: [Final license receipt for selected music]
next: Query job-123; inspect returned frame before editing scene-03.
```

Record facts, not aspirations: `independent` requires a distinct reviewer actually ran; `accepted` requires the appropriate gate passed. Do not place keys, secrets or complete private provider responses in the checkpoint.

## Scale the unit of work

| Project | Stable shared inputs | Useful units | Cross-unit acceptance |
| --- | --- | --- | --- |
| Single short/film | Script, design, asset versions | Sequence, scene, shot | Dramatic progression, rhythm, spatial and sonic continuity |
| Series | Series bible, character state, episode arcs | Episode then scene/shot | Information release and state across episodes |
| Explainer/documentary | Claim/source ledger, structure | Chapter, claim, illustration | Explanation dependencies, source accuracy, chapter pacing |
| Narrative MV | Music master, lyric map, story premise | Musical section and scene | Musical development plus story-state continuity |
| Visual MV/motion | Music master or motion mechanism | Phrase, loop, transformation | Visual motif development, beat/phrase alignment, final duration |

An expensive long-film shot may have layout, animation, lighting and compositing subunits. A small two-shot task normally does not need that breakdown.
