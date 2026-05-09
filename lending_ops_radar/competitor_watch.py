"""Rule-based triage helpers for public competitor-watch signals."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


def row_value(row: Any, key: str, default: str = "") -> str:
    try:
        value = row[key]
    except Exception:
        value = getattr(row, key, default)
    return default if value is None else str(value)


def competitor_text(row: Any) -> str:
    parts = [
        row_value(row, "item_title"),
        row_value(row, "raw_text"),
    ]
    return " ".join(part for part in parts if part).lower()


def has_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def triage_competitor_signal(row: Any) -> dict[str, str | int]:
    text = competitor_text(row)
    classification = row_value(row, "classification")

    if has_any(text, ("privacy", "data safety", "account delete", "delete account", "permission", "personal data")):
        return {
            "priority": 1,
            "lens_key": "privacy_data",
            "lens_cn": "隐私、数据与账户控制",
            "lens_en": "Privacy, Data, and Account Control",
            "why_cn": "app 权限、数据安全、隐私协议和账户删除会影响授信、风控、催收触达和客户信任。",
            "why_en": "App permissions, data safety, privacy terms, and account deletion affect underwriting, risk control, collections contact, and trust.",
            "action_cn": "人工查看隐私/账户删除页面；记录收集哪些数据、客户如何撤回或删除账户、是否影响贷款/催收流程。",
            "action_en": "Manually review privacy/account-deletion wording; record data categories, withdrawal/deletion route, and possible lending/collections impact.",
        }

    if has_any(
        text,
        (
            "fee",
            "fees",
            "interest",
            "apr",
            "rate",
            "rates",
            "loan amount",
            "loan amounts",
            "repayment",
            "repay",
            "months",
            "term",
            "tenure",
            "k1,000",
            "k10,000",
            "k250,000",
            "k1,000,000",
            "k 6,000",
        ),
    ):
        return {
            "priority": 1,
            "lens_key": "pricing_terms",
            "lens_cn": "产品定价、额度与期限",
            "lens_en": "Pricing, Limits, and Tenor",
            "why_cn": "额度、期限、费用、APR、还款计划是竞品情报里最直接影响产品定位和客户预期的部分。",
            "why_en": "Limits, tenor, fees, APR, and repayment plans are the most direct competitor-intelligence inputs for positioning and customer expectations.",
            "action_cn": "提取额度、期限、费率/费用、还款方式和是否有总成本披露；放入竞品矩阵，避免只保存页面标题。",
            "action_en": "Extract limit, tenor, rate/fee, repayment method, and total-cost disclosure; put it into the competitor matrix, not just a page title.",
        }

    if has_any(text, ("mobile money", "wallet", "bank account", "bank accounts", "payments", "mobile payments", "disbursement", "sent directly", "creditors")):
        return {
            "priority": 1,
            "lens_key": "payment_rails",
            "lens_cn": "支付轨道、放款与还款",
            "lens_en": "Payment Rails, Disbursement, and Repayment",
            "why_cn": "竞品如何使用 mobile money、wallet、bank account 会影响放款速度、失败交易、对账、客服解释和合作方依赖。",
            "why_en": "How competitors use mobile money, wallets, and bank accounts affects payout speed, failed transactions, reconciliation, support explanations, and partner dependency.",
            "action_cn": "记录放款/还款通道、资金到账承诺、支付合作方和失败交易可能场景；与 BoZ payment rails 信号交叉看。",
            "action_en": "Record payout/repayment channels, funding-time promise, payment partners, and failure scenarios; cross-check against BoZ payment-rail signals.",
        }

    if has_any(text, ("5 minutes", "30 seconds", "24hrs", "within minutes", "immediately", "instant", "fast", "quick")):
        return {
            "priority": 2,
            "lens_key": "speed_claims",
            "lens_cn": "审批速度与体验承诺",
            "lens_en": "Approval Speed and Experience Promise",
            "why_cn": "速度承诺会影响客户预期、客服压力、支付轨道依赖和失败体验。",
            "why_en": "Speed promises shape customer expectations, support pressure, rail dependency, and failure experience.",
            "action_cn": "记录速度承诺和条件限制：申请、审批、签约、放款分别承诺多快；失败或延迟时是否解释。",
            "action_en": "Record speed promises and conditions across application, approval, signing, and payout; check whether delays are explained.",
        }

    if has_any(
        text,
        (
            "civil servant",
            "salary advance",
            "women",
            "agri",
            "farmers",
            "sme",
            "small medium",
            "business loan",
            "business loans",
            "collateral",
            "invoice",
            "order finance",
            "yango",
            "defence forces",
        ),
    ):
        return {
            "priority": 2,
            "lens_key": "customer_segment",
            "lens_cn": "客群与产品分层",
            "lens_en": "Customer Segment and Product Segmentation",
            "why_cn": "竞品按公务员、SME、农业、女性、司机、抵押等客群拆产品，说明市场不是单一现金贷结构。",
            "why_en": "Competitors segment by civil servants, SMEs, agriculture, women, drivers, and collateral, so the market is not a single cash-loan category.",
            "action_cn": "记录目标客群、额度/期限差异、担保/资料要求和渠道；用来更新个人市场地图。",
            "action_en": "Record target segment, limit/tenor differences, security/document requirements, and channel; use it to update the market map.",
        }

    if has_any(text, ("support@", "hotline", "consumer hotline", "email", "contact", "support")):
        return {
            "priority": 2,
            "lens_key": "support_channel",
            "lens_cn": "客服与争议入口",
            "lens_en": "Support and Dispute Channel",
            "why_cn": "公开客服入口可以反推出竞品对投诉、账户问题、还款争议和隐私请求的基础承接能力。",
            "why_en": "Public support channels hint at how competitors handle complaints, account issues, repayment disputes, and privacy requests.",
            "action_cn": "记录客服入口、是否有投诉/隐私专门入口、是否有热线/邮箱/表单；与投诉风险一起看。",
            "action_en": "Record support channel, dedicated complaint/privacy entry, hotline/email/form availability; read alongside complaint risk.",
        }

    if has_any(text, ("ceo", "appointment", "partners with", "partnership", "unveils", "growth")):
        return {
            "priority": 3,
            "lens_key": "market_move",
            "lens_cn": "市场动作与合作",
            "lens_en": "Market Move and Partnership",
            "why_cn": "合作、任命、扩张新闻是市场背景信号，通常不如产品/费用/支付/隐私信号紧急。",
            "why_en": "Partnership, appointment, and expansion news is market context, usually less urgent than product, pricing, payment, or privacy signals.",
            "action_cn": "作为市场背景保留；只有当涉及支付合作、产品上线或渠道变化时提高优先级。",
            "action_en": "Keep as market context; raise priority only if it changes payment partners, product launch, or distribution channel.",
        }

    return {
        "priority": 3,
        "lens_key": "general_competitor",
        "lens_cn": "一般竞品背景",
        "lens_en": "General Competitor Context",
        "why_cn": "当前文字更像页面背景或导航，需要人工判断是否值得保留。",
        "why_en": "The current text looks like page context or navigation and needs manual judgement before keeping.",
        "action_cn": "快速扫一眼；若没有额度、期限、费用、还款、支付、客服、隐私或客群信息，可考虑 rejected。",
        "action_en": "Quick scan; if it lacks limits, tenor, fees, repayment, payment, support, privacy, or segment information, consider rejecting.",
    }


def triage_rows(rows: Iterable[Any]) -> list[dict[str, str | int]]:
    output: list[dict[str, str | int]] = []
    for row in rows:
        triage = triage_competitor_signal(row)
        triage.update(
            {
                "signal_id": row_value(row, "id"),
                "source_id": row_value(row, "source_id"),
                "source_name": row_value(row, "source_name"),
                "signal": row_value(row, "item_title"),
                "classification": row_value(row, "classification"),
                "risk_level": row_value(row, "risk_level"),
                "source_link": row_value(row, "item_url"),
            }
        )
        output.append(triage)
    return sorted(output, key=lambda item: (int(item["priority"]), str(item["source_id"]), str(item["signal"])))


def lens_counts(items: Iterable[dict[str, str | int]]) -> Counter[str]:
    return Counter(str(item["lens_key"]) for item in items)
