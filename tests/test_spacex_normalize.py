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

    def test_operating_metrics(self):
        # Starlink subs (M) / ARPU ($/mo) / nameplate compute (GW) from
        # the filings' Key Business Metrics tables (S-1, 10-Q, Q3'26
        # release segment tables).
        data = normalize()
        got = {q["period"]: (q["starlink_subs_m"], q["starlink_arpu"],
                              q["compute_gw"]) for q in data["quarters"]}
        self.assertEqual(got, {
            "Q1'25": (5.0, 86, 0.3), "Q2'25": (6.0, 85, 0.4),
            "Q3'25": (7.2, 83, 0.6), "Q1'26": (10.3, 66, 1.0),
            "Q2'26": (12.0, 66, 1.4), "Q3'26": (13.6, 69, 1.7),
        })
        q3 = next(q for q in data["quarters"] if q["period"] == "Q3'26")
        # (13.6 - 7.2) / 7.2 * 100 = 88.9%; (1.7 - 0.6) / 0.6 = 183.3%
        self.assertAlmostEqual(q3["yoy"]["subs_pct"], 88.9, places=1)
        self.assertAlmostEqual(q3["yoy"]["compute_pct"], 183.3, places=1)
        fy25 = next(a for a in data["annuals"] if a["period"] == "2025")
        self.assertEqual((fy25["starlink_subs_m"], fy25["starlink_arpu"],
                          fy25["compute_gw"]), (8.9, 81, 0.8))

    def test_launch_gaps_filled(self):
        # Q2'25 / Q2'26 launches + mass were None until the 10-Q KPI
        # tables and the Q3'26 release comparatives pinned them.
        data = normalize()
        q = {x["period"]: x for x in data["quarters"]}
        self.assertEqual((q["Q2'25"]["launches"],
                          q["Q2'25"]["mass_to_orbit_t"]), (46, 652))
        self.assertEqual((q["Q2'26"]["launches"],
                          q["Q2'26"]["mass_to_orbit_t"]), (38, 485))

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
