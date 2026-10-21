"""Focused tests for the SpaceX parser/normalizer layer."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scrapers.spacex.normalize import FACTS, normalize
from scrapers.spacex.parse import revenue_by_period_segment

RAW = os.path.join("data", "spacex", "raw")


class TestNormalize(unittest.TestCase):
    def test_bundle_shape(self):
        data = normalize()
        self.assertEqual(data["latest"], "Q3'26")
        self.assertEqual(len(data["quarters"]), 6)
        self.assertEqual(len(data["annuals"]), 3)

    def test_segment_ties(self):
        # Every period's segment and product splits sum to total revenue,
        # and segment operating income sums to consolidated operating income.
        for label, f in FACTS.items():
            with self.subTest(period=label):
                self.assertEqual(sum(f["seg_rev"].values()), f["revenue"])
                self.assertEqual(sum(f["products"].values()), f["revenue"])
                self.assertEqual(sum(f["seg_op"].values()), f["op_income"])

    def test_yoy_math(self):
        data = normalize()
        q2 = next(q for q in data["quarters"] if q["period"] == "Q2'26")
        # (7814 - 4071) / 4071 * 100 = 91.9%
        self.assertAlmostEqual(q2["yoy"]["revenue_pct"], 91.9, places=1)
        self.assertEqual(q2["yoy"]["vs"], "Q2'25")
        q3 = next(q for q in data["quarters"] if q["period"] == "Q3'26")
        # (14575 - 5576) / 5576 * 100 = 161.4%
        self.assertAlmostEqual(q3["yoy"]["revenue_pct"], 161.4, places=1)
        self.assertEqual(q3["yoy"]["vs"], "Q3'25")

    def test_missing_stays_missing(self):
        data = normalize()
        q2 = next(q for q in data["quarters"] if q["period"] == "Q2'25")
        self.assertIsNone(q2["launches"])
        self.assertIsNone(q2["mass_to_orbit_t"])

    def test_10q_xbrl_matches_curated(self):
        # Curated Q2'26 segment revenue must equal the inline-XBRL facts.
        path = os.path.join(RAW, "spcx-20260630.htm")
        if not os.path.exists(path):
            self.skipTest("raw 10-Q not cached")
        seg = revenue_by_period_segment(path)[("2026-04-01", "2026-06-30")]
        for key in ("space", "connectivity", "ai"):
            self.assertEqual(seg[key], FACTS["Q2'26"]["seg_rev"][key])


if __name__ == "__main__":
    unittest.main()
