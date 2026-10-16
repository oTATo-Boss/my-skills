---
name: video-production-pipeline
description: Manage versioned video production from approved scripts and assets through shot renders, editing, sound, subtitles and delivery. Use for reproducible long-form, episodic or mixed-media production, render recovery and final QA; it does not replace creative direction or a specific renderer.
metadata:
  version: "1.0.0"
---

# Video production pipeline

Turn approved creative inputs into reproducible, inspectable outputs. Reuse the project's task system, directory layout and toolchain. Bind every produced artifact to its actual inputs; preserve source media and previously delivered versions.

## Establish a time and media contract

Read the requested frame size, aspect ratios, frame rate, duration, audio format, subtitles, language, color expectations and required editable sources. Use measured media metadata. Do not assume vertical 30 fps, silent exports or H.264 for every project.

For timeline math, declare one project timebase and preserve rational frame rates where used. Keep source timecodes and sample rates; convert deliberately at ingest or render. For narration-driven work, align the final timeline to actual recorded speech and holds. For MV work, use the actual music master and phrase markers. Do not change playback speed to conceal unexplained duration mismatches.

## Produce one unit reproducibly

1. Register source IDs, paths, versions, hashes where available, provenance and use restrictions. Pin assets, fonts, tool/package versions and random seeds when needed for repeatability.
2. Confirm the selected tool really exists and can execute the needed route. A skill file or feature flag alone does not prove rendering, image generation or account access.
3. Validate a representative difficult frame/interval before bulk production. Include the final output scale and sound where it affects timing.
4. Render/generate into a new versioned work path. Save the exact command or reconstructible project configuration, input versions, output metadata and external job IDs. Never put credentials in the manifest.
5. Inspect the resulting media, accept or return a concrete defect, and only then add the unit to the accepted edit. Keep rejected output when useful for traceability; do not label it final.

For code animation, use a deterministic frame-time entrypoint. Wait for fonts/assets before rendering; remove uncontrolled wall-clock timers, pointer-dependent initial state and duplicate render loops. For browser Three.js/Anime.js, a smooth live preview is not evidence of deterministic offline capture.

Read [routes-and-qa.md](references/routes-and-qa.md) for route-specific acceptance and real-media QA. Read [manifest.md](references/manifest.md) when recording versions, external submissions or final delivery.

## Assemble and validate

Edit accepted units with handles where the project needs transitions or sound overlap. Check shot boundaries and whole-sequence progression. Mix dialogue, music and effects for the requested destination; check clipping and loudness against that delivery specification rather than a universal target. Keep dialogue/music/effect stems when required.

Generate subtitles from the actual final spoken audio; check timing, readability, speaker attribution, punctuation, safe areas and translation meaning. Track burnt-in and separate subtitle versions separately.

Technical verification includes metadata, full decode, missing media, audio channels and duration. Visual verification includes representative frames and continuous playback across motion and cuts. Listening verification requires actual audio perception. Mark each unavailable modality unverified; never infer aesthetic or sonic success from meters or file size.

After a correction, recheck the affected unit and assembly boundary, then verify the actual final file. Bind approval to its hash or equivalent exact version so a later render cannot inherit stale approval.

## Recovery and delivery

Persist external request intent before submission and provider job ID immediately after. On a timeout or lost response, query/reconcile first; do not automatically resubmit a potentially paid job. Keep a checkpoint that allows another session to retrieve active jobs and resume the correct unit.

Deliver a new immutable version containing the requested master, channel variants, subtitle files, editable sources and an inventory of external dependencies. State checks actually performed and remaining limitations. A job queued, a project that builds, or a successful transcode alone is not a completed film.
