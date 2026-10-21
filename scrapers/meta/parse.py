"""Parse Meta 8-K earnings releases (Exhibit 99.1) from the raw cache.

The releases are structured HTML. Flattening the markup keeps each
table row's label followed by its values, so the financial highlights,
the segment information table, and the free-cash-flow reconciliation
can be recovered with anchored patterns. parse.py extracts the
release's own quarter; normalize.py pins the curated values and the
tests assert the two layers agree.
"""

import html
import os
import re

RAW = os.path.join("data", "meta", "raw")


def _flatten(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text))


def _num(text):
    return int(text.replace(",", ""))


def _signed(segment):
    """First value in a table cell run; parentheses mean negative."""
    m = re.search(r"\(?\$?\s*([\d,]+)\)?", segment)
    if not m:
        return None
    value = _num(m.group(1))
    return -value if m.group(0).strip().startswith("(") else value


def _labeled(block, label):
    idx = block.find(label)
    if idx == -1:
        return None
    return _signed(block[idx + len(label):idx + len(label) + 24])


def release_facts(path):
    """Facts for the release's own quarter from its exhibit file."""
    t = _flatten(path)
    facts = {}

    m = re.search(r"Revenue \$ ([\d,]+)", t)
    facts["revenue"] = _num(m.group(1)) if m else None
    m = re.search(r"Income from operations \$ \(?([\d,]+)\)?", t)
    facts["operating_income"] = _num(m.group(1)) if m else None
    m = re.search(r"Net income \$ ([\d,]+)", t)
    facts["net_income"] = _num(m.group(1)) if m else None
    m = re.search(r"Diluted earnings per share \(EPS\)(?: \(\d\))? \$ ([\d.]+)", t)
    facts["eps_diluted"] = float(m.group(1)) if m else None
    m = re.search(r"Basic \$ ([\d.]+)", t)
    facts["eps_basic"] = float(m.group(1)) if m else None

    seg_start = t.find("Segment Information")
    seg_end = t.find("Reconciliation of GAAP", seg_start)
    seg = t[seg_start:seg_end] if seg_start != -1 else ""
    op_marker = seg.find("Income (loss) from operations:")
    rev_block, op_block = seg[:op_marker], seg[op_marker:]
    facts["advertising"] = _labeled(rev_block, "Advertising")
    facts["other"] = _labeled(rev_block, "Other revenue")
    facts["foa"] = _labeled(rev_block, "Family of Apps")
    facts["reality_labs"] = _labeled(rev_block, "Reality Labs")
    facts["foa_op"] = _labeled(op_block, "Family of Apps")
    facts["rl_op"] = _labeled(op_block, "Reality Labs")

    m = re.search(r"DAP was ([\d.]+) billion", t)
    facts["dap_b"] = float(m.group(1)) if m else None
    ppe = re.search(r"Purchases of property and equipment \(([\d,]+)\)", t)
    lease = re.search(r"Principal payments on finance leases \(([\d,]+)\)", t)
    facts["capex"] = (_num(ppe.group(1)) + _num(lease.group(1))
                      ) if ppe and lease else None
    m = re.search(r"Free cash flow \$ (\()?([\d,]+)\)?", t)
    facts["fcf"] = (-_num(m.group(2)) if m and m.group(1)
                    else _num(m.group(2)) if m else None)
    m = re.search(r"Headcount was ([\d,]+)", t)
    facts["headcount"] = _num(m.group(1)) if m else None
    return facts


def release_periods(cache_name):
    facts = release_facts(os.path.join(RAW, cache_name))
    facts = {k: v for k, v in facts.items() if v is not None}
    return facts
