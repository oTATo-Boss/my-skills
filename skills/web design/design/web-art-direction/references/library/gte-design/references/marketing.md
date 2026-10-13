> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# GTE Marketing / Non-Product Layer

The marketing layer is the **non-product tier** — landing pages, sections, slides/decks,
infographics, social/OG cards, posters, press kits. It inherits GTE's whole visual grammar
(tokens, palette, the 23.43° motif, no-emoji/no-decoration prohibitions) but relaxes a few
things product never allows: **light theme is permitted** (`data-theme="light"`), type runs
**bigger**, spacing is **generous**, and **large (40px) buttons are allowed**.

Everything else from `foundations.md` still binds. This file is the authoritative source for the
marketing-only rules; where it conflicts with older prose elsewhere, this file wins.

**Reuse first, here too.** Marketing surfaces are still built out of the locked atoms —
copy the buttons/inputs/badges/cards from `preview/*.html`, don't draw bespoke ones. The two
locked hero templates are the copy-sources for landing tops:

| Surface | Copy from | Theme |
|---|---|---|
| Landing hero — image-led (brand photo full-bleed, copy on scrim) | `preview/landing-hero.html` | dark |
| Landing hero — light editorial (two-column, framed image) | `preview/landing-hero-light.html` | light |

---

## Format coverage

Every marketing format obeys the rules in this file (heading system, mono = numbers, reuse the
locked buttons, one slant, PNG logos). What differs per format is dimensions and delivery. Status:

| Format | Status | Notes |
|---|---|---|
| **Landing page / section** | ✅ Built | `preview/landing-hero.html` (dark, image-led), `landing-hero-light.html` (light, editorial), `landing-feature.html` (UI mockup + frosted slab). Copy these. |
| **Press kit / poster** | ◐ Rules only | Image-led, editorial Ogg display type — follow the heading + image rules below; no fixed template. |
| **Social post / OG card** | ☐ Reserved | Routing destination only — **no template built yet**. Build from the rules here at the platform's pixel size (e.g. OG = 1200×630). Aesthetic specs (safe margins, logo lockup, single-headline vs stat) need Arnie's vet before locking — treat like an unvetted draft. |
| **Newsletter / email** | ☐ Not covered | **Needs a brief before building.** Email is not free-form HTML: most clients want table-based layout + inline styles, don't honor `backdrop-filter`/custom webfonts reliably (so the Ogg emphasis and slab may not survive — fallbacks required), and dark-mode handling varies. Don't reuse a landing snippet as-is. Ask Arnie for target clients + whether it's image-led or live-text. |
| **Slide / deck** | ☐ Reserved | Routing destination only — not yet built. Inherits the heading + button rules; 16:9 canvas. |

> **Do not silently invent** a social/newsletter/slide template and present it as canonical. These
> are reserved routes: build to the shared rules, label the output a draft, and flag the
> format-specific choices for review — the landing layer was locked one vetted file at a time and
> these will be too.

---

## Light vs dark — choose the theme by message

Product is always dark. **Marketing chooses its theme by what the section is saying:**

- **Dark is for the genuinely technical.** Only **agentic / API / developer / protocol** and
  heavy data messaging is *definitely* dark. That's the bar — reserve dark for it.
- **Everything softer can be light — including most "trading" copy.** General trading is **not**
  automatically technical: "Long or short, in two clicks" is a human, approachable message and
  reads better **light**. Brand, lifestyle, onboarding, "why GTE", and plain-language product
  benefits → light. When unsure whether a section is "technical enough" for dark, it usually
  isn't — default it to light and lean brighter.
- **A technically-loaded page can — and should — be all-dark.** *GTE for Developers*, the
  *Agentic API* page, protocol/docs landings: keep them fully dark, end to end.
- **A broad conversion page mixes — and can lean bright.** Dark for the agentic/API/performance
  chapters; light for trading, brand, and onboarding. An all-dark broad page reads as a dev tool,
  not a product for people — err toward more light.
- **Product UI stays dark inside light sections.** A light section may still show a dark product
  mockup (trade panel, order book) — wrap it in a `.dark-scope` (see *Real product UI* below) so
  the surface keeps dark tokens. Marketing chrome (cards, dividers, type) follows the section theme.
- Scope `data-theme="light"` per `<section>` to mix themes within one page; light sections then
  follow the light-mode rules below (canvas = `elevated-1`, flipped button borders, framed
  images).

## Layout & spacing — one system, applied everywhere

Pick a **single content-inset system** and use it for every section — mismatched side padding
section-to-section is the fastest way to make a page look amateur.

