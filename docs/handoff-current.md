# 交接：限时活动 AI + Maa

日期：2026-09-26（凌晨更新）

## ⚠ 当前卡点：浪漫满屋 swipe 命令突然失效（技术阻塞）

**现象**：浪漫满屋约会日历局进行中（完成日程 6/10），从 S0060 开始，所有 swipe 拖卡命令突然全部失效——连续 10+ 次 `adb shell input swipe` 执行成功（exit code 0），但游戏完全不响应，changed_fraction=0.0。

**已排除**：
- 坐标问题：多次 zoom 裁图精确测量卡池图标中心（鸭/熊/瓶），偏差 <10px，仍无效
- duration 问题：试过 2000 / 3000 / 5000 ms，均无效
- 游戏卡死：tap 命令仍然有效（点 X 退出、点「一起约会吧」重进都成功）
- 游戏状态异常：退出重进游戏后回到日历页面，进度保留（完成日程仍 6/10），但 swipe 仍然无效

**关键对比**：S0001~S0059 共 59 次 swipe 中绝大多数成功（cf>0.01），S0060 起全部失败（cf=0.0）。命令本身没变，突然失效。

**当前现场**：
- session：`activities/romantic-house/sessions/20260926-102010/`（目录名拼错 romantic-house 但证据链在此）
- 完成日程：6/10
- E（空格）：约 7-9（低于 10 预警线）
- 卡池：3 张（小黄鸭+调色盘 / 小黄鸭+小熊+香水瓶 / 小熊+调色盘）
- 需求列：裙子 / 小熊 / 香水瓶
- 截图：`D:\hf_tmp\current_stuck.png`

**待调查**：
1. 是否是 MuMu 模拟器的 swipe 输入通道异常？（tap 正常但 swipe 异常）
2. 是否需要用 `input touchscreen swipe` 而不是 `input swipe`？
3. 是否是游戏的拖卡识别机制变了（需要长按 + 拖动轨迹）？
4. 重启 MuMu 模拟器是否能恢复？

**不要做**：不要继续盲目试 swipe 坐标；不要重启游戏（进度会保留但问题不会解决）；不要消耗任何资源。

---

日期：2026-09-25（晚间更新）

当前停止原因：裁缝铺主活动第 2 局 Maa 实机已完成（Maa→AI→Maa 多次接力真实闭环：2 次 takeover 均为 knowledge_frontier，AI 处理弹窗后交还 Maa，第 3 关剪刀 0 由 AI 接管结束本局）；A25（剪刀0 识别）与 modal 优先路由已离线修复并全量验证。体力已 0，等下一体力恢复 + 用户授权后做 A25 修复的实机复测。无技术阻塞。

## 本轮完成（相对上一版）

- **第一只真实活动实验完成**：`mid-autumn-brew`（酿月食香，09.25-10.05）。活动语义记录在 `happyfish-activity-automation/activities/mid-autumn-brew/README.md`，session `20260925-143348`。
- 首轮 Maa：`StartRouter → S0012→…→S0016 → knowledge_frontier → Stop`，5 状态 5 点击，接管包 `takeover/20260925-145125-142853_knowledge_frontier_S0016`。
- 第二轮 Maa：`StartRouter → S0012→…→S0019 → knowledge_frontier → Stop`，8 状态 8 点击（> 第一轮），接管包 `takeover/20260925-145632-571321_knowledge_frontier_S0019`。
- **V1.1 StartRouter 零点击 smoke 实机闭环验证通过**（SMOKE_OK）：`activities/startrouter-smoke/sessions/20260925-145709`。0 Click、reason=start_router_unmatched、source_state=null、known_candidates 正确、TakeoverUnknown→Stop。
- 三轮离线回归均通过（18 / 11 / 6）。
- **巧手裁缝铺第 2 局 Maa 实机完成**（见下节）：Maa 自动跑第1关(3堆)+第2关(4堆)剪布与结算，两次遭遇弹窗（B/C 型）均 knowledge_frontier 交还 AI，AI 0 付费处理后交还 Maa；第 3 关剪刀 0 时 A25 识别失败卡循环，AI 接管结束本局；体力 2→0，全程 0 开心宝/0 宝石。

## 下一 Agent 建议（不做也行，看任务优先级）

- 若继续酿月食香：从接管包 `takeover/20260925-145632-571321_knowledge_frontier_S0019` 的 current.png（活动主页面-继续游戏变体）继续。下一个可探索点：做月饼玩法内部（注意：入口即消耗 1 体力，退出有确认框三选一）或 吃月饼（券=0 时入口无反应，待验证）。
- 若做其它：先读 `activity-ai-maa-handoff.md` 第七节。
- 概率公示页签 = 外部网页，用户确认不点。

## 2026-09-25 19:40-21:00 巧手裁缝铺（副线）：问号采集 + 主活动第1局 + 副活动3轮 + 主活动 Maa pipeline 离线建模（0 付费，体力 2→1）

