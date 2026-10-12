// GTE Web UI Kit — Markets sidebar
/* global React, TokenIcon, Icon */
const { useState: useStateMkt } = React;

const MarketsSidebar = () => {
  const markets = [
    { sym: "BTC", name: "Bitcoin", price: 43218.50, ch: 2.43, fav: true },
    { sym: "ETH", name: "Ethereum", price: 2284.17, ch: -1.08, fav: true },
    { sym: "SOL", name: "Solana", price: 142.94, ch: 5.82, fav: false },
    { sym: "HYPE", name: "Hyperliquid", price: 28.41, ch: 12.30, fav: false },
    { sym: "DOGE", name: "Dogecoin", price: 0.1082, ch: -3.14, fav: false },
    { sym: "AVAX", name: "Avalanche", price: 38.20, ch: 0.42, fav: false },
    { sym: "LINK", name: "Chainlink", price: 14.28, ch: 1.92, fav: false },
    { sym: "ARB", name: "Arbitrum", price: 1.124, ch: -2.18, fav: false },
  ];
  const [q, setQ] = useStateMkt("");
  const [filter, setFilter] = useStateMkt("all");
  return React.createElement("div", { style: {
    width: 240, background: "var(--surface-elevated-2)", borderRight: "1px solid var(--stroke-default)",
    display: "flex", flexDirection: "column", flexShrink: 0,
  }},
    React.createElement("div", { style: { padding: 10, borderBottom: "1px solid var(--stroke-default)", display: "flex", flexDirection: "column", gap: 8 } },
      React.createElement("div", { style: { display: "flex", gap: 2, background: "var(--surface-elevated-1)", borderRadius: 6, padding: 2 } },
        // sentence-case labels (Content Fundamentals), star as SVG not ★ (GTE-VOX-01)
        [["all", "All"], ["favs", React.createElement(Icon, { name: "star", size: 12 })], ["perps", "Perps"], ["spot", "Spot"]].map(([f, label]) =>
          React.createElement("button", { key: f, onClick: () => setFilter(f), style: {
            flex: 1, padding: "4px 6px", border: "none", cursor: "pointer",
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            background: filter === f ? "var(--surface-elevated-2)" : "transparent",
            color: filter === f ? "var(--text-high)" : "var(--text-mid)",
            borderRadius: 4, fontFamily: "var(--font-sans)", fontSize: 10, fontWeight: 500, letterSpacing: 0.3,
          }}, label)
        )
      ),
      React.createElement("input", { value: q, onChange: e => setQ(e.target.value), placeholder: "Search markets", style: {
        height: 28, padding: "0 10px", background: "var(--surface-input)", border: "none",
        borderRadius: 6, outline: "none", fontFamily: "var(--font-sans)", fontSize: 12, color: "var(--text-high)",
      }})
    ),
    React.createElement("div", { style: { flex: 1, overflow: "auto" } },
      markets.filter(m => !q || (m.sym + m.name).toLowerCase().includes(q.toLowerCase())).map((m, i) =>
        React.createElement("div", { key: m.sym, style: {
          padding: "8px 12px", display: "flex", alignItems: "center", gap: 10, cursor: "pointer",
          background: i === 0 ? "var(--surface-elevated-1)" : "transparent",
          borderLeft: i === 0 ? "2px solid var(--accent)" : "2px solid transparent",
        }},
          React.createElement(TokenIcon, { symbol: m.sym, size: 20 }),
          React.createElement("div", { style: { flex: 1, display: "flex", flexDirection: "column", gap: 1, minWidth: 0 } },
            React.createElement("div", { style: { display: "flex", justifyContent: "space-between", gap: 6 } },
              React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 600, color: "var(--text-high)" } }, m.sym + "-USD"),
              React.createElement("span", { style: { fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-high)", fontVariantNumeric: "tabular-nums" } },
                m.price < 1 ? m.price.toFixed(4) : m.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
              )
            ),
            React.createElement("div", { style: { display: "flex", justifyContent: "space-between", gap: 6 } },
              React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 10, color: "var(--text-low)" } }, m.name),
              React.createElement("span", { style: { fontFamily: "var(--font-mono)", fontSize: 10, color: m.ch >= 0 ? "var(--text-positive)" : "var(--text-negative)", fontVariantNumeric: "tabular-nums" } },
                (m.ch >= 0 ? "+" : "") + m.ch.toFixed(2) + "%"
              )
            )
          )
        )
      )
    )
  );
};

Object.assign(window, { MarketsSidebar });
