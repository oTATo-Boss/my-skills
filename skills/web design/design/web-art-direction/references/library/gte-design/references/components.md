> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# GTE Component Reference — structural ground truth

These are the **real** primitives from `gte-web` (`src/ui/*`, `src/features/trading/*`),
distilled to structure + states + tokens + proportions.

> **You do not need the `gte-web` repo to use this file.** The `src/...` paths in each
> heading are provenance — where the primitive came from — and a jump-to target *if* that repo
> happens to be checked out in your session. The structure, states, tokens, and proportions are
> fully captured here and in the `preview/*.html` snippets, so this skill works standalone
> (cloud sessions, artifacts, offline mocks). Only import from `src/...` when you're actually
> editing `gte-web`; otherwise copy the matching `preview/*.html` snippet.

**Reuse before you read this.** For an HTML mock, first copy the matching
`preview/*.html` snippet (button, input, segmented, badge, card, order book,
toast, controls, price-change) — see the copy-source table in `guide.md`. For
production code, import the real component named in each section below. This
file is for the cases reuse doesn't cover: **composite surfaces** with no static
snippet (order form, positions panel, ticker, header) and **hand-building novel
surfaces** — reproduce these skeletons rather than improvising, and build them
out of the atomic snippet classes so the small pieces stay identical. Prose
rules (README) constrain palette and prohibitions; **this file constrains the
skeleton.**

Conventions:
- Token names below are the `colors_and_type.css` variables (e.g. `--surface-elevated-2`). In repo Tailwind they appear as `bg-surface-color-surface-elevated-2`, `text-text-color-text-high`, etc. — same value.
- Sizes use the 4px spacing scale; `p-4` = 16px, `gap-2` = 8px, `py-0.5` = 2px.
- "typography-*" = the `.h*`/`.p*`/`.mono*`/`.btn*` classes (density-tiered).

---

## ✅ Locked canonical atoms — copy these, don't redraw

The six core atoms are **vetted and locked**. For an HTML mock, copy the matching
`preview/*.html` snippet verbatim (it links `colors_and_type.css`, so tokens + the
**self-hosted font** come for free). For production, import the named `src/ui` component.
These rules are authoritative — they override any older prose lower in this file.

