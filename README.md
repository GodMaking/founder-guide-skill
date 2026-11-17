# 创业者指南（founder-guide）

> **一句话定义**：创业者指南（founder-guide）——把 47 本创业经典蒸馏成一套能直接用的判断方法。你问“我想做 XX，值不值得”，它先问五个事实，再定阶段、过四道闸门、算数字，最后给一张决策卡：**做 / 小步验证 / 停**，外加一个 7 天内能做完的动作和止损线。书是来源，交付物是判断结果。

它不是书库，是判断器。免费版功能完整，源码、模板、案例与文档全部公开。

```bash
npx -y skills add GodMaking/founder-guide-skill -g --all
```

## 它解决什么问题

| 你现在的状态 | 它给你的东西 |
|---|---|
| “我想做 XX，不知道值不值得” | 五个事实 + 四道闸门 → 决策卡（做/验证/停） |
| “在做，但不知道卡在哪一步” | 15 题自测 → 阶段 + 关键维度 + 三个动作 |
| “不知道该怎么问客户” | 十人访谈脚本，每题标明要拿到什么信号 |
| “不敢开口报价” | 一页报价单 + 三个定价锚 + 五种异议应对 |
| “做出来了，但账算不清” | 单位经济速算：毛利率、盈亏平衡量、可触达客户覆盖倍数 |
| “现金不知道还能撑多久” | runway 计算，并按“成本两倍估”给出真实可用周期 |
| “书读了很多，用不上” | 47 本书按处境索引，一次只取一条，取完必须落成动作 |
| “想把一本书变成可读的方法论” | 蒸馏流水线：约 3 万字成书 + 脚本硬校验 |

## 和“AI 总结”“读书笔记”“书单库”有什么区别

| 维度 | 普通 AI 总结 | 读书笔记 | 书摘/书单库 | Founder Guide |
|---|---|---|---|---|
| 产出 | 几千字要点 | 结构散的个人记录 | 别人的观点合集 | 结论（做/验证/停）+ 数字 + 一个动作 |
| 是否给结论 | 不给 | 不给 | 不给 | 只给三种，不许“值得关注”这类中间态 |
| 是否要证据 | 不要求 | 不要求 | 不要求 | 替代方案成本与付费证据缺失就不给结论，只给“去验证什么” |
| 是否可执行 | 只能自己看 | 只能自己看 | 只能自己看 | 动作明确到人、天、钱、指标，并附止损线 |
| 质量门槛 | 无 | 无 | 无 | 四道闸门必须出数字；蒸馏另有脚本硬校验（字数 ±10%、章数 ≥8、中文占比 ≥70%、无占位符） |

## 演示：一张决策卡

```text
输入：我想做面向独立开发者的「周报生成器」，客单价 99 元/月，每月能触达 300 个独立开发者。

结论：小步验证
- 阶段：S1（有人询价，无预付）
- 有用性：替代方案 1,200 元/年 ÷ 你的 1,188 元/年 = 1.0 倍 → 不过
- 单位经济：毛利率 90%，CAC 回收 3.4 个月 → 过
- 时间：见效 3 个月 ÷ runway 15 个月 = 20% → 过
- 7 天动作：把年费改到 399 元，向 20 个非熟人报价，目标 3 个付费
- 止损线：30 天付费 < 3 人 → 停
```

完整三段案例见 [case-book.md](skills/founder-guide/assets/samples/case-book.md)（数字为虚拟，只示范判断链）。

## 安装

### 一键安装

```bash
npx -y skills add GodMaking/founder-guide-skill -g --all
```

### 手动安装

```bash
git clone https://github.com/GodMaking/founder-guide-skill.git
# 把 skills/founder-guide 复制到你所用客户端的 Agent Skills 目录
```

支持 Agent Skills 的客户端：Claude Code、Codex、Cursor、Windsurf 等。

### 验证安装

在仓库根目录运行：

```bash
python3 skills/founder-guide/scripts/startup_calc.py value --substitute-cost 3000 --my-cost 900
python3 skills/founder-guide/scripts/diagnose.py --answers "2,1,2,1,0,0,1,0,0,1,1,0,1,0,0"
```

