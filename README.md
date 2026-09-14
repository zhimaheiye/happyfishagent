# happyfishagent

《开心水族箱》（乐元素）**活动自动化技能包**。

用 MCP / adb 驱动 MuMu 模拟器，把「新活动 → 摸清规则 → 稳定自动刷完免费资源」这套流程固化下来。
目标是一次学会、下次直接上手，而不是一次性脚本。

## 结构

```
happyfishagent/
└── happyfish-activity-automation/       ← 主技能（umbrella，总入口）
    ├── SKILL.md                         ← 红线 + 主循环 + 子技能路由
    ├── references/
    │   └── automation-playbook.md       ← 通用技术手册（跨活动复用）
    ├── scripts/
    │   ├── grab.py                      ← adb 截图（规避中文路径坑）
    │   ├── zoom.py                      ← 局部裁剪放大
    │   ├── piece_identify.py            ← 按模板识别棋盘每格是空位还是哪块拼图
    │   └── line_shift_solver.py         ← 整行/整列循环平移棋盘的 BFS 求解器
    └── activities/                      ← 子技能：一个活动一个
        ├── romance-house/
        │   └── SKILL.md                 ← 浪漫满屋 · 约会日历
        └── daily-magic-puzzle/
            └── SKILL.md                 ← 每日魔幻拼图 · 4x4 环面滑动拼图
```

**设计约定：主技能管「怎么干」（通用流程 / 环境 / 红线），子技能管「这个活动是什么」（界面 / 规则 / 坐标）。**
新增活动 = 在 `activities/` 下新建一个目录放 `SKILL.md`，再回主技能的路由表补一行。

## 安装

把主技能目录整个复制到 WorkBuddy 的用户级技能目录：

```bash
cp -r happyfish-activity-automation ~/.workbuddy/skills/
```

（Windows：复制到 `C:\Users\<你>\.workbuddy\skills\`）

主技能会被自动加载；子技能由主技能按活动名路由读取，不需要单独安装。

## 已收录活动

| 活动 | 类型 | 状态 |
|---|---|---|
| [浪漫满屋](happyfish-activity-automation/activities/romance-house/SKILL.md) | 常驻 · 约会日历拼图（每日限次） | ✅ 已破解，10/10 全清 |
| [每日魔幻拼图](happyfish-activity-automation/activities/daily-magic-puzzle/SKILL.md) | 每日 · 4x4 环面滑动拼图（4 块） | ✅ 已破解，5 步通关，开心宝消耗 0 |
| 课间十分钟 | 限时 · 金币棋盘 | ⏳ 待整理为子技能 |

## 三条硬红线

1. **绝不点付费按钮** —— 开心宝（付费货币）相关的任何按钮一律不碰。
2. **不可逆操作先刹车** —— 花钱、删数据、对外发送，先停下来问人。
3. **每次操作前先截图确认界面** —— 禁止链式盲点，关闭类按钮尤其要看清楚。

> 界面右上角带**蓝色 ▶ 圆标 = 看广告**，带**开心宝图标/数字 = 付费**。两者都不点，宁可放弃奖励。

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
- 仅供个人学习与自动化研究使用，请遵守游戏用户协议。
