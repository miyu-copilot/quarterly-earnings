/* SpaceX (SPCX) dashboard. Vanilla JS, no dependencies. */
"use strict";

const SEGMENTS = ["space", "connectivity", "ai"];
const SEG_LABEL = { space: "Space", connectivity: "Connectivity", ai: "SI" };
const SEG_COLOR = { space: "#2a5d8a", connectivity: "#5a8a6a", ai: "#b5892e" };
const PRODUCTS = ["launch_services", "launch_development", "consumer",
  "enterprise_government", "advertising", "ai_solutions_infrastructure"];
const PROD_LABEL = {
  launch_services: "Launch Services", launch_development: "Launch & Dev",
  consumer: "Consumer", enterprise_government: "Enterprise & Gov",
  advertising: "Advertising", ai_solutions_infrastructure: "AI Infra & Sol."
};

const fmtB = (v) => v == null ? "—" : (v < 0 ? "−$" : "$") +
  (Math.abs(v) / 1000).toFixed(2) + "B";
const fmtPct = (v) => v == null ? "—" : (v > 0 ? "+" : "") + v.toFixed(1) + "%";
const fmtEps = (v) => v == null ? "—" : (v < 0 ? "−$" : "$") + Math.abs(v).toFixed(2);
const fmtSubs = (v) => v == null ? "—" : v.toFixed(1) + "M";
const fmtGw = (v) => v == null ? "—" : v.toFixed(1) + " GW";
const fmtArpu = (v) => v == null ? "—" : "$" + Math.round(v);
const fmtInt2 = (v) => v == null ? "—" : Math.round(v).toLocaleString("en-US");

/* Engine color from each quarter's filings — Starlink growth/ARPU,
   SI compute buildout, launch cadence and Starship milestones.
   Keyed by period; add the new quarter's notes when its filing lands. */
const SPCX_NOTES = {
  "Q3'26": [
    "Starship: Flight 14 was the first orbital Starship flight and the " +
    "first revenue-generating Starship mission — 26 Starlink V3 " +
    "satellites deployed, ~10x the downlink capacity added by a " +
    "Falcon 9 Starlink launch.",
    "Starlink: +1.6M subscribers in the quarter on developed-market " +
    "growth; over 3,800 aircraft now Starlink-equipped, plus hundreds " +
    "of thousands of enterprise subscribers on top of the consumer " +
    "count. After quarter-end, SpaceX agreed to acquire 800 MHz " +
    "spectrum licenses to advance Starlink Mobile (close expected " +
    "H1 2027).",
    "SI: the revenue inflection is a compute story — cloud services " +
    "agreements activated in the quarter plus the Cursor acquisition " +
    "and Grok adoption (Grok Bot, its always-on agentic system, " +
    "launched). SI operating income of $0.43B absorbed $1.2B of " +
    "Cursor share-based compensation; SI Adjusted EBITDA was $5.0B.",
    "Launch: 35 launches in Q3 (12 customer / 23 internal) and 113 " +
    "in the first nine months. Customer work included NASA's Nancy " +
    "Grace Roman Space Telescope; new pipeline signings include " +
    "three more NASA ISS Crew missions and 18 National Security " +
    "Space Launch missions.",
  ],
  "Q2'26": [
    "Starlink: subscribers doubled YoY (6.0M → 12.0M) while ARPU fell " +
    "~22% YoY — the 10-Q attributes the ARPU decline to international " +
    "expansion and lower-priced service plans.",
    "Compute: nameplate draw jumped 0.4 GW → 1.4 GW YoY as the " +
    "Colossus buildout accelerated.",
    "Launch: 38 launches (37 Falcon + 1 Starship); 485 tons to orbit.",
  ],
  "Q1'26": [
    "Starlink: 10.3M subscribers across 164 countries and ~9,600 " +
    "Starlink satellites in orbit — about 75% of all active " +
    "maneuverable satellites (S-1).",
    "Compute: nameplate draw crossed 1 GW (1.0 GW vs 0.3 GW a year " +
    "earlier).",
  ],
};

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

