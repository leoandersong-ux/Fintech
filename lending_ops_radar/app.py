"""Streamlit personal research dashboard for Zambia Digital Lending Ops Radar."""

from __future__ import annotations

import html
import json
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
from lending_ops_radar.competitor_intelligence import (
    build_competitor_event_rows,
    build_competitor_universe,
    build_policy_impact_rows,
    grouped_competitor_counts,
)
from lending_ops_radar.intelligence import (
    assessment_table_rows,
    build_assessments,
    coverage_gaps,
    operating_lane_rows,
    top_interpretive_findings,
)
from lending_ops_radar.competitor_matrix import build_product_matrix, render_matrix_markdown
from lending_ops_radar.pipeline import DEFAULT_SOURCES, connect, init_db, load_sources, upsert_sources
from lending_ops_radar.quality import build_quality_rows, summary_counts
from lending_ops_radar.reading_brief import build_reading_brief
from lending_ops_radar.snapshot_exporter import DEFAULT_OUTPUT as DEFAULT_SNAPSHOT
from lending_ops_radar.trends import market_voice_rows, source_trend_rows, trend_rows, weekly_action_rows
from lending_ops_radar.version import APP_VERSION, APP_VERSION_LABEL


st.set_page_config(page_title=f"个人研究雷达 {APP_VERSION}", layout="wide")

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
    .brief-panel {
        background: #fbfcf9;
        border: 1px solid #dfe7dc;
        border-radius: 8px;
        padding: 1rem 1.05rem;
        margin: 0.35rem 0 0.9rem 0;
    }
    .brief-panel h3 {
        font-size: 1.08rem;
        margin: 0 0 0.55rem 0;
    }
    .brief-card {
        background: #ffffff;
        border: 1px solid #d8e0db;
        border-radius: 8px;
        padding: 0.92rem 1rem;
        min-height: 168px;
        margin-bottom: 0.75rem;
    }
    .brief-card strong {
        color: #153a32;
    }
    .brief-index {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.55rem;
        height: 1.55rem;
        border-radius: 999px;
        background: #eaf2ed;
        color: #153a32;
        font-weight: 700;
        margin-right: 0.35rem;
    }
    .brief-meta {
        color: #64736c;
        font-size: 0.86rem;
        margin-top: 0.45rem;
    }
    .brief-action {
        background: #fff8ea;
        border: 1px solid #ead8a8;
        border-radius: 8px;
        padding: 0.72rem 0.85rem;
        margin-bottom: 0.65rem;
    }
    .brief-gap {
        border-left: 4px solid #b5653f;
        background: #fffaf6;
        border-radius: 0 8px 8px 0;
        padding: 0.68rem 0.85rem;
        margin-bottom: 0.55rem;
    }
    .landscape-hero {
        background: #f7fbf8;
        border: 1px solid #d8e5dc;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        margin: 0.4rem 0 1rem 0;
    }
    .tier-card {
        background: #ffffff;
        border: 1px solid #dce4df;
        border-radius: 8px;
        padding: 0.88rem 0.95rem;
        min-height: 225px;
        margin-bottom: 0.75rem;
    }
    .tier-pill {
        display: inline-block;
        background: #eaf2ed;
        color: #153a32;
        border-radius: 999px;
        padding: 0.16rem 0.55rem;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .event-card {
        border-left: 4px solid #2f6f61;
        background: #ffffff;
        border-radius: 0 8px 8px 0;
        border-top: 1px solid #dce4df;
        border-right: 1px solid #dce4df;
        border-bottom: 1px solid #dce4df;
        padding: 0.78rem 0.92rem;
        margin-bottom: 0.65rem;
    }
    .policy-card {
        background: #fffaf6;
        border: 1px solid #ecd6c8;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        min-height: 250px;
        margin-bottom: 0.75rem;
    }
    .field-chip {
        display: inline-block;
        border: 1px solid #cfd9d4;
        background: #fbfcfb;
        border-radius: 999px;
        padding: 0.12rem 0.5rem;
        margin: 0.12rem 0.15rem 0.12rem 0;
        font-size: 0.78rem;
        color: #47564f;
    }
    .compact-divider {
        border-top: 1px solid #e1e7e3;
        margin: 0.9rem 0;
    }
    .language-banner {
        background: #153a32;
        border: 1px solid #214f45;
        border-radius: 8px;
        color: #f5fbf8;
        padding: 0.85rem 1rem;
        margin: 0 0 0.7rem 0;
    }
    .language-banner strong {
        color: #ffffff;
        font-size: 1rem;
    }
    .language-banner span {
        color: #cfe3db;
        font-size: 0.94rem;
    }
</style>
"""

DEFAULT_UI_LANGUAGE = "zh"
LANGUAGE_NAMES = {"zh": "中文", "en": "English"}

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
    "lane_key": "能力线ID | Lane ID",
    "lane_cn": "迭代线 | Lane",
    "lane_en": "Lane | EN",
    "evidence_count": "证据数 | Evidence",
    "high_impact_count": "高影响数 | High Impact",
    "medium_impact_count": "中影响数 | Medium Impact",
    "priority_cn": "推进优先级 | Priority",
    "priority_en": "Priority | EN",
    "why_cn": "业务意义 | Why It Matters",
    "why_en": "Why It Matters | EN",
    "next_action_cn": "下一步动作 | Next Action",
    "next_action_en": "Next Action | EN",
    "theme_key": "主题ID | Theme ID",
    "theme_cn": "主题 | Theme",
    "theme_en": "Theme | EN",
    "business_read_cn": "业务解读 | Business Read",
    "business_read_en": "Business Read | EN",
    "action_cn": "建议动作 | Action",
    "action_en": "Action | EN",
    "current_count": "本窗口 | Current",
    "previous_count": "上一窗口 | Previous",
    "delta": "变化 | Change",
    "direction_cn": "方向 | Direction",
    "direction_en": "Direction | EN",
    "interpretation_cn": "趋势解读 | Trend Read",
    "interpretation_en": "Trend Read | EN",
    "window_days": "窗口天数 | Window Days",
    "anchor_date": "锚定日期 | Anchor Date",
    "action_area_cn": "行动领域 | Action Area",
    "action_area_en": "Action Area | EN",
    "trigger_cn": "触发依据 | Trigger",
    "trigger_en": "Trigger | EN",
    "recommended_action_cn": "建议动作 | Recommended Action",
    "recommended_action_en": "Recommended Action | EN",
    "owner_cn": "负责人 | Owner",
    "owner_en": "Owner | EN",
    "priority_score": "行动分 | Action Score",
    "success_rate": "成功率 | Success Rate",
    "status_cn": "状态 | Status",
    "status_en": "Status | EN",
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


REVIEW_DECISIONS = {
    "reviewed": "保留为 reviewed | Keep reviewed",
    "brief_candidate": "加入周报候选 | Add to brief candidate",
    "needs_source_review": "需要回源 | Needs source review",
    "background": "背景保留 | Keep as background",
    "rejected": "排除 rejected | Reject",
}

ACTION_TEMPLATES = {
    "fees": "回源核对 APR、服务费、逾期费、还款示例和披露位置。| Source-check APR, service fees, late fees, repayment examples, and disclosure placement.",
    "disbursement": "回源核对放款、还款、失败交易、对账和移动钱/银行轨道依赖。| Source-check payout, repayment, failed transactions, reconciliation, and mobile-money/bank rail dependency.",
    "repayment": "回源确认还款频率、扣款方式、宽限期、逾期处理和客户解释口径。| Source-check repayment frequency, deduction method, grace period, late handling, and borrower-facing explanation.",
    "privacy": "回源阅读隐私、权限、账户删除和投诉入口；不要把页面措辞直接当作合规结论。| Source-review privacy, permissions, account deletion, and complaint routes; do not treat page wording as a compliance conclusion.",
    "complaint": "核对投诉入口、处理时限、证据留存、升级路径和重复问题复盘机制。| Check complaint intake, timelines, evidence retention, escalation, and repeat-issue review.",
    "collections": "核对催收话术、触达频率、联系人使用、争议处理和隐私边界。| Check collections scripts, contact frequency, contact-person use, dispute handling, and privacy boundaries.",
    "fraud": "核对身份、设备、钱包、放款和客服环节的欺诈暴露点。| Check fraud exposure across identity, device, wallet, payout, and support flows.",
    "regulatory": "回源确认文件日期、适用范围和对产品/支付/客服流程的潜在影响。| Source-check document date, scope, and possible impact on product, payment, or support processes.",
    "competitor_change": "回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。| Source-review limit, tenor, fees, speed promise, payment/payout path, and support/privacy route; keep as public competitor signal.",
    "news_signal": "作为市场/舆情背景保留，除非能连接到具体运营流程。| Keep as market/sentiment context unless it connects to a concrete operating process.",
}


def current_language() -> str:
    language = st.session_state.get("ui_language", DEFAULT_UI_LANGUAGE)
    return "en" if language == "en" else "zh"


def ui_text(cn: str, en: str) -> str:
    return en if current_language() == "en" else cn


def split_bilingual_text(value: object) -> str:
    text = "" if value is None else str(value)
    if " | " not in text:
        return text
    left, right = text.split(" | ", 1)
    return right.strip() if current_language() == "en" else left.strip()


def split_bilingual_label(value: object) -> str:
    text = "" if value is None else str(value)
    if current_language() == "en" and text.endswith(" | EN"):
        return text[:-5].strip()
    if current_language() == "zh" and text.endswith(" | CN"):
        return text[:-5].strip()
    return split_bilingual_text(text)


def language_column(base: str) -> str:
    return f"{base}_en" if current_language() == "en" else f"{base}_cn"


def localized_label_map() -> dict[str, str]:
    return {column: split_bilingual_label(label) for column, label in COLUMN_LABELS.items()}


def localize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    localized = df.copy()
    columns = list(localized.columns)
    drops: list[str] = []
    for column in columns:
        if column.endswith("_cn"):
            base = column[:-3]
            twin = f"{base}_en"
            if twin in columns:
                if current_language() == "en":
                    drops.append(column)
        elif column.endswith("_en"):
            base = column[:-3]
            twin = f"{base}_cn"
            if twin in columns:
                if current_language() == "zh":
                    drops.append(column)
    if drops:
        localized = localized.drop(columns=drops, errors="ignore")
    return localized


def render_language_switcher() -> None:
    if "ui_language" not in st.session_state:
        st.session_state["ui_language"] = DEFAULT_UI_LANGUAGE
    is_english = current_language() == "en"
    col_text, col_button = st.columns([0.74, 0.26])
    with col_text:
        st.markdown(
            f"""
            <div class="language-banner">
                <strong>{ui_text("当前阅读模式：中文", "Reading mode: English")}</strong><br>
                <span>{ui_text("页面默认只显示中文，避免中英并排造成信息噪音。需要英文阅读时，点击右侧按钮切换为纯英文界面。", "This view shows English-only labels and interpretation text. Use the button on the right to switch back to Chinese.")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_button:
        if st.button(
            "ENGLISH VERSION" if not is_english else "切换中文版本",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["ui_language"] = "en" if not is_english else "zh"
            st.rerun()


def apply_app_style() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def title_pair(cn: str, en: str) -> str:
    return ui_text(cn, en)


def section_header(cn: str, en: str, note_cn: str = "", note_en: str = "") -> None:
    st.markdown(f"### {title_pair(cn, en)}")
    if note_cn or note_en:
        st.markdown(
            f'<div class="section-note">{ui_text(note_cn, note_en)}</div>',
            unsafe_allow_html=True,
        )


def looks_question_garbled(value: object) -> bool:
    text = "" if value is None else str(value)
    if not text:
        return False
    question_count = text.count("?")
    return "????" in text or (question_count >= 6 and question_count / max(len(text), 1) > 0.18)


def readable_text(value: object, fallback: str | None = None) -> str:
    fallback = fallback or ui_text("历史备注存在编码损坏，需回源复核。", "Historical note has encoding loss; review source.")
    text = "" if value is None else str(value)
    if looks_question_garbled(text):
        return fallback
    return split_bilingual_text(text)


def readable_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.select_dtypes(include=["object"]).columns:
        cleaned[column] = cleaned[column].map(readable_text)
    return cleaned


def display_df(df: pd.DataFrame, **kwargs: object) -> None:
    cleaned = readable_dataframe(df)
    cleaned = localize_dataframe_columns(cleaned)
    st.dataframe(cleaned.rename(columns=localized_label_map()), use_container_width=True, hide_index=True, **kwargs)


def load_dashboard_snapshot() -> dict[str, object]:
    if not DEFAULT_SNAPSHOT.exists():
        return {}
    try:
        return json.loads(DEFAULT_SNAPSHOT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def snapshot_list(snapshot: dict[str, object], key: str) -> list[dict[str, object]]:
    value = snapshot.get(key)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def public_app_listing_candidates() -> list[dict[str, object]]:
    watchlist_path = Path(__file__).with_name("watchlist.competitors.json")
    if not watchlist_path.exists():
        return []
    try:
        sources = json.loads(watchlist_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    candidates: list[dict[str, object]] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_type = str(source.get("source_type", "")).lower()
        name = str(source.get("name", "")).lower()
        if source_type == "public_app_listing" or "google play" in name:
            candidates.append(
                {
                    "source_id": source.get("source_id", ""),
                    "name": source.get("name", ""),
                    "enabled": source.get("enabled", False),
                    "category": source.get("category", ""),
                    "url": source.get("url", ""),
                    "compliance_notes": source.get("compliance_notes", ""),
                }
            )
    return candidates


def expanded_watchlist_candidates() -> list[dict[str, object]]:
    watchlist_path = Path(__file__).with_name("watchlist.competitors.expanded.json")
    if not watchlist_path.exists():
        return []
    try:
        sources = json.loads(watchlist_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return [item for item in sources if isinstance(item, dict)]


def localized_value(row: dict[str, object] | pd.Series, base: str) -> str:
    preferred = language_column(base)
    fallback = f"{base}_cn" if preferred.endswith("_en") else f"{base}_en"
    try:
        value = row.get(preferred, "")  # type: ignore[attr-defined]
        if not value:
            value = row.get(fallback, "")  # type: ignore[attr-defined]
    except Exception:
        value = ""
    return readable_text(value)


def safe_html(value: object) -> str:
    return html.escape(readable_text(value), quote=True)


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


def action_template_for(classification: object) -> str:
    return ACTION_TEMPLATES.get(
        str(classification or ""),
        "回源复核，并补写一条个人解释笔记。| Review the source and add one personal interpretation note.",
    )


def option_label(mapping: dict[str, str], value: object) -> str:
    return readable_text(mapping.get(str(value), str(value)))


def append_review_note(existing: object, addition: str) -> str:
    base = "" if looks_question_garbled(existing) else str(existing or "").strip()
    if not base:
        return addition
    if addition in base:
        return base
    return f"{base}\n{addition}"


def apply_review_decision(
    conn: sqlite3.Connection,
    signal_id: int,
    decision: str,
    classification: object,
    existing_notes: object,
    existing_action: object,
) -> None:
    template = readable_text(action_template_for(classification))
    action = "" if looks_question_garbled(existing_action) else str(existing_action or "").strip()
    action = action or template
    note_suffix = f"{APP_VERSION} quick decision: {readable_text(REVIEW_DECISIONS.get(decision, decision))}."
    if decision == "reviewed":
        update_review(conn, signal_id, "reviewed", 2, append_review_note(existing_notes, note_suffix), action)
    elif decision == "brief_candidate":
        update_review(conn, signal_id, "reviewed", 1, append_review_note(existing_notes, note_suffix), f"{ui_text('周报候选', 'Brief candidate')}: {action}")
    elif decision == "needs_source_review":
        update_review(conn, signal_id, "new", 1, append_review_note(existing_notes, note_suffix), f"{ui_text('需要回源复核', 'Needs source review')}: {template}")
    elif decision == "background":
        update_review(conn, signal_id, "reviewed", 3, append_review_note(existing_notes, note_suffix), action)
    elif decision == "rejected":
        update_review(
            conn,
            signal_id,
            "rejected",
            3,
            append_review_note(existing_notes, note_suffix),
            ui_text("排除：当前信号对个人研究价值不足或重复。", "Rejected: low value or duplicate for this personal research workflow."),
        )


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
    snapshot = load_dashboard_snapshot()
    snapshot_generated = readable_text(snapshot.get("generated_at", "")) if snapshot else "N/A"
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("数据库", "Database"), f"{db_size} MB")
    col2.metric(title_pair("信号", "Signals"), count_rows(conn, "SELECT COUNT(*) FROM signals"))
    col3.metric(title_pair("已复核", "Reviewed"), count_rows(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'reviewed'"))
    col4.metric(title_pair("快照", "Snapshot"), ui_text("可用", "Available") if snapshot else ui_text("缺失", "Missing"))
    st.caption(f"{title_pair('最近来源运行', 'Last Source Run')}: {latest_source or 'N/A'} · {title_pair('快照生成', 'Snapshot Generated')}: {snapshot_generated}")

    st.markdown(f"#### {title_pair('部署检查', 'Deployment Checks')}")
    display_df(pd.DataFrame(deployment_checks(conn)))

    st.markdown(f"#### {title_pair('节点同步边界', 'Milestone Sync Boundary')}")
    st.markdown(
        f"""
        <div class="section-note">
        {ui_text("节点同步只包含 fintech 研究平台文件、SQLite reviewed data、生成的 briefs 和部署文件；不包含无关商机项目资产、PDF/DOCX 渲染物、私人借款人数据或任何 secret。", "Milestone sync includes only fintech research platform files, reviewed SQLite data, generated briefs, and deployment files. It excludes unrelated opportunity-radar assets, PDF/DOCX render artifacts, private borrower data, and secrets.")}
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
    if st.button(title_pair("初始化/刷新来源配置", "Initialize / Refresh Source Config")):
        upsert_sources(conn, load_sources(DEFAULT_SOURCES))
        st.success(ui_text("来源配置已刷新。", "Source config refreshed."))
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

    st.markdown(f"#### {title_pair('来源健康度', 'Source Health')}")
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
        st.success(ui_text("当前没有待审信号。", "No new signals in the review queue."))
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
                    "quality_tier_en",
                    "recommended_use_cn",
                    "recommended_use_en",
                    "source_link",
                ]
            ]
        )
        with st.expander(title_pair("查看原始新信号", "Raw New Signals")):
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
    lane_rows = operating_lane_rows(assessments)

    high_count = sum(1 for item in assessments if item["impact_level"] == "high")
    medium_count = sum(1 for item in assessments if item["impact_level"] == "medium")
    domains = sorted({str(item["domain_cn"]) for item in assessments})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("已解读信号", "Interpreted Signals"), len(assessments))
    col2.metric(title_pair("高潜在影响", "High Potential Impact"), high_count)
    col3.metric(title_pair("中潜在影响", "Medium Potential Impact"), medium_count)
    col4.metric(title_pair("影响域", "Impact Domains"), len(domains))

    st.markdown(f"#### {title_pair('V0.7 五条迭代线行动板', 'V0.7 Five-Lane Action Board')}")
    lane_df = pd.DataFrame(lane_rows)
    if lane_df.empty:
        st.info(ui_text("暂无可用于行动板的解读信号。", "No interpreted signals available for the action board yet."))
    else:
        lane_cols = [
            language_column("lane"),
            "evidence_count",
            "high_impact_count",
            "medium_impact_count",
            language_column("priority"),
            language_column("why"),
            language_column("next_action"),
        ]
        display_df(lane_df[lane_cols])

    st.markdown(f"#### {title_pair('本周最值得看', 'Priority Reads')}")
    quality_df = pd.DataFrame(quality_rows)
    if quality_df.empty:
        st.info(ui_text("还没有质量评分。", "No quality scores yet."))
    else:
        q_col1, q_col2, q_col3 = st.columns(3)
        counts = summary_counts(quality_rows)
        q_col1.metric(title_pair("优先阅读", "Priority Reads"), counts["tier"].get("优先阅读", 0))
        q_col2.metric(title_pair("周报候选", "Brief Candidates"), counts["tier"].get("周报候选", 0))
        q_col3.metric(title_pair("平均候选分", "Average Score"), f"{round(quality_df['brief_candidate_score'].mean())}/100")
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
                    "quality_tier_en",
                    "recommended_use_cn",
                    "recommended_use_en",
                    "quality_reason_cn",
                    "quality_reason_en",
                    "source_link",
                ]
            ]
        )

    st.markdown(f"#### {title_pair('关键判断', 'Key Interpretive Findings')}")
    for item in findings:
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>{ui_text(item['finding_cn'], item['finding_en'])}</strong><br><br>
                {ui_text(item['why_cn'], item['why_en'])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(f"#### {title_pair('小微贷款业务影响矩阵', 'Micro-lending Impact Matrix')}")
    impact_df = pd.DataFrame(assessment_table_rows(assessments, limit=50))
    if impact_df.empty:
        st.info(ui_text("还没有已复核信号可解读。", "No reviewed signals available for interpretation."))
    else:
        st.markdown(
            f"""
            <div class="section-note">
            {ui_text("这里按卡片阅读，不再用宽表格。每张卡片只回答一个问题：这条公开信号会影响小微贷款业务的哪个流程、为什么重要、下一步该回源确认什么。", "This is card-based instead of a wide table. Each card explains which lending process the public signal may affect, why it matters, and what to verify next.")}
            </div>
            """,
            unsafe_allow_html=True,
        )
        for index, item in enumerate(impact_df.head(12).to_dict("records"), start=1):
            with st.container(border=True):
                st.markdown(f"**{index}. {ui_text(readable_text(item['domain_cn']), readable_text(item['domain_en']))}**")
                st.caption(f"{ui_text('等级', 'Level')}: {readable_text(item['impact_level'])} · Signal ID: {readable_text(item['signal_id'])}")
                st.markdown(f"**{title_pair('信号', 'Signal')}:** {readable_text(item['signal'])}")
                st.markdown(f"**{title_pair('对小微贷款业务的影响', 'Micro-lending impact')}:** {ui_text(readable_text(item['lending_impact_cn']), readable_text(item['lending_impact_en']))}")
                st.markdown(f"**{title_pair('建议动作', 'Recommended action')}:** {ui_text(readable_text(item['recommended_actions_cn']), readable_text(item['recommended_actions_en']))}")
                st.markdown(f"**{title_pair('待验证问题', 'Follow-up question')}:** {ui_text(readable_text(item['follow_up_questions_cn']), readable_text(item['follow_up_questions_en']))}")
                st.markdown(f"[{title_pair('来源', 'Source')}]({readable_text(item['source_link'])})")
        with st.expander(title_pair("查看完整结构化表格", "Full Structured Table")):
            display_df(
                impact_df[
                    [
                        "signal_id",
                        "domain_cn",
                        "domain_en",
                        "impact_level",
                        "signal",
                        "lending_impact_cn",
                        "lending_impact_en",
                        "affected_processes_cn",
                        "affected_processes_en",
                        "recommended_actions_cn",
                        "recommended_actions_en",
                        "follow_up_questions_cn",
                        "follow_up_questions_en",
                        "source_link",
                    ]
                ]
            )

    st.markdown(f"#### {title_pair('情报覆盖缺口', 'Intelligence Coverage Gaps')}")
    gap_df = pd.DataFrame(gaps)
    display_df(gap_df[["area_cn", "coverage_cn", "gap_cn", "next_source_cn", "area_en", "coverage_en", "gap_en", "next_source_en"]])


def render_market_voice(conn: sqlite3.Connection) -> None:
    section_header(
        "市场声音",
        "Market Voice",
        "把投诉、公开评论候选、竞品 App 层和客服/支付摩擦放在一个阅读面里，先看主题和业务含义，再回源。",
        "Read complaints, public-review candidates, competitor app-layer signals, and support/payment friction by theme before going back to sources.",
    )
    rows = market_voice_rows(conn, limit=50)
    snapshot = load_dashboard_snapshot()
    if not rows:
        rows = snapshot_list(snapshot, "market_voice")
    candidates = public_app_listing_candidates()
    enabled_candidates = [item for item in candidates if item.get("enabled")]
    theme_count = len({str(row.get("theme_key", "")) for row in rows})
    high_risk = sum(1 for row in rows if row.get("risk_level") == "high")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("市场声音信号", "Market Voice Signals"), len(rows))
    col2.metric(title_pair("主题数", "Themes"), theme_count)
    col3.metric(title_pair("高风险", "High Risk"), high_risk)
    col4.metric(title_pair("App 候选源", "App Candidates"), f"{len(enabled_candidates)}/{len(candidates)}")

    st.markdown(
        f"""
        <div class="section-note">
        {ui_text("Google Play / public app listing 仍按候选源处理：默认不启用，只有在确认只读取公开页面、不过度采集评论身份信息后再进入自动化。", "Google Play / public app listings remain candidate sources: disabled by default until public-page boundaries and review-identity minimization are confirmed.")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not rows:
        st.info(ui_text("暂无市场声音数据。", "No market-voice rows yet."))
        return

    st.markdown(f"#### {title_pair('主题卡片', 'Theme Cards')}")
    for index, row in enumerate(rows[:8], start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {localized_value(row, 'theme')}**")
            st.caption(
                f"{readable_text(row.get('source_name', ''))} · {readable_text(row.get('classification', ''))} · {readable_text(row.get('risk_level', ''))}"
            )
            st.markdown(f"**{title_pair('信号', 'Signal')}:** {readable_text(row.get('signal', ''))}")
            st.markdown(f"**{title_pair('业务解读', 'Business Read')}:** {localized_value(row, 'business_read')}")
            st.markdown(f"**{title_pair('建议动作', 'Action')}:** {localized_value(row, 'action')}")
            source_link = readable_text(row.get("source_link", ""))
            if source_link:
                st.markdown(f"[{title_pair('来源', 'Source')}]({source_link})")

    with st.expander(title_pair("公开 App Listing 候选源", "Public App Listing Candidates")):
        display_df(pd.DataFrame(candidates))
    with st.expander(title_pair("完整市场声音表", "Full Market Voice Table")):
        display_df(
            pd.DataFrame(rows)[
                [
                    "signal_id",
                    "theme_cn",
                    "theme_en",
                    "source_name",
                    "signal",
                    "classification",
                    "risk_level",
                    "review_status",
                    "business_read_cn",
                    "business_read_en",
                    "action_cn",
                    "action_en",
                    "source_link",
                ]
            ]
        )


def render_trend_changes(conn: sqlite3.Connection) -> None:
    section_header(
        "趋势变化",
        "Trend Changes",
        "用最近一个数据窗口和上一个窗口做轻量比较，帮助判断哪些主题在变多、哪些来源需要处理。",
        "Compare the latest data window with the previous one to see which themes are rising and which sources need attention.",
    )
    rows = trend_rows(conn)
    source_rows = source_trend_rows(conn)
    snapshot = load_dashboard_snapshot()
    if not rows:
        rows = snapshot_list(snapshot, "trend_rows")
    if not source_rows:
        source_rows = snapshot_list(snapshot, "source_trends")

    rising = sum(1 for row in rows if int(row.get("delta", 0)) > 0)
    falling = sum(1 for row in rows if int(row.get("delta", 0)) < 0)
    needs_attention = sum(1 for row in source_rows if row.get("status_cn") == "需要处理" or row.get("status_en") == "Needs attention")
    anchor = rows[0].get("anchor_date", "N/A") if rows else "N/A"
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("趋势主题", "Trend Themes"), len(rows))
    col2.metric(title_pair("上升主题", "Rising Themes"), rising)
    col3.metric(title_pair("下降主题", "Falling Themes"), falling)
    col4.metric(title_pair("需处理来源", "Sources Needing Attention"), needs_attention)
    st.caption(f"{title_pair('趋势锚定日期', 'Trend Anchor Date')}: {anchor}")

    if not rows:
        st.info(ui_text("暂无趋势数据。", "No trend data yet."))
        return

    chart_df = pd.DataFrame(rows)[["theme_cn", "theme_en", "current_count", "previous_count"]].copy()
    chart_df["theme"] = chart_df[language_column("theme")]
    st.bar_chart(chart_df.set_index("theme")[["previous_count", "current_count"]])

    st.markdown(f"#### {title_pair('趋势解读', 'Trend Reads')}")
    for row in rows[:8]:
        with st.container(border=True):
            st.markdown(f"**{localized_value(row, 'theme')}**")
            st.caption(
                f"{title_pair('本窗口', 'Current')}: {row.get('current_count', 0)} · "
                f"{title_pair('上一窗口', 'Previous')}: {row.get('previous_count', 0)} · "
                f"{title_pair('变化', 'Change')}: {int(row.get('delta', 0)):+d}"
            )
            st.markdown(f"**{title_pair('判断', 'Read')}:** {localized_value(row, 'interpretation')}")
            st.markdown(f"**{title_pair('动作', 'Action')}:** {localized_value(row, 'action')}")

    with st.expander(title_pair("来源健康趋势", "Source Health Trends")):
        display_df(pd.DataFrame(source_rows))
    with st.expander(title_pair("完整趋势表", "Full Trend Table")):
        display_df(pd.DataFrame(rows))


def render_weekly_actions(conn: sqlite3.Connection) -> None:
    section_header(
        "本周行动",
        "Weekly Actions",
        "把趋势和市场声音压缩成个人研究动作清单，避免周报只停留在信息摘要。",
        "Compress trends and market voice into personal research actions so weekly notes do not stop at summaries.",
    )
    rows = weekly_action_rows(conn, limit=8)
    snapshot = load_dashboard_snapshot()
    if not rows:
        rows = snapshot_list(snapshot, "weekly_actions")
    if not rows:
        st.info(ui_text("暂无本周行动建议。", "No weekly actions yet."))
        return

    top_priority = sum(1 for row in rows if row.get("priority_cn") == "本周优先" or row.get("priority_en") == "This-week priority")
    total_evidence = sum(int(row.get("evidence_count", 0)) for row in rows)
    positive_delta = sum(max(int(row.get("delta", 0)), 0) for row in rows)
    col1, col2, col3 = st.columns(3)
    col1.metric(title_pair("行动项", "Actions"), len(rows))
    col2.metric(title_pair("本周优先", "This-week Priority"), top_priority)
    col3.metric(title_pair("证据数", "Evidence Count"), total_evidence)
    st.caption(f"{title_pair('正向变化合计', 'Positive Change Total')}: {positive_delta:+d}")

    for index, row in enumerate(rows, start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {localized_value(row, 'action_area')} · {localized_value(row, 'priority')}**")
            st.markdown(f"**{title_pair('触发依据', 'Trigger')}:** {localized_value(row, 'trigger')}")
            st.markdown(f"**{title_pair('建议动作', 'Recommended Action')}:** {localized_value(row, 'recommended_action')}")
            st.caption(f"{title_pair('负责人', 'Owner')}: {localized_value(row, 'owner')}")

    with st.expander(title_pair("完整行动表", "Full Action Table")):
        display_df(pd.DataFrame(rows))


def _chips_from_csv(value: object) -> str:
    chips = []
    for item in str(value or "").split(","):
        item = item.strip()
        if item:
            chips.append(f'<span class="field-chip">{safe_html(item)}</span>')
    return " ".join(chips)


def render_competitor_landscape() -> None:
    snapshot = load_dashboard_snapshot()
    universe = snapshot_list(snapshot, "competitor_universe") or build_competitor_universe()
    policy_rows = snapshot_list(snapshot, "policy_impact_rows") or build_policy_impact_rows()
    event_rows = snapshot_list(snapshot, "competitor_event_rows") or build_competitor_event_rows()
    expanded_sources = expanded_watchlist_candidates()
    counts = grouped_competitor_counts(universe)

    section_header(
        "竞品地图与政策冲击",
        "Competitor Map and Policy Impact",
        "这一页按研究问题重排：先看市场里有哪些玩家，再看政策会压到哪些字段，最后看公司、产品、财报/社会和舆论层面的事件入口。",
        "This view is organized by research question: who is in the market, which competitor fields policy can pressure, and which company/product/financial/social/voice events to monitor.",
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("竞品/生态候选", "Competitor / Ecosystem Candidates"), len(universe))
    col2.metric(title_pair("核心数字贷款", "Core Digital Lenders"), counts.get("core_digital_lending", 0))
    col3.metric(title_pair("相邻微贷/薪资贷", "Adjacent MFIs / Payroll"), counts.get("adjacent_microfinance_payroll", 0))
    col4.metric(title_pair("政策影响主题", "Policy Impact Themes"), len(policy_rows))

    st.markdown(
        f"""
        <div class="landscape-hero">
            <strong>{title_pair("阅读方式", "How to read this")}</strong><br>
            {ui_text(
                "不要把所有玩家放在同一张表里硬比较。先区分 App-first 小额贷款、传统/薪资/微贷机构、支付轨道和生态伙伴，再看每类玩家受费用披露、数据隐私、投诉处理、支付失败和公司层变化的影响。",
                "Do not force every player into one flat comparison table. Separate app-first lenders, traditional/payroll/MFI players, payment rails, and ecosystem partners, then read how fee disclosure, privacy, complaints, failed payments, and company-level changes affect each group."
            )}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"#### {title_pair('竞品覆盖地图', 'Competitor Coverage Map')}")
    tiers = [
        ("core_digital_lending", title_pair("核心数字贷款 App", "Core Digital Lending Apps")),
        ("adjacent_microfinance_payroll", title_pair("相邻微贷/薪资贷", "Adjacent MFIs / Payroll Lenders")),
        ("rails_ecosystem", title_pair("支付轨道/生态伙伴", "Payment Rails / Ecosystem")),
    ]
    for tier_key, tier_title in tiers:
        tier_rows = [row for row in universe if row.get("tier_key") == tier_key]
        if not tier_rows:
            continue
        st.markdown(f"##### {tier_title}")
        columns = st.columns(3)
        for index, row in enumerate(tier_rows):
            with columns[index % 3]:
                source_links = str(row.get("source_links", ""))
                first_link = source_links.split(" ; ")[0] if source_links else ""
                source_html = (
                    f'<a href="{safe_html(first_link)}" target="_blank">{title_pair("来源候选", "Source candidate")}</a>'
                    if first_link
                    else ""
                )
                st.markdown(
                    f"""
                    <div class="tier-card">
                        <span class="tier-pill">{safe_html(localized_value(row, "watch_priority"))}</span><br>
                        <strong>{safe_html(row.get("institution", ""))}</strong>
                        <div class="brief-meta">{safe_html(localized_value(row, "tier"))}</div>
                        <div class="compact-divider"></div>
                        {safe_html(localized_value(row, "product_focus"))}<br><br>
                        <strong>{title_pair("观察重点", "Watch")}</strong><br>
                        {safe_html(localized_value(row, "primary_signals"))}<br>
                        <div class="brief-meta">{safe_html(localized_value(row, "evidence_status"))} · {source_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(f"#### {title_pair('政策对竞品字段的影响矩阵', 'Policy-to-Competitor Impact Matrix')}")
    policy_columns = st.columns(2)
    for index, row in enumerate(policy_rows):
        with policy_columns[index % 2]:
            st.markdown(
                f"""
                <div class="policy-card">
                    <strong>{safe_html(localized_value(row, "policy_theme"))}</strong>
                    <div class="brief-meta">
                        {title_pair("受影响候选", "Affected candidates")}: {safe_html(row.get("affected_competitor_count", 0))}
                        · {safe_html(row.get("examples", ""))}
                    </div>
                    <div class="compact-divider"></div>
                    <strong>{title_pair("政策含义", "Policy Meaning")}</strong><br>
                    {safe_html(localized_value(row, "impact"))}<br><br>
                    <strong>{title_pair("观察字段", "Watch Fields")}</strong><br>
                    {_chips_from_csv(row.get("watch_fields", ""))}<br><br>
                    <strong>{title_pair("下一步", "Next")}</strong><br>
                    {safe_html(localized_value(row, "next_action"))}
                    <div class="brief-meta">{safe_html(localized_value(row, "source_anchor"))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(f"#### {title_pair('公司/产品/财报/社会/舆论事件流候选', 'Company, Product, Financial, Social, and Voice Event Candidates')}")
    event_columns = st.columns(2)
    for index, row in enumerate(event_rows):
        with event_columns[index % 2]:
            link = row.get("source_link", "")
            source_html = (
                f'<a href="{safe_html(link)}" target="_blank">{title_pair("来源", "Source")}</a>'
                if link
                else ""
            )
            st.markdown(
                f"""
                <div class="event-card">
                    <span class="tier-pill">{safe_html(localized_value(row, "event_type"))}</span><br>
                    <strong>{safe_html(row.get("institution", ""))}</strong><br>
                    {safe_html(localized_value(row, "event"))}
                    <div class="compact-divider"></div>
                    <strong>{title_pair("业务解读", "Business Read")}</strong><br>
                    {safe_html(localized_value(row, "business_read"))}
                    <div class="brief-meta">{source_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander(title_pair("扩展来源候选清单", "Expanded Source Candidate List")):
        if expanded_sources:
            display_df(pd.DataFrame(expanded_sources))
        else:
            st.info(ui_text("尚未创建扩展 watchlist 文件。", "No expanded watchlist file yet."))

    with st.expander(title_pair("结构化竞品地图表", "Structured Competitor Map Table")):
        display_df(pd.DataFrame(universe))


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
    col1.metric(title_pair("竞品源", "Sources"), len(sources))
    col2.metric(title_pair("已启用", "Enabled"), int((sources["enabled"] == 1).sum()) if not sources.empty else 0)
    col3.metric(title_pair("竞品信号", "Signals"), len(signals))
    col4.metric(title_pair("待复核", "New"), int((signals["review_status"] == "new").sum()) if not signals.empty else 0)

    st.markdown(f"#### {title_pair('来源清单', 'Source Watchlist')}")
    display_df(sources)

    st.markdown(f"#### {title_pair('竞品新信号', 'Competitor Signals')}")
    if signals.empty:
        st.info(ui_text("还没有竞品信号。运行启用的 competitor watchlist 源后会出现在这里。", "No competitor signals yet. Run enabled competitor watchlist sources and they will appear here."))
    else:
        display_df(signals)

    st.markdown(f"#### {title_pair('阅读框架', 'Review Lens')}")
    st.markdown(
        f"""
        <div class="section-note">
        {ui_text("复核竞品信号时优先问：额度/期限/费用是否变化？放款和还款依赖什么支付轨道？客服和争议入口是否清晰？是否出现隐私、催收、失败扣款、到账慢等公开主题？", "Review competitor signals through limits, tenor, fees, payment-rail dependency, support/dispute clarity, and public themes such as privacy, collections, failed deductions, and slow payout.")}
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
        st.info(ui_text("还没有竞品矩阵。请先复核 competitor signals。", "No competitor matrix yet. Review competitor signals first."))
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
    col1.metric(title_pair("机构", "Institutions"), institutions)
    col2.metric(title_pair("矩阵行", "Matrix Rows"), len(matrix_df))
    col3.metric(title_pair("平均完整度", "Average Completeness"), f"{round(matrix_df['data_completeness_score'].mean())}/100")
    col4.metric(title_pair("高优先级", "High Priority"), int(matrix_df["matrix_priority_cn"].str.startswith("高").sum()))

    st.markdown(
        f"""
        <div class="section-note">
        {ui_text("完整度分数是“公开研究字段是否被捕捉”的分数，不是产品优劣分数。高优先级代表值得先回源复核，因为它可能影响放款体验、支付轨道、风控权重或隐私/投诉运营。", "Completeness measures captured public research fields, not product quality. High priority means the item deserves source review because it may affect payout experience, payment rails, risk weight, or privacy/dispute operations.")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    product_layer_col = language_column("product_layer")
    limit_tier_col = language_column("limit_tier")
    payment_maturity_col = language_column("payment_maturity")
    speed_tier_col = language_column("speed_tier")
    competitor_positioning_col = language_column("competitor_positioning")
    with filter_col1:
        focus = st.multiselect(
            title_pair("筛选机构", "Filter Institutions"),
            sorted(matrix_df["institution"].unique().tolist()),
            default=sorted(matrix_df["institution"].unique().tolist()),
        )
    with filter_col2:
        layer_focus = st.multiselect(
            title_pair("产品层", "Product Layer"),
            sorted(matrix_df[product_layer_col].unique().tolist()),
            default=sorted(matrix_df[product_layer_col].unique().tolist()),
        )
    with filter_col3:
        limit_focus = st.multiselect(
            title_pair("额度档", "Limit Tier"),
            sorted(matrix_df[limit_tier_col].unique().tolist()),
            default=sorted(matrix_df[limit_tier_col].unique().tolist()),
        )
    filtered = matrix_df.copy()
    if focus:
        filtered = filtered[filtered["institution"].isin(focus)]
    if layer_focus:
        filtered = filtered[filtered[product_layer_col].isin(layer_focus)]
    if limit_focus:
        filtered = filtered[filtered[limit_tier_col].isin(limit_focus)]

    st.markdown(f"#### {title_pair('横向比较', 'Comparison Summary')}")
    compare_col1, compare_col2 = st.columns(2)
    with compare_col1:
        display_df(
            filtered.groupby(product_layer_col, dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )
    with compare_col2:
        display_df(
            filtered.groupby(limit_tier_col, dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )

    compare_col3, compare_col4 = st.columns(2)
    with compare_col3:
        display_df(
            filtered.groupby(payment_maturity_col, dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )
    with compare_col4:
        display_df(
            filtered.groupby(speed_tier_col, dropna=False)
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )

    st.markdown(f"#### {title_pair('竞品定位 3.0', 'Competitor Positioning 3.0')}")
    display_df(
        filtered.groupby(competitor_positioning_col, dropna=False)
        .agg(
            rows=("product_or_signal", "count"),
            avg_completeness=("data_completeness_score", "mean"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )

    st.markdown(f"#### {title_pair('产品矩阵', 'Product Matrix')} ({len(filtered)} {ui_text('行', 'rows')})")
    display_cols = [
        "institution",
        "product_or_signal",
        "competitor_positioning_cn",
        "competitor_positioning_en",
        "product_layer_cn",
        "product_layer_en",
        "limit_tier_cn",
        "limit_tier_en",
        "segment_cn",
        "segment_en",
        "limit_amount",
        "tenor_or_repayment",
        "pricing_or_disclosure",
        "speed_tier_cn",
        "speed_tier_en",
        "payment_maturity_cn",
        "payment_maturity_en",
        "support_privacy_maturity_cn",
        "support_privacy_maturity_en",
        "data_completeness_score",
        "matrix_priority_cn",
        "matrix_priority_en",
        "operating_risk_focus_cn",
        "operating_risk_focus_en",
        "gap_flags_cn",
        "gap_flags_en",
        "business_interpretation_cn",
        "business_interpretation_en",
        "next_questions_cn",
        "next_questions_en",
        "source_links",
        "source_status",
    ]
    display_df(filtered[display_cols])

    with st.expander(title_pair("查看原始字段", "Source-linked Details")):
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
    markdown_content = render_matrix_markdown(filtered.to_dict("records"), language=current_language())
    col_a, col_b = st.columns(2)
    col_a.download_button(
        title_pair("下载 CSV 矩阵", "Download CSV Matrix"),
        data=csv_data,
        file_name="lending_ops_competitor_product_matrix.csv",
        mime="text/csv",
    )
    col_b.download_button(
        title_pair("下载 Markdown 矩阵", "Download Markdown Matrix"),
        data=markdown_content,
        file_name="zambia_digital_lending_competitor_product_matrix.md",
        mime="text/markdown",
    )

    st.markdown(f"#### {title_pair('Markdown 预览', 'Markdown Preview')}")
    st.markdown(markdown_content)


def review_workflow_rows(conn: sqlite3.Connection) -> pd.DataFrame:
    return dataframe(
        conn,
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
            s.last_seen_at,
            r.review_status,
            r.priority,
            r.reviewer_notes,
            r.recommended_action
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        WHERE r.review_status != 'rejected'
        ORDER BY r.review_status = 'new' DESC, r.priority ASC, s.last_seen_at DESC
        """,
    )


def render_review_cockpit(conn: sqlite3.Connection) -> None:
    section_header(
        "复核驾驶舱",
        "Review Cockpit",
        "把 v0.3 的质量评分变成实际复核工作流：优先看、套模板、做决定、进入周报候选或回源队列。",
        "Turns v0.3 quality scoring into a real review workflow: prioritize, apply templates, decide, and move items into brief candidates or source-review queue.",
    )
    rows = review_workflow_rows(conn)
    if rows.empty:
        st.info(ui_text("没有可复核信号。", "No reviewable signals."))
        return

    quality_df = pd.DataFrame(build_quality_rows(rows.to_dict("records")))
    quality_df["brief_candidate_score"] = pd.to_numeric(quality_df["brief_candidate_score"], errors="coerce").fillna(0).astype(int)
    quality_df["manual_review_need_score"] = pd.to_numeric(quality_df["manual_review_need_score"], errors="coerce").fillna(0).astype(int)
    rows = rows.copy()
    rows["_merge_signal_id"] = rows["id"].astype(str)
    merged = quality_df.merge(
        rows[
            [
                "id",
                "_merge_signal_id",
                "source_url",
                "item_title",
                "item_url",
                "raw_text",
                "last_seen_at",
                "reviewer_notes",
                "recommended_action",
            ]
        ],
        left_on="signal_id",
        right_on="_merge_signal_id",
        how="left",
    )

    counts = summary_counts(quality_df.to_dict("records"))
    new_count = int((merged["review_status"] == "new").sum())
    candidate_count = int((merged["brief_candidate_score"] >= 70).sum())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("待处理", "New"), new_count)
    col2.metric(title_pair("周报候选", "Brief Candidates"), candidate_count)
    col3.metric(title_pair("优先阅读", "Priority Reads"), counts["tier"].get("优先阅读", 0))
    col4.metric(title_pair("高回源需求", "High Review Need"), int((merged["manual_review_need_score"] >= 72).sum()))

    st.markdown(f"#### {title_pair('优先队列', 'Priority Queue')}")
    queue_cols = [
        "signal_id",
        "signal",
        "classification",
        "risk_level",
        "review_status",
        "priority",
        "brief_candidate_score",
        "manual_review_need_score",
        "quality_tier_cn",
        "quality_tier_en",
        "recommended_use_cn",
        "recommended_use_en",
        "source_link",
    ]
    display_df(merged[queue_cols].head(30))

    st.markdown(f"#### {title_pair('快速复核', 'Quick Review')}")
    selected_id = st.selectbox(
        title_pair("选择信号 ID", "Select Signal ID"),
        merged["signal_id"].astype(str).tolist(),
        format_func=lambda value: f"{value} - {merged[merged['signal_id'].astype(str) == value].iloc[0]['signal'][:90]}",
    )
    selected = merged[merged["signal_id"].astype(str) == selected_id].iloc[0]
    template = action_template_for(selected["classification"])

    with st.container(border=True):
        st.markdown(f"**{readable_text(selected['signal'])}**")
        st.caption(f"{readable_text(selected['source_name'])} · {readable_text(selected['classification'])} · {readable_text(selected['risk_level'])}")
        st.markdown(f"[{title_pair('来源', 'Source')}]({readable_text(selected['source_link'])})")
        st.markdown(f"**{title_pair('质量判断', 'Quality')}:** {ui_text(readable_text(selected['quality_tier_cn']), readable_text(selected.get('quality_tier_en', '')))} · {selected['brief_candidate_score']}/100")
        st.markdown(f"**{title_pair('建议用途', 'Recommended Use')}:** {ui_text(readable_text(selected['recommended_use_cn']), readable_text(selected.get('recommended_use_en', '')))}")
        st.markdown(f"**{title_pair('评分原因', 'Reason')}:** {ui_text(readable_text(selected['quality_reason_cn']), readable_text(selected.get('quality_reason_en', '')))}")
        st.markdown(f"**{title_pair('动作模板', 'Action Template')}:** {readable_text(template)}")
        with st.expander(title_pair("查看原文片段与历史备注", "Raw Text and Existing Notes")):
            st.write(readable_text(selected.get("raw_text", "")))
            st.write(readable_text(selected.get("reviewer_notes", "")))
            st.write(readable_text(selected.get("recommended_action", "")))

    decision_col1, decision_col2, decision_col3, decision_col4, decision_col5 = st.columns(5)
    if decision_col1.button(ui_text("保留 reviewed", "Keep Reviewed"), use_container_width=True):
        apply_review_decision(conn, int(selected["signal_id"]), "reviewed", selected["classification"], selected["reviewer_notes"], selected["recommended_action"])
        st.success(ui_text("已保留为 reviewed。", "Kept as reviewed."))
        st.rerun()
    if decision_col2.button(title_pair("加入周报候选", "Add to Brief"), use_container_width=True):
        apply_review_decision(conn, int(selected["signal_id"]), "brief_candidate", selected["classification"], selected["reviewer_notes"], selected["recommended_action"])
        st.success(ui_text("已加入周报候选。", "Added to brief candidates."))
        st.rerun()
    if decision_col3.button(title_pair("需要回源", "Needs Source Review"), use_container_width=True):
        apply_review_decision(conn, int(selected["signal_id"]), "needs_source_review", selected["classification"], selected["reviewer_notes"], selected["recommended_action"])
        st.warning(ui_text("已标记为需要回源。", "Marked as needing source review."))
        st.rerun()
    if decision_col4.button(title_pair("背景保留", "Keep as Background"), use_container_width=True):
        apply_review_decision(conn, int(selected["signal_id"]), "background", selected["classification"], selected["reviewer_notes"], selected["recommended_action"])
        st.success(ui_text("已作为背景保留。", "Kept as background."))
        st.rerun()
    if decision_col5.button(title_pair("排除", "Reject"), use_container_width=True):
        apply_review_decision(conn, int(selected["signal_id"]), "rejected", selected["classification"], selected["reviewer_notes"], selected["recommended_action"])
        st.success(ui_text("已排除。", "Rejected."))
        st.rerun()

    cockpit_tab1, cockpit_tab2, cockpit_tab3 = st.tabs(
        [title_pair("周报候选", "Brief Pool"), title_pair("待验证问题", "Questions"), title_pair("动作模板", "Templates")]
    )
    with cockpit_tab1:
        brief_pool = merged[(merged["brief_candidate_score"] >= 70) & (merged["review_status"].isin(["reviewed", "briefed"]))]
        if brief_pool.empty:
            st.info(ui_text("暂无周报候选。", "No brief candidates yet."))
        else:
            display_df(
                brief_pool[
                    [
                        "signal_id",
                        "signal",
                        "classification",
                        "risk_level",
                        "brief_candidate_score",
                        "quality_reason_cn",
                        "quality_reason_en",
                        "recommended_action",
                        "source_link",
                    ]
                ]
            )
    with cockpit_tab2:
        questions = dataframe(
            conn,
            """
            SELECT id, area, question, status, current_hypothesis, evidence, updated_at
            FROM market_questions
            ORDER BY status, updated_at DESC
            """,
        )
        display_df(questions)
    with cockpit_tab3:
        template_rows = [
            {"classification": key, "recommended_action": value}
            for key, value in ACTION_TEMPLATES.items()
        ]
        display_df(pd.DataFrame(template_rows))


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
        st.info(ui_text("还没有信号。请先运行 pipeline 或 seed sample records。", "No signals yet. Run the pipeline or seed sample records."))
        return

    selected_id = st.selectbox(title_pair("信号 ID", "Signal ID"), queue["id"].tolist())
    selected = queue[queue["id"] == selected_id].iloc[0]
    with st.container(border=True):
        st.markdown(f"**{selected['item_title']}**")
        st.caption(selected["item_url"] or "")
        st.write(selected["raw_text"])

    status = st.selectbox(
        title_pair("复核状态", "Review Status"),
        ["new", "reviewed", "briefed", "rejected"],
        index=["new", "reviewed", "briefed", "rejected"].index(selected["review_status"]),
        format_func=lambda value: option_label(STATUS_LABELS, value),
    )
    priority = st.slider(title_pair("优先级", "Priority"), min_value=1, max_value=3, value=int(selected["priority"]))
    notes = st.text_area(title_pair("研究备注", "Reviewer Notes"), value=selected["reviewer_notes"] or "")
    action = st.text_area(title_pair("下一步行动", "Recommended Action"), value=selected["recommended_action"] or "")
    if st.button(title_pair("保存复核", "Save Review")):
        update_review(conn, int(selected_id), status, priority, notes, action)
        st.success(ui_text("复核已更新。", "Review updated."))


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
    content = render_brief(rows, current_week_label(), notes, questions, source_health, language=current_language())
    st.download_button(
        title_pair("下载 Markdown 笔记", "Download Markdown Notes"),
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
    signal_options = {title_pair("不关联信号", "No Linked Signal"): None}
    signal_options.update({f"{row.id}: {row.item_title[:90]}": int(row.id) for row in signals.itertuples()})

    st.markdown(f"#### {title_pair('新增笔记', 'Add Note')}")
    selected_signal = st.selectbox(title_pair("可选关联信号", "Optional Linked Signal"), list(signal_options.keys()))
    note_type = st.selectbox(
        title_pair("笔记类型", "Note Type"),
        ["market_observation", "source_quality", "taxonomy_learning", "research_question", "weekly_synthesis", "capability_line"],
        format_func=lambda value: option_label(NOTE_TYPE_LABELS, value),
    )
    title = st.text_input(title_pair("标题", "Title"))
    question = st.text_input(title_pair("市场问题", "Market Question"))
    confidence = st.selectbox(
        title_pair("信心", "Confidence"),
        ["medium", "low", "high"],
        format_func=lambda value: option_label(CONFIDENCE_LABELS, value),
    )
    note = st.text_area(title_pair("笔记", "Note"))
    if st.button(title_pair("保存研究笔记", "Save Research Note")):
        if not title.strip() or not note.strip():
            st.error(ui_text("标题和笔记不能为空。", "Title and note are required."))
        else:
            add_research_note(conn, signal_options[selected_signal], note_type, title, note, question, confidence)
            st.success(ui_text("研究笔记已保存。", "Research note saved."))


def render_market_questions(conn: sqlite3.Connection) -> None:
    section_header(
        "市场问题",
        "Market Questions",
        "让研究围绕问题推进，而不是围绕数据堆积推进。",
        "Use questions to guide the research loop instead of collecting rows for their own sake.",
    )
    if st.button(title_pair("初始化市场问题", "Seed Market Questions")):
        seed_market_questions(conn)
        st.success(ui_text("市场问题已初始化。", "Market questions seeded."))

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
        st.info(ui_text("还没有市场问题。先初始化问题以开始结构化研究循环。", "No market questions yet. Seed them to start a structured research loop."))
        return

    selected_id = st.selectbox(title_pair("问题 ID", "Question ID"), questions["id"].tolist())
    current = questions[questions["id"] == selected_id].iloc[0]
    st.markdown(f"**{current['question']}**")
    status = st.selectbox(
        title_pair("问题状态", "Question Status"),
        ["open", "investigating", "answered", "parked"],
        index=["open", "investigating", "answered", "parked"].index(current["status"])
        if current["status"] in ["open", "investigating", "answered", "parked"]
        else 0,
            format_func=lambda value: option_label(QUESTION_STATUS_LABELS, value),
    )
    hypothesis = st.text_area(title_pair("当前假设", "Current Hypothesis"), value=current["current_hypothesis"] or "")
    evidence = st.text_area(title_pair("证据", "Evidence"), value=current["evidence"] or "")
    if st.button(title_pair("更新市场问题", "Update Market Question")):
        update_market_question(conn, int(selected_id), status, hypothesis, evidence)
        st.success(ui_text("市场问题已更新。", "Market question updated."))


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
                <strong>{title_pair("市场问题", "Market Question")}</strong><br>
                {current['question']}<br><br>
                <strong>{title_pair("当前假设", "Current Hypothesis")}</strong><br>
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
    col1.metric(title_pair("已复核轨道信号", "Reviewed Rails Signals"), len(rails))
    col2.metric(title_pair("高优先级", "Priority 1"), int((rails["priority"] == 1).sum()) if not rails.empty else 0)
    col3.metric(title_pair("需手读/OCR", "Manual Read/OCR"), int(rails["item_title"].str.contains("metadata-only", case=False, na=False).sum()) if not rails.empty else 0)
    display_df(rails)

    manual = rails[rails["item_title"].str.contains("metadata-only", case=False, na=False)] if not rails.empty else rails
    if not manual.empty:
        st.markdown(f"#### {title_pair('手动阅读/OCR 锚点', 'Manual-Read / OCR Anchors')}")
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
    if st.button(title_pair("初始化学习目标", "Seed Learning Goals")):
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
        st.success(ui_text("学习目标已初始化。", "Learning goals seeded."))

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
        selected_goal = st.selectbox(title_pair("目标 ID", "Goal ID"), goals_df["id"].tolist())
        current = goals_df[goals_df["id"] == selected_goal].iloc[0]
        status = st.selectbox(
            title_pair("目标状态", "Goal Status"),
            ["active", "in_progress", "done", "paused"],
            index=["active", "in_progress", "done", "paused"].index(current["status"])
            if current["status"] in ["active", "in_progress", "done", "paused"]
            else 0,
            format_func=lambda value: option_label(GOAL_STATUS_LABELS, value),
        )
        evidence = st.text_area(title_pair("证据/学习证明", "Evidence / Learning Proof"), value=current["evidence"] or "")
        if st.button(title_pair("更新学习目标", "Update Learning Goal")):
            update_learning_goal(conn, int(selected_goal), status, evidence)
            st.success(ui_text("学习目标已更新。", "Learning goal updated."))

    st.markdown(f"#### {title_pair('平台统计', 'Platform Stats')}")
    col1, col2, col3 = st.columns(3)
    col1.metric(title_pair("信号", "Signals"), int(conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]))
    col2.metric(title_pair("研究笔记", "Research Notes"), int(conn.execute("SELECT COUNT(*) FROM research_notes").fetchone()[0]))
    col3.metric(title_pair("来源运行", "Source Runs"), int(conn.execute("SELECT COUNT(*) FROM source_runs").fetchone()[0]))

    st.markdown(f"#### {title_pair('最近来源运行', 'Recent Source Runs')}")
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
        f"""
<div class="guardrail-band">
<strong>{title_pair("当前边界", "Current Guardrails")}</strong><br>
{ui_text(
"- 只使用公开网页、公开 app listing、官方公告、公开新闻/评论，以及你手动批准的公开 watchlist。<br>- 不收集借款人记录、私人消息、客户数据库、专有规则、非公开报告或受限页面。<br>- 不绕过登录、付费墙、CAPTCHA、访问频率限制或访问控制。<br>- 所有个人结论都要保留来源链接，并使用保守措辞。<br>- 使用“潜在信号”“需要验证”“应进一步人工检查”等表述。<br>- 不把输出表达为法律意见、监管认证或合规批准。<br>- 在存在真实或感知的职业冲突风险时，不商业化输出。",
"- Use only public webpages, public app listings, official announcements, public news/reviews, and manually approved public watchlists.<br>- Do not collect borrower records, private messages, client databases, proprietary rules, non-public reports, or restricted pages.<br>- Do not bypass login, paywalls, CAPTCHA, rate limits, or access controls.<br>- Keep personal conclusions source-linked and conservative.<br>- Use language such as \"potential signal\", \"requires verification\", and \"manual review needed\".<br>- Do not present this as legal advice, regulatory certification, or compliance approval.<br>- Do not commercialize outputs while real or perceived conflict-of-interest risk remains."
)}
</div>
"""
        ,
        unsafe_allow_html=True,
    )


def render_overview(conn: sqlite3.Connection) -> None:
    st.title(f"{ui_text('赞比亚数字借贷个人研究雷达', 'Zambia Digital Lending Personal Research Radar')} {APP_VERSION}")
    st.caption(
        f"{APP_VERSION_LABEL} · "
        f"{ui_text('公开来源市场研究工作台，用于市场理解和能力建设。', 'Public-source research workspace for market understanding and capability-building.')}"
    )
    st.markdown(
        f"""
        <div class="section-note">
        {ui_text("当前目标是能力建设和个人市场理解，不做商业交付，不使用私人/雇主/借款人数据。", "The current goal is capability-building and personal market understanding, not commercial delivery, and not private, employer, or borrower data use.")}
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("已复核", "Reviewed"), count_rows(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'reviewed'"))
    col2.metric(title_pair("待审", "New"), count_rows(conn, "SELECT COUNT(*) FROM reviews WHERE review_status = 'new'"))
    col3.metric(title_pair("研究笔记", "Notes"), count_rows(conn, "SELECT COUNT(*) FROM research_notes"))
    col4.metric(title_pair("市场问题", "Questions"), count_rows(conn, "SELECT COUNT(*) FROM market_questions"))


def render_research_brief_home(conn: sqlite3.Connection) -> None:
    snapshot = load_dashboard_snapshot()
    if not snapshot:
        st.warning(ui_text("尚未生成仪表盘快照。请先运行 snapshot_exporter.py。", "No dashboard snapshot found. Run snapshot_exporter.py first."))
        render_deployment_health(conn)
        return

    brief = build_reading_brief(snapshot, language=current_language())
    counts = brief["counts"]
    generated_at = brief.get("generated_at") or "N/A"

    section_header(
        "研究简报",
        "Research Brief",
        "按“结论、影响、行动、缺口”的顺序阅读，减少在表格之间来回跳转。",
        "Read by conclusion, impact, action, and gap instead of jumping across tables.",
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(title_pair("公开信号", "Public Signals"), counts["signals"])
    col2.metric(title_pair("已复核", "Reviewed"), counts["reviewed"])
    col3.metric(title_pair("待复核", "New"), counts["new"])
    competitor_scope = counts.get("competitor_universe_rows") or counts["competitor_matrix_rows"]
    col4.metric(title_pair("竞品候选", "Competitor Scope"), competitor_scope)
    st.caption(f"{title_pair('快照生成', 'Snapshot Generated')}: {generated_at}")

    st.markdown(f"#### {title_pair('先读这几条', 'Read These First')}")
    top_rows = brief["topline"]
    if not top_rows:
        st.info(ui_text("暂无可读的顶部信号。", "No readable top signals yet."))
    else:
        columns = st.columns(2)
        for index, item in enumerate(top_rows, start=1):
            with columns[(index - 1) % 2]:
                link = item.get("source_link") or ""
                source_line = (
                    f'<a href="{safe_html(link)}" target="_blank">{title_pair("来源", "Source")}</a>'
                    if link
                    else safe_html(item.get("source", ""))
                )
                st.markdown(
                    f"""
                    <div class="brief-card">
                        <div><span class="brief-index">{index}</span><strong>{safe_html(item.get("title", ""))}</strong></div>
                        <div class="brief-meta">{safe_html(item.get("classification", ""))} · {safe_html(item.get("risk", ""))} · {safe_html(item.get("source", ""))}</div>
                        <div class="compact-divider"></div>
                        <strong>{title_pair("为什么重要", "Why It Matters")}</strong><br>
                        {safe_html(item.get("why", ""))}<br><br>
                        <strong>{title_pair("下一步", "Next")}</strong><br>
                        {safe_html(item.get("recommended_use", ""))}
                        <div class="brief-meta">{source_line}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    left, right = st.columns([0.58, 0.42])
    with left:
        st.markdown(f"#### {title_pair('对小微贷款运营的影响线', 'Micro-lending Impact Lines')}")
        for item in brief["lanes"]:
            st.markdown(
                f"""
                <div class="brief-panel">
                    <h3>{safe_html(item.get("name", ""))}</h3>
                    <div class="brief-meta">
                        {title_pair("证据", "Evidence")}: {safe_html(item.get("evidence_count", 0))}
                        · {title_pair("高影响", "High impact")}: {safe_html(item.get("high_impact_count", 0))}
                        · {safe_html(item.get("priority", ""))}
                    </div>
                    <div class="compact-divider"></div>
                    <strong>{title_pair("业务含义", "Business Meaning")}</strong><br>
                    {safe_html(item.get("why", ""))}<br><br>
                    <strong>{title_pair("建议动作", "Suggested Action")}</strong><br>
                    {safe_html(item.get("next_action", ""))}
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        st.markdown(f"#### {title_pair('本周研究动作', 'This Week Actions')}")
        for item in brief["actions"]:
            st.markdown(
                f"""
                <div class="brief-action">
                    <strong>{safe_html(item.get("name", ""))}</strong><br>
                    <span class="brief-meta">{safe_html(item.get("priority", ""))} · {title_pair("证据", "Evidence")}: {safe_html(item.get("evidence_count", 0))}</span>
                    <div class="compact-divider"></div>
                    {safe_html(item.get("recommended_action", ""))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(f"#### {title_pair('仍需补强', 'Gaps To Close')}")
        for item in brief["gaps"]:
            st.markdown(
                f"""
                <div class="brief-gap">
                    <strong>{safe_html(item.get("name", ""))}</strong>
                    <span class="brief-meta"> · {safe_html(item.get("coverage", ""))}</span><br>
                    {safe_html(item.get("gap", ""))}<br>
                    <span class="brief-meta">{safe_html(item.get("next_source", ""))}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main() -> None:
    apply_app_style()
    render_language_switcher()
    conn = ensure_db()
    render_overview(conn)
    tabs = st.tabs(
        [
            title_pair("研究首页", "Brief"),
            title_pair("业务影响", "Ops Impact"),
            title_pair("市场竞品", "Market & Competitors"),
            title_pair("复核工作台", "Review"),
            title_pair("来源健康", "Sources & Health"),
            title_pair("输出与边界", "Outputs & Guardrails"),
        ]
    )
    with tabs[0]:
        render_research_brief_home(conn)
    with tabs[1]:
        impact_tabs = st.tabs(
            [
                title_pair("业务解读", "Intelligence"),
                title_pair("趋势变化", "Trends"),
                title_pair("本周行动", "Actions"),
                title_pair("支付轨道", "Payment Rails"),
            ]
        )
        with impact_tabs[0]:
            render_business_intelligence(conn)
        with impact_tabs[1]:
            render_trend_changes(conn)
        with impact_tabs[2]:
            render_weekly_actions(conn)
        with impact_tabs[3]:
            render_payment_rails(conn)
    with tabs[2]:
        market_tabs = st.tabs(
            [
                title_pair("竞品地图与政策", "Competitor Map & Policy"),
                title_pair("市场声音", "Market Voice"),
                title_pair("竞品矩阵", "Competitor Matrix"),
                title_pair("竞品观察", "Competitor Watch"),
            ]
        )
        with market_tabs[0]:
            render_competitor_landscape()
        with market_tabs[1]:
            render_market_voice(conn)
        with market_tabs[2]:
            render_competitor_matrix(conn)
        with market_tabs[3]:
            render_competitor_watch(conn)
    with tabs[3]:
        review_tabs = st.tabs(
            [
                title_pair("复核驾驶舱", "Review Cockpit"),
                title_pair("新信号", "New Signals"),
                title_pair("复核队列", "Review Queue"),
            ]
        )
        with review_tabs[0]:
            render_review_cockpit(conn)
        with review_tabs[1]:
            render_new_signals(conn)
        with review_tabs[2]:
            render_review_queue(conn)
    with tabs[4]:
        source_tabs = st.tabs(
            [
                title_pair("部署健康", "Deploy Health"),
                title_pair("数据源", "Sources"),
            ]
        )
        with source_tabs[0]:
            render_deployment_health(conn)
        with source_tabs[1]:
            render_sources(conn)
    with tabs[5]:
        output_tabs = st.tabs(
            [
                title_pair("周报", "Weekly Notes"),
                title_pair("笔记", "Notes"),
                title_pair("问题", "Questions"),
                title_pair("能力", "Capability"),
                title_pair("护栏", "Guardrails"),
            ]
        )
        with output_tabs[0]:
            render_brief_draft(conn)
        with output_tabs[1]:
            render_research_notes(conn)
        with output_tabs[2]:
            render_market_questions(conn)
        with output_tabs[3]:
            render_capability_tracker(conn)
        with output_tabs[4]:
            render_guardrails()


if __name__ == "__main__":
    main()
