"""Known SpaceX earnings release locations.

Primary source per user: https://ir.spacex.com/financials/ (Quarterly
Results + SEC Filings tabs). The IR page shell is JS-rendered, so the
pipeline pins the underlying SEC EDGAR documents directly and treats the
IR page as the discovery cross-check.
"""

COMPANY = {
    "name": "Space Exploration Technologies Corp.",
    "ticker": "SPCX",
    "exchange": "Nasdaq",
    "currency": "USD",
    "slug": "spacex",
    "cik": "0001181412",
    "ir_financials": "https://ir.spacex.com/financials/",
}

# EDGAR documents backing each reported period. Accession numbers are the
# stable identifiers; primary docs are cached under data/spacex/raw/.
RELEASES = [
    {
        "period": "FY2023",
        "form": "S-1",
        "accession": "0001628280-26-036936",
        "filed": "2026-05-20",
        "primary": "spaceexplorationtechnologi.htm",
    },
    {
        "period": "Q1'25",
        "form": "S-1",
        "accession": "0001628280-26-036936",
        "filed": "2026-05-20",
        "primary": "spaceexplorationtechnologi.htm",
    },
    {
        "period": "Q2'25",
        "form": "10-Q",
        "accession": "0001628280-26-052535",
        "filed": "2026-08-04",
        "primary": "spcx-20260630.htm",
    },
    {
        "period": "Q3'25",
        "form": "8-K",
        "accession": "0001628280-26-066482",
        "filed": "2026-10-20",
        "primary": "spcx-q3-2026-ex99.htm",
        "note": "Comparative column in Q3'26 earnings release (Ex. 99.1); "
                "no standalone Q3'25 filing exists (pre-IPO).",
    },
    {
        "period": "Q3'26",
        "form": "8-K",
        "accession": "0001628280-26-066482",
        "filed": "2026-10-20",
        "primary": "spcx-q3-2026-ex99.htm",
        "note": "Q3'26 earnings release (Ex. 99.1); segment now labeled SI "
                "(Super Intelligence). 10-Q not yet filed.",
    },
    {
        "period": "Q1'26",
        "form": "S-1",
        "accession": "0001628280-26-036936",
        "filed": "2026-05-20",
        "primary": "spaceexplorationtechnologi.htm",
    },
    {
        "period": "Q2'26",
        "form": "10-Q",
        "accession": "0001628280-26-052535",
        "filed": "2026-08-04",
        "primary": "spcx-20260630.htm",
    },
]

XBRL_COMPANYFACTS = (
    "https://data.sec.gov/api/xbrl/companyfacts/CIK0001181412.json"
)


def filing_url(accession, primary=""):
    """Build an EDGAR archive URL for an accession + document."""
    nospace = accession.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/1181412/{nospace}/"
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
