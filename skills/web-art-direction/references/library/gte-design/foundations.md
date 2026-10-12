> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# GTE Design System

A design system for **GTE** — a high-performance on-chain perpetuals trading platform. Built from the GTE Figma file ("GTE Design System") and the production `gte-web` codebase (Next.js 16 / React 19 / Tailwind 4).

## What is GTE?

GTE is a crypto trading product focused on **perpetual futures (perps)** with spot-style speed, an on-chain orderbook ("Turbo"), and a web app at the core. The UI centers a dark, fast, information-dense trading terminal — chart + order book + trade form — paired with an onboarding flow, portfolio, and an inline **Economic Agent** (AI) for research and execution assist.

Sources this system was built from:

- **Figma** — `GTE Design System.fig` (mounted VFS) — 5 pages: `/Atomic`, `/Web`, `/Mobile`, `/Sandbox`, `/Cover`. Focus was `/Atomic` and `/Web`.
- **Codebase** — `gte-web/` (repo `gte-web-v3`). Tokens live in `src/shared/styles/generated/supernova-tokens.desktop.css` (Supernova export); typography in `src/shared/styles/typography.css`; button system in `src/shared/styles/button.css`. UI primitives in `src/ui/*`; composite screens in `src/features/trading/*`.

## Index

| File | What it is |
|---|---|
| `foundations.md` | This manifest |
| `guide.md` | Agent Skill entry for Claude / Claude Code |
| `colors_and_type.css` | CSS vars for colors, fonts, radii, spacing + `.h1`..`.h6`, `.p1`..`.p3`, `.mono-1..4`, `.btn-1..3` |
| `fonts/` | JetBrains Mono (variable + regular), Ogg Text Light |
| `assets/logos/` | `gte-logo-white.svg` / `gte-logo-black.svg` (wordmark), `turbo-logo-white.svg` / `turbo-logo-black.svg` (Turbo chain mark) |
| `assets/tokens/` | ETH / USDC / USDT / placeholder |
| `assets/chains/` | Ethereum, Base, Arbitrum, Optimism, Polygon, Hyperliquid |
| `assets/backgrounds/` | `orders-per-second.svg` marketing flourish |
| `assets/brand-images/` | Four photos used by the locked marketing previews |
| `assets/misc/` | `linear.svg` |
| `preview/` | Small HTML cards that populate the Design System tab |
| `ui_kits/web/` | Hi-fi recreation of the GTE web trading terminal |
| `preview/.../icons.html` | Icon reference (Lucide CDN — matches `lucide-react` in repo) |

## Visual Foundations

**The vibe.** Near-black background, glowing **orange** accents, **electric green / hot pink** for long/short and up/down. Dense grids, hairline strokes, big mono numbers. The product looks like a Bloomberg terminal that drank a monster — minimal chrome, zero decoration, everything earns its place.

### Color

- **App surface** (the canvas) in dark mode is `--surface-elevated-1` `#101213` (near-black, slight cool cast) — this is what `body` and every app-shell surface render on in `gte-web`. The deeper `--surface-default` `#010304` is **reserved**: used only for separators/scrims and future deeper-floor layouts, *not* as the canvas. Cards and panels step **up** from the canvas to `--surface-elevated-2` `#181A1B`. There are no pure-white backgrounds anywhere unless asked to provide a light-mode version.
- **Text** is a 3-tier greyscale: `#FFFFFF` (high) / `#A6A7A8` (mid) / `#6A6E71` (low). No colored body text. Labels, timestamps, column headers live at mid/low.
- **Brand orange** `#FF7817` is reserved — primary CTA, focus rings, selected tab underline, the occasional numeric highlight. Using it is a design choice, not decoration. **Orange used as *text*** (links, accent numerals) uses the **`--text-accent`** token, which is bright orange on dark but **darkens to `orange-1000` under `data-theme="light"`** for contrast — the light peach of `--accent-light` is unreadable on a light canvas. Orange *fills* (buttons) are unaffected.
- **Semantic color is binary** in this product: **green `#2EE88B` = long / bid / positive**, **red `#FF667D` = short / ask / negative**. Both have 15 % / 25 % muted variants for tinted backgrounds.
- Strokes are almost always `rgba(255,255,255,0.06)` (default) or `rgba(255,255,255,0.15)` (subtle). Never darker than default — the system separates by brightness, not by adding color.

### Theme · dark is the product, light is a tool

- **The product is dark-mode only.** Every shipped app surface — trading terminal, portfolio, onboarding, settings, modals, mobile — uses the dark tokens. No exceptions, no toggle, no system preference.
- **Light-mode tokens exist but are scoped.** They are opt-in via `data-theme="light"` on a container and are reserved for **non-product work only**:
  - Infographics, data visualizations, research notes
  - Marketing pages, landing sections, press kits
  - Slides, decks, one-pagers
  - Social / OG cards where a light background improves readability off-platform
