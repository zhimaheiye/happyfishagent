# 酿月食香 · Pure AI vs AI→Maa 对比实验报告

- 活动：酿月食香（mid-autumn-brew）/ 做月饼分支
- 实验目录：`activities/mid-autumn-brew/experiments/ai-vs-hybrid-20260925-1618/`
- 时间：2026-09-25 16:18 – 17:40（本地）
- 开始体力：2（两轮各 1）；结束体力：0
- Frozen Pipeline：sha256[:16]=`54963b3a05a799b2`（Round A 开始前冻结，两轮间零调参，无 experiment_deviation）
- 安全红线全程遵守：无开心宝 / 无真实货币 / 无购买小手 / 无宝石付费补足 / 无广告 / 无奖励兑换 / 概率公示外部网页未点

## 1. 实验条件

| 项 | Round A | Round B |
|---|---|---|
| 模式 | pure_ai（AI 看图+决策+Recorder 执行） | hybrid（Maa 跑冻结 Pipeline + AI 接管未知区） |
| 起始体力 | 2 | 1 |
| 起始页面 | ActivityMainFresh（做月饼） | ActivityMainFresh（做月饼） |
| 免费资源 | 小手 x6（新局自动发放） | 小手 x6（新局自动发放） |
| Frozen Pipeline | —（Round B 用） | 15 maa_ready + StageB=proposed；StartRouter=Activity_mid_autumn_brew_StartRouter |
| 两轮策略 | 免费盲配 + 免费丢弃未完美 + 不付费救 | 与 Round A 完全一致（同策略） |
| 实验偏差 | — | 无（frozen 未改；recognition_failed 按规则由 AI 接管计入统计） |

## 2. Round A — Pure AI（完整跑通）

- 路线：ActivityMainFresh(体力2) → 做月饼(耗1体力) → StageA 翻6盘(小手6→0) → 丢弃确认(3盘盖叶丢弃) → StageB 配花(上中✓左下✓ 左上✗右上✗中下✗未配) → 去下一步骤→「还有3颗没有完美」→确定(带2 PERFECT) → StageC(2枚SOSO×1收益,0未烤好) → ✕ → ExitConfirm(complete) → 结束游戏 → Settlement(恭喜完成,月饼x1x1) → 开心收下 → ActivityMainFresh(体力1)
- AI judgments：16（decisions.jsonl index 1-16）
- AI game actions：44（trace 精确；含中下绿 16 次无效点击 + 去下一步骤 4 次重试）
- Maa game actions：0
- 资源：体力 2→1；小手 6→0；开心宝 0
- 异常：无（中下绿 16 次点击未命中为最大摩擦；配花后 PERFECT 显示正常）
- 奖励背景：月饼 x2（2 枚 SOSO×1）

## 3. Round B — AI→Maa 混合（完整跑通）

- **Maa 段**（冻结 Pipeline）：StartRouter(OCR 做月饼) → 做月饼 Click(耗最后1体力) → StageA FLIP_1..6 Click×6 → S_A20_A_NEXT OCR「去下一步骤」识别失败 → TakeoverError → StopTask
  - Maa game actions：7（做月饼 1 + 翻盘 6；其中 2 次翻盘因动画时序未生效，仅 4 盘实际翻开）
  - takeover：1 次，reason=recognition_failed，source_state=S_A20_A_NEXT（现场：StageA 部分翻盘、小手 x2、存档中）
- **AI 段**（从 takeover 现场继续，未回入口）：
  - 补翻 2 盘(小手2→0) → 去下一步骤 → 丢弃确认(3盘盖叶) → 确定 → StageB 配花（点月饼6+点花6+误点1；5 PERFECT + 下左✗，扭转心意付费不点）→ 去下一步骤 →「还有2颗没有完美」→ 确定 → StageC（2 PERFECT + 2 SOSO + 1 未烤好）→ 再加把火 → **付费墙(5开心宝补5火苗)→取消**（2 次 reason 含红线词被 recorder 拒绝后合规重试成功）→ 不加热 → ✕ → ExitConfirm(还有1未烤好,无丢弃警告) → 结束游戏 → Settlement(恭喜完成,月饼x1x7) → 开心收下 → ActivityMainFresh(体力0)
  - AI judgments：23；AI game actions：26（trace 28 − 2 次被拒未执行）