/* ---------- canvas charts ---------- */
function setupCanvas(id) {
  const c = document.getElementById(id);
  const dpr = window.devicePixelRatio || 1;
  const w = c.clientWidth, h = c.clientHeight;
  c.width = w * dpr; c.height = h * dpr;
  const ctx = c.getContext("2d");
  ctx.scale(dpr, dpr);
  return [ctx, w, h, c];
}

function tip() {
  let t = document.getElementById("chart-tip");
  if (!t) {
    t = document.createElement("div");
    t.id = "chart-tip";
    document.body.appendChild(t);
  }
  return t;
}

function showTip(x, y, html) {
  const t = tip();
  t.innerHTML = html;
  t.style.display = "block";
  const tw = t.offsetWidth || 180, th = t.offsetHeight || 90;
  t.style.left = Math.min(x + 14, window.innerWidth - tw - 8) + "px";
  t.style.top = Math.min(y + 14, window.innerHeight - th - 8) + "px";
}

function hideTip() {
  const t = document.getElementById("chart-tip");
  if (t) t.style.display = "none";
}

function moneyRow(label, value) {
  return `<div>${label}: <b>${value}</b></div>`;
}

function drawStackedBars(id, periods, getSegs) {
  const [ctx, W, H, c] = setupCanvas(id);
  const padL = 52, padB = 24, padT = 10;
  const max = Math.max(...periods.map((p) =>
    SEGMENTS.reduce((a, s) => a + getSegs(p)[s], 0)));
  const cw = (W - padL - 10) / periods.length;
  const bw = Math.min(64, cw * 0.6);
  ctx.fillStyle = "#666666"; ctx.font = "11px sans-serif";
  ctx.strokeStyle = "#cccccc"; ctx.fillStyle = "#666666";
  for (let g = 0; g <= 4; g++) {
    const v = max * g / 4, y = H - padB - (H - padB - padT) * g / 4;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - 4, y); ctx.stroke();
    ctx.fillText("$" + (v / 1000).toFixed(1) + "B", 2, y + 4);
  }
  periods.forEach((p, i) => {
    const segs = getSegs(p);
    let y0 = H - padB;
    const total = SEGMENTS.reduce((a, s) => a + segs[s], 0);
    SEGMENTS.forEach((s) => {
      const h = (H - padB - padT) * segs[s] / max;
      y0 -= h;
      ctx.fillStyle = SEG_COLOR[s];
      ctx.fillRect(padL + i * cw + (cw - bw) / 2, y0, bw, h);
    });
    ctx.fillStyle = "#111111";
    ctx.fillText(p.period, padL + i * cw + (cw - bw) / 2, H - 8);
    ctx.fillStyle = "#666666";
    ctx.fillText("$" + (total / 1000).toFixed(2) + "B",
      padL + i * cw + (cw - bw) / 2, H - padB - (H - padB - padT) * total / max - 4);
  });
  c.addEventListener("mousemove", (e) => {
    const r = c.getBoundingClientRect();
    const cw2 = (r.width - padL - 10) / periods.length;
    const i = Math.floor((e.clientX - r.left - padL) / cw2);
    if (e.clientX - r.left < padL || i < 0 || i >= periods.length) { hideTip(); return; }
    const p = periods[i];
    const segs = getSegs(p);
    const total = SEGMENTS.reduce((a, s) => a + segs[s], 0);
    showTip(e.clientX, e.clientY,
      `<div class="t-title">${p.period}</div>` +
      SEGMENTS.map((s) => moneyRow(SEG_LABEL[s], fmtB(segs[s]))).join("") +
      moneyRow("Total", fmtB(total)));
  });
  c.addEventListener("mouseleave", hideTip);
}