- Never apply `data-theme="light"` to anything a user reaches through the app shell. If a surface lives inside the trading product, it stays dark — even empty states, error screens, and print views.
- When in doubt: **dark**. Light is the exception, invoked deliberately, and always outside product chrome.

### Type

- **Inter** for **everything non-numeric** — **product** headings `700`, body `400`, emphasis `600`, buttons `500`. Used for labels, chips, body text, buttons, and all headings *in the product*. (Marketing headlines are the exception — those are Ogg; see below.) **Never use it in all caps**, it's a deliberate design decision.
- **JetBrains Mono** for **every number on screen** — prices, sizes, PnL, % change, timestamps, hashes, addresses. Always `font-variant-numeric: tabular-nums slashed-zero` — **tabular figures and slashed zeros are the rule, not the exception** (GTE never shows a plain `0` in mono). The one carve-out: **input fields stay Inter** even for numbers (see Inputs) — mono kicks in once the value is displayed. **Never use mono for text strings that aren't numbers or clear data**.
- **Ogg Text Light** is the **marketing headline typeface** — every marketing / editorial headline is set in it (the full headline, weight 300, one colour; see `references/marketing.md`). It also covers rare section display type, infographics, social assets, and posters. Never a UI label, never body, never product chrome. Deliberate, editorial use only.
- Type scale is compact and functional. The dominant body sizes in the trading app are `.p3` and `.mono-3` (numbers). `.h1` / `.h2` are reserved for hero / landing / empty-state moments — never product chrome.
- **The scale is density-tiered — sizes are NOT fixed.** `gte-web` runs a denser baseline below the `widescreen` breakpoint (1512 px) and the full Supernova "Desktop" snapshot at 1512 px and up. Most screens render the baseline tier, so **design dense by default**:

  | Class | Baseline (< 1512 px) — default | Widescreen (≥ 1512 px) |
  |---|---|---|
  | `.p3` / `.mono-3` (body) | **11 px** | 12 px |
  | `.p2` / `.mono-2` | 13 / 14 px | 14 / 15 px |
  | `.mono-1` (big numbers) | 18 px | 20 px |
  | `.mono-4` | 10 px | 11 px |
  | `.h1` | 42 px | 48 px |
  | `.h2` | 32 px | 36 px |

  The `.h*`/`.p*`/`.mono*`/`.btn*` classes in `colors_and_type.css` consume density variables, so a surface responds to the tier automatically. If you reach for 15 px body, you've drifted off-system — use 11 px.
- All four `.mono-*` sizes share **one 16 px line-height**. So `.mono-1` (18–20 px) is intentionally tighter than its font-size — for single-line big-number readouts (price headers, PnL). Don't use `.mono-1` for wrapping text; it will clip.
- Tracking is **tight** on headings and **slightly open** on body (+0.04 em on `.p3`). Intentional — reads like a broadcast ticker.

### Spacing, radii, corners

- Spacing is a 4-px scale: `4 / 8 / 12 / 16 / 24 / 32 / 48`. Trading panels cling to `4` and `8`.
- Corner radii: `4` (small — chips, mono-badges), `8` (buttons, inputs, cards — the default), `12` (complementary), `16` (large — modal corners). The product never uses pill shapes or hard 0-radius corners except on tables.

### Backgrounds, textures

- Product UI: **No photography, no illustrations, no gradients on surfaces.** The background is flat near-black, full stop.
- Marketing assets, posters, social media assets: **occasional** photography backgrounds using the curated images in the brand-images folder. The installable skill includes only photos used by its locked previews; use the canonical brand library when a broader selection becomes available. (No slanted hairline-grid backgrounds — see Axial tilt; that motif is retired from marketing.)
- Occasional **soft vertical gradients** appear behind tinted-state surfaces (positive / negative / brand) — always 15 % → 0 % top-to-bottom, never corner-to-corner.

### Axial tilt — the 23.43° system

GTE's signature geometry is a **23.43° slant** — the axial tilt of the Earth, and the angle of the GTE wordmark. It is a real, formalized part of the system, not decoration. Treat it as the one place GTE allows a non-orthogonal line.

**The angle is always exactly `23.43°`** (`--axial-tilt`). Never approximate it, never use a different tilt elsewhere. One angle, one meaning.

