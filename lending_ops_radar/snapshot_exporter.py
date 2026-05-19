"""Export a lightweight dashboard snapshot for Streamlit Cloud display."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lending_ops_radar.brief_generator import load_market_questions, load_recent_notes, load_reviewed_signals
from lending_ops_radar.competitor_matrix import build_product_matrix
from lending_ops_radar.intelligence import (
    assessment_table_rows,
    build_assessments,
    coverage_gaps,
    operating_lane_rows,
    top_interpretive_findings,
)
from lending_ops_radar.pipeline import DEFAULT_DB
from lending_ops_radar.quality import build_quality_rows, summary_counts
from lending_ops_radar.reading_brief import build_reading_brief
from lending_ops_radar.trends import market_voice_rows, source_trend_rows, trend_rows, weekly_action_rows
from lending_ops_radar.version import APP_VERSION, APP_VERSION_LABEL


DEFAULT_OUTPUT = ROOT / "data" / "snapshots" / "lending_ops_dashboard_snapshot.json"


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def scalar(conn: sqlite3.Connection, query: str) -> int:
    return int(conn.execute(query).fetchone()[0])


def looks_question_garbled(value: object) -> bool:
    text = "" if value is None else str(value)
    if not text:
        return False
    question_count = text.count("?")
    return "????" in text or (question_count >= 6 and question_count / max(len(text), 1) > 0.18)


def clean_text(value: str) -> str:
    if looks_question_garbled(value):
        return "历史备注存在编码损坏，需回源复核。"
    return value.strip()


def json_ready(value: Any) -> Any:
    if isinstance(value, sqlite3.Row):
        return {key: json_ready(value[key]) for key in value.keys()}
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items() if not str(key).startswith("sort_")}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, str):
        return clean_text(value)
    return value


def source_health_rows(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            """
            SELECT
                q.source_id,
                COALESCE(s.name, q.source_id) AS source_name,
                COALESCE(s.enabled, 0) AS enabled,
                q.run_count,
                q.success_count,
                q.fail_count,
                q.last_status,
                q.last_signal_count,
                q.total_signal_count,
                q.last_error,
                q.updated_at
            FROM source_quality q
            LEFT JOIN sources s ON s.source_id = q.source_id
            ORDER BY q.updated_at DESC
            LIMIT 30
            """
        )
    ]


def build_snapshot(conn: sqlite3.Connection) -> dict[str, Any]:
    reviewed = load_reviewed_signals(conn)
    assessments = build_assessments(reviewed)
    quality_rows = build_quality_rows(reviewed)
    quality_counts = summary_counts(quality_rows)
    matrix_rows = build_product_matrix(conn)
    source_rows = source_health_rows(conn)
    trend_items = trend_rows(conn)
    voice_items = market_voice_rows(conn, limit=40)
    action_items = weekly_action_rows(conn, limit=8)
    source_trends = source_trend_rows(conn)
    snapshot = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "app_version": APP_VERSION,
        "app_version_label": APP_VERSION_LABEL,
        "counts": {
            "signals": scalar(conn, "SELECT COUNT(*) FROM signals"),
            "reviewed": scalar(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'reviewed'"),
            "new": scalar(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'new'"),
            "rejected": scalar(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'rejected'"),
            "research_notes": scalar(conn, "SELECT COUNT(*) FROM research_notes"),
            "market_questions": scalar(conn, "SELECT COUNT(*) FROM market_questions"),
            "source_runs": scalar(conn, "SELECT COUNT(*) FROM source_runs"),
            "competitor_matrix_rows": len(matrix_rows),
        },
        "quality_summary": {
            "tier_counts": dict(quality_counts["tier"]),
            "average_brief_candidate_score": round(
                sum(int(row["brief_candidate_score"]) for row in quality_rows) / len(quality_rows)
            )
            if quality_rows
            else 0,
        },
        "top_quality_rows": quality_rows[:10],
        "operating_lanes": operating_lane_rows(assessments),
        "interpretive_findings": top_interpretive_findings(assessments),
        "impact_matrix_top": assessment_table_rows(assessments, limit=12),
        "coverage_gaps": coverage_gaps(assessments),
        "market_voice": voice_items,
        "trend_rows": trend_items,
        "weekly_actions": action_items,
        "source_health": source_rows,
        "source_trends": source_trends,
        "competitor_matrix_top": matrix_rows[:20],
        "research_notes": [dict(row) for row in load_recent_notes(conn)],
        "market_questions": [dict(row) for row in load_market_questions(conn)],
        "guardrails": {
            "cn": "仅使用公开来源；不使用私人、雇主、借款人、登录页、私域群组或专有数据；输出是个人研究判断，不是法律/合规结论。",
            "en": "Use public sources only; no private, employer, borrower, logged-in, private-group, or proprietary data; outputs are personal research judgments, not legal/compliance conclusions.",
        },
    }
    snapshot["reading_brief_zh"] = build_reading_brief(snapshot, language="zh")
    snapshot["reading_brief_en"] = build_reading_brief(snapshot, language="en")
    return snapshot


def write_snapshot(snapshot: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(json_ready(snapshot), ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a dashboard snapshot JSON from the lending ops SQLite database")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")
    conn = connect(args.db)
    output_path = write_snapshot(build_snapshot(conn), args.output)
    print(f"Wrote dashboard snapshot to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