function drawLines(id, periods, series) {
  const [ctx, W, H, c] = setupCanvas(id);
  const padL = 52, padB = 24, padT = 10;
  const all = series.flatMap((s) => periods.map((p) => s.get(p)).filter((v) => v != null));
  const lo = Math.min(0, ...all), hi = Math.max(...all);
  const Y = (v) => H - padB - (H - padB - padT) * (v - lo) / (hi - lo || 1);
  ctx.font = "11px sans-serif"; ctx.strokeStyle = "#cccccc"; ctx.fillStyle = "#666666";
  for (let g = 0; g <= 4; g++) {
    const v = lo + (hi - lo) * g / 4, y = Y(v);
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - 4, y); ctx.stroke();
    ctx.fillText("$" + (v / 1000).toFixed(1) + "B", 2, y + 4);
  }
  const cw = (W - padL - 10) / Math.max(1, periods.length - 1);
  series.forEach((s) => {
    ctx.strokeStyle = s.color; ctx.lineWidth = 2; ctx.beginPath();
    periods.forEach((p, i) => {
      const v = s.get(p);
      if (v == null) return;
      const x = padL + i * cw, y = Y(v);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke(); ctx.lineWidth = 1;
    ctx.fillStyle = s.color;
    periods.forEach((p, i) => {
      const v = s.get(p);
      if (v == null) return;
      ctx.beginPath();
      ctx.arc(padL + i * cw, Y(v), 3, 0, 7);
      ctx.fill();
    });
    ctx.fillStyle = "#111111";
  });
  ctx.fillStyle = "#666666";
  periods.forEach((p, i) => ctx.fillText(p.period, padL + i * cw - 12, H - 8));
  c.addEventListener("mousemove", (e) => {
    const r = c.getBoundingClientRect();
    const step = (r.width - padL - 10) / Math.max(1, periods.length - 1);
    const i = Math.round((e.clientX - r.left - padL) / step);
    if (e.clientX - r.left < padL || i < 0 || i >= periods.length) { hideTip(); return; }
    const p = periods[i];
    showTip(e.clientX, e.clientY,
      `<div class="t-title">${p.period}</div>` +
      series.map((s) => moneyRow(s.label || "Value", fmtB(s.get(p)))).join(""));
  });
  c.addEventListener("mouseleave", hideTip);
}

/* ---------- sections ---------- */
function kpiCard(label, value, delta, deltaCls) {
  const d = el("div", "kpi");
  d.appendChild(el("div", "label", label));
  d.appendChild(el("div", "value", value));
  if (delta != null) d.appendChild(el("div", "delta " + (deltaCls || ""), delta));
  return d;
}

function renderKpis(root, latest) {
  const card = el("div", "card");
  card.appendChild(el("h2", null, `Latest quarter: ${latest.period} (filed ${latest.source.filed})`));
  card.appendChild(el("p", "sub", "YoY deltas vs " + (latest.yoy ? latest.yoy.vs : "—")));
  const grid = el("div", "kpis");
  grid.appendChild(kpiCard("Revenue", fmtB(latest.revenue),
    latest.yoy ? fmtPct(latest.yoy.revenue_pct) + " YoY" : null,
    latest.yoy && latest.yoy.revenue_pct >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Operating income", fmtB(latest.op_income),
    latest.yoy ? `${fmtB(latest.yoy.op_income_delta)} YoY` : null,
    latest.yoy && latest.yoy.op_income_delta >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Net income", fmtB(latest.net_income),
    latest.yoy ? `${fmtB(latest.yoy.net_income_delta)} YoY` : null,
    latest.yoy && latest.yoy.net_income_delta >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Diluted EPS", fmtEps(latest.eps_diluted)));
  grid.appendChild(kpiCard("Operating margin", fmtPct(latest.op_margin_pct)));
  grid.appendChild(kpiCard("Net margin", fmtPct(latest.net_margin_pct)));
  grid.appendChild(kpiCard("Starlink subs", fmtSubs(latest.starlink_subs_m),
    latest.yoy && latest.yoy.subs_pct != null ?
      fmtPct(latest.yoy.subs_pct) + " YoY" : null,
    latest.yoy && latest.yoy.subs_pct >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Nameplate compute", fmtGw(latest.compute_gw),
    latest.yoy && latest.yoy.compute_pct != null ?
      fmtPct(latest.yoy.compute_pct) + " YoY" : null,
    latest.yoy && latest.yoy.compute_pct >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Launches", fmtInt2(latest.launches)));
  grid.appendChild(kpiCard("Starlink ARPU", fmtArpu(latest.starlink_arpu)));
  card.appendChild(grid);
  root.appendChild(card);
}

function renderTrend(root, quarters) {
  const card = el("div", "card");
  card.appendChild(el("h2", null, "Quarterly revenue trend by segment"));
  card.appendChild(el("p", "sub", "$ millions · Space + Connectivity + SI (Super Intelligence)"));
  const c = el("canvas", "chart"); c.id = "ch-trend";
  card.appendChild(c);
  const lg = el("div", "legend");
  SEGMENTS.forEach((s) => {
    const s2 = el("span", null, SEG_LABEL[s]);
    const dot = el("span", "dot"); dot.style.background = SEG_COLOR[s];
    s2.prepend(dot); lg.appendChild(s2);
  });
  card.appendChild(lg);
  root.appendChild(card);
  drawStackedBars("ch-trend", quarters, (p) => ({
    space: p.segments.space.revenue,
    connectivity: p.segments.connectivity.revenue,
    ai: p.segments.ai.revenue,
  }));
}

function renderProfit(root, quarters, annuals) {
  const card = el("div", "card");
  card.appendChild(el("h2", null, "Profitability: operating vs net income"));
  card.appendChild(el("p", "sub", "$ millions · quarterly (solid) and annual (history)"));
  const c = el("canvas", "chart"); c.id = "ch-profit";
  card.appendChild(c);
  const lg = el("div", "legend");
  [["Operating income", "#2a5d8a"], ["Net income", "#b5892e"]].forEach(([t, col]) => {
    const s2 = el("span", null, t);
    const dot = el("span", "dot"); dot.style.background = col;
    s2.prepend(dot); lg.appendChild(s2);
  });
  card.appendChild(lg);
  root.appendChild(card);
  drawLines("ch-profit", quarters, [
    { label: "Operating income", color: "#2a5d8a", get: (p) => p.op_income },
    { label: "Net income", color: "#b5892e", get: (p) => p.net_income },
  ]);
}

function moneyTable(periods, cols) {
  const t = el("table");
  const head = el("tr");
  head.appendChild(el("th", null, "Period"));
  cols.forEach((c) => head.appendChild(el("th", null, c[0])));
  t.appendChild(head);
  periods.forEach((p, i) => {
    const tr = el("tr");
    if (i === periods.length - 1) tr.className = "latest";
    tr.appendChild(el("td", null, p.period));
    cols.forEach((c) => tr.appendChild(el("td", null, c[1](p))));
    t.appendChild(tr);
  });
  return t;
}

function renderTables(root, quarters, annuals) {
  const q = el("div", "card");
  q.appendChild(el("h2", null, "Quarterly results"));
  q.appendChild(el("p", "sub", "Revenue and income in $B · EPS in $"));
  q.appendChild(moneyTable(quarters, [
    ["Revenue", (p) => fmtB(p.revenue)],
    ["YoY", (p) => p.yoy ? fmtPct(p.yoy.revenue_pct) : "—"],
    ["Space rev", (p) => fmtB(p.segments.space.revenue)],
    ["Connectivity rev", (p) => fmtB(p.segments.connectivity.revenue)],
    ["SI rev", (p) => fmtB(p.segments.ai.revenue)],
    ["Op income", (p) => fmtB(p.op_income)],
    ["Net income", (p) => fmtB(p.net_income)],
    ["Diluted EPS", (p) => fmtEps(p.eps_diluted)],
  ]));
  root.appendChild(q);

  const a = el("div", "card");
  a.appendChild(el("h2", null, "Annual results"));
  a.appendChild(el("p", "sub", "Revenue and income in $B · EPS in $ · audited S-1 statements"));
  a.appendChild(moneyTable(annuals, [
    ["Revenue", (p) => fmtB(p.revenue)],
    ["YoY", (p) => p.yoy ? fmtPct(p.yoy.revenue_pct) : "—"],
    ["Space rev", (p) => fmtB(p.segments.space.revenue)],
    ["Connectivity rev", (p) => fmtB(p.segments.connectivity.revenue)],
    ["SI rev", (p) => fmtB(p.segments.ai.revenue)],
    ["Op income", (p) => fmtB(p.op_income)],
    ["Net income", (p) => fmtB(p.net_income)],
    ["Launches", (p) => p.launches == null ? "—" : String(p.launches)],
  ]));
  root.appendChild(a);

  const s = el("div", "card");
  s.appendChild(el("h2", null, "Segment operating income"));
  s.appendChild(el("p", "sub", "$B · Connectivity funds Space + SI losses in earlier quarters"));
  s.appendChild(moneyTable(quarters.concat(annuals.slice(-1)), [
    ["Space", (p) => fmtB(p.segments.space.op_income)],
    ["Connectivity", (p) => fmtB(p.segments.connectivity.op_income)],
    ["AI", (p) => fmtB(p.segments.ai.op_income)],
  ]));
  root.appendChild(s);

  const o = el("div", "card");
  o.appendChild(el("h2", null, "Operating metrics"));
  o.appendChild(el("p", "sub", "The company's Key Business Metrics · subscribers and compute at period end · ARPU $ per month"));
  o.appendChild(moneyTable(quarters, [
    ["Launches", (p) => fmtInt2(p.launches)],
    ["Mass to orbit (t)", (p) => fmtInt2(p.mass_to_orbit_t)],
    ["Starlink subs", (p) => fmtSubs(p.starlink_subs_m)],
    ["Starlink ARPU", (p) => fmtArpu(p.starlink_arpu)],
    ["Nameplate compute", (p) => fmtGw(p.compute_gw)],
  ]));
  root.appendChild(o);
}

function renderEngines(root, data) {
  const qs = data.quarters.filter((q) => q.starlink_subs_m != null);
  if (!qs.length) return;
  const latest = qs[qs.length - 1];
  const all = data.quarters;
  const li = all.indexOf(latest);
  const prev = li > 0 ? all[li - 1] : null;
  const card = el("div", "card");
  card.appendChild(el("h2", null, "Starlink, Compute & Launch — the engines"));
  card.appendChild(el("p", "sub",
    "Starlink subscribers (millions, period end) · nameplate compute draw " +
    "(GW, period end) · launches and mass to orbit, from each filing's " +
    "Key Business Metrics and segment operating data"));
  const ul = el("ul", "insights");
  let head = `Starlink subscribers reached ${fmtSubs(latest.starlink_subs_m)} ` +
    `in ${latest.period}`;
  if (prev && prev.starlink_subs_m != null) {
    const adds = (latest.starlink_subs_m - prev.starlink_subs_m).toFixed(1);
    head += ` (+${adds}M in the quarter)`;
  }
  if (latest.yoy && latest.yoy.subs_pct != null) {
    head += `, ${fmtPct(latest.yoy.subs_pct)} YoY`;
  }
  head += `, at ${fmtArpu(latest.starlink_arpu)}/mo ARPU — the recurring ` +
    `base under Connectivity's ${fmtB(latest.segments.connectivity.revenue)} ` +
    `of revenue and ${fmtB(latest.segments.connectivity.op_income)} of ` +
    `operating income.`;
  ul.appendChild(el("li", null, head));
  ul.appendChild(el("li", null,
    `Nameplate compute hit ${fmtGw(latest.compute_gw)}` +
    (latest.yoy && latest.yoy.compute_pct != null ?
      ` (${fmtPct(latest.yoy.compute_pct)} YoY)` : "") +
    ` — the capacity behind SI's ${fmtB(latest.segments.ai.revenue)} ` +
    `revenue quarter. Trend: ` +
    qs.map((q) => q.period + " " + fmtGw(q.compute_gw)).join(" → ") + `.`));
  ul.appendChild(el("li", null,
    `${fmtInt2(latest.launches)} launches put ` +
    `${fmtInt2(latest.mass_to_orbit_t)} tons to orbit in ${latest.period} — ` +
    `most of it internal Starlink deployment that Space revenue never ` +
    `sees, which is why launch scale grows faster than Space revenue.`));
  (SPCX_NOTES[latest.period] || []).forEach((t) =>
    ul.appendChild(el("li", null, t)));
  card.appendChild(ul);
  card.appendChild(moneyTable(qs, [
    ["Starlink subs", (p) => fmtSubs(p.starlink_subs_m)],
    ["Net adds (M)", (p) => {
      const i = all.indexOf(p);
      const pr = i > 0 ? all[i - 1] : null;
      return pr && pr.starlink_subs_m != null ?
        "+" + (p.starlink_subs_m - pr.starlink_subs_m).toFixed(1) : "—";
    }],
    ["ARPU", (p) => fmtArpu(p.starlink_arpu)],
    ["Compute", (p) => fmtGw(p.compute_gw)],
    ["Launches", (p) => fmtInt2(p.launches)],
    ["Mass (t)", (p) => fmtInt2(p.mass_to_orbit_t)],
  ]));
  root.appendChild(card);
}

function renderInsights(root, data) {
  const qs = data.quarters;
  const latest = qs[qs.length - 1];
  const prev = qs[qs.length - 2];
  const top = SEGMENTS.reduce((a, s) =>
    latest.segments[s].revenue > latest.segments[a].revenue ? s : a, "space");
  const card = el("div", "card");
  card.appendChild(el("h2", null, "What stands out"));
  const ul = el("ul", "insights");
  const items = [
    `${latest.period} revenue of ${fmtB(latest.revenue)} is up ` +
    `${fmtPct(latest.yoy.revenue_pct)} YoY, with ${SEG_LABEL[top]} now the ` +
    `largest segment (${fmtB(latest.segments[top].revenue)}, ` +
    `${latest.segments[top].share_pct}% of sales).`,
    `All three segments posted positive operating income: Space ` +
    `${fmtB(latest.segments.space.op_income)}, Connectivity ` +
    `${fmtB(latest.segments.connectivity.op_income)}, SI ` +
    `${fmtB(latest.segments.ai.op_income)}.`,
    `2025 was the first full year above $18B in revenue ` +
    `(${fmtB(data.annuals[2].revenue)}), +${data.annuals[2].yoy.revenue_pct}% YoY, ` +
    `with ${data.annuals[2].launches} launches.`,
  ];
  if (latest.net_income > 0 && prev.net_income < 0) {
    items.push(`First profitable quarter in the dataset: net income ` +
      `${fmtB(latest.net_income)} vs ${fmtB(prev.net_income)} in ${prev.period}.`);
  }
  if (latest.starlink_subs_m != null) {
    items.push(`Under the financials, the engines compounded: Starlink ` +
      `subscribers ${fmtSubs(latest.starlink_subs_m)}` +
      (latest.yoy && latest.yoy.subs_pct != null ?
        ` (${fmtPct(latest.yoy.subs_pct)} YoY)` : "") +
      `, nameplate compute ${fmtGw(latest.compute_gw)}` +
      (latest.yoy && latest.yoy.compute_pct != null ?
        ` (${fmtPct(latest.yoy.compute_pct)} YoY)` : "") +
      `, on ${fmtInt2(latest.launches)} launches. See the engines card below.`);
  }
  items.forEach((t) => ul.appendChild(el("li", null, t)));
  card.appendChild(ul);
  root.appendChild(card);
}

async function main() {
  const root = document.getElementById("app");
  root.innerHTML = "";
  let data;
  try {
    const resp = await fetch("../data/exports/spacex_bundle.json", { cache: "no-store" });
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    data = await resp.json();
  } catch (e) {
    root.appendChild(el("div", "card status",
      "Could not load /data/exports/spacex_bundle.json (" + e.message + "). " +
      "Serve this folder with: python3 -m http.server 8000"));
    return;
  }
  const latest = data.quarters[data.quarters.length - 1];
  document.getElementById("subtitle").textContent =
    `${data.company.name} (${data.company.ticker}, ${data.company.exchange}) · ` +
    `latest filed quarter ${latest.period} · revenue ${fmtB(latest.revenue)} ` +
    `(${fmtPct(latest.yoy.revenue_pct)} YoY)`;
  renderKpis(root, latest);
  renderInsights(root, data);
  renderEngines(root, data);
  renderTrend(root, data.quarters);
  renderProfit(root, data.quarters, data.annuals);
  renderTables(root, data.quarters, data.annuals);
}

document.addEventListener("DOMContentLoaded", main);