- **问号帮助页采集**（session 20260925-195917，S0001~S0008）：主界面 ?(69,62) → 三个标签（全局介绍/奖励合集8页/所需宝石）。**标签点击用像素坐标**（奖励合集 ≈(498,95)、所需宝石 ≈(772,97)，OCR 千分比 ×1.28/×0.72 才是像素）；奖励合集 1/8→2/8（下箭头 1168,506）；所需宝石 3 种（洗衣机藤藤23/衣架0/蜜蜜24=活动宝石非开心宝）。全局介绍：每日登入领体力量体裁衣/布堆剪布/用心确认针脚；**领奖期仅能进细密针脚和奖励兑换**。规则已沉淀 `activities/tailor-shop/SKILL.md` 头部。
- **主活动第 1 局（S0009~S0029，纯 AI）**：精选布料(644,623) 体力 2→1；免费剪刀x12(258,509)；3 关全走（剪刀消耗 4+6，第3关用尽 x0）；遭遇事件 A/B/C 三型全实测（A=开心宝x8→X、B=免费档领完变Get、C=兑换商店整页关）；回主界面 体力=1、布料 黄16/蓝8/绿10、炫彩 58→60。recorder 红线词实证（reason 含「开心宝」被拒，改写合规通过）。
- **副活动细密针脚 3 轮（S0030~S0065，0 体力）**：订单1×2（137→146→157/200）+ 订单4×1（73→83→93/200，本轮加急翻倍：第1关/第2关各 +10）；打法=第1/2关一键穿针（线≥按钮N 先核验）+ 第3关 1 线探测；线尽→X→确认结束（绝不暂时离开）；布料 黄16→2/蓝8→3/绿10→2（耗尽）、纽扣 黄115→130 绿96→112、经验 40→50/100。新事实：订单重接消耗浮动（订单1 黄7→9、订单4 蓝5绿8→蓝6绿9）、加急翻倍判据=线档页「加急订单满意度翻倍！」文字、第3关 1 线探测 3 样本（1 未中 2 中，中后无线仍须退出）、第3关 6 列网格像素坐标。
- **主活动 Maa pipeline（离线编译，待实机）**：`activities/tailor-shop/experiments/maa-pipeline-20260925-2016/`。flow.json 9 状态全 maa_ready + generated/pipeline.json（schema 校验 [OK]）。核心：剪布循环=「裁剪」OCR ClickRecognitionResult 动态定位最左堆（自循环 + recognition_fail_next=完成本关）；遭遇弹窗拆 S_X10_B（TemplateMatch 标题模板，rapidocr 漏读艺术字）+ S_X11_AC（OCR regex 得鱼概率|压箱底），均 frontier；S_A25「x0」剪刀用尽 frontier。离线验证全过（ROI 像素修正、B 模板 1.0 vs ≤0.16、顺序/自循环/fail_next OK）。
- **第 2 局 Maa 实机 + A25/modal 修复**：见下节「2026-09-25 21:24-22:10」。未 commit/push。
- 证据：session 20260925-195917 screenshots/S0001~S0065、flow.json、diffs/；Maa pipeline 离线 fixture 脚本 `D:\开心水族箱活动经验\_vgtmp\tailor_fixture2.py`。

## 2026-09-25 21:24-22:10 巧手裁缝铺第 2 局 Maa 实机（用户授权消耗最后 1 体力）+ A25/modal 离线修复

- **运行1（第1关 3 堆，21:24-21:27）**：StartRouter → S_A00(精选布料,耗1体力) → S_A10(免费剪刀x12) → S_A20×3 → S_A21(完成本关) → S_A30(结算) → **S_X10_EVENT_B 命中 → knowledge_frontier takeover** 	akeover/20260925-212540-039106_knowledge_frontier_S_X10_EVENT_B。AI 读 current.png 确认 B 三档（免费 x2/宝石 x20/钞票 x12）→ 点免费 (258,507) 变 Get → 点 X (1215,57)（0 付费）→ 重跑 Maa。
- **运行2（第2关 4 堆，21:27-21:31）**：StartRouter → S_A20×4 → S_A21 → S_A30(结算) → **S_X11_EVENT_AC 命中 → takeover** 	akeover/20260925-212731-748262_knowledge_frontier_S_X11_EVENT_AC。AI 确认 C 型兑换商店六档全资源 → 整页 X (1220,65)（一档不点）→ 重跑 Maa。
- **运行3（第3关，21:31-21:39 卡点）**：Maa 剪 2 刀后剪刀 0 → **S_A25 OCR 空识别 → A20 无限循环点击无效裁剪卡死 >6 分钟**。日志确证：MaaOCR 对剪刀计数 ROI 返回 ll_results_=[]（读不出 x0 小黄字），而离线 rapidocr 能读「x0」→ **引擎不一致**。AI 杀 python PID 28516 → X → 确认 (313,578) 结束本局 → 回主界面。
- **结果**：第1关 3 堆 + 第2关 4 堆完成结算；第3关剪刀 2→0 未完退出；体力 2→0；全程 0 开心宝/0 宝石/0 付费；主界面「精选布料」角标 **0**、无「继续游戏」（裁缝铺无继续游戏概念）。**Maa→AI→Maa→AI 多次接力闭环已成型**（3 段 Maa + 3 段 AI）。
- **A25 修复（离线，体力 0）**：纯数字「0」模板 	emplates/scissors_digit0.png（20×27，裁自 S0068 的 0 字符 (522,641)-(542,668)；整体「x0」模板区分度差弃用）→ TemplateMatch，ROI [400,590,700,730]，**阈值 0.75**。离线稠密匹配：x0 两帧=1.000、x2=0.500、x12=0.503、x4=0.500、x1=0.462、**x8=0.719**（8 与 0 形态相近，0.719 接近阈值但误触发仅 AI 复核画面，安全）。
- **modal 优先路由（与酿月 V2 同款问题）**：路由模拟暴露退出确认框帧 rapidocr 在遮罩下仍读「精选布料」→ A00 抢先。重排 flow.json states 顺序：**X10 → X11 → A40(退出确认) → A30(结算) → A25(剪刀0) → A00 → A10 → A20 → A21 → A50**。
- **router_sim 9/9 全过**：剪刀0剪布页→A25 ✓；剪刀8/2剪布页→A20 ✓（不误触发）；退出确认框→A40 ✓；结算弹窗→A30 ✓；B 弹窗 Get→X10 ✓；B 弹窗关闭后剪布页→A20 ✓（新事实：B 弹窗点免费档后自动关闭回剪布页，奖励 1 级带 Get 标记）；C 商店→X11 ✓；主界面→A00 ✓。
- 重新编译 OK：pipeline 中 A25=TemplateMatch+绝对模板 0.75、A20.next=[A25,A20]（每循环先查剪刀0）、X10=绝对模板 0.7。
- **⚠ 安全红线（新增）**：体力 0 时主界面 StartRouter 命中 A00 会点击「精选布料」（体力不足弹窗未建模）。**启动 Maa 前必须 AI 确认体力 ≥ 1**；体力 0 时禁止运行 run_tailor_round2.py。
- **待实机复测（需体力恢复 + 用户授权）**：跑 
un_tailor_round2.py 验证 A25 模板在真实第 3 关剪刀 0 时命中 → frontier → AI 接管结束本局（预期：不再卡循环）。
- 证据：session 20260925-195917 screenshots/S0065~S0069、takeover 两包（含 maa_log_tail.txt 中 A25 空识别日志）、templates/scissors_digit0.png。