**Where it's allowed:**
- **Active-state indicators** in product chrome — the active tab / sidebar selection marker is a slanted edge. The slant offset is **derived from the element height, never hand-tuned**: `--tab-slant-px = --tab-bar-h × tan(23.43°)` (13.87 px at the 32 px baseline bar, 17.34 px at the 40 px widescreen bar). If the bar height changes, recompute — don't eyeball.
- **Frosted slabs** (marketing / editorial only) — a translucent panel tilted 23.43°, **overlaid on a product UI mockup** in a feature/presentation section (not as a hero copy container): `--surface-elevated-2` at ~8–15% over a darker field, optional `backdrop-filter: blur()`, a 1 px `--stroke-default` edge, corner radius `16 px`. Carries imagery or a single headline; never body copy or data. See `references/marketing.md`.
- **Slanted marketing feature cards & stat dividers** (marketing only) — small feature cards skewed to 23.43° parallelograms (content counter-skewed upright), or 23.43°-slanted 1 px dividers between stats. A cleverer expressive use of the tilt than any background. Never applies to *product* cards. See `references/marketing.md`.

**Retired:** the slanted **marketing grid background** (1 px hairline grid rotated 23.43°) is no longer used. In product, the slant lives solely in the active-tab / sidebar indicator.

**Where it's forbidden:**
- **Never skew type.** Text, labels, and especially numbers always sit upright. The tilt frames content; it never rotates it.
- **Never tilt data.** Charts, tables, order books, prices, PnL — all strictly orthogonal. The 23.43° motif lives in chrome and marketing, never in the data layer.
- **Never tilt product cards or panels.** Product surfaces are rectilinear. The slant is reserved for the active-indicator edge and non-product surfaces.
- **Don't stack tilts.** One slanted element per composition. Two competing 23.43° edges read as a mistake, not a motif.

**Scale.** Subtle and structural in product (a single indicator edge). Expressive in marketing (a frosted slab over a UI mockup). When in doubt in product: keep it orthogonal and let the active-indicator edge be the only slant on screen.

### Borders

- **1 px strokes, always**. Never 2 px, never dashed.
- Cards are **borderless by default** (separation comes from the brightness step + a subtle `shadow-sm`). A 1 px `--stroke-subtle` border is **opt-in** for cases that need a crisper edge — see the Cards section.
- Inputs use a slightly warmer inner surface (`rgba(255,255,255,0.06)`) with no border until hover, and a stronger stroke in focus state.

### Shadows

- UI is mostly **flat**. Shadows appear on floating elements only: overlays, dropdowns, toasts.
- Primary / positive / negative buttons get a **colored outer glow** — `0 2px 12px` in the button's own accent color at 40 % opacity. This is the only place color "bleeds".
- Overlay shadows are `0 16px 48px rgba(0,0,0,0.6)` + a 1 px stroke ring — hard-edged, dramatic, consistent with the dark background.

### Animation

- **Fast & functional**. All transitions are `200ms ease-out`. Nothing bounces, nothing lingers.
- Numeric fields flash briefly on value change (`alpha-flash` keyframe — surface-elevated-2 → transparent over 1.5 s). This is the signature motion moment.
- Hover on primary/positive/negative buttons: `filter: brightness(120%)`. Hover on ghost/tertiary: background fill darkens to `rgba(255,255,255,0.15)`.
- Press state: no scale, no shrink — just held `brightness(120%)` (primary) or held hover background (secondary).
- Collapsible content uses 300 ms ease-out height transitions. No other content motion.

### Transparency / blur

- Selective. Muted action surfaces use 15 % color tints over the dark background — this is the pattern, not `backdrop-filter`. True glass/blur effects are rare.
- Overlays sit on a flat `var(--surface-overlay)` (`#181A1B`), not a blurred app behind them.

### Layout rules

- The trading app is **viewport-locked** — no page scroll on the main screen. Internal panels scroll independently.
- Header is fixed at 48 px (`--header-height`), sidebar at 80 px (`--sidebar-width`), footer at 56 px. Banner (announcements, maintenance) is 28 px when present.
- Gutters between panels are 4 px (`--space-xs`). The outer app has 4 px padding. Density first, breathing room never.
- Responsive breakpoints are mobile-first: `480 / 768 / 1024 / 1280 / 1512`. The trading terminal collapses to stacked panels below 768 px.

### Cards

Matches the `Card` primitive in `gte-web` (`src/ui/card/card.tsx`):

- `background: var(--surface-elevated-2)` (`#181A1B`) — the canvas is `--surface-elevated-1`, so a card steps **up** to `--surface-elevated-2` to stand out. Surfaces nested *inside* a card step further again (a hairline `--stroke-default` divider, or `--surface-elevated-3`).
- `border-radius: 8px` (`--radius-regular`); `12px` (`--radius-complementary`) for larger composite panels, `16px` for modals.
- **Borderless by default**, with a subtle `shadow-sm`. Add `border: 1px solid var(--stroke-subtle)` **only when opt-in crispness is needed** (the primitive exposes this as a `border` variant). Never `--stroke-default` for a card edge — that's for internal dividers.
- Standard padding is `16px` (`p-4`) on header / content / footer.

## Content Fundamentals

