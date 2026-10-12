// GTE Web UI Kit — Recent trades tape
/* global React */
const { useMemo: useMemoTape } = React;

const RecentTrades = () => {
  const rows = useMemoTape(() => {
    const out = [];
    for (let i = 0; i < 24; i++) {
      const side = Math.random() > 0.5 ? "buy" : "sell";
      const price = 43218.5 + (Math.random() - 0.5) * 20;
      const size = +(Math.random() * 2.2).toFixed(3);
      const m = 48 - Math.floor(i * 2 + Math.random() * 2);
      out.push({ side, price, size, time: `12:${String(m).padStart(2, "0")}:${String(Math.floor(Math.random() * 60)).padStart(2, "0")}` });
    }
    return out;
  }, []);

  return React.createElement("div", { style: { display: "flex", flexDirection: "column", height: "100%" } },
    React.createElement("div", { style: {
      padding: "10px 12px", borderBottom: "1px solid var(--stroke-default)",
      fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 600, color: "var(--text-high)", letterSpacing: 0.3,
    }}, "Recent trades"),
    React.createElement("div", { style: {
      display: "grid", gridTemplateColumns: "1fr 1fr 1fr", padding: "6px 10px",
      fontFamily: "var(--font-sans)", fontSize: 9, color: "var(--text-low)", letterSpacing: 0.4,
    }},
      React.createElement("span", null, "Price"),
      React.createElement("span", { style: { textAlign: "center" } }, "Size"),
      React.createElement("span", { style: { textAlign: "right" } }, "Time")
    ),
    React.createElement("div", { style: { flex: 1, overflow: "hidden" } },
      rows.map((r, i) => React.createElement("div", { key: i, style: {
        display: "grid", gridTemplateColumns: "1fr 1fr 1fr", padding: "3px 10px",
        fontFamily: "var(--font-mono)", fontSize: 11, fontVariantNumeric: "tabular-nums",
      }},
        React.createElement("span", { style: { color: r.side === "buy" ? "var(--text-positive)" : "var(--text-negative)" } }, r.price.toFixed(2)),
        React.createElement("span", { style: { textAlign: "center", color: "var(--text-mid)" } }, r.size.toFixed(3)),
        React.createElement("span", { style: { textAlign: "right", color: "var(--text-low)" } }, r.time)
      ))
    )
  );
};

Object.assign(window, { RecentTrades });
