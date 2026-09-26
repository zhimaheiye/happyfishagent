# 限时活动 AI + Maa 接力工作流

这是 2026-09-25 已经落地的实现说明，不是项目设想。下一任 Agent 按本文继续，不要重新调查架构，也不要重做 V0 / V1。

现场状态以 [handoff-current.md](handoff-current.md) 为准。

## 1. 项目目的

AI 负责未知状态探索。Maa 负责已经确认的确定性流程。

这样做是为了少做三件事：

- 对同一界面反复调用 AI 视觉；
- 让人手工截图、报坐标；
- 为两周后就下线的限时活动增加永久 Maa 维护。

原则：AI 只处理未知，Maa 消化重复。

## 2. 当前架构

```text
AI
↓
record_action.py          探索时的唯一点击入口
↓
session / flow.json / trace.jsonl
↓
人工或 Agent 验证         不能靠“看起来对”
↓
status = maa_ready
↓
flow_to_maa.py
↓
session/generated/pipeline.json
↓
Maa 运行临时 Pipeline
↓
DumpActivityTakeover
↓
StopTask
↓
AI 读接管包，从当前画面继续
```

两个仓库分工：

| 仓库 | 本机路径 | 职责 |
|---|---|---|
| `happyfishagent` | `D:\开心水族箱活动经验\happyfishagent` | 探索、session、flow、临时 Pipeline |
| `MaaHappyFish` | `D:\happyfishgame` | 正式日常自动化，以及通用的 `DumpActivityTakeover` |

临时 Pipeline 留在 session 里。不要写入 `assets/resource/pipeline/features/`。

## 3. V0 Recorder

入口：`happyfish-activity-automation/scripts/record_action.py`。

实现在 `scripts/recorder/`，和编译器分开。`flow_to_maa.py` 只读 flow，不操作设备。

已实现：

- 动作前、动作后截图，归一化到 1280×720；
- 同时保存设备坐标和 1280×720 坐标；
- 帧差：全局变化、变化框、first-change、stable；画面一直在动时到 `--max-wait` 就保存，不无限等；
- `trace.jsonl` 只追加；
- 每次 `init` 新建 session，不覆盖旧目录；
- `--safety` 与 `--reason`。缺省 `unknown` 不点击。文案里的修复、复活、补充、加速、解锁、开心宝、广告会拒绝。

Session 路径：

```text
happyfish-activity-automation/activities/<event>/sessions/<时间戳>/
├── flow.json
├── trace.jsonl
├── screenshots/
├── diffs/
├── takeover/
└── generated/pipeline.json    编译之后才有
```

`activities/*/sessions/` 已在 `.gitignore` 中。不要把原始截图提交进库。

当前限制：

- Recorder 不理解页面语义，也不能代替红线判断；
- 鱼一直在游时，画面可能永远达不到“稳定”，超时后仍会留下现场；
- 不做 OCR、不自动裁模板、不自动生成 Pipeline。

常用命令和真实参数一致：

```bash
python happyfish-activity-automation/scripts/record_action.py --event <event> init
python happyfish-activity-automation/scripts/record_action.py --event <event> shot
python happyfish-activity-automation/scripts/record_action.py --event <event> --safety nav --reason "为什么安全" tap <x> <y>
python happyfish-activity-automation/scripts/record_action.py --event <event> --safety nav --reason "滑动列表" swipe <x1> <y1> <x2> <y2> <毫秒>
python happyfish-activity-automation/scripts/record_action.py --event <event> annotate --state S0001 --name "活动首页" --recognition-type OCR --expected "开始" --roi 10 20 30 40
```

坐标默认是设备像素。看的是工具保存的 1280×720 图时加 `--coord-space 720p`。

设备只认 `HAPPYFISH_ADB_DEV`、`ADB_DEV`、`tools/mumu_dev.py`，或当前唯一在线设备。本机 MuMu 的 `wm size` 可能仍是未旋转的 `720×1280`，点击坐标系以 `dumpsys input` 的 `logicalFrame` 为准。

`annotate` 默认只写 `proposals`，状态变成 `proposed`。只有显式 `--status confirmed` 或 `--status maa_ready` 才写入正式 `name` / `recognition`。

## 4. flow 状态生命周期

```text
observed → proposed → confirmed → maa_ready
```

| 状态 | 含义 | 能否编译进 Maa |
|---|---|---|
| `observed` | Recorder 写下的原始事实。`recognition` 仍是 null | 否 |
| `proposed` | AI 或人工的提议，例如名字、ROI、expected | 否。proposed 不能被编译 |
| `confirmed` | 人已经确认的规则，但还没有允许交给 Maa | 否。confirmed 也不会自动进入 Maa |
| `maa_ready` | 已确认，并且允许映射成临时 Pipeline 节点 | 是，且必须已有正式 `recognition` |

缺参数就编译失败，不猜 ROI、不猜模板、不猜坐标。

## 5. V1：flow → 临时 Maa

命令：

