/* Tesla (TSLA) dashboard. Vanilla JS, no dependencies. */
"use strict";

const SEGMENTS = ["automotive", "energy", "services"];
const SEG_LABEL = { automotive: "Automotive", energy: "Energy", services: "Services & Other" };
const SEG_COLOR = { automotive: "#2a5d8a", energy: "#5a8a6a", services: "#b5892e" };

const fmtB = (v) => v == null ? "—" : (v < 0 ? "−$" : "$") +
  (Math.abs(v) / 1000).toFixed(2) + "B";
const fmtPct = (v) => v == null ? "—" : (v > 0 ? "+" : "") + v.toFixed(1) + "%";
const fmtEps = (v) => v == null ? "—" : (v < 0 ? "−$" : "$") + Math.abs(v).toFixed(2);
const fmtInt = (v) => v == null ? "—" : Math.round(v).toLocaleString("en-US");
const fmtGwh = (v) => v == null ? "—" : v.toFixed(1) + " GWh";

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
  grid.appendChild(kpiCard("Deliveries", fmtInt(latest.deliveries),
    latest.yoy ? fmtPct(latest.yoy.deliveries_pct) + " YoY" : null,
    latest.yoy && latest.yoy.deliveries_pct >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Operating margin", fmtPct(latest.op_margin_pct)));
  grid.appendChild(kpiCard("Gross margin", fmtPct(latest.gross_margin_pct)));
  card.appendChild(grid);
  root.appendChild(card);
}

function renderTrend(root, quarters) {
  const card = el("div", "card");
  card.appendChild(el("h2", null, "Quarterly revenue trend by segment"));
  card.appendChild(el("p", "sub", "$ millions · Automotive + Energy + Services & Other"));
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
    automotive: p.segments.automotive.revenue,
    energy: p.segments.energy.revenue,
    services: p.segments.services.revenue,
  }));
}

function renderProfit(root, quarters, annuals) {
  const card = el("div", "card");
  card.appendChild(el("h2", null, "Profitability: operating vs net income"));
  card.appendChild(el("p", "sub", "$ millions · quarterly"));
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
    ["Auto rev", (p) => fmtB(p.segments.automotive.revenue)],
    ["Energy rev", (p) => fmtB(p.segments.energy.revenue)],
    ["Services rev", (p) => fmtB(p.segments.services.revenue)],
    ["Gross profit", (p) => fmtB(p.gross_profit)],
    ["Op income", (p) => fmtB(p.op_income)],
    ["Net income", (p) => fmtB(p.net_income)],
    ["Diluted EPS", (p) => fmtEps(p.eps_diluted)],
    ["Deliveries", (p) => fmtInt(p.deliveries)],
  ]));
  root.appendChild(q);

  const a = el("div", "card");
  a.appendChild(el("h2", null, "Annual results"));
  a.appendChild(el("p", "sub", "Revenue and income in $B · EPS in $ · audited 10-K statements"));
  a.appendChild(moneyTable(annuals, [
    ["Revenue", (p) => fmtB(p.revenue)],
    ["YoY", (p) => p.yoy ? fmtPct(p.yoy.revenue_pct) : "—"],
    ["Auto rev", (p) => fmtB(p.segments.automotive.revenue)],
    ["Energy rev", (p) => fmtB(p.segments.energy.revenue)],
    ["Services rev", (p) => fmtB(p.segments.services.revenue)],
    ["Gross profit", (p) => fmtB(p.gross_profit)],
    ["Op income", (p) => fmtB(p.op_income)],
    ["Net income", (p) => fmtB(p.net_income)],
    ["Diluted EPS", (p) => fmtEps(p.eps_diluted)],
    ["Deliveries", (p) => fmtInt(p.deliveries)],
    ["Storage deployed", (p) => fmtGwh(p.storage_gwh)],
  ]));
  root.appendChild(a);

  const s = el("div", "card");
  s.appendChild(el("h2", null, "Segment gross profit"));
  s.appendChild(el("p", "sub", "$B · Tesla does not allocate operating expenses by segment; FY2023 split not disclosed"));
  s.appendChild(moneyTable(quarters.concat(annuals.slice(-1)), [
    ["Automotive", (p) => fmtB(p.segments.automotive.gross_profit)],
    ["Energy", (p) => fmtB(p.segments.energy.gross_profit)],
    ["Services & Other", (p) => fmtB(p.segments.services.gross_profit)],
    ["Total", (p) => fmtB(p.gross_profit)],
  ]));
  root.appendChild(s);

  const o = el("div", "card");
  o.appendChild(el("h2", null, "Operating metrics"));
  o.appendChild(el("p", "sub", "Vehicles in units · storage in GWh · Supercharger network at quarter end"));
  o.appendChild(moneyTable(quarters, [
    ["Production", (p) => fmtInt(p.production)],
    ["Deliveries", (p) => fmtInt(p.deliveries)],
    ["Storage deployed", (p) => fmtGwh(p.storage_gwh)],
    ["Supercharger stations", (p) => fmtInt(p.stations)],
    ["Connectors", (p) => fmtInt(p.connectors)],
  ]));
  root.appendChild(o);
}

