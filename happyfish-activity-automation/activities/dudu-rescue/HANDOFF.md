# WorkBuddy接手：验证能否理解并复用模块

用户决定让WorkBuddy接手，本Agent暂停游戏输入，保留剩余体力供接手验证。当前不是要求再编一份MFA Pipeline，也不是重放之前138步。

**2026-10-25 20:43只读核对**：模拟器实例1，1280×720，活动首页显示**体力3、继续游戏**，没有冲突弹窗。[现场截图](../../../assets/dudu-rescue/evidence/20261025-204311/frames/screenshots--S0001_observe_01.webp)。用户说此前存档冲突已处理；本Agent没有进入局内，所以区域、补给、耐久、货币都要重新读。历史A/B/C达标不等于服务器现状。

## 先读什么

按主技能读资源边界和证据契约，再读 [模块复用方式](../../references/activity-module-reuse.md) 与 [本活动页面/分支](SKILL.md)。规则和脚本已同步到本机 `C:/Users/Administrator/.workbuddy/skills/happyfish-activity-automation`，对应素材在其同级 `assets/dudu-rescue`。仓库副本也可直接运行；任选一份，整次使用同一份的sessions，避免混账。

## 最小执行入口

在仓库副本运行：

```powershell
Set-Location 'D:/开心水族箱活动经验/happyfishagent'
$env:HAPPYFISH_ADB_DEV='127.0.0.1:16416'
$env:PYTHONIOENCODING='utf-8'
$OutputEncoding=[System.Text.UTF8Encoding]::new($false)
python happyfish-activity-automation/scripts/record_action.py --event dudu-rescue init
'{"op":"read"}' | python -u happyfish-activity-automation/scripts/activity_console.py --event dudu-rescue
```

`init`新建接手session，后续命令默认接在最新session；也可每次显式传同一 `--session <打印出的编号>`。每个JSON命令可通过stdin执行后退出，不需要维持交互终端。成功返回的 `image` 是要实际打开检查的文件，不能只读工具“成功”。

看完当前图，确认仍是本活动首页后，可由接手Agent单步点击“继续游戏”，再读后继图，辨认真正停留的区域或准备阶段。首页当前是继续已有一轮，不能当作新开一轮已经花掉另一点体力。原授权最多4体力，先前已观察用1、现剩3；不买体力。

只有真正遇到**翻找背包页**、当前免费额度清楚时，才复用：

```powershell
'{"op":"known_prepare"}' | python -u happyfish-activity-automation/scripts/activity_console.py --event dudu-rescue
```

该步骤最多4次，每次OCR额度、模板匹配、独立录制、额度恰减1才继续；只开免费包，不自动出发。已实测C区3普通+1加锁与下一准备区2普通+2加锁。当前若在检修/地图，不为测试模块退回、重开或购买背包。

## 已验证与仍需判断

| 情况 | 接手行为 |
|---|---|
| `done:true` 的免费背包步骤 | 检查最终图和库存；下一步仍由Agent决定 |
| 普通检修扳手/路线/请求补给/小游戏 | 读当页与子技能，用同一console单步操作并录制，不能裸连点 |
| `known_repair`静态模板低分 | 这是未完成的候选，既有实测只停手、零点击；不要降低阈值强行放行 |
| 指针浮层盖住飞机页 | 后台标题不代表扳手可点；看实际表盘位置，按明确浮层门禁单步处理 |
| `executed:true`但有`ocr_error`或画面不明 | 输入可能已生效，先read和看图，不重发 |
| 纸飞机宝石20、精修/一键钞票、+补给、未知成本 | 不点；体力授权不包含账号宝石或开心宝 |
| 新变体/随机鱼弹窗/再次存档冲突 | 停该动作并记分支；不套旧坐标、不直接重载存档 |
| 体力、补给、笑脸或耐久前后对不上 | 对照新图、OCR与trace，不能用旧局数值凑账 |

## 这次检验看什么

1. 能否从**实时图**确定状态，指出当前能复用哪个步骤、为什么；未命中就转回Agent判断。
2. 能否复用已有模块，同时对新状态使用相同录制入口单步探索，而非另写盲点脚本或要求MFA。
3. 能否在付费邻居、额度变动或浮层处停对，记录所见、动作、资源变化及结果；“拒绝继续”本身有时就是正确结果。
4. 收口时汇报实际消耗/收益、复用与未知分支，并将新证据归档入库。清空剩余3体力不是唯一的机制验收条件；不能为了跑满去买资源。

本次交接仅证明资料和执行入口已准备好，**尚未证明WorkBuddy已经理解或成功推进**。以它接手后产生的新trace、截图和判断为准。