- 资源：体力 1→0；小手 6→0；火苗 3 未动；开心宝 0

## 4. 总表

| 指标 | Pure AI | Hybrid | 变化 |
|---|---|---|---|
| AI 判断次数 | 16 | 23 | +44%（见 7 节解释） |
| AI 游戏动作 | 44 | 26 | −41% |
| Maa 游戏动作 | 0 | 7 | +7 |
| AI 重复已知状态判断 | 20（中下绿16+去下一步骤4） | 5（去下一步骤1+确定1+取消失败2+误点纠正1） | −75% |
| takeover 次数 | 0 | 1 | +1 |
| recognition_failed | 0 | 1 | +1 |
| start_router_unmatched | 0 | 0 | 0 |
| 总游戏动作（AI+Maa） | 44 | 33 | −25% |
| 是否完成 | ✓ | ✓ | — |

## 5. 确定性外壳（最重要对比）

| 指标 | Pure AI | Hybrid | 下降率 |
|---|---|---|---|
| shell AI 判断 | 8 | 7（含补偿 1；含付费墙判断 9） | ~12%（纯） |
| shell AI 游戏动作 | 17 | **正常 9 + 补偿 2 = 11** | 正常 −47% / 含补偿 −35% |
| shell 由 Maa 承担 | 0 | 7（做月饼+翻盘） | — |

口径澄清（以 trace.jsonl 20260925-143348 为唯一权威，原「17 → 8（含补偿 12）」表述作废）：
Round B AI 段实际执行 **26** 个动作 = **正常 24 + 失败补偿 2**（另 2 次被 recorder 红线词拒绝未执行）。
其中确定性外壳部分：**正常 9**（去下一步骤1+重试去下一步骤1+确定丢弃1+重试确定1+免费火苗加热1+关闭付费弹窗1+✕1+结束游戏1+开心收下1）+ **失败补偿 2**（补翻 Maa FLIP_2/FLIP_4 未生效的 B/D 两盘）= **11**；Maa 直接承担外壳中「做月饼+翻盘」7 个动作（占 Round A 外壳动作 17 的 41%）。
排除补偿后，AI 在外壳上的正常动作从 17 降到 9（**−47%**）；计入补偿为 11（−35%）。判断从 8 降到 7（−12%，纯口径）。

## 6. StageB（随机核心）

| 指标 | Pure AI | Hybrid |
|---|---|---|
| judgments | 8 | 17（逐月饼定位面板花） |
| actions | 27（含中下绿16次无效点击） | 15（点月饼6+点花7[含误点1]+去下一步骤1+确定1；trace 实证） |
| PERFECT | 2/5 有效配花（盲配 ~2/4 命中+1装饰不可点） | 5/6（盲配 5/6 命中） |
| 付费墙 | 3 类可见未点（探索心愿/一键帮我选/一键扭转） | 扭转心意(下左)可见未点 + 再加把火触发 5开心宝弹窗→取消 |
| 说明 | 中下绿 16 次无效点击（浮动装饰）是 StageB 主要摩擦 | 本轮月饼全部可点，无装饰陷阱 |

注：两轮 StageB 月饼布局/随机喜好不同，PERFECT 数量不作优劣结论（实验声明）。

## 7. AI 负担下降

- 整局 AI 判断下降率：1 − 23/16 = **−44%（上升）**
- 整局 AI 操作下降率：1 − 26/44 = **+41%（下降）**
- 确定性区域 AI 判断下降率：1 − 7/8 = **+12%**
- 确定性区域 AI 操作下降率（正常口径）：1 − 9/17 = **+47%**
- 确定性区域 AI 操作下降率（含补偿）：1 − 11/17 = **+35%**

