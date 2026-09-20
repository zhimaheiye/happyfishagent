# happyfishagent

《开心水族箱》（乐元素）**活动自动化技能包**。

用 MCP / adb 驱动 MuMu 模拟器，把「新活动 → 摸清规则 → 稳定自动刷完免费资源」这套流程固化下来。
目标是一次学会、下次直接上手，而不是一次性脚本。

## 结构

```
happyfishagent/
├── assets/                              ← 二进制素材库（供其它项目取用，**不随技能安装**）
│   ├── daily-magic-puzzle/              ← 每日魔幻拼图：拼块模板 / 导航图 / 参考帧
│   ├── mijing-gate/                     ← 秘境之门：入口导航图 / 参考帧 / 采集样本
│   └── class-break-10min/               ← 课间十分钟：进·出导航图 / 三大副玩法参考帧 / 付费陷阱帧
└── happyfish-activity-automation/       ← 主技能（umbrella，总入口）
    ├── SKILL.md                         ← 红线 + 主循环 + 进/出导航 + 子技能路由
    ├── references/
    │   └── automation-playbook.md       ← 通用技术手册（跨活动复用）
    ├── scripts/
    │   ├── grab.py                      ← adb 截图（规避中文路径坑）
    │   ├── zoom.py                      ← 局部裁剪放大
    │   ├── burst_tap.py                 ← 连拍 + 定时点击，抓一闪而过的文字
    │   ├── frame_diff.py                ← 帧间差异，从连拍里定位剧变帧
    │   ├── crop_scan.py                 ← 批量裁同区域挑最清晰帧
    │   ├── sweep_move.py                ← 边走边拍，定位「画面停住」
    │   ├── piece_identify.py            ← 按模板识别棋盘每格是空位还是哪块拼图
    │   ├── piece_numbering.py           ← 用「未开始帧」反推正确排布，编号并导出 MAA 模板
    │   ├── line_shift_solver.py         ← 整行/整列循环平移棋盘的 BFS 求解器
    │   ├── detect_pool.py               ← 卡池槽位测位（浪漫满屋右侧 3 槽）
    │   └── diff_cells.py                ← 两帧逐格差分，精确列出哪几格真的变了
    └── activities/                      ← 子技能：一个活动一个
        ├── romance-house/
        │   └── SKILL.md                 ← 浪漫满屋 · 约会日历
        ├── daily-magic-puzzle/
        │   └── SKILL.md                 ← 每日魔幻拼图 · 4x4 环面滑动拼图
        ├── tailor-shop/
        │   └── SKILL.md                 ← 巧手裁缝铺 · 精选布料 / 细密针脚
        ├── fish-baby-hatch/
        │   └── SKILL.md                 ← 鱼宝乐园 · 养鱼宝宝
        ├── mijing-gate/
        │   └── SKILL.md                 ← 秘境之门 · 送鱼任务
        └── class-break-10min/
            └── SKILL.md                 ← 课间十分钟 · 课桌比拼 / 课间休息 / 操场锻炼
```

**设计约定：主技能管「怎么干」（通用流程 / 环境 / 红线），子技能管「这个活动是什么」（界面 / 规则 / 坐标 / 进·出导航）。**
新增活动 = 在 `activities/` 下新建一个目录放 `SKILL.md`，再回主技能的路由表补一行。

## 安装

把主技能目录整个复制到 WorkBuddy 的用户级技能目录：

```bash
cp -r happyfish-activity-automation ~/.workbuddy/skills/
```

