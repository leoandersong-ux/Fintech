"""Signal quality scoring for the lending ops research platform."""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lending_ops_radar.pipeline import DEFAULT_DB


DEFAULT_OUTPUT_DIR = ROOT / "data"
DEFAULT_BRIEF_DIR = ROOT / "data" / "briefs"

OFFICIAL_PREFIXES = ("boz_", "zicta_", "ccpc_", "data_protection_")
COMPETITOR_PREFIXES = ("competitor_",)

CLASSIFICATION_RELEVANCE = {
    "complaint": 88,
    "fees": 86,
    "disbursement": 90,
    "repayment": 88,
    "collections": 84,
    "privacy": 86,
    "fraud": 82,
    "regulatory": 82,
    "competitor_change": 84,
    "news_signal": 60,
}

HIGH_VALUE_TERMS = (
    "loan",
    "repayment",
    "fee",
    "fees",
    "charge",
    "charges",
    "interest",
    "mobile money",
    "wallet",
    "disbursement",
    "complaint",
    "privacy",
    "data protection",
    "fraud",
    "collections",
    "customer",
    "borrower",
    "approval",
    "account",
    "airtel",
    "bank",
)

PAYMENT_TERMS = (
    "mobile money",
    "wallet",
    "payment",
    "settlement",
    "zipss",
    "montran",
    "national financial switch",
    "bank",
)


def today_label() -> str:
    return datetime.now(UTC).date().isoformat()


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def row_value(row: Any, key: str, default: str = "") -> str:
    try:
        value = row[key]
    except (KeyError, IndexError, TypeError):
        if isinstance(row, dict):
            value = row.get(key, default)
        else:
            value = getattr(row, key, default)
    return default if value is None else str(value)


def combined_text(row: Any) -> str:
    return " ".join(
        [
            row_value(row, "source_id"),
            row_value(row, "source_name"),
            row_value(row, "item_title"),
            row_value(row, "raw_text"),
            row_value(row, "reviewer_notes"),
            row_value(row, "recommended_action"),
        ]
    ).lower()


def clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def looks_question_garbled(value: object) -> bool:
    text = "" if value is None else str(value)
    if not text:
        return False
    question_count = text.count("?")
    return "????" in text or (question_count >= 6 and question_count / max(len(text), 1) > 0.18)


def source_credibility_score(row: Any) -> int:
    source_id = row_value(row, "source_id").lower()
    source_name = row_value(row, "source_name").lower()
    url = row_value(row, "item_url") or row_value(row, "source_url")
    score = 55
    if source_id.startswith(OFFICIAL_PREFIXES):
        score = 92
    elif source_id.startswith(COMPETITOR_PREFIXES):
        score = 76
    elif "bank of zambia" in source_name or "competition and consumer" in source_name:
        score = 90
    elif "data protection" in source_name or "zicta" in source_name:
        score = 88
    if not url:
        score -= 12
    if "google" in url.lower() or "play.google" in url.lower():
        score -= 8
    return clamp(score)


def lending_relevance_score(row: Any) -> int:
    classification = row_value(row, "classification").lower()
    text = combined_text(row)
    score = CLASSIFICATION_RELEVANCE.get(classification, 50)
    score += min(12, sum(1 for term in HIGH_VALUE_TERMS if term in text) * 2)
    if any(term in text for term in PAYMENT_TERMS):
        score += 5
    if "copyright" in text and len(text) < 220:
        score -= 18
    return clamp(score)


def manual_review_need_score(row: Any) -> int:
    review_status = row_value(row, "review_status")
    risk_level = row_value(row, "risk_level")
    priority = row_value(row, "priority", "3")
    notes = row_value(row, "reviewer_notes")
    action = row_value(row, "recommended_action")
    classification = row_value(row, "classification")
    text = combined_text(row)

    score = 35
    if review_status == "new":
        score += 32
    if risk_level == "high":
        score += 20
    elif risk_level == "medium":
        score += 10
    if priority == "1":
        score += 18
    elif priority == "2":
        score += 9
    if not action or looks_question_garbled(action):
        score += 14
    if not notes or looks_question_garbled(notes):
        score += 8
    if classification in {"fees", "privacy", "complaint", "disbursement", "repayment", "regulatory"}:
        score += 7
    if any(term in text for term in ("coming soon", "instant", "30 seconds", "24hrs", "low interest", "clearly disclosed")):
        score += 6
    return clamp(score)