```bash
python happyfish-activity-automation/scripts/flow_to_maa.py --event <event>
python happyfish-activity-automation/scripts/flow_to_maa.py --session <session 目录>
```

产物：`sessions/<时间戳>/generated/pipeline.json`。

当前只支持四类：

| flow | Pipeline |
|---|---|
| OCR + `ClickRecognitionResult` | `recognition: OCR`，`action: Click`，不写 `target` |
| TemplateMatch，且已有 template、threshold、recommended_roi，文件真实存在 | `TemplateMatch` + Click 识别结果 |
| OCR 或 TemplateMatch 门禁 + `target_center_720p` | `action: Click`，`target: [x, y]`。不用设备原生坐标 |
| `DoNothing` | 识别页面，不操作 |

其它约定：

- `expected_mode` 默认 `literal`，编译时正则转义。只有 `"regex"` 才原样传入。
- 节点名是 `Activity_<slug>_S0001`。原始活动名在 `$meta.event`。
- `StartRouter` 是 `DirectHit` + `DoNothing`，`next` 只含有 UI 识别的 `maa_ready` 状态，顺序跟 flow 一致。识别内容重叠时只警告，不改优先级。
- `post_delay` 优先用 `timing.action_to_stable_ms`。没有实测值时用 800 毫秒。Recorder 因为鱼缸动画而 `timed_out` 时，不要把那个等待上限写成 Maa timeout。
- 识别 `timeout` 默认 8000 毫秒。flow 里若有 `timing.recognition_timeout_ms` 则用它。
- 后继也是 `maa_ready`：`next` 连到那个状态。
- 后继还不是 `maa_ready`：`next` 进入该状态自己的 `TakeoverFrontier`，reason 为 `knowledge_frontier`，然后 `StopTask`。这不是识别错误，是知识用完了。
- 状态自己的识别失败：`on_error` 进入 `TakeoverError`，reason 为 `recognition_failed`，然后 `StopTask`。Dump 失败也进同一个 Stop。

校验生成结果时用 MaaHappyFish 的 schema，不要只做 `json.loads`：

```bash
python D:\happyfishgame\tools\validate_schema.py --schema-dir D:\happyfishgame\deps\tools --resource-dirs <只含 pipeline.json 的目录>
```

`test_flow_to_maa.py` 已经这样调用。

## 6. 三种 takeover

三者都走同一个 `DumpActivityTakeover`，没有第二套实现。截图函数是 `agent/my_action.py` 里的 `_capture_720p`。

### recognition_failed

已经处在某个已知状态节点上，但这条规则没有识别成功。`source_state` 是该状态，例如 `S0003`。节点名以 `__TakeoverError` 结尾。

### knowledge_frontier

Maa 已经做完这个状态上确认过的动作，下一状态还没有 Maa 规则。`source_state` 是刚做完动作的状态。`result_candidates` 里是尚未 `maa_ready` 的后继。节点名以 `__TakeoverFrontier` 结尾。

### start_router_unmatched

任务启动时，当前画面不属于任何一个已知 `maa_ready` 状态。Maa 的 `next` 未命中不会触发子节点的 `on_error`，所以超时落在 StartRouter 上。

```text
Activity_<event>_StartRouter
├─ next: 各个 maa_ready 状态
└─ on_error
      ↓
Activity_<event>_StartRouter__TakeoverUnknown
      ↓
Activity_<event>_StartRouter__Stop
```

参数：

```json
{
  "reason": "start_router_unmatched",
  "source_state": null,
  "known_candidates": ["S0001", "S0002"],
  "event": "<原始活动名>",
  "session": "<session id>",
  "flow_path": "<绝对路径>",
  "pipeline_path": "<绝对路径>"
}
```

`known_candidates` 与 StartRouter 的候选状态一致，用的是 flow 里的状态号，不是 Pipeline 节点名。Dump 失败时 `on_error` 仍是 `StopTask`。

这个 reason 的实机闭环还没跑，见第七节 Step 1。

## 7. Takeover package

目录：`sessions/<时间戳>/takeover/<takeover-id>/`。

| 文件 | 作用 |
|---|---|
| `meta.json` | 活动、session、reason、source_state、expected、roi、路径 |
| `current.png` | 最关键的证据。正式动作用 `_capture_720p`，正常时应是 1280×720 |
| `trace_tail.jsonl` | session `trace.jsonl` 的最后 10 条。没有 trace 时文件为空，`trace_status` 为 `unavailable` |
| `maa_log_tail.txt` | 可选。只在能定位到本次进程日志时写 |

日志找不到不能让整包失败。`source_state` 可以为 null，这表示不是某一个已知状态失败，而是启动时没有对上任何已知状态。

AI 接手时从 `current.png` 和 `meta.json` 继续，不要退回活动入口重新摸一遍。

`DumpActivityTakeover` 在 `my_action.py` 里只注册一次。helper 在 `agent/activity_takeover.py`，不绑定某个活动。没有把临时活动逻辑放进正式 feature JSON。

