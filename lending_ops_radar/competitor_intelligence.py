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


POSITIONING_BY_INSTITUTION: dict[str, dict[str, str]] = {
    "FLoan": {
        "positioning_cn": "App-first 小额现金贷",
        "positioning_en": "App-first microcash lender",
        "product_lane_cn": "数字小额现金贷",
        "product_lane_en": "Digital microcash loan",
        "target_segment_cn": "个人短期周转借款人",
        "target_segment_en": "Personal short-term cash borrowers",
        "channel_model_cn": "App / 官网 / 移动支付线索",
        "channel_model_en": "App / website / mobile-payment clues",
        "ops_impact_cn": "重点影响额度展示、费用披露、放款到账、账户删除和客服入口。",
        "ops_impact_en": "Main impact is on limit display, fee disclosure, payout posting, account deletion, and support routes.",
    },
    "Lupiya": {
        "positioning_cn": "多产品数字信贷平台",
        "positioning_en": "Multi-product digital lender",
        "product_lane_cn": "短期贷 / 工资客群 / 农业 / 女性 / 平台司机",
        "product_lane_en": "Short-term, salary, agriculture, women, and platform-driver loans",
        "target_segment_cn": "多客群分层借款人",
        "target_segment_en": "Multi-segment borrowers",
        "channel_model_cn": "官网产品页 + 数字申请旅程",
        "channel_model_en": "Website product pages plus digital application journey",
        "ops_impact_cn": "重点影响客群分层、审批资料、还款节奏、产品上线状态和定价披露。",
        "ops_impact_en": "Main impact is on segmentation, documentation, repayment rhythm, launch status, and pricing disclosure.",
    },
    "PowerKwacha": {
        "positioning_cn": "App 小额贷与账户控制能力",
        "positioning_en": "Small-loan app plus account-control capability",
        "product_lane_cn": "数字小额贷 / 隐私与客服入口",
        "product_lane_en": "Digital microloan / privacy and support routes",
        "target_segment_cn": "移动端个人借款人",
        "target_segment_en": "Mobile-first personal borrowers",
        "channel_model_cn": "App / 官网 / Google Play 候选",
        "channel_model_en": "App / website / Google Play candidate",
        "ops_impact_cn": "重点影响隐私权限、客服响应、账户删除、投诉入口和 app 评价主题。",
        "ops_impact_en": "Main impact is on privacy permissions, support response, account deletion, complaint routes, and app-review themes.",
    },
    "PremierCredit": {
        "positioning_cn": "工资预支到 SME 的多层级信贷",
        "positioning_en": "Multi-tier lender from salary advance to SME credit",
        "product_lane_cn": "工资预支 / 个人贷 / SME 贷款",
        "product_lane_en": "Salary advance, personal loan, and SME loan",
        "target_segment_cn": "工薪个人与中小企业",
        "target_segment_en": "Salary earners and SMEs",
        "channel_model_cn": "官网借款旅程 + 移动钱包线索",
        "channel_model_en": "Website borrowing journey plus mobile-wallet clues",
        "ops_impact_cn": "重点影响大额审批、资料收集、移动钱包放款、企业贷风控和客服解释。",
        "ops_impact_en": "Main impact is on larger-ticket approval, documentation, mobile-wallet payout, SME risk controls, and support explanations.",
    },
    "SuperKwacha": {
        "positioning_cn": "App-first 小额贷候选",
        "positioning_en": "App-first microloan candidate",
        "product_lane_cn": "Google Play 公开 listing 候选",
        "product_lane_en": "Public Google Play listing candidate",
        "target_segment_cn": "移动端小额借款人",
        "target_segment_en": "Mobile microloan borrowers",
        "channel_model_cn": "App listing / Data Safety / 公开评分主题",
        "channel_model_en": "App listing / Data Safety / public rating themes",
        "ops_impact_cn": "重点影响 APR/费用披露、权限透明度、更新频率和公开舆情主题。",
        "ops_impact_en": "Main impact is on APR/fee disclosure, permission transparency, update frequency, and public voice themes.",
    },
    "Finedge / ka Something": {
        "positioning_cn": "多通道即时数字贷款",
        "positioning_en": "Multichannel instant digital credit",
        "product_lane_cn": "App / Web / USSD 数字贷款",
        "product_lane_en": "App, web, and USSD digital loan",
        "target_segment_cn": "线上与 USSD 入口借款人",
        "target_segment_en": "Online and USSD-entry borrowers",
        "channel_model_cn": "App / Web / USSD / mobile money / bank",
        "channel_model_en": "App / web / USSD / mobile money / bank",
        "ops_impact_cn": "重点影响获客入口、身份核验、放还款通道、失败交易对账和客服脚本。",
        "ops_impact_en": "Main impact is on acquisition entry, identity checks, payout/repayment rails, failed-transaction reconciliation, and support scripts.",
    },
    "Phindu Credit": {
        "positioning_cn": "个人与工资客群贷款候选",
        "positioning_en": "Personal and salary-loan candidate",
        "product_lane_cn": "个人贷 / Salary loan",
        "product_lane_en": "Personal loan / salary loan",
        "target_segment_cn": "工薪或可验证收入借款人",
        "target_segment_en": "Salary or verifiable-income borrowers",
        "channel_model_cn": "官网申请与人工回源",
        "channel_model_en": "Website application and manual source review",
        "ops_impact_cn": "重点影响收入证明、还款节奏、费用披露和催收沟通脚本。",
        "ops_impact_en": "Main impact is on income proof, repayment rhythm, fee disclosure, and collections communication.",
    },
    "FairMoney Zambia": {
        "positioning_cn": "个人数字贷款候选",
        "positioning_en": "Personal digital-loan candidate",
        "product_lane_cn": "个人贷 / FAQ / App listing 候选",
        "product_lane_en": "Personal loan / FAQ / app-listing candidate",
        "target_segment_cn": "个人线上借款人",
        "target_segment_en": "Online personal borrowers",
        "channel_model_cn": "官网产品页 + App listing 候选",
        "channel_model_en": "Website product page plus app-listing candidate",
        "ops_impact_cn": "重点影响额度、费用、FAQ 解释、客服入口和公开 app 主题。",
        "ops_impact_en": "Main impact is on limits, fees, FAQ wording, support route, and public app themes.",
    },
    "Micro Finance Zambia": {
        "positioning_cn": "传统微贷/薪资贷对照组",
        "positioning_en": "Traditional microfinance/payroll benchmark",
        "product_lane_cn": "薪资扣款 / 个人与企业微贷",
        "product_lane_en": "Payroll-linked personal and business microfinance",
        "target_segment_cn": "工薪、个人和小微经营者",
        "target_segment_en": "Salary earners, individuals, and small businesses",
        "channel_model_cn": "分支机构 / 官网 / 线下资料",
        "channel_model_en": "Branch, website, and offline-document model",
        "ops_impact_cn": "重点作为 app-first 模式的对照，观察资料要求、扣款机制和线下客服。",
        "ops_impact_en": "Useful benchmark against app-first lending, especially documentation, deduction mechanics, and offline support.",
    },
    "SmartFin": {
        "positioning_cn": "数字信用/公司动态候选",
        "positioning_en": "Digital-credit and company-signal candidate",
        "product_lane_cn": "个人/SME 信用活动候选",
        "product_lane_en": "Individual and SME-credit activity candidate",
        "target_segment_cn": "个人与中小企业候选客群",
        "target_segment_en": "Individual and SME candidate segments",
        "channel_model_cn": "公司公开页 / 招聘 / 合作线索",
        "channel_model_en": "Company page, hiring, and partnership clues",
        "ops_impact_cn": "重点影响市场扩张判断、渠道合作、招聘动作和产品定位变化。",
        "ops_impact_en": "Main impact is on expansion signals, channel partnerships, hiring, and positioning changes.",
    },
    "Agora Microfinance": {
        "positioning_cn": "农村与低收入微贷",
        "positioning_en": "Rural and low-income microfinance",
        "product_lane_cn": "农村金融 / 低收入客群微贷",
        "product_lane_en": "Rural finance and low-income microfinance",
        "target_segment_cn": "农村、低收入和微型经营者",
        "target_segment_en": "Rural, low-income, and microenterprise borrowers",
        "channel_model_cn": "网点/代理/社会影响披露",
        "channel_model_en": "Branch/agent and social-impact disclosure model",
        "ops_impact_cn": "重点影响社会影响口径、线下触达、客户教育和非 app-first 替代方案。",
        "ops_impact_en": "Main impact is on social-impact framing, offline reach, customer education, and non-app-first alternatives.",
    },
    "Bayport Zambia": {
        "positioning_cn": "区域集团型薪资贷",
        "positioning_en": "Regional group-backed payroll lender",
        "product_lane_cn": "薪资贷 / 集团披露",
        "product_lane_en": "Payroll lending and group disclosure",
        "target_segment_cn": "工薪与可扣款客群",
        "target_segment_en": "Salary and deduction-capable borrowers",
        "channel_model_cn": "官网 / 集团披露 / 许可证线索",
        "channel_model_en": "Website, group disclosure, and licensing clues",
        "ops_impact_cn": "重点影响财报披露、许可监管、工资扣款、投诉与集团风险偏好。",
        "ops_impact_en": "Main impact is on financial disclosure, licensing, payroll deduction, complaints, and group risk appetite.",
    },
    "FINCA Zambia": {
        "positioning_cn": "金融包容型微贷",
        "positioning_en": "Financial-inclusion microfinance",
        "product_lane_cn": "微贷 / 金融包容 / 社会影响",
        "product_lane_en": "Microfinance, financial inclusion, and social impact",
        "target_segment_cn": "低收入、小微经营和包容金融客群",
        "target_segment_en": "Low-income, microenterprise, and inclusion segments",
        "channel_model_cn": "官网 / 集团披露 / 线下服务",
        "channel_model_en": "Website, group disclosure, and offline service",
        "ops_impact_cn": "重点影响数字化入口、社会影响叙事、客户保护和线下服务质量。",
        "ops_impact_en": "Main impact is on digital entry, social-impact narrative, customer protection, and offline service quality.",
    },
    "VisionFund Zambia": {
        "positioning_cn": "社会影响型小微金融",
        "positioning_en": "Impact-oriented microfinance",
        "product_lane_cn": "小微企业 / 农业 / 社会影响金融",
        "product_lane_en": "Microenterprise, agriculture, and impact finance",
        "target_segment_cn": "小微企业、农业和脆弱客群",
        "target_segment_en": "Microenterprise, agriculture, and vulnerable segments",
        "channel_model_cn": "官网 / 线下网络 / 影响披露",
        "channel_model_en": "Website, offline network, and impact disclosure",
        "ops_impact_cn": "重点作为非 app-first 替代方案，观察客户教育、还款节奏和社会影响指标。",
        "ops_impact_en": "Useful non-app-first alternative for customer education, repayment rhythm, and impact metrics.",
    },
    "LOLC Finance Zambia": {
        "positioning_cn": "消费/资产/微型金融集团型玩家",
        "positioning_en": "Consumer, asset, and microfinance-group player",
        "product_lane_cn": "消费金融 / 分期 / 资产金融",
        "product_lane_en": "Consumer finance, installment, and asset finance",
        "target_segment_cn": "消费、资产融资和小微客户",
        "target_segment_en": "Consumer, asset-finance, and SME-like borrowers",
        "channel_model_cn": "官网 / 区域集团披露 / 线下服务",
        "channel_model_en": "Website, regional group disclosure, and offline service",
        "ops_impact_cn": "重点影响分期结构、资产金融、监管披露和产品线扩张。",
        "ops_impact_en": "Main impact is on installment structure, asset finance, regulatory disclosure, and product-line expansion.",
    },
    "MFinance": {
        "positioning_cn": "微贷数字入口候选",
        "positioning_en": "Microfinance digital-entry candidate",
        "product_lane_cn": "微贷 / 线上申请入口候选",
        "product_lane_en": "Microfinance and online-application candidate",
        "target_segment_cn": "个人和小微候选客群",
        "target_segment_en": "Personal and microenterprise candidate segments",
        "channel_model_cn": "官网 / 数字入口 / 客服线索",
        "channel_model_en": "Website, digital entry, and support clues",
        "ops_impact_cn": "重点影响线上申请、客服入口、费用披露和渠道组合验证。",
        "ops_impact_en": "Main impact is on online application, support routes, fee disclosure, and channel-mix validation.",
    },
    "Airtel Money Zambia": {
        "positioning_cn": "放还款支付轨道",
        "positioning_en": "Payout and repayment payment rail",
        "product_lane_cn": "移动钱包 / 交易失败 / 代理网络",
        "product_lane_en": "Mobile wallet, failed transactions, and agent network",
        "target_segment_cn": "贷款机构与借款人的资金通道",
        "target_segment_en": "Funding rail for lenders and borrowers",
        "channel_model_cn": "Mobile money / 代理 / 客服",
        "channel_model_en": "Mobile money, agents, and support",
        "ops_impact_cn": "不一定是贷款竞品，但直接影响放款到账、还款入账、退款和对账体验。",
        "ops_impact_en": "Not necessarily a lender competitor, but directly affects payout posting, repayment posting, refunds, and reconciliation.",
    },
    "MTN MoMo Zambia": {
        "positioning_cn": "放还款支付轨道",
        "positioning_en": "Payout and repayment payment rail",
        "product_lane_cn": "移动钱包 / 金融服务生态",
        "product_lane_en": "Mobile wallet and financial-services ecosystem",
        "target_segment_cn": "贷款机构与借款人的资金通道",
        "target_segment_en": "Funding rail for lenders and borrowers",
        "channel_model_cn": "MoMo / 代理 / 合作入口",
        "channel_model_en": "MoMo, agents, and partnership entry",
        "ops_impact_cn": "重点影响放款、还款、失败交易、客户解释和合作渠道策略。",
        "ops_impact_en": "Main impact is on payout, repayment, failed transactions, customer explanations, and channel strategy.",
    },
    "JUMO": {
        "positioning_cn": "信贷基础设施/生态伙伴",
        "positioning_en": "Credit infrastructure / ecosystem partner",
        "product_lane_cn": "合作式数字信贷基础设施",
        "product_lane_en": "Partnership-based digital-credit infrastructure",
        "target_segment_cn": "金融机构、钱包和终端借款人生态",
        "target_segment_en": "Financial institutions, wallets, and end-borrower ecosystems",
        "channel_model_cn": "合作伙伴 / 平台 / 数据与风控能力",
        "channel_model_en": "Partners, platform, data and risk capabilities",
        "ops_impact_cn": "重点影响合作伙伴扩张、风控能力、产品嵌入和公司层面披露。",
        "ops_impact_en": "Main impact is on partner expansion, risk capability, embedded products, and company-level disclosure.",
    },
}