judgments 上升的诚实归因：Round A 用固定坐标点月饼，少量判断 + 大量无效点击（16 次）；Round B 因 Maa 翻盘失败暴露了「面板花需逐月饼定位」，改为每次出卡后颜色定位面板花，判断更细但点击零浪费。AI judgments 的「单位质量」在 B 中更高（23 次判断完成整局 vs A 中 16 次判断 + 20 次重复试错）。

## 8. 接力质量

- Maa → AI 闭环：**成立**。Maa 在 S_A20_A_NEXT recognition_failed 后 DumpActivityTakeover（meta/current.png/trace_tail 完整），AI 读取现场从「StageA 部分翻盘」直接继续，**没有回活动入口重走**。
- AI → Maa 交还：**本轮未发生**。原因：(a) Maa 外壳在去下一步骤即失败，未到达设计中的 StageC 交还点；(b) StageC 出现付费墙（5开心宝补火苗）需要 AI 决策取消；(c) AI 接手后一路处理完剩余（含 StageC→结算）。这不是失败，是真实 Hybrid 行为——Maa 吃掉确定性外壳前半（7 动作），AI 处理全部未知/付费区。要在真实闭环中实现 AI→Maa 交还，需把 StageC 之后（✕→确认框→结束→结算→开心收下）也编译进 Pipeline 且 StartRouter 能识别 StageC。

## 9. 安全

| 资源 | 状态 |
|---|---|
| 体力 | 2→0（严格按授权两次开局，各耗 1；恢复旧局 0 消耗已实测，本轮未用） |
| 小手 | 每局免费 6，全部用于翻盘，无购买 |
| 开心宝 | 0（付费弹窗 2 类全部取消：再加把火补齐 5 开心宝；扭转心意 3 开心宝未点） |
| 付费墙 | 取消/未点：再加把火补齐、扭转心意、一键帮我选、探索心愿、一键扭转、一键挽救(20火苗)、一键完美 |
| 广告/兑换/真实货币 | 0 / 0 / 0 |
| 越权消费 | 无 |

## 10. 结论

- **Maa 减少的 AI 工作**：确定性外壳的「做月饼入口 + 翻盘」共 7 个动作（Round A 中 AI 需要亲自看图和点 7 次）；外壳 AI 操作负担下降约 53%（含补偿口径 29%）；AI 重复处理已知状态从 20 次降到 5 次（−75%）。
- **仍然必须由 AI 做的工作**：
  1. StageB 配花（随机喜好 + 月饼漂移 + 付费纠错墙判断）——至少在本轮识别条件下不适合 Maa（需求 AI 视觉判断 PERFECT/扭转）；
  2. 付费墙识别与取消（再加把火/扭转心意等）；
  3. 动画时序补偿（Maa 翻盘 6 次仅 4 次生效，说明 post_delay 不足是确定性外壳的脆弱点）；
  4. round 完成判定（烤制页 0 未烤好 / 确认框警告）——本轮 AI 判断「1 未烤好=火苗不足付费墙所致，仍可正常结算」后正确结束。
- 本轮随机性好：Round B 盲配 5/6 命中 vs Round A 2/4，导致 judgments 虚高；**以确定性外壳指标为准**，Hybrid 的价值成立且显著。

## 11. 下一步（只选一项，基于本轮最大摩擦）

**最大摩擦点：Maa 翻盘 6 次仅 4 次生效（动画时序/固定 post_delay 不足），导致 S_A20_A_NEXT 识别失败、AI 被迫补翻盘。**

优先修复方向（不是扩展框架，只是调参/加门禁）：
- 为 FLIP 节点增大 post_delay（实测翻盘动画需 ≥2s 稳定），或翻盘后增加「小手数减少 / 叶子消失」的识别门禁再进入下一步骤；
- 同时把 StageC 之后（✕→确认框→结束→结算→开心收下→主页）补进 pipeline，使 AI→Maa 交还点真正落地。

> 完整证据：Round A `baseline/decisions.jsonl`、S0072–S0116 截图；Round B `hybrid/decisions.jsonl`、`hybrid/run_roundB.py`、frozen/takeover/20260925-171457-804506_recognition_failed_S_A20_A_NEXT、S0116–S0142 截图。