看到“数字 + 判读 + 动作”即安装成功。Python 脚本只用标准库，不需要联网或付费 API。

### 环境要求

- Python 3（脚本纯标准库）
- `pdftotext`（poppler-utils），仅处理 PDF 时需要
- `lark-cli`，仅处理飞书/豆包文档时需要

## 快速开始

判断方向：

```text
使用 $founder-guide 帮我判断这个方向：我想做 XX，客单价 YY，每月能触达 ZZ 个客户
```

不知道卡在哪：

```text
使用 $founder-guide 给我做一次阶段自测，15 题
```

问客户、报价：

```text
使用 $founder-guide 给我一份访谈脚本，我要去问 10 个目标客户
```

蒸书（第二用法）：

```text
使用 $founder-guide 把这本书蒸馏成成书：./books/穷查理宝典.pdf
```

## 判断流程（默认主流程，六步不许跳）

1. **建档**：项目事实落盘到 `startup-profile.json`，之后每轮只更新变化项，不重复盘问
2. **五问事实**：替代方案成本、付费证据（预付 > 意向 > 询价 > 口头）、现金与月净流出、手上最靠后的成果、最大可承受损失
3. **定模式**：内容 / 软件 / 门店 / 制造 / 服务，各自看不同的三个数
4. **定阶段**：S0 想法 → S1 验证 → S2 原型 → S3 首批交付 → S4 量产 → S5 规模化，判据只用过关证据
5. **过四闸门**：必须出数字，不接受“感觉还行”
6. **出决策卡**：结论 + 7 天动作 + 止损线，然后记账，季度对账

## 四道闸门

| 闸门 | 判据 | 不过怎么办 |
|---|---|---|
| 有用性 | 替代方案成本 ÷ 你的成本 ≥ 2 | 换人群，或把成本压到替代方案的 1/3 |
| 单位经济 | 固定成本 ÷ 单位毛利 = 盈亏平衡量；超过可触达客户即不过 | 降固定成本，或提毛利 |
| 时间 | 见效周期 ÷ runway > 60% | 先做 30 天内能收钱的小版本 |
| 风险红线 | 资质不可得、单点依赖 >40%、突破可承受损失、负现金流扩产 | 一票否决，不给折中方案 |

配套速算器：

```bash
python3 skills/founder-guide/scripts/startup_calc.py value  --substitute-cost 3000 --my-cost 900
python3 skills/founder-guide/scripts/startup_calc.py unit   --price 199 --variable 80 --fixed 12000 --reach 500
python3 skills/founder-guide/scripts/startup_calc.py idiot  --part-cost 13000 --raw-cost 200
python3 skills/founder-guide/scripts/startup_calc.py gap    --current 1000000 --target 100
python3 skills/founder-guide/scripts/startup_calc.py runway --cash 180000 --burn 30000 --lead-months 8
python3 skills/founder-guide/scripts/diagnose.py --interactive
```

输出永远是「数字 + 判读 + 动作」，例如：白痴指数 65 倍 →「冗余严重，先删部件不要先砍价」。

## 五类生意看不同的数

| 模式 | 必算三个数 | 一票否决线 |
|---|---|---|
| 内容/知识付费 | 单份获客成本、留资→付费转化率、月稳定产出上限 | 获客成本 > 单价 1/3 |
| 软件/SaaS | CAC 回收月数、月流失率、LTV/CAC | 回收期 > 12 个月 |
| 实体门店 | 月固定成本、盈亏平衡入住率、回本期 | 入住率 > 65% 或回本期 > 24 个月 |
| 制造/硬件 | 量产÷原型成本、白痴指数、爬坡现金缺口 | 按原型成本报价 |
| 服务/咨询 | 人效、标准化比例、客户集中度 | 单客户 > 40% |

## 47 本书怎么用

不是读完，是按处境取一条。索引见 [book-map.md](skills/founder-guide/references/book-map.md)。

说明：`books_index.json` 按 **47 条书目条目**索引，其中 30 与 39 均为《活法》（中文版与英文版），因此 47 份成书对应 **46 本原书**。下文说“47 本”指成书份数。

