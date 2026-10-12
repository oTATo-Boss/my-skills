> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# Diagrams

Principles for technical diagrams embedded in articles, docs, and marketing —
extracted from the perpetual-DEX architecture figure. Diagrams live in the
**non-product** surface tier (they may use light-mode tokens), but still inherit
GTE's visual grammar.

## What a diagram is here

A single SVG figure in a bounded canvas, intended to be dropped into prose.
Not a slide. Not a dashboard. One idea, read left-to-right or top-to-bottom,
at a glance.

## Hard rules

- **Flat fills only.** `--surface-elevated-2` for standard nodes. No gradients, no drop shadows, no strokes on node fills.
- **Wordmark the special node.** One node may carry meaning via tint — reserve `rgba(255,120,23,0.08)` + orange text for entry points (the user, the wallet, the "outside world"). Every other node is neutral.
- **No borders on nodes.** Separation is by surface-step, same as cards in the product.
- **Numbering is optional.** If the diagram lists N steps or N components, label each with `01`..`0N` in JetBrains Mono 11px, orange. Otherwise omit.
- **One label per edge, one line.** If an edge needs a paragraph, rethink the diagram.

## Nodes

- Corner radius `8px`. Same as product cards.
- Internal padding: **22px** horizontal, **24px** top and bottom.
- **Height is derived from content** — never hand-tune a box height. Measure the rendered text, stack, add padding. Editing the label reshapes the box.
- Minimum width `200px` so single-word nodes don't look naked.
- Title: Inter 600, 15px, `--text-high`.
- Subtitle: Inter 400, 12px, `--text-mid`, 18px line-height.
- Special (wallet-like) node: title `--accent`, subtitle `--orange-200` at 85% opacity.

## Edges

- **Orthogonal routing only.** Every segment is horizontal or vertical. Corners rounded at `10px`. No diagonals, no curves.
- Stroke `1.25px`, `--white-15`. Accent edges use `--accent`, negative/error edges use `--negative`. No other colors.
- Arrowheads are filled triangles, inherit edge color, sized `7×7px`.
- Every edge terminates **on a node's visible edge**, never inside it — use a fixed `22px` stub before the first bend so arrows don't look glued to the box.

## Edge labels

- Inter 400, 11px. Color matches the edge (`--accent` on orange, `--negative` on red, `--text-mid` on neutral).
- Sat on a filled pill matching the page background so they cut cleanly through the stroke.
- **Placed along the path**, not floating in whitespace. Never overlaps a node. Prefer the middle 70% of the path (skip the stub regions).

## Auto-layout — principles the code enforces

These are non-negotiable. They exist because hand-tuning arrow coordinates breaks every time a box's text changes.

1. **Declare, don't place.** Nodes declare an `id`, a top-left position, and their content. Edges declare source + target node ids, plus which side of each they attach to (`left | right | top | bottom`). Pixel coordinates for arrows never appear in the source.
2. **Boxes size themselves.** A layout pass measures each node's text, picks the largest line, and sets the rect width + height with fixed padding.
3. **Arrows attach to live edges.** The router resolves anchor points from the measured rects, so resizing a box re-lands its arrows on the new edge.
4. **Rectilinear router with two bend options.** For perpendicular routes (H + V sides), the router builds both elbow orderings and picks the one that crosses fewer unrelated nodes. An arrow that would cut through a third box automatically detours.
5. **Paired edges get lanes.** When two edges connect the same nodes on the same axis (a request/response pair), they get symmetric lane offsets (`±LANE_SPACING / 2`) perpendicular to the travel axis. They read as two parallel tracks instead of stacking.
6. **Corridor-aware lane assignment.** Lane grouping is keyed on *where the long middle segment lands* (bucketed x-column or y-row), not just node pairs — so two unrelated edges routing through the same gutter still separate.
7. **Labels follow the path.** Each label samples candidate positions along the middle 70% of its path, rejects any that overlap a node rect, scores the rest by distance from other edges and already-placed labels, and places itself at the winner. Never hand-positioned.

## Palette (picking from the system)

| Role | Token |
|---|---|
| Canvas background | `--surface-elevated-1` |
| Node fill | `--surface-elevated-2` |
| Entry-node fill | `rgba(255,120,23,0.08)` |
| Neutral edge | `--white-15` |
| Accent edge / number | `--accent` |
| Negative edge | `--negative` |
| Title text | `--text-high` |
| Sub text | `--text-mid` |
| Label text | `--text-mid` (or edge color) |
| Entry-node title | `--accent` |
| Entry-node sub | `--orange-200` @ 85% |

## When to make a diagram

- A reader would otherwise need two paragraphs of prose to understand a component graph.
- The topology matters (which component talks to which, in what direction).
- Three or more actors with named relationships between them.

If there are fewer than three nodes, or the relationships are a single sequence, use a sentence instead.

## Building one

There is **no prebuilt template file** in this skill. Build the figure directly
from the auto-layout principles above: inline the layout pass (measure text →
size rects → resolve anchors → route orthogonal elbows → place labels) in a
single self-contained `<svg>` (or an HTML file with an inline `<script>` that
emits SVG). Declare `node` and `edge` definitions at the top; let the engine
derive every coordinate. Never hand-place arrow points — that is the whole
reason this spec exists.
