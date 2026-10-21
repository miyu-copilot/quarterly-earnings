"""Curated Meta quarterly figures, normalized to a bundle.

Every figure is transcribed from Meta's 8-K earnings releases
(Exhibit 99.1) cached in data/meta/raw/ (see quarters.py for the
registry). Money is $M except per-share data and cash reserves ($B).
`dap_b` is Family daily active people (billions, average for the
quarter's final month); `cash_sec_b` is cash, cash equivalents and
marketable securities at period end. `capex` follows the release
definition: purchases of property and equipment plus principal
payments on finance leases. `fcf` is the release's non-GAAP free cash
flow. Annual rows are the twelve-month columns of the Q4 releases;
their DAP/headcount/cash are the December period-end values.
`impressions_pct` / `price_pct` are the year-over-year changes in ad
impressions and average price per ad disclosed in the highlights.

Q3'25 net income/EPS carry the one-time, non-cash $15.93B tax charge
from the One Big Beautiful Bill Act; Q1'26 carries the offsetting
$8.03B tax benefit. Q3'26 costs include the $9.89B charge for the
agreement with 52 U.S. state attorneys general (teen mental health
litigation; payments of up to ~$18.59B). Excluding it, Q3'26 operating
income was $22,877M and diluted EPS was $7.40.
"""

from .quarters import COMPANY

# period -> revenue, operating_income, net_income, eps_basic, eps_diluted,
#           segments{foa, reality_labs}, products{advertising, other},
#           foa_op, rl_op, dap_b, capex, fcf, headcount, cash_sec_b,
#           impressions_pct, price_pct
FACTS = {
    "Q1'25": (42314, 17555, 16644, 6.59, 6.43,
              {"foa": 41902, "reality_labs": 412},
              {"advertising": 41392, "other": 510},
              21765, -4210, 3.43, 13692, 10334, 76834, 70.23, 5, 10),
    "Q2'25": (47516, 20441, 18337, 7.28, 7.14,
              {"foa": 47146, "reality_labs": 370},
              {"advertising": 46563, "other": 583},
              24971, -4530, 3.48, 17012, 8549, 75945, 47.07, 11, 9),
    "Q3'25": (51242, 20535, 2709, 1.08, 1.05,
              {"foa": 50772, "reality_labs": 470},
              {"advertising": 50082, "other": 690},
              24967, -4432, 3.54, 19374, 10625, 78450, 44.45, 14, 10),
    "Q4'25": (59893, 24745, 22768, 9.02, 8.88,
              {"foa": 58938, "reality_labs": 955},
              {"advertising": 58137, "other": 801},
              30766, -6021, 3.58, 22137, 14077, 78865, 81.59, 18, 6),
    "Q1'26": (56311, 22872, 26773, 10.57, 10.44,
              {"foa": 55909, "reality_labs": 402},
              {"advertising": 55024, "other": 885},
              26900, -4028, 3.56, 19840, 12386, 77986, 81.18, 19, 12),
    "Q2'26": (60801, 18775, 15848, 6.23, 6.18,
              {"foa": 60370, "reality_labs": 431},
              {"advertising": 59363, "other": 1007},
              23394, -4619, 3.60, 31078, 784, 75472, 90.26, 14, 12),
    "Q3'26": (64601, 12988, 9860, 3.86, 3.83,
              {"foa": 64158, "reality_labs": 443},
              {"advertising": 63061, "other": 1097},
              17117, -4129, 3.64, 34906, -2120, 66775, 82.45, 10, 14),
}

ANNUAL_FACTS = {
    2023: (134902, 46751, 39098, 15.19, 14.87,
           {"foa": 133006, "reality_labs": 1896},
           {"advertising": 131948, "other": 1058},
           62871, -16120, 3.19, 28324, 43010, 67317, 65.40, None, None),
    2024: (164501, 69380, 62360, 24.61, 23.86,
           {"foa": 162355, "reality_labs": 2146},
           {"advertising": 160633, "other": 1722},
           87109, -17729, 3.35, 39225, 52103, 74067, 77.81, 11, 10),
    2025: (200966, 83276, 60458, 23.98, 23.49,
           {"foa": 198759, "reality_labs": 2207},
           {"advertising": 196175, "other": 2584},
           102469, -19193, 3.58, 72215, 43585, 78865, 81.59, 12, 9),
}

FIELDS = ("revenue", "operating_income", "net_income", "eps_basic",
          "eps_diluted", "segments", "products", "foa_op", "rl_op",
          "dap_b", "capex", "fcf", "headcount", "cash_sec_b",
          "impressions_pct", "price_pct")

QUARTER_ORDER = ["Q1'25", "Q2'25", "Q3'25", "Q4'25",
                 "Q1'26", "Q2'26", "Q3'26"]

# Periods with a matching prior-year quarter inside FACTS.
YOY = {"Q1'26": "Q1'25", "Q2'26": "Q2'25", "Q3'26": "Q3'25"}


def _pct(cur, base):
    if cur is None or base in (None, 0):
        return None
    return round((cur / base - 1) * 100, 1)


def _row(period, values):
    row = {"period": period}
    row.update(dict(zip(FIELDS, values)))
    row["operating_margin_pct"] = round(
        row["operating_income"] / row["revenue"] * 100, 1)
    row["dap_pct"] = None
    return row


def normalize():
    yoy_keys = {"revenue": "revenue", "op": "operating_income",
                "net": "net_income", "eps": "eps_diluted", "capex": "capex"}
    quarters = [_row(p, FACTS[p]) for p in QUARTER_ORDER]
    by_period = {q["period"]: q for q in quarters}
    for q in quarters:
        yoy = {}
        base_period = YOY.get(q["period"])
        if base_period:
            base = by_period[base_period]
            for out_key, key in yoy_keys.items():
                yoy[out_key] = _pct(q[key], base[key])
            q["dap_pct"] = _pct(q["dap_b"], base["dap_b"])
            yoy["rl_loss"] = _pct(abs(q["rl_op"]), abs(base["rl_op"]))
        q["yoy"] = yoy

    annuals = [_row(str(year), ANNUAL_FACTS[year])
               for year in sorted(ANNUAL_FACTS)]
    prev = None
    for a in annuals:
        yoy = {}
        if prev is not None:
            for out_key, key in yoy_keys.items():
                yoy[out_key] = _pct(a[key], prev[key])
            a["dap_pct"] = _pct(a["dap_b"], prev["dap_b"])
        a["yoy"] = yoy
        prev = a

    return {
        "company": COMPANY,
        "latest": quarters[-1]["period"],
        "quarters": quarters,
        "annuals": annuals,
    }
