"""Meta pipeline: download (EDGAR cache) -> normalize -> export bundle.

Usage:
    python3 -m scrapers.meta.pipeline
    python3 -m scrapers.meta.pipeline --full-refresh
    python3 -m scrapers.meta.pipeline --quarter "Q3'26"

The cache holds the 8-K earnings releases (Exhibit 99.1 exhibits).
"""

import argparse
import os
import sys
import urllib.request

from .dashboard_export import export
from .normalize import normalize
from .quarters import COMPANY, RELEASES, exhibit_url, filing_url

RAW = os.path.join("data", "meta", "raw")
UA = {"User-Agent": "MuseCode Dashboard Research contact@example.com"}


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as fh:
        fh.write(resp.read())
    return dest


def ensure_cache(full_refresh=False):
    """Ensure raw EDGAR cache exists; re-download on --full-refresh."""
    os.makedirs(RAW, exist_ok=True)
    for r in RELEASES:
        if "cache" not in r:
            continue
        dest = os.path.join(RAW, r["cache"])
        if full_refresh or not os.path.exists(dest) or os.path.getsize(dest) == 0:
            try:
                download(exhibit_url(r), dest)
                print(f"downloaded {r['cache']}")
            except Exception as exc:  # keep cache usable offline
                print(f"WARN: could not refresh {r['cache']}: {exc}",
                      file=sys.stderr)
    return RAW


def main(argv=None):
    ap = argparse.ArgumentParser(description="Meta dashboard pipeline")
    ap.add_argument("--full-refresh", action="store_true")
    ap.add_argument("--quarter", default=None,
                    help="period label to verify, e.g. \"Q3'26\"")
    args = ap.parse_args(argv)

    print(f"{COMPANY['name']} ({COMPANY['ticker']}, {COMPANY['exchange']})")
    for r in RELEASES:
        print(f"  {r['period']:8s} {r['form']:5s} filed {r['filed']} "
              f"{filing_url(r['accession'], r['primary'])}")
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
