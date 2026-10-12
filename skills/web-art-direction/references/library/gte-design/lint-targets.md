> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# Lint targets

Deterministic, machine-checkable subset of the GTE hard rules. Each row maps a
stable rule ID to a concrete check, the mechanism that can enforce it, and
whether a fix can be applied automatically.

The current `guide.md` (the Claude Design export) states the hard rules as
prose without inline IDs, so the table below is the **rule-ID registry**: cite
these IDs in reviews, lint output, and component specs. IDs were assigned
against the same rules in the June 2026 revision and their meanings are
unchanged. The bundle also ships `_adherence.oxlintrc.json`, Claude Design's
own machine-check config — that file and this one should converge over time.

| ID | One-line summary | Category |
|---|---|---|
| `GTE-THM-01` | Product is dark-surface only; light tokens are scoped to non-product work | THM |
| `GTE-NUM-01` | Numbers are always JetBrains Mono with tabular-nums (and slashed zeros) | NUM |
| `GTE-CLR-01` | Green = long/bid/up, red = short/ask/down; never swap | CLR |
| `GTE-VOX-01` | No emoji, no unicode-as-icon | VOX |
| `GTE-CLR-02` | No gradient decoration on surfaces | CLR |
| `GTE-CLR-03` | Orange (`--accent`) is reserved for primary CTA / focus / brand — not decoration | CLR |
| `GTE-TYP-01` | Text is one of three greys (`--text-high/mid/low`); no colored body text | TYP |
| `GTE-BRD-01` | Borders are 1 px, `rgba(255,255,255,0.06)`; never 2 px, never dashed | BRD |
| `GTE-DGM-01` | Diagrams: flat fills only — `--surface-elevated-2` nodes, no gradients/shadows/strokes on fills | DGM |
| `GTE-DGM-02` | Diagrams: wordmark the special node — reserve orange tint + orange text for entry points only | DGM |
| `GTE-DGM-03` | Diagrams: no borders on nodes — separation by surface-step | DGM |
| `GTE-DGM-04` | Diagrams: numbering is optional; if used, `01`..`0N` in JetBrains Mono 11 px orange | DGM |
| `GTE-DGM-05` | Diagrams: one label per edge, one line | DGM |

