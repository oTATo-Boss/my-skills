// GTE Web UI Kit — Header + Sidebar
/* global React, Button, Icon, Badge */
const { useState: useStateHeader } = React;

const Header = () => {
  return React.createElement("header", { style: {
    height: 48, background: "var(--surface-elevated-2)",
    borderBottom: "1px solid var(--stroke-default)",
    display: "flex", alignItems: "center", padding: "0 16px", gap: 24,
    flexShrink: 0,
  }},
    // Logo
    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 8 } },
      React.createElement("img", { src: "assets/logos/gte-logo-white.svg", style: { height: 18 } })
    ),
    // Primary nav
    React.createElement("nav", { style: { display: "flex", gap: 4, marginLeft: 16 } },
      ["Markets", "Trade", "Portfolio", "Earn", "Faucet"].map((n, i) =>
        React.createElement("a", { key: n, href: "#", style: {
          padding: "8px 12px", borderRadius: 6,
          fontFamily: "var(--font-sans)", fontSize: 13, fontWeight: 500,
          color: i === 1 ? "var(--text-high)" : "var(--text-mid)",
          background: i === 1 ? "var(--surface-elevated-1)" : "transparent",
          textDecoration: "none", display: "flex", alignItems: "center", gap: 6,
        }}, n, i === 3 && React.createElement(Badge, { tone: "brand" }, "New"))
      )
    ),
    // Spacer
    React.createElement("div", { style: { flex: 1 } }),
    // Search
    React.createElement("div", { style: {
      display: "flex", alignItems: "center", gap: 8, height: 30, padding: "0 10px",
      background: "var(--surface-input)", borderRadius: 8, width: 200,
      fontFamily: "var(--font-sans)", fontSize: 12, color: "var(--text-low)",
    }},
      React.createElement(Icon, { name: "search", size: 14, color: "var(--text-low)" }),
      "Search markets…",
      React.createElement("span", { style: {
        marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 10,
        padding: "2px 6px", background: "var(--white-15)", borderRadius: 4,
      }}, "⌘K")
    ),
    // Agent
    React.createElement(Button, { variant: "secondary", size: "sm",
      icon: React.createElement(Icon, { name: "sparkle", size: 14, color: "var(--accent)" })
    }, "Agent"),
    // Wallet
    React.createElement(Button, { variant: "primary", size: "sm",
      icon: React.createElement(Icon, { name: "wallet", size: 14 })
    }, "0x4A2B…9F3E"),
    // Bell
    React.createElement("button", { style: {
      width: 30, height: 30, borderRadius: 6, border: "1px solid var(--stroke-default)",
      background: "var(--surface-action-tertiary)", color: "var(--text-mid)",
      display: "inline-flex", alignItems: "center", justifyContent: "center", cursor: "pointer",
    }}, React.createElement(Icon, { name: "bell", size: 14 }))
  );
};

Object.assign(window, { Header });
