# Video production skills v1 design

2026-10-16. Consumer: AI-SMA v2 and standalone video projects. Each package is an independent, harness-neutral method skill. The user's project owns its folders, task tool, credentials, approval boundaries and delivery contracts.

```mermaid
flowchart LR
  P[Existing project brief and state] --> O[SKILL: video-project-orchestration]
  O --> W[SKILL: screenwriting]
  W --> C[SKILL: production-continuity]
  W --> V[SKILL: video-production-pipeline]
  C --> V
  V --> A[Existing project artifacts and evidence]
```

Edges represent optional workflow composition, not mandatory package imports. Each skill has its own runnable-by-agent procedure and inline artifact examples; no sibling file is needed at load time. Renderer and generation tools belong to the selected project, not these skills.

```mermaid
sequenceDiagram
  participant Lead as Existing project owner
  participant Work as Assigned role or same agent
  participant Store as Project artifact store
  Lead->>Store: Read latest brief, versions and pending tasks
  Lead->>Work: One bounded unit, inputs, allowed writes and acceptance
  Work->>Store: Write versioned artifact and evidence
  Work-->>Lead: Return paths, input versions, checks and blockers
  Lead->>Store: Verify evidence and merge shared state
```

Single writer owns each shared manifest. Independent work may use the client's native child agents; absent that capability the same role packets run sequentially and review is labeled self. No new agent framework or client settings are installed by these methods.

| Module | Input | Output | Excludes |
| --- | --- | --- | --- |
| video-project-orchestration | Goal, constraints, project state | Work packages, handoffs, checkpoint | Creative direction, renderer implementation, installation |
| screenwriting | Brief, research, approved story and scope | Treatment, script or revision and production notes | Unasked full prose, shooting or publishing |
| production-continuity | Approved script, assets, cuts, change request | State ledger, discrepancies, impact set | Invented canon or automatic creative rewriting |
| video-production-pipeline | Approved units, assets and delivery specs | Versioned production manifest, QA and delivery evidence | Selecting the user's story or claiming unobserved playback |

Composition: short common procedure in each entrypoint; long-form, example artifacts and route-specific guidance loaded only for the active mode. Cost stance balanced: existing model settings, no per-model routing; one bounded work unit at a time, concise receipts, persisted project state for resumption. No dedicated runtime dependencies for the four method skills. The image bridge separately requires Python and an actual compatible, authenticated Codex CLI.

Validation: lint four entrypoints and links; exercise film/series, explanatory, narrative MV and partial-edit scenarios. Parent AI-SMA validation must record actual use on four rendered samples. Unit tests for the image bridge cover output ownership, unavailable capability, recovery paths, Unicode paths and non-overwrite. Structural checks do not prove creative effectiveness; controlled with/without-skill model evaluation and native Windows/Linux execution remain separately reported until run.