（Windows：复制到 `C:\Users\<你>\.workbuddy\skills\`）

主技能会被自动加载；子技能由主技能按活动名路由读取，不需要单独安装。

## 更新与同步（改完技能文件后的固定收尾）

技能文件有**两份生效副本**：本仓库 + WorkBuddy 用户级技能目录 `~/.workbuddy/skills/`（WorkBuddy 实际加载的是后者）。只改一份，下次加载的还是旧经验。改完任何技能文件后按这个闭环收尾，缺一不可：

1. **commit + push** 本仓库；
2. **校验远程已到位**：`git ls-remote origin refs/heads/main` 确认指向新 commit —— push 完不校验等于没 push（09-17 出现过一轮「本地已改、技能目录已同步、仓库却还没 push」的半截状态）；
3. **同步回技能目录**：`cp -r happyfish-activity-automation ~/.workbuddy/skills/`（本机 Windows 实际用 robocopy）；
4. **逐一校验一致**：改过的文件（最好全量）用 diff / md5 对比仓库与技能目录，确认两边真是同一版。

> 实践记录：09-16 收尾「4 个文件逐一校验一致，远程 `refs/heads/main` 已确认指向 `673a65f`」；09-18 全量核对 21/21 文件 md5 一致。

## 已收录活动

| 活动 | 类型 | 状态 |
|---|---|---|
| [浪漫满屋](happyfish-activity-automation/activities/romance-house/SKILL.md) | 常驻 · 约会日历拼图（每日限次） | ✅ **全流程自动化**（珊瑚→气泡→大厅→约会→通关→X 退出），三轮均 10/10，开心宝消耗 0 |
| [每日魔幻拼图](happyfish-activity-automation/activities/daily-magic-puzzle/SKILL.md) | 每日 · 环面滑动拼图（2x2/3x3/4x4 三档，棋盘固定 4×4） | ✅ **全流程自动化**（主界面→游乐园→魔方→选难度→拼完），开心宝消耗 0；每天 4:00 刷新；通关即停不代领 |
| [鱼宝乐园（养鱼宝宝）](happyfish-activity-automation/activities/fish-baby-hatch/SKILL.md) | 常驻 · 养成（喂食+玩耍+喂奶三步） | ✅ 已收录，含入口导航与三步流程 |
| [巧手裁缝铺](happyfish-activity-automation/activities/tailor-shop/SKILL.md) | 限时（2026.09.18-09.28）· 剪布料 / 纽扣连线 | ✅ 已收录，含主活动与副活动玩法、⭐5 个付费陷阱 |
| [秘境之门（送鱼任务）](happyfish-activity-automation/activities/mijing-gate/SKILL.md) | 常驻 · 送鱼苗换魔力水晶（3 个订单槽） | ✅ 已收录（玩法 + 入口导航 + 全坐标 + 红线）；含只读采集器 |
| 深海寻鱼（深海地图） | 分层迷宫 · 潜艇下潜 | ⏳ 待整理为子技能（档案见 `活动档案/深海地图.md`） |
| [课间十分钟](happyfish-activity-automation/activities/class-break-10min/SKILL.md) | 限时（2026.09.11-09.21）· 课桌比拼下棋 / 课间休息翻望远镜 / 操场锻炼跑圈 | ✅ 已收录（主鱼缸直接入口 + 大厅兜底入口 + 退出回上级、9×5 棋盘公式、⭐紫笔收币四邻格自动补✗、全付费陷阱清单）；⚠️ 「纸币」= 开心宝 |

## 素材库（`assets/`）

可远程获取的**二进制素材**，给需要拼块模板 / 参考帧的其它项目用。

| 目录 | 内容 |
|---|---|
| [`assets/daily-magic-puzzle/`](assets/daily-magic-puzzle/README.md) | 每日魔幻拼图：5 套拼块模板（蛋糕鱼 / 炮弹鱼(绿) / 紫衣锦鲤 / 巧克力鱼(绿) / 首日未定名）、进·出导航图、参考帧 |
| [`assets/mijing-gate/`](assets/mijing-gate/README.md) | 秘境之门：进·出导航图（宝箱把手 / 紫门）、活动界面与各弹窗参考帧、锁定态订单、采集样本与 `采集记录.csv` |
| [`assets/class-break-10min/`](assets/class-break-10min/README.md) | 课间十分钟：进·出导航图（主鱼缸「课间时刻」/ 大厅卡片）、课桌比拼棋盘、三大副玩法与领奖处参考帧、5 张付费陷阱帧 |

**MAA 直接用**：模板为 **138×138 RGB PNG（无 alpha）**，按正确排布「左→右、上→下」编号 1~4；
要求同分辨率 **1280×720**，`roi` 建议 `[346,82,920,654]`，阈值 0.8 起。详见该目录 `README.md`。

> 素材放在技能包外，所以 `cp -r happyfish-activity-automation ~/.workbuddy/skills/` 安装技能时**不会**连带搬运。

## 三条硬红线

1. **绝不点付费按钮** —— 开心宝（付费货币）相关的任何按钮一律不碰。⚠️ 形态不是判据，新出现的浮空框/道具一律先当付费；「修复 / 补充 / 续命 / 复活 / 加速」默认全是开心宝；**货币别名要核实**（如课间休息把开心宝叫「纸币」）。
2. **不可逆操作先刹车** —— 花钱、删数据、对外发送，先停下来问人。
3. **每次操作前先截图确认界面** —— 禁止链式盲点，关闭类按钮尤其要看清楚。
   - 唯一例外：**已经实测验证过的固定导航路径**可以「盲连击」（一条命令串起，中途不截图），走完立刻截图验收。

> 界面右上角带**蓝色 ▶ 圆标 = 看广告**，带**开心宝图标/数字 = 付费**。两者都不点，宁可放弃奖励。

## 盲连击与进 / 出导航

**入口和出口都是「坐标知识」**，和解法同等重要：

- 每日魔幻拼图：主界面左下「游乐园」(58,505) → 「魔方」(515,452) → 2x2 卡 (469,335)
- 浪漫满屋：主鱼缸右下「珊瑚」(905,593) → 气泡中间那个 (910,417) → 大厅「一起约会吧！」(1069,581) → 通关确定 (640,440) → 右上角心形 X (1199,52) 直接回鱼缸

```bash
# 盲连击示例（间隔 0.5s，中途不截图）
adb shell "input tap 905 593; sleep 0.5; input tap 910 417"
```

## 到达终点即收手（不代选、不代领）

玩法跑完（拼好 / 清空 / 通关）后**立刻停手**，把界面交给用户：**奖励多选一和「领取」按钮一律不点**——不同人偏好不同（金币 / 经验 / 材料），脚本不替玩家做选择。候选奖励与坐标只记录在子技能里供人工参考。（纯提示类弹窗，如浪漫满屋通关的「确定」，可以直接点掉。）

## 环境

| 项目 | 值 |
|---|---|
| 模拟器 | MuMu Player，分辨率 1280×720 |
| adb | MuMu 自带（见 `references/automation-playbook.md`） |
| 设备 | `127.0.0.1:7555` |
| 通道 | maa-mcp 首选，adb 兜底 |

## 说明

- 全部操作基于屏幕坐标与图像识别，**不修改游戏文件、不注入、不碰网络协议**。
- 判读界面一律放大 2~3 倍核对，不凭缩略图猜。
- ⚠️ 截图原图是 1280×720，但对话里的预览被缩到 1080×608 —— **目测坐标必须 ×1.185**。更稳的是直接用像素连通域/投影扫描求中心。
- 仅供个人学习与自动化研究使用，请遵守游戏用户协议。
