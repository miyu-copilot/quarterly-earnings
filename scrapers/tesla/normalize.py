"""Normalize Tesla filings to dashboard-friendly metrics.

Source values and units are preserved below ($ millions, except per-share
$ and vehicle/station counts). Unavailable fields use None -- never
fabricated estimates.

Revenue lines (filing row name -> key):
- "Automotive sales" / "Automotive regulatory credits" /
  "Automotive leasing" -> products (components of Automotive revenue)
- "Total automotive revenues" -> segments.automotive
- "Energy generation and storage" -> segments.energy
- "Services and other" -> segments.services

Segment gross profit is revenue less the matching cost-of-revenues line
from the same statement of operations (Tesla does not allocate operating
expenses by segment, so gross profit -- not operating income -- is the
segment profitability measure). Cross-checks performed at build time:
each quarter's segment gross profits sum to total gross profit; FY2025
energy gross profit (3,802) and FY2024 (2,640) equal the 10-K segment
note; FY2025/FY2024 segment gross profit is the sum of the four quarterly
letters. FY2023 segment gross profit is None: the 10-K reports only two
reportable segments (Automotive incl. Services, Energy) for that split.

Provenance: quarterly figures come from each quarter's own 8-K update
letter (Ex. 99.1) and tie to EDGAR XBRL company facts (frame values for
revenue / operating income / net income / EPS). Q4'24 net income uses
the Q4'24 letter's 2,317: the four 2024 quarters then sum to the FY2024
attributable total of 7,091 (the Q4'25 letter's comparative column shows
2,128 under a footnoted re-presentation). Annual revenue splits are from
the FY2025 10-K revenue note (R44) and segment note (R93).
"""

L_Q1_25 = {"form": "8-K", "accession": "0001628280-25-018851",
           "filed": "2025-04-22"}
L_Q2_25 = {"form": "8-K", "accession": "0001628280-25-035738",
           "filed": "2025-07-23"}
L_Q3_25 = {"form": "8-K", "accession": "0001628280-25-045861",
           "filed": "2025-10-22"}
L_Q4_25 = {"form": "8-K", "accession": "0001628280-26-003837",
           "filed": "2026-01-28"}
L_Q1_26 = {"form": "8-K", "accession": "0001628280-26-026551",
           "filed": "2026-04-22"}
L_Q2_26 = {"form": "8-K", "accession": "0001628280-26-049213",
           "filed": "2026-07-22"}
K_FY25 = {"form": "10-K", "accession": "0001628280-26-003952",
          "filed": "2026-01-29",
          "note": "Audited FY2023-FY2025 statements; revenue note (R44) "
                  "and segment note (R93)."}

SEGMENTS = ("automotive", "energy", "services")
PRODUCTS = ("automotive_sales", "regulatory_credits", "automotive_leasing")