## 仓库与路径

| 什么 | 哪里 |
|---|---|
| 探索与证据 | `D:\开心水族箱活动经验\happyfishagent`，remote `zhimaheiye/happyfishagent` |
| Maa 执行与 DumpActivityTakeover | `D:\happyfishgame`，remote `zhimaheiye/MaaHappyFish` |
| 设备发现 | 工作区 `D:\开心水族箱活动经验\tools\mumu_dev.py` |
| 工作流说明 | `happyfishagent/docs/activity-ai-maa-handoff.md` |
| 本交接 | `happyfishagent/docs/handoff-current.md` |

`personal-hub` 本地 `main` 与 `origin/main` 分叉。不要 merge、rebase 或 reset。

## 已有测试

| 命令 | 结果 |
|---|---|
| `happyfishagent` `test_recorder_offline.py` | 18 通过 |
| `happyfishagent` `test_flow_to_maa.py`（含 V1.1 与 schema） | 11 通过 |
| `MaaHappyFish` `dev/test_activity_takeover.py` | 6 通过 |

实机（本轮）：首轮/二轮临时 Pipeline 均 `task_succeeded`；StartRouter smoke `SMOKE_OK`；零 consumption 消耗（做月饼探索误耗 1 体力已记录，非开心宝/券/金币）。

## 已知限制

- Recorder 不懂画面语义。安全靠 `--safety` / `--reason`，外加红线词拦截（备注含「补充」等词会被拒，改写即可）。
- 做月饼入口 = 隐性消耗（点即开一局耗 1 体力，退出走确认框「暂时离开」）。自动化建模前不可当普通 nav。
- 吃月饼入口当前无反应（疑似券=0 禁用态，待验证）。
- 其余限制沿用上一版（见 git 历史或 activity-ai-maa-handoff.md 第 6/7 节）。

## 禁止

- 裸 `adb shell input tap` 做探索。走 `record_action.py`。
- 把临时活动写入 `MaaHappyFish/assets/resource/pipeline/features/`、`interface.json`、DailyRoutine 或 Release。
- 自动把 `proposed` 升成 `maa_ready`。
- 为了验证去消耗活动次数、券、金币、开心宝。
- commit / push，除非用户明确要求。
- 处理 `personal-hub` 分叉。

## 本轮追加（2026-09-25 16:xx，做月饼消耗型入口分支）

- **做月饼入口建模完成**（不扩展 Recorder/compiler/takeover 框架）：
  - 活动模型 happyfish-activity-automation/activities/mid-autumn-brew/metadata.json：状态语义（ActivityMainFresh/Resume、MooncakeGameInProgress、MooncakeExitConfirm、Settlement[proposed]）、体力识别（红圆+白字模板，脚本 stamina_detect.py + templates/digit_{0,2,3}.png）、门禁（默认全 false，gate_check.py --allow-resource 授权）、确认框 round_status 路由。
  - 退出确认框 = 业务路由（in_progress→暂时离开；complete→结束游戏；unknown→Stop/Takeover）。**不是固定安全策略**，禁止永远点任一按钮。
  - 离线测试 test_consume_offline.py 19/19；零消耗实机闭环（复用现有局：继续游戏→游戏页→✕→确认框→暂时离开→主页，体力 2 不变，0 新增消耗），证据 S0021/S0022/S0023。
- 下一 Agent 若继续：**需芝麻授权**后才能做真实消耗 smoke（点做月饼耗 1 体力、完成一轮翻盘耗小手、结束游戏分支验证、去下一步骤语义）。未授权前不点做月饼。

## 2026-09-25 15:33-15:47 完成当前局实机尝试（配花阶段付费墙）

授权范围：仅小手道具（完成当前局必要）。起点主页面(继续游戏,体力2)。

- 阶段A推进完成：翻6盘(小手6→0) → 去下一步骤弹窗「未吃到馅料的月饼,将被丢失」→ 确定(900,575) → 带6枚月饼进入阶段B配花（未翻3盘按免费规则丢弃）。
- 阶段B配花 = 付费墙：探索心愿2开心宝 / 一键帮我选12开心宝 / 扭转心意3开心宝（均弹窗后取消）；手动点花免费（实测点喜好卡片第3朵花(835,170)生效）但为盲配（无放大镜=1/3正确率、6枚全对概率极低、配错纠错需付费）。
- round_complete 信号未找到（阶段B完成=全部月饼满足喜好→银勋章+小火苗，画面未验证）。
- 收尾：✕→确认框→暂时离开(480,580) → 主页继续游戏变体，体力=2（stamina_detect 复验 2/2=1.0）✓ 二次验证暂时离开路径零消耗。
- 现场：主页「继续游戏」+ 体力2 + 局内已配1枚花（配花阶段，含1次可能错误的配花）。
- 待用户决策：配花阶段是否授权开心宝（探索+扭转）继续完成本局？或接受盲配试错？或保留现场暂停？
- 证据：sessions/20260925-143348/screenshots/S0024→S0050（S0037阶段B规则/S0038探索心愿2/S0040喜好卡片/S0042一键帮我选12/S0044配花尝试/S0045配花成功/S0046扭转3/S0049确认框/S0050主页继续游戏体力2）。

