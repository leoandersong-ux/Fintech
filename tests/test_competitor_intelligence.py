import unittest

from lending_ops_radar.competitor_intelligence import (
    build_competitor_event_rows,
    build_competitor_universe,
    build_policy_impact_rows,
)


class CompetitorIntelligenceTests(unittest.TestCase):
    def test_competitor_universe_has_expanded_layers_without_excluded_names(self) -> None:
        rows = build_competitor_universe()
        names = {row["institution"] for row in rows}
        tiers = {row["tier_key"] for row in rows}

        self.assertGreaterEqual(len(rows), 12)
        self.assertIn("SuperKwacha", names)
        self.assertIn("Finedge / ka Something", names)
        self.assertIn("Phindu Credit", names)
        self.assertIn("Micro Finance Zambia", names)
        self.assertIn("SmartFin", names)
        self.assertIn("core_digital_lending", tiers)
        self.assertIn("adjacent_microfinance_payroll", tiers)
        self.assertNotIn("Zamcash", names)
        self.assertNotIn("Biu Capital", names)

    def test_policy_impact_rows_map_regulation_to_competitor_fields(self) -> None:
        rows = build_policy_impact_rows()
        fees_row = next(row for row in rows if row["policy_key"] == "fees_disclosure")
        privacy_row = next(row for row in rows if row["policy_key"] == "data_privacy_permissions")

        self.assertIn("pricing_or_disclosure", fees_row["watch_fields"])
        self.assertIn("privacy_policy", privacy_row["watch_fields"])
        self.assertGreaterEqual(fees_row["affected_competitor_count"], 4)
        self.assertIn("SuperKwacha", fees_row["examples"])

    def test_competitor_event_rows_cover_company_product_policy_and_voice(self) -> None:
        rows = build_competitor_event_rows()
        event_types = {row["event_type_key"] for row in rows}

        self.assertIn("company", event_types)
        self.assertIn("product", event_types)
        self.assertIn("policy_pressure", event_types)
        self.assertIn("market_voice", event_types)
        self.assertTrue(all(row["source_link"] for row in rows[:8]))


if __name__ == "__main__":
    unittest.main()