POSITIONING_GROUP_BY_INSTITUTION: dict[str, tuple[str, str]] = {
    "FLoan": ("App-first 小额现金贷", "App-first microcash lenders"),
    "PowerKwacha": ("App-first 小额现金贷", "App-first microcash lenders"),
    "SuperKwacha": ("App-first 小额现金贷", "App-first microcash lenders"),
    "FairMoney Zambia": ("App-first 小额现金贷", "App-first microcash lenders"),
    "Lupiya": ("多产品数字/综合信贷", "Multi-product digital or hybrid lenders"),
    "PremierCredit": ("多产品数字/综合信贷", "Multi-product digital or hybrid lenders"),
    "Finedge / ka Something": ("多通道数字入口", "Multichannel digital-entry lenders"),
    "MFinance": ("多通道数字入口", "Multichannel digital-entry lenders"),
    "Phindu Credit": ("薪资/收入客群贷款", "Salary or income-linked lenders"),
    "Bayport Zambia": ("薪资/收入客群贷款", "Salary or income-linked lenders"),
    "Micro Finance Zambia": ("薪资/收入客群贷款", "Salary or income-linked lenders"),
    "Agora Microfinance": ("金融包容/社会影响微贷", "Financial-inclusion and impact microfinance"),
    "FINCA Zambia": ("金融包容/社会影响微贷", "Financial-inclusion and impact microfinance"),
    "VisionFund Zambia": ("金融包容/社会影响微贷", "Financial-inclusion and impact microfinance"),
    "LOLC Finance Zambia": ("消费/资产/分期金融", "Consumer, asset, and installment finance"),
    "SmartFin": ("公司动态/数字信用候选", "Company-signal and digital-credit candidates"),
    "Airtel Money Zambia": ("支付轨道/钱包生态", "Payment rails and wallet ecosystem"),
    "MTN MoMo Zambia": ("支付轨道/钱包生态", "Payment rails and wallet ecosystem"),
    "JUMO": ("信贷基础设施/生态伙伴", "Credit infrastructure and ecosystem partners"),
}


