// GTE Web UI Kit — Positions / Orders table
/* global React, Badge, Button */
const { useState: useStatePos } = React;

const PositionsPanel = () => {
  const [tab, setTab] = useStatePos("positions");
  const tabs = [["positions", "Positions", 2], ["orders", "Open orders", 1], ["history", "History", 14], ["balances", "Balances", null]];
  return React.createElement("div", { style: { background: "var(--surface-elevated-2)", borderTop: "1px solid var(--stroke-default)", height: 240, display: "flex", flexDirection: "column" } },
    React.createElement("div", { style: { display: "flex", gap: 0, padding: "0 4px", borderBottom: "1px solid var(--stroke-default)", flexShrink: 0 } },
      tabs.map(([k, label, n]) =>
        React.createElement("button", { key: k, onClick: () => setTab(k), style: {
          padding: "10px 14px", background: "transparent", border: "none", cursor: "pointer",
          fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 500, letterSpacing: 0.3,
          color: tab === k ? "var(--text-high)" : "var(--text-mid)",
          borderBottom: tab === k ? "2px solid var(--accent)" : "2px solid transparent",
          display: "inline-flex", alignItems: "center", gap: 6,
        }}, label, n !== null && React.createElement("span", { style: {
          fontFamily: "var(--font-mono)", fontSize: 10, padding: "1px 5px", borderRadius: 3,
          background: "var(--white-15)", color: "var(--text-mid)",
        }}, n))
      )
    ),
    React.createElement("div", { style: { flex: 1, overflow: "auto" } },
      tab === "positions" && React.createElement(PositionsTable),
      tab === "orders" && React.createElement(OrdersTable),
      tab === "history" && React.createElement(HistoryTable),
      tab === "balances" && React.createElement(BalancesTable)
    )
  );
};

const TableHead = ({ cols }) => React.createElement("div", { style: {
  display: "grid", gridTemplateColumns: cols.map(c => c.w || "1fr").join(" "),
  padding: "8px 16px", fontFamily: "var(--font-sans)", fontSize: 10,
  letterSpacing: 0.4, color: "var(--text-low)", fontWeight: 500,
  borderBottom: "1px solid var(--stroke-default)",
}}, cols.map((c, i) => React.createElement("span", { key: i, style: { textAlign: c.align || "left" } }, c.label)));

const TableRow = ({ cols, cells }) => React.createElement("div", { style: {
  display: "grid", gridTemplateColumns: cols.map(c => c.w || "1fr").join(" "),
  padding: "10px 16px", fontFamily: "var(--font-mono)", fontSize: 12, fontVariantNumeric: "tabular-nums",
  color: "var(--text-high)", borderBottom: "1px solid var(--stroke-default)", alignItems: "center",
}}, cells.map((cell, i) => React.createElement("span", { key: i, style: { textAlign: cols[i].align || "left", color: cols[i].color } }, cell)));

const PositionsTable = () => {
  const cols = [
    { label: "Market", w: "1.2fr" }, { label: "Side", w: "0.6fr" },
    { label: "Size", w: "1fr", align: "right" }, { label: "Entry", w: "1fr", align: "right" },
    { label: "Mark", w: "1fr", align: "right" }, { label: "Liq.", w: "1fr", align: "right" },
    { label: "Margin", w: "1fr", align: "right" }, { label: "PnL (ROE)", w: "1.2fr", align: "right" },
    { label: "", w: "140px", align: "right" },
  ];
  return React.createElement(React.Fragment, null,
    React.createElement(TableHead, { cols }),
    React.createElement(TableRow, { cols, cells: [
      React.createElement("span", { key: "m", style: { fontFamily: "var(--font-sans)", fontWeight: 600 } }, "BTC-USD"),
      React.createElement(Badge, { key: "s", tone: "long", dot: true }, "Long 10x"),
      "0.12 BTC", "42,980.00", "43,218.50", "38,948.10", "$516.22",
      React.createElement("span", { key: "p", style: { color: "var(--text-positive)" } }, "+$28.62 (+5.55%)"),
      React.createElement("div", { key: "b", style: { display: "flex", gap: 6, justifyContent: "flex-end" } },
        React.createElement(Button, { variant: "tertiary", size: "sm" }, "TP/SL"),
        React.createElement(Button, { variant: "tertiary", size: "sm" }, "Close")
      ),
    ]}),
    React.createElement(TableRow, { cols, cells: [
      React.createElement("span", { key: "m", style: { fontFamily: "var(--font-sans)", fontWeight: 600 } }, "ETH-USD"),
      React.createElement(Badge, { key: "s", tone: "short", dot: true }, "Short 5x"),
      "1.50 ETH", "2,314.50", "2,284.17", "2,612.10", "$342.00",
      React.createElement("span", { key: "p", style: { color: "var(--text-positive)" } }, "+$45.50 (+13.30%)"),
      React.createElement("div", { key: "b", style: { display: "flex", gap: 6, justifyContent: "flex-end" } },
        React.createElement(Button, { variant: "tertiary", size: "sm" }, "TP/SL"),
        React.createElement(Button, { variant: "tertiary", size: "sm" }, "Close")
      ),
    ]})
  );
};
const OrdersTable = () => {
  const cols = [{ label: "Time", w: "1fr" }, { label: "Market", w: "1fr" }, { label: "Side", w: "0.7fr" },
    { label: "Type", w: "0.8fr" }, { label: "Price", w: "1fr", align: "right" },
    { label: "Size", w: "1fr", align: "right" }, { label: "Filled", w: "1fr", align: "right" }, { label: "", w: "90px", align: "right" }];
  return React.createElement(React.Fragment, null,
    React.createElement(TableHead, { cols }),
    React.createElement(TableRow, { cols, cells: [
      "12:48:07", React.createElement("span", { key: "m", style: { fontFamily: "var(--font-sans)", fontWeight: 600 } }, "SOL-USD"),
      React.createElement(Badge, { key: "s", tone: "long" }, "Long"),
      React.createElement(Badge, { key: "t", tone: "neutral" }, "Limit"),
      "138.00", "10 SOL", "0 / 10",
      React.createElement(Button, { key: "x", variant: "tertiary", size: "sm" }, "Cancel"),
    ]}),
  );
};
const HistoryTable = () => React.createElement("div", { style: { padding: 40, textAlign: "center", fontFamily: "var(--font-sans)", fontSize: 12, color: "var(--text-low)" } }, "14 historical fills · connect wallet for full history");
const BalancesTable = () => React.createElement("div", { style: { padding: 40, textAlign: "center", fontFamily: "var(--font-sans)", fontSize: 12, color: "var(--text-low)" } }, "USDC 12,482.30 · ETH 0.82 · BTC 0.00");

Object.assign(window, { PositionsPanel });