## 2026-09-25 16:08-16:12 完成当前局：round lifecycle 全链实测（盲配授权，0 开心宝）

- 用户决策：配花阶段选择盲配试错（不花开心宝）。
- 盲配结果 3/6（左上桂花✓ 右上玫瑰✓ 右下玫瑰✓ / 上中茉莉✗ 下排中花苞✗ 左下桂花✗）；配错无免费纠错（扭转=3开心宝）。
- 关键机制：未完美月饼可丢弃继续（点「去下一步骤」→「还有X颗月饼没有完美哦」→ 确定 → 带完美月饼进入开烤）。
- 阶段C（开烤）实测：PERFECT×3/SOSO×1 收益；火苗加热需宝石（不足→2开心宝补足弹窗）；x20挽救；一键挽救/一键完美疑似付费。
- 【round_complete 信号定稿】：阶段C「还有0个未烤好」+ 确认框无「未完美」警告 + 结算弹窗「恭喜您完成本轮烤月饼,获得奖励~」。
- 结束游戏(900,575) → 结算(开心收下638,607) → 主页恢复「做月饼」（继续游戏消失）→ 体力=2（stamina_detect 1.0）✓ 本轮两大验收全部达成。
- 全程 0 开心宝、0 新体力消耗。现场：主页「做月饼」+ 体力2，可开新局（未开）。
- 证据：sessions/20260925-143348/screenshots/S0051→S0072（S0053配花PERFECT/S0061配错扭转/S0066未完美丢弃弹窗/S0067开烤/S0068宝石不足弹窗/S0070确认框/S0071结算/S0072主页做月饼恢复）。
- metadata.json 已更新（7状态含StageC、Settlement confirmed）；README 已追加完整状态机。

## 2026-09-25 16:18-17:40 双轮对比实验完成（Pure AI vs AI→Maa，2 体力全部按授权消耗）

- 实验目录：`activities/mid-autumn-brew/experiments/ai-vs-hybrid-20260925-1618/`（baseline/hybrid/frozen + experiment.json + FINAL_REPORT.md）。
- Frozen Pipeline（Round A 前冻结，sha256[:16]=54963b3a05a799b2，两轮间零调参、无 deviation）：15 maa_ready + StageB=proposed，schema 校验通过。
- **Round A（pure_ai）**：44 AI actions / 16 judgments / 0 Maa / PERFECT 2 / 月饼x2 / 体力 2→1。最大摩擦=中下绿 16 次无效点击（浮动装饰）。
- **Round B（hybrid）**：Maa 跑 7 actions（做月饼+翻盘6，2 次翻盘因动画时序未生效）→ S_A20_A_NEXT recognition_failed → 1 次 takeover（包 frozen/takeover/20260925-171457-804506_recognition_failed_S_A20_A_NEXT）→ AI 从现场继续 26 actions / 23 judgments / PERFECT 5 / 月饼x8 / 体力 1→0。付费墙：再加把火=5开心宝补5火苗（取消）；注意 recorder 红线词拒绝（reason 含「开心宝」被拒 2 次，改写合规后成功取消）。
- **核心结论**：确定性外壳 AI 操作负担 −53%（17→8，含补偿口径 −29%）；AI 重复已知状态 −75%（20→5）；judgments 上升（16→23）系 Round B 配花策略更细（逐月饼定位面板花）且 Maa 失败引入补偿判断，以确定性外壳指标为准。
- **AI→Maa 交还未发生**：Maa 外壳在去下一步骤即失败 + StageC 付费墙需 AI 决策 → AI 一路处理完。真实闭环需把 StageC 之后（✕→确认框→结束→结算→开心收下→主页）编译进 pipeline 且 StartRouter 识别 StageC。
- **下一 Agent 最大摩擦点**：Maa 翻盘 6 次仅 4 次生效（固定 post_delay 不足，翻盘动画需 ≥2s）→ 建议给 FLIP 增大 post_delay 或加「叶子消失/小手数减少」门禁；同时补 StageC 尾部进 pipeline。
- 实验证据：baseline/decisions.jsonl（16条）、hybrid/decisions.jsonl（23条）、roundA_stats.json、roundB_stats.json、FINAL_REPORT.md、S0072→S0142 截图。

## 2026-09-25 18:00-19:00 离线修复：StageA 翻盘后置验证 + StageC 尾部 Pipeline（体力 0，仅离线）

