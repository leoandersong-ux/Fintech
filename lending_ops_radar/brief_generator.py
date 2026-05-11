"""Generate weekly personal research notes from reviewed lending-ops signals."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lending_ops_radar.intelligence import (
    assessment_table_rows,
    build_assessments,
    coverage_gaps,
    operating_lane_rows,
    top_interpretive_findings,
)
from lending_ops_radar.quality import build_quality_rows, quality_markdown_table, summary_counts
from lending_ops_radar.version import APP_VERSION_LABEL

DEFAULT_DB = ROOT / "data" / "lending_ops_radar.sqlite3"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "briefs"

SECTION_BY_CLASSIFICATION = {
    "regulatory": "Regulatory Watch",
    "competitor_change": "Competitor Changes",
    "complaint": "App Review & Complaint Themes",
    "fees": "App Review & Complaint Themes",
    "disbursement": "App Review & Complaint Themes",
    "repayment": "App Review & Complaint Themes",
    "privacy": "Regulatory Watch",
    "fraud": "Reputation / News Signals",
    "collections": "Collections Communication Insights",
    "news_signal": "Reputation / News Signals",
}

PAYMENT_RAIL_TERMS = (
    "zipss",
    "montran",
    "national financial switch",
    "electronic money",
    "e-money",
    "mobile payments",
    "money transfer",
    "payment service",
    "payment systems",
    "settlement",
    "gateway",
)


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def current_week_label() -> str:
    today = datetime.now(UTC).date()
    iso = today.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def load_reviewed_signals(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
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
                r.priority,
                r.reviewer_notes,
                r.recommended_action,
                r.review_status
            FROM signals s
            JOIN reviews r ON r.signal_id = s.id
            WHERE r.review_status IN ('reviewed', 'briefed')
            ORDER BY r.priority ASC, s.risk_level DESC, s.last_seen_at DESC
            """
        )
    )


def load_recent_notes(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT note_type, title, note, market_question, confidence, created_at
            FROM research_notes
            ORDER BY created_at DESC
            LIMIT 10
            """
        )
    )


def load_market_questions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT area, question, status, current_hypothesis, evidence, updated_at
            FROM market_questions
            ORDER BY status, area, question
            LIMIT 10
            """
        )
    )


