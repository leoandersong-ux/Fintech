"""Market voice, trend, and action helpers for the lending ops radar."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lending_ops_radar.pipeline import DEFAULT_DB


@dataclass(frozen=True)
class ThemeRule:
    theme_key: str
    theme_cn: str
    theme_en: str
    classifications: tuple[str, ...]
    keywords: tuple[str, ...]
    business_read_cn: str
    business_read_en: str
    action_cn: str
    action_en: str
    priority: int


THEME_RULES: tuple[ThemeRule, ...] = (
    ThemeRule(
        theme_key="disbursement_payment_failure",
        theme_cn="放款/支付失败与到账摩擦",
        theme_en="Disbursement and Payment-Failure Friction",
        classifications=("disbursement", "repayment"),
        keywords=("failed", "incomplete transaction", "mobile money", "wallet", "settlement", "zipss", "montran", "gateway", "delay", "reversal", "refund"),
        business_read_cn="这类信号会影响放款到账、还款入账、失败交易解释、逾期误判和客服升级路径。",
        business_read_en="These signals affect payout posting, repayment posting, failed-transaction explanation, false delinquency, and support escalation.",
        action_cn="建立支付异常分流表：到账慢、扣款失败、重复扣款、还款未入账分别对应证据、SLA、客服话术和升级负责人。",
        action_en="Build a payment-exception routing table for delayed payout, failed deduction, duplicate deduction, and unposted repayment, with evidence, SLA, support script, and owner.",
        priority=1,
    ),
    ThemeRule(
        theme_key="fees_disclosure",
        theme_cn="费用、定价与披露摩擦",
        theme_en="Fees, Pricing, and Disclosure Friction",
        classifications=("fees",),
        keywords=("fee", "fees", "charge", "charges", "interest", "pricing", "disclosure", "misleading", "terms", "apr", "penalty"),
        business_read_cn="费用和披露信号会影响申请页、确认页、还款页、逾期说明、客服解释和投诉风险。",
        business_read_en="Fee and disclosure signals affect application pages, confirmation pages, repayment pages, late-fee wording, support explanations, and complaint risk.",
        action_cn="把总成本、费用名称、扣款时点、第三方费用和逾期费用拆开复核，避免客户把支付轨道费用误认为贷款费用。",
        action_en="Review total cost, fee labels, deduction timing, third-party fees, and late fees separately so rail fees are not mistaken for loan fees.",
        priority=1,
    ),
    ThemeRule(
        theme_key="complaints_support",
        theme_cn="投诉、客服与争议处理",
        theme_en="Complaints, Support, and Dispute Handling",
        classifications=("complaint",),
        keywords=("complaint", "support", "dispute", "redress", "report", "resolution", "consumer", "clarification", "concern"),
        business_read_cn="投诉不是客服孤岛，而是放款、还款、费用、隐私、欺诈、催收和产品解释的综合反馈系统。",
        business_read_en="Complaints are not a support silo; they are a feedback system across payout, repayment, fees, privacy, fraud, collections, and product explanation.",
        action_cn="维护投诉分类树和关闭标准：每类要有证据要求、负责人、SLA、升级路径和复盘机制。",
        action_en="Maintain a complaint taxonomy and closure standard: evidence required, owner, SLA, escalation path, and repeat-issue review.",
        priority=1,
    ),
    ThemeRule(
        theme_key="privacy_permissions",
        theme_cn="隐私、权限与账户控制",
        theme_en="Privacy, Permissions, and Account Control",
        classifications=("privacy",),
        keywords=("privacy", "permission", "data safety", "delete account", "account delete", "consent", "personal data", "controller", "processor", "rights"),
        business_read_cn="数字贷款依赖身份、设备、交易和还款数据，隐私信号会影响权限、风控、催收触达、供应商和账户删除流程。",
        business_read_en="Digital lending depends on identity, device, transaction, and repayment data; privacy signals affect permissions, risk models, collections contact, vendors, and account deletion.",
        action_cn="为每类数据写清收集目的、使用场景、保存期限、共享对象和客户权利入口，尤其关注联系人、设备、位置和交易数据。",
        action_en="Document purpose, use case, retention, sharing party, and rights channel for each data type, especially contacts, device, location, and transaction data.",
        priority=1,
    ),
    ThemeRule(
        theme_key="collections_conduct",
        theme_cn="催收行为与客户沟通",
        theme_en="Collections Conduct and Customer Communication",
        classifications=("collections",),
        keywords=("collection", "collections", "overdue", "late payment", "arrears", "harassment", "contact", "recovery"),
        business_read_cn="催收风险常从投诉、隐私边界、联系人使用、逾期解释和客服升级里出现。",
        business_read_en="Collections risk often appears through complaints, privacy boundaries, contact-person usage, overdue explanations, and support escalation.",
        action_cn="建立催收话术、触达频率、联系人使用、争议暂停和隐私边界的复核清单。",
        action_en="Create a review checklist for collections scripts, contact frequency, contact-person usage, dispute pause, and privacy boundaries.",
        priority=1,
    ),
    ThemeRule(
        theme_key="fraud_security",
        theme_cn="欺诈、账户与交易安全",
        theme_en="Fraud, Account, and Transaction Security",
        classifications=("fraud",),
        keywords=("fraud", "scam", "phishing", "impersonation", "stolen", "cyber", "security", "authentication", "unsolicited"),
        business_read_cn="欺诈会同时影响获客、KYC、放款、还款、坏账、客服核验和品牌信任。",
        business_read_en="Fraud affects acquisition, KYC, payout, repayment, credit loss, support verification, and brand trust at the same time.",
        action_cn="把欺诈信号拆到账户接管、身份冒用、支付欺诈、短信/钓鱼和代理/内部风险，并定义人工复核与申诉路径。",
        action_en="Split fraud into account takeover, impersonation, payment fraud, SMS/phishing, and agent/internal risk; define manual review and appeal paths.",
        priority=1,
    ),
    ThemeRule(
        theme_key="competitor_product_change",
        theme_cn="竞品产品与 App 层变化",
        theme_en="Competitor Product and App-Layer Change",
        classifications=("competitor_change",),
        keywords=("loan", "instant", "repayment", "eligible", "approval", "app", "updated", "rating", "reviews", "privacy", "support"),
        business_read_cn="竞品信号要转成产品打法比较：额度、期限、费用表达、速度承诺、支付路径、客服入口和隐私入口。",
        business_read_en="Competitor signals should become product-strategy comparison: limits, tenor, fee wording, speed promise, payment path, support route, and privacy route.",
        action_cn="继续维护竞品矩阵；Google Play/app listing 先作为候选源，确认边界后再启用。",
        action_en="Keep maintaining the competitor matrix; keep Google Play/app listings as candidate sources until source boundaries are confirmed.",
        priority=2,
    ),
    ThemeRule(
        theme_key="regulatory_conduct",
        theme_cn="监管、消费者保护与运营约束",
        theme_en="Regulatory, Consumer Protection, and Operating Constraints",
        classifications=("regulatory", "news_signal"),
        keywords=("regulatory", "consumer", "directive", "circular", "public notice", "unfair", "rights", "compliance", "market"),
        business_read_cn="监管/消费者保护信号本身不等于结论，但可转成披露、投诉、支付、隐私和客服流程的复核项。",
        business_read_en="Regulatory and consumer-protection signals are not conclusions, but can become review items for disclosure, complaints, payments, privacy, and support processes.",
        action_cn="只把监管信号映射为待复核流程，不把公开页面表述当作法律或合规结论。",
        action_en="Map regulatory signals into process checks only; do not treat public-page wording as legal or compliance conclusions.",
        priority=2,
    ),
)

DEFAULT_THEME = ThemeRule(
    theme_key="background_market_signal",
    theme_cn="背景市场信号",
    theme_en="Background Market Signal",
    classifications=(),
    keywords=(),
    business_read_cn="当前只能作为背景观察，需要更多同类公开信号交叉验证。",
    business_read_en="This is background context for now and needs more public-source triangulation.",
    action_cn="保留来源链接，等待同类信号增加后再形成业务判断。",
    action_en="Keep the source link and wait for more similar signals before forming a business judgment.",
    priority=3,
)


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def row_value(row: Any, key: str, default: str = "") -> str:
    try:
        value = row[key]
    except Exception:
        value = getattr(row, key, default)
    return default if value is None else str(value)


def signal_text(row: Any) -> str:
    parts = [
        row_value(row, "source_id"),
        row_value(row, "source_name"),
        row_value(row, "classification"),
        row_value(row, "item_title"),
        row_value(row, "raw_text"),
        row_value(row, "reviewer_notes"),
        row_value(row, "recommended_action"),
    ]
    return " ".join(part for part in parts if part).lower()


def parse_time(value: object) -> datetime | None:
    text = "" if value is None else str(value).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def load_signal_review_rows(conn: sqlite3.Connection, include_rejected: bool = False) -> list[sqlite3.Row]:
    where = "" if include_rejected else "WHERE r.review_status != 'rejected'"
    return list(
        conn.execute(
            f"""
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
                s.first_seen_at,
                s.last_seen_at,
                r.review_status,
                r.priority,
                r.reviewer_notes,
                r.recommended_action
            FROM signals s
            JOIN reviews r ON r.signal_id = s.id
            {where}
            ORDER BY s.last_seen_at DESC, r.priority ASC, s.id DESC
            """
        )
    )


def classify_theme(row: Any) -> ThemeRule:
    classification = row_value(row, "classification")
    text = signal_text(row)
    best_score = -1
    best_rule = DEFAULT_THEME
    for rule in THEME_RULES:
        score = 0
        if classification in rule.classifications:
            score += 4
        score += sum(1 for keyword in rule.keywords if keyword in text)
        if row_value(row, "source_id").startswith("competitor_") and rule.theme_key == "competitor_product_change":
            score += 3
        if score > best_score:
            best_score = score
            best_rule = rule
    return best_rule if best_score > 0 else DEFAULT_THEME


def build_market_voice_row(row: Any) -> dict[str, object]:
    rule = classify_theme(row)
    title = row_value(row, "item_title")
    source_link = row_value(row, "item_url") or row_value(row, "source_url")
    review_status = row_value(row, "review_status")
    review_bonus = 0 if review_status in {"reviewed", "briefed"} else 1
    return {
        "signal_id": row_value(row, "id"),
        "theme_key": rule.theme_key,
        "theme_cn": rule.theme_cn,
        "theme_en": rule.theme_en,
        "source_name": row_value(row, "source_name"),
        "signal": title,
        "classification": row_value(row, "classification"),
        "risk_level": row_value(row, "risk_level"),
        "review_status": review_status,
        "priority": row_value(row, "priority"),
        "last_seen_at": row_value(row, "last_seen_at"),
        "business_read_cn": rule.business_read_cn,
        "business_read_en": rule.business_read_en,
        "action_cn": rule.action_cn,
        "action_en": rule.action_en,
        "source_link": source_link,
        "sort_priority": rule.priority + review_bonus,
    }


def market_voice_rows(conn: sqlite3.Connection, limit: int = 40) -> list[dict[str, object]]:
    rows = [build_market_voice_row(row) for row in load_signal_review_rows(conn)]
    rows.sort(
        key=lambda row: (
            int(row["sort_priority"]),
            {"high": 0, "medium": 1, "low": 2}.get(str(row["risk_level"]), 3),
            str(row["last_seen_at"]),
        )
    )
    return rows[:limit]


def max_signal_time(rows: Iterable[Any]) -> datetime:
    parsed = [parse_time(row_value(row, "last_seen_at")) for row in rows]
    valid = [item for item in parsed if item is not None]
    return max(valid) if valid else datetime.now(UTC)


def trend_rows(conn: sqlite3.Connection, window_days: int = 7) -> list[dict[str, object]]:
    rows = load_signal_review_rows(conn)
    if not rows:
        return []
    anchor = max_signal_time(rows)
    current_start = anchor - timedelta(days=window_days)
    previous_start = current_start - timedelta(days=window_days)
    current_counts: Counter[str] = Counter()
    previous_counts: Counter[str] = Counter()
    theme_lookup: dict[str, ThemeRule] = {}
    for row in rows:
        seen = parse_time(row_value(row, "last_seen_at"))
        if seen is None:
            continue
        rule = classify_theme(row)
        theme_lookup[rule.theme_key] = rule
        if seen >= current_start:
            current_counts[rule.theme_key] += 1
        elif previous_start <= seen < current_start:
            previous_counts[rule.theme_key] += 1
    keys = set(current_counts) | set(previous_counts)
    output: list[dict[str, object]] = []
    for key in keys:
        rule = theme_lookup.get(key, DEFAULT_THEME)
        current = current_counts.get(key, 0)
        previous = previous_counts.get(key, 0)
        delta = current - previous
        if delta > 0:
            direction_cn, direction_en = "上升", "Up"
        elif delta < 0:
            direction_cn, direction_en = "下降", "Down"
        else:
            direction_cn, direction_en = "持平", "Flat"
        if current == 0 and previous > 0:
            interpretation_cn = "本窗口未再出现，但仍应保留为观察项。"
            interpretation_en = "No current-window signal, but keep it on watch."
        elif delta > 0:
            interpretation_cn = f"最近窗口新增 {delta} 条同类公开信号，适合优先复核是否形成持续主题。"
            interpretation_en = f"The latest window added {delta} public signal(s), so review whether this is becoming a sustained theme."
        else:
            interpretation_cn = "当前变化不大，适合继续低频监控。"
            interpretation_en = "Change is limited; keep it on low-frequency monitoring."
        output.append(
            {
                "theme_key": key,
                "theme_cn": rule.theme_cn,
                "theme_en": rule.theme_en,
                "current_count": current,
                "previous_count": previous,
                "delta": delta,
                "direction_cn": direction_cn,
                "direction_en": direction_en,
                "interpretation_cn": interpretation_cn,
                "interpretation_en": interpretation_en,
                "action_cn": rule.action_cn,
                "action_en": rule.action_en,
                "window_days": window_days,
                "anchor_date": anchor.date().isoformat(),
            }
        )
    output.sort(key=lambda row: (-int(row["current_count"]), -int(row["delta"]), str(row["theme_cn"])))
    return output


def weekly_action_rows(conn: sqlite3.Connection, limit: int = 8) -> list[dict[str, object]]:
    trends = trend_rows(conn)
    voice = market_voice_rows(conn, limit=200)
    evidence_counts: Counter[str] = Counter(str(row["theme_key"]) for row in voice)
    theme_rows: dict[str, dict[str, object]] = {}
    for row in trends:
        theme_rows[str(row["theme_key"])] = row
    for row in voice:
        key = str(row["theme_key"])
        if key not in theme_rows:
            theme_rows[key] = {
                "theme_key": key,
                "theme_cn": row["theme_cn"],
                "theme_en": row["theme_en"],
                "delta": 0,
                "action_cn": row["action_cn"],
                "action_en": row["action_en"],
            }
    actions: list[dict[str, object]] = []
    for key, row in theme_rows.items():
        evidence = evidence_counts.get(key, 0)
        delta = int(row.get("delta", 0))
        priority_score = evidence + max(delta, 0) * 2
        if priority_score >= 12:
            priority_cn, priority_en = "本周优先", "This-week priority"
        elif priority_score >= 5:
            priority_cn, priority_en = "持续推进", "Keep moving"
        else:
            priority_cn, priority_en = "观察保留", "Keep on watch"
        actions.append(
            {
                "action_area_cn": row["theme_cn"],
                "action_area_en": row["theme_en"],
                "trigger_cn": f"{evidence} 条相关公开信号；本窗口变化 {delta:+d}。",
                "trigger_en": f"{evidence} related public signal(s); latest-window change {delta:+d}.",
                "recommended_action_cn": row["action_cn"],
                "recommended_action_en": row["action_en"],
                "owner_cn": "个人研究复核",
                "owner_en": "Personal research review",
                "priority_cn": priority_cn,
                "priority_en": priority_en,
                "evidence_count": evidence,
                "delta": delta,
                "priority_score": priority_score,
            }
        )
    actions.sort(key=lambda row: (-int(row["priority_score"]), str(row["action_area_cn"])))
    return actions[:limit]


def source_trend_rows(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = list(
        conn.execute(
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
            """
        )
    )
    output: list[dict[str, object]] = []
    for row in rows:
        run_count = int(row["run_count"] or 0)
        success_count = int(row["success_count"] or 0)
        success_rate = round(success_count / run_count, 2) if run_count else 0
        if row["enabled"] and success_rate < 0.7:
            status_cn, status_en = "需要处理", "Needs attention"
            action_cn = "检查 SSL、PDF/页面结构或是否应改为手动复核来源。"
            action_en = "Check SSL, PDF/page structure, or whether this should become a manual-review source."
        elif int(row["last_signal_count"] or 0) == 0:
            status_cn, status_en = "低产出观察", "Low-yield watch"
            action_cn = "确认来源是否仍有研究价值，避免低价值自动抓取。"
            action_en = "Confirm whether the source remains useful and avoid low-value automated fetching."
        else:
            status_cn, status_en = "稳定", "Stable"
            action_cn = "保持当前频率。"
            action_en = "Keep current frequency."
        output.append(
            {
                "source_id": row["source_id"],
                "source_name": row["source_name"],
                "enabled": row["enabled"],
                "run_count": run_count,
                "success_rate": success_rate,
                "last_status": row["last_status"],
                "last_signal_count": row["last_signal_count"],
                "status_cn": status_cn,
                "status_en": status_en,
                "action_cn": action_cn,
                "action_en": action_en,
                "last_error": row["last_error"],
                "updated_at": row["updated_at"],
            }
        )
    return output


def print_rows(rows: list[dict[str, object]], language: str) -> None:
    for row in rows:
        theme = row.get("theme_cn") or row.get("action_area_cn") or row.get("source_name")
        if language == "en":
            theme = row.get("theme_en") or row.get("action_area_en") or row.get("source_name")
        action = row.get("action_cn") or row.get("recommended_action_cn")
        if language == "en":
            action = row.get("action_en") or row.get("recommended_action_en")
        print(f"- {theme}: {action}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show market voice, trend, and weekly action rows")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--mode", choices=["voice", "trends", "actions", "sources"], default="trends")
    parser.add_argument("--language", choices=["zh", "en"], default="zh")
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")
    conn = connect(args.db)
    if args.mode == "voice":
        rows = market_voice_rows(conn, args.limit)
    elif args.mode == "actions":
        rows = weekly_action_rows(conn, args.limit)
    elif args.mode == "sources":
        rows = source_trend_rows(conn)[: args.limit]
    else:
        rows = trend_rows(conn)[: args.limit]
    print_rows(rows, args.language)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
