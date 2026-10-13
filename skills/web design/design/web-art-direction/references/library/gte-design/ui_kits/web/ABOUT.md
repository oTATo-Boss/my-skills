> 用途：按需参考原模块的技术或风格配方。项目与用户选择优先；示例数值、主题和文案格式不构成全局要求。

# GTE · Web UI Kit

A cosmetic recreation of the GTE web trading terminal. Components are intentionally simple — real state and data flow are not implemented; the goal is pixel-accurate visuals usable for mocks and prototypes.

## Files

| File | What |
|---|---|
| `index.html` | Full trading terminal screen — header, markets sidebar, ticker, chart, orderbook, trades tape, order form, positions panel. |
| `Primitives.jsx` | `Button`, `Icon` (inline Lucide paths), `Badge`, `TokenIcon`. |
| `Header.jsx` | Top nav — logo, primary nav, search, agent button, wallet. |
| `MarketsSidebar.jsx` | Left markets list with search, filter tabs, 24h price + change. |
| `MarketTicker.jsx` | Symbol + big mark price + 24h high/low/vol, OI, funding, next-funding timer. |
| `TradingChart.jsx` | Candle chart placeholder with timeframe selector and indicator chips. |
| `OrderBook.jsx` | Depth-bar orderbook with spread row. |
| `RecentTrades.jsx` | Live-tape recent trades. |
| `OrderForm.jsx` | Long/short tabs, market/limit, size slider, reduce-only, order summary. |
| `PositionsPanel.jsx` | Bottom tabbed table — positions, open orders, history, balances. |

## Source of truth

Built from the `gte-web` codebase (`features/trading/*`, `ui/*`, Supernova tokens) and the `/Web` page in the GTE Figma file. Components follow the production naming (`OrderBook`, `PositionsPanel`, etc.) where possible.

## Using the kit

Serve the **skill root** (two levels up, `skills/gte-design/`) over HTTP and open the kit from there — e.g. `python3 -m http.server` from the skill root, then `http://localhost:8000/ui_kits/web/index.html`. Serving from this folder instead breaks styling: `index.html` loads `../../colors_and_type.css` and `../../assets/…`, which resolve outside the server root and 404. Opening via `file://` doesn't work either — it renders blank because the in-browser Babel loader fetches the `.jsx` files with XHR, which Chrome/Edge block for local files. All components register themselves on `window` — compose them in your own HTML the same way `index.html` does. All color/type values come from `colors_and_type.css`.

## What's stubbed

- No real orderbook / market data. Prices are seeded and static.
- Wallet address, agent button, and nav items are decorative.
- Positions and orders are hand-crafted sample rows.
- Chart is an SVG candle set, not a real charting library.
