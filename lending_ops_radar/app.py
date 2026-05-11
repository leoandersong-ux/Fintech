"""Streamlit personal research dashboard for Zambia Digital Lending Ops Radar."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lending_ops_radar.brief_generator import (
    DEFAULT_DB,
    current_week_label,
    load_market_questions,
    load_recent_notes,
    load_reviewed_signals,
    load_source_health,
    render_brief,
)
from lending_ops_radar.intelligence import (
    assessment_table_rows,
    build_assessments,
    coverage_gaps,
    top_interpretive_findings,
)
from lending_ops_radar.competitor_matrix import build_product_matrix, render_matrix_markdown
from lending_ops_radar.pipeline import DEFAULT_SOURCES, connect, init_db, load_sources, upsert_sources
from lending_ops_radar.quality import build_quality_rows, summary_counts


st.set_page_config(page_title="个人研究雷达 | Lending Radar", layout="wide")

APP_CSS = """
<style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1480px;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    div[data-testid="stMetric"] {
        background: #f7faf6;
        border: 1px solid #dbe7dd;
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
    }
    .section-note {
        border-left: 4px solid #2f6f61;
        background: #f6faf8;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 0.95rem;
        color: #2b3a35;
        margin: 0.3rem 0 1rem 0;
    }
    .guardrail-band {
        background: #fff8ea;
        border: 1px solid #ead8a8;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        color: #4c3b16;
        margin: 0.4rem 0 1.1rem 0;
    }
    .quiet {
        color: #5f6f68;
        font-size: 0.94rem;
    }
    .rail-card {
        background: #f8f9fb;
        border: 1px solid #dfe5ea;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin: 0.4rem 0 1rem 0;
    }
    .insight-card {
        background: #ffffff;
        border: 1px solid #d9e2de;
        border-left: 4px solid #2f6f61;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 2px rgba(21, 52, 42, 0.04);
    }
    .gap-card {
        background: #fbfcff;
        border: 1px solid #dfe4ef;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin: 0.45rem 0;
    }