- **One shared container.** Define a single `.wrap` (e.g. `max-width: var(--page-max); margin: 0
  auto; padding: 0 56px`) and put **every** section's content in it. Every heading, paragraph, and
  card then shares the exact same left/right edge down the whole page.
- **Content width scales with the density tiers.** `1200px` is right for sub-1512px screens, but
  it looks cramped on the Supernova tier — widen it at the breakpoint: `--page-max: 1200px;` then
  `@media (min-width: 1512px){ :root{ --page-max: 1400px } }`. (Same 1512px breakpoint the product
  type scale uses.)
- **Full-bleed backgrounds, inset content.** Bands that span edge-to-edge (hero image, ticker
  strip, stats band, closing image, footer) still put their *inner content* inside the same
  `.wrap` — the background bleeds, the content aligns. Never give a section its own ad-hoc
  left padding.
- **Watch flex/grid children.** A `.wrap` placed inside a `display:flex` parent needs
  `width:100%` or it collapses to content width and stops aligning (a real bug we hit — the
  hero copy drifted off the shared inset until the wrap was forced full-width).
- **One vertical rhythm too.** Standardise section padding (e.g. `padding: 112px 0`) rather
  than hand-tuning each block.

## The heading system

Marketing headlines are set entirely in **Ogg Text Light** (`--font-display`, weight 300) —
the whole headline, one typeface.

