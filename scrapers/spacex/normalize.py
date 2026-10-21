"""Normalize SpaceX filings to dashboard-friendly metrics.

Source values and units are preserved below ($ millions, except per-share
$ and share counts in millions). Unavailable fields use None -- never
fabricated estimates.

Company-specific label mappings (filing row name -> key):
- "Launch Services" -> launch_services (Space)
- "Launch & Development" -> launch_development (Space)
- "Consumer" -> consumer (Connectivity)
- "Enterprise & Government" -> enterprise_government (Connectivity)
- "Advertising" -> advertising (AI)
- "AI Solutions & Infrastructure" -> ai_solutions_infrastructure (AI)
- "All of products revenue is attributable to the Connectivity segment"
  (S-1 Note 3): the Product-vs-Service split total is Connectivity-only.

Provenance: S-1 filed 2026-05-20 (accn 0001628280-26-036936) carries
FY2023/FY2024/FY2025 annuals and Q1'25/Q1'26 interim statements;
10-Q for quarter ended 2026-06-30 filed 2026-08-04
(accn 0001628280-26-052535) carries Q2'25/H1'25/Q2'26/H1'26 comparatives.
"""

S1 = {"form": "S-1", "accession": "0001628280-26-036936", "filed": "2026-05-20"}
Q2 = {"form": "10-Q", "accession": "0001628280-26-052535", "filed": "2026-08-04",
      "period_end": "2026-06-30"}
E8K = {"form": "8-K", "accession": "0001628280-26-066482", "filed": "2026-10-20",
       "note": "Q3'26 earnings release Ex. 99.1; 10-Q not yet filed"}

SEGMENTS = ("space", "connectivity", "ai")
PRODUCTS = ("launch_services", "launch_development", "consumer",
            "enterprise_government", "advertising",
            "ai_solutions_infrastructure")

# Curated source facts. Keys: revenue, op_income, net_income, eps_basic,
# eps_diluted, seg_rev{...}, seg_op{...}, products{...}.
FACTS = {
    "2023": {
        "revenue": 10387, "op_income": -3505, "net_income": -4628,
        "eps_basic": -1.68, "eps_diluted": -1.68,
        "seg_rev": {"space": 3557, "connectivity": 3869, "ai": 2961},
        "seg_op": {"space": -1, "connectivity": 469, "ai": -3973},
        "products": {"launch_services": 1964, "launch_development": 1593,
                     "consumer": 2817, "enterprise_government": 1052,
                     "advertising": 2323, "ai_solutions_infrastructure": 638},
        "launches": 98, "mass_to_orbit_t": 1210, "src": S1,
    },
    "2024": {
        "revenue": 14015, "op_income": 466, "net_income": 791,
        "eps_basic": 0.01, "eps_diluted": 0.00,
        "seg_rev": {"space": 3796, "connectivity": 7599, "ai": 2620},
        "seg_op": {"space": 21, "connectivity": 2006, "ai": -1561},
        "products": {"launch_services": 2584, "launch_development": 1212,
                     "consumer": 4830, "enterprise_government": 2769,
                     "advertising": 1728, "ai_solutions_infrastructure": 892},
        "launches": 138, "mass_to_orbit_t": 1699, "src": S1,
    },
    "2025": {
        "revenue": 18674, "op_income": -2589, "net_income": -4937,
        "eps_basic": -1.69, "eps_diluted": -1.69,
        "seg_rev": {"space": 4086, "connectivity": 11387, "ai": 3201},
        "seg_op": {"space": -657, "connectivity": 4423, "ai": -6355},
        "products": {"launch_services": 2576, "launch_development": 1510,
                     "consumer": 7208, "enterprise_government": 4179,
                     "advertising": 1844, "ai_solutions_infrastructure": 1357},
        "launches": 170, "mass_to_orbit_t": 2213, "src": S1,
    },
    "Q1'25": {
        "revenue": 4067, "op_income": 27, "net_income": -528,
        "eps_basic": -0.18, "eps_diluted": -0.18,
        "seg_rev": {"space": 865, "connectivity": 2475, "ai": 727},
        "seg_op": {"space": -70, "connectivity": 1033, "ai": -936},
        "products": {"launch_services": 566, "launch_development": 299,
                     "consumer": 1492, "enterprise_government": 983,
                     "advertising": 443, "ai_solutions_infrastructure": 284},
        "launches": 38, "mass_to_orbit_t": 450, "src": S1,
    },
    "Q2'25": {
        "revenue": 4071, "op_income": -970, "net_income": -1008,
        "eps_basic": -0.34, "eps_diluted": -0.34,
        "seg_rev": {"space": 746, "connectivity": 2588, "ai": 737},
        "seg_op": {"space": -369, "connectivity": 923, "ai": -1524},
        "products": {"launch_services": 490, "launch_development": 256,
                     "consumer": 1721, "enterprise_government": 867,
                     "advertising": 426, "ai_solutions_infrastructure": 311},
        "launches": None, "mass_to_orbit_t": None, "src": Q2,
    },
    "Q3'25": {
        "revenue": 5576, "op_income": -273, "net_income": -1054,
        "eps_basic": -0.36, "eps_diluted": -0.36,
        "seg_rev": {"space": 1666, "connectivity": 3097, "ai": 813},
        "seg_op": {"space": 259, "connectivity": 1190, "ai": -1722},
        "products": {"launch_services": 1000, "launch_development": 666,
                     "consumer": 1986, "enterprise_government": 1111,
                     "advertising": 454, "ai_solutions_infrastructure": 359},
        "launches": 44, "mass_to_orbit_t": 525, "src": E8K,
    },
    "Q3'26": {
        "revenue": 14575, "op_income": 2791, "net_income": 4404,
        "eps_basic": 0.37, "eps_diluted": 0.35,
        "seg_rev": {"space": 1767, "connectivity": 5248, "ai": 7560},
        "seg_op": {"space": -7, "connectivity": 2367, "ai": 431},
        "products": {"launch_services": 1130, "launch_development": 637,
                     "consumer": 3121, "enterprise_government": 2127,
                     "advertising": 538, "ai_solutions_infrastructure": 7022},
        "launches": 35, "mass_to_orbit_t": 476, "src": E8K,
    },
    "Q1'26": {
        "revenue": 4694, "op_income": -1943, "net_income": -4276,
        "eps_basic": -1.27, "eps_diluted": -1.27,
        "seg_rev": {"space": 619, "connectivity": 3257, "ai": 818},
        "seg_op": {"space": -662, "connectivity": 1188, "ai": -2469},
        "products": {"launch_services": 330, "launch_development": 289,
                     "consumer": 2148, "enterprise_government": 1109,
                     "advertising": 343, "ai_solutions_infrastructure": 475},
        "launches": 40, "mass_to_orbit_t": 556, "src": S1,
    },
    "Q2'26": {
        "revenue": 7814, "op_income": -143, "net_income": -541,
        "eps_basic": -0.09, "eps_diluted": -0.09,
        "seg_rev": {"space": 962, "connectivity": 4291, "ai": 2561},
        "seg_op": {"space": -542, "connectivity": 1656, "ai": -1257},
        "products": {"launch_services": 648, "launch_development": 314,
                     "consumer": 2485, "enterprise_government": 1806,
                     "advertising": 367, "ai_solutions_infrastructure": 2194},
        "launches": None, "mass_to_orbit_t": None, "src": Q2,
    },
}

