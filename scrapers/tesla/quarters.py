"""Known Tesla earnings release locations.

Primary source: Tesla investor relations quarterly disclosures
(https://ir.tesla.com/#quarterly-disclosure). The pipeline pins the
underlying SEC EDGAR documents directly: the quarterly update letter
furnished as Exhibit 99.1 to a Form 8-K on earnings day (financial
statements, revenue disaggregation, production/deliveries, energy
deployments) and the annual Form 10-K (audited annuals, revenue note,
segment note).
"""

COMPANY = {
    "name": "Tesla, Inc.",
    "ticker": "TSLA",
    "exchange": "Nasdaq",
    "currency": "USD",
    "slug": "tesla",
    "cik": "0001318605",
    "ir_financials": "https://ir.tesla.com/#quarterly-disclosure",
}

# EDGAR documents backing each reported period. Accession numbers are the
# stable identifiers; primary docs are cached under data/tesla/raw/.
RELEASES = [
    {
        "period": "Q1'25",
        "form": "8-K",
        "accession": "0001628280-25-018851",
        "filed": "2025-04-22",
        "primary": "exhbit991.htm",
        "cache": "tsla-20250422-ex99.htm",
        "note": "Q1'25 update letter (Ex. 99.1; exhibit filed as "
                "'exhbit991.htm').",
    },
    {
        "period": "Q2'25",
        "form": "8-K",
        "accession": "0001628280-25-035738",
        "filed": "2025-07-23",
        "primary": "exhibit991.htm",
        "cache": "tsla-20250723-ex99.htm",
        "note": "Q2'25 update letter (Ex. 99.1).",
    },
    {
        "period": "Q3'25",
        "form": "8-K",
        "accession": "0001628280-25-045861",
        "filed": "2025-10-22",
        "primary": "exhibit991.htm",
        "cache": "tsla-20251022-ex99.htm",
        "note": "Q3'25 update letter (Ex. 99.1).",
    },
    {
        "period": "Q4'25",
        "form": "8-K",
        "accession": "0001628280-26-003837",
        "filed": "2026-01-28",
        "primary": "exhibit991.htm",
        "cache": "tsla-20260128-ex99.htm",
        "note": "Q4'25 update letter (Ex. 99.1); also carries the "
                "FY2021-FY2025 financial summary.",
    },
    {
        "period": "Q1'26",
        "form": "8-K",
        "accession": "0001628280-26-026551",
        "filed": "2026-04-22",
        "primary": "exhibit991.htm",
        "cache": "tsla-20260422-ex99.htm",
        "note": "Q1'26 update letter (Ex. 99.1).",
    },
    {
        "period": "Q2'26",
        "form": "8-K",
        "accession": "0001628280-26-049213",
        "filed": "2026-07-22",
        "primary": "exhibit991.htm",
        "cache": "tsla-20260722-ex99.htm",
        "note": "Q2'26 update letter (Ex. 99.1).",
    },
    {
        "period": "FY2025",
        "form": "10-K",
        "accession": "0001628280-26-003952",
        "filed": "2026-01-29",
        "primary": "tsla-20251231.htm",
        "note": "FY2025 10-K: audited FY2023-FY2025 statements, revenue "
                "disaggregation note and segment note. Not cached in "
                "data/tesla/raw/ (multi-MB); read live from EDGAR.",
    },
    {
        "period": "Q4'24",
        "form": "8-K",
        "accession": "0001628280-25-002993",
        "filed": "2025-01-29",
        "primary": "exhibit991.htm",
        "cache": "tsla-20250129-ex99.htm",
        "note": "Q4'24 update letter (Ex. 99.1); FY2024 comparatives and "
                "the FY2020-FY2024 financial summary.",
    },
]

XBRL_COMPANYFACTS = (
    "https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json"
)


def filing_url(accession, primary=""):
    """Build an EDGAR archive URL for an accession + document."""
    nospace = accession.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/1318605/{nospace}/"
    return base + primary if primary else base


def release_urls():
    """Enumerate known release URLs (primary source list for the pipeline)."""
    return [
        {
            "period": r["period"],
            "form": r["form"],
            "filed": r["filed"],
            "url": filing_url(r["accession"], r["primary"]),
        }
        for r in RELEASES
    ]