def brief_candidate_score(row: Any) -> int:
    source = source_credibility_score(row)
    relevance = lending_relevance_score(row)
    need = manual_review_need_score(row)
    risk_bonus = 8 if row_value(row, "risk_level") == "high" else 3 if row_value(row, "risk_level") == "medium" else 0
    review_status = row_value(row, "review_status")
    score = (source * 0.28) + (relevance * 0.45) + (need * 0.22) + risk_bonus
    if review_status == "rejected":
        score -= 35
    return clamp(score)


def quality_tier(score: int) -> tuple[str, str]:
    if score >= 82:
        return "优先阅读", "Priority read"
    if score >= 70:
        return "周报候选", "Brief candidate"
    if score >= 55:
        return "常规监控", "Regular monitoring"
    return "背景/低优先级", "Background / lower priority"


def recommended_use(row: Any, score: int) -> tuple[str, str]:
    need = manual_review_need_score(row)
    if score >= 82:
        return "放入首页 Top 5，并回源复核", "Put in Top 5 and source-review"
    if score >= 70:
        return "纳入周报候选，补一句业务解读", "Use as brief candidate with one business interpretation"
    if need >= 72:
        return "先人工补证，再决定是否入周报", "Verify manually before briefing"
    if score >= 55:
        return "保留常规监控", "Keep in regular monitoring"
    return "仅作背景，不优先阅读", "Background only"


def quality_reasons(row: Any) -> tuple[str, str]:
    reasons_cn: list[str] = []
    reasons_en: list[str] = []
    source = source_credibility_score(row)
    relevance = lending_relevance_score(row)
    need = manual_review_need_score(row)
    if source >= 88:
        reasons_cn.append("官方/高可信公开来源")
        reasons_en.append("official or high-trust public source")
    elif source >= 72:
        reasons_cn.append("公开竞品/市场来源")
        reasons_en.append("public competitor or market source")
    if relevance >= 82:
        reasons_cn.append("直接影响小微贷款运营流程")
        reasons_en.append("directly affects micro-lending operations")
    if need >= 72:
        reasons_cn.append("需要优先人工回源")
        reasons_en.append("needs priority source review")
    if row_value(row, "risk_level") == "high":
        reasons_cn.append("高风险标签")
        reasons_en.append("high-risk label")
    if not reasons_cn:
        reasons_cn.append("当前更适合作为背景监控")
        reasons_en.append("better suited to background monitoring for now")
    return "；".join(reasons_cn), "; ".join(reasons_en)


def assess_signal_quality(row: Any) -> dict[str, object]:
    source_score = source_credibility_score(row)
    relevance_score = lending_relevance_score(row)
    review_need = manual_review_need_score(row)
    candidate_score = brief_candidate_score(row)
    tier_cn, tier_en = quality_tier(candidate_score)
    use_cn, use_en = recommended_use(row, candidate_score)
    why_cn, why_en = quality_reasons(row)
    return {
        "signal_id": row_value(row, "id") or row_value(row, "signal_id"),
        "source_id": row_value(row, "source_id"),
        "source_name": row_value(row, "source_name"),
        "signal": row_value(row, "item_title") or row_value(row, "signal"),
        "classification": row_value(row, "classification"),
        "risk_level": row_value(row, "risk_level"),
        "review_status": row_value(row, "review_status"),
        "priority": row_value(row, "priority"),
        "source_link": row_value(row, "item_url") or row_value(row, "source_url") or row_value(row, "source_link"),
        "source_credibility_score": source_score,
        "lending_relevance_score": relevance_score,
        "manual_review_need_score": review_need,
        "brief_candidate_score": candidate_score,
        "quality_tier_cn": tier_cn,
        "quality_tier_en": tier_en,
        "recommended_use_cn": use_cn,
        "recommended_use_en": use_en,
        "quality_reason_cn": why_cn,
        "quality_reason_en": why_en,
    }


