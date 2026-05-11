"""Build a source-linked competitor product matrix from reviewed signals."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lending_ops_radar.pipeline import DEFAULT_DB

DEFAULT_OUTPUT_DIR = ROOT / "data"
DEFAULT_BRIEF_DIR = ROOT / "data" / "briefs"


@dataclass(frozen=True)
class ProductMatrixSeed:
    institution: str
    product_or_signal: str
    product_type_cn: str
    product_type_en: str
    segment_cn: str
    segment_en: str
    limit_amount: str
    tenor_or_repayment: str
    pricing_or_disclosure: str
    speed_claim: str
    payment_or_disbursement: str
    support_privacy_ops: str
    business_interpretation_cn: str
    business_interpretation_en: str
    next_questions_cn: str
    next_questions_en: str
    source_signal_ids: tuple[int, ...]
    confidence: str = "medium"
    status: str = "source-linked observation"


MATRIX_SEEDS: tuple[ProductMatrixSeed, ...] = (
    ProductMatrixSeed(
        institution="FLoan",
        product_or_signal="Microloan app",
        product_type_cn="数字小额贷款",
        product_type_en="Digital microloan",
        segment_cn="赞比亚个人借款人",
        segment_en="Zambia personal borrowers",
        limit_amount="Up to K 6,000",
        tenor_or_repayment="Defined repayment options; installment-based repayment mentioned",
        pricing_or_disclosure="Terms and fees described as clearly disclosed; specific APR/fees not captured in current signal",
        speed_claim="Approval/disbursement subject to eligibility checks and successful verification",
        payment_or_disbursement="Mobile payments mentioned; disbursement subject to verification",
        support_privacy_ops="Public support email observed: support@floan.co",
        business_interpretation_cn="FLoan 看起来是 app-first 微贷产品，公开额度锚点较清楚，但费率、期限和失败场景还需要人工回源确认。",
        business_interpretation_en="FLoan appears to be an app-first microloan product with a clear public limit anchor, but rate, tenor, and failure scenarios still need manual source review.",
        next_questions_cn="K6,000 是否为单一额度上限？APR/服务费/逾期费在哪里披露？mobile payments 具体用于放款、还款还是两者？",
        next_questions_en="Is K6,000 the general cap? Where are APR, service fee, and late fee disclosed? Are mobile payments used for disbursement, repayment, or both?",
        source_signal_ids=(422, 424, 433, 434),
    ),
    ProductMatrixSeed(
        institution="Lupiya",
        product_or_signal="Instant Loan",
        product_type_cn="短期小额贷款",
        product_type_en="Short-term small loan",
        segment_cn="普通个人借款人",
        segment_en="General personal borrowers",
        limit_amount="K500",
        tenor_or_repayment="3 months",
        pricing_or_disclosure="Rate/fees not captured; page says choose repayment plan and rate elsewhere",
        speed_claim="Instant / 5 minutes / 30 seconds wording appears across pages; one signal says Coming soon",
        payment_or_disbursement="Funds may be sent to account or creditors according to broader Lupiya journey signal",
        support_privacy_ops="No dedicated support/privacy detail captured in current reviewed signal",
        business_interpretation_cn="这是 Lupiya 最像纯数字短期小额贷的公开锚点，但 Coming soon 表示需要持续监控上线状态。",
        business_interpretation_en="This is Lupiya's clearest public short-term microloan anchor, but the Coming soon wording means launch status needs monitoring.",
        next_questions_cn="Coming soon 是否已变成可申请？K500/3 months 的费用、APR、逾期规则和支付通道是什么？",
        next_questions_en="Has Coming soon changed to live application? What are the fees, APR, late rules, and payment channels for K500/3 months?",
        source_signal_ids=(332, 340, 348, 352, 353),
    ),
    ProductMatrixSeed(
        institution="Lupiya",
        product_or_signal="Civil Servant Loans",
        product_type_cn="工资收入客群贷款",
        product_type_en="Salary-linked segment loan",
        segment_cn="政府工作人员/公务员",
        segment_en="Government workers / civil servants",
        limit_amount="Not captured",
        tenor_or_repayment="Not captured",
        pricing_or_disclosure="Low interest wording observed; exact rate not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Likely part of Lupiya general application/disbursement journey; exact channel not captured",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="稳定工资客群可能带来更低定价或更高通过率，是客群分层的重要信号。",
        business_interpretation_en="A stable salary segment may support lower pricing or higher approval, making this an important segmentation signal.",
        next_questions_cn="是否需要雇佣证明或工资账户？低利率具体是多少？还款是否绑定工资周期？",
        next_questions_en="Is employment proof or salary account needed? What is the actual low rate? Is repayment aligned with salary cycle?",
        source_signal_ids=(334,),
    ),
    ProductMatrixSeed(
        institution="Lupiya",
        product_or_signal="Collateral-backed Loans",
        product_type_cn="资产抵押/担保贷款",
        product_type_en="Asset-backed loan",
        segment_cn="有资产可抵押的个人或小微经营者",
        segment_en="Borrowers with usable assets",
        limit_amount="Bigger loan wording; exact limit not captured",
        tenor_or_repayment="Not captured",
        pricing_or_disclosure="Better rates wording observed; exact rate not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Not captured",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="抵押型产品说明市场不只有无抵押现金贷，也存在更高额度/更低风险的贷款线。",
        business_interpretation_en="Asset-backed lending shows the market is not only unsecured cash loans; there is a higher-limit/lower-risk lane.",
        next_questions_cn="哪些资产可接受？估值与处置流程是什么？额度、期限、费率如何变化？",
        next_questions_en="Which assets are accepted? What valuation and recovery process applies? How do limit, tenor, and rate change?",
        source_signal_ids=(338,),
    ),
    ProductMatrixSeed(
        institution="Lupiya",
        product_or_signal="Yango Driver Loans",
        product_type_cn="职业/平台司机贷款",
        product_type_en="Occupation/platform-driver loan",
        segment_cn="Yango 司机",
        segment_en="Yango drivers",
        limit_amount="Not captured",
        tenor_or_repayment="Not captured",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Use case includes fuel top-up and car maintenance",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="平台司机贷款显示竞品可能围绕收入场景和车辆运营成本做产品分层。",
        business_interpretation_en="Driver loans suggest product segmentation around income activity and vehicle operating costs.",
        next_questions_cn="是否与平台收入或司机账户绑定？还款周期是否按司机现金流设计？",
        next_questions_en="Is it linked to platform income or driver account? Is repayment designed around driver cash flow?",
        source_signal_ids=(333,),
    ),
    ProductMatrixSeed(
        institution="Lupiya",
        product_or_signal="Lupiya for Women",
        product_type_cn="女性小微经营贷款",
        product_type_en="Women-focused business loan",
        segment_cn="女性创业者/女性经营者",
        segment_en="Women entrepreneurs / women business owners",
        limit_amount="Not captured",
        tenor_or_repayment="Not captured",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Not captured",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="女性经营者产品说明竞品在用包容金融或细分客群叙事拓展市场。",
        business_interpretation_en="A women-focused product suggests inclusive-finance and segment-led market positioning.",
        next_questions_cn="是否有特殊费率、资料要求、合作项目或额度？",
        next_questions_en="Are there special rates, documentation, partner programs, or limits?",
        source_signal_ids=(335,),
    ),
    ProductMatrixSeed(
        institution="Lupiya",
        product_or_signal="Agri Loans",
        product_type_cn="农业贷款",
        product_type_en="Agriculture loan",
        segment_cn="农户/农业经营者",
        segment_en="Farmers / agricultural operators",
        limit_amount="Not captured",
        tenor_or_repayment="Seeds, equipment, harvesting use cases imply seasonal cash-flow relevance",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Not captured",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="农业贷款可能需要不同授信与还款节奏，不能简单按月薪贷或即时贷理解。",
        business_interpretation_en="Agriculture loans likely need different underwriting and repayment rhythm than salary or instant loans.",
        next_questions_cn="是否有季节性还款、用途限制、采购/销售凭证要求？",
        next_questions_en="Are there seasonal repayments, use restrictions, or purchase/sales-document requirements?",
        source_signal_ids=(336,),
    ),
    ProductMatrixSeed(
        institution="Lupiya",
        product_or_signal="Zambia Defence Forces Loans",
        product_type_cn="特定雇佣群体贷款",
        product_type_en="Specific employment-segment loan",
        segment_cn="国防军/制服人员",
        segment_en="Defence forces / uniformed personnel",
        limit_amount="Not captured",
        tenor_or_repayment="Not captured",
        pricing_or_disclosure="Tailored loan wording observed; details not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Not captured",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="国防军贷款是稳定雇佣客群分层信号，可能与工资证明和风险定价相关。",
        business_interpretation_en="Defence forces loans indicate stable-employment segmentation and may relate to employment proof and risk pricing.",
        next_questions_cn="是否需要雇主证明？还款是否与工资周期或雇佣状态绑定？",
        next_questions_en="Is employer proof needed? Is repayment tied to salary cycle or employment status?",
        source_signal_ids=(337,),
    ),
    ProductMatrixSeed(
        institution="PremierCredit",
        product_or_signal="Salary Advance",
        product_type_cn="工资预支/短期现金贷款",
        product_type_en="Salary advance / short-term cash loan",
        segment_cn="有工资收入的个人",
        segment_en="Salary-earning individuals",
        limit_amount="Up to K10,000",
        tenor_or_repayment="Not captured",
        pricing_or_disclosure="Affordable wording observed; exact pricing not captured",
        speed_claim="Approval in 24hrs; money immediately wording observed",
        payment_or_disbursement="Mobile money account appears in application flow",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="Salary advance 是急用现金场景，额度和速度承诺清楚，可能与工资收入证明和移动钱包放款相关。",
        business_interpretation_en="Salary advance is an urgent-cash product with clear limit and speed promise, likely linked to salary proof and mobile-money payout.",
        next_questions_cn="费用/利率、还款日、工资扣款或手动还款机制是什么？",
        next_questions_en="What are the fees/rate, repayment date, salary-deduction or manual repayment mechanics?",
        source_signal_ids=(407, 405),
    ),
    ProductMatrixSeed(
        institution="PremierCredit",
        product_or_signal="Personal Loan",
        product_type_cn="大额个人贷款",
        product_type_en="Larger personal loan",
        segment_cn="有大额消费/教育/住房改善需求的个人",
        segment_en="Individuals with large expense, education, or home-improvement needs",
        limit_amount="Up to K250,000",
        tenor_or_repayment="Up to 60 months",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Mobile money account appears in broader borrow flow",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="这与即时小额贷不是同一产品层，周期和额度都更接近传统个人贷款。",
        business_interpretation_en="This is not the same lane as instant microloans; limit and tenor look closer to traditional personal lending.",
        next_questions_cn="是否需要工资证明、抵押、共同借款人或线下签约？提前还款/逾期规则是什么？",
        next_questions_en="Is salary proof, collateral, co-borrower, or offline signing required? What are prepayment and late rules?",
        source_signal_ids=(408,),
    ),
    ProductMatrixSeed(
        institution="PremierCredit",
        product_or_signal="SME Loans",
        product_type_cn="小微企业贷款",
        product_type_en="SME loan",
        segment_cn="SME/小微企业",
        segment_en="SMEs",
        limit_amount="Up to K1,000,000",
        tenor_or_repayment="Personalized and flexible repayment plans",
        pricing_or_disclosure="Not captured",
        speed_claim="Loan decision within minutes appears in borrow flow, but product-specific scope unclear",
        payment_or_disbursement="Mobile money account appears in borrow flow",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="SME K1,000,000 上限说明 PremierCredit 覆盖更重的企业融资，不应和 K500/K6,000 微贷放在同一档比较。",
        business_interpretation_en="The K1,000,000 SME cap shows heavier business finance coverage and should not be compared directly with K500/K6,000 microloans.",
        next_questions_cn="资料要求、财务报表、担保、审批周期、用途限制和还款频率是什么？",
        next_questions_en="What documentation, statements, security, approval time, use restrictions, and repayment frequency apply?",
        source_signal_ids=(410, 403, 405),
    ),
    ProductMatrixSeed(
        institution="PremierCredit",
        product_or_signal="Invoice / Receivables Finance",
        product_type_cn="应收账款/发票融资",
        product_type_en="Invoice / receivables finance",
        segment_cn="有应收账款的小微企业",
        segment_en="SMEs with receivables",
        limit_amount="Not captured",
        tenor_or_repayment="Repay when customer cash is received",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Repayment depends on receivables cash collection",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="这是现金流融资，不是普通小额贷；对运营来说关键是发票/应收账款真实性和回款监控。",
        business_interpretation_en="This is cash-flow finance, not a normal microloan; operations depend on invoice/receivables verification and cash-collection monitoring.",
        next_questions_cn="如何验证应收账款？是否通知付款方？违约和追索路径是什么？",
        next_questions_en="How are receivables verified? Is the payer notified? What are default and recourse paths?",
        source_signal_ids=(411,),
    ),
    ProductMatrixSeed(
        institution="PremierCredit",
        product_or_signal="Order Finance",
        product_type_cn="订单融资",
        product_type_en="Order finance",
        segment_cn="有 confirmed purchase order 的 SME",
        segment_en="SMEs with confirmed purchase orders",
        limit_amount="Not captured",
        tenor_or_repayment="Linked to order execution cash flow",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Draw money against a confirmed purchase order",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="订单融资说明竞品在做经营场景授信，风险点是订单真实性、买方信用和交付周期。",
        business_interpretation_en="Order finance indicates operating-scenario credit, with risk around order validity, buyer credit, and delivery cycle.",
        next_questions_cn="确认订单如何核验？资金是否定向支付供应商？还款来源是否为订单回款？",
        next_questions_en="How is the purchase order verified? Is funding paid to suppliers? Is repayment sourced from order proceeds?",
        source_signal_ids=(412,),
    ),
    ProductMatrixSeed(
        institution="PremierCredit",
        product_or_signal="Agri-Business Loans",
        product_type_cn="农业经营贷款",
        product_type_en="Agri-business loan",
        segment_cn="农户/农业经营企业",
        segment_en="Farmers / agribusinesses",
        limit_amount="Not captured",
        tenor_or_repayment="Land, equipment, and operational-expense use cases imply seasonal/operating cycle relevance",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Not captured",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="PremierCredit 与 Lupiya 都出现农业信号，农业/农资/收成周期可能是赞比亚小微金融重要垂直。",
        business_interpretation_en="Both PremierCredit and Lupiya show agriculture signals, suggesting farming/input/harvest cycles may be an important Zambia microfinance vertical.",
        next_questions_cn="是否有季节性还款、实物用途、买方/供应商合作或天气/产量风险控制？",
        next_questions_en="Are there seasonal repayments, use-of-funds controls, buyer/supplier partnerships, or weather/yield risk controls?",
        source_signal_ids=(413,),
    ),
    ProductMatrixSeed(
        institution="PremierCredit",
        product_or_signal="Wallet / Mobile Money Partnerships",
        product_type_cn="支付与钱包能力",
        product_type_en="Payment and wallet capability",
        segment_cn="PremierCredit 用户/借款人/钱包用户",
        segment_en="PremierCredit users / borrowers / wallet users",
        limit_amount="Not applicable",
        tenor_or_repayment="Not applicable",
        pricing_or_disclosure="Not captured",
        speed_claim="Seamless/convenient wording observed",
        payment_or_disbursement="Mobile Money Providers and banks partnerships; Airtel Money loan-services partnership headline observed",
        support_privacy_ops="No dedicated support/privacy detail captured",
        business_interpretation_cn="支付能力是 PremierCredit 竞争力的一部分，可能影响获客、放款、还款、账单支付和对账体验。",
        business_interpretation_en="Payment capability appears part of PremierCredit's competitive position and may affect acquisition, payout, repayment, bill pay, and reconciliation experience.",
        next_questions_cn="Airtel Money 合作具体覆盖哪些贷款服务？钱包是否用于自动还款、放款或账单支付？失败交易如何处理？",
        next_questions_en="Which loan services are covered by the Airtel Money partnership? Is the wallet used for auto-repayment, payout, or bill pay? How are failed transactions handled?",
        source_signal_ids=(394, 374, 405),
    ),
    ProductMatrixSeed(
        institution="PowerKwacha",
        product_or_signal="Privacy / Account Control",
        product_type_cn="隐私与账户控制信号",
        product_type_en="Privacy and account-control signal",
        segment_cn="PowerKwacha app 用户",
        segment_en="PowerKwacha app users",
        limit_amount="Not captured",
        tenor_or_repayment="Not captured",
        pricing_or_disclosure="Not captured",
        speed_claim="Not captured",
        payment_or_disbursement="Not captured",
        support_privacy_ops="Privacy Agreement, Account Delete, Consumer Hotline observed",
        business_interpretation_cn="虽然不是贷款产品，但 privacy/account delete/hotline 是 app-first lender 的关键运营与合规体验信号。",
        business_interpretation_en="This is not a loan product, but privacy/account deletion/hotline are key operating and compliance-experience signals for an app-first lender.",
        next_questions_cn="隐私协议收集哪些数据？账户删除对未结清贷款如何处理？热线是否也是投诉入口？",
        next_questions_en="What data does the privacy agreement collect? How does account deletion handle outstanding loans? Is the hotline also a complaint channel?",
        source_signal_ids=(416, 417, 419),
    ),
)


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def today_label() -> str:
    return datetime.now(UTC).date().isoformat()


def signal_lookup(conn: sqlite3.Connection) -> dict[int, sqlite3.Row]:
    return {
        int(row["id"]): row
        for row in conn.execute(
            """
            SELECT
                s.id,
                s.item_title,
                s.item_url,
                s.source_name,
                s.source_id,
                r.review_status,
                r.priority
            FROM signals s
            JOIN reviews r ON r.signal_id = s.id
            WHERE s.source_id LIKE 'competitor_%'
            """
        )
    }


def source_links(seed: ProductMatrixSeed, lookup: dict[int, sqlite3.Row]) -> str:
    links: list[str] = []
    for signal_id in seed.source_signal_ids:
        row = lookup.get(signal_id)
        if row is None:
            links.append(f"{signal_id}: missing")
            continue
        url = row["item_url"] or ""
        label = f"{signal_id}"
        links.append(f"[{label}]({url})" if url else label)
    return "; ".join(links)


def source_status(seed: ProductMatrixSeed, lookup: dict[int, sqlite3.Row]) -> str:
    statuses = []
    for signal_id in seed.source_signal_ids:
        row = lookup.get(signal_id)
        statuses.append(row["review_status"] if row is not None else "missing")
    return ", ".join(statuses)


LIMIT_PATTERN = re.compile(r"\bK\s*([0-9][0-9,]*)\b", re.IGNORECASE)


def normalize_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def is_blank_or_not_captured(value: object) -> bool:
    text = normalize_text(value).lower()
    return (
        not text
        or text == "not captured"
        or text == "not applicable"
        or text.startswith("no dedicated support/privacy")
    )


def field_completeness(value: object) -> float:
    text = normalize_text(value).lower()
    if is_blank_or_not_captured(value):
        return 0.0
    if "not captured" in text or "unclear" in text or "likely" in text:
        return 0.5
    return 1.0


def parsed_limit_value(limit_amount: object) -> int | None:
    text = normalize_text(limit_amount)
    values = [int(match.replace(",", "")) for match in LIMIT_PATTERN.findall(text)]
    return max(values) if values else None


def classify_product_layer(row: dict[str, object]) -> tuple[str, str]:
    text = " ".join(
        [
            normalize_text(row.get("product_or_signal")),
            normalize_text(row.get("product_type_en")),
            normalize_text(row.get("segment_en")),
        ]
    ).lower()
    if "privacy" in text or "account control" in text or "account-control" in text:
        return "运营/隐私能力", "Privacy and account-control capability"
    if "wallet" in text or "payment" in text:
        return "支付/钱包能力", "Payment and wallet capability"
    if "invoice" in text or "receivables" in text:
        return "SME/经营融资", "SME operating finance"
    if "order finance" in text:
        return "SME/经营融资", "SME operating finance"
    if "sme" in text or "business loan" in text:
        return "SME/经营融资", "SME operating finance"
    if "agri" in text or "farm" in text:
        return "农业金融", "Agriculture finance"
    if "salary" in text:
        return "工资/收入型短贷", "Salary or income-linked short-term credit"
    if "collateral" in text or "asset-backed" in text:
        return "抵押/担保贷款", "Collateral-backed credit"
    if "driver" in text or "platform-driver" in text:
        return "职业/平台场景贷款", "Occupation or platform-context credit"
    if "women" in text:
        return "细分客群贷款", "Segment-focused credit"
    if "defence" in text or "civil servant" in text or "employment" in text:
        return "稳定雇佣客群贷款", "Stable-employment segment credit"
    if "personal loan" in text or "larger personal" in text:
        return "大额个人贷款", "Larger personal credit"
    if "microloan" in text or "instant loan" in text or "short-term small loan" in text:
        return "短期小额贷", "Short-term microcredit"
    return "其他贷款/信号", "Other credit or signal"


def classify_limit_tier(limit_amount: object) -> tuple[str, str, str]:
    text = normalize_text(limit_amount).lower()
    value = parsed_limit_value(limit_amount)
    if text == "not applicable":
        return "", "非额度能力项", "Non-limit capability"
    if value is None:
        if "bigger loan" in text:
            return "", "较大额/抵押信号但未披露额度", "Higher-limit/collateral signal, limit not disclosed"
        return "", "未捕捉额度", "Limit not captured"
    if value <= 1_000:
        return str(value), "微额 <= K1,000", "Micro <= K1,000"
    if value <= 6_000:
        return str(value), "小额 K1,001-K6,000", "Small K1,001-K6,000"
    if value <= 10_000:
        return str(value), "短期现金 K6,001-K10,000", "Cash advance K6,001-K10,000"
    if value <= 250_000:
        return str(value), "大额个人 K10,001-K250,000", "Larger personal K10,001-K250,000"
    return str(value), "企业级 > K250,000", "Business-scale > K250,000"


def classify_speed_tier(speed_claim: object) -> tuple[str, str]:
    text = normalize_text(speed_claim).lower()
    if is_blank_or_not_captured(speed_claim):
        return "未捕捉速度承诺", "Speed promise not captured"
    if "coming soon" in text and ("instant" in text or "minutes" in text or "seconds" in text):
        return "混合/待确认速度承诺", "Mixed speed promise, needs verification"
    if "24hrs" in text or "24 hours" in text or "24hrs" in text:
        return "24小时审批/到账话术", "24-hour approval or payout wording"
    if "30 seconds" in text or "5 minutes" in text or "within minutes" in text or "instant" in text or "immediately" in text:
        return "即时/分钟级承诺", "Instant or minute-level promise"
    if "subject to" in text or "eligibility" in text or "verification" in text:
        return "条件型速度承诺", "Conditional speed promise"
    if "seamless" in text or "convenient" in text:
        return "便利性话术，非明确速度", "Convenience wording, not explicit speed"
    return "一般速度叙事", "General speed wording"


def classify_payment_maturity(payment_or_disbursement: object) -> tuple[str, str]:
    text = normalize_text(payment_or_disbursement).lower()
    if text == "not applicable":
        return "非贷款支付项", "Non-loan payment capability"
    if is_blank_or_not_captured(payment_or_disbursement):
        return "未捕捉支付/放款路径", "Payment or payout path not captured"
    if any(term in text for term in ["mobile money", "mobile payments", "wallet", "airtel", "banks"]):
        return "明确移动钱/银行支付轨道", "Explicit mobile-money or bank rail"
    if "account or creditors" in text or "creditors" in text:
        return "账户/债权人放款线索", "Account or creditor payout clue"
    if "receivables" in text or "cash collection" in text or "purchase order" in text:
        return "经营现金流还款/放款线索", "Operating cash-flow repayment or funding clue"
    if "fuel" in text or "maintenance" in text:
        return "用途场景线索", "Use-case funding clue"
    return "有支付/资金用途线索", "Payment or use-of-funds clue"


def classify_support_privacy_maturity(support_privacy_ops: object) -> tuple[str, str]:
    text = normalize_text(support_privacy_ops).lower()
    if is_blank_or_not_captured(support_privacy_ops):
        return "未捕捉客服/隐私入口", "Support/privacy route not captured"
    has_support = any(term in text for term in ["support@", "support", "hotline", "consumer hotline"])
    has_privacy = any(term in text for term in ["privacy", "account delete", "account control", "agreement"])
    if has_support and has_privacy:
        return "客服 + 隐私/账户控制入口", "Support plus privacy/account-control route"
    if has_privacy:
        return "隐私/账户控制入口", "Privacy/account-control route"
    if has_support:
        return "公开客服入口", "Public support route"
    return "运营入口线索", "Operating route clue"


def expected_gap_fields(row: dict[str, object]) -> list[tuple[str, str, str]]:
    layer_en = normalize_text(row.get("product_layer_en"))
    if layer_en == "Privacy and account-control capability":
        return [("support_privacy_ops", "客服/隐私入口仍需细读", "Support/privacy detail needs deeper read")]
    if layer_en == "Payment and wallet capability":
        return [
            ("payment_or_disbursement", "支付/钱包路径未明确", "Payment/wallet route not clear"),
            ("pricing_or_disclosure", "费用/合作成本未明确", "Fees or partnership cost not clear"),
            ("support_privacy_ops", "失败交易/客服入口未捕捉", "Failed-transaction/support route not captured"),
        ]
    return [
        ("limit_amount", "额度未捕捉", "Limit not captured"),
        ("tenor_or_repayment", "期限/还款节奏未捕捉", "Tenor or repayment rhythm not captured"),
        ("pricing_or_disclosure", "费率/费用未明确", "Rate or fees not clear"),
        ("speed_claim", "审批/放款速度未捕捉", "Approval or payout speed not captured"),
        ("payment_or_disbursement", "放款/还款支付路径未捕捉", "Payout or repayment rail not captured"),
        ("support_privacy_ops", "客服/投诉/隐私入口未捕捉", "Support, dispute, or privacy route not captured"),
    ]


def data_completeness_score(row: dict[str, object]) -> int:
    fields = expected_gap_fields(row)
    if not fields:
        return 0
    score = sum(field_completeness(row.get(field_name)) for field_name, _, _ in fields)
    return round(score / len(fields) * 100)


def gap_flags(row: dict[str, object]) -> tuple[str, str]:
    gaps_cn: list[str] = []
    gaps_en: list[str] = []
    for field_name, label_cn, label_en in expected_gap_fields(row):
        if field_completeness(row.get(field_name)) < 1:
            gaps_cn.append(label_cn)
            gaps_en.append(label_en)
    return "；".join(gaps_cn) if gaps_cn else "暂无核心字段缺口", "; ".join(gaps_en) if gaps_en else "No core field gap"


def matrix_priority(row: dict[str, object]) -> tuple[str, str]:
    layer_en = normalize_text(row.get("product_layer_en"))
    payment_en = normalize_text(row.get("payment_maturity_en"))
    speed_en = normalize_text(row.get("speed_tier_en"))
    support_en = normalize_text(row.get("support_privacy_maturity_en"))
    score = int(row.get("data_completeness_score") or 0)
    limit_value = parsed_limit_value(row.get("limit_amount")) or 0

    if "privacy" in layer_en.lower() or "privacy/account-control" in support_en.lower():
        return "高：运营/隐私体验需优先回源", "High: verify operating/privacy experience first"
    if limit_value >= 250_000:
        return "高：大额/SME 风险权重高", "High: larger-ticket or SME risk weight"
    if "Explicit mobile-money" in payment_en and ("Instant" in speed_en or "24-hour" in speed_en):
        return "高：速度 + 支付轨道影响放款体验", "High: speed plus rail affects payout experience"
    if score < 50:
        return "中：公开字段缺口较多，适合继续补证", "Medium: many public-field gaps, continue evidence capture"
    return "中：可纳入常规监控", "Medium: keep in regular monitoring"


def competitor_positioning(row: dict[str, object]) -> tuple[str, str]:
    layer = normalize_text(row.get("product_layer_en")).lower()
    payment = normalize_text(row.get("payment_maturity_en")).lower()
    speed = normalize_text(row.get("speed_tier_en")).lower()
    limit_tier = normalize_text(row.get("limit_tier_en")).lower()
    if "short-term microcredit" in layer and ("instant" in speed or "mobile-money" in payment):
        return "App-first 小额现金贷", "App-first microcash lender"
    if "salary" in layer:
        return "收入/工资锚定短贷", "Income or salary-linked short credit"
    if "larger personal" in layer:
        return "大额个人信贷", "Larger-ticket personal credit"
    if "sme operating" in layer and "business-scale" in limit_tier:
        return "企业级 SME 融资", "Business-scale SME finance"
    if "sme operating" in layer:
        return "经营现金流融资", "Operating cash-flow finance"
    if "agriculture" in layer:
        return "农业周期金融", "Agriculture-cycle finance"
    if "payment" in layer:
        return "支付/钱包生态能力", "Payment or wallet ecosystem capability"
    if "privacy" in layer:
        return "App 信任与账户控制能力", "App trust and account-control capability"
    if "collateral" in layer:
        return "抵押/担保型更大额信贷", "Collateral-backed larger credit"
    return "细分客群/场景贷款", "Segment or use-case lending"


def operating_risk_focus(row: dict[str, object]) -> tuple[str, str]:
    gaps = normalize_text(row.get("gap_flags_en")).lower()
    payment = normalize_text(row.get("payment_maturity_en")).lower()
    support = normalize_text(row.get("support_privacy_maturity_en")).lower()
    focus_cn: list[str] = []
    focus_en: list[str] = []
    if "rate or fees" in gaps or "fees" in gaps:
        focus_cn.append("费用/总成本披露")
        focus_en.append("fee and total-cost disclosure")
    if "payment" in payment or "rail" in payment or "payout" in gaps:
        focus_cn.append("放款/还款支付轨道")
        focus_en.append("payout and repayment rails")
    if "support" in gaps or "support" in support or "privacy" in support:
        focus_cn.append("客服/投诉/隐私入口")
        focus_en.append("support, dispute, and privacy routes")
    if "tenor" in gaps or "repayment" in gaps:
        focus_cn.append("期限/还款节奏")
        focus_en.append("tenor and repayment rhythm")
    if not focus_cn:
        focus_cn.append("持续常规监控")
        focus_en.append("regular monitoring")
    return "；".join(focus_cn), "; ".join(focus_en)


def enrich_matrix_row(row: dict[str, object]) -> dict[str, object]:
    product_layer_cn, product_layer_en = classify_product_layer(row)
    limit_value_zmw, limit_tier_cn, limit_tier_en = classify_limit_tier(row.get("limit_amount"))
    speed_tier_cn, speed_tier_en = classify_speed_tier(row.get("speed_claim"))
    payment_maturity_cn, payment_maturity_en = classify_payment_maturity(row.get("payment_or_disbursement"))
    support_privacy_maturity_cn, support_privacy_maturity_en = classify_support_privacy_maturity(row.get("support_privacy_ops"))
    row.update(
        {
            "product_layer_cn": product_layer_cn,
            "product_layer_en": product_layer_en,
            "limit_value_zmw": limit_value_zmw,
            "limit_tier_cn": limit_tier_cn,
            "limit_tier_en": limit_tier_en,
            "speed_tier_cn": speed_tier_cn,
            "speed_tier_en": speed_tier_en,
            "payment_maturity_cn": payment_maturity_cn,
            "payment_maturity_en": payment_maturity_en,
            "support_privacy_maturity_cn": support_privacy_maturity_cn,
            "support_privacy_maturity_en": support_privacy_maturity_en,
        }
    )
    row["data_completeness_score"] = data_completeness_score(row)
    gap_flags_cn, gap_flags_en = gap_flags(row)
    row["gap_flags_cn"] = gap_flags_cn
    row["gap_flags_en"] = gap_flags_en
    matrix_priority_cn, matrix_priority_en = matrix_priority(row)
    row["matrix_priority_cn"] = matrix_priority_cn
    row["matrix_priority_en"] = matrix_priority_en
    positioning_cn, positioning_en = competitor_positioning(row)
    row["competitor_positioning_cn"] = positioning_cn
    row["competitor_positioning_en"] = positioning_en
    risk_focus_cn, risk_focus_en = operating_risk_focus(row)
    row["operating_risk_focus_cn"] = risk_focus_cn
    row["operating_risk_focus_en"] = risk_focus_en
    return row


def build_product_matrix(conn: sqlite3.Connection) -> list[dict[str, object]]:
    lookup = signal_lookup(conn)
    rows: list[dict[str, object]] = []
    for seed in MATRIX_SEEDS:
        row: dict[str, object] = {
            "institution": seed.institution,
            "product_or_signal": seed.product_or_signal,
            "product_type_cn": seed.product_type_cn,
            "product_type_en": seed.product_type_en,
            "segment_cn": seed.segment_cn,
            "segment_en": seed.segment_en,
            "limit_amount": seed.limit_amount,
            "tenor_or_repayment": seed.tenor_or_repayment,
            "pricing_or_disclosure": seed.pricing_or_disclosure,
            "speed_claim": seed.speed_claim,
            "payment_or_disbursement": seed.payment_or_disbursement,
            "support_privacy_ops": seed.support_privacy_ops,
            "business_interpretation_cn": seed.business_interpretation_cn,
            "business_interpretation_en": seed.business_interpretation_en,
            "next_questions_cn": seed.next_questions_cn,
            "next_questions_en": seed.next_questions_en,
            "source_signal_ids": ", ".join(str(item) for item in seed.source_signal_ids),
            "source_links": source_links(seed, lookup),
            "source_status": source_status(seed, lookup),
            "confidence": seed.confidence,
            "status": seed.status,
        }
        rows.append(enrich_matrix_row(row))
    return rows


def escape_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def choose_text(cn: str, en: str, language: str = "zh") -> str:
    return en if language == "en" else cn


def language_field(base: str, language: str = "zh") -> str:
    return f"{base}_en" if language == "en" else f"{base}_cn"


def count_markdown_table(rows: list[dict[str, object]], field: str, title_cn: str, title_en: str, language: str = "zh") -> str:
    counts = Counter(normalize_text(row.get(field)) or "未分类 | Unclassified" for row in rows)
    if not counts:
        return choose_text("_暂无数据。_", "_No data._", language)
    lines = [
        choose_text(f"| {title_cn} | 数量 |", f"| {title_en} | Count |", language),
        "| --- | ---: |",
    ]
    for label, count in counts.most_common():
        lines.append(f"| {escape_cell(label)} | {count} |")
    return "\n".join(lines)


def top_gap_table(rows: list[dict[str, object]], language: str = "zh") -> str:
    gap_counter: Counter[str] = Counter()
    for row in rows:
        for gap in normalize_text(row.get(language_field("gap_flags", language))).split("；"):
            gap = gap.strip()
            if gap and gap != "暂无核心字段缺口":
                gap_counter[gap] += 1
    if not gap_counter:
        return choose_text("_暂无核心字段缺口。_", "_No core field gaps._", language)
    lines = [
        choose_text("| 缺口 | 出现次数 |", "| Gap | Count |", language),
        "| --- | ---: |",
    ]
    for gap, count in gap_counter.most_common():
        lines.append(f"| {escape_cell(gap)} | {count} |")
    return "\n".join(lines)


def matrix_markdown_table(rows: Iterable[dict[str, object]], limit: int | None = None, language: str = "zh") -> str:
    selected = list(rows)
    if limit is not None:
        selected = selected[:limit]
    if not selected:
        return choose_text("_暂无竞品产品矩阵。_", "_No competitor product matrix rows yet._", language)
    lines = [
        choose_text(
            "| 机构 | 产品/信号 | 定位 | 产品层 | 额度档 | 完整度 | 运营风险焦点 | 关键缺口 | 来源 |",
            "| Institution | Product/Signal | Positioning | Product Layer | Limit Tier | Score | Ops Focus | Key Gaps | Sources |",
            language,
        ),
        "| --- | --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in selected:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["institution"]),
                    escape_cell(row["product_or_signal"]),
                    escape_cell(row[language_field("competitor_positioning", language)]),
                    escape_cell(row[language_field("product_layer", language)]),
                    escape_cell(f"{row['limit_amount']} - {row[language_field('limit_tier', language)]}"),
                    escape_cell(row["data_completeness_score"]),
                    escape_cell(row[language_field("operating_risk_focus", language)]),
                    escape_cell(row[language_field("gap_flags", language)]),
                    row["source_links"],
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_matrix_markdown(rows: list[dict[str, object]], language: str = "zh") -> str:
    institutions = sorted({row["institution"] for row in rows})
    direct_limit_rows = [row for row in rows if row["limit_amount"] and row["limit_amount"] != "Not captured" and row["limit_amount"] != "Not applicable"]
    payment_rows = [row for row in rows if row["payment_or_disbursement"] and row["payment_or_disbursement"] != "Not captured"]
    ops_rows = [
        row
        for row in rows
        if row["support_privacy_ops"]
        and row["support_privacy_ops"] != "No dedicated support/privacy detail captured"
    ]
    average_score = round(sum(int(row.get("data_completeness_score") or 0) for row in rows) / len(rows)) if rows else 0
    product_layer_field = language_field("product_layer", language)
    limit_tier_field = language_field("limit_tier", language)
    speed_tier_field = language_field("speed_tier", language)
    payment_maturity_field = language_field("payment_maturity", language)
    competitor_positioning_field = language_field("competitor_positioning", language)
    reading_method = choose_text(
        "- 先比较额度、期限、速度承诺，再比较支付轨道和客服/隐私入口。\n"
        "- 把 K500/K6,000 这类短期小额产品与 K250,000/K1,000,000 这类个人/SME 贷款分开看。\n"
        "- 对 Coming soon、instant、30 seconds、24hrs 等营销语保持保守，回源确认它指申请、审批还是实际放款。\n"
        "- 完整度分数是研究字段完整度，不是产品质量分数；分数低通常代表下一步要继续补证。\n"
        "- Google Play listing 和公开评论层仍未纳入默认矩阵，需要单独确认后启用。",
        "- Compare limits, tenor, and speed promises first, then payment rails and support/privacy entry points.\n"
        "- Separate short-term small-ticket products such as K500/K6,000 from personal/SME loans such as K250,000/K1,000,000.\n"
        "- Treat marketing language such as Coming soon, instant, 30 seconds, and 24hrs conservatively; source-check whether it refers to application, approval, or actual payout.\n"
        "- Completeness is a research-field score, not a product-quality score; low scores usually mean the next step is evidence collection.\n"
        "- Google Play listings and public-review layers are still not part of the default matrix and should be enabled only after separate confirmation.",
        language,
    )
    return f"""# {choose_text('竞品产品矩阵', 'Competitor Product Matrix', language)} - {today_label()}