def _unique_join(values: Iterable[object], limit: int = 3) -> str:
    seen: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.append(text)
    return " / ".join(seen[:limit])


def _product_rows_by_institution(product_rows: Iterable[dict[str, object]] | None) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in product_rows or []:
        institution = str(row.get("institution", "")).strip()
        if institution:
            grouped.setdefault(institution, []).append(row)
    return grouped


def build_competitor_comparison_rows(product_rows: Iterable[dict[str, object]] | None = None) -> list[dict[str, object]]:
    """Return an all-target positioning and product matrix for concise comparison.

    Reviewed product rows override the provisional lane where possible; candidates
    remain explicitly marked as source hypotheses that need manual source review.
    """

    grouped_products = _product_rows_by_institution(product_rows)
    rows: list[dict[str, object]] = []
    for universe_row in build_competitor_overview_rows(product_rows):
        institution = str(universe_row.get("institution", ""))
        product_items = grouped_products.get(institution, [])
        base = POSITIONING_BY_INSTITUTION.get(institution, {})
        product_count = int(universe_row.get("product_matrix_rows", 0) or 0)
        if product_items:
            positioning_cn = _unique_join(item.get("competitor_positioning_cn") for item in product_items) or base.get("positioning_cn", "")
            positioning_en = _unique_join(item.get("competitor_positioning_en") for item in product_items) or base.get("positioning_en", "")
            product_lane_cn = _unique_join(item.get("product_layer_cn") for item in product_items) or base.get("product_lane_cn", "")
            product_lane_en = _unique_join(item.get("product_layer_en") for item in product_items) or base.get("product_lane_en", "")
            target_segment_cn = _unique_join(item.get("segment_cn") for item in product_items) or base.get("target_segment_cn", "")
            target_segment_en = _unique_join(item.get("segment_en") for item in product_items) or base.get("target_segment_en", "")
            channel_model_cn = _unique_join(item.get("payment_maturity_cn") for item in product_items) or base.get("channel_model_cn", "")
            channel_model_en = _unique_join(item.get("payment_maturity_en") for item in product_items) or base.get("channel_model_en", "")
            ops_impact_cn = _unique_join(item.get("operating_risk_focus_cn") for item in product_items) or base.get("ops_impact_cn", "")
            ops_impact_en = _unique_join(item.get("operating_risk_focus_en") for item in product_items) or base.get("ops_impact_en", "")
            evidence_mode_cn = f"已复核产品字段：{product_count} 条"
            evidence_mode_en = f"Reviewed product fields: {product_count} row(s)"
            matrix_status_cn = "已进入产品矩阵"
            matrix_status_en = "In product matrix"
        else:
            positioning_cn = base.get("positioning_cn", str(universe_row.get("tier_cn", "")))
            positioning_en = base.get("positioning_en", str(universe_row.get("tier_en", "")))
            product_lane_cn = base.get("product_lane_cn", str(universe_row.get("product_focus_cn", "")))
            product_lane_en = base.get("product_lane_en", str(universe_row.get("product_focus_en", "")))
            target_segment_cn = base.get("target_segment_cn", "待回源确认客群")
            target_segment_en = base.get("target_segment_en", "Segment needs source review")
            channel_model_cn = base.get("channel_model_cn", "待回源确认渠道")
            channel_model_en = base.get("channel_model_en", "Channel model needs source review")
            ops_impact_cn = base.get("ops_impact_cn", str(universe_row.get("watch_summary_cn", "")))
            ops_impact_en = base.get("ops_impact_en", str(universe_row.get("watch_summary_en", "")))
            evidence_mode_cn = "候选定位：待回源"
            evidence_mode_en = "Provisional positioning: source review needed"
            matrix_status_cn = "未入已复核产品矩阵"
            matrix_status_en = "Not in reviewed product matrix"

        rows.append(
            {
                "institution": institution,
                "tier_key": universe_row.get("tier_key", ""),
                "tier_cn": universe_row.get("tier_cn", ""),
                "tier_en": universe_row.get("tier_en", ""),
                "positioning_group_cn": POSITIONING_GROUP_BY_INSTITUTION.get(
                    institution,
                    (str(universe_row.get("tier_cn", "")), str(universe_row.get("tier_en", ""))),
                )[0],
                "positioning_group_en": POSITIONING_GROUP_BY_INSTITUTION.get(
                    institution,
                    (str(universe_row.get("tier_cn", "")), str(universe_row.get("tier_en", ""))),
                )[1],
                "watch_priority_cn": universe_row.get("watch_priority_cn", ""),
                "watch_priority_en": universe_row.get("watch_priority_en", ""),
                "positioning_cn": positioning_cn,
                "positioning_en": positioning_en,
                "product_lane_cn": product_lane_cn,
                "product_lane_en": product_lane_en,
                "target_segment_cn": target_segment_cn,
                "target_segment_en": target_segment_en,
                "channel_model_cn": channel_model_cn,
                "channel_model_en": channel_model_en,
                "ops_impact_cn": ops_impact_cn,
                "ops_impact_en": ops_impact_en,
                "evidence_mode_cn": evidence_mode_cn,
                "evidence_mode_en": evidence_mode_en,
                "matrix_status_cn": matrix_status_cn,
                "matrix_status_en": matrix_status_en,
                "product_matrix_rows": product_count,
                "policy_pressure_count": universe_row.get("policy_pressure_count", 0),
                "source_links": universe_row.get("source_links", ""),
            }
        )
    return rows