## 8. 为什么不进正式 feature

| 活动以后怎么样 | 放哪 |
|---|---|
| 一次性，或很快下线 | 留在 `happyfishagent` 的 session 和活动文档里，不再维护 |
| 偶尔复刻，流程稳定 | 保留这份临时 Pipeline，下次复用。不必进 MaaHappyFish 主界面 |
| 长期、高频、规则已经稳定 | 再按 MaaHappyFish 现有规范迁成 feature 文档、pipeline、测试和 interface |

在那之前，不要自动修改：

```text
interface.json
DailyRoutine
Release
```

## 9. 下一阶段：第一只真实活动实验

本阶段没有执行。下面是交给下一任 Agent 的步骤。

### Step 1：StartRouter 零点击 smoke test

这是下一轮的第一项实机验证。不要先做活动探索。

```text
StartRouter
↓
所有候选都不匹配
↓
reason = start_router_unmatched
↓
生成 takeover package
↓
StopTask
```

要求：0 Click，0 游戏资源消耗。

做法：编一份临时 flow，里面 1～2 个 `maa_ready` 状态的 OCR expected 使用绝不可能出现的字面量，动作为 `DoNothing`。入口必须是 `Activity_<event>_StartRouter`，不要直接进入业务节点。业务节点作为 next 候选失败时，不会走业务节点自己的 `on_error`。

跑完检查：

- `meta.reason` 是 `start_router_unmatched`；
- `meta.source_state` 是 null；
- `known_candidates` 与 Router 的候选一致；
- 有 `current.png`；
- 任务最后是 `StartRouter__Stop`；
- Pipeline 里没有 `Click`。

历史参考：`recognition_failed` 已经用直接进入业务节点的方式跑通过，脚本是 `D:\happyfishgame\dev\test_activity_takeover_live.py`。那个脚本的入口不是 StartRouter。下一轮要么改入口，要么另写一条只跑 Router 的命令。本轮不要启动它。

待下一阶段实机验证。

### Step 2：选择第一只真实活动

要同时满足：

- 当前开放；
- 流程短；
- 主要是识别加点击；
- 免费路径清楚；
- 没有复杂实时小游戏；
- 没有高风险消费；
- 没有明显的个人选择，例如奖励多选一。

不要先挑许愿神灯、深海寻鱼这类已经出过误消耗事故的活动，也不要先挑需要长链路策略的玩法。先看 `docs/handoff/CURRENT.md`（在 MaaHappyFish）和活动文档，确认仓库里是否已经有正式功能。已有的不要重做。

### Step 3：AI 首轮探索

只探索 2～4 个状态。游戏里的点击和滑动只用 `record_action.py`。禁止裸 `adb shell input tap`。

探索阶段只点导航、页签、关闭和只读视图。可能消耗资源的按钮先读字，拿不准就不点。

### Step 4：验证 recognition 再升级

AI 可以写 `proposed`。升到 `maa_ready` 之前要有确定性验证：

```text
ROI 内单独识别
→ 正样本命中
→ 必要的反样本不命中
→ 这一下是安全的
```

不要因为截图看起来像，就把状态标成 `maa_ready`。

### Step 5：第一次交给 Maa

至少有 2 个连续的 `maa_ready` 之后：

```text
flow_to_maa
→ schema validation
→ 用临时 Pipeline 运行
```

已经交给 Maa 的状态，AI 不要再自己点一遍。

### Step 6：第一次 knowledge_frontier

目标是这条链，而不是从入口重来：

```text
Maa 跑完已知状态
↓
knowledge_frontier
↓
takeover package
↓
AI 从 current.png 的当前位置继续
```

### Step 7：第二次编译

AI 再探索 1～3 个新状态，确认后重新编译再跑。要看的是：第二次 Maa 自动跑过的区间是否比第一次更长。

## 10. 指标

不要算 token。看的是 AI 是否越来越少重复处理旧状态。

| 指标 | 第一轮 | 第二轮 |
|---|---:|---:|
| AI 游戏动作数 |  |  |
| Maa 游戏动作数 |  |  |
| maa_ready 状态数 |  |  |
| takeover 次数 |  |  |
| recognition_failed |  |  |
| knowledge_frontier |  |  |
| start_router_unmatched |  |  |
| AI 重复查看旧状态次数 |  |  |

## 11. 离线回归

不碰游戏时跑：

```bash
python happyfish-activity-automation/scripts/recorder/test_recorder_offline.py
python happyfish-activity-automation/scripts/recorder/test_flow_to_maa.py
python D:\happyfishgame\dev\test_activity_takeover.py
```

`test_flow_to_maa.py` 包含 V1.1 的 StartRouter 断言，以及 MaaHappyFish schema 校验。

`dev/test_activity_takeover_live.py` 会连接模拟器并跑 Maa。额度或现场不合适时不要重复跑。此前通过应写成「此前已通过，本轮未重复」，不要写成失败。