| Atom | Copy from | Locked rules (what makes it right) |
|---|---|---|
| **Button** | `preview/buttons.html` | primary/positive/negative = 65° gradient fill + **text-high** + subtle `stroke-subtle` border + colored glow. secondary/tertiary = **masked gradient border** (accent-muted→0 / stroke-default→0). ghost = no border/shadow, **hover is text-only (no fill)**. Type **button-1** (Inter 500 / 13px / **+0.26 tracking** / lh 100%). Focus = **1px** offset ring. Sizes sm 28 / md 32 / lg 40 — **product UI never uses larger than `medium` (32px)**; `large` (40px) is for marketing/landing only. Submit/CTA buttons in the product are medium. **Icon buttons are not a separate type** — any variant, square (h-7/h-8), 16px glyph, `aria-label`; all variant+state rules inherited. |
| **Input** | `preview/inputs.html` | h-8, radius 8, `surface-input`, **always Inter** (`paragraph-2`, **+0.28 tracking**) — the *one exception* to "numbers are mono". Border transparent → hover `stroke-subtle` → focus `stroke-strong` → error `stroke-negative-muted`. Placeholder `text-low` → `text-mid` on hover/focus. Left-aligned; numeric variant has **no** special surface/align. |
| **Segmented** | `preview/segmented-buttons.html` | toggle-group. Track `surface-input`, **0 inset**. Inactive = default-input look (`text-low` → `text-mid` on hover; **a selected item never changes on hover**). Active neutral = **tertiary-button** look (white-6 + gradient border) + **text-high, no orange**. Active long/short = **secondary-button** look in positive/negative hues. **Use for filtering data / switching modes only — never section nav or order types (those are tabs).** |
| **Badge** | `preview/badges.html` | Border-only, never filled. **Small is the default**; medium only with breathing room (tables, landing/marketing). **Normal/sentence case** (caps only for acronyms). **Never standalone — always inline** (count on a tab, direction/leverage tag in a row). **Direction = semantic**: Long/Buy → positive, Short/Sell → negative (never grey). **Count badge** = square 20×20 mono slashed-zero (square ≤99). Height is line-height-driven (`paragraph-3`, lh 140%). |
| **Controls** | `preview/controls.html` | checkbox size-4 (masked gradient border off → gradient fill + check on). radio outer 24 / dot 12. switch — **kit update**: 16px tall (matches checkbox) + **green-600 on-track + green glow** (diverges from app `h-3 w-6`). |
| **Tabs** | `preview/tabs.html` | One slanted **23.43°** HeaderTab type (section/view nav with count badges AND order type). Height `var(--tab-bar-h)` (32/40), slant `var(--tab-slant-px)`. Active = **flat `surface-elevated-2`** parallelogram (clip-path, drawn behind the label so padding isn't eaten); active section-tab count flips to accent. **Tabs switch sections/views; segmented = filter/mode.** The bar sits **above** the block glued to its top edge with **no fill** (global bg shows behind inactive tabs); active tab flush to the left edge. The block body is a vertical **`elevated-2 → elevated-1` gradient** so the active tab merges in; **the block is not rounded** (unlike Card). |
| **Table** | `preview/table.html` | Header `thead` bg `surface-elevated-2`, `h-8`, `th` = paragraph-3 (12px) **text-low → text-mid on hover**, font-normal, left-aligned, **sort chevrons hidden until header hover**. Rows `border-b stroke-default`, ~38px (`py-[6.5px] px-4`), hover `surface-action-tertiary`, selected `surface-elevated-1`. Numbers mono (tabular + slashed-zero), value `text-high`, **units/secondary `text-low`**. Asset cell = side-colored left edge + fade (green long / red short) + avatar + mono symbol + leverage badge; PnL green/red by sign. **Row buttons are always tertiary.** |
| **Dropdown / select** | `preview/dropdown.html` | Trigger matches the **input field** states (surface-input bg, border transparent → `stroke-subtle` hover → `stroke-strong` open) + a ChevronDown (rotates when open). Panel = `surface-overlay` (#181a1b), `rounded-md` (6px), overlay shadow + 1px ring, py-2. Rows `px-3 py-1`, hover `surface-action-tertiary-hover`; selected = `text-high` (+ accent check), others `text-mid → text-high`; optional `text-low` group label. |
| **Tooltip** | `preview/tooltip.html` | Dark bubble: bg `--color-tooltip` (black-800 / #181a1b), `text-high`, paragraph-3 (12px), `rounded-md` (6px), `px-3 py-2`, max-width 270px, strong shadow, rotated-square arrow. Product trigger pattern = dotted underline under the term. |
| **Slider** | `preview/slider.html` | 4px `surface-input` track; range fill = **grey→white gradient** (`white-800 → white-200`), not orange; 12px white thumb with drop shadow, **ring (4px stroke-subtle) only on hover/focus**; marks below in `text-low`, **evenly spaced** (discrete leverage stops, not linear by value). Leverage variant may recolor range/thumb to the active side. |
| **Card** | `preview/cards.html` | **default bg = `surface-elevated-2`** to stand out from the elevated-1 canvas (diverges from repo `elevated-1`). radius 8, `shadow-sm`, border **opt-in** (`stroke-subtle`), p-4. Header = button-1, body = paragraph-3 (lh 140%). Nested surfaces step further. |

Cross-cutting rules these encode:
- **Mono = tabular-nums + slashed-zero, and the font MUST be self-hosted** (bundled `fonts/` via the `@font-face` in `colors_and_type.css`; embed base64 in a standalone mock). Google Fonts strips the `zero` feature → no slashed zeros.
- **Each type style owns its line-height** — button-1 = 100% (fixed-height controls), paragraph-2 = 160%, paragraph-3 = 140%. Content-sized elements (badges, card body) MUST carry the real line-height or they collapse.
- Encode **rules + representative examples**, not exhaustive matrices.

> Three of these intentionally **diverge from the current app** (ghost hover text-only, switch size+glow, card elevated-2). They're flagged in each snippet and tracked in `KIT-SYNC-NOTES.md` for syncing at source.

---

## Button — `src/ui/button/button.tsx`, `src/shared/styles/button.css`

The most load-bearing primitive. Six variants, gradient fill, colored glow.

**Skeleton**
```html
<button type="button" data-slot="button"
        class="button-base button-{variant} {size} {state}">
  {icon?}{label}
</button>
```

**Variants** (`variant`): `primary` · `secondary` · `tertiary` · `ghost` · `positive` · `negative`
**Sizes** (`size`): `small` (h-7, px-3) · `medium` (h-8, px-4) · `large` (h-10, px-4) · `iconSmall` (h-7 w-7) · `iconMedium` (h-8 w-8)
Modifiers: `active` (held brightness), `disableHoverBg`, `block` (w-full).

**Shared base:** `inline-flex items-center justify-center gap-2 rounded-lg cursor-pointer`, `typography-button-1`, gradient fill `linear-gradient(65deg, …)`, a 1px gradient border via pseudo-element, `disabled:opacity-50 disabled:pointer-events-none`. SVG icons default to `size-4` (16px).

**Per-variant tokens**
| Variant | Fill (from → to) | Text | Glow / ring |
|---|---|---|---|
| primary | `--surface-action-primary` → `-primary-hover` | `--text-action-primary` (near-black) | `0 2px 12px --orange-40`, ring `--accent` |
| secondary | `--surface-action-secondary` (orange-15) | `--accent-light` | ring `--accent-muted` |
| tertiary | `--surface-action-tertiary` (white-6) | `--text-action-tertiary` (low→mid hover) | ring `--stroke-default` |
| ghost | transparent | inherits | outline-only focus ring, no shadow |
| positive | `--surface-action-positive` (green-1000) | `--text-high` | glow in positive, ring positive |
| negative | `--surface-action-negative` (red-1000) | `--text-high` | glow in negative, ring negative |

**States:** hover = brightness/color shift + shadow grows to 16px; focus-visible = split focus ring, 2px offset; disabled = opacity-50; press = held brightness (no scale). Glow is the **only** place color bleeds outside a shape (README Shadows).

---

## Input / InputNumber — `src/ui/input/input.tsx`, `input-number.tsx`

**Skeleton**
```html
<span class="flex w-full min-w-0 flex-col gap-1">
  <span class="group/input flex items-center rounded-lg transition-all duration-100 {border/bg}">
    <input data-slot="input" class="px-2 min-w-0 flex-1 outline-none typography-paragraph-2" />
    {suffixNode?  <span class="flex shrink-0 items-center px-2">…</span>}
    {switcherNode? <span class="flex shrink-0 items-center px-3">…</span>}
  </span>
  {error? <span class="typography-paragraph-3" style="color:var(--text-negative)">{error}</span>}
</span>
```

**Heights:** `h-8` (32px), `rounded-lg`.
**Surfaces:** normal input = `--surface-input` (white-6); `InputNumber` = `--surface-elevated-2` (solid) or transparent.
**Border states (border starts transparent):** hover → `--stroke-subtle`; focus-within → `--stroke-strong`; error → `--stroke-negative-muted` (overrides). Placeholder `--text-low` → `--text-mid` on hover/focus.
`InputNumber` wraps react-number-format: `allowNegative={false}`, `isAllowed` for min/max, `suffixNode`/`switcherNode` for adjacent controls.

---

## Card / Panel — `src/ui/card/card.tsx`

```html
<div data-slot="card" class="bg-surface-elevated-2 flex flex-col rounded-lg shadow-sm {border?}">
  <div data-slot="card-header"  class="typography-button-1 items-start p-4">…</div>
  <div data-slot="card-content" class="p-4">…</div>
  <div data-slot="card-footer"  class="flex items-center p-4 pt-0">…</div>
</div>
```
Base `--surface-elevated-2` so the card steps up from the `elevated-1` canvas (hard rule; kit decision per `preview/cards.html` — repo `card.tsx` still ships `elevated-1`, sync at source), `rounded-lg` (8px), `shadow-sm`. Border is **opt-in** (`border` variant → `border-stroke-subtle`), not default. Padding `p-4` throughout; footer drops top padding (`pt-0`) to continue from content.

---

## Badge / Pill — `src/ui/badge/badge.tsx`

The direction/type tag (`Long`, `Short`, `Market`, `Limit`, `GTC`, `IOC`) — sentence case, caps only for true acronyms (per Content Fundamentals and `preview/badges.html`). **Border-only, no fill.**

```html
<span data-slot="badge" class="inline-flex items-center justify-center gap-1 w-fit rounded-lg whitespace-nowrap shrink-0 {variant} {size}">{icon? }{label}</span>
```

**Variants:** primary (border `--accent-muted`, text `--accent-light`) · secondary (border `--stroke-subtle`, text `--text-mid`) · positive (border positive-muted, text `--positive`) · negative (border negative-muted, text `--negative`).
**Sizes:** medium = `px-2 py-1 rounded-lg`; small = `px-1 py-0 rounded-sm`. Type = `typography-paragraph-3` (sans). For a **numeric** badge, opt into `typography-mono-3`. Icon `size-3`.

---

## Tabs & the 23.43° slant — `src/ui/tab/tabs.tsx`, `header-tab.tsx`

**Base tabs (`Tabs`/`TabsList`/`TabsTrigger`):** underline tabs. Trigger `typography-button-1`, `border-b p-4`, `text-low` → hover `text-mid` → active `text-high` + `border-stroke-strong`. List is horizontally scrollable (`overflow-x-auto no-scrollbar snap-x`).

**HeaderTab (the slanted product tab):**
```html
<div role="tab" data-state="active|inactive"
     class="typography-paragraph-3 inline-flex items-center gap-2 px-3 py-2 rounded-none
            text-low hover:text-mid
            {active: bg-surface-elevated-2 text-high}"
     style="transform: skewX(-23.43deg)">          <!-- the slant -->
  <span style="transform: skewX(23.43deg)">         <!-- counter-skew keeps content upright -->
    {icon?}{label}
  </span>
</div>
```
The slant is exactly **-23.43°** on the container, counter-skewed on the inner span so text/icons stay upright (see README → Axial tilt). In `TradePanelTabList` an absolutely-positioned indicator (`--surface-elevated-2` + a `rgba(255,255,255,0.06)→transparent` top gradient) is also `skewX(-23.43deg)` and animates `left/width` over 300ms. Focused tab adds `text-shadow: 0 0 6px rgba(255,255,255,0.4)`.

---

## Order Book — `src/features/trading/order-book/components/order-book.tsx`, `order-book-item.tsx`

**Row (`OrderBookItem`):**
```html
<div role="button" class="relative flex grow items-center px-4 py-0.5 cursor-pointer transition-all duration-200 {hover/flash}">
  <div class="absolute top-0 h-full {depth-bar}"></div>           <!-- cumulative depth -->
  {viewMode!=='cumulative' && <div class="absolute top-0 h-full opacity-20"></div>}
  <div class="z-10 flex w-full gap-4 {mirrored for asks}">
    <span class="typography-mono-3" style="color:{side}">{price}{hasOpenOrders? ' •'}</span>
    <span class="typography-mono-3">{size}</span>
    <span class="typography-mono-3">{total}</span>
  </div>
</div>
```
- **Bid (long):** price `--positive`; hover `--positive-muted`; new-price flash `--positive`/30 for 200ms. **Ask (short):** `--negative` equivalents.
- Column header + spread row: `border-y --stroke-default`, `px-4 py-1`, labels `typography-paragraph-3 --text-low`; values `typography-mono-3`.
- Bottom **bid/ask % bar:** 4px tall, `rounded-full`, green left + red right, `transition-all duration-500`. **Delta bar:** centered at 50%, extends ±, `--stroke-default` track.
- Levels: 12 (vertical) / 20 (horizontal). Rows `gap-0.5`.

---

## Trade form — `src/features/trading/trade-form/components/perps-trade-form.tsx`

```html
<form class="space-y-3">
  <Card>
    <CardHeader class="p-0"><FieldOrderType/></CardHeader>   <!-- slanted HeaderTabs: Market/Limit/TWAP -->
    <CardContent class="flex flex-col px-4 pt-4 pb-4">
      <div class="flex flex-col gap-4">
        <FieldSide/>     <!-- ToggleGroup LONG(positive)/SHORT(negative), each flex-1 h-8 -->
        <FieldSize/>     <!-- market readout + leverage slider + InputNumber -->
      </div>
      <AnimatedSection visible={isLimit}>   <!-- grid-rows + opacity transition -->
        <div class="flex flex-col gap-4 pt-4"><FieldPrice/><FieldTimeInForce/></div>
      </AnimatedSection>
      <AnimatedSection visible={isTwap}>…FieldTwapDuration + Randomize checkbox…</AnimatedSection>
      <div class="flex flex-col gap-4 pt-4">
        <div class="border-t --stroke-default my-2"></div>
        <FieldReduceOnly/>
      </div>
    </CardContent>
  </Card>
  <PerpsTradeOverview/>   <!-- collateral / risk summary -->
  <CardFooter><SubmitButton/></CardFooter>   <!-- primary, block (w-full) -->
</form>
```
- **Side toggle** is the canonical LONG/SHORT control: `ToggleGroup` with `positive`/`negative` variants, `flex-1`.
- Order-type tabs use the **slanted HeaderTab** pattern above.
- Conditional fields (limit price/TIF, TWAP) animate in via `AnimatedSection` (grid-rows 200ms + opacity 150ms, staggered).
- Submit is a full-width `primary` button; loading sets `aria-busy`, shows spinner, disables.

---

## Positions table & PnL — `src/features/trading/tables/components/positions-table.tsx`, `src/shared/components/columns/column-perp-asset.tsx`

Built on `DataTable`. Column order: **Asset · Size · Position Value · Entry · Unrealized PnL · Liq. Price · Margin · TP/SL · (Close)**.

**Asset cell (`ColumnPerpAsset`)** — the position-identity pattern with a side-colored left edge + fade:
```html
<div class="relative flex items-center gap-2 py-1 border-l-2 px-4 bg-linear-to-r from-{side-muted} to-{side-invisible}"
     style="border-left-color: var(--positive | --negative)">
  <AssetAvatar class="size-4"/>
  <span class="typography-mono-3" style="color:var(--text-high)">{symbol}</span>
  <span class="typography-mono-3" style="color:{side}">{leverage}x</span>
</div>
```
**PnL cell:** `flex items-center gap-3 tabular-nums min-w-[140px]`; `TokenAmount` colored `--positive` if >0 else `--negative`, + percentage + share dropdown.
**Margin cell:** `TokenAmount` + `typography-mono-3 --text-mid` `(Cross)`/`(Isolated)`.
All numeric cells use `TokenAmount` (auto-formats via `formatNumber`, flashes on change). Close = `secondary` button.

---

## Generic table — `src/ui/table/table.tsx`, `data-table.tsx`

```html
<div data-slot="table-container" class="relative w-full">
  <table class="w-full caption-bottom">
    <thead class="bg-surface-elevated-2">
      <tr class="border-b"><th class="typography-paragraph-3 text-mid h-8 text-left align-middle font-normal whitespace-nowrap">…</th></tr>
    </thead>
    <tbody>
      <tr class="border-b transition-colors {onClick? cursor-pointer hover:bg-surface-action-tertiary} data-[state=selected]:bg-surface-elevated-1">
        <td class="typography-paragraph-1 text-mid px-4 py-[6.5px] align-middle whitespace-nowrap">…</td>
      </tr>
    </tbody>
  </table>
</div>
```
Header `--surface-elevated-2`, `h-8`, `typography-paragraph-3 --text-mid`. Body rows ~38px (`py-[6.5px]`), `border-b --stroke-default`, hover `--surface-action-tertiary`. Column `meta`: `hideOnMobile` (`hidden xtablet:table-cell`), `hideOnDesktop`, `align:"right"`. `DataTable` (tanstack) adds virtualization, loading skeletons, empty message (`typography-paragraph-3 --text-low`), and a sign-in wall.

---

## Market ticker / header readout — `src/features/trading/perps-page/components/header-market-selector.tsx`

Responsive in 4 tiers (mobile → foldable → tablet → desktop). Core pieces:
- **MarketIdentity:** `tertiary` `small` button, `gap-2`, `AssetAvatar size-4` + `typography-button-1` ticker.
- **MarkPriceInfo (price + 24h change):** `TokenAmount` price `--text-high`, variant scales `mono1`(large)/`mono2`/`mono3`(small), `prefix="$"`, `highlight` (flash). Change = `TokenAmount` colored `--positive`/`--negative` with a `Triangle` icon (rotated 180° when down), `tokenType="PERCENTAGE"`, `suffix="%"`.
- **MarketInfoItems:** `grid grid-cols-3 gap-8`; each `InfoItem` = label `typography-paragraph-3 --text-low` over a `mono4` value. Index / Volume / OI (compact notation + tooltip with full value), Funding shows rate colored by sign + countdown.

---

## Toast — `src/shared/providers/toast-provider.tsx` (sonner)

Lifecycle owned by the **UI hook**: `showToast({title, description, variant})` → `updateToast(id, {…})`. Components never call it directly.
- Surface `--surface-default`, border `#212223`, `min-w-[320px] w-fit`, `px-4 py-3`, `gap-4`, position bottom-right, icon `size-6`.
- Title `typography-paragraph-3` semibold `--text-high`; description `typography-paragraph-3` `--text-mid`.
- Variants & duration: `loading` (no auto-dismiss, spinner) → `success` (5s, check) / `error` (10s, X). Custom brand icons; success/error trigger haptics.
- Copy follows Content Fundamentals: `"Placing order"` → `"Order placed"` / `"Order failed — insufficient margin"`.

---

## What to lift first

Trading-critical, most-canonical (ground truth): **Button, Input/InputNumber, OrderBook, PerpsTradeForm, PositionsTable, HeaderMarketSelector**. Then DataTable, Tabs/HeaderTab, Badge, Toast, Card. Every one uses `data-slot` attributes, cva variants, and design tokens (no CSS modules).