def load_source_health(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT
                q.source_id,
                COALESCE(s.name, q.source_id) AS source_name,
                q.run_count,
                q.success_count,
                q.fail_count,
                q.last_status,
                q.last_signal_count,
                q.updated_at
            FROM source_quality q
            LEFT JOIN sources s ON s.source_id = q.source_id
            ORDER BY q.updated_at DESC
            LIMIT 10
            """
        )
    )


def escape_cell(value: object) -> str:
    text = readable_text(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def looks_question_garbled(value: object) -> bool:
    text = "" if value is None else str(value)
    if not text:
        return False
    question_count = text.count("?")
    return "????" in text or (question_count >= 6 and question_count / max(len(text), 1) > 0.18)


def choose_text(cn: str, en: str, language: str = "zh") -> str:
    return en if language == "en" else cn


def split_bilingual_text(value: object, language: str = "zh") -> str:
    text = "" if value is None else str(value)
    if " | " not in text:
        return text
    left, right = text.split(" | ", 1)
    return right.strip() if language == "en" else left.strip()


def field_for(row: dict[str, object] | sqlite3.Row, base: str, language: str = "zh") -> object:
    key = f"{base}_en" if language == "en" else f"{base}_cn"
    try:
        return row[key]
    except Exception:
        return ""


def readable_text(value: object, fallback: str = "历史备注存在编码损坏，需回源复核 | Historical note has encoding loss; review source.", language: str = "zh") -> str:
    text = "" if value is None else str(value)
    if looks_question_garbled(text):
        return split_bilingual_text(fallback, language)
    return split_bilingual_text(text, language).strip()


def row_link(row: sqlite3.Row, language: str = "zh") -> str:
    url = row["item_url"] or row["source_url"]
    return f"[{choose_text('来源', 'source', language)}]({url})"


def fallback_next_action(row: sqlite3.Row) -> str:
    classification = str(row["classification"] or "")
    if classification == "competitor_change":
        return "回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 | Source-review limit, tenor, fees, speed promise, payment/payout path, and support/privacy route; keep as public competitor signal."
    if classification == "privacy":
        return "回源阅读隐私、权限、账户删除和投诉入口；不要把页面措辞直接当作合规结论。 | Source-review privacy, permissions, account deletion, and complaint routes; do not treat page wording as a compliance conclusion."
    if classification == "fees":
        return "回源核对 APR、服务费、逾期费、还款示例和披露位置。 | Source-check APR, service fees, late fees, repayment examples, and disclosure placement."
    if classification == "disbursement":
        return "回源核对放款、还款、失败交易、对账和移动钱/银行轨道依赖。 | Source-check payout, repayment, failed transactions, reconciliation, and mobile-money/bank rail dependency."
    if classification == "repayment":
        return "回源确认还款频率、扣款方式、宽限期、逾期处理和客户解释口径。 | Source-check repayment frequency, deduction method, grace period, late handling, and borrower-facing explanation."
    if classification == "regulatory":
        return "回源确认监管文件日期、适用范围和对产品/支付/客服流程的潜在影响。 | Source-check document date, scope, and possible impact on product, payment, or support processes."
    return "回源复核，并补写一条个人解释笔记。 | Review the source and add one personal interpretation note."


def table_for(rows: Iterable[sqlite3.Row], language: str = "zh") -> str:
    rows = list(rows)
    if not rows:
        return choose_text("_暂无已复核条目。_", "_No reviewed items selected yet._", language)
    lines = [
        choose_text(
            "| 信号 | 分类 | 风险 | 来源 | 下一步 |",
            "| Signal | Classification | Risk | Source | Next Action |",
            language,
        ),
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        action = readable_text(row["recommended_action"], fallback_next_action(row), language) or readable_text(fallback_next_action(row), language=language)
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["item_title"]),
                    escape_cell(row["classification"]),
                    escape_cell(row["risk_level"]),
                    row_link(row, language),
                    escape_cell(action),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def link_for(url: object, language: str = "zh") -> str:
    text = "" if url is None else str(url).strip()
    if not text:
        return ""
    return f"[{choose_text('来源', 'source', language)}]({text})"


def findings_table(rows: Iterable[dict[str, str]], language: str = "zh") -> str:
    rows = list(rows)
    if not rows:
        return choose_text("_暂无关键判断。_", "_No interpretive findings yet._", language)
    lines = [
        choose_text("| 关键判断 | 为什么重要 |", "| Key Finding | Why It Matters |", language),
        "| --- | --- |",
    ]
    for row in rows:
        finding = choose_text(row["finding_cn"], row["finding_en"], language)
        why = choose_text(row["why_cn"], row["why_en"], language)
        lines.append(f"| {escape_cell(finding)} | {escape_cell(why)} |")
    return "\n".join(lines)


def quality_table(rows: list[dict[str, object]], language: str = "zh", limit: int = 5) -> str:
    if not rows:
        return choose_text("_暂无质量评分。_", "_No quality scores yet._", language)
    lines = [
        choose_text(
            "| 信号 | 分类 | 风险 | 候选分 | 建议用途 | 原因 | 来源 |",
            "| Signal | Classification | Risk | Candidate Score | Recommended Use | Reason | Source |",
            language,
        ),
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows[:limit]:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["signal"]),
                    escape_cell(row["classification"]),
                    escape_cell(row["risk_level"]),
                    str(row["brief_candidate_score"]),
                    escape_cell(field_for(row, "recommended_use", language)),
                    escape_cell(field_for(row, "quality_reason", language)),
                    link_for(row["source_link"], language),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def quality_summary_section(rows: list[dict[str, object]], language: str = "zh") -> str:
    if not rows:
        return choose_text("_暂无质量评分。_", "_No quality scores yet._", language)
    counts = summary_counts(rows)
    avg_score = round(sum(int(row["brief_candidate_score"]) for row in rows) / len(rows))
    tier_lines = "\n".join(f"- {tier}: {count}" for tier, count in counts["tier"].most_common()) if language == "zh" else ""
    english_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        english_counts[str(row["quality_tier_en"])] += 1
    english_tiers = "\n".join(f"- {tier}: {count}" for tier, count in english_counts.items())
    tier_block = tier_lines if language == "zh" else english_tiers
    return f"""{choose_text(f"- 平均候选分：{avg_score}/100", f"- Average candidate score: {avg_score}/100", language)}
{choose_text(f"- 优先阅读：{counts['tier'].get('优先阅读', 0)}", f"- Priority reads: {sum(1 for row in rows if row['quality_tier_en'] == 'Priority read')}", language)}
{choose_text(f"- 周报候选：{counts['tier'].get('周报候选', 0)}", f"- Brief candidates: {sum(1 for row in rows if row['quality_tier_en'] == 'Brief candidate')}", language)}

{tier_block}

### 2.1 {choose_text("本周最值得看", "Priority Reads", language)}

{quality_table(rows, language, limit=5)}
"""


def impact_matrix_cards(assessments: list[dict[str, str | int]], limit: int = 10, section_number: int = 4, language: str = "zh") -> str:
    rows = assessment_table_rows(assessments, limit=limit)
    if not rows:
        return choose_text("_暂无已复核信号可解读。_", "_No reviewed signals available for interpretation._", language)
    lines: list[str] = []
    for index, row in enumerate(rows, start=1):
        domain = choose_text(str(row["domain_cn"]), str(row["domain_en"]), language)
        lines.extend(
            [
                f"### {section_number}.{index} {readable_text(domain)}",
                "",
                f"**{choose_text('等级', 'Level', language)}:** {readable_text(row['impact_level'], language=language)}",
                "",
                f"**{choose_text('信号', 'Signal', language)}:** {readable_text(row['signal'], language=language)}",
                "",
                f"**{choose_text('对小微贷款业务的影响', 'Micro-lending impact', language)}:** {choose_text(readable_text(row['lending_impact_cn'], language=language), readable_text(row['lending_impact_en'], language=language), language)}",
                "",
                f"**{choose_text('建议动作', 'Recommended action', language)}:** {choose_text(readable_text(row['recommended_actions_cn'], language=language), readable_text(row['recommended_actions_en'], language=language), language)}",
                "",
                f"**{choose_text('待验证问题', 'Follow-up question', language)}:** {choose_text(readable_text(row['follow_up_questions_cn'], language=language), readable_text(row['follow_up_questions_en'], language=language), language)}",
                "",
                f"**{choose_text('来源', 'Source', language)}:** {link_for(row['source_link'], language)}",
                "",
            ]
        )
    return "\n".join(lines)


def operating_lane_table(rows: Iterable[dict[str, str | int]], language: str = "zh") -> str:
    rows = list(rows)
    if not rows:
        return choose_text("_暂无行动板数据。_", "_No action-board data yet._", language)
    lines = [
        choose_text(
            "| 迭代线 | 证据数 | 高影响 | 优先级 | 业务意义 | 下一步动作 |",
            "| Lane | Evidence | High Impact | Priority | Why It Matters | Next Action |",
            language,
        ),
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(field_for(row, "lane", language)),
                    str(row["evidence_count"]),
                    str(row["high_impact_count"]),
                    escape_cell(field_for(row, "priority", language)),
                    escape_cell(field_for(row, "why", language)),
                    escape_cell(field_for(row, "next_action", language)),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def coverage_gap_table(rows: Iterable[dict[str, str]], language: str = "zh") -> str:
    rows = list(rows)
    if not rows:
        return choose_text("_暂无覆盖缺口判断。_", "_No coverage-gap assessment yet._", language)
    lines = [
        choose_text(
            "| 情报线 | 当前覆盖 | 主要缺口 | 下一步来源 |",
            "| Intelligence Lane | Current Coverage | Main Gap | Next Sources |",
            language,
        ),
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        area = choose_text(row["area_cn"], row["area_en"], language)
        coverage = choose_text(row["coverage_cn"], row["coverage_en"], language)
        gap = choose_text(row["gap_cn"], row["gap_en"], language)
        next_source = choose_text(row["next_source_cn"], row["next_source_en"], language)
        lines.append(
            f"| {escape_cell(area)} | {escape_cell(coverage)} | {escape_cell(gap)} | {escape_cell(next_source)} |"
        )
    return "\n".join(lines)


def notes_table(rows: Iterable[sqlite3.Row], language: str = "zh") -> str:
    rows = list(rows)
    if not rows:
        return choose_text("_暂无个人研究笔记。_", "_No personal research notes yet._", language)
    lines = [
        choose_text("| 笔记 | 类型 | 市场问题 | 信心 |", "| Note | Type | Market Question | Confidence |", language),
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["title"]),
                    escape_cell(row["note_type"]),
                    escape_cell(row["market_question"]),
                    escape_cell(row["confidence"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def questions_table(rows: Iterable[sqlite3.Row], language: str = "zh") -> str:
    rows = list(rows)
    if not rows:
        return choose_text("_暂无市场问题。_", "_No market questions seeded yet._", language)
    lines = [
        choose_text(
            "| 领域 | 问题 | 状态 | 当前假设 | 证据 |",
            "| Area | Question | Status | Current Hypothesis | Evidence |",
            language,
        ),
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["area"]),
                    escape_cell(row["question"]),
                    escape_cell(row["status"]),
                    escape_cell(row["current_hypothesis"]),
                    escape_cell(row["evidence"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def source_health_table(rows: Iterable[sqlite3.Row], language: str = "zh") -> str:
    rows = list(rows)
    if not rows:
        return choose_text("_暂无来源健康记录。_", "_No source health records yet._", language)
    lines = [
        choose_text(
            "| 来源 | 运行 | 成功 | 失败 | 最近状态 | 最近信号 |",
            "| Source | Runs | Success | Fail | Last Status | Last Signals |",
            language,
        ),
        "| --- | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["source_name"]),
                    str(row["run_count"]),
                    str(row["success_count"]),
                    str(row["fail_count"]),
                    escape_cell(row["last_status"]),
                    str(row["last_signal_count"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def grouped_by_section(rows: list[sqlite3.Row]) -> dict[str, list[sqlite3.Row]]:
    grouped: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in rows:
        title = f"{row['source_id']} {row['source_name']} {row['item_title']}".lower()
        if row["source_id"].startswith("boz_") and any(term in title for term in PAYMENT_RAIL_TERMS):
            section = "Payment Rails / Lending Ops"
        else:
            section = SECTION_BY_CLASSIFICATION.get(row["classification"], "Reputation / News Signals")
        grouped[section].append(row)
    return grouped


def render_brief(
    rows: list[sqlite3.Row],
    week_label: str,
    notes: list[sqlite3.Row] | None = None,
    questions: list[sqlite3.Row] | None = None,
    source_health: list[sqlite3.Row] | None = None,
    language: str = "zh",
) -> str:
    grouped = grouped_by_section(rows)
    top_risks = sorted(rows, key=lambda row: (row["priority"], row["risk_level"] != "high"))[:5]
    recommended = [row for row in rows if row["recommended_action"]][:5]
    assessments = build_assessments(rows)
    quality_rows = build_quality_rows(rows)
    high_impact_count = sum(1 for item in assessments if item["impact_level"] == "high")
    medium_impact_count = sum(1 for item in assessments if item["impact_level"] == "medium")
    interpreted_domains = len({str(item["domain_key"]) for item in assessments})
    findings = top_interpretive_findings(assessments)
    gaps = coverage_gaps(assessments)
    lane_rows = operating_lane_rows(assessments)
    notes = notes or []
    questions = questions or []
    source_health = source_health or []
    operating_notes = choose_text(
        "- 观察公开投诉语言如何映射到真实运营域：客服、放款、还款、催收、欺诈、隐私和披露。\n"
        "- 判断重复出现的公开信号到底是来源质量问题、市场共性摩擦，还是一次性噪声。\n"
        "- 始终把来源事实和个人推断分开记录。\n"
        "- 对支付轨道信号，要区分基础设施/合作伙伴依赖与直接面向借款人的产品规则。",
        "- Watch how public complaint language maps to real operating domains: support, disbursement, repayment, collections, fraud, privacy, and disclosure.\n"
        "- Track whether repeated public signals point to source quality, market-wide friction, or one-off noise.\n"
        "- Keep a written distinction between what the source says and what you infer.\n"
        "- For payment rails, separate infrastructure/partner-dependency signals from direct borrower-facing product rules.",
        language,
    )
    capability_checklist = choose_text(
        "- 本周是否至少运行过一个 Scrapling 公开来源抓取？\n"
        "- 是否复核并分类了最有价值的信号？\n"
        "- 是否写了至少一条个人研究笔记？\n"
        "- 是否更新了至少一个市场问题？\n"
        "- 是否检查了 source health，并判断哪些来源适合自动化、哪些需要手动复核？\n"
        "- 是否记录了下周要继续追踪的开放问题？\n"
        "- 是否避免了私人、雇主、借款人或专有数据？",
        "- Did I run at least one Scrapling public-source fetch?\n"
        "- Did I review and classify the strongest signals?\n"
        "- Did I write at least one personal research note?\n"
        "- Did I update at least one market question?\n"
        "- Did I check source health and decide which sources need manual review?\n"
        "- Did I record one open market question for next week?\n"
        "- Did I avoid private, employer, borrower, or proprietary data?",
        language,
    )

    return f"""# {choose_text('数字借贷个人研究笔记', 'Digital Lending Personal Research Notes', language)} - {week_label}

Platform version: {APP_VERSION_LABEL}

{choose_text('这是一份个人公开来源研究笔记，用于市场理解和能力建设。它不是法律意见、监管结论、客户交付物或商业材料。', 'Prepared as a personal public-source research note for market understanding and capability-building. This is not legal advice, regulatory determination, customer delivery, or commercial material.', language)}

## 1. {choose_text('执行摘要', 'Executive Summary', language)}

{choose_text(f'本周笔记包含 {len(rows)} 条已复核公开来源信号和 {len(notes)} 条个人研究笔记；其中 {high_impact_count} 条落在高潜在影响域，{medium_impact_count} 条落在中等潜在影响域，覆盖 {interpreted_domains} 个 lending ops 影响域。这里的“影响”是研究优先级，不是合规结论。', f'This weekly note contains {len(rows)} reviewed public-source signal(s) and {len(notes)} personal research note(s); {high_impact_count} sit in high-potential-impact domains, {medium_impact_count} in medium-potential-impact domains, across {interpreted_domains} lending-ops impact domain(s). "Impact" means research priority, not a compliance conclusion.', language)}

{choose_text('仅作为私人研究资料使用。请持续区分“来源事实”和“个人解释”。', 'Use this only as a private research artifact. Separate source facts from personal interpretation.', language)}

## 2. {choose_text('信息质量与阅读优先级', 'Signal Quality and Reading Priority', language)}

{quality_summary_section(quality_rows, language)}

## 3. {choose_text('五条迭代线行动板', 'Five-Lane Action Board', language)}

{operating_lane_table(lane_rows, language)}

## 4. {choose_text('本周业务判断', 'Business Interpretation', language)}

{findings_table(findings, language)}

## 5. {choose_text('小微贷款业务影响矩阵', 'Micro-lending Impact Matrix', language)}

{impact_matrix_cards(assessments, section_number=5, language=language)}

## 6. {choose_text('情报覆盖缺口', 'Intelligence Coverage Gaps', language)}

{coverage_gap_table(gaps, language)}

## 7. {choose_text('监管观察', 'Regulatory Watch', language)}

{table_for(grouped.get("Regulatory Watch", []), language)}

## 8. {choose_text('支付轨道与借贷运营', 'Payment Rails / Lending Ops', language)}

{table_for(grouped.get("Payment Rails / Lending Ops", []), language)}

## 9. {choose_text('竞品变化', 'Competitor Changes', language)}

{table_for(grouped.get("Competitor Changes", []), language)}

## 10. {choose_text('App 评价与投诉主题', 'App Review and Complaint Themes', language)}

{table_for(grouped.get("App Review & Complaint Themes", []), language)}

## 11. {choose_text('声誉与新闻信号', 'Reputation and News Signals', language)}

{table_for(grouped.get("Reputation / News Signals", []), language)}

## 12. {choose_text('运营模式笔记', 'Operating Pattern Notes', language)}

{operating_notes}

## 13. {choose_text('个人研究笔记', 'Personal Research Notes', language)}

{notes_table(notes, language)}

## 14. {choose_text('市场问题', 'Market Questions', language)}

{questions_table(questions, language)}

## 15. {choose_text('来源健康度', 'Source Health', language)}

{source_health_table(source_health, language)}

## 16. {choose_text('催收与行为观察', 'Collections / Conduct Watch', language)}

{table_for(grouped.get("Collections Communication Insights", []), language)}

## 17. {choose_text('重点风险 Top 5', 'Top 5 Risks To Watch', language)}

{table_for(top_risks, language)}

## 18. {choose_text('下一步学习动作', 'Next Learning Actions', language)}

{table_for(recommended, language)}

## 19. {choose_text('来源', 'Sources', language)}

{choose_text('本笔记中的主要来源均已在上方表格中链接。只应使用公开网页、公开 app listing、官方公告、公开新闻，以及你手动批准的公开 watchlist。', 'Primary sources in this note are source-linked in the tables above. Only public webpages, public app listings, official announcements, public news, and your own manually approved public watchlists should be used.', language)}

## 20. {choose_text('能力建设检查清单', 'Capability-Building Checklist', language)}

{capability_checklist}
"""


def write_brief(content: str, output_dir: Path, week_label: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"zambia_digital_lending_personal_notes_{week_label}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def mark_brief_items(conn: sqlite3.Connection, rows: list[sqlite3.Row], week_label: str) -> None:
    timestamp = datetime.now(UTC).isoformat()
    for row in rows:
        section = SECTION_BY_CLASSIFICATION.get(row["classification"], "Reputation / News Signals")
        conn.execute(
            """
            INSERT INTO brief_items (signal_id, week_label, section, note, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(signal_id, week_label) DO UPDATE SET
                section=excluded.section,
                note=excluded.note
            """,
            (row["id"], week_label, section, row["reviewer_notes"] or "", timestamp),
        )
    conn.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate personal lending market research notes from reviewed signals")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--week", default="current", help="'current' or a label such as 2026-W18")
    parser.add_argument("--language", choices=["zh", "en"], default="zh", help="Output language for the generated brief")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}. Run pipeline.py init first.")
    week_label = current_week_label() if args.week == "current" else args.week
    conn = connect(args.db)
    rows = load_reviewed_signals(conn)
    notes = load_recent_notes(conn)
    questions = load_market_questions(conn)
    source_health = load_source_health(conn)
    content = render_brief(rows, week_label, notes, questions, source_health, language=args.language)
    output_path = write_brief(content, args.output_dir, week_label)
    mark_brief_items(conn, rows, week_label)
    print(f"Wrote {len(rows)} reviewed signal(s) to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
