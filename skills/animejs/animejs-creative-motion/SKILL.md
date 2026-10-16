---
name: animejs-creative-motion
description: Design and implement Anime.js motion for typography, SVG, geometric compositions and video graphics. Use when motion structure is the deliverable; preserve a supplied visual direction and use a deterministic timeline for exported video.
metadata:
  version: "2.0.0"
---

# Anime.js creative motion

Start from the visible event and its purpose: an object changes, a relationship becomes legible, or a phrase receives emphasis. Define the start, transition and end state before selecting an easing function. Read the installed project's Anime.js version and the matching [official documentation](https://animejs.com/documentation/) before using an unfamiliar API.

## Design the movement

- Choose the focal object, reading order, depth and timing from the brief. Use anticipation, overlap or follow-through only where they clarify the action.
- For typography, preserve readable holds and intentional line breaks at the target dimensions. Distinguish the message's arrival from decorative per-letter movement.
- For SVG, inspect path geometry and coordinate systems. Make draw, morph and position changes reflect the intended object rather than concealing an unsuitable drawing.
- For a generated field, derive positions and variations from recorded parameters and a seed. Avoid independent random changes that break visual continuity.
- Adapt actual official examples when their mechanism fits. Record the example source and replace its unrelated brand, text and assets.

## Produce a video-safe timeline

Use a paused timeline and drive it from the output frame's time. Anime.js [seek](https://animejs.com/documentation/timeline/timeline-methods/seek/) accepts milliseconds. Keep one owner of the clock; do not combine autonomous animation playback with a separate capture clock. Use callbacks for application effects only when they do not make a sought frame depend on prior playback history.

When images, fonts or 3D resources are involved, establish a readiness signal before capture. Keep randomness, physics state and camera placement reproducible. For simulations, precompute or replay a defined fixed-step state rather than assuming seek can reverse arbitrary external effects.

## Verify the actual result

Inspect the first frame, focal transition, readable hold and end state at delivery size. Compare direct seeking to sequential playback for the same frames. Check continuous motion and audio alignment when applicable. Render a short interval through the selected media renderer before exporting the whole piece. Report browser preview and rendered-file verification separately.

A narrow timing revision should preserve approved content and geometry. Return the changed source and requested preview/export, with the real remaining limitations.