</style>
"""

COLUMN_LABELS = {
    "id": "ID",
    "source_id": "来源ID | Source ID",
    "source_name": "来源 | Source",
    "name": "名称 | Name",
    "source_type": "来源类型 | Source Type",
    "frequency": "频率 | Frequency",
    "category": "类别 | Category",
    "enabled": "启用 | Enabled",
    "url": "链接 | URL",
    "compliance_notes": "边界说明 | Guardrails",
    "item_title": "信号内容 | Signal",
    "classification": "分类 | Classification",
    "risk_level": "风险 | Risk",
    "item_url": "来源链接 | Source Link",
    "last_seen_at": "最近发现 | Last Seen",
    "review_status": "状态 | Status",
    "raw_text": "原文片段 | Raw Text",
    "priority": "优先级 | Priority",
    "reviewer_notes": "研究备注 | Research Notes",
    "recommended_action": "下一步 | Next Action",
    "run_count": "运行次数 | Runs",
    "success_count": "成功 | Success",
    "fail_count": "失败 | Fail",
    "success_rate": "成功率 | Success Rate",
    "last_status": "最近状态 | Last Status",
    "last_signal_count": "最近信号数 | Last Signals",
    "total_signal_count": "累计信号数 | Total Signals",
    "last_error": "最近错误 | Last Error",
    "updated_at": "更新时间 | Updated",
    "created_at": "创建时间 | Created",
    "note_type": "笔记类型 | Note Type",
    "title": "标题 | Title",
    "market_question": "市场问题 | Market Question",
    "confidence": "信心 | Confidence",
    "linked_signal": "关联信号 | Linked Signal",
    "question_key": "问题ID | Question Key",
    "area": "领域 | Area",
    "question": "问题 | Question",
    "status": "状态 | Status",
    "current_hypothesis": "当前假设 | Current Hypothesis",
    "evidence": "证据 | Evidence",
    "capability_area": "能力线 | Capability Area",
    "goal": "目标 | Goal",
    "finished_at": "完成时间 | Finished",
    "run_status": "运行状态 | Run Status",
    "signal_count": "信号数 | Signals",
    "error_message": "错误信息 | Error",
    "signal_id": "信号ID | Signal ID",
    "signal": "信号 | Signal",
    "source": "来源 | Source",
    "source_link": "来源链接 | Source Link",
    "impact_level": "影响级别 | Impact",
    "domain_cn": "影响域 | Domain",
    "domain_en": "Domain",
    "lending_impact_cn": "对小微贷款业务的影响",
    "lending_impact_en": "Micro-lending Impact",
    "affected_processes_cn": "受影响流程",
    "affected_processes_en": "Affected Processes",
    "recommended_actions_cn": "建议动作",
    "recommended_actions_en": "Recommended Actions",
    "follow_up_questions_cn": "待验证问题",
    "follow_up_questions_en": "Follow-up Questions",
    "finding_cn": "关键判断",
    "finding_en": "Key Finding",
    "why_cn": "为什么重要",
    "why_en": "Why It Matters",
    "area_cn": "领域",
    "area_en": "Area",
    "coverage_cn": "覆盖度",
    "coverage_en": "Coverage",
    "gap_cn": "缺口",
    "gap_en": "Gap",
    "next_source_cn": "下一步来源",
    "next_source_en": "Next Sources",
    "institution": "机构 | Institution",
    "product_or_signal": "产品/信号 | Product/Signal",
    "product_type_cn": "产品类型 | CN",
    "product_type_en": "Product Type | EN",
    "segment_cn": "客群 | CN",
    "segment_en": "Segment | EN",
    "limit_amount": "额度 | Limit",
    "tenor_or_repayment": "期限/还款 | Tenor/Repayment",
    "pricing_or_disclosure": "定价/披露 | Pricing/Disclosure",
    "speed_claim": "速度承诺 | Speed Claim",
    "payment_or_disbursement": "支付/放款 | Payment/Payout",
    "support_privacy_ops": "客服/隐私/运营 | Support/Privacy/Ops",
    "business_interpretation_cn": "业务解读 | CN",
    "business_interpretation_en": "Business Interpretation | EN",
    "next_questions_cn": "后续问题 | CN",
    "next_questions_en": "Next Questions | EN",
    "source_signal_ids": "来源信号ID | Source IDs",
    "source_links": "来源链接 | Source Links",
    "source_status": "来源状态 | Source Status",
    "product_layer_cn": "产品层 | Product Layer",
    "product_layer_en": "Product Layer | EN",
    "limit_value_zmw": "额度数值ZMW | Limit Value",
    "limit_tier_cn": "额度档 | Limit Tier",
    "limit_tier_en": "Limit Tier | EN",
    "speed_tier_cn": "速度层 | Speed Tier",
    "speed_tier_en": "Speed Tier | EN",
    "payment_maturity_cn": "支付成熟度 | Payment Maturity",
    "payment_maturity_en": "Payment Maturity | EN",
    "support_privacy_maturity_cn": "客服/隐私成熟度",
    "support_privacy_maturity_en": "Support/Privacy Maturity | EN",
    "data_completeness_score": "公开字段完整度 | Completeness",
    "gap_flags_cn": "信息缺口 | Evidence Gaps",
    "gap_flags_en": "Evidence Gaps | EN",
    "matrix_priority_cn": "矩阵优先级 | Priority",
    "matrix_priority_en": "Matrix Priority | EN",
    "competitor_positioning_cn": "竞品定位 | Positioning",
    "competitor_positioning_en": "Competitor Positioning | EN",
    "operating_risk_focus_cn": "运营风险焦点 | Ops Focus",
    "operating_risk_focus_en": "Operating Risk Focus | EN",
    "source_credibility_score": "来源可信度 | Source Score",
    "lending_relevance_score": "业务相关度 | Relevance",
    "manual_review_need_score": "回源需求 | Review Need",
    "brief_candidate_score": "周报候选分 | Brief Score",
    "quality_tier_cn": "质量层级 | Quality Tier",
    "quality_tier_en": "Quality Tier | EN",
    "recommended_use_cn": "建议用途 | Recommended Use",
    "recommended_use_en": "Recommended Use | EN",
    "quality_reason_cn": "评分原因 | Quality Reason",
    "quality_reason_en": "Quality Reason | EN",
    "check_cn": "检查项 | Check",
    "check_en": "Check | EN",
    "check_status": "状态 | Status",
    "detail_cn": "说明 | Detail",
    "detail_en": "Detail | EN",
    "rows": "行数 | Rows",
}

STATUS_LABELS = {
    "new": "待审 | new",
    "reviewed": "已审 | reviewed",
    "briefed": "已入周报 | briefed",
    "rejected": "已排除 | rejected",
}

QUESTION_STATUS_LABELS = {
    "open": "开放 | open",
    "investigating": "研究中 | investigating",
    "answered": "已回答 | answered",
    "parked": "暂存 | parked",
}

GOAL_STATUS_LABELS = {
    "active": "进行中 | active",
    "in_progress": "推进中 | in progress",
    "done": "完成 | done",
    "paused": "暂停 | paused",
}

CONFIDENCE_LABELS = {
    "high": "高 | high",
    "medium": "中 | medium",
    "low": "低 | low",
}

NOTE_TYPE_LABELS = {
    "market_observation": "市场观察 | market observation",
    "source_quality": "来源质量 | source quality",
    "taxonomy_learning": "分类学习 | taxonomy learning",
    "research_question": "研究问题 | research question",
    "weekly_synthesis": "周度综合 | weekly synthesis",
    "capability_line": "能力线 | capability line",
}


def apply_app_style() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def title_pair(cn: str, en: str) -> str:
    return f"{cn} | {en}"


def section_header(cn: str, en: str, note_cn: str = "", note_en: str = "") -> None:
    st.markdown(f"### {title_pair(cn, en)}")
    if note_cn or note_en:
        st.markdown(
            f'<div class="section-note">{note_cn}<br><span class="quiet">{note_en}</span></div>',
            unsafe_allow_html=True,
        )


def looks_question_garbled(value: object) -> bool:
    text = "" if value is None else str(value)
    if not text:
        return False
    question_count = text.count("?")
    return "????" in text or (question_count >= 6 and question_count / max(len(text), 1) > 0.18)


def readable_text(value: object, fallback: str = "历史备注存在编码损坏，需回源复核 | Historical note has encoding loss; review source.") -> str:
    text = "" if value is None else str(value)
    if looks_question_garbled(text):
        return fallback
    return text


def readable_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.select_dtypes(include=["object"]).columns:
        cleaned[column] = cleaned[column].map(readable_text)
    return cleaned


def display_df(df: pd.DataFrame, **kwargs: object) -> None:
    cleaned = readable_dataframe(df)
    st.dataframe(cleaned.rename(columns=COLUMN_LABELS), use_container_width=True, hide_index=True, **kwargs)


def count_rows(conn: sqlite3.Connection, query: str, params: tuple = ()) -> int:
    return int(conn.execute(query, params).fetchone()[0])


def ensure_db() -> sqlite3.Connection:
    conn = connect(DEFAULT_DB)
    init_db(conn)
    if conn.execute("SELECT COUNT(*) AS count FROM sources").fetchone()["count"] == 0:
        upsert_sources(conn, load_sources(DEFAULT_SOURCES))
    return conn


def dataframe(conn: sqlite3.Connection, query: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(query, conn, params=params)


def update_review(conn: sqlite3.Connection, signal_id: int, status: str, priority: int, notes: str, action: str) -> None:
    conn.execute(
        """
        UPDATE reviews
        SET review_status = ?, priority = ?, reviewer_notes = ?, recommended_action = ?, updated_at = datetime('now')
        WHERE signal_id = ?
        """,
        (status, priority, notes, action, signal_id),
    )
    conn.commit()


def add_research_note(
    conn: sqlite3.Connection,
    signal_id: int | None,
    note_type: str,
    title: str,
    note: str,
    question: str,
    confidence: str,
) -> None:
    conn.execute(
        """
        INSERT INTO research_notes (
            signal_id, note_type, title, note, market_question, confidence, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (signal_id, note_type, title, note, question, confidence),
    )
    conn.commit()


def update_learning_goal(conn: sqlite3.Connection, goal_id: int, status: str, evidence: str) -> None:
    conn.execute(
        """
        UPDATE learning_goals
        SET status = ?, evidence = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (status, evidence, goal_id),
    )
    conn.commit()


def update_market_question(
    conn: sqlite3.Connection,
    question_id: int,
    status: str,
    hypothesis: str,
    evidence: str,
) -> None:
    conn.execute(
        """
        UPDATE market_questions
        SET status = ?, current_hypothesis = ?, evidence = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (status, hypothesis, evidence, question_id),
    )
    conn.commit()


