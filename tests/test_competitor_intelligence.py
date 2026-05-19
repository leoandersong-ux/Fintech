import unittest

from lending_ops_radar.competitor_intelligence import (
    build_competitor_event_rows,
    build_competitor_overview_rows,
    build_competitor_universe,
    build_policy_impact_rows,
    build_watch_panel_rows,
)


class CompetitorIntelligenceTests(unittest.TestCase):
    def test_competitor_universe_has_expanded_layers(self) -> None:
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

    def test_overview_matrix_includes_all_candidates_and_evidence_status(self) -> None:
        product_rows = [
            {"institution": "FLoan", "product_or_signal": "Microloan app"},
            {"institution": "Lupiya", "product_or_signal": "Instant Loan"},
        ]
        rows = build_competitor_overview_rows(product_rows)
        by_name = {row["institution"]: row for row in rows}

        self.assertEqual(len(rows), len(build_competitor_universe()))
        self.assertEqual(by_name["FLoan"]["product_matrix_rows"], 1)
        self.assertEqual(by_name["SuperKwacha"]["product_matrix_rows"], 0)
        self.assertEqual(by_name["FLoan"]["evidence_level_key"], "reviewed_product_matrix")
        self.assertIn("候选", by_name["SuperKwacha"]["matrix_status_cn"])

    def test_watch_panel_rows_are_concise_per_institution(self) -> None:
        rows = build_watch_panel_rows()
        names = {row["institution"] for row in rows}

        self.assertIn("SuperKwacha", names)
        self.assertIn("Airtel Money Zambia", names)
        self.assertTrue(all(row["watch_summary_cn"] for row in rows))
        self.assertTrue(all(len(str(row["watch_summary_cn"])) < 90 for row in rows))


if __name__ == "__main__":
    unittest.main()
