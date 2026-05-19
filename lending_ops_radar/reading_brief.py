"""Readable dashboard model for the Streamlit research workspace.

The rest of the platform keeps detailed source, signal, and review tables. This
module turns those records into a compact reading order for the top of the app.
"""

from __future__ import annotations

from typing import Any


GARBLE_FALLBACK_ZH = "历史备注存在编码损坏，需回源复核。"
GARBLE_FALLBACK_EN = "Historical note has encoding loss; review the source."


def looks_question_garbled(value: object) -> bool:
    text = "" if value is None else str(value)
    if not text:
        return False
    question_count = text.count("?")
    return "????" in text or (question_count >= 6 and question_count / max(len(text), 1) > 0.18)


def clean_display_text(value: object, language: str = "zh") -> str:
    text = "" if value is None else str(value).strip()
    if looks_question_garbled(text) or "\ufffd" in text:
        return GARBLE_FALLBACK_EN if language == "en" else GARBLE_FALLBACK_ZH
    return text


def _localized(row: dict[str, Any], base: str, language: str) -> str:
    preferred = f"{base}_en" if language == "en" else f"{base}_cn"
    fallback = f"{base}_cn" if language == "en" else f"{base}_en"
    value = row.get(preferred) or row.get(fallback) or row.get(base) or ""
    return clean_display_text(value, language)


def _take_rows(snapshot: dict[str, Any], key: str, limit: int) -> list[dict[str, Any]]:
    rows = snapshot.get(key, [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)][:limit]


def _counts(snapshot: dict[str, Any]) -> dict[str, int]:
    raw_counts = snapshot.get("counts", {})
    if not isinstance(raw_counts, dict):
        raw_counts = {}
    result: dict[str, int] = {}
    for key in (
        "signals",
        "reviewed",
        "new",
        "market_questions",
        "competitor_matrix_rows",
        "competitor_universe_rows",
        "policy_impact_rows",
        "competitor_event_rows",
    ):
        try:
            result[key] = int(raw_counts.get(key, 0))
        except (TypeError, ValueError):
            result[key] = 0
    return result


def build_reading_brief(
    snapshot: dict[str, Any],
    *,
    language: str = "zh",
    topline_limit: int = 4,
    lane_limit: int = 5,
    action_limit: int = 5,
    gap_limit: int = 4,
) -> dict[str, Any]:
    """Build a compact, ordered reading model from a dashboard snapshot."""

    language = "en" if language == "en" else "zh"
    topline: list[dict[str, Any]] = []
    for row in _take_rows(snapshot, "top_quality_rows", topline_limit):
        topline.append(
            {
                "id": clean_display_text(row.get("signal_id", ""), language),
                "title": clean_display_text(row.get("signal", ""), language),
                "classification": clean_display_text(row.get("classification", ""), language),
                "risk": clean_display_text(row.get("risk_level", ""), language),
                "why": _localized(row, "quality_reason", language),
                "recommended_use": _localized(row, "recommended_use", language),
                "source": clean_display_text(row.get("source_name", ""), language),
                "source_link": clean_display_text(row.get("source_link", ""), language),
            }
        )

    lanes: list[dict[str, Any]] = []
    for row in _take_rows(snapshot, "operating_lanes", lane_limit):
        lanes.append(
            {
                "name": _localized(row, "lane", language),
                "priority": _localized(row, "priority", language),
                "why": _localized(row, "why", language),
                "next_action": _localized(row, "next_action", language),
                "evidence_count": int(row.get("evidence_count") or 0),
                "high_impact_count": int(row.get("high_impact_count") or 0),
            }
        )

    actions: list[dict[str, Any]] = []
    for row in _take_rows(snapshot, "weekly_actions", action_limit):
        actions.append(
            {
                "name": _localized(row, "action_area", language),
                "priority": _localized(row, "priority", language),
                "trigger": _localized(row, "trigger", language),
                "recommended_action": _localized(row, "recommended_action", language),
                "owner": _localized(row, "owner", language),
                "evidence_count": int(row.get("evidence_count") or 0),
            }
        )

    gaps: list[dict[str, Any]] = []
    for row in _take_rows(snapshot, "coverage_gaps", gap_limit):
        gaps.append(
            {
                "name": _localized(row, "area", language),
                "coverage": _localized(row, "coverage", language),
                "gap": _localized(row, "gap", language),
                "next_source": _localized(row, "next_source", language),
            }
        )

    return {
        "counts": _counts(snapshot),
        "generated_at": clean_display_text(snapshot.get("generated_at", ""), language),
        "topline": topline,
        "lanes": lanes,
        "actions": actions,
        "gaps": gaps,
    }
