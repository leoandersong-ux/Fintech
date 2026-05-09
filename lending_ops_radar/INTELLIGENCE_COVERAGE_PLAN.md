# Lending Ops Intelligence Coverage Plan

中文：这个文件把平台从“公开资料收集器”推进到“个人业务研究平台”。重点不是多抓网页，而是把公开信号解释成对小微金融贷款业务的影响。

English: This file moves the platform from a public-source collector toward a personal business research workspace. The point is not to crawl more pages; it is to interpret public signals into micro-lending operating impact.

## 1. 核心原则 | Core Principle

每条情报都要回答四个问题：

1. 这条公开信号影响哪一个小微贷款流程？
2. 它更像监管、竞品、投诉、舆情、客服、催收，还是运营风险？
3. 业务上应该检查什么，而不是立刻得出什么合规结论？
4. 还缺什么来源，才能让判断更可靠？

Every intelligence item should answer four questions:

1. Which micro-lending process does this public signal affect?
2. Is it mainly regulatory, competitor, complaint, sentiment, support, collections, or operational risk?
3. What should the business inspect, without turning it into a legal conclusion?
4. Which source is still missing before the interpretation becomes reliable?

## 2. 情报线 | Intelligence Lanes

| 情报线 Lane | 当前状态 Current State | 对小微贷款业务的意义 Lending Ops Meaning | 下一步自动化 Next Automation |
| --- | --- | --- | --- |
| 监管/政策 Regulatory | BoZ、CCPC、DPC 已接入，BoZ payment systems 线较强。/ BoZ, CCPC, and DPC are connected; BoZ payment rails are the strongest lane. | 转化为费用披露、投诉处理、支付失败、数据授权、合作方依赖等流程检查。/ Convert into process checks for fee disclosure, complaints handling, failed payments, data consent, and partner dependency. | 继续 BoZ JSON:API；为重要 PDF 建固定锚点；把每类政策信号映射到 lending process。/ Continue BoZ JSON:API; keep fixed PDF anchors; map policy signals to lending processes. |
| 竞品 Competitors | 目前覆盖弱，只有 watchlist 模板。/ Weak coverage; only watchlist templates exist. | 观察额度、期限、费用、审批速度、FAQ、app 权限、公开评价变化。/ Track limits, tenor, fees, approval speed, FAQ, app permissions, and public-review changes. | 建手动批准的 competitor websites + Google Play public listing 文件，不硬编码不确定 app ID。/ Build a manually approved competitor website + Google Play public listing file; do not hard-code uncertain app IDs. |
| 投诉/客服 Complaints and Support | ZICTA/CCPC/BoZ complaint 信号可用，但真实用户声音不足。/ ZICTA/CCPC/BoZ complaint signals exist, but real user voice is thin. | 建立客服工单分类法：放款、还款、费用、欺诈、隐私、催收、系统故障、客服态度。/ Build support taxonomy: disbursement, repayment, fees, fraud, privacy, collections, system failure, support conduct. | 增加公开 app reviews、公开新闻、公开社媒页面；只用无需登录内容。/ Add public app reviews, public news, and public social pages; no login-required content. |
| 舆情/声誉 Sentiment and Reputation | 目前多为官方叙事，不能代表借款人声音。/ Mostly official narrative today, not borrower voice. | 捕捉公众敏感词：隐藏费用、到账慢、扣款失败、骚扰催收、隐私滥用、客服无响应。/ Watch public sensitivity terms: hidden fees, slow payout, failed deductions, harassment, privacy misuse, no support response. | 建低频公开新闻与公开评论关键词监控，人工复核后再进入周报。/ Add low-frequency public-news and public-review keyword monitoring, human-reviewed before weekly notes. |
| 催收 Collections | 直接公开来源弱，只能从投诉、隐私、消费者保护间接推断。/ Direct public sources are weak; current view is inferred from complaints, privacy, and consumer protection. | 关注触达频率、第三方联系人、误催、争议暂停、已还款仍催、隐私边界。/ Watch contact frequency, third-party contact, false collections, dispute pause, paid-but-chased cases, and privacy boundaries. | 在评论/投诉关键词中加入 harassment、overdue、late payment、collections、contact、threat 等词。/ Add harassment, overdue, late payment, collections, contact, and threat keywords to review/complaint monitoring. |
| 运营风险 Operational Risk | 支付轨道和来源健康度已有基础。/ Payment rails and source health are now usable. | 影响放款、还款入账、对账、退款/冲正、客服排班、异常积压、供应商 SLA。/ Affects payout, repayment posting, reconciliation, reversals, support staffing, exception backlog, and vendor SLA. | 把 BoZ ZIPSS/NFS/Montran 信号固定映射到运营日历与异常处理清单。/ Map BoZ ZIPSS/NFS/Montran signals into an ops calendar and exception-handling checklist. |

## 3. 输出字段 | Output Fields

平台中的业务解读不应只显示标题和链接。每条已复核信号至少应生成：

- `impact_domain`: 影响域，例如支付轨道、费用披露、隐私、投诉、催收。
- `impact_level`: high / medium / low。
- `lending_impact`: 对小微贷款业务的具体影响。
- `affected_processes`: 受影响流程，例如放款、还款、客服、对账、催收。
- `recommended_actions`: 下一步检查动作，不是法律结论。
- `follow_up_questions`: 需要人工继续追问的问题。
- `source_link`: 来源链接。
- `coverage_gap`: 当前还缺什么来源。

## 4. 当前缺口判断 | Current Gap Assessment

当前平台已经能支撑监管和 payment rails 线的能力建设，但还不能称为完整市场情报系统。主要缺口是：

- 竞品 watchlist 尚未建立。
- 公开 app reviews 和公开用户评论不足。
- 舆情来源偏官方，缺真实借款人语言。
- 催收只能间接推断，不能过度解释。
- 政策 PDF 仍需要人工读重点段落，避免“标题即结论”。

The platform can now support regulatory and payment-rails learning, but it is not yet a full market-intelligence system. Main gaps:

- Competitor watchlist is not built.
- Public app reviews and user comments are insufficient.
- Sentiment sources are mostly official, not borrower language.
- Collections must be inferred conservatively.
- Policy PDFs still need manual reading of important passages; titles are not conclusions.

## 5. 下一阶段工作 | Next Stage

1. 使用 Streamlit 的 `业务解读 Intelligence` tab 作为主阅读入口。
2. 每周只把 `reviewed` 或 `briefed` 信号进入周报。
3. 优先补竞品和公开用户声音，而不是继续增加政策页。
4. 为每条重要政策/PDF 写一条个人研究笔记，明确“来源事实”和“我的推断”。
5. 每周更新一条市场问题，例如“哪些投诉主题最可能影响小微贷款留存/坏账/声誉？”

Next:

1. Use the Streamlit `业务解读 Intelligence` tab as the main reading view.
2. Let only `reviewed` or `briefed` signals enter weekly notes.
3. Prioritize competitor and public user voice over more policy pages.
4. Write a personal note for each important policy/PDF, separating source fact from inference.
5. Update one durable market question each week, such as "Which complaint themes most affect retention, credit loss, or reputation?"
