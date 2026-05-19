"""Competitor coverage and policy-impact read models.

This module is intentionally source-linked and conservative. It expands the
research scope beyond the first four competitors while keeping app listings,
social pages, and review surfaces as candidates until manually approved.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CompetitorProfile:
    institution: str
    tier_key: str
    tier_cn: str
    tier_en: str
    product_focus_cn: str
    product_focus_en: str
    evidence_status_cn: str
    evidence_status_en: str
    watch_priority_cn: str
    watch_priority_en: str
    primary_signals_cn: str
    primary_signals_en: str
    watch_fields: tuple[str, ...]
    source_links: tuple[str, ...]


COMPETITOR_PROFILES: tuple[CompetitorProfile, ...] = (
    CompetitorProfile(
        institution="FLoan",
        tier_key="core_digital_lending",
        tier_cn="核心数字贷款 App",
        tier_en="Core digital lending app",
        product_focus_cn="App-first 小额现金贷、额度和费用披露线索",
        product_focus_en="App-first small-ticket cash loan with limit and fee-disclosure clues",
        evidence_status_cn="已有矩阵行和官网信号",
        evidence_status_en="Matrix rows and website signals already captured",
        watch_priority_cn="高",
        watch_priority_en="High",
        primary_signals_cn="额度、费用披露、移动支付、隐私/删除账号入口",
        primary_signals_en="Limit, fee disclosure, mobile payments, privacy/account deletion",
        watch_fields=("limit_amount", "pricing_or_disclosure", "payment_or_disbursement", "privacy_policy", "support"),
        source_links=("https://www.floan.co/",),
    ),
    CompetitorProfile(
        institution="Lupiya",
        tier_key="core_digital_lending",
        tier_cn="核心数字贷款 App",
        tier_en="Core digital lending app",
        product_focus_cn="多产品线：短期贷、工资客群、女性/农业/平台司机",
        product_focus_en="Multi-product lender: short-term, salary, women, agriculture, platform-driver segments",
        evidence_status_cn="已有矩阵行和官网信号",
        evidence_status_en="Matrix rows and website signals already captured",
        watch_priority_cn="高",
        watch_priority_en="High",
        primary_signals_cn="客群分层、期限、费用、上线状态、产品叙事变化",
        primary_signals_en="Segmentation, tenor, fees, launch status, product narrative changes",
        watch_fields=("segment", "tenor_or_repayment", "pricing_or_disclosure", "speed_claim", "company_news"),
        source_links=("https://www.lupiya.com/", "https://www.lupiya.com/loans"),
    ),
    CompetitorProfile(
        institution="PowerKwacha",
        tier_key="core_digital_lending",
        tier_cn="核心数字贷款 App",
        tier_en="Core digital lending app",
        product_focus_cn="小额贷款 App、客服、隐私、账号删除入口",
        product_focus_en="Small-ticket loan app with support, privacy, and account-deletion clues",
        evidence_status_cn="已有官网信号；App listing 仍为候选",
        evidence_status_en="Website signals exist; app listing remains candidate",
        watch_priority_cn="高",
        watch_priority_en="High",
        primary_signals_cn="隐私政策、客服入口、Google Play 候选、费用和还款文案",
        primary_signals_en="Privacy policy, support route, Google Play candidate, fee and repayment wording",
        watch_fields=("privacy_policy", "support", "pricing_or_disclosure", "app_listing", "market_voice"),
        source_links=("https://powerkwacha.app/", "https://play.google.com/store/apps/details?id=zambia.powerkwacha"),
    ),
    CompetitorProfile(
        institution="PremierCredit",
        tier_key="core_digital_lending",
        tier_cn="核心数字贷款 App",
        tier_en="Core digital lending app",
        product_focus_cn="工资预支、个人贷、SME 贷款和移动钱包申请流程",
        product_focus_en="Salary advance, personal loans, SME loans, and mobile-wallet application flow",
        evidence_status_cn="已有矩阵行和官网信号",
        evidence_status_en="Matrix rows and website signals already captured",
        watch_priority_cn="高",
        watch_priority_en="High",
        primary_signals_cn="额度层级、工资客群、SME、移动钱包、审批速度",
        primary_signals_en="Limit tiers, salary segments, SME, mobile wallet, approval speed",
        watch_fields=("limit_amount", "segment", "payment_or_disbursement", "speed_claim", "pricing_or_disclosure"),
        source_links=("https://www.premiercredit.co.zm/", "https://www.premiercredit.co.zm/borrow/"),
    ),
    CompetitorProfile(
        institution="SuperKwacha",
        tier_key="core_digital_lending",
        tier_cn="核心数字贷款 App 候选",
        tier_en="Core digital lending app candidate",
        product_focus_cn="Google Play 公开 listing 显示额度、期限、APR/费用、安全和更新时间线索",
        product_focus_en="Google Play listing exposes limit, tenor, APR/fees, safety, and update clues",
        evidence_status_cn="公开 App listing 候选，默认不抓个人评论身份信息",
        evidence_status_en="Public app-listing candidate; personal review identity is not collected by default",
        watch_priority_cn="高",
        watch_priority_en="High",
        primary_signals_cn="App 更新时间、费用披露、数据安全、评分/评论主题",
        primary_signals_en="App update date, fee disclosure, data safety, rating/review themes",
        watch_fields=("app_listing", "pricing_or_disclosure", "privacy_policy", "market_voice", "support"),
        source_links=("https://play.google.com/store/apps/details?hl=en-US&id=com.superkwacha.app",),
    ),
    CompetitorProfile(
        institution="Finedge / ka Something",
        tier_key="core_digital_lending",
        tier_cn="核心数字贷款/多渠道候选",
        tier_en="Core digital lending / multichannel candidate",
        product_focus_cn="App、web、USSD 即时贷款；移动钱包和银行还款线索",
        product_focus_en="Instant digital loans through app, web, and USSD; mobile-money and bank-repayment clues",
        evidence_status_cn="官网公开来源候选",
        evidence_status_en="Public website candidate",
        watch_priority_cn="高",
        watch_priority_en="High",
        primary_signals_cn="USSD、放款/还款渠道、资格、费用、客服",
        primary_signals_en="USSD, disbursement/repayment channel, eligibility, fees, support",
        watch_fields=("channel_mix", "payment_or_disbursement", "pricing_or_disclosure", "support", "eligibility"),
        source_links=("https://www.finedge.co.zm/aboutus",),
    ),
    CompetitorProfile(
        institution="Phindu Credit",
        tier_key="core_digital_lending",
        tier_cn="核心个人/工资贷候选",
        tier_en="Core personal/salary lending candidate",
        product_focus_cn="个人贷款、salary loan、快速申请文案",
        product_focus_en="Personal loans, salary loans, and fast-application messaging",
        evidence_status_cn="官网公开来源候选",
        evidence_status_en="Public website candidate",
        watch_priority_cn="中高",
        watch_priority_en="Medium-high",
        primary_signals_cn="薪资客群、资格、还款周期、费用披露、客服",
        primary_signals_en="Salary segment, eligibility, repayment rhythm, fee disclosure, support",
        watch_fields=("segment", "eligibility", "tenor_or_repayment", "pricing_or_disclosure", "support"),
        source_links=("https://phindu.com/",),
    ),
    CompetitorProfile(
        institution="FairMoney Zambia",
        tier_key="core_digital_lending",
        tier_cn="核心数字贷款候选",
        tier_en="Core digital lending candidate",
        product_focus_cn="个人贷款、FAQ、App listing 候选",
        product_focus_en="Personal loans, FAQ, and app-listing candidate",
        evidence_status_cn="已在 watchlist 中有公开页面候选",
        evidence_status_en="Public-page candidate already exists in watchlist",
        watch_priority_cn="中高",
        watch_priority_en="Medium-high",
        primary_signals_cn="额度、利率/费用、FAQ、支持、App listing",
        primary_signals_en="Limit, rate/fees, FAQ, support, app listing",
        watch_fields=("limit_amount", "pricing_or_disclosure", "support", "app_listing", "market_voice"),
        source_links=("https://fairmoney.co.zm/personal-loans", "https://fairmoney.co.zm/faqs-zm/"),
    ),
    CompetitorProfile(
        institution="Micro Finance Zambia",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻微贷/薪资贷",
        tier_en="Adjacent microfinance / payroll lender",
        product_focus_cn="工资扣款、个人/企业贷款、传统微贷数字化周边",
        product_focus_en="Payroll-linked, personal/business lending, and adjacent MFI digitization",
        evidence_status_cn="公开官网候选；用于比较传统微贷与 App-first 模式",
        evidence_status_en="Public website candidate for comparing traditional MFI and app-first models",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="工资还款、资料要求、分支/线上入口、费用披露",
        primary_signals_en="Payroll repayment, documentation, branch/online entry, fee disclosure",
        watch_fields=("segment", "tenor_or_repayment", "pricing_or_disclosure", "channel_mix", "support"),
        source_links=("https://www.microfin.co.zm/",),
    ),
    CompetitorProfile(
        institution="SmartFin",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻微贷/数字信用候选",
        tier_en="Adjacent microfinance / digital-credit candidate",
        product_focus_cn="公开公司/LinkedIn 信息显示个人和中小企业信用活动线索",
        product_focus_en="Public company/LinkedIn information suggests individual and SME-credit activity",
        evidence_status_cn="社交/公司页候选，默认人工回源",
        evidence_status_en="Social/company-page candidate; manual source review by default",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="公司动态、招聘、产品定位、合作伙伴",
        primary_signals_en="Company updates, hiring, product positioning, partnerships",
        watch_fields=("company_news", "hiring", "segment", "partnerships", "support"),
        source_links=("https://www.linkedin.com/company/smartfin-zambia/",),
    ),
    CompetitorProfile(
        institution="Agora Microfinance",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻微贷/农村金融",
        tier_en="Adjacent microfinance / rural finance",
        product_focus_cn="农村和低收入客群微贷，适合观察社会影响和财务披露",
        product_focus_en="Rural and low-income microfinance; useful for social-impact and financial-disclosure watch",
        evidence_status_cn="公开官网候选",
        evidence_status_en="Public website candidate",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="社会影响、网点/代理、财务披露、客群变化",
        primary_signals_en="Social impact, branch/agent network, financial disclosure, segment changes",
        watch_fields=("financial_disclosure", "social_impact", "segment", "channel_mix", "company_news"),
        source_links=("https://www.agoramicrofinance.com/",),
    ),
    CompetitorProfile(
        institution="Bayport Zambia",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻薪资贷/微贷",
        tier_en="Adjacent payroll lender / microfinance",
        product_focus_cn="薪资类和多国集团背景，适合观察财报、监管和公司层面变化",
        product_focus_en="Payroll lending and regional group context; useful for financial, regulatory, and company watch",
        evidence_status_cn="公开官网/集团披露候选",
        evidence_status_en="Public website/group disclosure candidate",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="财报/集团披露、工资客群、监管许可证、投诉风险",
        primary_signals_en="Financial/group disclosure, salary segment, licensing, complaint risk",
        watch_fields=("financial_disclosure", "segment", "licensing", "complaints", "company_news"),
        source_links=("https://www.bayport.co.zm/",),
    ),
    CompetitorProfile(
        institution="FINCA Zambia",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻微贷/金融包容",
        tier_en="Adjacent microfinance / financial inclusion",
        product_focus_cn="微贷和金融包容，适合观察数字化、客群和社会影响",
        product_focus_en="Microfinance and financial inclusion; useful for digitization, segment, and social-impact watch",
        evidence_status_cn="公开官网/集团披露候选",
        evidence_status_en="Public website/group disclosure candidate",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="金融包容、数字化入口、财务和社会影响披露",
        primary_signals_en="Financial inclusion, digital entry points, financial and social-impact disclosure",
        watch_fields=("social_impact", "financial_disclosure", "channel_mix", "segment", "company_news"),
        source_links=("https://finca.co.zm/",),
    ),
    CompetitorProfile(
        institution="VisionFund Zambia",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻微贷/社会影响金融",
        tier_en="Adjacent microfinance / impact finance",
        product_focus_cn="社会影响和小微客群，适合观察非 App-first 信贷替代方案",
        product_focus_en="Impact finance and small-business segments; useful for non-app-first lending alternatives",
        evidence_status_cn="公开官网候选",
        evidence_status_en="Public website candidate",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="小微企业、农业、社会影响、线下/数字化入口",
        primary_signals_en="Microenterprise, agriculture, social impact, offline/digital entry points",
        watch_fields=("segment", "social_impact", "channel_mix", "tenor_or_repayment", "company_news"),
        source_links=("https://www.visionfund.org/where-we-work/africa/zambia",),
    ),
    CompetitorProfile(
        institution="LOLC Finance Zambia",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻消费/微型金融",
        tier_en="Adjacent consumer / microfinance",
        product_focus_cn="区域金融集团背景，适合观察产品线、分期和监管披露",
        product_focus_en="Regional finance-group context; useful for product, installment, and regulatory-disclosure watch",
        evidence_status_cn="公开官网候选",
        evidence_status_en="Public website candidate",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="产品线、分期、资产融资、公司披露",
        primary_signals_en="Product lines, installment, asset finance, company disclosure",
        watch_fields=("product_layer", "tenor_or_repayment", "financial_disclosure", "company_news", "licensing"),
        source_links=("https://www.lolcfinance.co.zm/",),
    ),
    CompetitorProfile(
        institution="MFinance",
        tier_key="adjacent_microfinance_payroll",
        tier_cn="相邻微贷/数字入口候选",
        tier_en="Adjacent microfinance / digital-entry candidate",
        product_focus_cn="公开页面候选，用于扩展微贷和数字入口观察面",
        product_focus_en="Public-page candidate for widening microfinance and digital-entry monitoring",
        evidence_status_cn="需人工回源确认",
        evidence_status_en="Manual source validation needed",
        watch_priority_cn="低到中",
        watch_priority_en="Low-medium",
        primary_signals_cn="产品层、线上申请、客服、费用披露",
        primary_signals_en="Product layer, online application, support, fee disclosure",
        watch_fields=("product_layer", "channel_mix", "support", "pricing_or_disclosure"),
        source_links=("https://www.mfinance.co.zm/",),
    ),
    CompetitorProfile(
        institution="Airtel Money Zambia",
        tier_key="rails_ecosystem",
        tier_cn="支付轨道/生态伙伴",
        tier_en="Payment rails / ecosystem partner",
        product_focus_cn="移动钱包、放款/还款通道和失败交易体验",
        product_focus_en="Mobile wallet, payout/repayment rails, and failed-transaction experience",
        evidence_status_cn="生态来源候选；不是贷款竞品，但会影响贷款运营",
        evidence_status_en="Ecosystem candidate; not a lender competitor, but affects lending operations",
        watch_priority_cn="中高",
        watch_priority_en="Medium-high",
        primary_signals_cn="放款到账、还款入账、失败交易、客服和代理网络",
        primary_signals_en="Payout posting, repayment posting, failed transactions, support, and agent network",
        watch_fields=("payment_or_disbursement", "channel_mix", "support", "market_voice", "partnerships"),
        source_links=("https://www.airtel.co.zm/airtel-money",),
    ),
    CompetitorProfile(
        institution="MTN MoMo Zambia",
        tier_key="rails_ecosystem",
        tier_cn="支付轨道/生态伙伴",
        tier_en="Payment rails / ecosystem partner",
        product_focus_cn="移动钱包、MoMo 生态和金融服务合作入口",
        product_focus_en="Mobile wallet, MoMo ecosystem, and financial-service partnership routes",
        evidence_status_cn="生态来源候选；不是贷款竞品，但会影响贷款运营",
        evidence_status_en="Ecosystem candidate; not a lender competitor, but affects lending operations",
        watch_priority_cn="中高",
        watch_priority_en="Medium-high",
        primary_signals_cn="钱包可用性、还款入口、代理网络、金融服务合作",
        primary_signals_en="Wallet availability, repayment routes, agent network, financial-service partnerships",
        watch_fields=("payment_or_disbursement", "channel_mix", "support", "partnerships", "market_voice"),
        source_links=("https://www.mtn.zm/momo/",),
    ),
    CompetitorProfile(
        institution="JUMO",
        tier_key="rails_ecosystem",
        tier_cn="信贷基础设施/生态伙伴",
        tier_en="Credit infrastructure / ecosystem partner",
        product_focus_cn="与移动运营商/金融机构合作的数字信贷基础设施候选",
        product_focus_en="Digital-credit infrastructure candidate through mobile-operator and financial-institution partnerships",
        evidence_status_cn="生态来源候选；用于观察合作、风控和资金方变化",
        evidence_status_en="Ecosystem candidate for partnership, risk, and funding-side changes",
        watch_priority_cn="中",
        watch_priority_en="Medium",
        primary_signals_cn="合作伙伴、市场扩张、风险模型、融资/资金方披露",
        primary_signals_en="Partners, market expansion, risk models, funding/funder disclosure",
        watch_fields=("partnerships", "company_news", "financial_disclosure", "social_impact", "channel_mix"),
        source_links=("https://www.jumo.world/",),
    ),
)


POLICY_THEMES: tuple[dict[str, object], ...] = (
    {
        "policy_key": "fees_disclosure",
        "policy_theme_cn": "费用、APR、总还款和营销披露",
        "policy_theme_en": "Fees, APR, total repayment, and marketing disclosure",
        "source_anchor_cn": "CCPC 消费者保护、BoZ 市场行为、公开产品页面",
        "source_anchor_en": "CCPC consumer protection, BoZ market conduct, public product pages",
        "watch_fields": ("pricing_or_disclosure", "limit_amount", "tenor_or_repayment", "speed_claim"),
        "impact_cn": "高 APR、服务费、逾期费或“instant/low interest”文案越强，越需要检查是否清楚说明总成本、期限和还款条件。",
        "impact_en": "The stronger APR, service-fee, late-fee, or instant/low-interest claims are, the more important total-cost, tenor, and repayment disclosure becomes.",
        "next_action_cn": "把每个核心 App 的费用、总还款、逾期费、期限和示例还款表拆成可比较字段。",
        "next_action_en": "Turn each core app's fee, total repayment, late fee, tenor, and example repayment table into comparable fields.",
    },
    {
        "policy_key": "data_privacy_permissions",
        "policy_theme_cn": "数据保护、权限、同意和删除账号",
        "policy_theme_en": "Data protection, permissions, consent, and account deletion",
        "source_anchor_cn": "Data Protection Commission、公开隐私政策、Google Play Data Safety",
        "source_anchor_en": "Data Protection Commission, public privacy policies, Google Play Data Safety",
        "watch_fields": ("privacy_policy", "app_listing", "support", "market_voice"),
        "impact_cn": "App-first 贷款通常依赖设备、身份、联系人或位置类数据线索；隐私政策和删除账号入口会直接影响信任、投诉和监管风险。",
        "impact_en": "App-first lending often depends on device, identity, contact, or location data clues; privacy and account-deletion routes affect trust, complaints, and regulatory risk.",
        "next_action_cn": "对核心 App 建立隐私政策、Data Safety、账号删除和客服入口的对照表。",
        "next_action_en": "Build a side-by-side table for privacy policy, Data Safety, account deletion, and support routes.",
    },
    {
        "policy_key": "complaints_dispute_handling",
        "policy_theme_cn": "投诉、争议处理和客服 SLA",
        "policy_theme_en": "Complaints, dispute handling, and support SLA",
        "source_anchor_cn": "ZICTA DFS 投诉入口、CCPC 通知、公开客服页面",
        "source_anchor_en": "ZICTA DFS complaint channel, CCPC notices, public support pages",
        "watch_fields": ("support", "market_voice", "payment_or_disbursement", "complaints"),
        "impact_cn": "放款失败、还款未入账、欺诈和客服不响应会从运营问题升级成投诉和声誉风险。",
        "impact_en": "Failed disbursement, unposted repayment, fraud, and weak support can move from operations issues into complaint and reputation risk.",
        "next_action_cn": "对每个竞品记录公开客服入口、投诉路径、退款/失败交易说明和是否有人工升级机制。",
        "next_action_en": "Track public support routes, complaint paths, refund/failed-transaction wording, and manual escalation options for each competitor.",
    },
    {
        "policy_key": "payment_rails_reconciliation",
        "policy_theme_cn": "支付轨道、放款/还款失败和对账",
        "policy_theme_en": "Payment rails, disbursement/repayment failures, and reconciliation",
        "source_anchor_cn": "BoZ 支付系统、电子货币、移动支付和转账公开文件",
        "source_anchor_en": "BoZ payment-system, e-money, mobile-payment, and money-transfer public documents",
        "watch_fields": ("payment_or_disbursement", "channel_mix", "support", "market_voice"),
        "impact_cn": "依赖 mobile money、银行转账或 USSD 的产品，需要重点观察失败交易、到账时效、退款、人工对账和客服脚本。",
        "impact_en": "Products relying on mobile money, bank transfer, or USSD need attention on failed transactions, payout timing, refunds, manual reconciliation, and support scripts.",
        "next_action_cn": "把所有放款/还款通道字段统一到矩阵，并把失败交易处理作为单独字段。",
        "next_action_en": "Normalize all disbursement/repayment channels into the matrix and add a separate failed-transaction handling field.",
    },
    {
        "policy_key": "company_financial_social_signals",
        "policy_theme_cn": "公司、财报和社会影响变化",
        "policy_theme_en": "Company, financial, and social-impact changes",
        "source_anchor_cn": "官网公告、年报、集团披露、LinkedIn、行业研究",
        "source_anchor_en": "Official news, annual reports, group disclosures, LinkedIn, and industry studies",
        "watch_fields": ("company_news", "financial_disclosure", "social_impact", "hiring", "partnerships"),
        "impact_cn": "融资、招聘、合作伙伴、亏损/盈利、社会影响披露会影响竞品扩张速度、风控偏好和渠道策略。",
        "impact_en": "Funding, hiring, partnerships, profit/loss, and social-impact disclosures affect expansion speed, risk appetite, and channel strategy.",
        "next_action_cn": "为相邻微贷和集团型玩家建立公司层事件流，而不是只看产品页。",
        "next_action_en": "Create a company-level event stream for adjacent MFIs and group-backed players instead of reading only product pages.",
    },
)


EVENT_SEEDS: tuple[dict[str, str], ...] = (
    {
        "institution": "SuperKwacha",
        "event_type_key": "product",
        "event_type_cn": "产品/App listing",
        "event_type_en": "Product / app listing",
        "event_cn": "公开 Google Play listing 可作为额度、期限、APR、Data Safety 和更新时间的候选监控入口。",
        "event_en": "Public Google Play listing can be used as a candidate source for limit, tenor, APR, Data Safety, and update timing.",
        "business_read_cn": "这类 App-first 产品最容易把费用披露、隐私权限和公开评论主题连接起来，应进入核心候选池。",
        "business_read_en": "This app-first product connects fee disclosure, privacy permissions, and public-review themes, so it belongs in the core candidate pool.",
        "source_link": "https://play.google.com/store/apps/details?hl=en-US&id=com.superkwacha.app",
    },
    {
        "institution": "Finedge / ka Something",
        "event_type_key": "product",
        "event_type_cn": "产品/渠道",
        "event_type_en": "Product / channel",
        "event_cn": "官网显示 app、web、USSD 数字贷款和 mobile money/bank repayment 线索。",
        "event_en": "Website shows app, web, USSD digital-loan clues and mobile-money/bank repayment language.",
        "business_read_cn": "USSD 和多通道入口会影响获客、身份核验、客服和失败交易处理方式。",
        "business_read_en": "USSD and multichannel entry affect acquisition, identity checks, support, and failed-transaction handling.",
        "source_link": "https://www.finedge.co.zm/aboutus",
    },
    {
        "institution": "Phindu Credit",
        "event_type_key": "product",
        "event_type_cn": "产品/工资客群",
        "event_type_en": "Product / salary segment",
        "event_cn": "官网公开个人贷款和 salary loan 定位。",
        "event_en": "Website presents personal-loan and salary-loan positioning.",
        "business_read_cn": "工资客群通常会改变授信资料、还款节奏和催收脚本，应与纯 App 小额现金贷分开比较。",
        "business_read_en": "Salary segments usually change documentation, repayment rhythm, and collections scripting, so they should be compared separately from pure app cash loans.",
        "source_link": "https://phindu.com/",
    },
    {
        "institution": "SmartFin",
        "event_type_key": "company",
        "event_type_cn": "公司/社交公开页",
        "event_type_en": "Company / public social page",
        "event_cn": "公开公司页面可用于观察招聘、合作伙伴和产品定位，但默认只做人工回源候选。",
        "event_en": "Public company pages can show hiring, partnerships, and positioning, but remain manual-review candidates by default.",
        "business_read_cn": "公司层动态能补足官网产品页看不到的扩张和渠道信号。",
        "business_read_en": "Company-level updates can reveal expansion and channel signals that product pages miss.",
        "source_link": "https://www.linkedin.com/company/smartfin-zambia/",
    },
    {
        "institution": "ZICTA / CCPC / BoZ public signals",
        "event_type_key": "policy_pressure",
        "event_type_cn": "政策压力",
        "event_type_en": "Policy pressure",
        "event_cn": "公开监管和消费者保护信号应映射到竞品费用披露、投诉、隐私和支付失败处理字段。",
        "event_en": "Public regulatory and consumer-protection signals should be mapped to competitor fee disclosure, complaints, privacy, and failed-payment handling fields.",
        "business_read_cn": "政策不只是一份文件；它会决定哪些竞品字段必须持续观察。",
        "business_read_en": "Policy is not just a document; it decides which competitor fields need continuous monitoring.",
        "source_link": "https://www.boz.zm/regulatory-framework.htm",
    },
    {
        "institution": "Public app listings",
        "event_type_key": "market_voice",
        "event_type_cn": "舆论/公开评论候选",
        "event_type_en": "Market voice / public-review candidate",
        "event_cn": "Google Play 等公开 listing 可用于主题聚合，但不默认保存用户名、个人身份或原始敏感叙述。",
        "event_en": "Google Play and similar public listings can be used for theme aggregation, without storing usernames, identity data, or sensitive raw narratives by default.",
        "business_read_cn": "公开评论的价值在于主题趋势，而不是个人故事采集。",
        "business_read_en": "The value of public reviews is theme trend analysis, not collection of individual stories.",
        "source_link": "https://play.google.com/store",
    },
)


def choose_text(cn: str, en: str, language: str = "zh") -> str:
    return en if language == "en" else cn


def build_competitor_universe() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for profile in COMPETITOR_PROFILES:
        rows.append(
            {
                "institution": profile.institution,
                "tier_key": profile.tier_key,
                "tier_cn": profile.tier_cn,
                "tier_en": profile.tier_en,
                "product_focus_cn": profile.product_focus_cn,
                "product_focus_en": profile.product_focus_en,
                "evidence_status_cn": profile.evidence_status_cn,
                "evidence_status_en": profile.evidence_status_en,
                "watch_priority_cn": profile.watch_priority_cn,
                "watch_priority_en": profile.watch_priority_en,
                "primary_signals_cn": profile.primary_signals_cn,
                "primary_signals_en": profile.primary_signals_en,
                "watch_fields": ", ".join(profile.watch_fields),
                "source_links": " ; ".join(profile.source_links),
            }
        )
    return rows


def _profile_matches_fields(profile: CompetitorProfile, fields: Iterable[str]) -> bool:
    field_set = set(fields)
    return bool(field_set.intersection(profile.watch_fields))


def build_policy_impact_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for theme in POLICY_THEMES:
        fields = tuple(str(item) for item in theme["watch_fields"])  # type: ignore[index]
        affected = [profile for profile in COMPETITOR_PROFILES if _profile_matches_fields(profile, fields)]
        examples = ", ".join(profile.institution for profile in affected[:6])
        rows.append(
            {
                "policy_key": theme["policy_key"],
                "policy_theme_cn": theme["policy_theme_cn"],
                "policy_theme_en": theme["policy_theme_en"],
                "source_anchor_cn": theme["source_anchor_cn"],
                "source_anchor_en": theme["source_anchor_en"],
                "watch_fields": ", ".join(fields),
                "affected_competitor_count": len(affected),
                "examples": examples,
                "impact_cn": theme["impact_cn"],
                "impact_en": theme["impact_en"],
                "next_action_cn": theme["next_action_cn"],
                "next_action_en": theme["next_action_en"],
            }
        )
    return rows


def build_competitor_event_rows() -> list[dict[str, object]]:
    return [dict(item) for item in EVENT_SEEDS]


FIELD_LABELS: dict[str, tuple[str, str]] = {
    "limit_amount": ("额度", "limit"),
    "pricing_or_disclosure": ("费用披露", "fee disclosure"),
    "payment_or_disbursement": ("放款/还款通道", "payout/repayment rails"),
    "privacy_policy": ("隐私/权限", "privacy/permissions"),
    "support": ("客服/投诉入口", "support/complaints"),
    "segment": ("客群", "segment"),
    "tenor_or_repayment": ("期限/还款节奏", "tenor/repayment"),
    "speed_claim": ("速度承诺", "speed promise"),
    "company_news": ("公司动态", "company news"),
    "app_listing": ("App listing", "app listing"),
    "market_voice": ("舆论主题", "market voice"),
    "channel_mix": ("渠道组合", "channel mix"),
    "eligibility": ("资格要求", "eligibility"),
    "financial_disclosure": ("财报/披露", "financial disclosure"),
    "social_impact": ("社会影响", "social impact"),
    "hiring": ("招聘", "hiring"),
    "partnerships": ("合作伙伴", "partnerships"),
    "licensing": ("许可/监管", "licensing"),
    "complaints": ("投诉", "complaints"),
    "product_layer": ("产品层", "product layer"),
}


TIER_ORDER = {
    "core_digital_lending": 0,
    "adjacent_microfinance_payroll": 1,
    "rails_ecosystem": 2,
}


PRIORITY_ORDER = {
    "高": 0,
    "High": 0,
    "中高": 1,
    "Medium-high": 1,
    "中": 2,
    "Medium": 2,
    "低到中": 3,
    "Low-medium": 3,
}


def _field_labels(fields: str, language: str = "zh", limit: int = 4) -> str:
    labels: list[str] = []
    for raw_field in fields.split(","):
        field = raw_field.strip()
        if not field:
            continue
        cn, en = FIELD_LABELS.get(field, (field, field))
        labels.append(en if language == "en" else cn)
    return " / ".join(labels[:limit])


def _policy_count_for_fields(fields: str) -> int:
    field_set = {field.strip() for field in fields.split(",") if field.strip()}
    count = 0
    for theme in POLICY_THEMES:
        theme_fields = {str(item) for item in theme["watch_fields"]}  # type: ignore[index]
        if field_set.intersection(theme_fields):
            count += 1
    return count


def _product_counts(product_rows: Iterable[dict[str, object]] | None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in product_rows or []:
        institution = str(row.get("institution", "")).strip()
        if institution:
            counts[institution] = counts.get(institution, 0) + 1
    return counts


def build_competitor_overview_rows(product_rows: Iterable[dict[str, object]] | None = None) -> list[dict[str, object]]:
    """Return one concise matrix row per competitor or ecosystem candidate."""

    matrix_counts = _product_counts(product_rows)
    rows: list[dict[str, object]] = []
    for row in build_competitor_universe():
        institution = str(row["institution"])
        product_count = matrix_counts.get(institution, 0)
        if product_count:
            evidence_level_key = "reviewed_product_matrix"
            evidence_level_cn = "已复核产品字段"
            evidence_level_en = "Reviewed product fields"
            matrix_status_cn = f"已入产品矩阵：{product_count} 行"
            matrix_status_en = f"In product matrix: {product_count} row(s)"
            next_step_cn = "继续补费用、还款、支付失败和客服字段。"
            next_step_en = "Continue filling fee, repayment, failed-payment, and support fields."
        else:
            evidence_level_key = "candidate_source"
            evidence_level_cn = "候选来源/待回源"
            evidence_level_en = "Candidate source / needs source review"
            matrix_status_cn = "候选观察：暂未入产品矩阵"
            matrix_status_en = "Candidate watch: not yet in product matrix"
            next_step_cn = "先做人工回源，确认产品字段后再进入产品矩阵。"
            next_step_en = "Manually source-check first, then promote into the product matrix after product fields are confirmed."

        watch_fields = str(row.get("watch_fields", ""))
        rows.append(
            {
                **row,
                "product_matrix_rows": product_count,
                "evidence_level_key": evidence_level_key,
                "evidence_level_cn": evidence_level_cn,
                "evidence_level_en": evidence_level_en,
                "matrix_status_cn": matrix_status_cn,
                "matrix_status_en": matrix_status_en,
                "watch_summary_cn": f"看{_field_labels(watch_fields, 'zh', 3)}",
                "watch_summary_en": f"Watch {_field_labels(watch_fields, 'en', 3)}",
                "policy_pressure_count": _policy_count_for_fields(watch_fields),
                "next_step_cn": next_step_cn,
                "next_step_en": next_step_en,
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            TIER_ORDER.get(str(item.get("tier_key")), 99),
            PRIORITY_ORDER.get(str(item.get("watch_priority_cn")), 99),
            str(item.get("institution")),
        ),
    )


def build_watch_panel_rows(product_rows: Iterable[dict[str, object]] | None = None) -> list[dict[str, object]]:
    """Return compact visual cards for competitor observation panels."""

    rows = []
    for row in build_competitor_overview_rows(product_rows):
        rows.append(
            {
                "institution": row["institution"],
                "tier_key": row["tier_key"],
                "tier_cn": row["tier_cn"],
                "tier_en": row["tier_en"],
                "watch_priority_cn": row["watch_priority_cn"],
                "watch_priority_en": row["watch_priority_en"],
                "evidence_level_cn": row["evidence_level_cn"],
                "evidence_level_en": row["evidence_level_en"],
                "matrix_status_cn": row["matrix_status_cn"],
                "matrix_status_en": row["matrix_status_en"],
                "watch_summary_cn": row["watch_summary_cn"],
                "watch_summary_en": row["watch_summary_en"],
                "policy_pressure_count": row["policy_pressure_count"],
                "product_matrix_rows": row["product_matrix_rows"],
                "next_step_cn": row["next_step_cn"],
                "next_step_en": row["next_step_en"],
                "source_links": row["source_links"],
            }
        )
    return rows


def grouped_competitor_counts(rows: list[dict[str, object]] | None = None) -> dict[str, int]:
    rows = rows or build_competitor_universe()
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("tier_key", "unknown"))
        counts[key] = counts.get(key, 0) + 1
    return counts