| 处境 | 取哪几本 |
|---|---|
| 不确定要不要做 | 02 低风险创业、15 从0到1、18 穷查理宝典 |
| 做不出东西 | 47 埃隆之书（原型先行、工程学五步法） |
| 卖不动 | 26 影响力、25 世界上最伟大的推销员 |
| 交付失控、成本高 | 47 埃隆之书（工厂即产品、白痴指数、瓶颈） |
| 团队不出活 | 47 埃隆之书（特种部队、面试法）、16 原则 |
| 现金紧 | 05 创业维艰、17 一本书读懂财报 |
| 战略与对手 | 35 毛泽东选集、15 从0到1 |

规矩：一次一本一条，取完必须落成一个动作。整本读完是读书，不是判断。

## 覆盖的 9 个维度（蒸馏自 47 本书）

| 维度 | 代表书 | 提炼的方法论 |
|---|---|---|
| 创业 | 小米创业思考、低风险创业、创业36条军规、创业维艰、种下股权的苹果树、埃隆之书 | 低成本试错、从 0 到 1 打法、融资节奏、股权设计、第一性原理 |
| 行动力 | 埃隆之书 | 工程学五步法、白痴指数、时间成本核算、工厂即产品、极简组织 |
| 财商 | 富爸爸穷爸爸、小狗钱钱、百万富翁快车道 | 资产 vs 负债、被动收入、快车道思维 |
| 经济 | 经济学原理、小岛经济学、金融的本质、逃不开的经济周期、薛兆丰经济学讲义 | 供需、货币本质、经济周期规律 |
| 商业思维 | 从 0 到 1、原则、一本书读懂财报、穷查理宝典、基业长青、企业市场法律 | 垄断式创新、原则化决策、多元思维模型、长期主义、法律红线 |
| 投资 | 纳瓦尔宝典、投资中最简单的事、指数基金投资指南、漫步华尔街 | 复利、指数定投、均值回归 |
| 营销 | 世界上最伟大的推销员、影响力 | 影响力六原理、成交心态 |
| 职场 | 向前一步、心、干法、活法 | 职场突破、利他之心、精进工作法 |
| 个人成长 / 心态 | 微习惯、人生由我、认知觉醒、素书、毛泽东选集、被讨厌的勇气、活出生命的意义、为何家会伤人、曾奇峰的心理课、谁动了我的奶酪 | 微习惯、认知升级、课题分离、意义疗法、家庭心理、应对变化 |

## 蒸馏流水线（第二用法）

1. **解析源书为全文**：PDF 走 `pdftotext`，飞书/豆包文档走 `lark-cli docs +fetch`，落盘为 `full_text.txt`
2. **初始化工作目录**：`make_workspace.py` 生成四件套（checklist / outline / ledger / manuscript）
3. **规划**：定核心主张、章节结构、每章核心问题与目标字数，全书目标字数精确分配到章
4. **逐章成稿**：每章独立成稿，忠实转述，保留关键原句、角色与专有名词，去 AI 腔
5. **合并 + 校验**：合并 `final.md`，跑 `distill_check.py`，任何一项不达标不放行
6. **交付**：markdown + 原书 PDF；需要时上传云盘

蒸馏校验门槛（写死在脚本里）：

- 非空白字数 ∈ 目标 ±10%（默认目标 31,040 字，可调）
- 章节数 ≥ 8 且编号从第一章起连续
- 章标题为 `# 第X章`（汉字数字）
- 无占位符（TODO / 待补 / 占位 / 待定 / xxx）
- 中文占比 ≥ 70%；每章非空白字符 ≥ 500
- 层级规范（“一、” → “（一）”），不跳级
- 章节目标字数合计 = 全书目标字数，台账已回填且章节齐全

## 常见问题

**Q：免费版和付费版功能有区别吗？**
A：没有。GitHub 上的源码、模板、案例、文档与付费交付内容一致，免费版功能完整。付费买的是商业授权、作者后期制作的中文安装使用教程，以及订单页约定范围内的版本更新/答疑。

**Q：个人接私活、做自己的小生意，算商业使用吗？**
A：算。只要使用与收入有关，就需要个人商业使用授权。纯学习、研究、非商业试验不需要。