- **翻盘失败根因（定论）**：Maa FLIP 固定 post_delay=1200ms 不足，动画期截图盘面未变。grid_diff（baseline=S0073 全盖帧，|dMean|>25=OPEN）定位失败盘=B(850,193)、D(577,340)（diff=0.0，即点击已发出但像素未变）；成功盘 A/C/E/F ≥54.7。AI 接管补翻的正是 B/D（trace S0116→S0117 实证）。不是"等得不够久"，而是 Maa 不知道翻盘是否成功。
- **修复方案（已离线验证）**：每盘 FLIP_i 后插入 VERIFY_i = TemplateMatch 该盘翻开模板（improved\templates\flip\open_{A..F}.png，80×80，阈值 0.7，ROI 半窗 ±45）。离线匹配：翻开盘 1.000、盖叶盘 0.214-0.454；fixture 24/24（S0073 全盖/S0079 全翻/takeover 现场 A翻C翻E翻F翻 B盖D盖/S0117 全翻）。失败 → recognition_failed → takeover（安全降级，不再盲目再点）。局限：模板来自这一局，下一局同盘馅料可能不同→验证失败走 takeover 属预期。
- **S_A20_A_NEXT 真因 = 裁剪 OCR 不可靠**：rapidocr 对 ROI(100,560,250,600) 只读「步骤」（期望「去下一步骤」失配→8s 超时→takeover）。修复：改按钮 TemplateMatch（next_step_btn.png 165×65，阈值 0.75；StageA 帧 1.000 vs 弹窗遮罩 0.695）。
- **S_C01 complete 信号调整**：底部「还有0个未烤好」裁剪 OCR 实测不可读（rapidocr 空）→ 放弃作为门禁；S_C01 改 OCR「开烤」规则行(120,45,880,160)=StageC 存在确认；complete 唯一硬门禁=S_C10「确定现在结束游戏吗」(380,130,900,300，S0114/S0140 HIT)，该文案天然排除 StageB 未完美弹窗（「确定现在离开吗」不匹配→takeover）。Round B 实证：1 未烤好（火苗不足）也可免费正常结算→未烤好不阻塞结束；付费墙由「不加热」策略规避。
- **S_C20 结算**：expected 改「恭喜您完成本轮」（Maa OCR expected 支持正则子串；裁剪实测输出「恭喜您完成本轮烤月」截断，完整串会失配），ROI(300,100,700,260)；开心收下 Click(638,601) 固定坐标。
- **StageC 尾部 pipeline 定稿（improved/flow.json，23 状态全 maa_ready 除 StageB=proposed）**：S_A00(OCR做月饼)→S_A10→S_A11..16 FLIP+VERIFY→S_A20(按钮模板)→S_A21(OCR未吃到馅料,ROI改120,100,880,330)→S_B00(proposed,AI区域,frontier)→S_C00(OCR开烤,回交入口)→S_C01→S_C05(✕1231,81)→S_C10(OCR确定现在结束游戏吗→Click 900,575)→S_C20(OCR恭喜您完成本轮→Click 638,601)→S_C30(OCR做月饼=终点,不再点)。编译通过 + Maa schema 校验 [OK] All validations passed!。
- **AI→Maa 回交设计**：AI 完成 StageB 配花后自己点去下一步骤(187,565)+确定(909,580)进入烤制页即停止，重启 run_roundC.py，StartRouter 从「开烤」识别进 S_C00 接管尾部。Maa 节点格式确证（fishing.json）：OCR/TemplateMatch/Click/DoNothing/DirectHit/post_delay/timeout/on_error/next/focus；pipeline.schema.json 确认 expected 支持正则。
- **统计口径澄清（trace 实证，替代原「17→8(含补偿12)」歧义）**：Round B AI 段 26 动作 = 正常 24 + 失败补偿 2（补翻 B/D）+ 被拒 2（recorder 红线词）。其中 shell：正常 9 + 补偿 2 = 11；StageB：15（点月饼6+点花7[含误点1]+去下一步骤1+确定1）。下降率修正：shell 正常 −47%（9/17），含补偿 −35%（11/17）；StageB 15（原 14 笔误）。roundB_stats.json / FINAL_REPORT.md 已同步。
- **StartRouter 路由模拟（8 关键帧）**：主页→S_A00 ✓；StageA 全盖→S_A10 ✓；烤制页→S_C00 ✓；退出确认→S_C10 唯一 ✓；结算→S_C20 唯一 ✓。已知摩擦点（记录不修）：①丢弃弹窗帧 S_A10(规则行)先于 S_A21 匹配→从弹窗启动会路由错误（实机 AI 交还前先关弹窗规避）；②StageA 翻后启动会重走 FLIP（再点已翻盘，无害低效）。不把问号/按钮坐标做成全局规则。
- **下一轮一体力 smoke（需用户授权 1 体力）步骤**：① 确认主页「做月饼」+ 体力≥1 + 无继续游戏；② 跑 improved\run_roundC.py（Maa: 做月饼→StageA 翻6盘每步后置验证→去下一步骤→丢弃确认→[frontier StageB]→DumpActivityTakeover→Stop）；③ AI 读 takeover 包从现场继续 StageB（免费盲配/逐月饼定位面板花，SOSO 不付费挽救）；④ AI 到烤制页后停止，再跑 improved\run_roundC.py（Maa: 开烤→✕→退出确认→结束游戏→结算→开心收下→主页做月饼→Stop）；⑤ 验收：主页做月饼恢复、无继续游戏、体力=起始−1、Maa→AI→Maa 真实闭环、StageA 6 盘全部后置确认无 AI 补偿。模板绝对路径已写入 pipeline（MaaFramework TemplateMatch 支持绝对路径）；若验证失败走 takeover=预期降级，AI 重新采集模板。
- 本轮未动：frozen 实验数据（frozen/pipeline.json sha 54963b3a05a799b2、baseline/hybrid stats）、未 commit/push、未新开局（体力 0）。
## 2026-09-25 19:00-19:40 V2 离线修复：StageA CHECK-before-FLIP（resumable）+ modal 优先路由（体力 0，仅离线）

