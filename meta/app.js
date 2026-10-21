/* Meta Platforms (META) dashboard. Vanilla JS, no dependencies. */
"use strict";

const SEGMENTS = ["foa", "reality_labs"];
const SEG_LABEL = { foa: "Family of Apps", reality_labs: "Reality Labs" };
const SEG_COLOR = { foa: "#2a5d8a", reality_labs: "#b5892e" };

const fmtB = (v) => v == null ? "—" : (v < 0 ? "−$" : "$") +
  (Math.abs(v) / 1000).toFixed(2) + "B";
const fmtPct = (v) => v == null ? "—" : (v > 0 ? "+" : "") + v.toFixed(1) + "%";
const fmtEps = (v) => v == null ? "—" : (v < 0 ? "−$" : "$") + Math.abs(v).toFixed(2);
const fmtInt = (v) => v == null ? "—" : Math.round(v).toLocaleString("en-US");
const fmtDap = (v) => v == null ? "—" : v.toFixed(2) + "B";

/* Quarter color from each earnings release — the legal charge, the
   capex/FCF squeeze, Reality Labs guidance, and the Class C stock.
   Keyed by period; add the new quarter's notes when its release lands. */
const META_NOTES = {
  "Q3'26": [
    "The $9.89B legal charge: in August 2026 Meta agreed with 52 state " +
    "attorneys general to resolve the teen mental-health litigation, " +
    "with payments of up to ~$18.59B; $9.89B was expensed in Q3. " +
    "Excluding it, operating income was $22.88B (+11.4% YoY), diluted " +
    "EPS $7.40, and the effective tax rate 17% instead of 24%. The " +
    "charge sits in Family of Apps — FoA operating income of $17.12B " +
    "would have been ~$27.0B without it, a record.",
    "Capex ate the cash flow: capital expenditures hit $34.91B in the " +
    "quarter (+80% YoY) against $32.79B of operating cash flow, so " +
    "free cash flow went negative (−$2.12B) for the first time in this " +
    "series. FY2026 capex guidance was narrowed to $135–145B, and " +
    "management says it will keep investing aggressively in 2027.",
    "Reality Labs burn is bending: the RL loss narrowed to $4.13B. " +
    "Meta now expects FY2026 RL losses of $18–19B and ~$15B in 2027 " +
    "as investment is reallocated toward AI. Q4'26 revenue guidance " +
    "is $73–76B; FY2026 total expenses $175–179B including the charge.",
    "Smaller, AI-heavier company: headcount fell 15% YoY to 66,775 " +
    "even as DAP grew to 3.64B. The quarter also launched Muse and " +
    "Muse Wonder, Meta's first frontier models, per the release.",
    "New Class C stock: a non-voting Class C was approved, effective " +
    "January 19, 2027, with a one-for-one stock dividend to Class A " +
    "and B holders — economically a 2-for-1 split of the Class A " +
    "price, with no change to anyone's voting power.",
  ],
  "Q2'26": [
    "The capex step-up: capital expenditures jumped to $31.08B " +
    "(+83% YoY) and free cash flow was squeezed to just $0.78B as the " +
    "AI data-center build-out accelerated.",
    "Operating income fell 8% YoY despite revenue up 28% — total " +
    "costs and expenses grew 55% as infrastructure and hiring for the " +
    "superintelligence effort hit the P&L.",
  ],
  "Q1'26": [
    "Tax-distorted bottom line: net income of $26.77B and EPS of " +
    "$10.44 were flattered by an $8.03B income tax benefit (a −23% " +
    "effective tax rate) that partially offsets the $15.93B non-cash " +
    "charge booked in Q3'25 when the One Big Beautiful Bill Act was " +
    "enacted. The operating story is cleaner: revenue +33%, " +
    "operating income +30% at a 41% margin.",
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
  const y = latest.yoy || {};
  const card = el("div", "card");
  card.appendChild(el("h2", null, `Latest quarter: ${latest.period}`));
  card.appendChild(el("p", "sub", "YoY deltas vs the same quarter last year"));
  const grid = el("div", "kpis");
  grid.appendChild(kpiCard("Revenue", fmtB(latest.revenue),
    fmtPct(y.revenue) + " YoY", y.revenue >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Operating income", fmtB(latest.operating_income),
    fmtPct(y.op) + " YoY", y.op >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Net income", fmtB(latest.net_income),
    fmtPct(y.net) + " YoY", y.net >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Diluted EPS", fmtEps(latest.eps_diluted),
    fmtPct(y.eps) + " YoY", y.eps >= 0 ? "up" : "down"));
  grid.appendChild(kpiCard("Family DAP", fmtDap(latest.dap_b),
    fmtPct(latest.dap_pct) + " YoY", "up"));
  grid.appendChild(kpiCard("Operating margin",
    (latest.operating_margin_pct || 0).toFixed(1) + "%"));
  grid.appendChild(kpiCard("Capital expenditures", fmtB(latest.capex),
    fmtPct(y.capex) + " YoY", "down"));
  grid.appendChild(kpiCard("Free cash flow", fmtB(latest.fcf),
    latest.fcf < 0 ? "negative this quarter" : null,
    latest.fcf < 0 ? "down" : "up"));
  card.appendChild(grid);
  root.appendChild(card);
}

function renderInsights(root, data) {
  const qs = data.quarters;
  const latest = qs[qs.length - 1];
  const fy = data.annuals[data.annuals.length - 1];
  const adShare = (latest.products.advertising / latest.revenue * 100).toFixed(1);
  const card = el("div", "card");
  card.appendChild(el("h2", null, "What stands out"));
  const ul = el("ul", "insights");
  const items = [
    `${latest.period} revenue of ${fmtB(latest.revenue)} grew ` +
    `${fmtPct(latest.yoy.revenue)} YoY, and it is still almost all ` +
    `advertising: ${fmtB(latest.products.advertising)} (${adShare}% of ` +
    `the total), on ad impressions ${fmtPct(latest.impressions_pct)} and ` +
    `average price per ad ${fmtPct(latest.price_pct)}.`,
    `GAAP operating income fell ${fmtPct(latest.yoy.op)} YoY to ` +
    `${fmtB(latest.operating_income)} — but only because of the $9.89B ` +
    `legal charge. Excluding it, operating income was $22.88B and the ` +
    `margin 35%, and Family of Apps earned ~$27.0B against a Reality ` +
    `Labs loss of ${fmtB(latest.rl_op)}.`,
    `The AI build-out is now bigger than the cash machine's spare ` +
    `capacity: capex of ${fmtB(latest.capex)} (+${(latest.yoy.capex || 0).toFixed(0)}% YoY) ` +
    `exceeded operating cash flow, pushing free cash flow to ` +
    `${fmtB(latest.fcf)} — the first negative quarter in the series — ` +
    `while cash and securities still stand at $${latest.cash_sec_b.toFixed(2)}B.`,
    `Reality Labs losses narrowed ${fmtPct(latest.yoy.rl_loss)} YoY in ` +
    `absolute terms, and guidance bends the curve further: $18–19B of ` +
    `losses expected in FY2026, ~$15B in 2027, as spend shifts to AI.`,
    `FY${fy.period} (latest full year) revenue was ${fmtB(fy.revenue)} ` +
    `with FoA operating income of ${fmtB(fy.foa_op)} absorbing ` +
    `${fmtB(-fy.rl_op)} of Reality Labs losses; the quarterly run-rate ` +
    `has since stepped up to the mid-$60Bs.`,
  ];
  items.forEach((t) => ul.appendChild(el("li", null, t)));
  card.appendChild(ul);
  root.appendChild(card);
}

function renderBuildout(root, data) {
  const qs = data.quarters;
  const latest = qs[qs.length - 1];
  const card = el("div", "card");
  card.appendChild(el("h2", null,
    "The AI build-out: capex, Reality Labs and free cash flow"));
  card.appendChild(el("p", "sub",
    "Per the releases' reconciliations · capex includes finance-lease " +
    "principal payments"));
  const ul = el("ul", "insights");
  (META_NOTES[latest.period] || []).forEach((t) =>
    ul.appendChild(el("li", null, t)));
  card.appendChild(ul);
  card.appendChild(moneyTable(qs, [
    ["Capex", (p) => fmtB(p.capex)],
    ["Free cash flow", (p) => fmtB(p.fcf)],
    ["FoA op income", (p) => fmtB(p.foa_op)],
    ["RL op loss", (p) => fmtB(p.rl_op)],
    ["Headcount", (p) => fmtInt(p.headcount)],
  ]));
  root.appendChild(card);
}

function renderTrend(root, quarters) {
  const card = el("div", "card");
  card.appendChild(el("h2", null, "Quarterly revenue trend by segment"));
  card.appendChild(el("p", "sub", "$ millions · Family of Apps + Reality Labs"));
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
  drawStackedBars("ch-trend", quarters, (p) => p.segments);
}

function renderProfit(root, quarters) {
  const card = el("div", "card");
  card.appendChild(el("h2", null, "Profitability: operating vs net income"));
  card.appendChild(el("p", "sub", "$ millions · quarterly · net income swings with the Q3'25 tax charge, the Q1'26 tax benefit, and the Q3'26 legal charge"));
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
    { label: "Operating income", color: "#2a5d8a", get: (p) => p.operating_income },
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
    ["YoY", (p) => fmtPct(p.yoy && p.yoy.revenue)],
    ["FoA rev", (p) => fmtB(p.segments.foa)],
    ["RL rev", (p) => fmtB(p.segments.reality_labs)],
    ["Advertising", (p) => fmtB(p.products.advertising)],
    ["Op income", (p) => fmtB(p.operating_income)],
    ["Net income", (p) => fmtB(p.net_income)],
    ["Diluted EPS", (p) => fmtEps(p.eps_diluted)],
  ]));
  root.appendChild(q);

  const a = el("div", "card");
  a.appendChild(el("h2", null, "Annual results"));
  a.appendChild(el("p", "sub", "Revenue and income in $B · EPS in $ · twelve-month columns of the Q4 releases"));
  a.appendChild(moneyTable(annuals, [
    ["Revenue", (p) => fmtB(p.revenue)],
    ["YoY", (p) => fmtPct(p.yoy && p.yoy.revenue)],
    ["FoA rev", (p) => fmtB(p.segments.foa)],
    ["RL rev", (p) => fmtB(p.segments.reality_labs)],
    ["Advertising", (p) => fmtB(p.products.advertising)],
    ["Op income", (p) => fmtB(p.operating_income)],
    ["Net income", (p) => fmtB(p.net_income)],
    ["Diluted EPS", (p) => fmtEps(p.eps_diluted)],
    ["Capex", (p) => fmtB(p.capex)],
    ["FCF", (p) => fmtB(p.fcf)],
  ]));
  root.appendChild(a);

  const s = el("div", "card");
  s.appendChild(el("h2", null, "Segment operating income"));
  s.appendChild(el("p", "sub", "$B · Meta reports operating income by segment directly"));
  s.appendChild(moneyTable(quarters.concat(annuals.slice(-1)), [
    ["Family of Apps", (p) => fmtB(p.foa_op)],
    ["Reality Labs", (p) => fmtB(p.rl_op)],
    ["Total", (p) => fmtB(p.operating_income)],
    ["FoA margin", (p) => (p.foa_op / p.segments.foa * 100).toFixed(1) + "%"],
  ]));
  root.appendChild(s);

  const o = el("div", "card");
  o.appendChild(el("h2", null, "Operating metrics"));
  o.appendChild(el("p", "sub", "DAP = Family daily active people (billions, monthly average) · cash = cash, equivalents and marketable securities at period end"));
  o.appendChild(moneyTable(quarters, [
    ["DAP", (p) => fmtDap(p.dap_b)],
    ["Ad impressions YoY", (p) => fmtPct(p.impressions_pct)],
    ["Price per ad YoY", (p) => fmtPct(p.price_pct)],
    ["Capex", (p) => fmtB(p.capex)],
    ["Free cash flow", (p) => fmtB(p.fcf)],
    ["Headcount", (p) => fmtInt(p.headcount)],
    ["Cash & securities", (p) => "$" + p.cash_sec_b.toFixed(2) + "B"],
  ]));
  root.appendChild(o);
}

async function main() {
  const root = document.getElementById("app");
  root.innerHTML = "";
  let data;
  try {
    const resp = await fetch("../data/exports/meta_bundle.json", { cache: "no-store" });
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    data = await resp.json();
  } catch (e) {
    root.appendChild(el("div", "card status",
      "Could not load /data/exports/meta_bundle.json (" + e.message + "). " +
      "Serve this folder with: python3 -m http.server 8000"));
    return;
  }
  const latest = data.quarters[data.quarters.length - 1];
  document.getElementById("subtitle").textContent =
    `${data.company.name} (${data.company.ticker}, ${data.company.exchange}) · ` +
    `latest filed quarter ${latest.period} · revenue ${fmtB(latest.revenue)} ` +
    `(${fmtPct(latest.yoy.revenue)} YoY)`;
  renderKpis(root, latest);
  renderInsights(root, data);
  renderBuildout(root, data);
  renderTrend(root, data.quarters);
  renderProfit(root, data.quarters);
  renderTables(root, data.quarters, data.annuals);
}

document.addEventListener("DOMContentLoaded", main);