# Curated source facts. Keys: revenue, op_income, net_income, eps_basic,
# eps_diluted, gross_profit, seg_rev{...}, seg_gp{...}, products{...},
# deliveries, production, storage_gwh, stations, connectors.
FACTS = {
    "2023": {
        "revenue": 96773, "op_income": 8891, "net_income": 14997,
        "eps_basic": 4.73, "eps_diluted": 4.30, "gross_profit": 17660,
        "seg_rev": {"automotive": 82419, "energy": 6035, "services": 8319},
        "seg_gp": {"automotive": None, "energy": None, "services": None},
        "products": {"automotive_sales": 78509, "regulatory_credits": 1790,
                     "automotive_leasing": 2120},
        "deliveries": 1808581, "production": 1845985, "storage_gwh": 14.7,
        "stations": 5952, "connectors": 54892, "src": K_FY25,
    },
    "2024": {
        "revenue": 97690, "op_income": 7076, "net_income": 7091,
        "eps_basic": 2.23, "eps_diluted": 2.04, "gross_profit": 17450,
        "seg_rev": {"automotive": 77070, "energy": 10086, "services": 10534},
        "seg_gp": {"automotive": 14197, "energy": 2640, "services": 613},
        "products": {"automotive_sales": 72480, "regulatory_credits": 2763,
                     "automotive_leasing": 1827},
        "deliveries": 1789226, "production": 1773443, "storage_gwh": 31.4,
        "stations": 6975, "connectors": 65495, "src": K_FY25,
    },
    "2025": {
        "revenue": 94827, "op_income": 4355, "net_income": 3794,
        "eps_basic": 1.18, "eps_diluted": 1.08, "gross_profit": 17094,
        "seg_rev": {"automotive": 69526, "energy": 12771, "services": 12530},
        "seg_gp": {"automotive": 12361, "energy": 3802, "services": 931},
        "products": {"automotive_sales": 65821, "regulatory_credits": 1993,
                     "automotive_leasing": 1712},
        "deliveries": 1636129, "production": 1654667, "storage_gwh": 46.7,
        "stations": 8182, "connectors": 77682, "src": K_FY25,
    },
    "Q1'25": {
        "revenue": 19335, "op_income": 399, "net_income": 409,
        "eps_basic": 0.13, "eps_diluted": 0.12, "gross_profit": 3153,
        "seg_rev": {"automotive": 13967, "energy": 2730, "services": 2638},
        "seg_gp": {"automotive": 2267, "energy": 785, "services": 101},
        "products": {"automotive_sales": 12925, "regulatory_credits": 595,
                     "automotive_leasing": 447},
        "deliveries": 336681, "production": 362615, "storage_gwh": 10.4,
        "stations": 7131, "connectors": 67316, "src": L_Q1_25,
    },
    "Q2'25": {
        "revenue": 22496, "op_income": 923, "net_income": 1172,
        "eps_basic": 0.36, "eps_diluted": 0.33, "gross_profit": 3878,
        "seg_rev": {"automotive": 16661, "energy": 2789, "services": 3046},
        "seg_gp": {"automotive": 2866, "energy": 846, "services": 166},
        "products": {"automotive_sales": 15787, "regulatory_credits": 439,
                     "automotive_leasing": 435},
        "deliveries": 384122, "production": 410244, "storage_gwh": 9.6,
        "stations": 7377, "connectors": 70228, "src": L_Q2_25,
    },
    "Q3'25": {
        "revenue": 28095, "op_income": 1624, "net_income": 1373,
        "eps_basic": 0.43, "eps_diluted": 0.39, "gross_profit": 5054,
        "seg_rev": {"automotive": 21205, "energy": 3415, "services": 3475},
        "seg_gp": {"automotive": 3615, "energy": 1073, "services": 366},
        "products": {"automotive_sales": 20359, "regulatory_credits": 417,
                     "automotive_leasing": 429},
        "deliveries": 497099, "production": 447450, "storage_gwh": 12.5,
        "stations": 7753, "connectors": 73817, "src": L_Q3_25,
    },
    "Q4'25": {
        "revenue": 24901, "op_income": 1409, "net_income": 840,
        "eps_basic": 0.26, "eps_diluted": 0.24, "gross_profit": 5009,
        "seg_rev": {"automotive": 17693, "energy": 3837, "services": 3371},
        "seg_gp": {"automotive": 3613, "energy": 1098, "services": 298},
        "products": {"automotive_sales": 16750, "regulatory_credits": 542,
                     "automotive_leasing": 401},
        "deliveries": 418227, "production": 434358, "storage_gwh": 14.2,
        "stations": 8182, "connectors": 77682, "src": L_Q4_25,
    },
    "Q1'26": {
        "revenue": 22387, "op_income": 941, "net_income": 477,
        "eps_basic": 0.15, "eps_diluted": 0.13, "gross_profit": 4720,
        "seg_rev": {"automotive": 16234, "energy": 2408, "services": 3745},
        "seg_gp": {"automotive": 3422, "energy": 952, "services": 346},
        "products": {"automotive_sales": 15473, "regulatory_credits": 380,
                     "automotive_leasing": 381},
        "deliveries": 358023, "production": 408386, "storage_gwh": 8.8,
        "stations": 8463, "connectors": 79918, "src": L_Q1_26,
    },
    "Q2'26": {
        "revenue": 28236, "op_income": 398, "net_income": 1114,
        "eps_basic": 0.34, "eps_diluted": 0.32, "gross_profit": 4751,
        "seg_rev": {"automotive": 20516, "energy": 3139, "services": 4581},
        "seg_gp": {"automotive": 3463, "energy": 640, "services": 648},
        "products": {"automotive_sales": 20006, "regulatory_credits": 146,
                     "automotive_leasing": 364},
        "deliveries": 480126, "production": 451758, "storage_gwh": 13.5,
        "stations": 8704, "connectors": 82357, "src": L_Q2_26,
    },
}