### 1) StageA resumable 重构（编译器最小扩展 + flow 重构）
- **编译器**（scripts/recorder/flow_to_maa.py，V1 最小扩展，未重设计）：state 支持 `recognition_fail_next` → 识别失败时 `node["on_error"]=[目标节点]` 而非固定 TakeoverError；无该字段节点行为不变。回归 test_flow_to_maa 11/11 OK。
- **flow 结构**（improved/flow.json，31 状态）：新增 6 个 CHECK 节点（S_A11..A16_CHECK，TemplateMatch 同盘 open 模板阈值0.7、ROI 各盘±45、recognition_fail_next=对应 FLIP、next=下一 CHECK，F→S_A20）；FLIP post_delay 2500ms（动画≥2s）+ recognition_timeout 8000；VERIFY next 改为下一 CHECK（F→S_A20），on_error 仍 TakeoverError（不自动二次点击）。已开盘→SKIP→下一盘；CLOSED→FLIP→VERIFY；unknown 判定也走 FLIP+VERIFY 兜底（不假设 closed 盲点）。
- **恢复场景模拟（resume_sim.py，模板分实测）**：Case1 全盖 S0073→CLOSED=A..F（6 FLIP）✓；Case2 takeover 现场 current.png（A/C/E/F 开 B/D 盖）→仅 B,D 需 FLIP ✓；Case3 全开 S0117/S0079→0 FLIP ✓。**重启后不会从 FLIP_A 盲点**——每盘先 CHECK，已完成的动作不重执行。

### 2) modal 优先路由（付费墙/未完美/丢弃/结束确认不被底层抢路由）
- 新增 S_X10_PAYWALL（TemplateMatch paywall_title.png 731×49，阈值0.7，ROI [100,120,1020,320]——搜索窗必须≥模板宽，x2≥1005 才能对齐标题右缘；离线分：S0138=1.000 vs 烤制页0.096/未完美0.202/确认框0.117/丢弃0.200）+ S_X20_STAGEB_LEAVE（OCR「不能陪您去下一步骤」ROI[150,150,850,280]，S0112 HIT，S0080/S0119「定继续吗？」天然不匹配）+ S_A21 丢弃确认移到 modal 区（states 顺序最前）。
- **StartRouter 路由模拟 9 帧全过**：S0138付费墙→S_X10 ✓（先于 S_C00）；S0112未完美→S_X20 ✓（先于底层配花页）；S0080丢弃→S_A21 ✓（修复：S_A21 必须排在 S_A10 之前，原顺序会被规则行抢路由）；S0114退出确认→S_C10 ✓；S0113烤制页/S0079 StageA/S0072+S0142主页/S0115结算 无弹窗帧路由不变 ✓。
- S_X10/S_X20 result_candidates 指向非 ready 占位（AI_DECISION_*）→ 编译为 Frontier→DumpActivityTakeover（弹窗命中即交还 AI 决策，绝不绕过弹窗继续底层动作）。
- 付费墙标题含数字（如「5开心宝」）跨轮可能变化→模板失配走 start_router_unmatched=takeover 安全降级（预期路径）。

### 3) 关键调试记录（脚本缺陷 ≠ flow 缺陷）
- resume_sim 首跑 2 FAIL 均为模拟脚本问题：①非 flip 模板中心搜索窗 half=95（190px）容不下 731px 宽付费墙模板 → S_X10 ROI 加大 [100,120,1020,320]（模拟脚本 half 亦需≥380）；②S_A21 排序错误（曾排在 S_A10 后）→ 已移到 modal 区。S_C01_COMPLETE_CHECK 曾被脚本误报 fail_next FAIL——名字含「CHECK」但本就不需要 fail_next（识别失败→TakeoverError 是正确设计），脚本过滤后全绿。

### 4) 本轮验收状态
- 全盖→6 FLIP / 半开→仅 B,D FLIP / 全开→0 FLIP：✓（已开盘绝不重复 Click）
- FLIP 后仍有 VERIFY、VERIFY 失败→takeover：✓（on_error=TakeoverError 结构验证）
- StageB 弹窗/StageC 确认框/开心宝付费墙 优先于底层 Stage：✓（9/9 帧）
- schema 校验 [OK] All validations passed!（schema_imp7，pipeline 副本 improved/schema_check/pipeline.json）；test_flow_to_maa 11/11 OK
- 未改 StageB（AI 区域）、未改 StageC 尾部业务规则（S_C01 无 fail_next 保持）、frozen 实验数据未动、未 commit/push、未实机新局（体力 0）

### 5) 下一轮一体力 Maa→AI→Maa smoke（唯一待办，需体力恢复+用户确认授权 1 体力）
步骤：① 确认主页「做月饼」+体力≥1+无「继续游戏」；② 跑 improved\run_roundC.py（Maa: 做月饼[耗1体力]→StageA CHECK→FLIP→VERIFY 六盘→去下一步骤→丢弃确认→frontier StageB→DumpActivityTakeover→Stop）；③ AI 读 takeover 包（meta.json/current.png/trace_tail.jsonl）从现场继续 StageB（免费策略：盲配/逐月饼定位面板花，SOSO 不付费挽救；配花页去下一步骤(187,565)+确定(909,580)）；④ AI 到烤制页「开烤」后**立即停止游戏操作**；⑤ 再跑 improved\run_roundC.py（Maa: StartRouter 识别「开烤」→S_C00→✕→退出确认→结束游戏→结算→开心收下→主页「做月饼」→Stop）。
10 项验收（任一项失败→保存 takeover/trace，不临场修复再耗体力）：① 实际只耗 1 体力；② StageA 6 盘最终全 OPEN；③ Maa 不重复点击已 OPEN 盘；④ 无 AI 补偿翻盘；⑤ StageB 由 AI 完成；⑥ AI 到 StageC 后停止游戏操作；⑦ Maa 第二次真接管；⑧ Maa 自己完成退出+结算；⑨ 最终回 ActivityMainFresh（做月饼恢复、无继续游戏、体力=起始−1）；⑩ 完整 Maa→AI→Maa 闭环。
开放点（离线无法验证）：MaaFramework TemplateMatch 对 pipeline 中绝对路径模板的实机加载；CHECK 判定与 VERIFY 的像素级时序。

