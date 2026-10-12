/* @ds-bundle: {"format":3,"namespace":"GTEDesignSystem_6d6f71","components":[],"sourceHashes":{"ui_kits/web/Header.jsx":"4263356b34aa","ui_kits/web/MarketTicker.jsx":"458c81371bbe","ui_kits/web/MarketsSidebar.jsx":"13028a2784fc","ui_kits/web/OrderBook.jsx":"648fee5794ba","ui_kits/web/OrderForm.jsx":"aec51b0cce0f","ui_kits/web/PositionsPanel.jsx":"426cd6b69e4b","ui_kits/web/Primitives.jsx":"9609de143182","ui_kits/web/RecentTrades.jsx":"f0932e084482","ui_kits/web/TradingChart.jsx":"5cdb917286eb"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.GTEDesignSystem_6d6f71 = window.GTEDesignSystem_6d6f71 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// ui_kits/web/Header.jsx
try { (() => {
// GTE Web UI Kit — Header + Sidebar
/* global React, Button, Icon, Badge */
const {
  useState: useStateHeader
} = React;
const Header = () => {
  return React.createElement("header", {
    style: {
      height: 48,
      background: "var(--surface-elevated-2)",
      borderBottom: "1px solid var(--stroke-default)",
      display: "flex",
      alignItems: "center",
      padding: "0 16px",
      gap: 24,
      flexShrink: 0
    }
  },
  // Logo
  React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8
    }
  }, React.createElement("img", {
    src: "assets/logos/gte-logo-white.svg",
    style: {
      height: 18
    }
  })),
  // Primary nav
  React.createElement("nav", {
    style: {
      display: "flex",
      gap: 4,
      marginLeft: 16
    }
  }, ["Markets", "Trade", "Portfolio", "Earn", "Faucet"].map((n, i) => React.createElement("a", {
    key: n,
    href: "#",
    style: {
      padding: "8px 12px",
      borderRadius: 6,
      fontFamily: "var(--font-sans)",
      fontSize: 13,
      fontWeight: 500,
      color: i === 1 ? "var(--text-high)" : "var(--text-mid)",
      background: i === 1 ? "var(--surface-elevated-1)" : "transparent",
      textDecoration: "none",
      display: "flex",
      alignItems: "center",
      gap: 6
    }
  }, n, i === 3 && React.createElement(Badge, {
    tone: "brand"
  }, "New")))),
  // Spacer
  React.createElement("div", {
    style: {
      flex: 1
    }
  }),
  // Search
  React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      height: 30,
      padding: "0 10px",
      background: "var(--surface-input)",
      borderRadius: 8,
      width: 200,
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      color: "var(--text-low)"
    }
  }, React.createElement(Icon, {
    name: "search",
    size: 14,
    color: "var(--text-low)"
  }), "Search markets…", React.createElement("span", {
    style: {
      marginLeft: "auto",
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      padding: "2px 6px",
      background: "var(--white-15)",
      borderRadius: 4
    }
  }, "⌘K")),
  // Agent
  React.createElement(Button, {
    variant: "secondary",
    size: "sm",
    icon: React.createElement(Icon, {
      name: "sparkle",
      size: 14,
      color: "var(--accent)"
    })
  }, "Agent"),
  // Wallet
  React.createElement(Button, {
    variant: "primary",
    size: "sm",
    icon: React.createElement(Icon, {
      name: "wallet",
      size: 14
    })
  }, "0x4A2B…9F3E"),
  // Bell
  React.createElement("button", {
    style: {
      width: 30,
      height: 30,
      borderRadius: 6,
      border: "1px solid var(--stroke-default)",
      background: "var(--surface-action-tertiary)",
      color: "var(--text-mid)",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      cursor: "pointer"
    }
  }, React.createElement(Icon, {
    name: "bell",
    size: 14
  })));
};
Object.assign(window, {
  Header
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/Header.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/MarketTicker.jsx
try { (() => {
// GTE Web UI Kit — Market ticker row
/* global React, Badge, TokenIcon, Icon */

const MarketTicker = ({
  symbol = "BTC-USD",
  mark = 43218.50,
  change = 2.43,
  oi = "124.8M",
  funding = 0.0087,
  volume = "842.1M"
}) => {
  const stat = (label, value, tone) => React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 2,
      padding: "0 16px",
      borderLeft: "1px solid var(--stroke-default)",
      minWidth: 92
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      color: "var(--text-low)",
      letterSpacing: 0.4
    }
  }, label), React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 13,
      color: tone || "var(--text-high)",
      fontVariantNumeric: "tabular-nums"
    }
  }, value));
  return React.createElement("div", {
    style: {
      height: 56,
      background: "var(--surface-elevated-2)",
      borderBottom: "1px solid var(--stroke-default)",
      display: "flex",
      alignItems: "center",
      padding: "0 16px",
      flexShrink: 0
    }
  },
  // Symbol picker
  React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10,
      paddingRight: 16
    }
  }, React.createElement(TokenIcon, {
    symbol: "BTC",
    size: 28
  }), React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 2
    }
  }, React.createElement("div", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 14,
      fontWeight: 600,
      color: "var(--text-high)",
      display: "flex",
      alignItems: "center",
      gap: 6
    }
  }, symbol, React.createElement("svg", {
    width: 12,
    height: 12,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2
  }, React.createElement("path", {
    d: "M6 9l6 6 6-6"
  }))), React.createElement("div", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      color: "var(--text-low)",
      letterSpacing: 0.3
    }
  }, "Perpetual · Turbo"))),
  // Big price
  React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 2,
      padding: "0 20px 0 16px",
      borderLeft: "1px solid var(--stroke-default)"
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 20,
      fontWeight: 500,
      color: "var(--text-high)",
      fontVariantNumeric: "tabular-nums"
    }
  }, mark.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })), React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 6
    }
  }, React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 3,
      fontFamily: "var(--font-mono)",
      fontSize: 11,
      color: change >= 0 ? "var(--text-positive)" : "var(--text-negative)",
      fontVariantNumeric: "tabular-nums"
    }
  },
  // SVG icon, not ▲/▼ — unicode-as-icon is banned (GTE-VOX-01)
  React.createElement(Icon, {
    name: change >= 0 ? "arrowUp" : "arrowDown",
    size: 10
  }), (change >= 0 ? "+" : "") + change.toFixed(2) + "%"), React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      color: "var(--text-low)"
    }
  }, "24h"))), stat("24h high", "43,712.00"), stat("24h low", "41,884.30"), stat("24h vol", volume), stat("Open interest", oi), stat("Funding", "+" + funding.toFixed(4) + "%", "var(--text-positive)"), stat("Next funding", "2h 14m"), React.createElement("div", {
    style: {
      flex: 1
    }
  }));
};
Object.assign(window, {
  MarketTicker
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/MarketTicker.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/MarketsSidebar.jsx
try { (() => {
// GTE Web UI Kit — Markets sidebar
/* global React, TokenIcon, Icon */
const {
  useState: useStateMkt
} = React;
const MarketsSidebar = () => {
  const markets = [{
    sym: "BTC",
    name: "Bitcoin",
    price: 43218.50,
    ch: 2.43,
    fav: true
  }, {
    sym: "ETH",
    name: "Ethereum",
    price: 2284.17,
    ch: -1.08,
    fav: true
  }, {
    sym: "SOL",
    name: "Solana",
    price: 142.94,
    ch: 5.82,
    fav: false
  }, {
    sym: "HYPE",
    name: "Hyperliquid",
    price: 28.41,
    ch: 12.30,
    fav: false
  }, {
    sym: "DOGE",
    name: "Dogecoin",
    price: 0.1082,
    ch: -3.14,
    fav: false
  }, {
    sym: "AVAX",
    name: "Avalanche",
    price: 38.20,
    ch: 0.42,
    fav: false
  }, {
    sym: "LINK",
    name: "Chainlink",
    price: 14.28,
    ch: 1.92,
    fav: false
  }, {
    sym: "ARB",
    name: "Arbitrum",
    price: 1.124,
    ch: -2.18,
    fav: false
  }];
  const [q, setQ] = useStateMkt("");
  const [filter, setFilter] = useStateMkt("all");
  return React.createElement("div", {
    style: {
      width: 240,
      background: "var(--surface-elevated-2)",
      borderRight: "1px solid var(--stroke-default)",
      display: "flex",
      flexDirection: "column",
      flexShrink: 0
    }
  }, React.createElement("div", {
    style: {
      padding: 10,
      borderBottom: "1px solid var(--stroke-default)",
      display: "flex",
      flexDirection: "column",
      gap: 8
    }
  }, React.createElement("div", {
    style: {
      display: "flex",
      gap: 2,
      background: "var(--surface-elevated-1)",
      borderRadius: 6,
      padding: 2
    }
  },
  // sentence-case labels (Content Fundamentals), star as SVG not ★ (GTE-VOX-01)
  [["all", "All"], ["favs", React.createElement(Icon, {
    name: "star",
    size: 12
  })], ["perps", "Perps"], ["spot", "Spot"]].map(([f, label]) => React.createElement("button", {
    key: f,
    onClick: () => setFilter(f),
    style: {
      flex: 1,
      padding: "4px 6px",
      border: "none",
      cursor: "pointer",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      background: filter === f ? "var(--surface-elevated-2)" : "transparent",
      color: filter === f ? "var(--text-high)" : "var(--text-mid)",
      borderRadius: 4,
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      fontWeight: 500,
      letterSpacing: 0.3
    }
  }, label))), React.createElement("input", {
    value: q,
    onChange: e => setQ(e.target.value),
    placeholder: "Search markets",
    style: {
      height: 28,
      padding: "0 10px",
      background: "var(--surface-input)",
      border: "none",
      borderRadius: 6,
      outline: "none",
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      color: "var(--text-high)"
    }
  })), React.createElement("div", {
    style: {
      flex: 1,
      overflow: "auto"
    }
  }, markets.filter(m => !q || (m.sym + m.name).toLowerCase().includes(q.toLowerCase())).map((m, i) => React.createElement("div", {
    key: m.sym,
    style: {
      padding: "8px 12px",
      display: "flex",
      alignItems: "center",
      gap: 10,
      cursor: "pointer",
      background: i === 0 ? "var(--surface-elevated-1)" : "transparent",
      borderLeft: i === 0 ? "2px solid var(--accent)" : "2px solid transparent"
    }
  }, React.createElement(TokenIcon, {
    symbol: m.sym,
    size: 20
  }), React.createElement("div", {
    style: {
      flex: 1,
      display: "flex",
      flexDirection: "column",
      gap: 1,
      minWidth: 0
    }
  }, React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      gap: 6
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 600,
      color: "var(--text-high)"
    }
  }, m.sym + "-USD"), React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 11,
      color: "var(--text-high)",
      fontVariantNumeric: "tabular-nums"
    }
  }, m.price < 1 ? m.price.toFixed(4) : m.price.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }))), React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      gap: 6
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      color: "var(--text-low)"
    }
  }, m.name), React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      color: m.ch >= 0 ? "var(--text-positive)" : "var(--text-negative)",
      fontVariantNumeric: "tabular-nums"
    }
  }, (m.ch >= 0 ? "+" : "") + m.ch.toFixed(2) + "%")))))));
};
Object.assign(window, {
  MarketsSidebar
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/MarketsSidebar.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/OrderBook.jsx
try { (() => {
// GTE Web UI Kit — Order book panel
/* global React */
const {
  useMemo: useMemoBook
} = React;
const OrderBook = () => {
  const rows = useMemoBook(() => {
    const asks = [];
    const bids = [];
    let p = 43219;
    for (let i = 0; i < 12; i++) {
      asks.push({
        price: p + i * 0.5,
        size: +(Math.random() * 2 + 0.1).toFixed(3)
      });
    }
    for (let i = 0; i < 12; i++) {
      bids.push({
        price: p - (i + 1) * 0.5,
        size: +(Math.random() * 2 + 0.1).toFixed(3)
      });
    }
    let t = 0;
    asks.slice().reverse().forEach(r => {
      t += r.size;
      r.total = t;
    });
    t = 0;
    bids.forEach(r => {
      t += r.size;
      r.total = t;
    });
    const maxTot = Math.max(...asks.map(r => r.total), ...bids.map(r => r.total));
    return {
      asks,
      bids,
      maxTot
    };
  }, []);
  const row = (r, side) => React.createElement("div", {
    key: r.price,
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr 1fr",
      padding: "3px 10px",
      position: "relative",
      fontFamily: "var(--font-mono)",
      fontSize: 11,
      fontVariantNumeric: "tabular-nums",
      cursor: "pointer"
    }
  }, React.createElement("div", {
    style: {
      position: "absolute",
      top: 0,
      bottom: 0,
      right: 0,
      width: `${r.total / rows.maxTot * 100}%`,
      background: side === "ask" ? "var(--surface-action-negative-secondary)" : "var(--surface-action-positive-secondary)"
    }
  }), React.createElement("span", {
    style: {
      color: side === "ask" ? "var(--text-negative)" : "var(--text-positive)",
      position: "relative"
    }
  }, r.price.toFixed(2)), React.createElement("span", {
    style: {
      textAlign: "center",
      color: "var(--text-mid)",
      position: "relative"
    }
  }, r.size.toFixed(3)), React.createElement("span", {
    style: {
      textAlign: "right",
      color: "var(--text-mid)",
      position: "relative"
    }
  }, r.total.toFixed(3)));
  return React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      height: "100%",
      background: "var(--surface-elevated-2)"
    }
  }, React.createElement("div", {
    style: {
      padding: "10px 12px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      borderBottom: "1px solid var(--stroke-default)"
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 600,
      color: "var(--text-high)",
      letterSpacing: 0.3
    }
  }, "Order book"), React.createElement("div", {
    style: {
      display: "flex",
      gap: 4
    }
  }, ["0.5", "1", "5"].map((v, i) => React.createElement("button", {
    key: v,
    style: {
      padding: "2px 8px",
      borderRadius: 4,
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      background: i === 0 ? "var(--surface-elevated-2)" : "transparent",
      color: i === 0 ? "var(--text-high)" : "var(--text-mid)",
      border: "1px solid " + (i === 0 ? "var(--stroke-subtle)" : "transparent"),
      cursor: "pointer"
    }
  }, v)))), React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr 1fr",
      padding: "6px 10px",
      fontFamily: "var(--font-sans)",
      fontSize: 9,
      color: "var(--text-low)",
      letterSpacing: 0.4
    }
  }, React.createElement("span", null, "Price"), React.createElement("span", {
    style: {
      textAlign: "center"
    }
  }, "Size (BTC)"), React.createElement("span", {
    style: {
      textAlign: "right"
    }
  }, "Total")), React.createElement("div", {
    style: {
      flex: 1,
      overflow: "hidden"
    }
  }, React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column-reverse"
    }
  }, rows.asks.map(r => row(r, "ask"))), React.createElement("div", {
    style: {
      padding: "8px 10px",
      display: "flex",
      justifyContent: "space-between",
      borderTop: "1px solid var(--stroke-default)",
      borderBottom: "1px solid var(--stroke-default)",
      fontFamily: "var(--font-mono)",
      fontSize: 14,
      color: "var(--text-high)"
    }
  }, React.createElement("span", {
    style: {
      color: "var(--text-positive)",
      fontVariantNumeric: "tabular-nums"
    }
  }, "43,218.50"), React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      color: "var(--text-low)",
      alignSelf: "center"
    }
  }, "SPREAD 0.50")), rows.bids.map(r => row(r, "bid"))));
};
Object.assign(window, {
  OrderBook
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/OrderBook.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/OrderForm.jsx
try { (() => {
// GTE Web UI Kit — Order form
/* global React, Button, Icon */
const {
  useState: useStateForm
} = React;
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
    onClick,
    style: {
      flex: 1,
      height: 36,
      fontFamily: "var(--font-sans)",
      fontSize: 13,
      fontWeight: 600,
      background: active ? label === "Long" ? "var(--surface-action-positive-secondary)" : label === "Short" ? "var(--surface-action-negative-secondary)" : "var(--surface-elevated-2)" : "transparent",
      color: active ? label === "Long" ? "var(--text-positive)" : label === "Short" ? "var(--text-negative)" : "var(--text-high)" : "var(--text-mid)",
      border: "none",
      borderBottom: active ? `2px solid ${label === "Long" ? "var(--text-positive)" : label === "Short" ? "var(--text-negative)" : "var(--accent)"}` : "2px solid transparent",
      cursor: "pointer",
      letterSpacing: 0.3
    }
  }, label);
  const inputRow = (label, value, onChange, suffix) => React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      height: 36,
      padding: "0 12px",
      gap: 8,
      background: "var(--surface-input)",
      borderRadius: 8,
      border: "1px solid transparent"
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      color: "var(--text-low)",
      letterSpacing: 0.4,
      fontWeight: 500,
      minWidth: 40
    }
  }, label), React.createElement("input", {
    value,
    onChange: e => onChange(e.target.value),
    style: {
      flex: 1,
      background: "transparent",
      border: "none",
      outline: "none",
      // editable fields stay Inter while typing (hard rule); mono resumes on displayed values
      fontFamily: "var(--font-sans)",
      fontSize: 13,
      color: "var(--text-high)",
      fontVariantNumeric: "tabular-nums",
      textAlign: "right"
    }
  }), React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      color: "var(--text-mid)"
    }
  }, suffix));
  return React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      height: "100%",
      background: "var(--surface-elevated-2)"
    }
  },
  // Long/Short tabs
  React.createElement("div", {
    style: {
      display: "flex",
      borderBottom: "1px solid var(--stroke-default)"
    }
  }, tab("Long", isLong, () => setSide("long")), tab("Short", !isLong, () => setSide("short"))), React.createElement("div", {
    style: {
      padding: 12,
      display: "flex",
      flexDirection: "column",
      gap: 10,
      flex: 1,
      overflow: "auto"
    }
  },
  // Market / Limit
  React.createElement("div", {
    style: {
      display: "flex",
      background: "var(--surface-elevated-1)",
      borderRadius: 8,
      padding: 2,
      gap: 2
    }
  }, ["Market", "Limit", "Stop"].map(t => React.createElement("button", {
    key: t,
    onClick: () => setType(t.toLowerCase()),
    style: {
      flex: 1,
      height: 26,
      borderRadius: 6,
      border: "none",
      cursor: "pointer",
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      fontWeight: 500,
      background: type === t.toLowerCase() ? "var(--surface-elevated-2)" : "transparent",
      color: type === t.toLowerCase() ? "var(--text-high)" : "var(--text-mid)"
    }
  }, t))),
  // Margin mode
  React.createElement("div", {
    style: {
      display: "flex",
      gap: 8
    }
  }, React.createElement("div", {
    style: {
      flex: 1,
      padding: "7px 10px",
      borderRadius: 6,
      background: "var(--surface-elevated-1)",
      border: "1px solid var(--stroke-default)",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      cursor: "pointer"
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      color: "var(--text-mid)"
    }
  }, "Cross"), React.createElement(Icon, {
    name: "chevronDown",
    size: 12,
    color: "var(--text-low)"
  })), React.createElement("div", {
    style: {
      flex: 1,
      padding: "7px 10px",
      borderRadius: 6,
      background: "var(--surface-elevated-1)",
      border: "1px solid var(--stroke-default)",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      cursor: "pointer"
    }
  }, React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      color: "var(--text-mid)"
    }
  }, "10x"), React.createElement(Icon, {
    name: "chevronDown",
    size: 12,
    color: "var(--text-low)"
  }))),
  // Inputs
  type === "limit" && inputRow("Price", price, setPrice, "USDC"), inputRow("Size", size, setSize, "BTC"),
  // Size slider
  React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 6,
      paddingTop: 4
    }
  }, React.createElement("div", {
    style: {
      position: "relative",
      height: 16,
      display: "flex",
      alignItems: "center"
    }
  }, React.createElement("div", {
    style: {
      position: "absolute",
      left: 0,
      right: 0,
      height: 2,
      background: "var(--white-15)",
      borderRadius: 1
    }
  }), React.createElement("div", {
    style: {
      position: "absolute",
      left: 0,
      width: "45%",
      height: 2,
      background: accent,
      borderRadius: 1
    }
  }), [0, 25, 50, 75, 100].map(p => React.createElement("div", {
    key: p,
    style: {
      position: "absolute",
      left: `${p}%`,
      transform: "translateX(-50%)",
      width: 8,
      height: 8,
      borderRadius: "50%",
      background: p <= 45 ? accent : "var(--surface-elevated-2)",
      border: "1px solid " + (p <= 45 ? accent : "var(--stroke-subtle)")
    }
  }))), React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      fontFamily: "var(--font-mono)",
      fontSize: 9,
      color: "var(--text-low)"
    }
  }, ["0%", "25%", "50%", "75%", "100%"].map(p => React.createElement("span", {
    key: p
  }, p)))),
  // Reduce only
  React.createElement("label", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      cursor: "pointer",
      padding: "4px 0"
    }
  }, React.createElement("span", {
    onClick: () => setReduceOnly(!reduceOnly),
    style: {
      width: 28,
      height: 16,
      borderRadius: 10,
      position: "relative",
      background: reduceOnly ? "var(--accent)" : "var(--white-15)",
      transition: "all 200ms"
    }
  }, React.createElement("span", {
    style: {
      position: "absolute",
      width: 12,
      height: 12,
      borderRadius: "50%",
      background: "white",
      top: 2,
      left: reduceOnly ? 14 : 2,
      transition: "all 200ms"
    }
  })), React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      color: "var(--text-mid)"
    }
  }, "Reduce only")),
  // Order summary
  React.createElement("div", {
    style: {
      padding: 10,
      background: "var(--surface-elevated-1)",
      borderRadius: 8,
      display: "flex",
      flexDirection: "column",
      gap: 6
    }
  }, [["Order value", "$2,160.93"], ["Margin required", "$216.09"], ["Liquidation price", "$38,948.10"], ["Est. fees", "$1.08"]].map(([k, v]) => React.createElement("div", {
    key: k,
    style: {
      display: "flex",
      justifyContent: "space-between",
      fontFamily: "var(--font-sans)",
      fontSize: 11
    }
  }, React.createElement("span", {
    style: {
      color: "var(--text-low)"
    }
  }, k), React.createElement("span", {
    style: {
      color: "var(--text-high)",
      fontFamily: "var(--font-mono)",
      fontVariantNumeric: "tabular-nums"
    }
  }, v)))),
  // CTA
  React.createElement(Button, {
    variant: isLong ? "positive" : "negative",
    style: {
      width: "100%",
      justifyContent: "center"
    }
  }, (isLong ? "Long" : "Short") + " BTC-USD · 10x")));
};
Object.assign(window, {
  OrderForm
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/OrderForm.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/PositionsPanel.jsx
try { (() => {
// GTE Web UI Kit — Positions / Orders table
/* global React, Badge, Button */
const {
  useState: useStatePos
} = React;
const PositionsPanel = () => {
  const [tab, setTab] = useStatePos("positions");
  const tabs = [["positions", "Positions", 2], ["orders", "Open orders", 1], ["history", "History", 14], ["balances", "Balances", null]];
  return React.createElement("div", {
    style: {
      background: "var(--surface-elevated-2)",
      borderTop: "1px solid var(--stroke-default)",
      height: 240,
      display: "flex",
      flexDirection: "column"
    }
  }, React.createElement("div", {
    style: {
      display: "flex",
      gap: 0,
      padding: "0 4px",
      borderBottom: "1px solid var(--stroke-default)",
      flexShrink: 0
    }
  }, tabs.map(([k, label, n]) => React.createElement("button", {
    key: k,
    onClick: () => setTab(k),
    style: {
      padding: "10px 14px",
      background: "transparent",
      border: "none",
      cursor: "pointer",
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 500,
      letterSpacing: 0.3,
      color: tab === k ? "var(--text-high)" : "var(--text-mid)",
      borderBottom: tab === k ? "2px solid var(--accent)" : "2px solid transparent",
      display: "inline-flex",
      alignItems: "center",
      gap: 6
    }
  }, label, n !== null && React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      padding: "1px 5px",
      borderRadius: 3,
      background: "var(--white-15)",
      color: "var(--text-mid)"
    }
  }, n)))), React.createElement("div", {
    style: {
      flex: 1,
      overflow: "auto"
    }
  }, tab === "positions" && React.createElement(PositionsTable), tab === "orders" && React.createElement(OrdersTable), tab === "history" && React.createElement(HistoryTable), tab === "balances" && React.createElement(BalancesTable)));
};
const TableHead = ({
  cols
}) => React.createElement("div", {
  style: {
    display: "grid",
    gridTemplateColumns: cols.map(c => c.w || "1fr").join(" "),
    padding: "8px 16px",
    fontFamily: "var(--font-sans)",
    fontSize: 10,
    letterSpacing: 0.4,
    color: "var(--text-low)",
    fontWeight: 500,
    borderBottom: "1px solid var(--stroke-default)"
  }
}, cols.map((c, i) => React.createElement("span", {
  key: i,
  style: {
    textAlign: c.align || "left"
  }
}, c.label)));
const TableRow = ({
  cols,
  cells
}) => React.createElement("div", {
  style: {
    display: "grid",
    gridTemplateColumns: cols.map(c => c.w || "1fr").join(" "),
    padding: "10px 16px",
    fontFamily: "var(--font-mono)",
    fontSize: 12,
    fontVariantNumeric: "tabular-nums",
    color: "var(--text-high)",
    borderBottom: "1px solid var(--stroke-default)",
    alignItems: "center"
  }
}, cells.map((cell, i) => React.createElement("span", {
  key: i,
  style: {
    textAlign: cols[i].align || "left",
    color: cols[i].color
  }
}, cell)));
const PositionsTable = () => {
  const cols = [{
    label: "Market",
    w: "1.2fr"
  }, {
    label: "Side",
    w: "0.6fr"
  }, {
    label: "Size",
    w: "1fr",
    align: "right"
  }, {
    label: "Entry",
    w: "1fr",
    align: "right"
  }, {
    label: "Mark",
    w: "1fr",
    align: "right"
  }, {
    label: "Liq.",
    w: "1fr",
    align: "right"
  }, {
    label: "Margin",
    w: "1fr",
    align: "right"
  }, {
    label: "PnL (ROE)",
    w: "1.2fr",
    align: "right"
  }, {
    label: "",
    w: "140px",
    align: "right"
  }];
  return React.createElement(React.Fragment, null, React.createElement(TableHead, {
    cols
  }), React.createElement(TableRow, {
    cols,
    cells: [React.createElement("span", {
      key: "m",
      style: {
        fontFamily: "var(--font-sans)",
        fontWeight: 600
      }
    }, "BTC-USD"), React.createElement(Badge, {
      key: "s",
      tone: "long",
      dot: true
    }, "Long 10x"), "0.12 BTC", "42,980.00", "43,218.50", "38,948.10", "$516.22", React.createElement("span", {
      key: "p",
      style: {
        color: "var(--text-positive)"
      }
    }, "+$28.62 (+5.55%)"), React.createElement("div", {
      key: "b",
      style: {
        display: "flex",
        gap: 6,
        justifyContent: "flex-end"
      }
    }, React.createElement(Button, {
      variant: "tertiary",
      size: "sm"
    }, "TP/SL"), React.createElement(Button, {
      variant: "tertiary",
      size: "sm"
    }, "Close"))]
  }), React.createElement(TableRow, {
    cols,
    cells: [React.createElement("span", {
      key: "m",
      style: {
        fontFamily: "var(--font-sans)",
        fontWeight: 600
      }
    }, "ETH-USD"), React.createElement(Badge, {
      key: "s",
      tone: "short",
      dot: true
    }, "Short 5x"), "1.50 ETH", "2,314.50", "2,284.17", "2,612.10", "$342.00", React.createElement("span", {
      key: "p",
      style: {
        color: "var(--text-positive)"
      }
    }, "+$45.50 (+13.30%)"), React.createElement("div", {
      key: "b",
      style: {
        display: "flex",
        gap: 6,
        justifyContent: "flex-end"
      }
    }, React.createElement(Button, {
      variant: "tertiary",
      size: "sm"
    }, "TP/SL"), React.createElement(Button, {
      variant: "tertiary",
      size: "sm"
    }, "Close"))]
  }));
};
const OrdersTable = () => {
  const cols = [{
    label: "Time",
    w: "1fr"
  }, {
    label: "Market",
    w: "1fr"
  }, {
    label: "Side",
    w: "0.7fr"
  }, {
    label: "Type",
    w: "0.8fr"
  }, {
    label: "Price",
    w: "1fr",
    align: "right"
  }, {
    label: "Size",
    w: "1fr",
    align: "right"
  }, {
    label: "Filled",
    w: "1fr",
    align: "right"
  }, {
    label: "",
    w: "90px",
    align: "right"
  }];
  return React.createElement(React.Fragment, null, React.createElement(TableHead, {
    cols
  }), React.createElement(TableRow, {
    cols,
    cells: ["12:48:07", React.createElement("span", {
      key: "m",
      style: {
        fontFamily: "var(--font-sans)",
        fontWeight: 600
      }
    }, "SOL-USD"), React.createElement(Badge, {
      key: "s",
      tone: "long"
    }, "Long"), React.createElement(Badge, {
      key: "t",
      tone: "neutral"
    }, "Limit"), "138.00", "10 SOL", "0 / 10", React.createElement(Button, {
      key: "x",
      variant: "tertiary",
      size: "sm"
    }, "Cancel")]
  }));
};
const HistoryTable = () => React.createElement("div", {
  style: {
    padding: 40,
    textAlign: "center",
    fontFamily: "var(--font-sans)",
    fontSize: 12,
    color: "var(--text-low)"
  }
}, "14 historical fills · connect wallet for full history");
const BalancesTable = () => React.createElement("div", {
  style: {
    padding: 40,
    textAlign: "center",
    fontFamily: "var(--font-sans)",
    fontSize: 12,
    color: "var(--text-low)"
  }
}, "USDC 12,482.30 · ETH 0.82 · BTC 0.00");
Object.assign(window, {
  PositionsPanel
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/PositionsPanel.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/Primitives.jsx
try { (() => {
// GTE Web UI Kit — Primitives
// These are cosmetic recreations of /src/ui/* — not production code.
/* global React */
const {
  useState
} = React;

// ─── Button ──────────────────────────────────────────────
const Button = ({
  variant = "primary",
  size = "md",
  children,
  onClick,
  icon,
  disabled,
  style
}) => {
  // sm 28 / md 32 / lg 40 per references/components.md; product UI never uses larger than md
  const h = size === "sm" ? 28 : size === "lg" ? 40 : 32;
  const px = size === "sm" ? 10 : size === "lg" ? 20 : 14;
  const base = {
    height: h,
    padding: `0 ${px}px`,
    borderRadius: 8,
    fontFamily: "var(--font-sans)",
    fontWeight: 500,
    fontSize: size === "sm" ? 12 : 13,
    letterSpacing: 0.26,
    lineHeight: 1,
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    border: "1px solid transparent",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1,
    transition: "all 200ms ease-out",
    color: "var(--text-high)",
    whiteSpace: "nowrap"
  };
  const v = {
    primary: {
      background: "var(--gradient-button-primary)",
      color: "var(--text-action-primary)",
      boxShadow: "var(--shadow-button)"
    },
    positive: {
      background: "linear-gradient(65deg, var(--surface-action-positive) 0%, var(--surface-action-positive-hover) 100%)",
      color: "var(--text-high)",
      boxShadow: "0 2px 12px var(--positive-muted)"
    },
    negative: {
      background: "linear-gradient(65deg, var(--surface-action-negative) 0%, var(--surface-action-negative-hover) 100%)",
      color: "var(--text-high)",
      boxShadow: "0 2px 12px var(--negative-muted)"
    },
    secondary: {
      background: "var(--surface-action-secondary)",
      color: "var(--accent-light)",
      borderColor: "var(--accent-muted)"
    },
    tertiary: {
      background: "var(--surface-action-tertiary)",
      color: "var(--text-action-tertiary)",
      borderColor: "var(--stroke-default)"
    },
    ghost: {
      background: "transparent",
      color: "var(--text-action-tertiary)"
    }
  }[variant];
  return React.createElement("button", {
    onClick,
    disabled,
    style: {
      ...base,
      ...v,
      ...style
    }
  }, icon, children);
};

// ─── Icon (Lucide-style inline) ─────────────────────────────
const Icon = ({
  name,
  size = 16,
  color = "currentColor",
  style
}) => {
  const paths = {
    chevronDown: "M6 9l6 6 6-6",
    chevronRight: "M9 6l6 6-6 6",
    chevronLeft: "M15 6l-6 6 6 6",
    search: "M11 4a7 7 0 110 14 7 7 0 010-14zM21 21l-4.3-4.3",
    menu: "M3 6h18M3 12h18M3 18h18",
    x: "M18 6L6 18M6 6l12 12",
    plus: "M12 5v14M5 12h14",
    minus: "M5 12h14",
    arrowUp: "M12 19V5M5 12l7-7 7 7",
    arrowDown: "M12 5v14M19 12l-7 7-7-7",
    star: "M12 2l3 7 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z",
    wallet: "M3 7h18v12a1 1 0 01-1 1H4a1 1 0 01-1-1V7zm0 0V5a1 1 0 011-1h14M17 13h.01",
    settings: "M12 15a3 3 0 100-6 3 3 0 000 6zM19 12a7 7 0 01-.14 1.4l2 1.56-2 3.46-2.36-.94a7 7 0 01-2.42 1.4L13.72 22h-3.44l-.36-2.12a7 7 0 01-2.42-1.4L5.14 19.4l-2-3.46 2-1.56A7 7 0 015 12c0-.48.05-.94.14-1.4l-2-1.56 2-3.46 2.36.94a7 7 0 012.42-1.4L10.28 2h3.44l.36 2.12a7 7 0 012.42 1.4l2.36-.94 2 3.46-2 1.56c.1.46.14.92.14 1.4z",
    bell: "M18 16v-5a6 6 0 10-12 0v5l-2 3h16l-2-3zM10 20a2 2 0 004 0",
    user: "M16 10a4 4 0 11-8 0 4 4 0 018 0zM4 20a8 8 0 0116 0",
    globe: "M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20M12 2a15 15 0 010 20M12 2a15 15 0 000 20",
    bolt: "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
    sparkle: "M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1",
    copy: "M8 4h10a2 2 0 012 2v10M4 8h10a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V10a2 2 0 012-2z",
    external: "M15 3h6v6M10 14L21 3M21 14v5a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h5",
    info: "M12 21a9 9 0 100-18 9 9 0 000 18zM12 16v-4M12 8h.01",
    refresh: "M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"
  };
  const filled = name === "bolt" || name === "sparkle" || name === "star";
  return React.createElement("svg", {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: filled ? color : "none",
    stroke: color,
    strokeWidth: 1.5,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    style
  }, React.createElement("path", {
    d: paths[name] || ""
  }));
};

// ─── Badge / Pill ───────────────────────────────────────
// Border-only, no fill, normal/sentence case — matches preview/badges.html
const Badge = ({
  tone = "neutral",
  children,
  dot
}) => {
  const tones = {
    long: {
      border: "var(--positive-muted)",
      fg: "var(--positive)"
    },
    short: {
      border: "var(--negative-muted)",
      fg: "var(--negative)"
    },
    brand: {
      border: "var(--accent-muted)",
      fg: "var(--accent-light)"
    },
    neutral: {
      border: "var(--stroke-subtle)",
      fg: "var(--text-mid)"
    }
  }[tone] || {
    border: "var(--stroke-subtle)",
    fg: "var(--text-mid)"
  };
  return React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      color: tones.fg,
      fontSize: 12,
      fontWeight: 400,
      letterSpacing: 0.48,
      lineHeight: 1.4,
      padding: "4px 8px",
      borderRadius: "var(--radius-regular)",
      fontFamily: "var(--font-sans)",
      border: "1px solid " + tones.border
    }
  }, dot && React.createElement("span", {
    style: {
      width: 6,
      height: 6,
      borderRadius: 99,
      background: "currentColor",
      boxShadow: "0 0 8px currentColor"
    }
  }), children);
};

// ─── Token Icon (real SVGs) ────────────────────────────
const TokenIcon = ({
  symbol,
  size = 20
}) => {
  const map = {
    ETH: "assets/tokens/eth.svg",
    USDC: "assets/tokens/usdc.svg",
    USDT: "assets/tokens/usdt.svg",
    BTC: "assets/tokens/placeholder.svg",
    SOL: "assets/tokens/placeholder.svg"
  };
  return React.createElement("img", {
    src: map[symbol] || map.BTC,
    width: size,
    height: size,
    alt: symbol,
    style: {
      borderRadius: "50%",
      background: "var(--surface-elevated-2)"
    }
  });
};
Object.assign(window, {
  Button,
  Icon,
  Badge,
  TokenIcon
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/Primitives.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/RecentTrades.jsx
try { (() => {
// GTE Web UI Kit — Recent trades tape
/* global React */
const {
  useMemo: useMemoTape
} = React;
const RecentTrades = () => {
  const rows = useMemoTape(() => {
    const out = [];
    for (let i = 0; i < 24; i++) {
      const side = Math.random() > 0.5 ? "buy" : "sell";
      const price = 43218.5 + (Math.random() - 0.5) * 20;
      const size = +(Math.random() * 2.2).toFixed(3);
      const m = 48 - Math.floor(i * 2 + Math.random() * 2);
      out.push({
        side,
        price,
        size,
        time: `12:${String(m).padStart(2, "0")}:${String(Math.floor(Math.random() * 60)).padStart(2, "0")}`
      });
    }
    return out;
  }, []);
  return React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      height: "100%"
    }
  }, React.createElement("div", {
    style: {
      padding: "10px 12px",
      borderBottom: "1px solid var(--stroke-default)",
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 600,
      color: "var(--text-high)",
      letterSpacing: 0.3
    }
  }, "Recent trades"), React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr 1fr",
      padding: "6px 10px",
      fontFamily: "var(--font-sans)",
      fontSize: 9,
      color: "var(--text-low)",
      letterSpacing: 0.4
    }
  }, React.createElement("span", null, "Price"), React.createElement("span", {
    style: {
      textAlign: "center"
    }
  }, "Size"), React.createElement("span", {
    style: {
      textAlign: "right"
    }
  }, "Time")), React.createElement("div", {
    style: {
      flex: 1,
      overflow: "hidden"
    }
  }, rows.map((r, i) => React.createElement("div", {
    key: i,
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr 1fr",
      padding: "3px 10px",
      fontFamily: "var(--font-mono)",
      fontSize: 11,
      fontVariantNumeric: "tabular-nums"
    }
  }, React.createElement("span", {
    style: {
      color: r.side === "buy" ? "var(--text-positive)" : "var(--text-negative)"
    }
  }, r.price.toFixed(2)), React.createElement("span", {
    style: {
      textAlign: "center",
      color: "var(--text-mid)"
    }
  }, r.size.toFixed(3)), React.createElement("span", {
    style: {
      textAlign: "right",
      color: "var(--text-low)"
    }
  }, r.time)))));
};
Object.assign(window, {
  RecentTrades
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/RecentTrades.jsx", error: String((e && e.message) || e) }); }

// ui_kits/web/TradingChart.jsx
try { (() => {
// GTE Web UI Kit — Trading chart (placeholder candles)
/* global React */
const {
  useMemo: useMemoChart
} = React;
const TradingChart = ({
  height = 380
}) => {
  const candles = useMemoChart(() => {
    const out = [];
    let p = 43100;
    for (let i = 0; i < 80; i++) {
      const o = p;
      const move = (Math.sin(i * 0.35) + (Math.random() - 0.5)) * 80;
      const c = o + move;
      const hi = Math.max(o, c) + Math.random() * 40;
      const lo = Math.min(o, c) - Math.random() * 40;
      out.push({
        o,
        c,
        hi,
        lo
      });
      p = c;
    }
    return out;
  }, []);
  const all = candles.flatMap(k => [k.hi, k.lo]);
  const max = Math.max(...all),
    min = Math.min(...all);
  const y = v => 20 + (max - v) / (max - min) * (height - 60);
  const cw = 760 / candles.length;
  return React.createElement("div", {
    style: {
      background: "var(--surface-elevated-2)",
      height,
      position: "relative",
      padding: "12px",
      display: "flex",
      flexDirection: "column",
      gap: 8
    }
  },
  // Chart toolbar
  React.createElement("div", {
    style: {
      display: "flex",
      gap: 4,
      alignItems: "center"
    }
  }, ["1m", "5m", "15m", "1h", "4h", "1D"].map((t, i) => React.createElement("button", {
    key: t,
    style: {
      padding: "4px 10px",
      borderRadius: 6,
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      fontWeight: 500,
      background: i === 2 ? "var(--surface-elevated-2)" : "transparent",
      color: i === 2 ? "var(--text-high)" : "var(--text-mid)",
      border: "1px solid " + (i === 2 ? "var(--stroke-subtle)" : "transparent"),
      cursor: "pointer"
    }
  }, t)), React.createElement("span", {
    style: {
      marginLeft: 12,
      fontFamily: "var(--font-sans)",
      fontSize: 10,
      color: "var(--text-low)",
      letterSpacing: 0.4
    }
  }, "Indicators"), ["EMA 21", "VOL", "RSI"].map((t, i) => React.createElement("button", {
    key: t,
    style: {
      padding: "4px 10px",
      borderRadius: 6,
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      background: "transparent",
      color: "var(--text-mid)",
      border: "1px solid var(--stroke-default)",
      cursor: "pointer"
    }
  }, t))), React.createElement("div", {
    style: {
      flex: 1,
      position: "relative",
      background: "var(--surface-elevated-1)",
      borderRadius: 6,
      border: "1px solid var(--stroke-default)",
      overflow: "hidden"
    }
  },
  // Grid lines
  React.createElement("svg", {
    width: "100%",
    height: "100%",
    viewBox: `0 0 780 ${height - 40}`,
    preserveAspectRatio: "none",
    style: {
      position: "absolute",
      inset: 0
    }
  }, [0.2, 0.4, 0.6, 0.8].map(f => React.createElement("line", {
    key: f,
    x1: 0,
    x2: 780,
    y1: (height - 40) * f,
    y2: (height - 40) * f,
    stroke: "var(--stroke-default)",
    strokeDasharray: "2 4"
  })),
  // Candles
  candles.map((k, i) => {
    const up = k.c >= k.o;
    const color = up ? "var(--positive)" : "var(--negative)";
    const x = 10 + i * cw;
    return React.createElement("g", {
      key: i
    }, React.createElement("line", {
      x1: x + cw / 2,
      x2: x + cw / 2,
      y1: y(k.hi),
      y2: y(k.lo),
      stroke: color,
      strokeWidth: 1
    }), React.createElement("rect", {
      x: x + 1,
      y: Math.min(y(k.o), y(k.c)),
      width: cw - 2,
      height: Math.max(2, Math.abs(y(k.c) - y(k.o))),
      fill: color
    }));
  }),
  // Price line
  React.createElement("line", {
    x1: 0,
    x2: 780,
    y1: y(candles[candles.length - 1].c),
    y2: y(candles[candles.length - 1].c),
    stroke: "var(--accent)",
    strokeDasharray: "4 3",
    strokeWidth: 1
  })),
  // Y-axis labels
  React.createElement("div", {
    style: {
      position: "absolute",
      right: 0,
      top: 0,
      bottom: 0,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      padding: "8px 8px",
      alignItems: "flex-end",
      pointerEvents: "none"
    }
  }, ["43,500", "43,300", "43,100", "42,900"].map(v => React.createElement("span", {
    key: v,
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      color: "var(--text-low)",
      background: "var(--surface-default)",
      padding: "1px 4px",
      borderRadius: 3
    }
  }, v))),
  // Price tag
  React.createElement("div", {
    style: {
      position: "absolute",
      right: 4,
      top: y(candles[candles.length - 1].c) + 8,
      background: "var(--accent)",
      color: "var(--text-action-primary)",
      padding: "2px 6px",
      borderRadius: 3,
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      fontWeight: 600
    }
  }, candles[candles.length - 1].c.toFixed(2))));
};
Object.assign(window, {
  TradingChart
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/web/TradingChart.jsx", error: String((e && e.message) || e) }); }

})();