QUARTER_ORDER = ["Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]
ANNUAL_ORDER = ["2023", "2024", "2025"]


def _check_ties(label, f):
    assert sum(f["seg_rev"].values()) == f["revenue"], f"segment tie {label}"
    assert sum(f["products"].values()) == f["seg_rev"]["automotive"], \
        f"product tie {label}"
    if all(v is not None for v in f["seg_gp"].values()):
        assert sum(f["seg_gp"].values()) == f["gross_profit"], \
            f"seg-gp tie {label}"


def _pct(new, old):
    if old is None or new is None or old == 0:
        return None
    return round((new - old) / abs(old) * 100, 1)


def build_period(label, yoy=None):
    f = FACTS[label]
    _check_ties(label, f)
    rev = f["revenue"]
    row = {
        "period": label,
        "revenue": rev,
        "op_income": f["op_income"],
        "net_income": f["net_income"],
        "eps_basic": f["eps_basic"],
        "eps_diluted": f["eps_diluted"],
        "gross_profit": f["gross_profit"],
        "gross_margin_pct": round(f["gross_profit"] / rev * 100, 1),
        "op_margin_pct": round(f["op_income"] / rev * 100, 1),
        "net_margin_pct": round(f["net_income"] / rev * 100, 1),
        "segments": {
            s: {"revenue": f["seg_rev"][s],
                "share_pct": round(f["seg_rev"][s] / rev * 100, 1),
                "gross_profit": f["seg_gp"][s]}
            for s in SEGMENTS
        },
        "products": dict(f["products"]),
        "deliveries": f["deliveries"],
        "production": f["production"],
        "storage_gwh": f["storage_gwh"],
        "stations": f["stations"],
        "connectors": f["connectors"],
        "source": dict(f["src"]),
    }
    if yoy:
        y = FACTS[yoy]
        row["yoy"] = {
            "vs": yoy,
            "revenue_pct": _pct(rev, y["revenue"]),
            "op_income_delta": f["op_income"] - y["op_income"],
            "net_income_delta": f["net_income"] - y["net_income"],
            "deliveries_pct": _pct(f["deliveries"], y["deliveries"]),
            "storage_pct": _pct(f["storage_gwh"], y["storage_gwh"]),
        }
    else:
        row["yoy"] = None
    return row


def normalize():
    quarters = [
        build_period("Q1'25"),
        build_period("Q2'25"),
        build_period("Q3'25"),
        build_period("Q4'25"),
        build_period("Q1'26", yoy="Q1'25"),
        build_period("Q2'26", yoy="Q2'25"),
    ]
    annuals = [
        build_period("2023"),
        build_period("2024", yoy="2023"),
        build_period("2025", yoy="2024"),
    ]
    return {
        "company": {"name": "Tesla, Inc.",
                    "ticker": "TSLA", "exchange": "Nasdaq",
                    "currency": "USD", "units": "$ millions"},
        "latest": "Q2'26",
        "quarters": quarters,
        "annuals": annuals,
    }
