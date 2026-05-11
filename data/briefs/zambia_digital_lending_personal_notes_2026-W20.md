# 数字借贷个人研究笔记 - 2026-W20

Platform version: v0.5 Business Interpretation Layer

这是一份个人公开来源研究笔记，用于市场理解和能力建设。它不是法律意见、监管结论、客户交付物或商业材料。

## 1. 执行摘要

本周笔记包含 70 条已复核公开来源信号和 9 条个人研究笔记；其中 55 条落在高潜在影响域，15 条落在中等潜在影响域，覆盖 8 个 lending ops 影响域。这里的“影响”是研究优先级，不是合规结论。

仅作为私人研究资料使用。请持续区分“来源事实”和“个人解释”。

## 2. 信息质量与阅读优先级

- 平均候选分：80/100
- 优先阅读：24
- 周报候选：44

- 周报候选: 44
- 优先阅读: 24
- 常规监控: 2

### 2.1 本周最值得看

| 信号 | 分类 | 风险 | 候选分 | 建议用途 | 原因 | 来源 |
| --- | --- | --- | ---: | --- | --- | --- |
| DFS Incident Reporting System lists mobile payment fraud and incomplete transaction as reportable public categories | complaint | high | 95 | 放入首页 Top 5，并回源复核 | 官方/高可信公开来源；直接影响小微贷款运营流程；需要优先人工回源；高风险标签 | [来源](https://dfscomplaints.zicta.zm/) |
| In particular, businesses are required to clearly communicate key terms relating to their services, including operating hours, conditions for access, pricing, and any limitations that may reasonably affect a consumer’s decision to engage with the service. Where such information is provided, it shoul | fees | high | 95 | 放入首页 Top 5，并回源复核 | 官方/高可信公开来源；直接影响小微贷款运营流程；需要优先人工回源；高风险标签 | [来源](https://www.ccpc.org.zm/#item-104) |
| Data Protection Enforcement: Ensure the effective enforcement of data protection laws in Zambia, safeguarding the privacy rights of individuals | privacy | high | 93 | 放入首页 Top 5，并回源复核 | 官方/高可信公开来源；直接影响小微贷款运营流程；需要优先人工回源；高风险标签 | [来源](https://www.dataprotection.gov.zm/#item-77) |
| Public Education: Educate individuals and organizations about data protection rights and responsibilities, fostering a culture of privacy awareness | privacy | high | 93 | 放入首页 Top 5，并回源复核 | 官方/高可信公开来源；直接影响小微贷款运营流程；需要优先人工回源；高风险标签 | [来源](https://www.dataprotection.gov.zm/#item-79) |
| Data Protection Commission public page highlights data-subject rights and responsible personal-data handling | privacy | high | 93 | 放入首页 Top 5，并回源复核 | 官方/高可信公开来源；直接影响小微贷款运营流程；需要优先人工回源；高风险标签 | [来源](https://www.dataprotection.gov.zm/) |


## 3. 五条迭代线行动板

| 迭代线 | 证据数 | 高影响 | 优先级 | 业务意义 | 下一步动作 |
| --- | ---: | ---: | --- | --- | --- |
| 监管与支付轨道 | 55 | 48 | 优先推进 | 这条线决定贷款产品能不能稳定放款、正确入账、解释费用，并在监管/消费者保护语境下保持可复核。 | 固定追踪 BoZ 支付系统、CCPC 消费者保护、DPC 数据保护；每条信号都映射到产品页面、支付异常、客服话术或复核清单。 |
| 竞品产品矩阵 | 25 | 13 | 优先推进 | 竞品变化最有价值的部分不是“谁存在”，而是额度、期限、费用表达、速度承诺、支付方式、客服/隐私入口如何组合成产品打法。 | 把已复核竞品信号继续结构化成额度档、期限、速度、支付成熟度、客服/隐私成熟度和公开信息缺口。 |
| 投诉、客服与舆情 | 8 | 7 | 优先推进 | 这条线更接近真实用户摩擦：不到账、扣费不清、客服解释不足、欺诈、账号或钱包问题，都会直接影响坏账、投诉和口碑。 | 增加公开 app listing/review、公开新闻和公开投诉关键词 watchlist；只抓公开页面，不碰登录、私域群组或借款人数据。 |
| 催收与客户沟通 | 18 | 18 | 优先推进 | 催收风险通常不会先以政策文件出现，而会从投诉、隐私边界、联系人使用、逾期解释和客服升级里显形。 | 在投诉/评论来源中强化 overdue、late payment、collection、harassment、contact、privacy 等关键词，并把结果映射到催收话术和升级边界。 |
| 周报解读与部署数据层 | 70 | 55 | 优先推进 | 平台的价值不在抓取次数，而在每周能不能产出一份可读、可复核、能指导学习重点的个人研究笔记。 | 云端展示用 GitHub snapshot 和生成的 Markdown/CSV，本地继续保留 SQLite 作为研究库；节点版本同步后让 Streamlit 自动刷新。 |

## 4. 本周业务判断

| 关键判断 | 为什么重要 |
| --- | --- |
| 支付轨道已经是小微贷款运营风险的核心变量，不只是银行后台问题。 | BoZ/ZIPSS/Montran/NFS 信号会影响放款到账、还款入账、失败交易、对账、客服解释和合作方管理。 |
| 费用与披露是监管/投诉/声誉风险交汇点。 | CCPC 与 BoZ 相关信号都指向清晰、充分、不可误导的信息披露，贷款产品需要把总成本、费用名称和扣款时点讲清楚。 |
| 投诉处理应被当成运营数据系统，而不是单纯客服事项。 | 支付失败、费用争议、隐私请求和催收争议需要统一分类、证据留存、SLA 和升级路径。 |
| 数据保护会影响 app 权限、风控建模和催收触达。 | 数字贷款依赖个人数据和第三方处理，隐私信号需要转化为数据清单、授权说明、供应商边界和客户权利流程。 |
| 竞品线已经从空白进入 phase-1 产品矩阵阶段。 | 已复核信号开始覆盖 FLoan、Lupiya、PremierCredit、PowerKwacha 的额度、期限、速度承诺、客群、支付路径、客服和隐私入口。下一步不是多抓，而是把这些字段结构化比较。 |

## 5. 小微贷款业务影响矩阵

### 5.1 竞品与市场动作

**等级:** high

**信号:** Support for mobile payments and installment-based repayment, with clear schedules and terms.

**对小微贷款业务的影响:** 首轮竞品官网/FAQ 监控已经能看到额度、期限、速度承诺、客群分层、支付路径、客服入口和隐私入口。对小微贷款业务最有用的是把这些信号整理成产品矩阵，而不是只保存网页标题。

**建议动作:** 维护竞品矩阵：机构、客群、产品、额度、期限、速度承诺、放款/还款通道、客服入口、隐私/账户控制入口。Google Play/public reviews 仍需单独批准后再启用。

**待验证问题:** 哪些竞品信号会改变产品定位：额度更高、期限更长、审批更快、支付轨道更强、客群更细、隐私/客服入口更清楚？

**来源:** [来源](https://www.floan.co/#item-31)

### 5.2 竞品与市场动作

**等级:** high

**信号:** The app supports flexible loan amounts and defined repayment options. Loan approval and disbursement are subject to eligibility checks and successful verification, with all terms and fees clearly disclosed to users. The app supports flexible loan amounts and defined repayment options. Loan approval

**对小微贷款业务的影响:** 首轮竞品官网/FAQ 监控已经能看到额度、期限、速度承诺、客群分层、支付路径、客服入口和隐私入口。对小微贷款业务最有用的是把这些信号整理成产品矩阵，而不是只保存网页标题。

**建议动作:** 维护竞品矩阵：机构、客群、产品、额度、期限、速度承诺、放款/还款通道、客服入口、隐私/账户控制入口。Google Play/public reviews 仍需单独批准后再启用。

**待验证问题:** 哪些竞品信号会改变产品定位：额度更高、期限更长、审批更快、支付轨道更强、客群更细、隐私/客服入口更清楚？

**来源:** [来源](https://www.floan.co/#item-50)

### 5.3 费用、定价与披露

**等级:** high

**信号:** 2020-01-01

**对小微贷款业务的影响:** 对贷款业务的影响集中在定价页面、借款确认页、逾期/罚息说明、客服解释和投诉风险。费用越复杂，越需要在客户旅程里提前解释。

**建议动作:** 把所有客户可能支付的金额拆成“本金、利息、服务费、罚费、第三方费用、支付轨道费用”，逐项检查是否在申请前、确认前和还款前可见。

**待验证问题:** 客户在点击确认前能否知道总成本？费用名称是否和实际扣款一致？支付轨道费用是否被误认为贷款费用？

**来源:** [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/DirectivesProhibitionAgainstUnwarrantedChargesandFeesandRegulationsofSpecificChargesDirectives2020.pdf)

### 5.4 投诉、客服与争议处理

**等级:** high

**信号:** BoZ Customer Complaints Handling and Resolution Directives (metadata-only PDF; manual read/OCR needed)

**对小微贷款业务的影响:** 对小微贷款的影响不是“有没有投诉入口”这么简单，而是投诉数据、处理时限、证据留存、跨团队升级和重复问题复盘能力。

**建议动作:** 建立 lending ops 投诉分类树：放款、还款、费用、欺诈、隐私、催收、客服态度、技术故障；每类都要有证据、负责人和关闭标准。

**待验证问题:** 哪些投诉会升级为监管风险？哪些投诉代表产品设计问题而不是单个客服问题？AI/自动化处理是否会造成解释不足？

**来源:** [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/BankofZambiaCustomerComplaintsHandlingandResolutionDirectives1.pdf#page=1-item-1)

### 5.5 竞品与市场动作

**等级:** high

**信号:** Floan is a microloan app in Zambia offering access to credit, with loan amounts of up to K 6,000, subject to eligibility and terms.

**对小微贷款业务的影响:** 首轮竞品官网/FAQ 监控已经能看到额度、期限、速度承诺、客群分层、支付路径、客服入口和隐私入口。对小微贷款业务最有用的是把这些信号整理成产品矩阵，而不是只保存网页标题。

**建议动作:** 维护竞品矩阵：机构、客群、产品、额度、期限、速度承诺、放款/还款通道、客服入口、隐私/账户控制入口。Google Play/public reviews 仍需单独批准后再启用。

**待验证问题:** 哪些竞品信号会改变产品定位：额度更高、期限更长、审批更快、支付轨道更强、客群更细、隐私/客服入口更清楚？

**来源:** [来源](https://www.floan.co/#item-29)

### 5.6 隐私、数据与授权

**等级:** high

**信号:** Account Delete Account Delete

**对小微贷款业务的影响:** 数字贷款高度依赖身份、设备、联系人、交易和还款数据。隐私信号会影响 app 权限、信用评估、风控模型、催收联系、第三方供应商和跨境处理。

**建议动作:** 为每类数据写出“收集目的、使用场景、保存期限、共享对象、客户权利入口”；尤其关注联系人/设备/位置/交易数据。

**待验证问题:** 哪些数据是放款必需，哪些只是优化模型？客户撤回授权后贷款和催收流程如何处理？供应商是否构成 processor/controller 风险？

**来源:** [来源](https://powerkwacha.app/accountdelete)

### 5.7 竞品与市场动作

**等级:** high

**信号:** Loans up to K1,000,000 for Small Medium Enterprises (SMEs). These loans are tailor-made to the needs of SMEs with personalized and flexible repayment plans according to the client’s business.

**对小微贷款业务的影响:** 首轮竞品官网/FAQ 监控已经能看到额度、期限、速度承诺、客群分层、支付路径、客服入口和隐私入口。对小微贷款业务最有用的是把这些信号整理成产品矩阵，而不是只保存网页标题。

**建议动作:** 维护竞品矩阵：机构、客群、产品、额度、期限、速度承诺、放款/还款通道、客服入口、隐私/账户控制入口。Google Play/public reviews 仍需单独批准后再启用。

**待验证问题:** 哪些竞品信号会改变产品定位：额度更高、期限更长、审批更快、支付轨道更强、客群更细、隐私/客服入口更清楚？

**来源:** [来源](https://www.premiercredit.co.zm/borrow/#item-74)

### 5.8 竞品与市场动作

**等级:** high

**信号:** This loan enables businesses to leverage the value of their sales ledger. Keep the receivables bills of your business as security and repay the credit when you receive cash from your customers.

**对小微贷款业务的影响:** 首轮竞品官网/FAQ 监控已经能看到额度、期限、速度承诺、客群分层、支付路径、客服入口和隐私入口。对小微贷款业务最有用的是把这些信号整理成产品矩阵，而不是只保存网页标题。

**建议动作:** 维护竞品矩阵：机构、客群、产品、额度、期限、速度承诺、放款/还款通道、客服入口、隐私/账户控制入口。Google Play/public reviews 仍需单独批准后再启用。

**待验证问题:** 哪些竞品信号会改变产品定位：额度更高、期限更长、审批更快、支付轨道更强、客群更细、隐私/客服入口更清楚？

**来源:** [来源](https://www.premiercredit.co.zm/borrow/#item-75)

### 5.9 支付轨道与资金流

**等级:** high

**信号:** Your mobile money account

**对小微贷款业务的影响:** 对小微贷款最直接的影响是放款到账、还款入账、失败交易处理、对账和合作方依赖。它不一定改变贷款产品本身，但会改变运营可用性、异常处理和客户体验。

**建议动作:** 建立支付轨道清单：哪些贷款流程依赖银行、钱包、NFS、ZIPSS、聚合器；为失败交易、延迟入账和重复扣款写清楚客服口径和升级路径。

**待验证问题:** 如果某条轨道延迟或不可用，借款人会看到什么？还款逾期计算是否会误伤客户？客服如何证明是轨道问题而非客户问题？

**来源:** [来源](https://www.premiercredit.co.zm/borrow/#item-67)

### 5.10 竞品与市场动作

**等级:** high

**信号:** Salary advances are the most affordable and convenient to meet your urgent cash needs. Approval happens in 24hrs and you get your money immediately. Get salary advances up to K10,000 .

**对小微贷款业务的影响:** 首轮竞品官网/FAQ 监控已经能看到额度、期限、速度承诺、客群分层、支付路径、客服入口和隐私入口。对小微贷款业务最有用的是把这些信号整理成产品矩阵，而不是只保存网页标题。

**建议动作:** 维护竞品矩阵：机构、客群、产品、额度、期限、速度承诺、放款/还款通道、客服入口、隐私/账户控制入口。Google Play/public reviews 仍需单独批准后再启用。

**待验证问题:** 哪些竞品信号会改变产品定位：额度更高、期限更长、审批更快、支付轨道更强、客群更细、隐私/客服入口更清楚？

**来源:** [来源](https://www.premiercredit.co.zm/borrow/#item-71)


## 6. 情报覆盖缺口

| 情报线 | 当前覆盖 | 主要缺口 | 下一步来源 |
| --- | --- | --- | --- |
| 监管/政策 | 中高 | 已有 BoZ、CCPC、DPC，但仍偏政策文件，需要转成业务流程影响。 | 继续 BoZ JSON:API、CCPC、DPC；补 BoZ publications/annual reports 的稳定文件路径。 |
| 竞品 | 中低 | phase-1 官网/FAQ watchlist 已建立并完成首轮复核，但 Google Play/app listing 和公开评论层仍未默认启用。 | 把已复核官网信号整理成竞品矩阵；再决定是否启用 Google Play/public app listing，用于观察 app 权限、评分、公开评论主题。 |
| 投诉/客服 | 中低 | 已有 ZICTA/CCPC/BoZ complaint 信号，但缺少真实公开用户评论和投诉主题趋势。 | 运行 ZICTA DFS 两个源；补公开 app review、公开新闻和公开社媒页面的低频监控。 |
| 舆情/声誉 | 低 | 目前多为官方叙事，不能代表借款人声音或品牌舆情。 | 增加公开新闻搜索结果、公开 app reviews、公开 Facebook/LinkedIn 页面，仅限无需登录内容。 |
| 催收 | 低 | 缺少直接催收行为信号；只能从投诉、隐私、消费者保护间接推断。 | 在公开评论/投诉里增加 harassment、overdue、late payment、collections、contact 等关键词。 |
| 运营风险 | 中高 | 支付轨道和网络/供应商信号不错，但还缺少将变更映射到内部流程的自动视图。 | 把 BoZ ZIPSS/NFS/Montran 信号固定映射到放款、还款、对账、客服排班、异常处理。 |

## 7. 监管观察

| 信号 | 分类 | 风险 | 来源 | 下一步 |
| --- | --- | --- | --- | --- |
| 2023-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2023/CBCIRCULARNO.16OF2023BANKOFZAMBIACYBERANDINFORMATIONRISKMANAGEMENTGUIDELINES.pdf) | Map to personal capability checklist: incident response, uptime, access control, vendor risk, and data-security monitoring. |
| The Data Protection Commissioner (DPC) of Zambia is charged with the responsibility and central authority for overseeing and enforcing data protection regulations in Public bodies and Private Institutions through licensing of Auditors, registration of data processors and controllers, to ensuring tha | privacy | low | [来源](https://www.dataprotection.gov.zm/#item-76) | Use as a practical checklist anchor: controller/processor status, registration, audit readiness. |
| Compliance Oversight: Monitor and regulate organizations' compliance with data protection regulations, and promoting responsible data handling practices | privacy | low | [来源](https://www.dataprotection.gov.zm/#item-78) | Use as a core DPC conduct signal for lending app data practices. |
| Data Protection Act Learn More | privacy | low | [来源](http://www.dataprotection.gov.zm/wp-content/uploads/2024/06/Act-No.-3-The-Data-Protection-Act-2021_0-2.pdf) | Create a follow-up task to manually extract lending-relevant concepts: controller, processor, consent, rights, registration, audit, cross-border transfer. |
| Control Your Data, Protect Your Rights | privacy | low | [来源](https://www.dataprotection.gov.zm/#item-93) | Track as a recurring privacy-awareness signal. |
| Data in Your Hands, Rights in Your Control | privacy | low | [来源](https://www.dataprotection.gov.zm/data-in-your-hands-rights-in-your-control/) | Use as a high-level privacy UX principle for public loan-app review. |
| PUBLIC NOTICE: CONSUMER RIGHTS AND ONGOING INQUIRY | regulatory | low | [来源](https://www.ccpc.org.zm/details/137) | Prefer details-page URLs over homepage fragment items when both are available. |
| The Competition and Consumer Protection Commission (“the Commission”) wishes to remind members of the public that the law provides for fair, transparent, and honest conduct in the marketplace. Consumers are entitled to receive accurate and sufficient information about goods and services to enable th | regulatory | low | [来源](https://www.ccpc.org.zm/#item-103) | Use as a high-level regulatory/conduct principle in personal notes. |
| Privacy Agreement Privacy Agreement | privacy | high | [来源](https://powerkwacha.app/agreement/privacy) | 回源阅读隐私、权限、账户删除和投诉入口；不要把页面措辞直接当作合规结论。 |
| Data Protection Enforcement: Ensure the effective enforcement of data protection laws in Zambia, safeguarding the privacy rights of individuals | privacy | high | [来源](https://www.dataprotection.gov.zm/#item-77) | Mark as high-priority privacy enforcement signal for future watch. |
| Public Education: Educate individuals and organizations about data protection rights and responsibilities, fostering a culture of privacy awareness | privacy | high | [来源](https://www.dataprotection.gov.zm/#item-79) | Use in personal notes when evaluating app permission wording and FAQ clarity. |
| Data Protection Commission public page highlights data-subject rights and responsible personal-data handling | privacy | high | [来源](https://www.dataprotection.gov.zm/) | Review consent, data-permission, and privacy wording in customer-facing journeys. |
| International Cooperation: Collaborate with international data protection authorities to facilitate cross-border data transfers and ensure global data protection standards are upheld. | privacy | low | [来源](https://www.dataprotection.gov.zm/#item-81) | Track as market question evidence for privacy_lending_apps and fintech vendor architecture. |
| Mandate of the Data Protection Commission in Zambia | privacy | low | [来源](https://www.dataprotection.gov.zm/#item-75) | Keep as low-detail source anchor; prefer richer mandate text from signal 184. |
| The Competition and Consumer Protection Commission (CCPC) signed a revised Memorandum of Understanding (MoU) with the COMESA Competition Commission (CCC) on 4th November, 2022 at Lusaka’s Mulungushi International Conference Center. The MoU has areas of cooperation which include; regional e-commerce | regulatory | low | [来源](https://www.ccpc.org.zm/#item-123) | Keep as background evidence for market-question regulatory_surface; do not over-weight for lending-specific conclusions. |
| PRESS BRIEFING BY THE NATIONAL COORDINATOR, MR. PERCY CHINYAMA ON THE ESTABLISHMENT OF THE OFFICE OF THE DATA PROTECTION COMMISSIONER | privacy | low | [来源](https://www.dataprotection.gov.zm/press-briefing-by-the-national-coordinator-mr-percy-chinyama-on-the-establishment-of-the-office-of-the-data-protection-commissioner/) | Keep as institutional context for regulatory_surface; do not over-weight in weekly notes. |
| Throughout March 2026, the Competition and Consumer Protection Commission (CCPC) conducted a series of routine inspections and sensitisation exercises across Zambia in collaboration with local authorities and partner institutions. The activities focused on promoting consumer welfare, product safety, | regulatory | low | [来源](https://www.ccpc.org.zm/#item-112) | Keep as low-priority context; avoid treating as lending-specific without stronger evidence. |
| CCPC public notice language reinforces clear, truthful, and sufficient consumer information | regulatory | low | [来源](https://www.ccpc.org.zm/) | Review support macros and escalation rules for repeated complaint themes. |

## 8. 支付轨道与借贷运营

| 信号 | 分类 | 风险 | 来源 | 下一步 |
| --- | --- | --- | --- | --- |
| 2022-01-01 | repayment | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2022/CBCIRCULARNO.16OF2022DUEDILIGENCEONENTITIESPARTNEREDWITHORENGAGEDTOPROVIDEPAYMENTSERVICES.pdf) | Translate into a partner-risk research question for mobile money, bank, aggregator, and collection/payment processors. |
| 2025-01-01 | repayment | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2025/CBCircularNo.04of2025MandatoryUseoftheMontranGatewayontheZambiaInterbankPaymentandSettlementSystem.pdf) | Map this to lending disbursement/repayment rails and ask which partners depend on ZIPSS gateway readiness. |
| 2025-01-01 | repayment | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2025/CBCircularNo.23of2025RevisionofOperatingRulesfortheZambiaInterbankPaymentandSettlement.pdf) | Treat as a priority manual-read item; extract any operational obligations affecting settlement timing and exceptions. |
| BoZ ATM/POS/Internet Transactions and Mobile Payments Directive 2020 (metadata-only PDF; manual read/OCR needed) | repayment | low | [来源](https://www.boz.zm/sites/default/files/migrated/regulatory/202002DomesticAutomatedTellerMachinePointofSaleInternetTransactionsandMobilePayments.pdf#page=1-item-1) | Manual-read for failed transactions, authentication, reversals, disputes, fees, and channel-security expectations. |
| BoZ Electronic Money Issuance Directives 2023 (metadata-only PDF; manual read/OCR needed) | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/regulatory/Directive202307ElectronicMoneyIssuance2023.pdf#page=1-item-1) | Manual-read the directive for e-money float, agents, customer funds, disclosure, and operational controls. |
| 2020-01-01 | fees | medium | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2020/CBCIRCULARNO07OF2020REVISIONOFTHEZIPSSFEES.pdf) | Track as cost-stack input; separate rail fees from borrower-facing fees. |
| 2022-01-01 | repayment | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2022/CBCIRCULARNO.13OF2022REVIEWOFTHEDRAFTNATIONALPAYMENTSYSTEMSVISIONANDSTRATEGY20232027.pdf) | Use as a pointer to locate the full strategy document and extract themes: interoperability, DFS, inclusion, cyber, complaints. |
| 2021-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2021/CBCIRCULARNO.19OF2021POSTIMPLEMENTATIONISSUESONTHENATIONALFINANCIALSWITCH.pdf) | Watch for repeated NFS issues that could affect failed transactions, reversals, and customer support load. |
| 2020-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2020/CBCIRCULARNO24OF2020GOLIVEDATESFORPHASETWOOFTHENATIONALFINANCIALSWITCH.pdf) | Use as background for Zambia retail payment interoperability timeline. |
| 2018-01-01 | repayment | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2018/CBCircularNo.012018NATIONALPAYMENTSYSTEMSDIRECTIVESONELECTRONICMONEYISSUANCE2018.pdf) | Use only as background when comparing evolution of e-money obligations. |
| 2025-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2025/CBCircularNo.18of2025SixDayOperationsattheBCMCentreforZIPSSCSDandBankSupervisionApplications.pdf) | Watch for operating-hours changes that could alter repayment posting, settlement windows, or support coverage. |
| 2024-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2024/CBCircularNo.16of2024ImplementationofExtendedOperatingHoursontheZIPSSandCSD.pdf) | Compare with lender repayment posting cutoffs and partner bank settlement windows. |
| 2024-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2024/CBCircularNo.20of2024NotificationofChangeofServiceProviderontheZIPSSCSDandEBoPSystemNetwork.pdf) | Track as infrastructure/vendor-dependency risk rather than consumer-facing conclusion. |
| 2022-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2022/CBCIRCULARNO.11OF2022UPGRADEANDISO20022MESSAGINGSTANDARDMIGRATIONFORTHEREALTIMEGROSSSETTLEMENTSYSTEM.pdf) | Track as rails modernization context; avoid inferring direct lender obligations without reading source PDF. |
| 2025-01-01 | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2025/GatewaySwitchingGuide.pdf) | Track whether gateway switching affects settlement dependencies, failed payment handling, or partner bank readiness. |
| BoZ Money Transfer Services Directives 2021 (metadata-only PDF; manual read/OCR needed) | regulatory | low | [来源](https://www.boz.zm/sites/default/files/migrated/regulatory/202109NationalPaymentSystemsMoneyTransferServicesDirectives.pdf#page=1-item-1) | Manual-read for agent, transfer, disclosure, AML/CFT, and customer-service obligations relevant to payout/repayment rails. |

## 9. 竞品变化

| 信号 | 分类 | 风险 | 来源 | 下一步 |
| --- | --- | --- | --- | --- |
| Account Delete Account Delete | competitor_change | low | [来源](https://powerkwacha.app/accountdelete) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| Salary advances are the most affordable and convenient to meet your urgent cash needs. Approval happens in 24hrs and you get your money immediately. Get salary advances up to K10,000 . | competitor_change | low | [来源](https://www.premiercredit.co.zm/borrow/#item-71) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| Personal loans can help you cover large expenses. You can either buy assets, finance your education, and or home improvement with a Personal Loan of up to K250,000 up to 60 months . | competitor_change | low | [来源](https://www.premiercredit.co.zm/borrow/#item-72) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| Once approved, your funds are sent directly to your account or creditors. | competitor_change | low | [来源](https://www.lupiya.com/#item-78) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| Email support@floan.co Email | competitor_change | medium | [来源](https://www.floan.co/) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| This loan is designed to support farmers seeking funds for land, equipment, or operational expenses, and an agribusiness looking to expand or modernize agricultural production. | competitor_change | medium | [来源](https://www.premiercredit.co.zm/borrow/#item-77) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| Consumer Hotline：+260 773 868 979 Consumer Hotline：+260 773 868 979 | competitor_change | low | [来源](https://powerkwacha.app/#item-8) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| This loan is used to improve a company’s working capital and cash flow when they have orders to execute. It allows a business (SME) to draw money against a confirmed purchase order from its customer. | competitor_change | low | [来源](https://www.premiercredit.co.zm/borrow/#item-76) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| Upload all required documents and submit for our internal processing. Get your loan decision within minutes | competitor_change | low | [来源](https://www.premiercredit.co.zm/borrow/#item-63) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| PremierCredit Partners with Airtel Money to Unveil Loan Services | competitor_change | low | [来源](https://www.premiercredit.co.zm/news/premiercredit-partners-with-airtel-money-to-unveil-loan-services/) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |
| Get a Loan in 30 seconds | competitor_change | low | [来源](https://www.lupiya.com/#item-67) | 回源确认额度、期限、费用、速度承诺、支付/放款路径和客服/隐私入口；只作为公开竞品信号记录。 |

## 10. App 评价与投诉主题

| 信号 | 分类 | 风险 | 来源 | 下一步 |
| --- | --- | --- | --- | --- |
| Support for mobile payments and installment-based repayment, with clear schedules and terms. | fees | medium | [来源](https://www.floan.co/#item-31) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| The app supports flexible loan amounts and defined repayment options. Loan approval and disbursement are subject to eligibility checks and successful verification, with all terms and fees clearly disclosed to users. The app supports flexible loan amounts and defined repayment options. Loan approval | fees | medium | [来源](https://www.floan.co/#item-50) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| 2020-01-01 | fees | medium | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/DirectivesProhibitionAgainstUnwarrantedChargesandFeesandRegulationsofSpecificChargesDirectives2020.pdf) | Map public fee controls to lending product fee disclosure, penalty-fee language, and customer complaint triggers. |
| BoZ Customer Complaints Handling and Resolution Directives (metadata-only PDF; manual read/OCR needed) | complaint | medium | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/BankofZambiaCustomerComplaintsHandlingandResolutionDirectives1.pdf#page=1-item-1) | Manual-read for complaint intake, resolution timeframes, escalation, evidence retention, and customer communication norms. |
| Floan is a microloan app in Zambia offering access to credit, with loan amounts of up to K 6,000, subject to eligibility and terms. | fees | low | [来源](https://www.floan.co/#item-29) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| Loans up to K1,000,000 for Small Medium Enterprises (SMEs). These loans are tailor-made to the needs of SMEs with personalized and flexible repayment plans according to the client’s business. | repayment | low | [来源](https://www.premiercredit.co.zm/borrow/#item-74) | 回源确认还款频率、扣款方式、宽限期、逾期处理和客户解释口径。 |
| This loan enables businesses to leverage the value of their sales ledger. Keep the receivables bills of your business as security and repay the credit when you receive cash from your customers. | repayment | low | [来源](https://www.premiercredit.co.zm/borrow/#item-75) | 回源确认还款频率、扣款方式、宽限期、逾期处理和客户解释口径。 |
| Your mobile money account | disbursement | low | [来源](https://www.premiercredit.co.zm/borrow/#item-67) | 回源核对放款、还款、失败交易、对账和移动钱/银行轨道依赖。 |
| Thanks to our partnerships with Mobile Money Providers and banks, transferring money, paying bills, and keeping track of your payment activities are now just a touch away. | disbursement | low | [来源](https://www.premiercredit.co.zm/#item-111) | 回源核对放款、还款、失败交易、对账和移动钱/银行轨道依赖。 |
| Instant Loan Get K500 instantly and pay it back over 3 months. Coming soon Get K500 instantly and pay it back over 3 months. Coming soon | fees | low | [来源](https://www.lupiya.com/loans) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| Civil Servant Loans Low interest loans for government workers. Apply now > Low interest loans for government workers. Apply now > | fees | low | [来源](https://www.lupiya.com/civil-service) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| Collateral-backed Loans Have an asset? Use it to get a bigger loan with better rates. Apply now > Have an asset? Use it to get a bigger loan with better rates. Apply now > | fees | low | [来源](https://app.lupiya.com/collateral-backed-loan) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| Select type of loan and choose repayment plan and rate that works for you. | repayment | low | [来源](https://www.lupiya.com/#item-77) | 回源确认还款频率、扣款方式、宽限期、逾期处理和客户解释口径。 |
| In particular, businesses are required to clearly communicate key terms relating to their services, including operating hours, conditions for access, pricing, and any limitations that may reasonably affect a consumer’s decision to engage with the service. Where such information is provided, it shoul | fees | high | [来源](https://www.ccpc.org.zm/#item-104) | Use as a core taxonomy anchor for fees/disclosure review. |
| DFS Incident Reporting System lists mobile payment fraud and incomplete transaction as reportable public categories | complaint | high | [来源](https://dfscomplaints.zicta.zm/) | Review support macros and escalation rules for repeated complaint themes. |
| Agri Loans Supporting farmers with loans for seeds, equipment, or harvesting Apply now > Supporting farmers with loans for seeds, equipment, or harvesting Apply now > | fees | medium | [来源](https://app.lupiya.com/business-clients/agri-loan) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| 2023-01-01 | complaint | medium | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/circulars/banks/2023/CBCIRCULARNO.34OF2023DEPLOYMENTOFARTIFICIALINTELLIGENCEINFINANCIALCOMPLAINTHANDLINGINTEGRATIONANDREFRESHERTRAININGINUSERACCEPTANCETESTING.pdf) | Watch whether AI complaint tooling changes dispute handling norms or regulator expectations for structured complaint data. |
| Sensitisation activities were also conducted across the country. In Solwezi, CCPC partnered with the Pensions and Insurance Authority to hold a consumer rights sensitisation at Mitech Market featuring dance, sketches, and one-on-one engagements. In Kasama, learners from Kasama Boys Secondary School | repayment | medium | [来源](https://www.ccpc.org.zm/#item-114) | Track whether public education themes connect to credit, insurance, pensions, mobile money, or lending-adjacent conduct. |
| Loans for Yango Drivers Get money for car expenses like fuel top up, car maintenance. Get money for car expenses like fuel top up, car maintenance. | fees | low | [来源](https://www.lupiya.com/loans) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| Lupiya for Women Special loans to help women grow their businesses. Learn more > Special loans to help women grow their businesses. Learn more > | fees | low | [来源](https://app.lupiya.com/women) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| Zambia Defence Forces Tailored loans for our heroes in uniform. Apply now > Tailored loans for our heroes in uniform. Apply now > | fees | low | [来源](https://app.lupiya.com/zambia-defence-forces/fixed-term-loan) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| Get a loan in just 5 Minutes | fees | low | [来源](https://www.lupiya.com/loans#item-72) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |

## 11. 声誉与新闻信号

| 信号 | 分类 | 风险 | 来源 | 下一步 |
| --- | --- | --- | --- | --- |
| Consumers are also encouraged to seek clarification where information is unclear and to report concerns where they believe their rights may have been infringed. Consumers are also encouraged to seek clarification where information is unclear and to report concerns where they believe their rights may | news_signal | low | [来源](https://www.ccpc.org.zm/#item-106) | Use as evidence for the complaint_themes and disclosure-related market questions. |
| The law further prohibits unfair trading practices, including misleading representations, false or incomplete disclosure of material information, and conduct that may be considered unconscionable. These provisions are designed to promote fairness, accountability, and confidence in the marketplace fo | news_signal | high | [来源](https://www.ccpc.org.zm/#item-105) | Track as a high-value conduct-risk signal for public lending-app and website review. |
| CCPC is determined to work towards safer markets that will ensure business compliance and a more informed consumer base that will access services and products with confidence. | news_signal | low | [来源](https://www.ccpc.org.zm/#item-115) | Map this to disclosure, support, and customer-education themes in weekly notes. |

## 12. 运营模式笔记

- 观察公开投诉语言如何映射到真实运营域：客服、放款、还款、催收、欺诈、隐私和披露。
- 判断重复出现的公开信号到底是来源质量问题、市场共性摩擦，还是一次性噪声。
- 始终把来源事实和个人推断分开记录。
- 对支付轨道信号，要区分基础设施/合作伙伴依赖与直接面向借款人的产品规则。

## 13. 个人研究笔记

| 笔记 | 类型 | 市场问题 | 信心 |
| --- | --- | --- | --- |
| Phase-1 competitor watch review | market_observation | Which competitor product, payment, support, and privacy signals matter most for Zambia micro-lending ops? | medium |
| Payment rails affect lending ops before they look like lending rules | market_observation | payment_rails_lending_ops | medium |
| BoZ payment rails line is metadata-first, then manual-read | capability_line | payment_rails_lending_ops | high |
| DPC source creates a privacy capability line for lending research | market_observation | What privacy and data-subject rights themes should a lending app operator understand from public sources? | high |
| DPC source requires SSL fallback but produces useful privacy signals | source_quality | Which public sources are stable enough for recurring Scrapling collection, and which need fallback/manual review? | high |
| CCPC signals split into conduct principles vs noise | taxonomy_learning | Which CCPC public signals transfer cleanly into digital lending operations research? | high |
| Disclosure and pricing are the strongest CCPC-to-lending bridge | market_observation | Which disclosure failures would create the highest risk for a public loan-app review? | high |
| CCPC selector noise | market_observation | Which selectors produce useful consumer-protection signals without boilerplate noise? | high |
| Personal research mode reset | market_observation | Which public signals best explain Zambia digital lending market risk without using private knowledge? | high |

## 14. 市场问题

| 领域 | 问题 | 状态 | 当前假设 | 证据 |
| --- | --- | --- | --- | --- |
| Complaints | Which public complaint themes appear most often around digital financial services and lending-adjacent journeys? | investigating | For public-source lending research, the strongest CCPC-derived complaint themes are unclear material information, pricing/term disclosure, misleading representations, and consumer ability to report concerns. | Reviewed signals 23, 24, 25, and 26 from CCPC public-source scrape; rejected non-lending goods seizure and navigation noise. |
| Payment rails | How do BoZ payment-system rules, payment-rail changes, and mobile-money/payment-service directives affect digital lending disbursement, repayment, failed transactions, complaints, fees, and partner risk? | investigating | BoZ payment-rails signals matter to lending ops through three practical channels: payment availability/settlement windows, partner due diligence for payment-service providers, and customer-facing complaint/fee/dispute controls. | Reviewed BoZ signals include Montran Gateway/ZIPSS circulars, National Financial Switch items, Cyber and Information Risk Management Guidelines, payment-service partner due diligence, unwarranted charges directives, e-money/mobile-payments/money-transfer/complaints directives as manual-read sources. |
| Privacy | What privacy and data-subject rights themes should a lending app operator understand from public sources? | investigating | The most important public privacy themes for lending apps are data-subject rights, consent/permission clarity, controller/processor registration, responsible data handling, enforcement risk, and cross-border transfer awareness for SaaS/vendor stacks. | Reviewed DPC signals 184-190 and 192; Data Protection Act PDF signal 189 should become a manual reading task. |
| Regulatory watch | Which public regulator pages are most useful for tracking lending, payments, consumer protection, and data protection risk? | investigating | CCPC is useful as a broad conduct and consumer-protection source, but it needs manual filtering before it becomes useful for digital lending notes. | CCPC source produced both useful conduct-principle signals and substantial noise; reviewed 9 useful/low-to-high relevance items and rejected 16 noisy or duplicated items. |
| Research process | Which public sources are stable enough for recurring Scrapling collection, and which should remain manual review sources? | investigating | CCPC is reachable through Scrapling with noise filtering; DPC needs a documented SSL fallback but produces higher-quality privacy signals after manual filtering. | CCPC latest run: 24 signals after exclude_keywords. DPC latest run: 17 signals via source-scoped SSL fallback; 10 reviewed and 7 rejected as navigation/title noise. |
| Fraud and payments | Where do mobile-money fraud, incomplete transaction, and customer-support issues overlap with lending operations? | open |  |  |

## 15. 来源健康度

| 来源 | 运行 | 成功 | 失败 | 最近状态 | 最近信号 |
| --- | ---: | ---: | ---: | --- | ---: |
| Competitor Watch - FLoan Home | 1 | 1 | 0 | success | 14 |
| Competitor Watch - PowerKwacha Home | 1 | 1 | 0 | success | 5 |
| Competitor Watch - FairMoney Zambia FAQ | 1 | 1 | 0 | success | 0 |
| Competitor Watch - FairMoney Zambia Personal Loans | 1 | 1 | 0 | success | 0 |
| Competitor Watch - PremierCredit Borrow | 1 | 1 | 0 | success | 18 |
| Competitor Watch - PremierCredit Home | 1 | 1 | 0 | success | 30 |
| Competitor Watch - Lupiya Loans | 3 | 2 | 1 | success | 14 |
| Competitor Watch - Lupiya Home | 1 | 1 | 0 | success | 13 |
| Bank of Zambia Regulatory Documents API | 4 | 3 | 1 | success | 38 |
| Bank of Zambia ZIPSS Operating Rules Revision Circular 2025 | 1 | 1 | 0 | success | 0 |

## 16. 催收与行为观察

_暂无已复核条目。_

## 17. 重点风险 Top 5

| 信号 | 分类 | 风险 | 来源 | 下一步 |
| --- | --- | --- | --- | --- |
| Privacy Agreement Privacy Agreement | privacy | high | [来源](https://powerkwacha.app/agreement/privacy) | 回源阅读隐私、权限、账户删除和投诉入口；不要把页面措辞直接当作合规结论。 |
| Data Protection Enforcement: Ensure the effective enforcement of data protection laws in Zambia, safeguarding the privacy rights of individuals | privacy | high | [来源](https://www.dataprotection.gov.zm/#item-77) | Mark as high-priority privacy enforcement signal for future watch. |
| Public Education: Educate individuals and organizations about data protection rights and responsibilities, fostering a culture of privacy awareness | privacy | high | [来源](https://www.dataprotection.gov.zm/#item-79) | Use in personal notes when evaluating app permission wording and FAQ clarity. |
| In particular, businesses are required to clearly communicate key terms relating to their services, including operating hours, conditions for access, pricing, and any limitations that may reasonably affect a consumer’s decision to engage with the service. Where such information is provided, it shoul | fees | high | [来源](https://www.ccpc.org.zm/#item-104) | Use as a core taxonomy anchor for fees/disclosure review. |
| The law further prohibits unfair trading practices, including misleading representations, false or incomplete disclosure of material information, and conduct that may be considered unconscionable. These provisions are designed to promote fairness, accountability, and confidence in the marketplace fo | news_signal | high | [来源](https://www.ccpc.org.zm/#item-105) | Track as a high-value conduct-risk signal for public lending-app and website review. |

## 18. 下一步学习动作

| 信号 | 分类 | 风险 | 来源 | 下一步 |
| --- | --- | --- | --- | --- |
| Support for mobile payments and installment-based repayment, with clear schedules and terms. | fees | medium | [来源](https://www.floan.co/#item-31) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| The app supports flexible loan amounts and defined repayment options. Loan approval and disbursement are subject to eligibility checks and successful verification, with all terms and fees clearly disclosed to users. The app supports flexible loan amounts and defined repayment options. Loan approval | fees | medium | [来源](https://www.floan.co/#item-50) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |
| 2020-01-01 | fees | medium | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/DirectivesProhibitionAgainstUnwarrantedChargesandFeesandRegulationsofSpecificChargesDirectives2020.pdf) | Map public fee controls to lending product fee disclosure, penalty-fee language, and customer complaint triggers. |
| BoZ Customer Complaints Handling and Resolution Directives (metadata-only PDF; manual read/OCR needed) | complaint | medium | [来源](https://www.boz.zm/sites/default/files/migrated/financial-stability/BankofZambiaCustomerComplaintsHandlingandResolutionDirectives1.pdf#page=1-item-1) | Manual-read for complaint intake, resolution timeframes, escalation, evidence retention, and customer communication norms. |
| Floan is a microloan app in Zambia offering access to credit, with loan amounts of up to K 6,000, subject to eligibility and terms. | fees | low | [来源](https://www.floan.co/#item-29) | 回源核对 APR、服务费、逾期费、还款示例和披露位置。 |

## 19. 来源

本笔记中的主要来源均已在上方表格中链接。只应使用公开网页、公开 app listing、官方公告、公开新闻，以及你手动批准的公开 watchlist。

## 20. 能力建设检查清单

- 本周是否至少运行过一个 Scrapling 公开来源抓取？
- 是否复核并分类了最有价值的信号？
- 是否写了至少一条个人研究笔记？
- 是否更新了至少一个市场问题？
- 是否检查了 source health，并判断哪些来源适合自动化、哪些需要手动复核？
- 是否记录了下周要继续追踪的开放问题？
- 是否避免了私人、雇主、借款人或专有数据？