def seed_market_questions(conn: sqlite3.Connection) -> None:
    questions = [
        (
            "complaint_themes",
            "Complaints",
            "Which public complaint themes appear most often around digital financial services and lending-adjacent journeys?",
        ),
        (
            "regulatory_surface",
            "Regulatory watch",
            "Which public regulator pages are most useful for tracking lending, payments, consumer protection, and data protection risk?",
        ),
        (
            "fraud_payment_overlap",
            "Fraud and payments",
            "Where do mobile-money fraud, incomplete transaction, and customer-support issues overlap with lending operations?",
        ),
        (
            "privacy_lending_apps",
            "Privacy",
            "What privacy and data-subject rights themes should a lending app operator understand from public sources?",
        ),
        (
            "source_reliability",
            "Research process",
            "Which public sources are stable enough for recurring Scrapling collection, and which should remain manual review sources?",
        ),
        (
            "payment_rails_lending_ops",
            "Payment rails",
            "How do BoZ payment-system rules, payment-rail changes, and mobile-money/payment-service directives affect digital lending disbursement, repayment, failed transactions, complaints, fees, and partner risk?",
        ),
    ]
    for key, area, question in questions:
        conn.execute(
            """
            INSERT INTO market_questions (question_key, area, question, status, updated_at)
            VALUES (?, ?, ?, 'open', datetime('now'))
            ON CONFLICT(question_key) DO UPDATE SET
                area=excluded.area,
                question=excluded.question,
                updated_at=excluded.updated_at
            """,
            (key, area, question),
        )
    conn.commit()