{choose_text('这是一份基于已复核公开来源信号整理的个人研究矩阵。它不是完整市场报告，也不是法律/合规结论；字段为空代表当前公开信号未捕捉到，不代表来源页面一定没有。', 'This is a personal research matrix based on reviewed public-source signals. It is not a complete market report or legal/compliance conclusion. Blank or "not captured" fields mean the current signal did not capture the information, not that the source page lacks it.', language)}

## 1. {choose_text('摘要', 'Summary', language)}

- {choose_text('机构数', 'Institutions', language)}: {len(institutions)}
- {choose_text('矩阵行', 'Matrix rows', language)}: {len(rows)}
- {choose_text('有明确额度', 'Rows with explicit limit', language)}: {len(direct_limit_rows)}
- {choose_text('有支付/放款线索', 'Rows with payment/payout clues', language)}: {len(payment_rows)}
- {choose_text('有客服/隐私/账户控制线索', 'Rows with support/privacy/account-control clues', language)}: {len(ops_rows)}
- {choose_text('平均公开字段完整度', 'Average public-field completeness', language)}: {average_score}/100

## 2. {choose_text('横向比较摘要', 'Comparison Summary', language)}

### 2.1 {choose_text('产品层', 'Product Layer', language)}

{count_markdown_table(rows, product_layer_field, "产品层", "Product Layer", language)}