def build_quality_rows(rows: Iterable[Any]) -> list[dict[str, object]]:
    quality_rows = [assess_signal_quality(row) for row in rows]
    return sorted(
        quality_rows,
        key=lambda row: (
            -int(row["brief_candidate_score"]),
            -int(row["manual_review_need_score"]),
            str(row["signal_id"]),
        ),
    )


def load_signal_rows(conn: sqlite3.Connection, statuses: tuple[str, ...] = ("reviewed", "briefed")) -> list[sqlite3.Row]:
    placeholders = ", ".join("?" for _ in statuses)
    return list(
        conn.execute(
            f"""
            SELECT
                s.id,
                s.source_id,
                s.source_name,
                s.source_url,
                s.item_title,
                s.item_url,
                s.classification,
                s.risk_level,
                s.raw_text,
                s.last_seen_at,
                r.priority,
                r.reviewer_notes,
                r.recommended_action,
                r.review_status
            FROM signals s
            JOIN reviews r ON r.signal_id = s.id
            WHERE r.review_status IN ({placeholders})
            ORDER BY s.last_seen_at DESC
            """,
            statuses,
        )
    )


def summary_counts(quality_rows: Iterable[dict[str, object]]) -> dict[str, Counter[str]]:
    rows = list(quality_rows)
    return {
        "tier": Counter(str(row["quality_tier_cn"]) for row in rows),
        "classification": Counter(str(row["classification"]) for row in rows),
        "use": Counter(str(row["recommended_use_cn"]) for row in rows),
    }


def escape_cell(value: object) -> str:
    return ("" if value is None else str(value)).replace("|", "\\|").replace("\n", " ").strip()


def quality_markdown_table(rows: list[dict[str, object]], limit: int = 10) -> str:
    selected = rows[:limit]
    if not selected:
        return "_暂无质量评分 | No quality scores yet._"
    lines = [
        "| 信号 Signal | 质量层级 Tier | 候选分 Score | 来源分 Source | 相关度 Relevance | 回源需求 Review Need | 建议用途 Recommended Use | 来源 Source |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in selected:
        source = f"[source]({row['source_link']})" if row.get("source_link") else ""
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["signal"]),
                    escape_cell(f"{row['quality_tier_cn']} / {row['quality_tier_en']}"),
                    escape_cell(row["brief_candidate_score"]),
                    escape_cell(row["source_credibility_score"]),
                    escape_cell(row["lending_relevance_score"]),
                    escape_cell(row["manual_review_need_score"]),
                    escape_cell(row["recommended_use_cn"]),
                    source,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_quality_snapshot(rows: list[dict[str, object]]) -> str:
    counts = summary_counts(rows)
    avg_score = round(sum(int(row["brief_candidate_score"]) for row in rows) / len(rows)) if rows else 0
    tier_lines = "\n".join(f"- {tier}: {count}" for tier, count in counts["tier"].most_common())
    class_lines = "\n".join(f"- {classification}: {count}" for classification, count in counts["classification"].most_common())
    return f"""# 信号质量快照 | Signal Quality Snapshot - {today_label()}

中文：这是 reviewed/briefed 公开来源信号的研究质量评分，不是产品质量、法律判断或监管结论。

English: This scores reviewed/briefed public-source signals for research usefulness. It is not product quality, legal judgment, or a regulatory conclusion.

## 摘要 | Summary

- 信号数 | Signals: {len(rows)}
- 平均候选分 | Average candidate score: {avg_score}/100

## 层级分布 | Tier Distribution

{tier_lines or "_No tier data._"}

## 分类分布 | Classification Distribution

{class_lines or "_No classification data._"}

## 本周最值得看 | Priority Reads

{quality_markdown_table(rows, limit=10)}
"""


def write_csv(rows: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["signal_id"])
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate signal quality snapshot")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--brief-dir", type=Path, default=DEFAULT_BRIEF_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")
    conn = connect(args.db)
    rows = build_quality_rows(load_signal_rows(conn))
    csv_path = write_csv(rows, args.output_dir / "lending_ops_signal_quality.csv")
    md_path = args.brief_dir / f"zambia_digital_lending_signal_quality_{today_label()}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_quality_snapshot(rows), encoding="utf-8")
    print(f"Wrote {len(rows)} quality row(s) to {csv_path}")
    print(f"Wrote quality snapshot to {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
