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

Operating metrics (the company's own Key Business Metrics):
- starlink_subs_m: Starlink subscribers in millions, end of period
  (unique service lines; excludes managed enterprise/government contracts).
  S-1 segment table: Q1'25 5.0, Q1'26 10.3, FY2023 2.3, FY2024 4.4,
  FY2025 8.9. 10-Q KPI table: Q2'25 6.0, Q2'26 12.0. Q3'26 release
  segment table: Q3'25 7.2, Q3'26 13.6.
- starlink_arpu: $ per month. S-1: Q1'25 86, Q1'26 66, FY2023 99,
  FY2024 91, FY2025 81. 10-Q: Q2'25 85, Q2'26 66. Release: Q3'25 83,
  Q3'26 69.
- compute_gw: nameplate compute draw in GW, end of period. S-1: Q1'25
  0.3, Q1'26 1.0, FY2023 0.0, FY2024 0.3, FY2025 0.8. 10-Q: Q2'25 0.4,
  Q2'26 1.4. Release: Q3'25 0.6, Q3'26 1.7.
- launches / mass_to_orbit_t for Q2'25 (46 / 652 t) and Q2'26 (38 /
  485 t) were previously None; the 10-Q KPI tables (Falcon 45 + Starship
  1 in Q2'25; Falcon 37 + Starship 1 in Q2'26; mass tables) and the
  Q3'26 release's comparative columns now pin them.
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
        "launches": 98, "mass_to_orbit_t": 1210, "starlink_subs_m": 2.3, "starlink_arpu": 99, "compute_gw": 0.0, "src": S1,
    },
    "2024": {
        "revenue": 14015, "op_income": 466, "net_income": 791,
        "eps_basic": 0.01, "eps_diluted": 0.00,
        "seg_rev": {"space": 3796, "connectivity": 7599, "ai": 2620},
        "seg_op": {"space": 21, "connectivity": 2006, "ai": -1561},
        "products": {"launch_services": 2584, "launch_development": 1212,
                     "consumer": 4830, "enterprise_government": 2769,
                     "advertising": 1728, "ai_solutions_infrastructure": 892},
        "launches": 138, "mass_to_orbit_t": 1699, "starlink_subs_m": 4.4, "starlink_arpu": 91, "compute_gw": 0.3, "src": S1,
    },
    "2025": {
        "revenue": 18674, "op_income": -2589, "net_income": -4937,
        "eps_basic": -1.69, "eps_diluted": -1.69,
        "seg_rev": {"space": 4086, "connectivity": 11387, "ai": 3201},
        "seg_op": {"space": -657, "connectivity": 4423, "ai": -6355},
        "products": {"launch_services": 2576, "launch_development": 1510,
                     "consumer": 7208, "enterprise_government": 4179,
                     "advertising": 1844, "ai_solutions_infrastructure": 1357},
        "launches": 170, "mass_to_orbit_t": 2213, "starlink_subs_m": 8.9, "starlink_arpu": 81, "compute_gw": 0.8, "src": S1,
    },
    "Q1'25": {
        "revenue": 4067, "op_income": 27, "net_income": -528,
        "eps_basic": -0.18, "eps_diluted": -0.18,
        "seg_rev": {"space": 865, "connectivity": 2475, "ai": 727},
        "seg_op": {"space": -70, "connectivity": 1033, "ai": -936},
        "products": {"launch_services": 566, "launch_development": 299,
                     "consumer": 1492, "enterprise_government": 983,
                     "advertising": 443, "ai_solutions_infrastructure": 284},
        "launches": 38, "mass_to_orbit_t": 450, "starlink_subs_m": 5.0, "starlink_arpu": 86, "compute_gw": 0.3, "src": S1,
    },
    "Q2'25": {
        "revenue": 4071, "op_income": -970, "net_income": -1008,
        "eps_basic": -0.34, "eps_diluted": -0.34,
        "seg_rev": {"space": 746, "connectivity": 2588, "ai": 737},
        "seg_op": {"space": -369, "connectivity": 923, "ai": -1524},
        "products": {"launch_services": 490, "launch_development": 256,
                     "consumer": 1721, "enterprise_government": 867,
                     "advertising": 426, "ai_solutions_infrastructure": 311},
        "launches": 46, "mass_to_orbit_t": 652, "starlink_subs_m": 6.0, "starlink_arpu": 85, "compute_gw": 0.4, "src": Q2,
    },
    "Q3'25": {
        "revenue": 5576, "op_income": -273, "net_income": -1054,
        "eps_basic": -0.36, "eps_diluted": -0.36,
        "seg_rev": {"space": 1666, "connectivity": 3097, "ai": 813},
        "seg_op": {"space": 259, "connectivity": 1190, "ai": -1722},
        "products": {"launch_services": 1000, "launch_development": 666,
                     "consumer": 1986, "enterprise_government": 1111,
                     "advertising": 454, "ai_solutions_infrastructure": 359},
        "launches": 44, "mass_to_orbit_t": 525, "starlink_subs_m": 7.2, "starlink_arpu": 83, "compute_gw": 0.6, "src": E8K,
    },
    "Q3'26": {
        "revenue": 14575, "op_income": 2791, "net_income": 4404,
        "eps_basic": 0.37, "eps_diluted": 0.35,
        "seg_rev": {"space": 1767, "connectivity": 5248, "ai": 7560},
        "seg_op": {"space": -7, "connectivity": 2367, "ai": 431},
        "products": {"launch_services": 1130, "launch_development": 637,
                     "consumer": 3121, "enterprise_government": 2127,
                     "advertising": 538, "ai_solutions_infrastructure": 7022},
        "launches": 35, "mass_to_orbit_t": 476, "starlink_subs_m": 13.6, "starlink_arpu": 69, "compute_gw": 1.7, "src": E8K,
    },
    "Q1'26": {
        "revenue": 4694, "op_income": -1943, "net_income": -4276,
        "eps_basic": -1.27, "eps_diluted": -1.27,
        "seg_rev": {"space": 619, "connectivity": 3257, "ai": 818},
        "seg_op": {"space": -662, "connectivity": 1188, "ai": -2469},
        "products": {"launch_services": 330, "launch_development": 289,
                     "consumer": 2148, "enterprise_government": 1109,
                     "advertising": 343, "ai_solutions_infrastructure": 475},
        "launches": 40, "mass_to_orbit_t": 556, "starlink_subs_m": 10.3, "starlink_arpu": 66, "compute_gw": 1.0, "src": S1,
    },
    "Q2'26": {
        "revenue": 7814, "op_income": -143, "net_income": -541,
        "eps_basic": -0.09, "eps_diluted": -0.09,
        "seg_rev": {"space": 962, "connectivity": 4291, "ai": 2561},
        "seg_op": {"space": -542, "connectivity": 1656, "ai": -1257},
        "products": {"launch_services": 648, "launch_development": 314,
                     "consumer": 2485, "enterprise_government": 1806,
                     "advertising": 367, "ai_solutions_infrastructure": 2194},
        "launches": 38, "mass_to_orbit_t": 485, "starlink_subs_m": 12.0, "starlink_arpu": 66, "compute_gw": 1.4, "src": Q2,
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
        "starlink_subs_m": f.get("starlink_subs_m"),
        "starlink_arpu": f.get("starlink_arpu"),
        "compute_gw": f.get("compute_gw"),
        "source": dict(f["src"]),
    }
    if yoy:
        y = FACTS[yoy]
        row["yoy"] = {
            "vs": yoy,
            "revenue_pct": _pct(rev, y["revenue"]),
            "op_income_delta": f["op_income"] - y["op_income"],
            "net_income_delta": f["net_income"] - y["net_income"],
            "subs_pct": _pct(f.get("starlink_subs_m"),
                             y.get("starlink_subs_m")),
            "compute_pct": _pct(f.get("compute_gw"), y.get("compute_gw")),
            "arpu_pct": _pct(f.get("starlink_arpu"),
                             y.get("starlink_arpu")),
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
