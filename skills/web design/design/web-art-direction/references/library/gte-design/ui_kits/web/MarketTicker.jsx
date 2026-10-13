// GTE Web UI Kit — Market ticker row
/* global React, Badge, TokenIcon, Icon */

const MarketTicker = ({ symbol = "BTC-USD", mark = 43218.50, change = 2.43, oi = "124.8M", funding = 0.0087, volume = "842.1M" }) => {
  const stat = (label, value, tone) => React.createElement("div", { style: {
    display: "flex", flexDirection: "column", gap: 2, padding: "0 16px",
    borderLeft: "1px solid var(--stroke-default)", minWidth: 92,
  }},
    React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 10, color: "var(--text-low)", letterSpacing: 0.4 } }, label),
    React.createElement("span", { style: { fontFamily: "var(--font-mono)", fontSize: 13, color: tone || "var(--text-high)", fontVariantNumeric: "tabular-nums" } }, value)
  );
  return React.createElement("div", { style: {
    height: 56, background: "var(--surface-elevated-2)",
    borderBottom: "1px solid var(--stroke-default)",
    display: "flex", alignItems: "center", padding: "0 16px", flexShrink: 0,
  }},
    // Symbol picker
    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 10, paddingRight: 16 } },
      React.createElement(TokenIcon, { symbol: "BTC", size: 28 }),
      React.createElement("div", { style: { display: "flex", flexDirection: "column", gap: 2 } },
        React.createElement("div", { style: { fontFamily: "var(--font-sans)", fontSize: 14, fontWeight: 600, color: "var(--text-high)", display: "flex", alignItems: "center", gap: 6 } },
          symbol, React.createElement("svg", { width: 12, height: 12, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2 }, React.createElement("path", { d: "M6 9l6 6 6-6" }))
        ),
        React.createElement("div", { style: { fontFamily: "var(--font-sans)", fontSize: 10, color: "var(--text-low)", letterSpacing: 0.3 } }, "Perpetual · Turbo")
      )
    ),
    // Big price
    React.createElement("div", { style: {
      display: "flex", flexDirection: "column", gap: 2, padding: "0 20px 0 16px",
      borderLeft: "1px solid var(--stroke-default)",
    }},
      React.createElement("span", { style: { fontFamily: "var(--font-mono)", fontSize: 20, fontWeight: 500, color: "var(--text-high)", fontVariantNumeric: "tabular-nums" } }, mark.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })),
      React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 6 } },
        React.createElement("span", { style: { display: "inline-flex", alignItems: "center", gap: 3, fontFamily: "var(--font-mono)", fontSize: 11, color: change >= 0 ? "var(--text-positive)" : "var(--text-negative)", fontVariantNumeric: "tabular-nums" } },
          // SVG icon, not ▲/▼ — unicode-as-icon is banned (GTE-VOX-01)
          React.createElement(Icon, { name: change >= 0 ? "arrowUp" : "arrowDown", size: 10 }),
          (change >= 0 ? "+" : "") + change.toFixed(2) + "%"),
        React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 10, color: "var(--text-low)" } }, "24h")
      )
    ),
    stat("24h high", "43,712.00"),
    stat("24h low", "41,884.30"),
    stat("24h vol", volume),
    stat("Open interest", oi),
    stat("Funding", "+" + funding.toFixed(4) + "%", "var(--text-positive)"),
    stat("Next funding", "2h 14m"),
    React.createElement("div", { style: { flex: 1 } })
  );
};

Object.assign(window, { MarketTicker });
