// GTE Web UI Kit — Trading chart (placeholder candles)
/* global React */
const { useMemo: useMemoChart } = React;

const TradingChart = ({ height = 380 }) => {
  const candles = useMemoChart(() => {
    const out = []; let p = 43100;
    for (let i = 0; i < 80; i++) {
      const o = p;
      const move = (Math.sin(i * 0.35) + (Math.random() - 0.5)) * 80;
      const c = o + move;
      const hi = Math.max(o, c) + Math.random() * 40;
      const lo = Math.min(o, c) - Math.random() * 40;
      out.push({ o, c, hi, lo });
      p = c;
    }
    return out;
  }, []);
  const all = candles.flatMap(k => [k.hi, k.lo]);
  const max = Math.max(...all), min = Math.min(...all);
  const y = (v) => 20 + ((max - v) / (max - min)) * (height - 60);
  const cw = 760 / candles.length;

  return React.createElement("div", { style: {
    background: "var(--surface-elevated-2)", height, position: "relative", padding: "12px",
    display: "flex", flexDirection: "column", gap: 8,
  }},
    // Chart toolbar
    React.createElement("div", { style: { display: "flex", gap: 4, alignItems: "center" } },
      ["1m", "5m", "15m", "1h", "4h", "1D"].map((t, i) =>
        React.createElement("button", { key: t, style: {
          padding: "4px 10px", borderRadius: 6, fontFamily: "var(--font-sans)", fontSize: 11, fontWeight: 500,
          background: i === 2 ? "var(--surface-elevated-2)" : "transparent",
          color: i === 2 ? "var(--text-high)" : "var(--text-mid)",
          border: "1px solid " + (i === 2 ? "var(--stroke-subtle)" : "transparent"),
          cursor: "pointer",
        }}, t)
      ),
      React.createElement("span", { style: { marginLeft: 12, fontFamily: "var(--font-sans)", fontSize: 10, color: "var(--text-low)", letterSpacing: 0.4 } }, "Indicators"),
      ["EMA 21", "VOL", "RSI"].map((t, i) =>
        React.createElement("button", { key: t, style: {
          padding: "4px 10px", borderRadius: 6, fontFamily: "var(--font-sans)", fontSize: 11,
          background: "transparent", color: "var(--text-mid)", border: "1px solid var(--stroke-default)", cursor: "pointer",
        }}, t)
      )
    ),
    React.createElement("div", { style: { flex: 1, position: "relative", background: "var(--surface-elevated-1)", borderRadius: 6, border: "1px solid var(--stroke-default)", overflow: "hidden" } },
      // Grid lines
      React.createElement("svg", { width: "100%", height: "100%", viewBox: `0 0 780 ${height - 40}`, preserveAspectRatio: "none", style: { position: "absolute", inset: 0 } },
        [0.2, 0.4, 0.6, 0.8].map(f =>
          React.createElement("line", { key: f, x1: 0, x2: 780, y1: (height - 40) * f, y2: (height - 40) * f, stroke: "var(--stroke-default)", strokeDasharray: "2 4" })
        ),
        // Candles
        candles.map((k, i) => {
          const up = k.c >= k.o;
          const color = up ? "var(--positive)" : "var(--negative)";
          const x = 10 + i * cw;
          return React.createElement("g", { key: i },
            React.createElement("line", { x1: x + cw/2, x2: x + cw/2, y1: y(k.hi), y2: y(k.lo), stroke: color, strokeWidth: 1 }),
            React.createElement("rect", { x: x + 1, y: Math.min(y(k.o), y(k.c)), width: cw - 2, height: Math.max(2, Math.abs(y(k.c) - y(k.o))), fill: color })
          );
        }),
        // Price line
        React.createElement("line", { x1: 0, x2: 780, y1: y(candles[candles.length - 1].c), y2: y(candles[candles.length - 1].c), stroke: "var(--accent)", strokeDasharray: "4 3", strokeWidth: 1 })
      ),
      // Y-axis labels
      React.createElement("div", { style: { position: "absolute", right: 0, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "space-between", padding: "8px 8px", alignItems: "flex-end", pointerEvents: "none" } },
        ["43,500", "43,300", "43,100", "42,900"].map(v =>
          React.createElement("span", { key: v, style: { fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-low)", background: "var(--surface-default)", padding: "1px 4px", borderRadius: 3 } }, v)
        )
      ),
      // Price tag
      React.createElement("div", { style: {
        position: "absolute", right: 4, top: y(candles[candles.length - 1].c) + 8,
        background: "var(--accent)", color: "var(--text-action-primary)",
        padding: "2px 6px", borderRadius: 3, fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 600,
      }}, candles[candles.length - 1].c.toFixed(2))
    )
  );
};

Object.assign(window, { TradingChart });
