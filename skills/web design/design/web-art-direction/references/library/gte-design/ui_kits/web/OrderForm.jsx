// GTE Web UI Kit — Order form
/* global React, Button, Icon */
const { useState: useStateForm } = React;

const OrderForm = () => {
  const [side, setSide] = useStateForm("long");
  const [type, setType] = useStateForm("market");
  const [size, setSize] = useStateForm("0.05");
  const [price, setPrice] = useStateForm("43218.50");
  const [leverage, setLeverage] = useStateForm(10);
  const [reduceOnly, setReduceOnly] = useStateForm(false);

  const isLong = side === "long";
  const accent = isLong ? "var(--text-positive)" : "var(--text-negative)";
  const accentBg = isLong ? "var(--surface-action-positive-secondary)" : "var(--surface-action-negative-secondary)";

  const tab = (label, active, onClick) => React.createElement("button", {
    onClick, style: {
      flex: 1, height: 36, fontFamily: "var(--font-sans)", fontSize: 13, fontWeight: 600,
      background: active ? (label === "Long" ? "var(--surface-action-positive-secondary)" : label === "Short" ? "var(--surface-action-negative-secondary)" : "var(--surface-elevated-2)") : "transparent",
      color: active ? (label === "Long" ? "var(--text-positive)" : label === "Short" ? "var(--text-negative)" : "var(--text-high)") : "var(--text-mid)",
      border: "none", borderBottom: active ? `2px solid ${label === "Long" ? "var(--text-positive)" : label === "Short" ? "var(--text-negative)" : "var(--accent)"}` : "2px solid transparent",
      cursor: "pointer", letterSpacing: 0.3,
    }
  }, label);

  const inputRow = (label, value, onChange, suffix) => React.createElement("div", { style: {
    display: "flex", alignItems: "center", height: 36, padding: "0 12px", gap: 8,
    background: "var(--surface-input)", borderRadius: 8, border: "1px solid transparent",
  }},
    React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 10, color: "var(--text-low)", letterSpacing: 0.4, fontWeight: 500, minWidth: 40 } }, label),
    React.createElement("input", { value, onChange: e => onChange(e.target.value), style: {
      flex: 1, background: "transparent", border: "none", outline: "none",
      // editable fields stay Inter while typing (hard rule); mono resumes on displayed values
      fontFamily: "var(--font-sans)", fontSize: 13, color: "var(--text-high)", fontVariantNumeric: "tabular-nums", textAlign: "right",
    } }),
    React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 11, color: "var(--text-mid)" } }, suffix)
  );

  return React.createElement("div", { style: { display: "flex", flexDirection: "column", height: "100%", background: "var(--surface-elevated-2)" } },
    // Long/Short tabs
    React.createElement("div", { style: { display: "flex", borderBottom: "1px solid var(--stroke-default)" } },
      tab("Long", isLong, () => setSide("long")),
      tab("Short", !isLong, () => setSide("short"))
    ),
    React.createElement("div", { style: { padding: 12, display: "flex", flexDirection: "column", gap: 10, flex: 1, overflow: "auto" } },
      // Market / Limit
      React.createElement("div", { style: { display: "flex", background: "var(--surface-elevated-1)", borderRadius: 8, padding: 2, gap: 2 } },
        ["Market", "Limit", "Stop"].map(t =>
          React.createElement("button", { key: t, onClick: () => setType(t.toLowerCase()), style: {
            flex: 1, height: 26, borderRadius: 6, border: "none", cursor: "pointer",
            fontFamily: "var(--font-sans)", fontSize: 11, fontWeight: 500,
            background: type === t.toLowerCase() ? "var(--surface-elevated-2)" : "transparent",
            color: type === t.toLowerCase() ? "var(--text-high)" : "var(--text-mid)",
          }}, t)
        )
      ),
      // Margin mode
      React.createElement("div", { style: { display: "flex", gap: 8 } },
        React.createElement("div", { style: {
          flex: 1, padding: "7px 10px", borderRadius: 6, background: "var(--surface-elevated-1)",
          border: "1px solid var(--stroke-default)",
          display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer",
        }},
          React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 11, color: "var(--text-mid)" } }, "Cross"),
          React.createElement(Icon, { name: "chevronDown", size: 12, color: "var(--text-low)" })
        ),
        React.createElement("div", { style: {
          flex: 1, padding: "7px 10px", borderRadius: 6, background: "var(--surface-elevated-1)",
          border: "1px solid var(--stroke-default)",
          display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer",
        }},
          React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 11, color: "var(--text-mid)" } }, "10x"),
          React.createElement(Icon, { name: "chevronDown", size: 12, color: "var(--text-low)" })
        )
      ),
      // Inputs
      type === "limit" && inputRow("Price", price, setPrice, "USDC"),
      inputRow("Size", size, setSize, "BTC"),
      // Size slider
      React.createElement("div", { style: { display: "flex", flexDirection: "column", gap: 6, paddingTop: 4 } },
        React.createElement("div", { style: { position: "relative", height: 16, display: "flex", alignItems: "center" } },
          React.createElement("div", { style: { position: "absolute", left: 0, right: 0, height: 2, background: "var(--white-15)", borderRadius: 1 } }),
          React.createElement("div", { style: { position: "absolute", left: 0, width: "45%", height: 2, background: accent, borderRadius: 1 } }),
          [0, 25, 50, 75, 100].map(p =>
            React.createElement("div", { key: p, style: {
              position: "absolute", left: `${p}%`, transform: "translateX(-50%)",
              width: 8, height: 8, borderRadius: "50%",
              background: p <= 45 ? accent : "var(--surface-elevated-2)",
              border: "1px solid " + (p <= 45 ? accent : "var(--stroke-subtle)"),
            }})
          )
        ),
        React.createElement("div", { style: { display: "flex", justifyContent: "space-between", fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text-low)" } },
          ["0%", "25%", "50%", "75%", "100%"].map(p => React.createElement("span", { key: p }, p))
        )
      ),
      // Reduce only
      React.createElement("label", { style: { display: "flex", alignItems: "center", gap: 8, cursor: "pointer", padding: "4px 0" } },
        React.createElement("span", { onClick: () => setReduceOnly(!reduceOnly), style: {
          width: 28, height: 16, borderRadius: 10, position: "relative",
          background: reduceOnly ? "var(--accent)" : "var(--white-15)", transition: "all 200ms",
        }},
          React.createElement("span", { style: {
            position: "absolute", width: 12, height: 12, borderRadius: "50%", background: "white",
            top: 2, left: reduceOnly ? 14 : 2, transition: "all 200ms",
          }})
        ),
        React.createElement("span", { style: { fontFamily: "var(--font-sans)", fontSize: 12, color: "var(--text-mid)" } }, "Reduce only")
      ),
      // Order summary
      React.createElement("div", { style: { padding: 10, background: "var(--surface-elevated-1)", borderRadius: 8, display: "flex", flexDirection: "column", gap: 6 } },
        [["Order value", "$2,160.93"], ["Margin required", "$216.09"], ["Liquidation price", "$38,948.10"], ["Est. fees", "$1.08"]].map(([k, v]) =>
          React.createElement("div", { key: k, style: { display: "flex", justifyContent: "space-between", fontFamily: "var(--font-sans)", fontSize: 11 } },
            React.createElement("span", { style: { color: "var(--text-low)" } }, k),
            React.createElement("span", { style: { color: "var(--text-high)", fontFamily: "var(--font-mono)", fontVariantNumeric: "tabular-nums" } }, v)
          )
        )
      ),
      // CTA
      React.createElement(Button, {
        variant: isLong ? "positive" : "negative", style: { width: "100%", justifyContent: "center" },
      }, (isLong ? "Long" : "Short") + " BTC-USD · 10x")
    )
  );
};

Object.assign(window, { OrderForm });
