import unittest

from scrapers.meta.normalize import FACTS, normalize
from scrapers.meta.parse import release_periods
from scrapers.meta.quarters import RELEASES


class TestMetaNormalize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = normalize()
        cls.quarters = {q["period"]: q for q in cls.data["quarters"]}
        cls.annuals = {a["period"]: a for a in cls.data["annuals"]}

    def test_quarters_present(self):
        self.assertEqual(
            [q["period"] for q in self.data["quarters"]],
            ["Q1'25", "Q2'25", "Q3'25", "Q4'25",
             "Q1'26", "Q2'26", "Q3'26"])
        self.assertEqual(self.data["latest"], "Q3'26")

    def test_latest_quarter_values(self):
        q = self.quarters["Q3'26"]
        self.assertEqual(q["revenue"], 64601)
        self.assertEqual(q["operating_income"], 12988)
        self.assertEqual(q["net_income"], 9860)
        self.assertEqual(q["eps_diluted"], 3.83)
        self.assertEqual(q["segments"]["foa"], 64158)
        self.assertEqual(q["segments"]["reality_labs"], 443)
        self.assertEqual(q["foa_op"], 17117)
        self.assertEqual(q["rl_op"], -4129)
        self.assertEqual(q["dap_b"], 3.64)
        self.assertEqual(q["capex"], 34906)
        self.assertEqual(q["fcf"], -2120)
        self.assertEqual(q["yoy"]["revenue"], 26.1)

    def test_releases_agree_with_curated_facts(self):
        cache = {r["period"]: r["cache"] for r in RELEASES if "cache" in r}
        keys = {"revenue": "revenue", "operating_income": "operating_income",
                "net_income": "net_income", "eps_diluted": "eps_diluted",
                "eps_basic": "eps_basic", "dap_b": "dap_b",
                "capex": "capex", "fcf": "fcf", "headcount": "headcount"}
        for period, values in FACTS.items():
            parsed = release_periods(cache[period])
            row = dict(zip(
                ("revenue", "operating_income", "net_income", "eps_basic",
                 "eps_diluted", "segments", "products", "foa_op", "rl_op",
                 "dap_b", "capex", "fcf", "headcount", "cash_sec_b",
                 "impressions_pct", "price_pct"), values))
            for pkey, fkey in keys.items():
                self.assertEqual(parsed[pkey], row[fkey],
                                 f"{period} {pkey}")
            self.assertEqual(parsed["foa"], row["segments"]["foa"])
            self.assertEqual(parsed["reality_labs"],
                             row["segments"]["reality_labs"])
            self.assertEqual(parsed["advertising"],
                             row["products"]["advertising"])
            self.assertEqual(parsed["other"], row["products"]["other"])
            self.assertEqual(parsed["foa_op"], row["foa_op"])
            self.assertEqual(parsed["rl_op"], row["rl_op"])

    def test_segment_ties(self):
        for row in self.data["quarters"] + self.data["annuals"]:
            self.assertEqual(
                row["segments"]["foa"] + row["segments"]["reality_labs"],
                row["revenue"], row["period"])
            self.assertEqual(row["foa_op"] + row["rl_op"],
                             row["operating_income"], row["period"])
            self.assertEqual(
                row["products"]["advertising"] + row["products"]["other"],
                row["segments"]["foa"], row["period"])

    def test_fy2025_quarters_sum_to_annual(self):
        total_rev = sum(self.quarters[p]["revenue"]
                        for p in ("Q1'25", "Q2'25", "Q3'25", "Q4'25"))
        # Meta's own release carries a $1M presentation difference
        # between the summed quarters (200,965) and the stated
        # twelve-month column (200,966); the annual row keeps the
        # stated figure.
        self.assertLessEqual(
            abs(total_rev - self.annuals["2025"]["revenue"]), 1)
        total_capex = sum(self.quarters[p]["capex"]
                          for p in ("Q1'25", "Q2'25", "Q3'25", "Q4'25"))
        self.assertEqual(total_capex, self.annuals["2025"]["capex"])

    def test_annuals_present(self):
        self.assertEqual(sorted(self.annuals), ["2023", "2024", "2025"])
        self.assertEqual(self.annuals["2025"]["revenue"], 200966)
        self.assertEqual(self.annuals["2025"]["rl_op"], -19193)
        self.assertEqual(self.annuals["2023"]["eps_diluted"], 14.87)


if __name__ == "__main__":
    unittest.main()
