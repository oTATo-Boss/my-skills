---
name: animejs-workflows
description: Integrate Anime.js into an existing application or renderable video scene, with scoped ownership, teardown and deterministic capture. Use for React lifecycle, resource readiness, animation cleanup and browser/video clock integration.
metadata:
  version: "2.0.0"
---

# Anime.js integration

Inspect the project architecture, installed version, existing render loop and intended output before editing. Follow [official Anime.js documentation](https://animejs.com/documentation/) for that version; do not upgrade a dependency merely because an example uses a newer API.

## Ownership

Give each mounted component or scene one scope for targets and resources. In React, initialize against owned refs after the DOM exists, and revert/cancel the owned animations and listeners on cleanup. Verify remount behavior; development double mounting must not create duplicate listeners or animation instances. Avoid document-wide selectors that capture another component's nodes.

One subsystem owns each animated property. If CSS, a framework, Anime.js and a 3D renderer all write the same transform, choose an owner and pass parameters to it. A Canvas or Three.js scene retains one render loop. Do not add another loop merely to animate camera or material values.

## Playback and capture

Interactive playback may use the engine clock; offline video uses the renderer's explicit time. Build paused timelines and seek them from output time. Asset/font readiness, seeded variation and simulation state must be defined before capturing frames. Test arbitrary seek, reverse seek and repeated rendering of the same frame. Prefer the project's existing Remotion, HyperFrames or capture adapter instead of inventing a second export pipeline.

Responsive layout and fixed video framing are different contracts. Recompute geometry on layout changes for a website; lock the requested dimensions for video export. In interactive UIs, respect reduced-motion preferences and preserve keyboard/accessibility behavior. These UI constraints do not silently remove motion explicitly requested in a video.

## Completion

Run a targeted mount/unmount or scene-load test, then inspect the relevant visual interval in the real application or exported media. Check missing fonts/assets, duplicate work, layout shifts and changed final state. Preserve dependency versions and report which runtime was actually tested.
