# 活动执行与收工验收

2026-11-02 用户授权落实。适用于本项目的日常活动执行；离线调查、文档维护不自动启动游戏，也不触发玩法完成要求。

## 谁能规定目标，谁能记录事实

当前用户指令、已核实的持续要求决定目标及资源边界。用户约束集中在 `tools/activity-guard/user-policy.json`，来源见其中原话。技能只提供方法；技能、旧台账、记忆中由助手形成的结论，都不能更改用户目标。真实UI可否定旧的机制描述，但不能新增花钱/兑换授权。

执行时遇到冲突，执行用户规定，舍弃冲突技能段；继续在既定免费边界内核实方法，不反复请用户确认早已授权的事项。尚不知道结束/新开路径时先读帮助、页面和退出弹窗，逐步录制；不能编造坐标、不能把“没有查明”说成“只剩付费”。

日常执行期间，AGENTS、有效SKILL、边界文档、用户约束及验收代码受保护。新截图/动作表照常归档；新发现写 `assets/<slug>/observations/<run-id>.md`，分成“直接观察（截图/动作号）”“待验证推断”“建议修订”。不得在当轮把自己的停手理由写回有效SKILL。

离线维护可以自动整理这些材料，不要求用户手工分类。每条提升为有效机制的内容须有动作前后证据，并与用户约束核对；失败记录只记“当时做了什么、哪里错”，不能作为下次的规定。用户新纠正仍用结构化check保存，但why应包含 `用户原话：「逐字原句」` 及来源；助手自述不算用户原话。修改或撤销旧知识须在旧入口原位标记失效/替换，避免只追加一条更正而保留旧权威。

## 每项活动的状态分开记录

- **入口资源**：本活动主页体力/门票/次数余额及每局成本。不能用主缸同图标读数或别日数字代替。
- **关内资源**：南瓜、剪刀、耐久等，仅说明本局能否继续。
- **当前局**：无局、正在玩、死局、已结束。暂离/继续存档均不证明已结束。

关内资源为0 → 核实本轮是否还可安全获益 → 无路时结束本轮 → 核对结束后的页面及入口额度 → 仍可开局则继续。新局是否补材料必须实测；既不能从恢复旧局不补材料推出新局也不补，也不能反过来保证必发15个。入口余额不足也不免除尚可推进的活局。

## 执行入口与机器验收

Qoder的04:00任务提示词以 `[HAPPYFISH_DAILY_EXECUTION_V1]` 开头时自动启用；也兼容原始“你是《开心水族箱》项目的「04:00 全天档」”开头。hook会告知本会话 `run_id` 和清单绝对路径。其它Agent或手动活动任务先运行：

```powershell
node D:/开心水族箱活动经验/happyfishagent/tools/activity-guard/guard.mjs begin "唯一运行ID"
```

使用返回的manifest路径填写JSON；`begin`本身不做游戏操作。Qoder手动执行时要用hook给出的会话id，确保Stop验证同一份清单。无hook的客户端必须显式运行check，不得把它描述成已有宿主强制拦截。

```powershell
node D:/开心水族箱活动经验/happyfishagent/tools/activity-guard/guard.mjs check "返回的manifest.json绝对路径"
```

最小清单结构（占位值须换成本轮现场证据，不能照抄当验收）：

```json
{
  "version": 1,
  "run_id": "hook给出的ID",
  "inventory": {
    "observed_at": "本次ISO时间含时区",
    "evidence": ["D:/本轮大厅.png"],
    "activities": [{"id": "halloween-cat-house", "included": true, "reason": "有效期内已纳入，现场发放免费入口额度"}]
  },
  "activities": [{
    "id": "halloween-cat-house",
    "entry": {"scope": "activity-entry", "resource": "喵喵屋入口闪电", "balance": 0, "cost": 1, "observed_at": "本次ISO时间含时区", "evidence": ["D:/本轮入口.png"]},
    "round": {"state": "ended", "observed_at": "本次ISO时间含时区", "evidence": ["D:/本轮结束后.png"]},
    "outcome": "exhausted"
  }]
}
```

发现清单必须覆盖本次现场活动以及之前已纳入、仍需核对的活动；排除项 `included:false` 必须填reason、observed_at、evidence。纳入项和activities逐项对应。不能删掉难做项来通过验收。

`outcome`：

- `exhausted`：入口余额小于每局成本，且round为`ended`或`none`。不能把体力未知写成0。
- 已耗尽免费入口且没有活局时，看到付费续局仍属于`exhausted`，不能把未授权付费玩法列成未完成义务。
- `expired`：本轮截图、observed_at、带时区play_deadline证明玩法已到期；不是兑换授权。
- `blocked`：结果为**未完成**；block须有kind（`paid-only`/`unsafe-reset`/`unresolved-ui`）、具体description，以及checks数组。数组必须含step=`entry-inspection`、`round-end-inspection`、`new-round-inspection`三项，各有finding、observed_at、evidence。只截南瓜为0或引用技能不能通过。

全局设备/并发/存档问题可用顶层external_block，包含kind=`device-unavailable`/`concurrent-controller`/`save-conflict`、description、observed_at、evidence；仍只能报未完成，不要求为补齐截图强行恢复设备。无法取得任何截图时如实报告，验收保持失败，不能伪造。

用户暂停立即停输入。Qoder识别简短直接暂停指令，其他措辞也必须服从；如hook尚未识别，报告未完成即可，不得为了通过验收继续游戏。Stop最多要求两次补正，再明确结束为未完成，避免无限循环。用户明确恢复后才恢复。

返回 `accepted:true,status:completed` 才能写活动全部完成；`incomplete`/`paused`允许安全结束但不得写成功。收工报告附receipt路径。游戏归还、MFA恢复、归档等其它职责仍按原任务执行。

## 可验证的范围

验收程序检查字段、入口资源与局状态的逻辑、纳入项覆盖、图片格式/存在性/本轮时间及哈希；它**不自动理解图片内容**，不能证明Agent没有漏发现活动或伪报读数。仍须保留Recorder证据供复核。Qoder hooks提供防误写与完整性检查，不是隔离恶意进程的系统权限沙箱；同账户任意代码权限仍能绕过，不能声称绝对不可篡改。

规则维护时离线修改、测试后重新安装基线；日常任务禁止自行重新安装保护器。测试见 `node --test tools/activity-guard/guard.test.mjs`。Qoder hook协议参考 https://docs.qoder.com/cli/hooks ，安装与实测结果见本次部署记录。
