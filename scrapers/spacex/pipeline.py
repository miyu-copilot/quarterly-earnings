"""SpaceX pipeline: download (EDGAR cache) -> normalize -> export bundle.

Usage:
    python3 -m scrapers.spacex.pipeline
    python3 -m scrapers.spacex.pipeline --full-refresh
    python3 -m scrapers.spacex.pipeline --quarter "Q2'26"
"""

import argparse
import os
import sys
import urllib.request

from .dashboard_export import export
from .normalize import normalize
from .quarters import COMPANY, XBRL_COMPANYFACTS, filing_url, release_urls

RAW = os.path.join("data", "spacex", "raw")
UA = {"User-Agent": "MuseCode Dashboard Research contact@example.com"}


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as fh:
        fh.write(resp.read())
    return dest


def ensure_cache(full_refresh=False):
    """Ensure raw EDGAR cache exists; re-download on --full-refresh."""
    os.makedirs(RAW, exist_ok=True)
    cached = {
        "companyfacts.json": XBRL_COMPANYFACTS,
        "spcx-20260630.htm": filing_url("0001628280-26-052535", "spcx-20260630.htm"),
        "spaceexplorationtechnologi.htm": filing_url(
            "0001628280-26-036936", "spaceexplorationtechnologi.htm"),
    }
    for name, url in cached.items():
        dest = os.path.join(RAW, name)
        if full_refresh or not os.path.exists(dest) or os.path.getsize(dest) == 0:
            try:
                download(url, dest)
                print(f"downloaded {name}")
            except Exception as exc:  # keep cache usable offline
                print(f"WARN: could not refresh {name}: {exc}", file=sys.stderr)
    return RAW


def main(argv=None):
    ap = argparse.ArgumentParser(description="SpaceX dashboard pipeline")
    ap.add_argument("--full-refresh", action="store_true")
    ap.add_argument("--quarter", default=None,
                    help="period label to verify, e.g. \"Q2'26\"")
    args = ap.parse_args(argv)

    print(f"{COMPANY['name']} ({COMPANY['ticker']}, {COMPANY['exchange']})")
    for r in release_urls():
        print(f"  {r['period']:8s} {r['form']:5s} filed {r['filed']} {r['url']}")
    ensure_cache(full_refresh=args.full_refresh)

    data = normalize()
    if args.quarter:
        rows = [p for p in data["quarters"] + data["annuals"]
                if p["period"] == args.quarter]
        if not rows:
            raise SystemExit(f"unknown period {args.quarter!r}")
        print(f"verified {args.quarter}: revenue={rows[0]['revenue']}")
    path, bundle = export()
    print(f"wrote {path}: {len(bundle['quarters'])} quarters, "
          f"{len(bundle['annuals'])} annuals")


if __name__ == "__main__":
    main()
