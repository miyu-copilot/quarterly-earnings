"""Export the normalized Meta dataset to the frontend JSON bundle."""

import json
import os

from .normalize import normalize

EXPORT_PATH = os.path.join("data", "exports", "meta_bundle.json")


def export(path=EXPORT_PATH):
    bundle = normalize()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, indent=2)
    # Audit copy of the normalized layer beside the raw cache.
    processed = os.path.join("data", "meta", "processed", "quarters.json")
    os.makedirs(os.path.dirname(processed), exist_ok=True)
    with open(processed, "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, indent=2)
    return path, bundle


if __name__ == "__main__":
    path, bundle = export()
    print(f"wrote {path}: {len(bundle['quarters'])} quarters, "
          f"{len(bundle['annuals'])} annuals")
