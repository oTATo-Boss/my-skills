/* dither-charts.js — self-contained Bayer-dithered canvas charts for Artifacts.
   No dependencies, no framework, CSP-safe (inline this whole file in a <script>).
   Area / line / bar (stackable), hover crosshair + tooltip, flow legend,
   entrance animation (respects prefers-reduced-motion), DPR-aware, resizes.

   API:
     const chart = DitherCharts.chart(el, {
       type: 'area' | 'line' | 'bar',
       data: [{ x: '07-12', a: 12, b: 4 }, ...],
       xKey: 'x',
       series: [{ key:'a', label:'Model A', color:'orange' }, ...], // color = palette seed name
       palette: DitherCharts.PALETTES.llDark,   // or qladMonoDark / qladMonoLight / hues
       stacked: true,
       formatValue: v => String(v),   // tooltip values
       formatTick: v => String(v),    // y-axis ticks
       formatX: v => String(v),       // x-axis ticks
       yTicks: 3, xTicks: 6, legend: true, animate: true,
     });
     chart.destroy(); chart.setPalette(p); chart.setData(data);
*/
(function (global) {
  "use strict";

  var CELL = 2; // css px per dither cell
  var BAYER = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
  ].map(function (row) {
    return row.map(function (v) { return (v + 0.5) / 16; });
  });

  function mix(a, b, t) {
    return [
      Math.round(a[0] + (b[0] - a[0]) * t),
      Math.round(a[1] + (b[1] - a[1]) * t),
      Math.round(a[2] + (b[2] - a[2]) * t),
    ];
  }
  function seed(fill, toward) {
    toward = toward || [255, 255, 255];
    return { fill: fill, line: mix(fill, toward, 0.4), star: mix(fill, toward, 0.7) };
  }
  function rgb(c, k, a) {
    k = k == null ? 1 : k; a = a == null ? 1 : a;
    return "rgba(" + Math.round(c[0] * k) + "," + Math.round(c[1] * k) + "," + Math.round(c[2] * k) + "," + a + ")";
  }

  /* Palettes: named series seeds + chrome (axis ink, grid, tooltip). */
  var PALETTES = {
    /* Liquid Labs instrument panel — orange leads, tracker tokens. */
    llDark: {
      series: {
        orange: seed([255, 120, 23]),
        green:  seed([46, 232, 139]),
        blue:   seed([96, 165, 250]),
        purple: seed([167, 139, 250]),
        pink:   seed([255, 102, 125]),
        yellow: seed([250, 204, 21]),
        grey:   seed([106, 110, 113]),
      },
      order: ["orange", "green", "blue", "purple", "pink", "yellow"],
      ink: "rgb(106,110,113)",
      grid: "rgba(255,255,255,.06)",
      tooltipBg: "rgb(24,26,27)",
      tooltipBorder: "rgba(255,255,255,.15)",
      tooltipInk: "#fff",
      tooltipMuted: "rgb(166,167,168)",
    },
    /* QLAD register-D monochrome, dark ground. */
    qladMonoDark: {
      series: {
        g1: seed([236, 236, 236]), g2: seed([196, 196, 196]), g3: seed([154, 154, 154]),
        g4: seed([117, 117, 117]), g5: seed([84, 84, 84]),   g6: seed([60, 60, 60]),
        grey: seed([92, 92, 100]),
      },
      order: ["g1", "g2", "g3", "g4", "g5", "g6"],
      ink: "#666", grid: "#1F1F1F",
      tooltipBg: "#0A0A0A", tooltipBorder: "#333", tooltipInk: "#fff", tooltipMuted: "#999",
    },
    /* QLAD monochrome, light ground (ladder inverts, accents pull darker). */
    qladMonoLight: {
      series: {
        g1: seed([26, 26, 26], [0, 0, 0]), g2: seed([68, 68, 68], [0, 0, 0]),
        g3: seed([107, 107, 107], [0, 0, 0]), g4: seed([140, 140, 140], [0, 0, 0]),
        g5: seed([173, 173, 173], [0, 0, 0]), g6: seed([200, 200, 200], [0, 0, 0]),
        grey: seed([160, 160, 166], [0, 0, 0]),
      },
      order: ["g1", "g2", "g3", "g4", "g5", "g6"],
      ink: "#888", grid: "#E6E6E6",
      tooltipBg: "#fff", tooltipBorder: "#ddd", tooltipInk: "#111", tooltipMuted: "#666",
    },
    /* dither-kit's own hue wheel, for neutral/product contexts. */
    hues: {
      series: {
        green:  seed([40, 210, 110]),  blue: seed([53, 143, 243]),
        purple: seed([150, 110, 255]), pink: seed([240, 90, 190]),
        orange: seed([255, 150, 50]),  red:  seed([240, 70, 70]),
        grey:   seed([92, 92, 100]),
      },
      order: ["green", "blue", "purple", "orange", "pink", "red"],
      ink: "rgb(120,122,125)",
      grid: "rgba(128,128,128,.15)",
      tooltipBg: "rgba(20,21,22,.97)", tooltipBorder: "rgba(255,255,255,.15)",
      tooltipInk: "#fff", tooltipMuted: "rgb(166,167,168)",
    },
  };

  function niceCeil(v) {
    if (v <= 0) return 1;
    var mag = Math.pow(10, Math.floor(Math.log10(v)));
    var n = v / mag;
    var step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
    return step * mag;
  }
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  /* Deterministic per-cell hash for star placement. */
  function cellHash(c, r, s) {
    var h = (c * 73856093) ^ (r * 19349663) ^ ((s + 1) * 83492791);
    h = h >>> 0;
    return (h % 1000) / 1000;
  }

  function chart(el, opts) {
    var type = opts.type || "area";
    var data = opts.data || [];
    var xKey = opts.xKey || "x";
    var seriesDefs = opts.series || [];
    var palette = opts.palette || PALETTES.llDark;
    var stacked = opts.stacked !== false && type !== "line";
    var fmtV = opts.formatValue || String;
    var fmtT = opts.formatTick || function (v) {
      return Math.abs(v) >= 1000 && Number.isInteger(v)
        ? v.toLocaleString("en-US")
        : String(+(+v).toFixed(2));
    };
    var fmtX = opts.formatX || String;
    var yTickCount = opts.yTicks || 3;
    var xTickMax = opts.xTicks || 6;
    var reduced = typeof matchMedia !== "undefined" &&
      matchMedia("(prefers-reduced-motion: reduce)").matches;
    var animate = opts.animate !== false && !reduced;

    el.style.display = "flex";
    el.style.flexDirection = "column";
    var wrap = document.createElement("div");
    wrap.style.cssText = "position:relative;flex:1;min-height:0;width:100%;";
    var canvas = document.createElement("canvas");
    canvas.style.cssText = "display:block;width:100%;height:100%;";
    if (opts.ariaLabel) { wrap.setAttribute("role", "img"); wrap.setAttribute("aria-label", opts.ariaLabel); }
    wrap.appendChild(canvas);
    var tip = document.createElement("div");
    tip.style.cssText =
      "position:absolute;pointer-events:none;opacity:0;transition:opacity .15s ease;" +
      "font:11px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;white-space:nowrap;z-index:3;";
    wrap.appendChild(tip);
    el.appendChild(wrap);

    var legendEl = null;
    if (opts.legend !== false) {
      legendEl = document.createElement("ul");
      legendEl.style.cssText =
        "display:flex;flex-wrap:wrap;gap:6px 16px;list-style:none;margin:10px 0 0;padding:0;flex:none;" +
        "font:11px ui-monospace,SFMono-Regular,Menlo,monospace;";
      el.appendChild(legendEl);
    }

    var ctx = canvas.getContext("2d");
    var W = 0, H = 0, dpr = 1;
    var hoverIndex = null;
    var t0 = 0, raf = 0, progress = animate ? 0 : 1;
    var destroyed = false;

    var leftMargin = 44;
    function margins() {
      return { top: 8, right: 10, bottom: 20, left: opts.yTicks === 0 ? 8 : leftMargin };
    }
    function measureLeftMargin(tickStep) {
      ctx.font = "10px ui-monospace,SFMono-Regular,Menlo,monospace";
      var w = 0;
      for (var tI = 0; tI <= yTickCount; tI++) {
        w = Math.max(w, ctx.measureText(fmtT(tickStep * tI)).width);
      }
      leftMargin = Math.ceil(w) + 12;
    }

    function seedOf(def) {
      return palette.series[def.color] || palette.series.grey || seed([128, 128, 128]);
    }

    function renderLegend() {
      if (!legendEl) return;
      legendEl.innerHTML = "";
      seriesDefs.forEach(function (d) {
        var li = document.createElement("li");
        li.style.cssText = "display:flex;align-items:center;gap:6px;color:" + palette.tooltipMuted + ";";
        var sw = document.createElement("span");
        sw.style.cssText = "width:9px;height:9px;display:inline-block;background:" + rgb(seedOf(d).fill) + ";";
        li.appendChild(sw);
        li.appendChild(document.createTextNode(d.label || d.key));
        legendEl.appendChild(li);
      });
    }

    /* Geometry: per series, top/floor y (css px) per data index. */
    function computeBands() {
      var m = margins();
      var plotW = W - m.left - m.right, plotH = H - m.top - m.bottom;
      var totals = data.map(function (row) {
        if (!stacked) return 0;
        return seriesDefs.reduce(function (n, d) { return n + (+row[d.key] || 0); }, 0);
      });
      var rawMax;
      if (stacked) rawMax = Math.max.apply(null, [0].concat(totals));
      else rawMax = Math.max.apply(null, [0].concat(data.map(function (row) {
        return Math.max.apply(null, seriesDefs.map(function (d) { return +row[d.key] || 0; }));
      })));
      var tickStep = niceCeil(rawMax / yTickCount || 1);
      var maxV = tickStep * yTickCount;
      var y = function (v) { return m.top + plotH - (v / maxV) * plotH; };
      var bands = seriesDefs.map(function () { return { top: [], floor: [] }; });
      data.forEach(function (row, i) {
        var acc = 0;
        seriesDefs.forEach(function (d, s) {
          var v = +row[d.key] || 0;
          if (stacked) {
            bands[s].floor[i] = y(acc);
            acc += v;
            bands[s].top[i] = y(acc);
          } else {
            bands[s].top[i] = y(v);
            bands[s].floor[i] = y(0);
          }
        });
      });
      return { m: m, plotW: plotW, plotH: plotH, maxV: maxV, tickStep: tickStep, y: y, bands: bands };
    }

    function xAt(g, i) {
      if (type === "bar") {
        var band = g.plotW / Math.max(data.length, 1);
        return g.m.left + i * band + band / 2;
      }
      if (data.length <= 1) return g.m.left + g.plotW / 2;
      return g.m.left + (i / (data.length - 1)) * g.plotW;
    }
    /* Linear interp of a band curve at a css-px x. */
    function curveAt(g, arr, px) {
      if (data.length <= 1) return arr[0] != null ? arr[0] : g.m.top + g.plotH;
      var t = (px - g.m.left) / g.plotW * (data.length - 1);
      var i = Math.max(0, Math.min(data.length - 2, Math.floor(t)));
      var f = t - i;
      return arr[i] + (arr[i + 1] - arr[i]) * f;
    }

    function paint() {
      if (!W || !H) return;
      ctx.save();
      ctx.clearRect(0, 0, W, H);
      var g = computeBands();
      if (opts.yTicks !== 0) {
        measureLeftMargin(g.tickStep);
        g = computeBands();
      }
      var m = g.m;

      /* grid + axes */
      ctx.strokeStyle = palette.grid;
      ctx.lineWidth = 1;
      ctx.font = "10px ui-monospace,SFMono-Regular,Menlo,monospace";
      ctx.fillStyle = palette.ink;
      if (opts.yTicks !== 0) {
        for (var tI = 0; tI <= yTickCount; tI++) {
          var tv = g.tickStep * tI;
          var ty = g.y(tv);
          ctx.beginPath(); ctx.moveTo(m.left, Math.round(ty) + 0.5); ctx.lineTo(W - m.right, Math.round(ty) + 0.5); ctx.stroke();
          ctx.textAlign = "right"; ctx.textBaseline = "middle";
          ctx.fillText(fmtT(tv), m.left - 6, ty);
        }
      } else {
        ctx.beginPath(); ctx.moveTo(m.left, Math.round(g.y(0)) + 0.5); ctx.lineTo(W - m.right, Math.round(g.y(0)) + 0.5); ctx.stroke();
      }
      var step = Math.max(1, Math.ceil(data.length / xTickMax));
      ctx.textAlign = "center"; ctx.textBaseline = "alphabetic";
      for (var i = 0; i < data.length; i += step) {
        ctx.fillText(fmtX(data[i][xKey]), xAt(g, i), H - 6);
      }

      /* dither field */
      var cols = Math.floor(g.plotW / CELL);
      var reveal = progress * cols;
      var glowCells = 12;

      for (var s = 0; s < seriesDefs.length; s++) {
        var sd = seedOf(seriesDefs[s]);
        if (type === "bar") {
          var band = g.plotW / Math.max(data.length, 1);
          var gap = Math.max(2, Math.min(8, band * 0.12));
          for (var bi = 0; bi < data.length; bi++) {
            var x0 = m.left + bi * band + gap / 2, x1 = m.left + (bi + 1) * band - gap / 2;
            var c0 = Math.floor((x0 - m.left) / CELL), c1 = Math.floor((x1 - m.left) / CELL);
            paintBandCols(g, sd, s, c0, c1, function () { return g.bands[s].top[bi]; }, function () { return g.bands[s].floor[bi]; }, reveal, false, glowCells);
          }
        } else {
          paintBandCols(g, sd, s, 0, cols, function (px) { return curveAt(g, g.bands[s].top, px); }, function (px) { return curveAt(g, g.bands[s].floor, px); }, reveal, type === "line", glowCells);
        }
      }

      /* hover crosshair */
      if (hoverIndex != null && data.length) {
        var hx = xAt(g, hoverIndex);
        ctx.fillStyle = "rgba(255,255,255,.12)";
        ctx.fillRect(Math.round(hx) - 1, m.top, 2, g.plotH);
      }
      ctx.restore();
    }

    /* Paint dithered cells for one series band across a column range. */
    function paintBandCols(g, sd, sIdx, c0, c1, topAt, floorAt, reveal, lineMode, glowCells) {
      var m = g.m;
      for (var c = c0; c < c1; c++) {
        if (c > reveal) break;
        var edge = Math.max(0, Math.min(1, (reveal - c) / 8)); // dissolve at leading edge
        var px = m.left + c * CELL + CELL / 2;
        var topY = topAt(px), floorY = floorAt(px);
        if (!(floorY > topY)) continue;
        var rTop = Math.floor((topY - m.top) / CELL), rFloor = Math.floor((floorY - m.top) / CELL);
        var depthCells = lineMode ? Math.min(glowCells, rFloor - rTop) : rFloor - rTop;
        for (var r = rTop; r <= rTop + depthCells && r <= rFloor; r++) {
          var depth = depthCells > 0 ? (r - rTop) / depthCells : 0;
          var intensity, k;
          if (lineMode) { intensity = Math.pow(1 - depth, 2) * 0.85; k = 1 - depth * 0.3; }
          else { intensity = 1 - depth * 0.72; k = 1 - depth * 0.35; }
          intensity *= edge;
          if (r === rTop) {
            ctx.fillStyle = rgb(sd.line, 1, edge);
            ctx.fillRect(m.left + c * CELL, m.top + r * CELL, CELL, CELL);
            continue;
          }
          if (BAYER[r % 4][c % 4] < intensity) {
            ctx.fillStyle = rgb(sd.fill, k, 0.95 * edge);
            ctx.fillRect(m.left + c * CELL, m.top + r * CELL, CELL, CELL);
          } else if (cellHash(c, r, sIdx) < 0.015 && depth > 0.05) {
            ctx.fillStyle = rgb(sd.star, 1, 0.8 * edge);
            ctx.fillRect(m.left + c * CELL, m.top + r * CELL, CELL, CELL);
          }
        }
      }
    }

    function frame(ts) {
      if (destroyed) return;
      if (!t0) t0 = ts;
      var t = Math.min(1, (ts - t0) / 800);
      progress = easeOutCubic(t);
      paint();
      if (t < 1) raf = requestAnimationFrame(frame);
    }

    function resize() {
      var rect = wrap.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      dpr = Math.min(2, global.devicePixelRatio || 1);
      W = Math.round(rect.width); H = Math.round(rect.height);
      canvas.width = W * dpr; canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      paint();
    }

    function indexFromEvent(ev) {
      var rect = canvas.getBoundingClientRect();
      var g = computeBands();
      var px = ev.clientX - rect.left;
      if (data.length <= 1) return data.length ? 0 : null;
      if (type === "bar") {
        var band = g.plotW / data.length;
        var i = Math.floor((px - g.m.left) / band);
        return i >= 0 && i < data.length ? i : null;
      }
      var t = (px - g.m.left) / g.plotW * (data.length - 1);
      var idx = Math.round(t);
      return idx >= 0 && idx < data.length ? idx : null;
    }

    function onMove(ev) {
      var i = indexFromEvent(ev);
      if (i === hoverIndex) return;
      hoverIndex = i;
      paint();
      if (i == null) { tip.style.opacity = "0"; return; }
      var row = data[i];
      var html = '<div style="color:' + palette.tooltipMuted + ';margin-bottom:4px;">' + fmtX(row[xKey]) + "</div>";
      seriesDefs.forEach(function (d) {
        html += '<div style="display:flex;align-items:center;gap:6px;color:' + palette.tooltipInk + ';">' +
          '<span style="width:8px;height:8px;background:' + rgb(seedOf(d).fill) + ';"></span>' +
          '<span style="color:' + palette.tooltipMuted + ';">' + (d.label || d.key) + "</span>" +
          '<span style="margin-left:auto;padding-left:12px;">' + fmtV(+row[d.key] || 0) + "</span></div>";
      });
      tip.innerHTML = html;
      tip.style.background = palette.tooltipBg;
      tip.style.border = "1px solid " + palette.tooltipBorder;
      var g = computeBands();
      var tx = xAt(g, i);
      tip.style.opacity = "1";
      var tw = tip.offsetWidth;
      tip.style.left = Math.max(4, Math.min(W - tw - 4, tx - tw / 2)) + "px";
      tip.style.top = "6px";
    }
    function onLeave() { hoverIndex = null; tip.style.opacity = "0"; paint(); }

    canvas.addEventListener("mousemove", onMove);
    canvas.addEventListener("mouseleave", onLeave);
    var ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(resize) : null;
    if (ro) ro.observe(wrap);

    renderLegend();
    resize();
    if (animate) raf = requestAnimationFrame(frame);

    return {
      el: wrap,
      destroy: function () {
        destroyed = true;
        if (raf) cancelAnimationFrame(raf);
        if (ro) ro.disconnect();
        canvas.removeEventListener("mousemove", onMove);
        canvas.removeEventListener("mouseleave", onLeave);
        wrap.remove();
        if (legendEl) legendEl.remove();
      },
      setPalette: function (p) { palette = p; renderLegend(); paint(); },
      setData: function (d) { data = d; t0 = 0; progress = animate ? 0 : 1; if (animate) { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); } else paint(); },
    };
  }

  global.DitherCharts = { chart: chart, PALETTES: PALETTES, seed: seed, rgb: rgb };
})(typeof window !== "undefined" ? window : this);