**Q：买了授权能不能转卖或分享给朋友？**
A：不能。授权仅限被授权人本人在其经营项目中使用，不可转售、分销、转授权或多人共享。

**Q：团队/企业商业使用能不能用？**
A：需另行书面授权。在 GitHub 开 Issue 说明人数、主体、场景和交付形式，作者确认范围与价格后签发。非商业组织内部使用仍可按 PolyForm Noncommercial 1.0.0 免费使用。

**Q：这和让 AI 总结一本书有什么区别？**
A：总结产出观点，这里产出结论和动作。判断过程强制要求替代方案成本、付费证据、盈亏平衡量、runway 四个数，缺一个就不给方向结论。

**Q：它会不会顺着我说好话？**
A：设计上不允许。SKILL.md 自检里明确：结论只能是“做/小步验证/停”，出现“值得关注”“可以尝试”这类中间态就重写；用户明显在自我说服时要直接指出证据不够。

**Q：我没有项目，只是想学创业，能用吗？**
A：能。跑 `python3 skills/founder-guide/scripts/diagnose.py --interactive` 答 15 题，它告诉你处在哪个阶段、这一周只该做哪三件。

**Q：会不会编造原书没有的内容？**
A：规则上禁止虚构。成书要求忠实转述原书，保留关键原句、案例与专有名词；无源书材料时直接停止，不生成。校验脚本会拦截占位符与空章节。

**Q：蒸馏出来的书能商用吗？**
A：不能直接商用分发。成书是原书内容的浓缩转述，版权归原作者与出版方。购买 Skill 商业授权不等于获得原书或衍生内容的商业传播权；公开传播或商业发行需自行取得原书权利人的授权。

**Q：发现有人倒卖怎么办？**
A：先保存证据，再按 [侵权对比清单](docs/infringement-checklist.md) 和 [平台投诉模板](docs/takedown-templates.md) 处理。投诉是否成立由平台或相关机构依据证据判断。

**Q：公开源码能防止别人复制吗？**
A：不能。许可证明确授权边界、提供投诉依据，但从技术上无法阻止复制。真正降低风险靠版本记录、授权编号溯源、软著登记与平台投诉。

**Q：需要联网或付费 API 吗？**
A：不需要。脚本只用 Python 3 标准库；解析 PDF 需要本机有 `pdftotext`，处理飞书文档需要 `lark-cli`。

**Q：一次能蒸馏一份书单吗？**
A：能。按 `NN-书名` 自动编号，逐本产出，互不覆盖，适合几十本的批量作业。

**Q：支持英文书吗？**
A：支持英文源书，但成书输出为中文（中文占比 ≥70% 是硬门槛）。

**Q：可以只用它的校验脚本或速算器吗？**
A：可以。`skills/founder-guide/scripts/` 下每个脚本都能独立运行，传入参数即可。

## 许可与商业授权

### 免费与授权速览（先看这一段）

| 你想做什么 | 是否免费 | 说明 |
|---|---|---|
| 个人学习、研究、试验 | 免费 | 按 [PolyForm Noncommercial 1.0.0](LICENSE) 使用 |
| 非商业读书会、学校/公益机构内部使用 | 免费 | 不收费、不导流卖课 |
| 在自己的经营项目中使用 | 需商业授权 | 购买**个人商业使用授权** |
| 团队/企业商业使用、商业产品集成 | 需另行书面授权 | 在 GitHub 开 Issue 说明场景 |
| 转售、分销、打包收费、付费课程/社群/代做 | 禁止 | 未经授权属于违约/侵权 |