Only the rules that can be checked *mechanically* appear in the check table
below. Rules that require human judgement (e.g. "orange is reserved for brand
moments — `GTE-CLR-03`", or "when in doubt: dark — `GTE-THM-01`") are
intentionally out of scope for the linter and stay in `guide.md` as review
guidance.

Anything not directly grounded in the source `foundations.md` / `guide.md` is
marked **proposed — confirm**.

| Rule ID | Check | Mechanism | Autofixable? |
|---|---|---|---|
| `GTE-CLR-04` (proposed — confirm) | No raw hex color literals outside a `var(--*)` reference — all color must flow through a token | stylelint `color-no-hex` + `declaration-property-value-disallowed-list` (see snippet below) | No (requires choosing the right token) |
| `GTE-NUM-01` | Price / number / numeric elements must use a mono (`.mono-*` / JetBrains Mono) class and `font-variant-numeric: tabular-nums` | Custom stylelint/ESLint rule scanning numeric-bearing elements (see regex below); also a stylelint check that `font-variant-numeric` accompanies mono usage on numeric classes | No (needs the right class applied) |
| `GTE-NUM-01` | No non-tabular / non-mono numerals on price/number elements — flag elements that render numerics but resolve to Inter or omit `tabular-nums` | ESLint JSX rule on elements matching the numeric selector list (proposed list below) | No |
| `GTE-TYP-01` | All-caps Inter is banned (Inter must never be set in all caps — `text-transform: uppercase` on an Inter run) | stylelint `declaration-property-value-disallowed-list` for `text-transform: uppercase` on Inter contexts (see snippet); the badge/pill exception is allowlisted by class | Partially (can flag; cannot decide if it is an allowed pill) |
| `GTE-TYP-01` | Non-display / non-mono font where mono is required — numeric/data runs must not fall back to Inter or Ogg | stylelint custom rule: numeric selectors must resolve to `--font-mono` / JetBrains Mono | No |
| `GTE-TYP-02` (proposed — confirm) | Body/label text color must be one of `--text-high` / `--text-mid` / `--text-low`; no other color on body text | stylelint `declaration-property-value-allowed-list` for `color` on text selectors | No |
| `GTE-BRD-01` | Borders must be `1px` and never `2px`+ and never `dashed`/`dotted` | stylelint `declaration-property-value-disallowed-list` on `border*` (see snippet) | Partially (can rewrite `2px`→`1px`; style fixes need review) |
| `GTE-CLR-02` | No `linear-gradient` / `radial-gradient` on surface `background`/`background-image` (decorative gradients banned on surfaces) | stylelint `declaration-property-value-disallowed-list` for `*gradient*` on `background*` | No (tinted-state exception per README is intentional) |
| `GTE-VOX-01` | No emoji and no unicode-as-icon (`★`, `➕`, arrows-as-chars) anywhere in copy/markup | Text/JSX lint scanning string literals for emoji + the banned glyph set (regex below) | No |
| `GTE-VOX-02` | No hedge words in copy — banned terms from `foundations.md`: `approximately`, `about`, `around` (use a number or `~`) | Text/JSX string-literal lint, case-insensitive word-boundary match (regex below) | No (rewrite is editorial) |
| `GTE-DGM-01` | Diagram node fills are flat — no `gradient`, `filter: drop-shadow`, `box-shadow`, or `stroke` on node fills | stylelint scoped to diagram SVG classes (`.node` fill) | No |
| `GTE-DGM-03` | Diagram nodes have no border/stroke (`stroke: none` on `.node` rects) | stylelint scoped to `.node` rect | Yes (can force `stroke: none`) |

> Note on rule IDs: `GTE-CLR-04`, `GTE-TYP-02`, and `GTE-VOX-02` are **new IDs introduced for lintable checks** that the source prose implies but does
> not state as standalone numbered hard rules (raw-hex-via-tokens, the three-grey constraint as a *machine check*, and the hedge-word ban). They are
> marked **proposed — confirm** so Arnie can ratify or fold them into existing rules. Everything else maps to an existing hard rule.
>
> Not yet covered by any ID: the newer hard rules from the current `guide.md` revision (canvas is `--surface-elevated-1`, density tiers / 11 px default
> body, the 23.43°-slant-only exception, slashed zeros + self-hosted mono). Assign IDs when Arnie ratifies the proposed set.

## Banned hedge words (source: `foundations.md` › Content Fundamentals)

The README lists these explicitly — do not invent additional terms here:

- `approximately`
- `about`
- `around`

Replacement guidance from the README: "Commit to a number or show a `~` character."

## Starter regexes

These are starting points, not finished rules — tune anchoring and false-positive
handling before wiring into CI. Mark each as `proposed — confirm` until verified
against the real codebase.

```
# GTE-VOX-02 — banned hedge words (case-insensitive, word-boundary)
\b(approximately|about|around)\b

# GTE-VOX-01 — banned unicode-as-icon glyphs (extend as needed)
[★☆➕←-⇿⌀-➿]      # ★ ☆ ➕ arrows, misc symbols/dingbats
# emoji blocks (broad):
[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}]

# GTE-NUM-01 — proposed numeric element selector list (confirm against real markup):
# elements/classes that render prices, sizes, PnL, %, timestamps, hashes, addresses
\b(price|size|pnl|p-and-l|pct|percent|change|timestamp|hash|address|amount|qty|balance|funding|leverage)\b
```

## Starter stylelint config (proposed — confirm)

```jsonc
{
  "rules": {
    // GTE-CLR-04 (proposed): no raw hex; force var(--*) tokens
    "color-no-hex": true,
    "declaration-property-value-disallowed-list": {
      // GTE-CLR-04: catch rgb()/rgba()/hsl() literals on color props that aren't var()
      "/^(color|background|background-color|border-color|fill|stroke)$/": [
        "/#[0-9a-fA-F]{3,8}/",
        "/^(rgb|rgba|hsl|hsla)\\(/"
      ],
      // GTE-BRD-01: no thick or non-solid borders
      "/^border(-(top|right|bottom|left))?$/": ["/\\b([2-9]|[1-9]\\d+)px\\b/", "/\\b(dashed|dotted)\\b/"],
      "border-width": ["/\\b([2-9]|[1-9]\\d+)px\\b/"],
      "border-style": ["dashed", "dotted"],
      // GTE-CLR-02: no decorative gradients on surfaces
      "/^background(-image)?$/": ["/gradient/"],
      // GTE-TYP-01: no all-caps Inter (allowlist pill/badge classes separately)
      "text-transform": ["uppercase"]
    }
  }
}
```

> The `text-transform: uppercase` ban (`GTE-TYP-01`) needs an allowlist for the
> README's documented exception: short uppercase pills/badges (`"LONG"`,
> `"SHORT"`, `"MARKET"`, `"LIMIT"`, `"GTC"`, `"IOC"`). Scope the rule so badge
> classes are exempt — **proposed — confirm** which classes those are.
