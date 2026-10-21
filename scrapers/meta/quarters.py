"""Meta release registry for the quarterly earnings dashboard.

Sources are Meta's 8-K earnings releases (Exhibit 99.1), filed the same
day results are announced. Quarterly figures come from each release's
financial highlights, segment information table, and GAAP-to-non-GAAP
reconciliation (capital expenditures = purchases of property and
equipment + principal payments on finance leases; free cash flow as
defined there). Annual figures are the twelve-month columns of the Q4
releases. Meta reports segment operating income directly: Family of
Apps (FoA) and Reality Labs (RL).
"""

CIK = "0001326801"
ARCHIVES = "https://www.sec.gov/Archives/edgar/data/1326801"

COMPANY = {
    "name": "Meta Platforms, Inc.",
    "ticker": "META",
    "exchange": "Nasdaq",
    "segments": ["foa", "reality_labs"],
    "segment_labels": {
        "foa": "Family of Apps",
        "reality_labs": "Reality Labs",
    },
    "products": ["advertising", "other"],
    "product_labels": {
        "advertising": "Advertising",
        "other": "Other revenue (FoA)",
    },
}

# The 8-K earnings release carrying each period (filed date, accession
# number without dashes for cache filename suffix, exhibit filename).
RELEASES = [
    {"period": "Q4'23", "form": "8-K", "filed": "2024-02-01",
     "accession": "0001326801-24-000010", "primary": "meta-20240201.htm",
     "exhibit": "meta-12312023xexhibit991.htm", "cache": "meta-q423-ex99.htm"},
    {"period": "Q4'24", "form": "8-K", "filed": "2025-01-29",
     "accession": "0001326801-25-000014", "primary": "meta-20250129.htm",
     "exhibit": "meta-12312024xexhibit991.htm", "cache": "meta-000014-ex99.htm"},
    {"period": "Q1'25", "form": "8-K", "filed": "2025-04-30",
     "accession": "0001326801-25-000050", "primary": "meta-20250430.htm",
     "exhibit": "meta-03312025xexhibit991.htm", "cache": "meta-000050-ex99.htm"},
    {"period": "Q2'25", "form": "8-K", "filed": "2025-07-30",
     "accession": "0001628280-25-036719", "primary": "meta-20250730.htm",
     "exhibit": "meta-06302025xexhibit991.htm", "cache": "meta-036719-ex99.htm"},
    {"period": "Q3'25", "form": "8-K", "filed": "2025-10-29",
     "accession": "0001628280-25-047114", "primary": "meta-20251029.htm",
     "exhibit": "meta-09302025xexhibit991.htm", "cache": "meta-047114-ex99.htm"},
    {"period": "Q4'25", "form": "8-K", "filed": "2026-01-28",
     "accession": "0001628280-26-003832", "primary": "meta-20260128.htm",
     "exhibit": "meta-12312025xexhibit991.htm", "cache": "meta-003832-ex99.htm"},
    {"period": "Q1'26", "form": "8-K", "filed": "2026-04-29",
     "accession": "0001628280-26-028364", "primary": "meta-20260429.htm",
     "exhibit": "meta-03312026xexhibit991.htm", "cache": "meta-028364-ex99.htm"},
    {"period": "Q2'26", "form": "8-K", "filed": "2026-07-29",
     "accession": "0001628280-26-050596", "primary": "meta-20260729.htm",
     "exhibit": "meta-06302026xexhibit991.htm", "cache": "meta-050596-ex99.htm"},
    {"period": "Q3'26", "form": "8-K", "filed": "2026-10-21",
     "accession": "0001628280-26-066700", "primary": "meta-20261019.htm",
     "exhibit": "meta-09302026xexhibit991.htm", "cache": "meta-066700-ex99.htm"},
]


def filing_url(accession, primary):
    return f"{ARCHIVES}/{accession.replace('-', '')}/{primary}"


def exhibit_url(release):
    return f"{ARCHIVES}/{release['accession'].replace('-', '')}/{release['exhibit']}"