QUARTER_ORDER = ["Q1'25", "Q2'25", "Q3'25", "Q1'26", "Q2'26", "Q3'26"]
ANNUAL_ORDER = ["2023", "2024", "2025"]


def _check_ties(label, f):
    assert sum(f["seg_rev"].values()) == f["revenue"], f"segment tie {label}"
    assert sum(f["products"].values()) == f["revenue"], f"product tie {label}"
    assert sum(f["seg_op"].values()) == f["op_income"], f"seg-op tie {label}"


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
        "op_margin_pct": round(f["op_income"] / rev * 100, 1),
        "net_margin_pct": round(f["net_income"] / rev * 100, 1),
        "segments": {
            s: {"revenue": f["seg_rev"][s],
                "share_pct": round(f["seg_rev"][s] / rev * 100, 1),
                "op_income": f["seg_op"][s]}
            for s in SEGMENTS
        },
        "products": dict(f["products"]),
        "launches": f["launches"],
        "mass_to_orbit_t": f["mass_to_orbit_t"],
        "source": dict(f["src"]),
    }
    if yoy:
        y = FACTS[yoy]
        row["yoy"] = {
            "vs": yoy,
            "revenue_pct": _pct(rev, y["revenue"]),
            "op_income_delta": f["op_income"] - y["op_income"],
            "net_income_delta": f["net_income"] - y["net_income"],
        }
    else:
        row["yoy"] = None
    return row


def normalize():
    quarters = [
        build_period("Q1'25"),
        build_period("Q2'25"),
        build_period("Q3'25"),
        build_period("Q1'26", yoy="Q1'25"),
        build_period("Q2'26", yoy="Q2'25"),
        build_period("Q3'26", yoy="Q3'25"),
    ]
    annuals = [
        build_period("2023"),
        build_period("2024", yoy="2023"),
        build_period("2025", yoy="2024"),
    ]
    return {
        "company": {"name": "Space Exploration Technologies Corp.",
                    "ticker": "SPCX", "exchange": "Nasdaq",
                    "currency": "USD", "units": "$ millions"},
        "latest": "Q3'26",
        "quarters": quarters,
        "annuals": annuals,
    }
