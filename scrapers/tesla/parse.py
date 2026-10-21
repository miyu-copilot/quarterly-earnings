"""Parser for Tesla's quarterly update letters (8-K Exhibit 99.1).

The letters are presentation HTML without machine-readable tables: once
tags are stripped, each financial table is a header row of period labels
(e.g. "Q2-2025 Q3-2025 Q4-2025 Q1-2026 Q2-2026") followed by
"label value value ..." rows. This parser recovers per-period revenue,
cost, income, EPS and operating metrics from that text layout.

Values are $ millions (except per-share $, vehicle counts, GWh and
station/connector counts). Em-dash cells read as 0; parenthesized values
are negative. Normalization/curation lives in normalize.py; this module
is the verification layer that ties curated facts back to the letters.
"""

import html
import re

VAL = r"(?:\$ )?\(?-?[\d,]+(?:\.\d+)?\)?|—"
HDR = re.compile(
    r"((?:Q[1-4]-20\d\d)(?: Q[1-4]-20\d\d){4}|(?:20\d\d)(?: 20\d\d){2,4})")

REV_LABELS = ["Automotive sales", "Automotive regulatory credits",
              "Automotive leasing", "Total automotive revenues",
              "Energy generation and storage", "Services and other",
              "Total revenues"]
COST_LABELS = ["Automotive sales", "Automotive leasing",
               "Total automotive cost of revenues",
               "Energy generation and storage", "Services and other",
               "Total cost of revenues", "Gross profit"]
OPS_LABELS = ["Model 3/Y production", "Other models production",
              "Total production", "Model 3/Y deliveries",
              "Other models deliveries", "Total deliveries",
              "Storage deployed (GWh)", "Supercharger stations",
              "Supercharger connectors"]


def flat_text(path):
    doc = open(path, encoding="utf-8", errors="replace").read()
    doc = re.sub(r"<[^>]+>", " ", doc)
    doc = html.unescape(doc)
    return re.sub(r"\s+", " ", doc)


def _num(tok):
    tok = tok.strip().replace("$", "").strip()
    if tok == "—":
        return 0
    neg = tok.startswith("(") and tok.endswith(")")
    v = float(tok.strip("()").replace(",", ""))
    return -v if neg else v


def row_values(block, label, ncols):
    """Find 'label v1 ... vn' in block (footnote markers tolerated)."""
    pat = re.compile(
        re.escape(label) + r"(?:\s+\(\d+\))?\s+((?:"
        + VAL + r")(?:\s+(?:" + VAL + r")){" + str(ncols - 1) + r"})")
    m = pat.search(block)
    if not m:
        return None
    toks = re.findall(VAL, m.group(1))
    if len(toks) != ncols:
        return None
    return [_num(t) for t in toks]


def _period_label(col):
    if col.startswith("Q"):
        return col.replace("-20", "'")
    return col


def letter_periods(path):
    """{period: {'rev': {...}, 'cost': {...}, 'ops': {...}, ...}}."""
    text = flat_text(path)
    periods = {}
    matches = list(HDR.finditer(text))
    for i, m in enumerate(matches):
        cols = [_period_label(c) for c in m.group(1).split()]
        n = len(cols)
        block = text[m.end(): matches[i + 1].start()
                     if i + 1 < len(matches) else len(text)]
        for j, per in enumerate(cols):
            rec = periods.setdefault(per, {})
            for lab in OPS_LABELS:
                vals = row_values(block, lab, n)
                if vals is not None:
                    rec.setdefault("ops", {})[lab] = vals[j]
        if "Total revenues" not in block:
            continue
        rev_block = block.split("COST OF REVENUES")[0]
        cost_block = block[len(rev_block):]
        for j, per in enumerate(cols):
            rec = periods.setdefault(per, {})
            for lab in REV_LABELS:
                vals = row_values(rev_block, lab, n)
                if vals is None and lab in (
                        "Energy generation and storage", "Services and other"):
                    vals = row_values(rev_block, lab + " revenue", n)
                if vals is not None:
                    rec.setdefault("rev", {})[lab] = vals[j]
            for lab in COST_LABELS:
                vals = row_values(cost_block, lab, n)
                if vals is not None:
                    rec.setdefault("cost", {})[lab] = vals[j]
            for lab, key in [("Total gross profit", "gross_profit_total"),
                             ("Income from operations", "op_income")]:
                vals = row_values(rev_block, lab, n)
                if vals is not None and key not in rec:
                    rec[key] = vals[j]
            if "INCOME FROM OPERATIONS" in block:
                for lab, key in [
                        ("INCOME FROM OPERATIONS", "op_income"),
                        ("NET INCOME ATTRIBUTABLE TO COMMON STOCKHOLDERS",
                         "net_income")]:
                    vals = row_values(block, lab, n)
                    if vals is not None:
                        rec[key] = vals[j]
                seg = block.split(
                    "attributable to common stockholders")[-1]
                for lab, key in [("Basic", "eps_basic"),
                                 ("Diluted", "eps_diluted")]:
                    vals = row_values(seg, lab, n)
                    if vals is not None and key not in rec:
                        rec[key] = vals[j]
    return periods