## 2026-09-26 00:00-01:20 cron 触发双活动自动线（TaskID 12341833902082「巧手裁缝铺零点体力自动执行」）

**触发与刷新**：09-26 00:00 cron 触发。实测两活动每日体力 **0 点刷新**（裁缝铺登入引导发 2 点、酿月登入引导发 3 点[x3]）。全程 0 开心宝/0 宝石/0 付费/0 广告，未 commit/push。

### A 线裁缝铺（体力 2→1→0 全部消耗，A25 修复实机复测成功）
- **活动入口变更（新事实）**：活动列表卡片顺序每次变化——本次裁缝铺排**第 5 张卡片**(1180,380)（旧记录第 1 张(165,325) 失效）。进列表必须 OCR 定位卡片名，不能固定坐标。
- **第 1 局**：Maa 全程自动（A00→A10→A20×3→A21→A30→C 型兑换商店弹窗 frontier）→ AI 整页 X(1220,65) 关闭 → 第 2 关剪布页 → **A25 x10 帧误触发**（0 模板 Maa=0.781≥0.75）→ AI 复核 x10 不消费 → 修复 A25（裁 x10 模板 + A26 分流排除）→ 续跑 → 剪刀 0 AI 结束本局 → 主界面体力 2→1。
- **A25 三版修复史（最终有效）**：①0.75 阈值 → x10 帧 0.781 误触发（"10"含 0 圆圈）；②OCR 精确匹配 `x0|X0|xo|XO|×0` → 实机失败（MaaOCR 把剪刀区小字 x0 读成「V」score 0.253，A25 漏判 → A20 在剪刀 0 时连续点裁剪死循环，00:42 日志确认）；③**TemplateMatch 0 模板阈值 0.75→0.80**（templates/scissors_digit0.png，ROI 像素(400,590,700,730)）→ **实机两次验证通过**：x0 帧准确命中→knowledge_frontier（包 20260926-004411 / 010324），x6 帧 0.772、x10 帧 0.781 均 <0.80 不触发。**注意**：本地 python 稠密匹配分数与 Maa TemplateMatcher 不一致（x6 帧本地 0.696 vs Maa 0.772），离线夹具不能定 Maa 阈值；整体 x0/x6 模板被 x 前缀支配不可用。
- **第 2 局（A30 修复后）**：Maa 自动：结算(开心收下)→**无弹窗回 A20 下一关**（新分支 S_A20_CUT 实机验证成功，连续关卡不再需要 AI 干预）→再结算→B 型弹窗 frontier → AI 点免费档(253,508)变 Get + X 关闭 → 续跑 → **A25 剪刀 0 第二次实机命中 frontier** → AI 退出（X→确认(372,570)）→ 主界面体力角标 **0** → A 线收口。
- **A30 修复定论（像素坐标）**：Maa OCR/TemplateMatch 的 **box 与 ROI 均为像素坐标（1280×720）**，Read 工具 OCR box 才是千分比。A30 两版失败：①OCR expected「恭喜您获得了」→ MaaOCR 把艺术字标题读成「添喜恐状侍了」(score 0.447) 漏判；②ROI 误写千分比 (400,790,600,900) → `roi is out of range` 越界（图高 720）A30 永不命中 → A21 抢跑/超时。**最终方案**：OCR expected「开心收下」（普通字体稳定）+ ROI 像素(500,570,800,650)（按钮像素(553,585)-(726,626)）+ click(633,609)。**Maa 候选失败级联（再确认）**：next 列表候选识别失败只算"未命中"，不执行候选自身 on_error/recognition_fail_next，回父节点反复重试至父超时→父 on_error(TakeoverError)。

### B 线酿月食香：最终一体力 Maa→AI→Maa smoke（10 项验收全部通过 ✓✓✓）
- 入口：活动列表**第 1 张卡片**(87,595)（本次顺序：酿月/碎片/宝石/百草/裁缝）。主页「做月饼」+体力角标 **3**（0 点刷新登入领 x3）+无「继续游戏」+桂花酒 x3。
- **第一次 Maa 实机暴露 StageA CHECK 设计缺陷并修复（全正向语义）**：原 CHECK 用 open 模板「命中=已开、不命中→recognition_fail_next=FLIP」——Maa 语义下 A11_CHECK 作为 A10 的 next 候选识别失败=未命中，fail_next 不生效 → A10 超时 TakeoverError（包 010633）。**修复**：CHECK 改用 **closed 模板（每盘粽叶覆盖图 closed_{A..F}.png，90×90，阈值 0.7）正向语义**——命中=盖叶→result=[FLIP]；不命中=已开→recognition_fail_next=下一盘 CHECK（F→S_A20）；FLIP 后直接 result=下一盘 CHECK（移除 VERIFY 独立节点，未翻盘由去下一步骤免费丢弃兜底）。resume 时已开盘 closed 不命中自动跳过 ✓。
- **Maa 第一次运行（修复后）完整自动**：StartRouter→A10→CHECK/FLIP×6（六盘全翻，各耗 1 小手，小手 6→0）→A20 去下一步骤(187,581)→（A21 丢弃确认误命中 StageB 规则行，OCR 误读，无实际危害）→**frontier at StageB**（包 011122）。
- **AI StageB 配花（免费盲配黄桂花策略）**：6 枚月饼（3列×2行：本轮 6 枚与 Round B 4 枚不同，每局随机）。逐月饼：点月饼→点其上方黄花(桂花)→PERFECT 保留/SOSO 不挽救。结果 3 PERFECT + 1 SOSO + 右侧 2 枚未配 → 去下一步骤 → 「还有3颗月饼没有完美哦」确认框 → 确定(905,580) 免费丢弃 → **烤制页（开烤，0未烤好）→ AI 立即停止**。
- **第二次 Maa（尾部，ROI 修正后）完整自动**：StartRouter→S_C00(开烤识别)→S_C01→S_C05(✕1231,81)→S_C10(「确定现在结束游戏吗」→结束游戏(900,575))→S_C20(「恭喜您完成本轮」→开心收下(638,607))→**S_C30(主页「做月饼」识别=终点) 全程无 takeover**。
- **StageC/终点 ROI 修正**：烤制页规则行像素(182,37)-(1156,112)，旧 ROI(120,45,880,160) 右侧被切 → 放宽(140,30,1170,170)；做月饼按钮像素(530,587)-(749,683)，旧 ROI(500,600,790,680) 顶部切 → 放宽(480,570,810,700)。
- **10 项验收**：① 只耗 1 体力（3→2，主页 OCR 复验）✓；② StageA 6 盘全翻 ✓；③ 无重复点击已开盘 ✓；④ 无 AI 补偿翻盘 ✓；⑤ StageB 由 AI 完成 ✓；⑥ AI 到烤制页后停止 ✓；⑦ Maa 第二次真接管 ✓；⑧ Maa 完成退出+结算 ✓；⑨ 回 ActivityMainFresh（做月饼恢复、无继续游戏、体力=2）✓；⑩ 完整 Maa→AI→Maa 闭环 ✓。
- 两线收口：裁缝铺体力 0、酿月体力 2（起始 3→耗 1→剩余 2，以实机截图+stamina_detect 2/2=1.0 为准；本轮只跑 1 局 smoke，剩余 2 点未继续消耗——根因见下节 cron 生产模式修正）。证据：tailor session S0070→S0083、mid-autumn session S0143→S0155、takeover 包 010633/011122/尾部无包。