- **源码始终公开**：GitHub 上的代码、模板、案例、文档与付费交付内容一致，不存在“付费才解锁源码”。
- **付费买什么**：个人商业使用授权 + 作者后期制作的中文安装与使用教程（以商品页说明为准）+ 按订单页说明提供的版本更新/答疑。
- **官方购买/申请**：[GitHub Issue · 商业授权申请](https://github.com/GodMaking/founder-guide-skill/issues/new?template=commercial-license.yml)
- **禁止未经授权倒卖**：详见 [商业授权说明](COMMERCIAL-LICENSE.md)。
- **正版核验**：[GitHub Issue · 授权核验](https://github.com/GodMaking/founder-guide-skill/issues/new?template=license-verification.yml)；编号是溯源依据，不是技术锁。

> 本仓库不包含任何受版权保护书籍的正文或成书全文。蒸馏成书是原书内容的浓缩转述，原书著作权归原作者与出版方；购买 Skill 商业授权不等于获得原书或衍生内容的公开传播权/出版权。

本仓库采用 **PolyForm Noncommercial License 1.0.0**：

- **免费**：个人学习与研究、非商业读书会、学校与公益机构内部使用
- **需授权**：出售（无论是 Skill 还是它的产出）、付费课程/社群、收费代做、打包进付费产品、企业内部商用培训、转售与分销
- **商业授权类型**：默认是个人商业使用授权；团队/企业商业使用、商业产品集成、白标分销需另签书面协议
- **付费交付**：商业授权书 + 唯一授权编号 + 作者后期制作的中文安装使用教程 + 订单页约定范围内的版本更新/答疑
- **不包含**：独家源码、隐藏功能、原书版权、转售权、子授权、收益承诺

条款全文见 [LICENSE](LICENSE)，商业授权范围、申请方式、禁止行为与维权路径见 [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)。

一句话：**可以免费用，不能拿去卖；要用于自己的经营项目，先取得书面商业授权。**

### 一客一码（卖出每一份都带唯一编号）

`skills/founder-guide/scripts/issue_license.py` 为每个买家生成唯一授权编号、个人商业使用授权书与交付物版权页，并记入本地台账；台账只存本地、不入库。

```bash
# 预生成 50 个编号，用于闲鱼自动发货
python3 skills/founder-guide/scripts/issue_license.py --gen-codes 50 --output ./licenses

# 用预生成编号签发个人商业使用授权书
python3 skills/founder-guide/scripts/issue_license.py --buyer "闲鱼昵称" --order "订单号" \
    --code FG-20261113-XXXXXXXX --product skill --output ./licenses

# 为指定成书签发授权，并把版权页写进成书末尾（附零宽水印）
python3 skills/founder-guide/scripts/issue_license.py --buyer "闲鱼昵称" --order "订单号" \
    --product books --books "01,47" --embed deliverables/final.md --output ./licenses

# 拿到疑似盗版文件，反查它出自哪一份授权
python3 skills/founder-guide/scripts/issue_license.py --decode 疑似盗版.md

# 校验授权书是否被改动（摘要匹配，不是数字签名）
python3 skills/founder-guide/scripts/issue_license.py --verify licenses/授权书-FG-....md
```

编号形如 `FG-20261113-2TD8U5TY`，与本地台账一一对应。编号中的日期是取号日期，不是授权日期。

需要说明的是：公开仓库的协议**无法在技术上阻止盗卖**，它的作用是明确授权边界、让平台投诉与维权有依据；真正降低风险靠一客一码溯源、软著登记与平台知识产权投诉。

## 版权与维权

- **版本记录**：[CHANGELOG.md](CHANGELOG.md) + Git 提交历史
- **权属证据整理方法**：[docs/copyright-evidence.md](docs/copyright-evidence.md)
- **侵权对比证据清单**：[docs/infringement-checklist.md](docs/infringement-checklist.md)
- **平台投诉材料模板**：[docs/takedown-templates.md](docs/takedown-templates.md)
- **版权声明**：[NOTICE](NOTICE) + [LICENSE](LICENSE) 中的 `Required Notice`

边界说明：

- 公开源码不能在技术上完全阻止复制
- 投诉是否成立，由平台或相关机构依据证据判断
- 不声称“只要使用相同的创业方法论、写了类似 Skill，就一定侵权”
- 著作权保护具体表达，不保护思想、方法、概念本身
- 其他开发者独立开发类似功能，且没有复制本仓库的代码、文案、结构或素材，不构成侵权
- 发现侵权时，先固定证据，再判断是否属于非商业许可允许的行为，最后按平台流程投诉

## 仓库结构

```text
founder-guide-skill/
├── README.md
├── LICENSE                     # PolyForm Noncommercial 1.0.0（非商业免费，商用需授权）
├── NOTICE                      # 版权声明与 Required Notice
├── COMMERCIAL-LICENSE.md       # 商业授权范围、付费交付、禁止倒卖与维权路径
├── CHANGELOG.md                # 版本记录
├── llms.txt                    # 给 AI 引擎读取的仓库摘要（GEO）
├── docs/
│   ├── copyright-evidence.md   # 权属证据整理方法
│   ├── infringement-checklist.md  # 侵权对比证据清单
│   ├── takedown-templates.md   # 闲鱼/平台投诉材料模板
│   └── github-settings.md      # GitHub About、Topics 与展示文案建议
├── delivery/
│   ├── README.md               # 闲鱼自动发货与交付方案
│   ├── auto-delivery-message.md   # 自动发货文案模板
│   └── buyer-tutorial-outline.md  # 中文安装使用教程大纲（作者后期制作）
├── .github/ISSUE_TEMPLATE/
│   ├── config.yml              # Issue 模板入口配置
│   ├── commercial-license.yml  # 商业授权申请
│   ├── license-verification.yml   # 授权核验
│   └── infringement-report.yml    # 侵权举报
└── skills/
    └── founder-guide/
        ├── SKILL.md            # 主入口：三种用法、判断流程、输出规范、自检
        ├── agents/openai.yaml
        ├── references/
        │   ├── judgment-framework.md     # 五问、六阶段、四闸门、复盘、边界
        │   ├── execution-playbook.md     # S0–S5 动作清单与常见死法
        │   ├── business-models.md        # 五类生意的必算数与一票否决线
        │   ├── interview-and-offer.md    # 十问脚本、报价单、异议应对、30 天日历
        │   ├── book-map.md               # 47 本书按处境索引
        │   └── distill-workflow.md       # 逐章写作细则与去 AI 味规范
        ├── scripts/
        │   ├── profile.py                # 创业档案：建档、填数、检查、记账
        │   ├── startup_calc.py           # 闸门速算：value/unit/idiot/gap/runway
        │   ├── diagnose.py               # 15 题阶段自测
        │   ├── make_workspace.py         # 初始化四件套工作目录
        │   ├── distill_check.py          # 独立校验（纯标准库）
        │   └── issue_license.py          # 一客一码：授权编号、授权书、版权页、溯源
        └── assets/
            ├── templates/                # 四件套模板 + 决策卡模板
            └── samples/
                ├── books_index.json      # 47 条书目索引（46 本原书）
                ├── SAMPLE-FORMAT.md      # 成书结构范式（不含原文）
                ├── decision-card-example.md  # 示范决策卡（数字为虚拟）
                └── case-book.md          # 三段完整判断案例（内容付费/门店/软件）
```

## 版本

见 [CHANGELOG.md](CHANGELOG.md)。仓库持续公开更新；付费用户的版本更新范围以订单页说明为准。

## 边界（不做什么）

- 不做收益承诺、不给投资建议，不做法律与税务结论
- 行业技术、资质、法律结论这类书库没有的，直接说“没有”，不硬套
- 不替用户做“押上家庭资产”这类不可逆决定，只给风险清单
- 没有真实源书内容时不生成成书，不猜、不编
- 不做原创书籍创作（走 ai-novel-production）、Word 排版（走 word）、在线长文档协同（走 lark-doc）
- 不承诺安装成功率、创业成功率或盈利
- 不声称购买 Skill 商业授权就获得原书版权

## 反馈与举报

- Bug、功能建议：开 GitHub Issue
- 商业授权：[商业授权申请](https://github.com/GodMaking/founder-guide-skill/issues/new?template=commercial-license.yml)
- 授权核验：[授权核验](https://github.com/GodMaking/founder-guide-skill/issues/new?template=license-verification.yml)
- 侵权举报：[侵权举报](https://github.com/GodMaking/founder-guide-skill/issues/new?template=infringement-report.yml)
- 举报时请提供具体链接与证据，不要在公开 Issue 中填写个人敏感信息
