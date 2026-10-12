// GTE Web UI Kit — Order book panel
/* global React */
const { useMemo: useMemoBook } = React;

const OrderBook = () => {
  const rows = useMemoBook(() => {
    const asks = []; const bids = [];
    let p = 43219;
    for (let i = 0; i < 12; i++) { asks.push({ price: p + i * 0.5, size: +(Math.random() * 2 + 0.1).toFixed(3) }); }
    for (let i = 0; i < 12; i++) { bids.push({ price: p - (i + 1) * 0.5, size: +(Math.random() * 2 + 0.1).toFixed(3) }); }
    let t = 0; asks.slice().reverse().forEach(r => { t += r.size; r.total = t; });
    t = 0; bids.forEach(r => { t += r.size; r.total = t; });
    const maxTot = Math.max(...asks.map(r => r.total), ...bids.map(r => r.total));
    return { asks, bids, maxTot };
  }, []);

  const row = (r, side) => React.createElement("div", { key: r.price, style: {
    display: "grid", gridTemplateColumns: "1fr 1fr 1fr", padding: "3px 10px", position: "relative",
    fontFamily: "var(--font-mono)", fontSize: 11, fontVariantNumeric: "tabular-nums", cursor: "pointer",
  }},
    React.createElement("div", { style: {
      position: "absolute", top: 0, bottom: 0, right: 0,
      width: `${(r.total / rows.maxTot) * 100}%`,
      background: side === "ask" ? "var(--surface-action-negative-secondary)" : "var(--surface-action-positive-secondary)",
    }}),
    React.createElement("span", { style: { color: side === "ask" ? "var(--text-negative)" : "var(--text-positive)", position: "relative" } }, r.price.toFixed(2)),
    React.createElement("span", { style: { textAlign: "center", color: "var(--text-mid)", position: "relative" } }, r.size.toFixed(3)),
    React.createElement("span", { style: { textAlign: "right", color: "var(--text-mid)", position: "relative" } }, r.total.toFixed(3))
  );

  return React.createElement("div", { style: { display: "flex", flexDirection: "column", height: "100%", background: "var(--surface-elevated-2)" } },
    React.createElement("div", { style: {
      padding: "10px 12px", display: "flex", justifyContent: "space-between", alignItems: "center",
      borderBottom: "1px solid var(--stroke-default)",
    }},
      React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 600, color: "var(--text-high)", letterSpacing: 0.3 } }, "Order book"),
      React.createElement("div", { style: { display: "flex", gap: 4 } },
        ["0.5", "1", "5"].map((v, i) =>
          React.createElement("button", { key: v, style: {
            padding: "2px 8px", borderRadius: 4, fontFamily: "var(--font-mono)", fontSize: 10,
            background: i === 0 ? "var(--surface-elevated-2)" : "transparent",
            color: i === 0 ? "var(--text-high)" : "var(--text-mid)",
            border: "1px solid " + (i === 0 ? "var(--stroke-subtle)" : "transparent"), cursor: "pointer",
          }}, v)
        )
      )
    ),
    React.createElement("div", { style: {
      display: "grid", gridTemplateColumns: "1fr 1fr 1fr", padding: "6px 10px",
      fontFamily: "var(--font-sans)", fontSize: 9, color: "var(--text-low)", letterSpacing: 0.4,
    }},
      React.createElement("span", null, "Price"),
      React.createElement("span", { style: { textAlign: "center" } }, "Size (BTC)"),
      React.createElement("span", { style: { textAlign: "right" } }, "Total")
    ),
    React.createElement("div", { style: { flex: 1, overflow: "hidden" } },
      React.createElement("div", { style: { display: "flex", flexDirection: "column-reverse" } },
        rows.asks.map(r => row(r, "ask"))
      ),
      React.createElement("div", { style: {
        padding: "8px 10px", display: "flex", justifyContent: "space-between",
        borderTop: "1px solid var(--stroke-default)", borderBottom: "1px solid var(--stroke-default)",
        fontFamily: "var(--font-mono)", fontSize: 14, color: "var(--text-high)",
      }},
        React.createElement("span", { style: { color: "var(--text-positive)", fontVariantNumeric: "tabular-nums" } }, "43,218.50"),
        React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 10, color: "var(--text-low)", alignSelf: "center" } }, "SPREAD 0.50")
      ),
      rows.bids.map(r => row(r, "bid"))
    )
  );
};

Object.assign(window, { OrderBook });