function renderInsights(root, data) {
  const qs = data.quarters;
  const latest = qs[qs.length - 1];
  const top = SEGMENTS.reduce((a, s) =>
    latest.segments[s].revenue > latest.segments[a].revenue ? s : a, "automotive");
  const fy = data.annuals[data.annuals.length - 1];
  const svcRecord = latest.segments.services.revenue >=
    Math.max(...qs.map((q) => q.segments.services.revenue));
  const card = el("div", "card");
  card.appendChild(el("h2", null, "What stands out"));
  const ul = el("ul", "insights");
  const items = [
    `${latest.period} revenue of ${fmtB(latest.revenue)} is up ` +
    `${fmtPct(latest.yoy.revenue_pct)} YoY, with ${SEG_LABEL[top]} still the ` +
    `largest line (${fmtB(latest.segments[top].revenue)}, ` +
    `${latest.segments[top].share_pct}% of sales) — but operating income ` +
    `fell to ${fmtB(latest.op_income)} (${fmtPct(latest.op_margin_pct)} margin) ` +
    `as operating expenses climbed.`,
    `Deliveries hit ${fmtInt(latest.deliveries)} in ${latest.period} ` +
    `(${fmtPct(latest.yoy.deliveries_pct)} YoY) on production of ` +
    `${fmtInt(latest.production)}; energy storage deployments of ` +
    `${fmtGwh(latest.storage_gwh)} were up ${fmtPct(latest.yoy.storage_pct)} YoY.`,
    `FY${fy.period.slice(2)} revenue of ${fmtB(fy.revenue)} was Tesla's first ` +
    `annual decline (${fmtPct(fy.yoy.revenue_pct)}), even as Energy revenue ` +
    `grew to ${fmtB(fy.segments.energy.revenue)} and Services & Other to ` +
    `${fmtB(fy.segments.services.revenue)}; FY deliveries were ` +
    `${fmtInt(fy.deliveries)}.`,
  ];
  if (svcRecord) {
    items.push(`Services & Other set a record in ${latest.period} at ` +
      `${fmtB(latest.segments.services.revenue)} of revenue and ` +
      `${fmtB(latest.segments.services.gross_profit)} of gross profit.`);
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
    const resp = await fetch("../data/exports/tesla_bundle.json", { cache: "no-store" });
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    data = await resp.json();
  } catch (e) {
    root.appendChild(el("div", "card status",
      "Could not load /data/exports/tesla_bundle.json (" + e.message + "). " +
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
  renderTrend(root, data.quarters);
  renderProfit(root, data.quarters, data.annuals);
  renderTables(root, data.quarters, data.annuals);
}

document.addEventListener("DOMContentLoaded", main);
