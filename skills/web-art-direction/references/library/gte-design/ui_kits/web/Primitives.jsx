// GTE Web UI Kit — Primitives
// These are cosmetic recreations of /src/ui/* — not production code.
/* global React */
const { useState } = React;

// ─── Button ──────────────────────────────────────────────
const Button = ({ variant = "primary", size = "md", children, onClick, icon, disabled, style }) => {
  // sm 28 / md 32 / lg 40 per references/components.md; product UI never uses larger than md
  const h = size === "sm" ? 28 : size === "lg" ? 40 : 32;
  const px = size === "sm" ? 10 : size === "lg" ? 20 : 14;
  const base = {
    height: h, padding: `0 ${px}px`, borderRadius: 8,
    fontFamily: "var(--font-sans)", fontWeight: 500, fontSize: size === "sm" ? 12 : 13,
    letterSpacing: 0.26, lineHeight: 1, display: "inline-flex", alignItems: "center",
    gap: 6, border: "1px solid transparent", cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1, transition: "all 200ms ease-out", color: "var(--text-high)",
    whiteSpace: "nowrap",
  };
  const v = {
    primary:   { background: "var(--gradient-button-primary)", color: "var(--text-action-primary)", boxShadow: "var(--shadow-button)" },
    positive:  { background: "linear-gradient(65deg, var(--surface-action-positive) 0%, var(--surface-action-positive-hover) 100%)", color: "var(--text-high)", boxShadow: "0 2px 12px var(--positive-muted)" },
    negative:  { background: "linear-gradient(65deg, var(--surface-action-negative) 0%, var(--surface-action-negative-hover) 100%)", color: "var(--text-high)", boxShadow: "0 2px 12px var(--negative-muted)" },
    secondary: { background: "var(--surface-action-secondary)", color: "var(--accent-light)", borderColor: "var(--accent-muted)" },
    tertiary:  { background: "var(--surface-action-tertiary)", color: "var(--text-action-tertiary)", borderColor: "var(--stroke-default)" },
    ghost:     { background: "transparent", color: "var(--text-action-tertiary)" },
  }[variant];
  return React.createElement("button", { onClick, disabled, style: { ...base, ...v, ...style } }, icon, children);
};

// ─── Icon (Lucide-style inline) ─────────────────────────────
const Icon = ({ name, size = 16, color = "currentColor", style }) => {
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
    refresh: "M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15",
  };
  const filled = name === "bolt" || name === "sparkle" || name === "star";
  return React.createElement("svg", { width: size, height: size, viewBox: "0 0 24 24",
    fill: filled ? color : "none", stroke: color, strokeWidth: 1.5, strokeLinecap: "round", strokeLinejoin: "round", style },
    React.createElement("path", { d: paths[name] || "" }));
};

// ─── Badge / Pill ───────────────────────────────────────
// Border-only, no fill, normal/sentence case — matches preview/badges.html
const Badge = ({ tone = "neutral", children, dot }) => {
  const tones = {
    long:    { border: "var(--positive-muted)", fg: "var(--positive)" },
    short:   { border: "var(--negative-muted)", fg: "var(--negative)" },
    brand:   { border: "var(--accent-muted)",   fg: "var(--accent-light)" },
    neutral: { border: "var(--stroke-subtle)",  fg: "var(--text-mid)" },
  }[tone] || { border: "var(--stroke-subtle)", fg: "var(--text-mid)" };
  return React.createElement("span", { style: {
    display: "inline-flex", alignItems: "center", gap: 6,
    color: tones.fg,
    fontSize: 12, fontWeight: 400, letterSpacing: 0.48, lineHeight: 1.4,
    padding: "4px 8px", borderRadius: "var(--radius-regular)",
    fontFamily: "var(--font-sans)", border: "1px solid " + tones.border,
  }},
    dot && React.createElement("span", { style: { width: 6, height: 6, borderRadius: 99, background: "currentColor", boxShadow: "0 0 8px currentColor" } }),
    children);
};

// ─── Token Icon (real SVGs) ────────────────────────────
const TokenIcon = ({ symbol, size = 20 }) => {
  const map = {
    ETH: "assets/tokens/eth.svg", USDC: "assets/tokens/usdc.svg",
    USDT: "assets/tokens/usdt.svg", BTC: "assets/tokens/placeholder.svg",
    SOL: "assets/tokens/placeholder.svg",
  };
  return React.createElement("img", { src: map[symbol] || map.BTC, width: size, height: size,
    alt: symbol, style: { borderRadius: "50%", background: "var(--surface-elevated-2)" } });
};

Object.assign(window, { Button, Icon, Badge, TokenIcon });
