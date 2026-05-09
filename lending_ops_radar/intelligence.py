"""Rule-based business impact interpretation for lending-ops signals."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable


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


@dataclass(frozen=True)
class ImpactRule:
    domain_key: str
    domain_cn: str
    domain_en: str
    keywords: tuple[str, ...]
    classifications: tuple[str, ...]
    impact_level: str
    lending_impact_cn: str
    lending_impact_en: str
    affected_processes_cn: str
    affected_processes_en: str
    recommended_actions_cn: str
    recommended_actions_en: str
    follow_up_questions_cn: str
    follow_up_questions_en: str


RULES: tuple[ImpactRule, ...] = (
    ImpactRule(
        domain_key="payment_rails",
        domain_cn="支付轨道与资金流",
        domain_en="Payment Rails and Fund Flow",
        keywords=(
            "zipss",
            "montran",
            "national financial switch",
            "settlement",
            "gateway",
            "interbank payment",
            "iso 20022",
            "mobile payments",
            "money transfer",
            "electronic money",
            "e-money",
            "payment service",
            "incomplete transaction",
            "mobile money",
            "wallet",
            "bank account",
            "bank accounts",
            "funds are sent",
            "creditors",
        ),
        classifications=("repayment", "disbursement", "regulatory"),
        impact_level="high",
        lending_impact_cn="对小微贷款最直接的影响是放款到账、还款入账、失败交易处理、对账和合作方依赖。它不一定改变贷款产品本身，但会改变运营可用性、异常处理和客户体验。",
        lending_impact_en="The direct micro-lending impact is disbursement reliability, repayment posting, failed-transaction handling, reconciliation, and partner dependency. It may not change the loan product, but it changes operating availability and customer experience.",
        affected_processes_cn="放款、还款、对账、失败交易、退款/冲正、合作银行/钱包/聚合器管理、周末和延长营业时间支持。",
        affected_processes_en="Disbursement, repayment, reconciliation, failed transactions, reversals/refunds, partner bank/wallet/aggregator management, weekend and extended-hours support.",
        recommended_actions_cn="建立支付轨道清单：哪些贷款流程依赖银行、钱包、NFS、ZIPSS、聚合器；为失败交易、延迟入账和重复扣款写清楚客服口径和升级路径。",
        recommended_actions_en="Build a payment-rail dependency map: which loan flows depend on banks, wallets, NFS, ZIPSS, or aggregators; define support scripts and escalation paths for failed, delayed, or duplicate transactions.",
        follow_up_questions_cn="如果某条轨道延迟或不可用，借款人会看到什么？还款逾期计算是否会误伤客户？客服如何证明是轨道问题而非客户问题？",
        follow_up_questions_en="If a rail is delayed or unavailable, what does the borrower see? Could repayment-late logic harm customers? How can support distinguish rail failure from customer error?",
    ),
    ImpactRule(
        domain_key="fees_disclosure",
        domain_cn="费用、定价与披露",
        domain_en="Fees, Pricing, and Disclosure",
        keywords=(
            "fee",
            "fees",
            "charges",
            "pricing",
            "interest",
            "unwarranted charges",
            "specific charges",
            "clear communication",
            "terms",
            "misleading",
            "incomplete disclosure",
            "sufficient information",
        ),
        classifications=("fees", "regulatory", "news_signal"),
        impact_level="high",
        lending_impact_cn="对贷款业务的影响集中在定价页面、借款确认页、逾期/罚息说明、客服解释和投诉风险。费用越复杂，越需要在客户旅程里提前解释。",
        lending_impact_en="The lending impact sits in pricing pages, loan confirmation screens, late-fee/penalty explanations, support explanations, and complaint risk. The more complex the fee stack, the earlier it must be explained in the customer journey.",
        affected_processes_cn="产品定价、费用披露、借款合同摘要、营销文案、FAQ、客服话术、投诉复核。",
        affected_processes_en="Product pricing, fee disclosure, loan-summary pages, marketing copy, FAQ, support scripts, complaint review.",
        recommended_actions_cn="把所有客户可能支付的金额拆成“本金、利息、服务费、罚费、第三方费用、支付轨道费用”，逐项检查是否在申请前、确认前和还款前可见。",
        recommended_actions_en="Break every customer payable amount into principal, interest, service fee, penalty fee, third-party fee, and rail fee; check visibility before application, confirmation, and repayment.",
        follow_up_questions_cn="客户在点击确认前能否知道总成本？费用名称是否和实际扣款一致？支付轨道费用是否被误认为贷款费用？",
        follow_up_questions_en="Can the customer see total cost before confirmation? Do fee labels match actual deductions? Could rail fees be mistaken for lender fees?",
    ),
    ImpactRule(
        domain_key="complaints_support",
        domain_cn="投诉、客服与争议处理",
        domain_en="Complaints, Support, and Dispute Handling",
        keywords=(
            "complaint",
            "complaints",
            "redress",
            "resolution",
            "support",
            "clarification",
            "report concerns",
            "consumer complaints",
            "dispute",
            "reversal",
            "track incident",
        ),
        classifications=("complaint", "news_signal", "repayment"),
        impact_level="high",
        lending_impact_cn="对小微贷款的影响不是“有没有投诉入口”这么简单，而是投诉数据、处理时限、证据留存、跨团队升级和重复问题复盘能力。",
        lending_impact_en="The micro-lending impact is not just whether a complaint channel exists. It is complaint data, resolution timelines, evidence retention, cross-team escalation, and repeat-issue review.",
        affected_processes_cn="客服工单、投诉分类、SLA、支付失败争议、费用争议、催收争议、数据/隐私请求、监管问询准备。",
        affected_processes_en="Support tickets, complaint taxonomy, SLA, payment-failure disputes, fee disputes, collections disputes, data/privacy requests, regulator-query readiness.",
        recommended_actions_cn="建立 lending ops 投诉分类树：放款、还款、费用、欺诈、隐私、催收、客服态度、技术故障；每类都要有证据、负责人和关闭标准。",
        recommended_actions_en="Build a lending-ops complaint taxonomy: disbursement, repayment, fees, fraud, privacy, collections, support conduct, technical failure; each needs evidence, owner, and closure criteria.",
        follow_up_questions_cn="哪些投诉会升级为监管风险？哪些投诉代表产品设计问题而不是单个客服问题？AI/自动化处理是否会造成解释不足？",
        follow_up_questions_en="Which complaints could become regulatory risk? Which complaints indicate product design issues rather than agent errors? Could AI/automation under-explain decisions?",
    ),
    ImpactRule(
        domain_key="privacy_data",
        domain_cn="隐私、数据与授权",
        domain_en="Privacy, Data, and Consent",
        keywords=(
            "privacy",
            "personal data",
            "data protection",
            "data subject",
            "consent",
            "controller",
            "processor",
            "cross-border",
            "registration",
            "audit",
            "rights",
            "account delete",
            "delete account",
            "data safety",
            "permission",
            "permissions",
        ),
        classifications=("privacy",),
        impact_level="high",
        lending_impact_cn="数字贷款高度依赖身份、设备、联系人、交易和还款数据。隐私信号会影响 app 权限、信用评估、风控模型、催收联系、第三方供应商和跨境处理。",
        lending_impact_en="Digital lending depends on identity, device, contact, transaction, and repayment data. Privacy signals affect app permissions, credit assessment, risk models, collections contact, vendors, and cross-border processing.",
        affected_processes_cn="注册/KYC、app 权限、信用评分、反欺诈、数据保留、第三方处理、催收触达、数据主体请求。",
        affected_processes_en="Registration/KYC, app permissions, credit scoring, anti-fraud, retention, third-party processing, collections contact, data-subject requests.",
        recommended_actions_cn="为每类数据写出“收集目的、使用场景、保存期限、共享对象、客户权利入口”；尤其关注联系人/设备/位置/交易数据。",
        recommended_actions_en="For each data category, document purpose, use case, retention, sharing party, and customer-rights channel; pay special attention to contacts, device, location, and transaction data.",
        follow_up_questions_cn="哪些数据是放款必需，哪些只是优化模型？客户撤回授权后贷款和催收流程如何处理？供应商是否构成 processor/controller 风险？",
        follow_up_questions_en="Which data is necessary for lending, and which only optimizes the model? What happens if consent is withdrawn? Do vendors create processor/controller risk?",
    ),
    ImpactRule(
        domain_key="fraud_security",
        domain_cn="欺诈、账户安全与交易安全",
        domain_en="Fraud, Account Security, and Transaction Security",
        keywords=(
            "fraud",
            "scam",
            "stolen",
            "lost",
            "unsolicited",
            "phishing",
            "impersonation",
            "cyber",
            "security",
            "authentication",
            "incident",
        ),
        classifications=("fraud", "regulatory"),
        impact_level="high",
        lending_impact_cn="欺诈会同时打到获客、KYC、放款、还款和客服。移动钱包欺诈或身份冒用会让坏账、投诉和声誉风险同时上升。",
        lending_impact_en="Fraud hits acquisition, KYC, disbursement, repayment, and support at once. Wallet fraud or impersonation can raise credit loss, complaints, and reputation risk together.",
        affected_processes_cn="KYC、登录、设备绑定、放款账户验证、还款账户识别、异常交易监控、客服身份核验。",
        affected_processes_en="KYC, login, device binding, payout-account verification, repayment-account recognition, anomaly monitoring, support identity checks.",
        recommended_actions_cn="把欺诈信号拆成账户接管、身份冒用、支付欺诈、短信/钓鱼、内部/代理风险；为每类配置阻断、人工复核和客户解释流程。",
        recommended_actions_en="Split fraud into account takeover, impersonation, payment fraud, SMS/phishing, and internal/agent risk; define blocking, manual review, and customer explanation flows.",
        follow_up_questions_cn="欺诈拦截会不会误伤真实小微客户？客户如何申诉？放款账户和还款账户是否有一致性校验？",
        follow_up_questions_en="Could fraud controls harm legitimate micro customers? How can customers appeal? Are payout and repayment accounts consistently verified?",
    ),
    ImpactRule(
        domain_key="collections_conduct",
        domain_cn="催收行为与客户沟通",
        domain_en="Collections Conduct and Customer Communication",
        keywords=(
            "collection",
            "collections",
            "overdue",
            "arrears",
            "late payment",
            "recovery",
            "harassment",
            "unfair",
            "conduct",
            "consumer rights",
        ),
        classifications=("collections", "complaint", "news_signal"),
        impact_level="medium",
        lending_impact_cn="当前公开来源里催收信号偏少，但消费者保护、隐私和投诉规则会间接影响催收话术、触达频率、联系人使用和争议处理。",
        lending_impact_en="Direct collections signals are sparse, but consumer-protection, privacy, and complaint rules indirectly affect collections scripts, contact frequency, contact-person use, and dispute handling.",
        affected_processes_cn="逾期提醒、催收话术、联系人触达、还款承诺记录、争议暂停、投诉升级。",
        affected_processes_en="Late reminders, collections scripts, third-party contact, promise-to-pay records, dispute pauses, complaint escalation.",
        recommended_actions_cn="先建立催收合规观察清单：频率、时间、语气、联系人、隐私、争议暂停、已还款但仍催收、轨道延迟导致的误催。",
        recommended_actions_en="Create a collections-conduct watchlist: frequency, timing, tone, third-party contact, privacy, dispute pause, paid-but-chased cases, and rail-delay false collections.",
        follow_up_questions_cn="如果支付轨道延迟导致系统显示逾期，催收是否自动暂停？是否允许联系第三方？客户投诉后催收如何冻结？",
        follow_up_questions_en="If rail delay makes an account appear late, are collections paused? Is third-party contact allowed? How are collections frozen after a complaint?",
    ),
    ImpactRule(
        domain_key="ops_resilience",
        domain_cn="运营韧性与供应商依赖",
        domain_en="Operational Resilience and Vendor Dependency",
        keywords=(
            "operational",
            "business continuity",
            "availability",
            "network infrastructure",
            "service provider",
            "migration",
            "upgrade",
            "extended operating hours",
            "six day operations",
            "risk management",
            "vendor",
        ),
        classifications=("regulatory", "repayment"),
        impact_level="medium",
        lending_impact_cn="对小微贷款来说，系统升级、供应商变化和营业时间调整会影响到账、对账、客服排班、资金清算和异常处理容量。",
        lending_impact_en="For micro-lending, system upgrades, vendor changes, and operating-hours changes affect posting, reconciliation, support staffing, settlement, and exception-handling capacity.",
        affected_processes_cn="系统变更管理、合作方 SLA、事故响应、客服排班、批处理/对账、资金清算。",
        affected_processes_en="Change management, partner SLA, incident response, support staffing, batch/reconciliation, settlement.",
        recommended_actions_cn="把监管/基础设施变更放进运营日历，提前标注潜在影响窗口、备选流程、客服口径和人工对账责任人。",
        recommended_actions_en="Put regulatory/infrastructure changes into an ops calendar with impact windows, fallback processes, support scripts, and manual-reconciliation owners.",
        follow_up_questions_cn="系统升级时是否冻结放款或调整还款入账时间？供应商切换是否需要客户通知？异常积压由谁清理？",
        follow_up_questions_en="During upgrades, should disbursement pause or repayment posting rules change? Does vendor switching require customer notice? Who clears exception backlog?",
    ),
    ImpactRule(
        domain_key="competitor_market",
        domain_cn="竞品与市场动作",
        domain_en="Competitor and Market Movement",
        keywords=(
            "competitor",
            "faq",
            "eligibility",
            "loan",
            "loans",
            "loan amount",
            "microloan",
            "personal loan",
            "business loan",
            "salary advance",
            "sme",
            "collateral",
            "agri",
            "farmers",
            "civil servant",
            "approval",
            "offer",
            "terms",
            "app",
            "pricing",
        ),
        classifications=("competitor_change", "fees"),
        impact_level="medium",
        lending_impact_cn="首轮竞品官网/FAQ 监控已经能看到额度、期限、速度承诺、客群分层、支付路径、客服入口和隐私入口。对小微贷款业务最有用的是把这些信号整理成产品矩阵，而不是只保存网页标题。",
        lending_impact_en="The phase-1 competitor website/FAQ watch now shows limits, tenor, speed promises, customer segmentation, payment paths, support channels, and privacy entry points. The useful lending impact is a product matrix, not saved page titles.",
        affected_processes_cn="竞品 watchlist、Google Play/app listing、官网 FAQ、费用页、申请资格页、公开用户评价。",
        affected_processes_en="Competitor watchlist, Google Play/app listings, FAQ, fee pages, eligibility pages, public user reviews.",
        recommended_actions_cn="维护竞品矩阵：机构、客群、产品、额度、期限、速度承诺、放款/还款通道、客服入口、隐私/账户控制入口。Google Play/public reviews 仍需单独批准后再启用。",
        recommended_actions_en="Maintain a competitor matrix: institution, segment, product, limit, tenor, speed promise, payout/repayment channel, support route, privacy/account-control route. Enable Google Play/public reviews only after separate approval.",
        follow_up_questions_cn="哪些竞品信号会改变产品定位：额度更高、期限更长、审批更快、支付轨道更强、客群更细、隐私/客服入口更清楚？",
        follow_up_questions_en="Which competitor signals change positioning: higher limits, longer tenor, faster approval, stronger payment rails, finer segmentation, clearer privacy/support routes?",
    ),
    ImpactRule(
        domain_key="reputation_news",
        domain_cn="舆情、声誉与公共叙事",
        domain_en="Public Sentiment, Reputation, and Narrative",
        keywords=(
            "news",
            "press",
            "public notice",
            "market",
            "e-commerce",
            "consumer base",
            "confidence",
            "safer markets",
            "misleading representations",
        ),
        classifications=("news_signal", "regulatory"),
        impact_level="medium",
        lending_impact_cn="舆情信号目前主要来自官方叙事，不能代表真实借款人声音。它更适合提示监管关注点和公众敏感词，而不是衡量品牌好坏。",
        lending_impact_en="Current sentiment signals mainly come from official narratives, not borrower voice. They are better for identifying regulator-sensitive themes and public vocabulary than measuring brand quality.",
        affected_processes_cn="品牌风险、客服解释、营销合规、消费者教育、新闻监控、危机预案。",
        affected_processes_en="Brand risk, support explanations, marketing compliance, consumer education, news monitoring, crisis playbook.",
        recommended_actions_cn="把官方舆情和真实用户声音分开；下一步需要公开评论、公开新闻和公开社媒页面的手动批准来源。",
        recommended_actions_en="Separate official narrative from real user voice; next add manually approved public reviews, public news, and public social pages.",
        follow_up_questions_cn="哪些词会触发公众不信任：隐藏费用、扣款失败、骚扰催收、隐私滥用、到账慢？目前哪些来源能真实观察这些词？",
        follow_up_questions_en="Which terms trigger distrust: hidden fees, failed deductions, harassment, privacy misuse, slow payout? Which sources can truly observe these terms today?",
    ),
)


DEFAULT_RULE = ImpactRule(
    domain_key="general_watch",
    domain_cn="综合观察",
    domain_en="General Watch",
    keywords=(),
    classifications=(),
    impact_level="low",
    lending_impact_cn="这条信号目前只能作为背景信息，尚不能直接推出对小微贷款业务的明确影响。",
    lending_impact_en="This signal is currently background context and does not yet support a concrete micro-lending impact conclusion.",
    affected_processes_cn="待进一步人工判断。",
    affected_processes_en="Needs further manual review.",
    recommended_actions_cn="保留来源链接，等待更多同类信号后再纳入业务判断。",
    recommended_actions_en="Keep the source link and wait for more similar signals before using it for business interpretation.",
    follow_up_questions_cn="它是否会影响客户旅程、费用、支付、投诉、隐私、催收或合作方？如果不能说明，先不要过度解读。",
    follow_up_questions_en="Does it affect customer journey, fees, payments, complaints, privacy, collections, or partners? If unclear, do not over-interpret.",
)


def rule_score(rule: ImpactRule, row: Any) -> int:
    text = signal_text(row)
    score = 0
    classification = row_value(row, "classification")
    if classification in rule.classifications:
        score += 2
    score += sum(1 for keyword in rule.keywords if keyword in text)
    if rule.domain_key == "payment_rails" and row_value(row, "source_id").startswith("boz_"):
        score += 1
    if rule.domain_key == "privacy_data" and "data_protection" in row_value(row, "source_id"):
        score += 2
    if rule.domain_key == "complaints_support" and "zicta" in row_value(row, "source_id"):
        score += 2
    if rule.domain_key == "competitor_market" and row_value(row, "source_id").startswith("competitor_"):
        score += 1
    if rule.domain_key == "payment_rails" and row_value(row, "source_id").startswith("competitor_"):
        rail_terms = ("mobile money", "wallet", "bank account", "bank accounts", "funds are sent", "creditors")
        if any(term in text for term in rail_terms):
            score += 2
        else:
            score = 0
    if rule.domain_key == "privacy_data" and row_value(row, "source_id").startswith("competitor_"):
        if any(term in text for term in ("privacy", "account delete", "delete account", "data safety", "permission")):
            score += 2
    return score


def assess_signal(row: Any) -> dict[str, str | int]:
    scored = [(rule_score(rule, row), rule) for rule in RULES]
    score, rule = max(scored, key=lambda item: item[0])
    if score <= 0:
        rule = DEFAULT_RULE
    priority = row_value(row, "priority", "3")
    try:
        priority_int = int(priority)
    except ValueError:
        priority_int = 3
    if priority_int == 1 and rule.impact_level == "medium":
        impact_level = "high"
    else:
        impact_level = rule.impact_level
    return {
        "signal_id": row_value(row, "id"),
        "source": row_value(row, "source_name"),
        "signal": row_value(row, "item_title"),
        "source_link": row_value(row, "item_url") or row_value(row, "source_url"),
        "classification": row_value(row, "classification"),
        "risk_level": row_value(row, "risk_level"),
        "priority": priority_int,
        "impact_level": impact_level,
        "domain_key": rule.domain_key,
        "domain_cn": rule.domain_cn,
        "domain_en": rule.domain_en,
        "lending_impact_cn": rule.lending_impact_cn,
        "lending_impact_en": rule.lending_impact_en,
        "affected_processes_cn": rule.affected_processes_cn,
        "affected_processes_en": rule.affected_processes_en,
        "recommended_actions_cn": rule.recommended_actions_cn,
        "recommended_actions_en": rule.recommended_actions_en,
        "follow_up_questions_cn": rule.follow_up_questions_cn,
        "follow_up_questions_en": rule.follow_up_questions_en,
    }


def build_assessments(rows: Iterable[Any]) -> list[dict[str, str | int]]:
    return [assess_signal(row) for row in rows]


def domain_counts(assessments: Iterable[dict[str, str | int]]) -> Counter[str]:
    return Counter(str(item["domain_key"]) for item in assessments)


def top_interpretive_findings(assessments: list[dict[str, str | int]]) -> list[dict[str, str]]:
    counts = domain_counts(assessments)
    findings: list[dict[str, str]] = []
    if counts["payment_rails"]:
        findings.append(
            {
                "finding_cn": "支付轨道已经是小微贷款运营风险的核心变量，不只是银行后台问题。",
                "finding_en": "Payment rails are a core micro-lending operating-risk variable, not just a bank back-office issue.",
                "why_cn": "BoZ/ZIPSS/Montran/NFS 信号会影响放款到账、还款入账、失败交易、对账、客服解释和合作方管理。",
                "why_en": "BoZ/ZIPSS/Montran/NFS signals affect payout, repayment posting, failed transactions, reconciliation, support explanations, and partner management.",
            }
        )
    if counts["fees_disclosure"]:
        findings.append(
            {
                "finding_cn": "费用与披露是监管/投诉/声誉风险交汇点。",
                "finding_en": "Fees and disclosure are where regulatory, complaint, and reputation risk meet.",
                "why_cn": "CCPC 与 BoZ 相关信号都指向清晰、充分、不可误导的信息披露，贷款产品需要把总成本、费用名称和扣款时点讲清楚。",
                "why_en": "CCPC and BoZ signals point to clear, sufficient, non-misleading disclosure. Lending products need clear total cost, fee labels, and deduction timing.",
            }
        )
    if counts["complaints_support"]:
        findings.append(
            {
                "finding_cn": "投诉处理应被当成运营数据系统，而不是单纯客服事项。",
                "finding_en": "Complaint handling should be treated as an operating data system, not just a support task.",
                "why_cn": "支付失败、费用争议、隐私请求和催收争议需要统一分类、证据留存、SLA 和升级路径。",
                "why_en": "Failed payments, fee disputes, privacy requests, and collections disputes need common taxonomy, evidence retention, SLA, and escalation paths.",
            }
        )
    if counts["privacy_data"]:
        findings.append(
            {
                "finding_cn": "数据保护会影响 app 权限、风控建模和催收触达。",
                "finding_en": "Data protection affects app permissions, risk modeling, and collections contact.",
                "why_cn": "数字贷款依赖个人数据和第三方处理，隐私信号需要转化为数据清单、授权说明、供应商边界和客户权利流程。",
                "why_en": "Digital lending depends on personal data and third-party processing. Privacy signals must become data inventory, consent language, vendor boundaries, and rights-handling workflows.",
            }
        )
    if counts["competitor_market"]:
        findings.append(
            {
                "finding_cn": "竞品线已经从空白进入 phase-1 产品矩阵阶段。",
                "finding_en": "The competitor lane has moved from blank coverage into a phase-1 product-matrix stage.",
                "why_cn": "已复核信号开始覆盖 FLoan、Lupiya、PremierCredit、PowerKwacha 的额度、期限、速度承诺、客群、支付路径、客服和隐私入口。下一步不是多抓，而是把这些字段结构化比较。",
                "why_en": "Reviewed signals now cover limits, tenor, speed promises, segments, payment paths, support, and privacy entry points across FLoan, Lupiya, PremierCredit, and PowerKwacha. The next step is structured comparison, not just more crawling.",
            }
        )
    if not findings:
        findings.append(
            {
                "finding_cn": "当前信号仍以背景信息为主，业务影响需要更多来源交叉验证。",
                "finding_en": "Current signals remain mostly background context; business impact needs more source triangulation.",
                "why_cn": "需要补充竞品、公开评论、客服/投诉类别和舆情来源，才能形成更稳定的自动化情报。",
                "why_en": "Competitor, public review, support/complaint category, and sentiment sources are needed for more stable automated intelligence.",
            }
        )
    return findings[:5]


def coverage_gaps(assessments: list[dict[str, str | int]]) -> list[dict[str, str]]:
    counts = domain_counts(assessments)
    rows = [
        {
            "area_cn": "监管/政策",
            "area_en": "Regulatory and Policy",
            "coverage_cn": "中高",
            "coverage_en": "Medium-high",
            "gap_cn": "已有 BoZ、CCPC、DPC，但仍偏政策文件，需要转成业务流程影响。",
            "gap_en": "BoZ, CCPC, and DPC exist, but many signals are policy documents and need process-level interpretation.",
            "next_source_cn": "继续 BoZ JSON:API、CCPC、DPC；补 BoZ publications/annual reports 的稳定文件路径。",
            "next_source_en": "Continue BoZ JSON:API, CCPC, DPC; add stable BoZ publications/annual-report file routes.",
        },
        {
            "area_cn": "竞品",
            "area_en": "Competitors",
            "coverage_cn": "中低",
            "coverage_en": "Medium-low",
            "gap_cn": "phase-1 官网/FAQ watchlist 已建立并完成首轮复核，但 Google Play/app listing 和公开评论层仍未默认启用。",
            "gap_en": "The phase-1 website/FAQ watchlist exists and has first-pass review, but Google Play/app listings and public-review sources remain disabled by default.",
            "next_source_cn": "把已复核官网信号整理成竞品矩阵；再决定是否启用 Google Play/public app listing，用于观察 app 权限、评分、公开评论主题。",
            "next_source_en": "Turn reviewed website signals into a competitor matrix; then decide whether to enable Google Play/public app listings for app permissions, ratings, and public-review themes.",
        },
        {
            "area_cn": "投诉/客服",
            "area_en": "Complaints and Support",
            "coverage_cn": "中低",
            "coverage_en": "Medium-low",
            "gap_cn": "已有 ZICTA/CCPC/BoZ complaint 信号，但缺少真实公开用户评论和投诉主题趋势。",
            "gap_en": "ZICTA/CCPC/BoZ complaint signals exist, but real public user-review and complaint-theme trend sources are missing.",
            "next_source_cn": "运行 ZICTA DFS 两个源；补公开 app review、公开新闻和公开社媒页面的低频监控。",
            "next_source_en": "Run both ZICTA DFS sources; add low-frequency public app review, public news, and public social-page monitoring.",
        },
        {
            "area_cn": "舆情/声誉",
            "area_en": "Sentiment and Reputation",
            "coverage_cn": "低",
            "coverage_en": "Low",
            "gap_cn": "目前多为官方叙事，不能代表借款人声音或品牌舆情。",
            "gap_en": "Current signals are mostly official narratives and do not represent borrower voice or brand sentiment.",
            "next_source_cn": "增加公开新闻搜索结果、公开 app reviews、公开 Facebook/LinkedIn 页面，仅限无需登录内容。",
            "next_source_en": "Add public news results, public app reviews, and public Facebook/LinkedIn pages, only where no login is required.",
        },
        {
            "area_cn": "催收",
            "area_en": "Collections",
            "coverage_cn": "低",
            "coverage_en": "Low",
            "gap_cn": "缺少直接催收行为信号；只能从投诉、隐私、消费者保护间接推断。",
            "gap_en": "Direct collections-conduct signals are missing; current view is inferred from complaints, privacy, and consumer protection.",
            "next_source_cn": "在公开评论/投诉里增加 harassment、overdue、late payment、collections、contact 等关键词。",
            "next_source_en": "Add harassment, overdue, late payment, collections, contact keywords to public review/complaint monitoring.",
        },
        {
            "area_cn": "运营风险",
            "area_en": "Operational Risk",
            "coverage_cn": "中",
            "coverage_en": "Medium",
            "gap_cn": "支付轨道和网络/供应商信号不错，但还缺少将变更映射到内部流程的自动视图。",
            "gap_en": "Payment-rail and network/vendor signals are useful, but need automatic mapping into internal process impact.",
            "next_source_cn": "把 BoZ ZIPSS/NFS/Montran 信号固定映射到放款、还款、对账、客服排班、异常处理。",
            "next_source_en": "Map BoZ ZIPSS/NFS/Montran signals into disbursement, repayment, reconciliation, support staffing, and exception handling.",
        },
    ]
    if counts["payment_rails"] >= 8:
        rows[-1]["coverage_cn"] = "中高"
        rows[-1]["coverage_en"] = "Medium-high"
    if counts["privacy_data"] >= 5:
        rows[0]["coverage_cn"] = "中高"
    return rows


def assessment_table_rows(assessments: list[dict[str, str | int]], limit: int = 20) -> list[dict[str, str | int]]:
    ordered = sorted(
        assessments,
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}.get(str(item["impact_level"]), 3),
            int(item["priority"]),
        ),
    )
    return ordered[:limit]