> *Superseded:* the earlier **Inter-base + Ogg-emphasis** mix is retired — mixing the two
> within a single headline read as off. Headlines are now **all-Ogg**. (So the old "Inter & Ogg
> share a line" rule no longer applies — there is only Ogg.)

- **Ogg Text Light, weight 300, for the full headline.** No Inter inside a headline, no
  two-typeface emphasis. The voice comes from Ogg itself.
- **ONE colour only.** All white on dark, near-black on light. Never two colours, never an
  orange accent word — orange is the primary CTA, never type.
- **Tracking slightly tight** (`letter-spacing: -.01em`), line-height ~1.05–1.12. Ogg is a
  serif display face — give it room; don't pack the lines.
- **Everything else stays Inter.** Eyebrows, kickers, labels, sub-copy, body — all Inter. Ogg
  is editorial display only (headlines, rare section display type), never a UI label or body.
- **Mono is still numbers only** (see below) — never a headline.

```html
<h1 class="headline">Trade perps at terminal speed.</h1>
<!-- .headline { font-family: var(--font-display); font-weight: 300; letter-spacing: -.01em; line-height: 1.08; } -->
```

## Imagery — lifestyle vs technical

The brand photo library splits two ways; match the photo to the section's job:

- **Lifestyle / human photography** (people, places, everyday moments — the bundled examples are
  `gte_-06` and `gte_-09`) → **generic GTE brand sections, human messaging, light sections.**
  This is the default for brand storytelling — it makes GTE feel like a product for people.
- **Cosmic / abstract / speed photography** (Earth + order-flow rings, warp streaks, techwear
  figures — the bundled examples are `gte_-04` and `gte_-12`) → **technically-loaded pages and the
  technical/agentic/performance chapters.** Powerful, but easy to overuse: if every section is
  an abstract light-streak (or a globe), the page reads cold and "too techy."
- **Lead a broad conversion page with human/lifestyle — not a globe.** The homepage hero should
  put people front and centre; save the Earth/warp/abstract shots for a *GTE for Developers* /
  *Agentic API* hero or an interior technical chapter.
- **Show substance with product-UI, not more photos.** Below the hero, prove the product with
  **real UI mockups** — trade panel / order ticket, positions table (semantic Long/Short + green/red
  PnL), order book, agent console. Reuse the atoms (`order-form.html`, `table.html`, `orderbook.html`).
  Don't stack lifestyle photos section after section; keep lifestyle to the hero + roughly one human
  "why us" moment, and let product screenshots do the rest.
- **Rule of thumb:** human/lifestyle to lead and to humanise; product-UI to prove; abstract/cosmic
  for the technical chapters only.

## Foundational rules still apply

Marketing relaxes scale and theme — it does **not** relax the core grammar:

- **Mono is for numbers only.** Eyebrows, labels, and kickers are **Inter**, not mono. Don't
  set a tagline or eyebrow in JetBrains Mono for "techy" flavour.
- **No random embellishments.** No decorative slashes, no ornamental glyphs, no emoji, no
  gradient decoration on surfaces. Every mark earns its place.
- **Reuse the locked buttons — never bespoke.** CTAs use the real primary/ghost/tertiary
  classes and adapt to light tokens automatically.

## Buttons vs links — where each belongs

Marketing uses buttons **sparingly**. Actual `<button>`-style CTAs appear in only three places:
the **hero**, the **final CTA band**, and the **nav**. Everywhere else — every feature/content
section — the call to action is a **text link**, not a button.

**Buttons (hero / final CTA / nav only):**
- **Large (40px) is allowed here** — and only here. Product UI caps at medium (32px).
- **The secondary button pairs by surface:** on a **plain/solid** background pair primary with
  **tertiary**; on a **photo / image background** pair primary with a **ghost** button — tertiary's
  translucent fill reads as a muddy grey box over imagery, ghost (text-only) stays clean.
- **The nav button is always PRIMARY** (e.g. "Launch app"), never tertiary/ghost — it's the one
  persistent conversion affordance.
- **The primary CTA is ONE button — same copy and same size everywhere it appears.** The nav,
  hero, and final-CTA primary buttons are the *same* action, so they read identically: same label
  ("Launch app") and same size. Don't shrink the nav one or reword the hero one — a primary that
  says "Launch app" in the nav and "Start trading" in the hero looks like two different buttons.
- **Never put an icon on a primary button.** Primary CTAs are text-only. (Icons are fine on
  badges, links, list items — just not the primary button.)
- Primary stays **orange** in both themes.

**Links (every feature / content section):**
- **Never use buttons inside feature sections — use text links.** Primary link = **orange**
  (`--accent-light`), e.g. "Open a position →" (a trailing arrow is fine on a link). Secondary
  link = **text-mid**, e.g. "See the markets". Weight 500, ~14px.
- This keeps buttons meaningful: when everything is a button, nothing is. Sections invite; the
  hero/CTA/nav convert.

## Logo

- **Default to the PNG, not the SVG.** Use `assets/logos/gte-logo-white.png` on dark,
  `gte-logo-black.png` on light. The SVG renders "off" in some contexts; PNG is the safe choice.

## The 23.43° motif in marketing

- **The slanted-grid background is KILLED.** Do **not** put 23.43°-rotated hairline grids
  behind marketing content. (This reverses the old README "marketing grid rotated 23.43°"
  line — that rule is retired.) The 23.43° motif now lives only in **product chrome**
  (active tab / sidebar indicator) and the **frosted slab** below.
- **Frosted 23.43° slab — over a UI mockup only.** The translucent tilted panel belongs
  **overlaid on a product UI mockup in a feature/presentation section** — never as a hero
  copy container, never carrying body copy or data. For an image-led hero, copy sits
  **directly on a scrim**, no slab. Slab spec: `--surface-elevated-2` at ~8–15% over a darker
  field, optional `backdrop-filter: blur()`, 1px `--stroke-default` edge, 16px radius.
- **Slanted feature cards — in both dark and light.** A cleverer use of the tilt than a
  background: skew a row of small feature cards to 23.43° parallelograms. `transform:
  skewX(-23.43deg)` on the card, `transform: skewX(23.43deg)` on each direct child to keep content
  upright. Parallel cards keep their gaps; the outer corners lean into the section inset (keep card
  height modest so the overhang stays within the inset). Apply it to **every** feature-card row,
  dark or light — not just one. On **light** sections, use a **very subtle** drop shadow
  (`~0 6px 20px rgba(1,3,4,.05)`) — the heavy dark-mode shadow reads as a dirty smudge on light.
- **Slanted stat dividers.** In a stats band, divide the numbers with a **23.43°-skewed 1px
  stroke** (`transform: skewX(-23.43deg)` on a thin divider pseudo-element) instead of a plain
  vertical rule — small touch, on-motif.
- **One slant per composition.** Don't stack competing tilts in a single section — a slab *or*
  slanted cards *or* slanted dividers, not several at once.

## Real product UI in a marketing surface

When a section needs to show the actual product (a trade panel, positions, an order book, a
chart):

1. **Reuse the prebuilt Product components first.** Copy the matching `preview/*.html`
   snippet or follow the `references/components.md` skeleton — `order-form.html` (trade panel),
   `table.html` (positions), `orderbook.html`, etc. Do **not** hand-draw a surface that already
   exists.
2. **Only build a new surface if none exists** — and then build it strictly from the **atomic
   components** in the UI kit (button, input, segmented, badge, table row, card…), matching their
   exact tokens. A hand-built surface that drifts from the atoms (e.g. Long/Short badges with a
   full-bright stroke instead of the canonical `--positive-muted`/`--negative-muted` border) is a bug.
3. **Product stays dark, even inside a light section.** Product UI is dark-only. To place a dark
   mockup on a light marketing section, wrap it in a scope that re-asserts the dark tokens (a
   `.dark-scope` that resets `--surface-*`, `--text-*`, `--stroke-*` to their dark values) so the
   surface doesn't flip to light. The mockup then reads as a dark product screenshot floating on
   the light section — exactly how a framed dark photo sits on a light hero.

## Bands: stats & tickers

- **Never place a stats band and a ticker strip adjacent.** Two dense number-strips stacked
  together read as clutter. Give stats its **own section** further down the page, with room to
  breathe; keep the ticker near the top as a thin strip. One dense numeric band per region.
- **Stats band = lively, not a bare row.** Big mono numbers (slashed-zero) with the **unit** in
  `--text-accent` (the one restrained orange touch — adaptive, so it stays legible if the band is
  ever light), and **23.43°-slanted dividers** between cells (see the slant section). It's a proof
  moment — let it feel confident.
- **Don't use the extra-black `--surface-default` for dark bands on a MIXED page.** On a page that
  mixes light and dark, dark bands (stats, ticker, footer) sit on `--surface-elevated-1` (the dark
  canvas), *not* `--surface-default` (`#010304`) — the near-pure-black slab reads as an ugly hole
  next to the light sections. `--surface-default` as a section background is reserved for
  **dark-theme-only** landings, where a deeper floor adds depth. (It's still fine everywhere for
  hairline separators/scrims.)
- **Ticker strip = multi-asset + alive.** If you show a live ticker, don't make it crypto-only —
  mix **crypto, major tech stocks, indices, and commodities** (BTC, ETH · NVDA, AAPL, TSLA · SPX,
  NDX · XAU, WTI). Give it a **slow sideways marquee** (duplicate the set, `translateX(0 → -50%)`,
  ~60–75s linear infinite; pause on hover) and a **subtle live pulse** on a few cells. Mono
  prices, green/red change, tabular + slashed-zero.

## Light mode (marketing only)

Light theme is opt-in via `data-theme="light"` on the root or a scoped `<section>`, and is
reserved for non-product work. A few adjustments that make it read right:

- **Canvas = one level darker than the lightest.** Use `--surface-elevated-1` (a soft grey),
  **not** `--surface-default` (`#fafafa`, stark white). The page should feel like a soft grey
  field, not paper.
- **Orange TEXT must darken on light.** The bright `--accent-light` (orange-400) is an orange for
  *dark* backgrounds — on the light grey canvas it has almost no contrast. Use the **`--text-accent`**
  token for any orange text (links, accent numerals): it's orange-400 on dark and **orange-1000**
  (`rgb(189,79,0)`) under `data-theme="light"`. This applies to text only — orange **fills** (the
  primary button) keep the standard orange, since white text on the fill carries the contrast.
- **Flip the button border gradient to `to top`.** In light mode the masked border gradient
  runs `to top` (dark edge at the bottom) so buttons read **raised**, not inset. Dark mode
  keeps `to bottom`. (See the `.btn::before` rule in `landing-hero-light.html`.)
- Brand photos are dark/moody, so on a light page they sit in a **contained rounded frame**
  (border `stroke-subtle`, soft shadow), not full-bleed.

## Hero patterns (the two locked templates)

- **Dark, image-led** (`preview/landing-hero.html`): brand photo full-bleed, a left-weighted
  linear scrim for legibility, copy directly on the scrim. Heading block inset **~116px** from
  the left. CTAs primary + tertiary `lg`.
- **Light, editorial** (`preview/landing-hero-light.html`): two-column grid, airy copy left,
  brand image in a contained rounded frame right, black PNG logo. Same heading system, same
  button pairing.

Brand imagery: the curated orange motion-streak and lifestyle photography in
`assets/brand-images/`. These are the four files used by the locked previews, not the full source
photo library. Pick frames where a dark region gives the scrim/copy room to breathe.

## Review workflow (important)

The `preview/*.html` files `<link>` `../colors_and_type.css`, which **doesn't resolve in the
Launch preview pane**. To review a marketing file, build a **self-contained `*-review.html`**
in `scratchpad/gte-design-workspace/`:

1. Inline `colors_and_type.css` into a `<style>` block.
2. Base64-embed **both** fonts (JetBrains Mono + OggText — Ogg is needed for the heading
   emphasis) as `@font-face` data-URIs.
3. Base64-embed any brand image and PNG logo the file references.
4. `open` the result.

(Reuse the python inliner pattern from the kit-lock sessions.) Always review at the target
viewport (heroes are ~1440px wide).
