"""Focused tests for the Tesla parser/normalizer layer."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scrapers.tesla.normalize import FACTS, normalize
from scrapers.tesla.parse import letter_periods

RAW = os.path.join("data", "tesla", "raw")


class TestNormalize(unittest.TestCase):
    def test_bundle_shape(self):
        data = normalize()
        self.assertEqual(data["latest"], "Q2'26")
        self.assertEqual(len(data["quarters"]), 6)
        self.assertEqual(len(data["annuals"]), 3)

    def test_ties(self):
        # Segment revenue sums to total revenue; automotive product lines
        # sum to automotive revenue; segment gross profit (when fully
        # disclosed) sums to total gross profit.
        for label, f in FACTS.items():
            with self.subTest(period=label):
                self.assertEqual(sum(f["seg_rev"].values()), f["revenue"])
                self.assertEqual(sum(f["products"].values()),
                                 f["seg_rev"]["automotive"])
                if all(v is not None for v in f["seg_gp"].values()):
                    self.assertEqual(sum(f["seg_gp"].values()),
                                     f["gross_profit"])

    def test_yoy_math(self):
        data = normalize()
        q2 = next(q for q in data["quarters"] if q["period"] == "Q2'26")
        # (28236 - 22496) / 22496 * 100 = 25.5%
        self.assertAlmostEqual(q2["yoy"]["revenue_pct"], 25.5, places=1)
        self.assertEqual(q2["yoy"]["vs"], "Q2'25")
        # (480126 - 384122) / 384122 * 100 = 25.0%
        self.assertAlmostEqual(q2["yoy"]["deliveries_pct"], 25.0, places=1)

    def test_missing_stays_missing(self):
        data = normalize()
        fy23 = next(a for a in data["annuals"] if a["period"] == "2023")
        self.assertIsNone(fy23["segments"]["automotive"]["gross_profit"])
        self.assertIsNone(fy23["segments"]["energy"]["gross_profit"])

    def test_letters_match_curated(self):
        # Each quarter's own update letter must reproduce the curated
        # revenue / operating income / net income / diluted EPS.
        letters = {
            "Q1'25": "tsla-20250422-ex99.htm",
            "Q2'25": "tsla-20250723-ex99.htm",
            "Q3'25": "tsla-20251022-ex99.htm",
            "Q4'25": "tsla-20260128-ex99.htm",
            "Q1'26": "tsla-20260422-ex99.htm",
            "Q2'26": "tsla-20260722-ex99.htm",
        }
        for period, name in letters.items():
            path = os.path.join(RAW, name)
            if not os.path.exists(path):
                self.skipTest(f"raw letter {name} not cached")
            got = letter_periods(path)[period]
            f = FACTS[period]
            with self.subTest(period=period):
                self.assertEqual(got["rev"]["Total revenues"], f["revenue"])
                self.assertEqual(got["op_income"], f["op_income"])
                self.assertEqual(got["net_income"], f["net_income"])
                self.assertAlmostEqual(got["eps_diluted"],
                                       f["eps_diluted"], places=2)
                self.assertEqual(got["ops"]["Total deliveries"],
                                 f["deliveries"])


if __name__ == "__main__":
    unittest.main()