def deployment_checks(conn: sqlite3.Connection) -> list[dict[str, object]]:
    brief_dir = ROOT / "data" / "briefs"
    db_path = DEFAULT_DB
    latest_brief = max(brief_dir.glob("zambia_digital_lending_personal_notes_*.md"), key=lambda path: path.stat().st_mtime, default=None)
    checks = [
        {
            "check_cn": "Streamlit 入口",
            "check_en": "Streamlit entrypoint",
            "check_status": "pass" if (ROOT / "streamlit_app.py").exists() else "missing",
            "detail_cn": "streamlit_app.py 存在，可作为 Cloud main file。",
            "detail_en": "streamlit_app.py exists and can be used as the Cloud main file.",
        },
        {
            "check_cn": "云端依赖",
            "check_en": "Cloud requirements",
            "check_status": "pass" if (ROOT / "requirements.txt").exists() else "missing",
            "detail_cn": "requirements.txt 保持精简，避免云端重编译 pyarrow。",
            "detail_en": "requirements.txt is intentionally minimal to avoid rebuilding pyarrow.",
        },
        {
            "check_cn": "研究数据库",
            "check_en": "Research database",
            "check_status": "pass" if db_path.exists() else "missing",
            "detail_cn": f"SQLite: {db_path.name}, {round(db_path.stat().st_size / 1024 / 1024, 2) if db_path.exists() else 0} MB。",
            "detail_en": "SQLite research database is available for the dashboard.",
        },
        {
            "check_cn": "已复核信号",
            "check_en": "Reviewed signals",
            "check_status": "pass" if count_rows(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'reviewed'") > 0 else "empty",
            "detail_cn": "有 reviewed 信号，可生成业务解读和周报。",
            "detail_en": "Reviewed signals exist for intelligence and weekly notes.",
        },
        {
            "check_cn": "最近周报",
            "check_en": "Latest weekly note",
            "check_status": "pass" if latest_brief else "missing",
            "detail_cn": latest_brief.name if latest_brief else "尚未找到个人周报 Markdown。",
            "detail_en": "Latest generated personal notes file.",
        },
    ]
    return checks


def render_deployment_health(conn: sqlite3.Connection) -> None:
    section_header(
        "部署健康",
        "Deploy Health",
        "确认 Streamlit Cloud 部署、数据库、周报和同步边界是否处于可用状态。",
        "Check whether Streamlit deployment, database, weekly notes, and sync boundaries are usable.",
    )
    db_size = round(DEFAULT_DB.stat().st_size / 1024 / 1024, 2) if DEFAULT_DB.exists() else 0
    latest_source = conn.execute("SELECT MAX(updated_at) FROM source_quality").fetchone()[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("数据库 | DB", f"{db_size} MB")
    col2.metric("信号 | Signals", count_rows(conn, "SELECT COUNT(*) FROM signals"))
    col3.metric("已复核 | Reviewed", count_rows(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'reviewed'"))
    col4.metric("最近来源运行 | Last Source Run", latest_source or "N/A")

    st.markdown("#### 部署检查 | Deployment Checks")
    display_df(pd.DataFrame(deployment_checks(conn)))

    st.markdown("#### 节点同步边界 | Milestone Sync Boundary")
    st.markdown(
        """
        <div class="section-note">
        中文：节点同步只包含 fintech 研究平台文件、SQLite reviewed data、生成的 briefs 和部署文件；不包含无关商机项目资产、PDF/DOCX 渲染物、私人借款人数据或任何 secret。
        <br>
        <span class="quiet">English: Milestone sync includes only fintech research platform files, reviewed SQLite data, generated briefs, and deploy files. It excludes unrelated opportunity-radar assets, PDF/DOCX render artifacts, private borrower data, and secrets.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(conn: sqlite3.Connection) -> None:
    section_header(
        "数据源",
        "Sources",
        "查看当前启用的公开来源、抓取边界和运行健康度。",
        "Review configured public sources, collection boundaries, and source health.",
    )
    if st.button("初始化/刷新来源配置 | Initialize / Refresh Source Config"):
        upsert_sources(conn, load_sources(DEFAULT_SOURCES))
        st.success("来源配置已刷新 | Source config refreshed.")
    display_df(
        dataframe(
            conn,
            """
            SELECT source_id, name, source_type, frequency, category, enabled, url, compliance_notes
            FROM sources
            ORDER BY enabled DESC, source_type, source_id
            """,
        )
    )

    st.markdown("#### 来源健康度 | Source Health")
    health = dataframe(
        conn,
        """
        SELECT
            q.source_id,
            s.name,
            s.enabled,
            q.run_count,
            q.success_count,
            q.fail_count,
            ROUND(CASE WHEN q.run_count > 0 THEN 1.0 * q.success_count / q.run_count ELSE 0 END, 2) AS success_rate,
            q.last_status,
            q.last_signal_count,
            q.total_signal_count,
            q.last_error,
            q.updated_at
        FROM source_quality q
        LEFT JOIN sources s ON s.source_id = q.source_id
        ORDER BY q.updated_at DESC
        """,
    )
    display_df(health)


def render_new_signals(conn: sqlite3.Connection) -> None:
    section_header(
        "新信号",
        "New Signals",
        "这里显示尚未人工判断的新条目。目标是保留能帮助理解市场的问题，而不是堆积所有抓取结果。",
        "Unreviewed items appear here. The goal is useful market learning, not maximum row count.",
    )
    new_df = dataframe(
        conn,
        """
        SELECT
            s.id, s.source_name, s.item_title, s.classification, s.risk_level,
            s.source_id, s.source_url, s.item_url, s.raw_text, s.last_seen_at,
            r.review_status, r.priority, r.reviewer_notes, r.recommended_action
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        WHERE r.review_status = 'new'
        ORDER BY s.last_seen_at DESC
        """,
    )
    if new_df.empty:
        st.success("当前没有待审信号 | No new signals in the review queue.")
    else:
        quality_df = pd.DataFrame(build_quality_rows(new_df.to_dict("records")))
        display_df(
            quality_df[
                [
                    "signal_id",
                    "signal",
                    "classification",
                    "risk_level",
                    "brief_candidate_score",
                    "manual_review_need_score",
                    "quality_tier_cn",
                    "recommended_use_cn",
                    "source_link",
                ]
            ]
        )
        with st.expander("查看原始新信号 | Raw new signals"):
            display_df(new_df.drop(columns=["raw_text"], errors="ignore"))


def render_business_intelligence(conn: sqlite3.Connection) -> None:
    section_header(
        "业务影响解读",
        "Business Impact Intelligence",
        "这里不再只是列出政策/网页，而是把已复核信号映射到小微贷款业务流程、风险域和下一步动作。",
        "This view maps reviewed public signals into micro-lending processes, risk domains, and next actions.",
    )
    rows = load_reviewed_signals(conn)
    assessments = build_assessments(rows)
    quality_rows = build_quality_rows(rows)
    findings = top_interpretive_findings(assessments)
    gaps = coverage_gaps(assessments)

    high_count = sum(1 for item in assessments if item["impact_level"] == "high")
    medium_count = sum(1 for item in assessments if item["impact_level"] == "medium")
    domains = sorted({str(item["domain_cn"]) for item in assessments})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("已解读信号 | Interpreted", len(assessments))
    col2.metric("高潜在影响 | High Potential", high_count)
    col3.metric("中潜在影响 | Medium Potential", medium_count)
    col4.metric("影响域 | Domains", len(domains))

    st.markdown("#### 本周最值得看 | Priority Reads")
    quality_df = pd.DataFrame(quality_rows)
    if quality_df.empty:
        st.info("还没有质量评分 | No quality scores yet.")
    else:
        q_col1, q_col2, q_col3 = st.columns(3)
        counts = summary_counts(quality_rows)
        q_col1.metric("优先阅读 | Priority", counts["tier"].get("优先阅读", 0))
        q_col2.metric("周报候选 | Brief Candidates", counts["tier"].get("周报候选", 0))
        q_col3.metric("平均候选分 | Avg Score", f"{round(quality_df['brief_candidate_score'].mean())}/100")
        display_df(
            quality_df.head(5)[
                [
                    "signal_id",
                    "signal",
                    "classification",
                    "risk_level",
                    "brief_candidate_score",
                    "source_credibility_score",
                    "lending_relevance_score",
                    "manual_review_need_score",
                    "quality_tier_cn",
                    "recommended_use_cn",
                    "quality_reason_cn",
                    "source_link",
                ]
            ]
        )

    st.markdown("#### 关键判断 | Key Interpretive Findings")
    for item in findings:
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>{item['finding_cn']}</strong><br>
                <span class="quiet">{item['finding_en']}</span><br><br>
                {item['why_cn']}<br>
                <span class="quiet">{item['why_en']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 小微贷款业务影响矩阵 | Micro-lending Impact Matrix")
    impact_df = pd.DataFrame(assessment_table_rows(assessments, limit=50))
    if impact_df.empty:
        st.info("还没有已复核信号可解读 | No reviewed signals available for interpretation.")
    else:
        st.markdown(
            """
            <div class="section-note">
            中文：这里按卡片阅读，不再用宽表格。每张卡片只回答一个问题：这条公开信号会影响小微贷款业务的哪个流程、为什么重要、下一步该回源确认什么。
            <br>
            <span class="quiet">English: This is card-based instead of a wide table. Each card explains which lending process the public signal may affect, why it matters, and what to verify next.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for index, item in enumerate(impact_df.head(12).to_dict("records"), start=1):
            with st.container(border=True):
                st.markdown(f"**{index}. {readable_text(item['domain_cn'])} | {readable_text(item['domain_en'])}**")
                st.caption(f"Level: {readable_text(item['impact_level'])} · Signal ID: {readable_text(item['signal_id'])}")
                st.markdown(f"**信号 | Signal:** {readable_text(item['signal'])}")
                st.markdown(f"**对小微贷款业务的影响：** {readable_text(item['lending_impact_cn'])}")
                st.markdown(f"**Lending impact:** {readable_text(item['lending_impact_en'])}")
                st.markdown(f"**建议动作：** {readable_text(item['recommended_actions_cn'])}")
                st.markdown(f"**Recommended action:** {readable_text(item['recommended_actions_en'])}")
                st.markdown(f"**待验证问题：** {readable_text(item['follow_up_questions_cn'])}")
                st.markdown(f"**Follow-up question:** {readable_text(item['follow_up_questions_en'])}")
                st.markdown(f"[来源 | Source]({readable_text(item['source_link'])})")
        with st.expander("查看完整结构化表格 | Full structured table"):
            display_df(
                impact_df[
                    [
                        "signal_id",
                        "domain_cn",
                        "impact_level",
                        "signal",
                        "lending_impact_cn",
                        "affected_processes_cn",
                        "recommended_actions_cn",
                        "follow_up_questions_cn",
                        "source_link",
                    ]
                ]
            )

    st.markdown("#### 情报覆盖缺口 | Intelligence Coverage Gaps")
    gap_df = pd.DataFrame(gaps)
    display_df(gap_df[["area_cn", "coverage_cn", "gap_cn", "next_source_cn", "area_en", "coverage_en", "gap_en", "next_source_en"]])


def render_competitor_watch(conn: sqlite3.Connection) -> None:
    section_header(
        "竞品观察",
        "Competitor Watch",
        "只看手动批准的公开竞品来源，重点关注产品、费用、期限、支持、隐私和公开 app listing 变化。",
        "A focused view for manually approved public competitor sources: products, fees, tenor, support, privacy, and public app-listing changes.",
    )
    sources = dataframe(
        conn,
        """
        SELECT source_id, name, source_type, url, category, enabled, compliance_notes, updated_at
        FROM sources
        WHERE source_id LIKE 'competitor_%'
        ORDER BY enabled DESC, source_type, source_id
        """,
    )
    signals = dataframe(
        conn,
        """
        SELECT
            s.id,
            s.source_name,
            s.item_title,
            s.classification,
            s.risk_level,
            r.review_status,
            r.priority,
            r.recommended_action,
            s.item_url,
            s.last_seen_at
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        WHERE s.source_id LIKE 'competitor_%'
        ORDER BY r.review_status = 'new' DESC, r.priority ASC, s.last_seen_at DESC
        LIMIT 100
        """,
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("竞品源 | Sources", len(sources))
    col2.metric("已启用 | Enabled", int((sources["enabled"] == 1).sum()) if not sources.empty else 0)
    col3.metric("竞品信号 | Signals", len(signals))
    col4.metric("待复核 | New", int((signals["review_status"] == "new").sum()) if not signals.empty else 0)

    st.markdown("#### 来源清单 | Source Watchlist")
    display_df(sources)

    st.markdown("#### 竞品新信号 | Competitor Signals")
    if signals.empty:
        st.info("还没有竞品信号。运行启用的 competitor watchlist 源后会出现在这里。| No competitor signals yet.")
    else:
        display_df(signals)

    st.markdown("#### 阅读框架 | Review Lens")
    st.markdown(
        """
        <div class="section-note">
        中文：复核竞品信号时优先问：额度/期限/费用是否变化？放款和还款依赖什么支付轨道？客服和争议入口是否清晰？是否出现隐私、催收、失败扣款、到账慢等公开主题？<br>
        <span class="quiet">English: Review competitor signals through limits, tenor, fees, payment-rail dependency, support/dispute clarity, and public themes such as privacy, collections, failed deductions, and slow payout.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_competitor_matrix(conn: sqlite3.Connection) -> None:
    section_header(
        "竞品产品矩阵",
        "Competitor Product Matrix",
        "把已复核的竞品信号整理成可比较的定位、产品层、额度档、速度承诺、支付成熟度、客服/隐私成熟度和信息缺口。",
        "A comparable view of reviewed competitor signals: positioning, product layer, limit tier, speed promise, payment maturity, support/privacy maturity, and evidence gaps.",
    )
    rows = build_product_matrix(conn)
    matrix_df = pd.DataFrame(rows)
    if matrix_df.empty:
        st.info("还没有竞品矩阵。请先复核 competitor signals。| No competitor matrix yet.")
        return

    matrix_df["data_completeness_score"] = pd.to_numeric(matrix_df["data_completeness_score"], errors="coerce").fillna(0).astype(int)
    institutions = matrix_df["institution"].nunique()
    direct_limits = int((matrix_df["limit_amount"].notna() & ~matrix_df["limit_amount"].isin(["Not captured", "Not applicable", ""])).sum())
    payment_rows = int((matrix_df["payment_or_disbursement"].notna() & ~matrix_df["payment_or_disbursement"].isin(["Not captured", ""])).sum())
    ops_rows = int(
        (
            matrix_df["support_privacy_ops"].notna()
            & (matrix_df["support_privacy_ops"] != "No dedicated support/privacy detail captured")
            & (matrix_df["support_privacy_ops"] != "")
        ).sum()
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("机构 | Institutions", institutions)
    col2.metric("矩阵行 | Matrix Rows", len(matrix_df))
    col3.metric("平均完整度 | Avg Completeness", f"{round(matrix_df['data_completeness_score'].mean())}/100")
    col4.metric("高优先级 | High Priority", int(matrix_df["matrix_priority_cn"].str.startswith("高").sum()))

    st.markdown(
        """
        <div class="section-note">
        中文：完整度分数是“公开研究字段是否被捕捉”的分数，不是产品优劣分数。高优先级代表值得先回源复核，因为它可能影响放款体验、支付轨道、风控权重或隐私/投诉运营。
        <br>
        <span class="quiet">English: Completeness measures captured public research fields, not product quality. High priority means the item deserves source review because it may affect payout experience, payment rails, risk weight, or privacy/dispute operations.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        focus = st.multiselect(
            "筛选机构 | Filter institutions",
            sorted(matrix_df["institution"].unique().tolist()),
            default=sorted(matrix_df["institution"].unique().tolist()),
        )
    with filter_col2:
        layer_focus = st.multiselect(
            "产品层 | Product layer",
            sorted(matrix_df["product_layer_cn"].unique().tolist()),
            default=sorted(matrix_df["product_layer_cn"].unique().tolist()),
        )
    with filter_col3:
        limit_focus = st.multiselect(
            "额度档 | Limit tier",
            sorted(matrix_df["limit_tier_cn"].unique().tolist()),
            default=sorted(matrix_df["limit_tier_cn"].unique().tolist()),
        )
    filtered = matrix_df.copy()
    if focus:
        filtered = filtered[filtered["institution"].isin(focus)]
    if layer_focus:
        filtered = filtered[filtered["product_layer_cn"].isin(layer_focus)]
    if limit_focus:
        filtered = filtered[filtered["limit_tier_cn"].isin(limit_focus)]

    st.markdown("#### 横向比较 | Comparison Summary")
    compare_col1, compare_col2 = st.columns(2)
    with compare_col1:
        display_df(
            filtered.groupby("product_layer_cn", dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )
    with compare_col2:
        display_df(
            filtered.groupby("limit_tier_cn", dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )

    compare_col3, compare_col4 = st.columns(2)
    with compare_col3:
        display_df(
            filtered.groupby("payment_maturity_cn", dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )
    with compare_col4:
        display_df(
            filtered.groupby("speed_tier_cn", dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )

    st.markdown("#### 竞品定位 2.0 | Competitor Positioning 2.0")
    display_df(
        filtered.groupby("competitor_positioning_cn", dropna=False)
        .agg(
            rows=("product_or_signal", "count"),
            avg_completeness=("data_completeness_score", "mean"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )

    st.markdown(f"#### 产品矩阵 | Product Matrix ({len(filtered)} rows)")
    display_cols = [
        "institution",
        "product_or_signal",
        "competitor_positioning_cn",
        "product_layer_cn",
        "limit_tier_cn",
        "segment_cn",
        "limit_amount",
        "tenor_or_repayment",
        "pricing_or_disclosure",
        "speed_tier_cn",
        "payment_maturity_cn",
        "support_privacy_maturity_cn",
        "data_completeness_score",
        "matrix_priority_cn",
        "operating_risk_focus_cn",
        "gap_flags_cn",
        "business_interpretation_cn",
        "next_questions_cn",
        "source_links",
        "source_status",
    ]
    display_df(filtered[display_cols])

    with st.expander("查看原始字段 | Source-linked details"):
        detail_cols = [
            "institution",
            "product_or_signal",
            "product_type_cn",
            "product_type_en",
            "segment_cn",
            "segment_en",
            "limit_amount",
            "tenor_or_repayment",
            "pricing_or_disclosure",
            "speed_claim",
            "payment_or_disbursement",
            "support_privacy_ops",
            "business_interpretation_en",
            "next_questions_en",
            "competitor_positioning_en",
            "operating_risk_focus_en",
            "source_links",
        ]
        display_df(filtered[detail_cols])

    csv_data = filtered.to_csv(index=False).encode("utf-8-sig")
    markdown_content = render_matrix_markdown(filtered.to_dict("records"))
    col_a, col_b = st.columns(2)
    col_a.download_button(
        "下载 CSV 矩阵 | Download CSV Matrix",
        data=csv_data,
        file_name="lending_ops_competitor_product_matrix.csv",
        mime="text/csv",
    )
    col_b.download_button(
        "下载 Markdown 矩阵 | Download Markdown Matrix",
        data=markdown_content,
        file_name="zambia_digital_lending_competitor_product_matrix.md",
        mime="text/markdown",
    )

    st.markdown("#### Markdown 预览 | Markdown Preview")
    st.markdown(markdown_content)


def render_review_queue(conn: sqlite3.Connection) -> None:
    section_header(
        "人工复核队列",
        "Review Queue",
        "把来源事实、个人解释和下一步行动分开写，避免把公开信号误读成监管结论。",
        "Keep source facts, personal interpretation, and next actions separate.",
    )
    queue = dataframe(
        conn,
        """
        SELECT
            s.id, s.source_name, s.item_title, s.classification, s.risk_level,
            s.raw_text, s.item_url, r.review_status, r.priority,
            r.reviewer_notes, r.recommended_action
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        ORDER BY r.review_status = 'new' DESC, r.priority ASC, s.last_seen_at DESC
        """,
    )
    display_df(queue.drop(columns=["raw_text"], errors="ignore"))
    if queue.empty:
        st.info("还没有信号。请先运行 pipeline 或 seed sample records。| No signals yet. Run the pipeline or seed sample records.")
        return

    selected_id = st.selectbox("信号 ID | Signal ID", queue["id"].tolist())
    selected = queue[queue["id"] == selected_id].iloc[0]
    with st.container(border=True):
        st.markdown(f"**{selected['item_title']}**")
        st.caption(selected["item_url"] or "")
        st.write(selected["raw_text"])

    status = st.selectbox(
        "复核状态 | Review status",
        ["new", "reviewed", "briefed", "rejected"],
        index=["new", "reviewed", "briefed", "rejected"].index(selected["review_status"]),
        format_func=lambda value: STATUS_LABELS.get(value, value),
    )
    priority = st.slider("优先级 | Priority", min_value=1, max_value=3, value=int(selected["priority"]))
    notes = st.text_area("研究备注 | Reviewer notes", value=selected["reviewer_notes"] or "")
    action = st.text_area("下一步行动 | Recommended action", value=selected["recommended_action"] or "")
    if st.button("保存复核 | Save Review"):
        update_review(conn, int(selected_id), status, priority, notes, action)
        st.success("复核已更新 | Review updated.")


def render_brief_draft(conn: sqlite3.Connection) -> None:
    section_header(
        "个人周度笔记",
        "Personal Weekly Notes",
        "只使用已复核信号生成，方便后续手工精修。",
        "Generated only from reviewed signals so it stays suitable for human refinement.",
    )
    rows = load_reviewed_signals(conn)
    notes = load_recent_notes(conn)
    questions = load_market_questions(conn)
    source_health = load_source_health(conn)
    content = render_brief(rows, current_week_label(), notes, questions, source_health)
    st.download_button(
        "下载 Markdown 笔记 | Download Markdown Notes",
        data=content,
        file_name=f"zambia_digital_lending_personal_notes_{current_week_label()}.md",
        mime="text/markdown",
    )
    st.markdown(content)


def render_research_notes(conn: sqlite3.Connection) -> None:
    section_header(
        "研究笔记",
        "Research Notes",
        "把你自己的市场理解沉淀下来，最好每条笔记都能回答一个市场问题。",
        "Capture your own interpretation and connect each note to a durable market question where possible.",
    )
    notes = dataframe(
        conn,
        """
        SELECT
            n.id,
            n.created_at,
            n.note_type,
            n.title,
            n.market_question,
            n.confidence,
            s.item_title AS linked_signal
        FROM research_notes n
        LEFT JOIN signals s ON s.id = n.signal_id
        ORDER BY n.created_at DESC
        """,
    )
    display_df(notes)

    signals = dataframe(
        conn,
        """
        SELECT id, item_title
        FROM signals
        ORDER BY last_seen_at DESC
        LIMIT 100
        """,
    )
    signal_options = {"不关联信号 | No linked signal": None}
    signal_options.update({f"{row.id}: {row.item_title[:90]}": int(row.id) for row in signals.itertuples()})

    st.markdown("#### 新增笔记 | Add Note")
    selected_signal = st.selectbox("可选关联信号 | Optional linked signal", list(signal_options.keys()))
    note_type = st.selectbox(
        "笔记类型 | Note type",
        ["market_observation", "source_quality", "taxonomy_learning", "research_question", "weekly_synthesis", "capability_line"],
        format_func=lambda value: NOTE_TYPE_LABELS.get(value, value),
    )
    title = st.text_input("标题 | Title")
    question = st.text_input("市场问题 | Market question")
    confidence = st.selectbox(
        "信心 | Confidence",
        ["medium", "low", "high"],
        format_func=lambda value: CONFIDENCE_LABELS.get(value, value),
    )
    note = st.text_area("笔记 | Note")
    if st.button("保存研究笔记 | Save Research Note"):
        if not title.strip() or not note.strip():
            st.error("标题和笔记不能为空 | Title and note are required.")
        else:
            add_research_note(conn, signal_options[selected_signal], note_type, title, note, question, confidence)
            st.success("研究笔记已保存 | Research note saved.")


def render_market_questions(conn: sqlite3.Connection) -> None:
    section_header(
        "市场问题",
        "Market Questions",
        "让研究围绕问题推进，而不是围绕数据堆积推进。",
        "Use questions to guide the research loop instead of collecting rows for their own sake.",
    )
    if st.button("初始化市场问题 | Seed Market Questions"):
        seed_market_questions(conn)
        st.success("市场问题已初始化 | Market questions seeded.")

    questions = dataframe(
        conn,
        """
        SELECT id, question_key, area, question, status, current_hypothesis, evidence, updated_at
        FROM market_questions
        ORDER BY status, area, question_key
        """,
    )
    display_df(questions)

    if questions.empty:
        st.info("还没有市场问题。先初始化问题以开始结构化研究循环。| No market questions yet. Seed them to start a structured research loop.")
        return

    selected_id = st.selectbox("问题 ID | Question ID", questions["id"].tolist())
    current = questions[questions["id"] == selected_id].iloc[0]
    st.markdown(f"**{current['question']}**")
    status = st.selectbox(
        "问题状态 | Question status",
        ["open", "investigating", "answered", "parked"],
        index=["open", "investigating", "answered", "parked"].index(current["status"])
        if current["status"] in ["open", "investigating", "answered", "parked"]
        else 0,
        format_func=lambda value: QUESTION_STATUS_LABELS.get(value, value),
    )
    hypothesis = st.text_area("当前假设 | Current hypothesis", value=current["current_hypothesis"] or "")
    evidence = st.text_area("证据 | Evidence", value=current["evidence"] or "")
    if st.button("更新市场问题 | Update Market Question"):
        update_market_question(conn, int(selected_id), status, hypothesis, evidence)
        st.success("市场问题已更新 | Market question updated.")


def render_payment_rails(conn: sqlite3.Connection) -> None:
    section_header(
        "支付轨道与借贷运营",
        "Payment Rails / Lending Ops",
        "集中阅读 BoZ 公开信号：ZIPSS、Montran、National Financial Switch、e-money、移动支付、投诉和费用。",
        "Read BoZ public-source signals around ZIPSS, Montran, National Financial Switch, e-money, mobile payments, complaints, and fees.",
    )

    question = dataframe(
        conn,
        """
        SELECT question, status, current_hypothesis, evidence, updated_at
        FROM market_questions
        WHERE question_key = 'payment_rails_lending_ops'
        """,
    )
    if not question.empty:
        current = question.iloc[0]
        st.markdown(
            f"""
            <div class="rail-card">
                <strong>市场问题 | Market question</strong><br>
                {current['question']}<br><br>
                <strong>当前假设 | Current hypothesis</strong><br>
                {current["current_hypothesis"] or ""}<br><br>
                <span class="quiet">{current["evidence"] or ""}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    rails = dataframe(
        conn,
        """
        SELECT
            s.id,
            s.source_name,
            s.item_title,
            s.classification,
            s.risk_level,
            r.priority,
            r.review_status,
            r.reviewer_notes,
            r.recommended_action,
            s.item_url
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        WHERE s.source_id LIKE 'boz_%'
          AND r.review_status IN ('reviewed', 'briefed')
          AND (
            lower(s.item_title) LIKE '%zipss%'
            OR lower(s.item_title) LIKE '%montran%'
            OR lower(s.item_title) LIKE '%national financial switch%'
            OR lower(s.item_title) LIKE '%electronic money%'
            OR lower(s.item_title) LIKE '%mobile payments%'
            OR lower(s.item_title) LIKE '%money transfer%'
            OR lower(s.item_title) LIKE '%payment service%'
            OR lower(s.item_title) LIKE '%settlement%'
            OR lower(s.item_title) LIKE '%gateway%'
            OR lower(s.item_title) LIKE '%complaints%'
            OR lower(s.item_title) LIKE '%charges%'
            OR lower(s.item_title) LIKE '%fees%'
          )
        ORDER BY r.priority ASC, s.last_seen_at DESC
        """,
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("已复核轨道信号 | Reviewed Rails Signals", len(rails))
    col2.metric("高优先级 | Priority 1", int((rails["priority"] == 1).sum()) if not rails.empty else 0)
    col3.metric("需手读/OCR | Manual Read/OCR", int(rails["item_title"].str.contains("metadata-only", case=False, na=False).sum()) if not rails.empty else 0)
    display_df(rails)

    manual = rails[rails["item_title"].str.contains("metadata-only", case=False, na=False)] if not rails.empty else rails
    if not manual.empty:
        st.markdown("#### 手动阅读/OCR 锚点 | Manual-Read / OCR Anchors")
        display_df(
            manual[["id", "item_title", "item_url", "recommended_action"]],
        )


def render_capability_tracker(conn: sqlite3.Connection) -> None:
    section_header(
        "能力建设追踪",
        "Capability Tracker",
        "这里不是 KPI 面板，而是记录你每周具体学到了什么、哪条能力线更清楚了。",
        "This is a learning ledger: what became clearer this week, and which capability line advanced.",
    )
    if st.button("初始化学习目标 | Seed Learning Goals"):
        goals = [
            (
                "scrapling_public_sources",
                "Scrapling collection",
                "Run at least three public-source fetches and understand which source types are stable for HTTP fetching.",
            ),
            (
                "lending_taxonomy",
                "Market taxonomy",
                "Build a useful taxonomy for complaint, fraud, privacy, fees, repayment, disbursement, and regulatory signals.",
            ),
            (
                "review_discipline",
                "Human review workflow",
                "Review signals weekly and write notes that separate source facts from personal interpretation.",
            ),
            (
                "weekly_personal_brief",
                "Research synthesis",
                "Generate one weekly personal market note with sources, open questions, and next learning actions.",
            ),
            (
                "payment_rails_lens",
                "Payment rails lens",
                "Track how public BoZ payment-system rules and payment-rail changes may affect lending disbursement, repayment, failed transactions, complaints, fees, and partner risk.",
            ),
        ]
        for goal_key, area, goal in goals:
            conn.execute(
                """
                INSERT INTO learning_goals (goal_key, capability_area, goal, status, updated_at)
                VALUES (?, ?, ?, 'active', datetime('now'))
                ON CONFLICT(goal_key) DO UPDATE SET
                    capability_area=excluded.capability_area,
                    goal=excluded.goal,
                    updated_at=excluded.updated_at
                """,
                (goal_key, area, goal),
            )
        conn.commit()
        st.success("学习目标已初始化 | Learning goals seeded.")

    goals_df = dataframe(
        conn,
        """
        SELECT id, capability_area, goal, status, evidence, updated_at
        FROM learning_goals
        ORDER BY status, capability_area
        """,
    )
    display_df(goals_df)

    if not goals_df.empty:
        selected_goal = st.selectbox("目标 ID | Goal ID", goals_df["id"].tolist())
        current = goals_df[goals_df["id"] == selected_goal].iloc[0]
        status = st.selectbox(
            "目标状态 | Goal status",
            ["active", "in_progress", "done", "paused"],
            index=["active", "in_progress", "done", "paused"].index(current["status"])
            if current["status"] in ["active", "in_progress", "done", "paused"]
            else 0,
            format_func=lambda value: GOAL_STATUS_LABELS.get(value, value),
        )
        evidence = st.text_area("证据/学习证明 | Evidence / learning proof", value=current["evidence"] or "")
        if st.button("更新学习目标 | Update Learning Goal"):
            update_learning_goal(conn, int(selected_goal), status, evidence)
            st.success("学习目标已更新 | Learning goal updated.")

    st.markdown("#### 平台统计 | Platform Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("信号 | Signals", int(conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]))
    col2.metric("研究笔记 | Research Notes", int(conn.execute("SELECT COUNT(*) FROM research_notes").fetchone()[0]))
    col3.metric("来源运行 | Source Runs", int(conn.execute("SELECT COUNT(*) FROM source_runs").fetchone()[0]))

    st.markdown("#### 最近来源运行 | Recent Source Runs")
    display_df(
        dataframe(
            conn,
            """
            SELECT source_id, run_status, signal_count, error_message, finished_at
            FROM source_runs
            ORDER BY finished_at DESC
            LIMIT 20
            """,
        )
    )


def render_guardrails() -> None:
    section_header(
        "边界与合规护栏",
        "Compliance Guardrails",
        "这个平台是个人公开来源研究工具，不是合规结论、法律意见或商业交付物。",
        "This is a personal public-source research tool, not a legal opinion, compliance approval, or commercial deliverable.",
    )
    st.markdown(
        """
<div class="guardrail-band">
<strong>中文</strong><br>
- 只使用公开网页、公开 app listing、官方公告、公开新闻/评论，以及你手动批准的公开 watchlist。<br>
- 不收集借款人记录、私人消息、客户数据库、专有规则、非公开报告或受限页面。<br>
- 不绕过登录、付费墙、CAPTCHA、访问频率限制或访问控制。<br>
- 所有个人结论都要保留来源链接，并使用保守措辞。<br>
- 使用“潜在信号”“需要验证”“应进一步人工检查”等表述。<br>
- 不把输出表达为法律意见、监管认证或合规批准。<br>
- 在存在真实或感知的职业冲突风险时，不商业化输出。<br><br>
<strong>English</strong><br>
- Use only public webpages, public app listings, official announcements, public news/reviews, and manually approved public watchlists.<br>
- Do not collect borrower records, private messages, client databases, proprietary rules, non-public reports, or restricted pages.<br>
- Do not bypass login, paywalls, CAPTCHA, rate limits, or access controls.<br>
- Keep personal conclusions source-linked and conservative.<br>
- Use language such as "potential signal", "requires verification", and "manual review needed".<br>
- Do not present this as legal advice, regulatory certification, or compliance approval.<br>
- Do not commercialize outputs while real or perceived conflict-of-interest risk remains.
</div>
"""
        ,
        unsafe_allow_html=True,
    )


def render_overview(conn: sqlite3.Connection) -> None:
    st.title("赞比亚数字借贷个人研究雷达 | Zambia Digital Lending Personal Research Radar")
    st.caption("公开来源市场研究工作台 | Public-source research workspace for market understanding and capability-building.")
    st.markdown(
        """
        <div class="section-note">
        中文：当前目标是能力建设和个人市场理解，不做商业交付，不使用私人/雇主/借款人数据。<br>
        <span class="quiet">English: The current goal is capability-building and personal market understanding, not commercial delivery, and not private, employer, or borrower data use.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("已复核 | Reviewed", count_rows(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'reviewed'"))
    col2.metric("待审 | New", count_rows(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'new'"))
    col3.metric("研究笔记 | Notes", count_rows(conn, "SELECT COUNT(*) FROM research_notes"))
    col4.metric("市场问题 | Questions", count_rows(conn, "SELECT COUNT(*) FROM market_questions"))


def main() -> None:
    apply_app_style()
    conn = ensure_db()
    render_overview(conn)
    tabs = st.tabs(
        [
            "健康 Health",
            "数据源 Sources",
            "新信号 New",
            "业务解读 Intelligence",
            "竞品 Watch",
            "竞品矩阵 Matrix",
            "复核 Queue",
            "笔记 Notes",
            "问题 Questions",
            "支付轨道 Payment Rails",
            "周报 Weekly Notes",
            "能力 Capability",
            "护栏 Guardrails",
        ]
    )
    with tabs[0]:
        render_deployment_health(conn)
    with tabs[1]:
        render_sources(conn)
    with tabs[2]:
        render_new_signals(conn)
    with tabs[3]:
        render_business_intelligence(conn)
    with tabs[4]:
        render_competitor_watch(conn)
    with tabs[5]:
        render_competitor_matrix(conn)
    with tabs[6]:
        render_review_queue(conn)
    with tabs[7]:
        render_research_notes(conn)
    with tabs[8]:
        render_market_questions(conn)
    with tabs[9]:
        render_payment_rails(conn)
    with tabs[10]:
        render_brief_draft(conn)
    with tabs[11]:
        render_capability_tracker(conn)
    with tabs[12]:
        render_guardrails()


if __name__ == "__main__":
    main()
