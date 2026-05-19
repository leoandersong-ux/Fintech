import unittest

from lending_ops_radar.reading_brief import build_reading_brief, clean_display_text


class ReadingBriefTests(unittest.TestCase):
    def test_clean_display_text_replaces_question_mark_garble(self) -> None:
        self.assertEqual(
            clean_display_text("??????????"),
            "历史备注存在编码损坏，需回源复核。",
        )

    def test_build_reading_brief_prioritizes_readable_topline(self) -> None:
        snapshot = {
            "counts": {"signals": 12, "reviewed": 5, "new": 1, "market_questions": 2},
            "top_quality_rows": [
                {
                    "signal_id": "10",
                    "signal": "Public complaint channel flags failed mobile money transactions",
                    "classification": "complaint",
                    "risk_level": "high",
                    "recommended_use_cn": "放入首页 Top 5，并回源复核",
                    "recommended_use_en": "Put in Top 5 and source-review",
                    "quality_reason_cn": "直接影响小微贷款运营流程",
                    "quality_reason_en": "directly affects micro-lending operations",
                    "source_link": "https://example.test",
                }
            ],
            "operating_lanes": [
                {
                    "lane_cn": "支付/放款摩擦",
                    "lane_en": "Payment and disbursement friction",
                    "evidence_count": 3,
                    "high_impact_count": 2,
                    "next_action_cn": "回源检查失败交易投诉入口",
                    "next_action_en": "Source-check failed transaction complaint channels",
                }
            ],
            "weekly_actions": [
                {
                    "action_area_cn": "客服与投诉",
                    "action_area_en": "Support and complaints",
                    "priority_cn": "本周优先",
                    "priority_en": "This-week priority",
                    "recommended_action_cn": "整理投诉场景清单",
                    "recommended_action_en": "Build a complaint scenario list",
                    "evidence_count": 4,
                }
            ],
            "coverage_gaps": [
                {
                    "area_cn": "公开 App 评论",
                    "area_en": "Public app reviews",
                    "gap_cn": "尚未安全启用",
                    "gap_en": "Not safely enabled yet",
                }
            ],
        }

        brief = build_reading_brief(snapshot, language="zh")

        self.assertEqual(brief["counts"]["signals"], 12)
        self.assertEqual(brief["topline"][0]["title"], "Public complaint channel flags failed mobile money transactions")
        self.assertIn("小微贷款", brief["topline"][0]["why"])
        self.assertEqual(brief["lanes"][0]["name"], "支付/放款摩擦")
        self.assertEqual(brief["actions"][0]["name"], "客服与投诉")
        self.assertEqual(brief["gaps"][0]["name"], "公开 App 评论")


if __name__ == "__main__":
    unittest.main()