### 2.2 {choose_text('额度档', 'Limit Tier', language)}

{count_markdown_table(rows, limit_tier_field, "额度档", "Limit Tier", language)}

### 2.3 {choose_text('速度承诺', 'Speed Promise', language)}

{count_markdown_table(rows, speed_tier_field, "速度承诺", "Speed Promise", language)}

### 2.4 {choose_text('支付/放款成熟度', 'Payment/Payout Maturity', language)}

{count_markdown_table(rows, payment_maturity_field, "支付/放款成熟度", "Payment/Payout Maturity", language)}

### 2.5 {choose_text('主要信息缺口', 'Main Evidence Gaps', language)}

{top_gap_table(rows, language)}

### 2.6 {choose_text('竞品定位', 'Competitor Positioning', language)}

{count_markdown_table(rows, competitor_positioning_field, "竞品定位", "Competitor Positioning", language)}

## 3. {choose_text('产品矩阵 3.0', 'Product Matrix 3.0', language)}

{matrix_markdown_table(rows, language=language)}

## 4. {choose_text('阅读方法', 'How To Read', language)}

{reading_method}
"""


def write_csv(rows: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["institution"])
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def write_markdown(content: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a source-linked competitor product matrix")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--brief-dir", type=Path, default=DEFAULT_BRIEF_DIR)
    parser.add_argument("--language", choices=["zh", "en"], default="zh")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        raise SystemExit(f"Database not found: {args.db}")
    conn = connect(args.db)
    rows = build_product_matrix(conn)
    csv_path = write_csv(rows, args.output_dir / "lending_ops_competitor_product_matrix.csv")
    md_path = write_markdown(
        render_matrix_markdown(rows, language=args.language),
        args.brief_dir / f"zambia_digital_lending_competitor_product_matrix_{today_label()}.md",
    )
    print(f"Wrote {len(rows)} matrix row(s) to {csv_path}")
    print(f"Wrote Markdown matrix to {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