def build_positioning_group_rows(
    comparison_rows: Iterable[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    rows = list(comparison_rows or build_competitor_comparison_rows())
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        key = (str(row.get("positioning_group_cn", "")), str(row.get("positioning_group_en", "")))
        grouped.setdefault(key, []).append(row)

    output: list[dict[str, object]] = []
    for (positioning_group_cn, positioning_group_en), items in grouped.items():
        institutions = ", ".join(str(item.get("institution", "")) for item in items)
        reviewed_count = sum(1 for item in items if int(item.get("product_matrix_rows", 0) or 0) > 0)
        candidate_count = len(items) - reviewed_count
        lanes_cn = _unique_join((item.get("product_lane_cn") for item in items), limit=4)
        lanes_en = _unique_join((item.get("product_lane_en") for item in items), limit=4)
        output.append(
            {
                "positioning_cn": positioning_group_cn,
                "positioning_en": positioning_group_en,
                "institutions": institutions,
                "target_count": len(items),
                "reviewed_count": reviewed_count,
                "candidate_count": candidate_count,
                "product_lanes_cn": lanes_cn,
                "product_lanes_en": lanes_en,
                "business_read_cn": "这一组用于判断同类玩家的客群、渠道和运营风险是否可横向比较；候选项需要先补来源证据。",
                "business_read_en": "Use this group to compare similar players by segment, channel, and operating risk; candidate targets need source evidence first.",
            }
        )
    return sorted(output, key=lambda item: (-int(item["target_count"]), str(item["positioning_en"])))


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
    comparison_by_name = {str(row.get("institution", "")): row for row in build_competitor_comparison_rows(product_rows)}
    for row in build_competitor_overview_rows(product_rows):
        comparison = comparison_by_name.get(str(row["institution"]), {})
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
                "positioning_cn": comparison.get("positioning_cn", ""),
                "positioning_en": comparison.get("positioning_en", ""),
                "product_lane_cn": comparison.get("product_lane_cn", ""),
                "product_lane_en": comparison.get("product_lane_en", ""),
                "target_segment_cn": comparison.get("target_segment_cn", ""),
                "target_segment_en": comparison.get("target_segment_en", ""),
                "ops_impact_cn": comparison.get("ops_impact_cn", ""),
                "ops_impact_en": comparison.get("ops_impact_en", ""),
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
