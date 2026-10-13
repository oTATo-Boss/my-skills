> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# Dither Charts (vanilla engine)

The dither-kit look (tripwire.sh/dither-kit) for pages where React is unavailable —
When a target surface forbids external scripts, this dependency-free IIFE can be inlined. Otherwise use the project’s own asset loading and CSP rules.

**Engine:** `assets/dither-charts.js` (~9 KB). Load the whole file using the target project’s supported mechanism, then call `DitherCharts.chart(el, opts)`.

⚠️ If you assemble the page with a shell heredoc, QUOTE the delimiter (`<<'EOF'`) —
an unquoted heredoc lets the shell expand `$0`/`$vars` inside the JS and corrupts
formatters (a literal `"$0"` became `/bin/zsh` once).

## What it renders

- `type: 'bar'` — stacked dithered bars (spend/requests-style)
- `type: 'area'` — stacked dithered area (tokens-style)
- `type: 'line'` — line with dithered glow band (latency-style)
- Hover crosshair + tooltip (formatted values, colored swatches), flow legend below
  the chart (never overlays the plot), y-ticks with nice steps and measured margins,
  entrance animation honoring `prefers-reduced-motion`, DPR-aware, resizes.

## API

```js
const c = DitherCharts.chart(document.getElementById('chart'), {
  type: 'bar',                       // 'area' | 'line' | 'bar'
  data: [{ x: '07-12', fable: 12, sol: 4 }, ...],
  xKey: 'x',
  series: [                          // color = seed name from the palette
    { key: 'fable', label: 'claude-fable-5', color: 'orange' },
    { key: 'sol',   label: 'gpt-5.6-sol',    color: 'green'  },
  ],
  palette: DitherCharts.PALETTES.llDark,
  stacked: true,                     // default true (except line)
  formatValue: v => '$' + v.toFixed(2),  // tooltip
  formatTick:  v => '$' + v,             // y-axis
  formatX:     v => String(v),
  yTicks: 3, xTicks: 6, legend: true, animate: true,
  ariaLabel: 'Daily spend stacked by model',
});
c.setData(rows); c.setPalette(p); c.destroy();
```

The host `el` must have a fixed height (e.g. `height: 210px`); the engine makes it a
flex column and gives the legend its own row inside that height.

## Palettes — pick by surface

- **`llDark`** — Liquid Labs instrument panel (loop-tracker artifacts, run trackers,
  factory dashboards). Series wheel BY RANK: `orange → green → blue → purple → pink
  → yellow`; `grey` = no-data/unrouted. Page chrome comes from loop-tracker-design
  tokens (page `rgb(10,11,12)`, card `rgb(24,26,27)`); trackers are deliberately
  dark-only.
- **`qladMonoDark` / `qladMonoLight`** — QLAD register-D monochrome ladders
  (`g1`…`g6` by rank, rank 0 strongest). For QLAD-branded artifacts. NOT for the
  qlad-monorepo React app — that uses the real dither-kit React components.
- **`hues`** — dither-kit's own wheel (`green blue purple pink orange red` + `grey`)
  for neutral/product contexts.

Custom brand: `DitherCharts.seed([r,g,b])` builds a fill/line/star seed
(pass `[0,0,0]` as the second arg on light grounds so accents pull darker).

## Rules

- **One color = one entity, everywhere.** If several charts on a page share
  entities (models, channels), assign colors ONCE by global rank and reuse the
  mapping in every chart and list — same principle as the qlad-monorepo model color
  key (`apps/web/components/gateway/charts/model-colors.ts`).
- Reserve `grey` for "no data / unattributed" buckets; never spend it on a real series.
- Dual-theme artifact pages: keep two palettes and swap on toggle —
  `new MutationObserver(() => c.setPalette(isDark ? dark : light))` watching
  `data-theme` on the root element, plus a `prefers-color-scheme` initial pick.
  Single-theme instrument panels (trackers) skip this by design.
- Choose the chart form from the comparison being made, preserve units and axes, and supply accessible HTML data; the engine only supplies rendering and palette options.
- Canvas text is not selectable/readable by screen readers: always pass `ariaLabel`,
  and put the headline numbers in HTML text near the chart (stat tiles), not only
  in the pixels.