**Voice.** Terse, operator-grade, quant-adjacent. GTE addresses users as professionals doing a job, not customers to be charmed. Copy reads like a trading desk Slack channel — short, confident, no exclamation marks.

- **Sentence case everywhere** — button labels, headers, tooltips, and badges/pills (`"Long"`, `"Short"`, `"Cross"`, `"Reduce only"`). There is **no forced-uppercase rule**; reserve all-caps for genuine acronyms that are already uppercase (`"GTC"`, `"IOC"`, `"PnL"`, `"OI"`).
- **No emoji.** Ever. Brand-incompatible.
- **Numbers do the talking.** Microcopy is support for numeric content; it should not overshadow it. Prefer `"Filled at $43,218.50"` over `"Your order filled successfully."`
- **Second person, sparingly.** "You" appears in onboarding / empty states. In-product live surfaces drop pronouns entirely: `"Position closed."` not `"Your position was closed."`
- **Active, present tense.** `"Placing order"` loading state. `"Order placed"` confirmation. `"Order failed — insufficient margin"` on error.
- **Abbreviations are welcome.** `"PnL"`, `"OI"`, `"FR"`, `"Lev"`, `"Liq."`, `"P&L"` are legible to the audience. Don't over-explain.
- **No hedge words.** Never `"approximately"`, `"about"`, `"around"`. Commit to a number or show a `~` character.
- **Error copy is specific.** `"Insufficient USDC for margin (need 24.50 USDC, have 12.30)"` — never `"Something went wrong."`

**Example phrases from the product** (tone reference):
- `"Markets"`, `"Portfolio"`, `"Faucet"`, `"Trade"`
- `"Place order"`, `"Close position"`, `"Set leverage"`
- `"Long BTC-USD"`, `"Short ETH-USD"`, `"IOC"`, `"GTC"`, `"Reduce only"`
- `"Margin mode"`, `"Cross"`, `"Isolated"`
- `"Funding rate"`, `"Mark price"`, `"Index price"`, `"Open interest"`

## Iconography

GTE uses **three icon sources**, in this order:

1. **Custom SVG components** in `gte-web/src/assets/*-icon.tsx` — the brand-specific ones: `sparkle-icon` (the Economic Agent sparkle), `bolt-icon` (speed / Turbo chain), `qr-icon`, `wallet-icon`, `polymarket-logo`, `x-twitter-logo`, `star-filled` / `star-empty` (favorites), `toast-error/success/loading-icon`, and a full set of arrow / chevron / bank / card / card / mint / profit / loss marks. **These are the first choice** — they match GTE's stroke weight and optical grid.
2. **Lucide React** (`lucide-react@0.562.0`) — the baseline icon set, matched via the Lucide CDN in our previews. Use when no brand-specific SVG exists. Stroke width `1.5` (default).
3. **Radix Icons** (`@radix-ui/react-icons`) — niche UI primitives only (chevron-right, chevron-down, etc.). Avoid for anything expressive.

**Rules:**
- Default icon size: **16 px** (`--dimension-size-icon-default`). Larger sizes jump to `20 px` (toolbar) or `24 px` (hero).
- Stroke icons, never filled — except for `star-filled` (favorite-on), `sparkle-icon` (agent), and semantic states.
- Icon color tracks text color via `currentColor`. No hardcoded icon hex values.
- **No emoji, no unicode-as-icon** (don't use `★`, `➕`, arrows-as-chars). Even in terminal/mono contexts, use a proper SVG.

**Logo assets** (in `assets/logos/`):
- `gte-logo-white.svg` — primary wordmark, pure white. Use on dark (the default product surface), ~56 × 20 px in headers.
- `gte-logo-black.svg` — same wordmark in black, for light/marketing surfaces only.
- `turbo-logo-white.svg` / `turbo-logo-black.svg` — Turbo chain mark (GTE's L1), white on dark / black on light.

## UI Kits

| Product | Path | Status |
|---|---|---|
| **Web trading terminal** | `ui_kits/web/` | Perps trade view (chart + book + form + positions) — reproduced from `gte-web` `features/trading/*`. |

Mobile and marketing kits are stubbed; they would be next if prioritized.

## Known substitutions / caveats

- **Inter** is loaded from Google Fonts; the Figma file references `Suisse Intl Trial` and `PP Supply Mono` for earlier drafts but the production codebase standardized on Inter + JetBrains Mono (per `fonts.ts`). I followed the codebase.
- `Martian Mono` shows high usage in Figma but is **not** in the production app. It appears to be a pre-production choice that was replaced by JetBrains Mono. Not included.
- `Ogg Text Light` is included (user provided) but has essentially no in-app usage (3 instances in Figma). It's preserved for marketing / editorial moments.
- `Eurostile Extd Black Italic` and `Cutive Mono` / `Courier Prime` / `Manrope` have trace usage in Figma — treated as experimental and not included.
