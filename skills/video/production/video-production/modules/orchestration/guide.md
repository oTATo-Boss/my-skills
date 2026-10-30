# Video project orchestration

Convert the user's outcome into bounded, resumable work. Use the project's existing folders, role names, task commands, IDs and acceptance rules. This skill supplies coordination method; it does not replace the project's agent framework or install tools.

## Establish the current contract

Read the brief, latest checkpoint and relevant active tasks before dispatch. Separate facts from proposals. Record only unresolved decisions that affect what can be produced: audience and response, format, duration, source material, delivery variants, technical route and authorized external actions. Honor an explicit analysis or approval boundary. Resolve routine production choices without repeated confirmation.

Identify three independent dimensions: content type, single film/series/account, and production route. A platform is a delivery constraint, not a story genre. A long-form interview should not inherit short-form hook frequency; an animated short should not inherit account publishing tasks.

For a narrow request such as correcting subtitles, enter the affected stage directly. Reuse approved upstream work; do not demand a new brief, team or style study.

## Build the smallest useful work graph

1. Define the final artifacts and their acceptance evidence, then work backward to the necessary inputs.
2. Decompose by independently reviewable units. A long film uses sequences/scenes/shots; a series adds episode and shared canon; an explainer uses claims/sections/visual beats; an MV follows musical sections plus any narrative scenes.
3. Give every unit one owner, exact input revisions, permitted output paths and a finish condition. Keep a single writer for shared manifests, continuity ledgers and final assemblies.
4. Parallelize units only when inputs are stable and output ownership does not overlap. Use the client's native subagents when available. Otherwise execute the same packets sequentially and label reviews `self`.
5. Prefer a representative difficult unit before multiplying work. Validate a look, voice, pipeline or continuity assumption at the scale where it could fail.

Read [handoffs.md](references/handoffs.md) when creating work packets or a checkpoint for a new session. It contains directly usable structures, not a required new directory layout.

## Receive, reconcile and recover

Accept a receipt only after checking its files and stated evidence. A renderer exit code is not creative approval; a claimed tool call is not an installed capability. Preserve observed, inferred and untested states separately. Review mode must reflect who actually reviewed the artifact.

For revisions, compare the approved input version with the changed version; mark dependent work for recheck and dispatch only the affected interval/unit. Do not reset unrelated accepted scenes. Keep previous deliveries immutable and write a new delivery version.

Before an external generation/render submission, persist the request intent and idempotency key when supported. After submission, persist the returned task ID. If the response is lost, query that ID or provider history before retrying; an unknown outcome is not a failed task. Do not duplicate a paid request to discover whether the first succeeded.

On interruption, record finished artifacts, active external IDs, unresolved decisions and the next bounded action. A new conversation must resume from project files without relying on hidden chat history. Apply the project's concurrency and retry limits; if none exist, start with at most three independent workers and two evidence-driven repair attempts, then report the unresolved cause instead of repeating the same action.

## Completion receipt

```yaml
unit: sequence-02
owner: editor
inputs: [{id: script, version: 3}, {id: selects, version: 2}]
outputs: [{path: work/sequence-02/edit-v02.mp4, version: 2}]
checks: [{kind: decode, result: passed, evidence: work/sequence-02/decode.txt}]
review_mode: self
unverified: [continuous playback, listening]
next: review sequence boundary with sequence-03
```

Use actual project paths and evidence. Close only when the requested deliverables exist and their required checks pass; otherwise return usable completed work plus the specific remaining dependency.
