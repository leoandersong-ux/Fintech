"""Generate a Markdown snapshot from public competitor-watch signals."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lending_ops_radar.competitor_watch import lens_counts, triage_rows
from lending_ops_radar.pipeline import DEFAULT_DB

DEFAULT_OUTPUT_DIR = ROOT / "data" / "briefs"


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def today_label() -> str:
    return datetime.now(UTC).date().isoformat()


def escape_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def load_competitor_signals(conn: sqlite3.Connection, status: str) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT
                s.id,
                s.source_id,
                s.source_name,
                s.source_type,
                s.source_url,
                s.item_title,
                s.item_url,
                s.classification,
                s.risk_level,
                s.raw_text,
                r.review_status,
                r.priority,
                r.reviewer_notes,
                r.recommended_action,
                s.last_seen_at
            FROM signals s
            JOIN reviews r ON r.signal_id = s.id
            WHERE s.source_id LIKE 'competitor_%'
              AND (? = 'all' OR r.review_status = ?)
            ORDER BY r.priority ASC, s.last_seen_at DESC, s.id DESC
            """,
            (status, status),
        )
    )


def source_table(rows: Iterable[sqlite3.Row]) -> str:
    counts = Counter(row["source_name"] for row in rows)
    if not counts:
        return "_暂无竞品信号 | No competitor signals yet._"
    lines = [
        "| 竞品来源 Competitor Source | 信号数 Signals |",
        "| --- | ---: |",
    ]
    for source_name, count in counts.most_common():
        lines.append(f"| {escape_cell(source_name)} | {count} |")
    return "\n".join(lines)


def lens_table(items: Iterable[dict[str, str | int]]) -> str:
    counts = lens_counts(items)
    if not counts:
        return "_暂无预分诊结果 | No triage output yet._"
    labels = {
        "pricing_terms": "产品定价、额度与期限 / Pricing, Limits, and Tenor",
        "customer_segment": "客群与产品分层 / Customer Segmentation",
        "payment_rails": "支付轨道、放款与还款 / Payment Rails",
        "speed_claims": "审批速度与体验承诺 / Speed Promise",
        "privacy_data": "隐私、数据与账户控制 / Privacy and Data",
        "support_channel": "客服与争议入口 / Support Channel",
        "market_move": "市场动作与合作 / Market Move",
        "general_competitor": "一般竞品背景 / General Context",
    }
    lines = [
        "| 阅读角度 Review Lens | 信号数 Signals |",
        "| --- | ---: |",
    ]
    for key, count in counts.most_common():
        lines.append(f"| {escape_cell(labels.get(key, key))} | {count} |")
    return "\n".join(lines)


def top_items_table(items: list[dict[str, str | int]], limit: int) -> str:
    if not items:
        return "_暂无重点信号 | No priority items yet._"
    lines = [
        "| P | 角度 Lens | 信号 Signal | 建议动作 Recommended Action | 来源 Source |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for item in items[:limit]:
        source = f"[source]({item['source_link']})" if item["source_link"] else ""
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["priority"]),
                    escape_cell(f"{item['lens_cn']} / {item['lens_en']}"),
                    escape_cell(item["signal"]),
                    escape_cell(item["action_cn"]),
                    source,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def source_signal_table(items: list[dict[str, str | int]], limit_per_source: int = 8) -> str:
    grouped: dict[str, list[dict[str, str | int]]] = defaultdict(list)
    for item in items:
        grouped[str(item["source_name"])].append(item)
    if not grouped:
        return "_暂无竞品信号 | No competitor signals yet._"

    sections: list[str] = []
    for source_name in sorted(grouped):
        rows = grouped[source_name][:limit_per_source]
        lines = [
            f"### {source_name}",
            "",
            "| P | 角度 Lens | 信号 Signal | 来源 Source |",
            "| ---: | --- | --- | --- |",
        ]
        for item in rows:
            source = f"[source]({item['source_link']})" if item["source_link"] else ""
            lines.append(
                f"| {item['priority']} | {escape_cell(item['lens_cn'])} | {escape_cell(item['signal'])} | {source} |"
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def render_snapshot(rows: list[sqlite3.Row], status: str, limit: int) -> str:
    items = triage_rows(rows)
    p1_count = sum(1 for item in items if int(item["priority"]) == 1)
    p2_count = sum(1 for item in items if int(item["priority"]) == 2)
    p3_count = sum(1 for item in items if int(item["priority"]) == 3)
    return f"""# 竞品观察快照 | Competitor Watch Snapshot - {today_label()}

中文：这是一份个人公开来源竞品观察快照。它是预分诊材料，不是事实核验完成的市场报告，也不是法律/合规结论。

English: This is a personal public-source competitor-watch snapshot. It is pre-triage material, not a fully verified market report or legal/compliance conclusion.

## 1. 摘要 | Summary

- 范围 | Scope: `{status}` competitor signals.
- 信号数 | Signals: {len(rows)}
- P1 优先 | Priority 1: {p1_count}
- P2 优先 | Priority 2: {p2_count}
- P3 快扫 | Priority 3: {p3_count}

## 2. 来源覆盖 | Source Coverage

{source_table(rows)}

## 3. 阅读角度 | Review Lens

{lens_table(items)}

## 4. 优先阅读 Top Items | Priority Items

{top_items_table(items, limit)}

## 5. 按竞品查看 | By Competitor Source

{source_signal_table(items)}

## 6. 人工复核原则 | Manual Review Guardrails

- 只把公开网页文字作为市场信号，不当作事实核验完成的结论。
- 对费用、额度、期限、速度承诺要回到来源页面人工确认上下文。
- Google Play listing 和公开评论层仍需单独确认后再启用。
- 不记录私人借款人数据、非公开投诉、登录后内容或雇主/内部数据。
- Reviewed/briefed 之后才进入正式 weekly intelligence。
"""


def write_snapshot(content: str, output_dir: Path, status: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"zambia_digital_lending_competitor_watch_{status}_{today_label()}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a competitor-watch Markdown snapshot")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--status", default="new", choices=["all", "new", "reviewed", "briefed", "rejected"])
    parser.add_argument("--limit", type=int, default=25)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")
    conn = connect(args.db)
    rows = load_competitor_signals(conn, args.status)
    content = render_snapshot(rows, args.status, args.limit)
    output_path = write_snapshot(content, args.output_dir, args.status)
    print(f"Wrote {len(rows)} competitor signal(s) to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
