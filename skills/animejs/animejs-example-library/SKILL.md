---
name: animejs-example-library
description: Find and adapt actual Anime.js examples from a pinned official source snapshot. Use to select a motion mechanism or inspect working typography, SVG, layout, Canvas and Three.js examples before writing a new implementation.
metadata:
  version: "1.0.0"
---

# Anime.js example library

Search [the catalog](references/catalog.md) for the requested mechanism, then inspect only the chosen example and its dependencies. The complete upstream snapshot and file identities are in [source-manifest.json](assets/upstream/source-manifest.json). Its source revision is fixed; this library is not evidence that a different installed Anime.js version supports the same calls.

Choose examples by the movement or interaction they demonstrate. Record the source path and revision. Replace sample branding, text, colors and media with the project's approved material; a reusable code example does not establish rights to every depicted brand or third-party resource.

Before integration read [integration.md](references/integration.md). Verify the modified result in the actual target runtime. For video, drive a deterministic output clock and inspect an exported interval; a browser demo alone does not prove export readiness.