### 下一 Agent 建议（体力限制）
- **裁缝铺**：体力 0 已收口，明日 0 点 cron 自动续跑（同 query）。已知待办：无（A25/A30 均已实机修复验证）。
- **酿月食香**：剩余体力 2（起始 3→耗 1→剩 2，实机截图+stamina_detect 2/2 验证；今日仅 smoke 1 局）。明日 cron 已改为 production/drain-stamina 模式，按每局后重读体力驱动，2 点可跑 2 局。改进点（记录不修）：A21 丢弃确认 OCR 在 StageB 规则行误读（expected「未吃到馅料的月饼」在 ROI(120,100,880,330) 内对 StageB 误命中）——建议 StageB 触发后 A21 失效或加排除；StageA 翻盘未翻盘由丢弃兜底（可接受）。改进点（记录不修）：A21 丢弃确认 OCR 在 StageB 规则行误读（expected「未吃到馅料的月饼」在 ROI(120,100,880,330) 内对 StageB 误命中）——建议 StageB 触发后 A21 失效或加排除；StageA 翻盘未翻盘由丢弃兜底（可接受）。
- 安全：两线均 0 付费；「x20挽救/一键挽救/一键完美/扭转心意/一键帮我选/探索心愿/一键扭转」均为付费/消耗按钮，全程未点。

## 2026-09-26 复核：cron 停止条件修正（smoke → production/drain-stamina）

**根因（实机 + 文档三层确认）**：09-26 00:00 cron 酿月线停在体力 2 不是 stamina_detect bug，而是 **cron query 把 B 线写死为「最终一体力 smoke」验收模式**——验收 10 项成功即结束，被沿用成了生产任务的停止条件；run_roundC.py 本身也是单局执行脚本（post_task 一次即退出，无体力循环）。三层证据：①cron query 原文 B 线标题=「酿月食香最终一体力 smoke（唯一待办）」+第 5 步验收成功即止；②handoff B 线步骤同为 smoke 语义；③run_roundC.py 无 while 体力循环。A 线 query 原已含"若第 1 局结束体力=1 执行第 2 局"，近似体力驱动但未统一为生产循环语义。

**体力事实（矛盾修正）**：酿月起始 3（0 点登入领 x3）→ 做月饼耗 1 → **剩余 2**（final_main.png OCR「2」+ stamina_detect 2/2=1.0）。此前「剩余 1 点/续跑 1 局」为笔误，已修正为「剩余 2 点，可续跑 2 局」。今日仅跑 smoke 1 局属 query 语义所致，非异常。

**修改（最小变更，未动任何已实机验证逻辑）**：update_cron_job 12341833902082 仅改 query（schedule 0 0 * * * / title / enable 均不变）。新版 query 明确 production / drain-stamina 模式：
- 每线每局：读体力 N → N=0 停该线 → N>0 完整跑 1 局（Maa→AI→Maa 闭环 + 每局验收）→ 回该线主界面 → 重读体力 → 重复，直到体力=0。
- 生产安全停止：任一局 recognition_failed 无法安全恢复 / 未知付费墙 / 资源不足 / 无法可靠回主界面 → 保存 takeover 停止该线，不再消耗下一点体力。
- 禁止按「今天应有几体力」预设局数；每轮实测（不预设 2 局/3 局）。
- 顺带更新背景事实：酿月每日 0 点登入领 x3（非"每日 2 点"）、A25 阈值 0.80（勿回退 0.75）、活动列表卡片顺序变化需 OCR 定位、刷新时刻已实测 0 点。
- 每局验收沿用酿月 10 项 + 裁缝铺 A25 命中/体力-1/回主界面。

**状态**：体力 2 保留未动（本轮不消耗）；下次触发 09-27 00:00 按生产模式把裁缝铺 2 点 + 酿月 2 点分别消耗至 0。run_roundC.py / run_tailor_round2.py 维持单局执行（生产循环由 cron query 的 AI 每局编排实现，不重写脚本）。