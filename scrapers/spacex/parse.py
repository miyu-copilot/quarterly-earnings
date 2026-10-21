"""Parsers for SpaceX EDGAR documents.

Two document shapes:
- 10-Q (spcx-20260630.htm): inline XBRL. Facts are read from ix:nonFraction
  tags joined to xbrli:context periods/dimensions. Exact, no guessing.
- S-1 (spaceexplorationtechnologi.htm): no XBRL tagging on the financials,
  so audited tables are read in DOM order with a stdlib HTML table parser.

Both parsers preserve source values/units; normalization lives in
normalize.py.
"""

import re
from collections import defaultdict
from html.parser import HTMLParser

REVENUE_TAG = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
SEG_AXIS = "us-gaap:StatementBusinessSegmentsAxis"
PRODUCT_AXIS = "srt:ProductOrServiceAxis"

SEGMENT_MEMBERS = {
    "spcx:SpaceMember": "space",
    "spcx:ConnectivityMember": "connectivity",
    "spcx:AIMember": "ai",
}

PRODUCT_MEMBERS = {
    "us-gaap:LaunchServicesMember": "launch_services",
    "spcx:LaunchAndDevelopmentMember": "launch_development",
    "spcx:ConsumerMember": "consumer",
    "spcx:EnterpriseAndGovernmentMember": "enterprise_government",
    "us-gaap:AdvertisingMember": "advertising",
    "spcx:AISolutionsAndInfrastructureMember": "ai_solutions_infrastructure",
}


def parse_ixds(path):
    """Return (contexts, facts) from an inline-XBRL filing."""
    doc = open(path, encoding="utf-8", errors="replace").read()
    contexts = {}
    for m in re.finditer(r'<xbrli:context id="([^"]+)">(.*?)</xbrli:context>', doc, re.S):
        cid, body = m.group(1), m.group(2)
        per = {}
        for t in ("startDate", "endDate", "instant"):
            sm = re.search(r"<xbrli:%s>([^<]+)</xbrli:%s>" % (t, t), body)
            if sm:
                per[t] = sm.group(1)
        dims = dict(
            re.findall(
                r'<xbrldi:explicitMember dimension="([^"]+)">([^<]+)</xbrldi:explicitMember>',
                body,
            )
        )
        contexts[cid] = {"period": per, "dims": dims}
    facts = []
    for m in re.finditer(r"<ix:nonFraction\b([^>]*)>(.*?)</ix:nonFraction>", doc, re.S):
        attrs, body = m.group(1), m.group(2)
        nm = re.search(r'name="([^"]+)"', attrs)
        cm = re.search(r'contextRef="([^"]+)"', attrs)
        if not nm or not cm:
            continue
        val = re.sub(r"<[^>]+>", "", body).strip().replace(",", "")
        try:
            v = float(val)
        except ValueError:
            continue
        facts.append({"tag": nm.group(1), "ctx": cm.group(1), "val": v})
    return contexts, facts


def revenue_by_period_segment(path):
    """{(start, end): {'total': v, 'space': v, ...}} from inline XBRL."""
    contexts, facts = parse_ixds(path)
    out = defaultdict(dict)
    for f in facts:
        if f["tag"] != REVENUE_TAG:
            continue
        c = contexts.get(f["ctx"], {})
        per = c.get("period", {})
        dims = c.get("dims", {})
        if PRODUCT_AXIS in dims:
            continue  # product split handled separately
        key = (per.get("startDate"), per.get("endDate"))
        seg = SEGMENT_MEMBERS.get(dims.get(SEG_AXIS), "total")
        out[key][seg] = f["val"]
    return dict(out)


def revenue_by_product(path):
    """{(start, end): {product_key: v}} from inline XBRL."""
    contexts, facts = parse_ixds(path)
    out = defaultdict(dict)
    for f in facts:
        if f["tag"] != REVENUE_TAG:
            continue
        c = contexts.get(f["ctx"], {})
        per = c.get("period", {})
        dims = c.get("dims", {})
        if PRODUCT_AXIS not in dims:
            continue
        prod = PRODUCT_MEMBERS.get(dims[PRODUCT_AXIS])
        if not prod:
            continue
        out[(per.get("startDate"), per.get("endDate"))][prod] = f["val"]
    return dict(out)


class _Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.cur = self.row = self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.cur = []
        elif tag == "tr" and self.cur is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.cur.append(self.row)
            self.row = None
        elif tag == "table" and self.cur is not None:
            self.tables.append(self.cur)
            self.cur = None

    def handle_data(self, d):
        if self.cell is not None:
            self.cell.append(d)


def html_tables(path):
    """All tables in a filing in DOM cell order."""
    doc = open(path, encoding="utf-8", errors="replace").read()
    p = _Tables()
    p.feed(doc)
    return p.tables


def find_tables(path, phrase):
    """Tables whose text contains phrase (case-insensitive)."""
    out = []
    for t in html_tables(path):
        blob = " | ".join(" ".join(r) for r in t)
        if phrase.lower() in blob.lower():
            out.append(t)
    return out
