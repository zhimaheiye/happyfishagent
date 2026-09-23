# happyfishagent

《开心水族箱》（乐元素）**活动自动化知识库与素材库**。

把「新活动 → 摸清规则 → 记录界面坐标与素材 → 供自动化工具调用」这套流程固化下来。
目标是把每个活动的玩法、入口坐标、退出路径、付费陷阱和参考帧都记录清楚，供 MaaFramework、MCP 工具或其他自动化项目直接取用。

## 结构

```
happyfishagent/
├── assets/                              ← 二进制素材库（供其它项目直接取用）
│   ├── daily-magic-puzzle/              ← 每日魔幻拼图：拼块模板 / 导航图 / 参考帧
│   ├── mijing-gate/                     ← 秘境之门：入口导航图 / 参考帧 / 采集样本
│   ├── class-break-10min/               ← 课间十分钟：进·出导航图 / 三大副玩法参考帧 / 付费陷阱帧
│   └── sea-dive/                        ← 深海寻鱼：地图攻略图 / 导航参考帧
└── happyfish-activity-automation/       ← 活动文档与工具脚本
    ├── SKILL.md                         ← 通用红线 + 主循环 + 进/出导航 + 活动路由
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
    │   ├── calib_calendar.py            ← 约会日历棋盘行 / 列锚点标定
    │   ├── cell_xy.py                   ← 格号 ↔ 屏幕坐标互算
    │   ├── count_empty.py               ← 数空格数 E + 空格格号清单 + 各空格的 4 邻格号
    │   ├── count_icons.py               ← 逐格数「图标个数」
    │   ├── element_chart.py             ← 把需求列 + 盘面元素裁成带中文标注的并排对照图
    │   └── diff_cells.py                ← 两帧逐格差分，精确列出哪几格真的变了
    └── activities/                      ← 活动文档：一个活动一个目录
        ├── romance-house/
        │   └── SKILL.md                 ← 浪漫满屋 · 约会日历
        ├── daily-magic-puzzle/
        │   └── SKILL.md                 ← 每日魔幻拼图 · 4x4 环面滑动拼图
        ├── tailor-shop/
        │   └── SKILL.md                 ← 巧手裁缝铺 · 精选布料 / 细密针脚
        ├── mijing-gate/
        │   └── SKILL.md                 ← 秘境之门 · 送鱼任务
        ├── sea-dive/
        │   └── SKILL.md                 ← 深海寻鱼 · 潜艇下潜
        ├── sea-otter/
        │   └── SKILL.md                 ← 海獭摸宝 · 指定宝石采集
        └── class-break-10min/
            └── SKILL.md                 ← 课间十分钟 · 课桌比拼 / 课间休息 / 操场锻炼
```

**设计约定：主文档管「怎么干」（通用流程 / 环境 / 红线），各活动文档管「这个活动是什么」（界面 / 规则 / 坐标 / 进·出导航）。**
新增活动 = 在 `activities/` 下新建一个目录放说明文档，再回主路由表补一行。

## 已收录活动

| 活动 | 类型 | 状态 |
|---|---|---|
| [浪漫满屋](happyfish-activity-automation/activities/romance-house/SKILL.md) | 常驻 · 约会日历拼图（每日限次） | ✅ 全流程文档化（珊瑚→气泡→大厅→约会→通关→X 退出），开心宝消耗 0 |
| [每日魔幻拼图](happyfish-activity-automation/activities/daily-magic-puzzle/SKILL.md) | 每日 · 环面滑动拼图（2x2/3x3/4x4 三档） | ✅ 全流程文档化（主界面→游乐园→魔方→选难度→拼完），开心宝消耗 0；每天 4:00 刷新 |
| [巧手裁缝铺](happyfish-activity-automation/activities/tailor-shop/SKILL.md) | 限时 · 剪布料 / 纽扣连线 | ✅ 已收录，含主活动与副活动玩法、付费陷阱清单 |
| [秘境之门（送鱼任务）](happyfish-activity-automation/activities/mijing-gate/SKILL.md) | 常驻 · 送鱼苗换魔力水晶（3 个订单槽） | ✅ 已收录（玩法 + 入口导航 + 全坐标 + 红线） |
| [深海寻鱼](happyfish-activity-automation/activities/sea-dive/SKILL.md) | 分层迷宫 · 潜艇下潜 | ✅ 已收录（地图攻略 + 导航坐标 + 免费/付费态判断） |
| [海獭摸宝](happyfish-activity-automation/activities/sea-otter/SKILL.md) | 好友互访 · 指定宝石采集 | ✅ 已收录（状态机规则 + 边界门禁） |
| [课间十分钟](happyfish-activity-automation/activities/class-break-10min/SKILL.md) | 限时 · 课桌比拼 / 课间休息 / 操场锻炼 | ✅ 已收录（入口 + 退出 + 棋盘公式 + 付费陷阱） |

## 素材库（`assets/`）

可直接取用的**二进制素材**，给需要拼块模板 / 参考帧的自动化项目用。

| 目录 | 内容 |
|---|---|
| [`assets/daily-magic-puzzle/`](assets/daily-magic-puzzle/README.md) | 每日魔幻拼图：5 套拼块模板、进·出导航图、参考帧 |
| [`assets/mijing-gate/`](assets/mijing-gate/README.md) | 秘境之门：进·出导航图、活动界面与各弹窗参考帧、锁定态订单、采集样本 |
| [`assets/class-break-10min/`](assets/class-break-10min/README.md) | 课间十分钟：进·出导航图、棋盘参考帧、三大副玩法与领奖处参考帧、付费陷阱帧 |
| [`assets/sea-dive/`](assets/sea-dive/) | 深海寻鱼：分层地图攻略图、导航参考帧 |

**MAA 模板规格**：模板为 **138×138 RGB PNG（无 alpha）**，按正确排布「左→右、上→下」编号 1~4；
要求同分辨率 **1280×720**，`roi` 建议 `[346,82,920,654]`，阈值 0.8 起。详见各目录 `README.md`。

## 三条硬红线

1. **绝不点付费按钮** —— 开心宝（付费货币）相关的任何按钮一律不碰。⚠️ 形态不是判据，新出现的浮空框/道具一律先当付费；「修复 / 补充 / 续命 / 复活 / 加速」默认全是开心宝；**货币别名要核实**（如课间休息把开心宝叫「纸币」）。
2. **不可逆操作先刹车** —— 花钱、删数据、对外发送，先停下来确认。
3. **每次操作前先截图确认界面** —— 禁止链式盲点，关闭类按钮尤其要看清楚。
   - 唯一例外：**已经实测验证过的固定导航路径**可以「盲连击」（一条命令串起，中途不截图），走完立刻截图验收。

> 界面右上角带**蓝色 ▶ 圆标 = 看广告**，带**开心宝图标/数字 = 付费**。两者都不点，宁可放弃奖励。

## 盲连击与进 / 出导航

**入口和出口都是「坐标知识」**，和解法同等重要：

- 每日魔幻拼图：主界面左下「游乐园」(58,505) → 「魔方」(515,452) → 2x2 卡 (469,335)
- 浪漫满屋：主鱼缸右下「珊瑚」(905,593) → 气泡中间那个 (910,417) → 大厅「一起约会吧！」(1069,564) → 通关确定 (640,440) → 右上角心形 X (1199,52) 直接回鱼缸

```bash
# 盲连击示例（间隔 0.5s，中途不截图）
adb shell "input tap 905 593; sleep 0.5; input tap 910 417"
```

## 到达终点即收手（不代选、不代领）

玩法跑完（拼好 / 清空 / 通关）后**立刻停手**，把界面交给用户：**奖励多选一和「领取」按钮一律不点**——不同人偏好不同（金币 / 经验 / 材料），脚本不替玩家做选择。候选奖励与坐标只记录在活动文档里供人工参考。（纯提示类弹窗，如浪漫满屋通关的「确定」，可以直接点掉。）

## 环境

| 项目 | 值 |
|---|---|
| 模拟器 | MuMu Player，分辨率 1280×720 |
| adb | MuMu 自带 |
| 设备 | 实例 n ↔ `127.0.0.1:(16384 + 32n)`；**开心水族箱 = 实例 1 → `127.0.0.1:16416`**（端口动态读，别硬编码） |
| 通道 | MCP 工具首选，adb 兜底 |

## 说明

- 全部操作基于屏幕坐标与图像识别，**不修改游戏文件、不注入、不碰网络协议**。
- 判读界面一律放大 2~3 倍核对，不凭缩略图猜。
- ⚠️ 截图原图是 1280×720，但对话预览常被缩到更小尺寸 —— **目测坐标必须按比例换算**。更稳的是直接用像素连通域/投影扫描求中心。
- 仅供个人学习与自动化研究使用，请遵守游戏用户协议。

## 关联项目

- **[MaaHappyFish](https://github.com/zhimaheiye/MaaHappyFish)**：基于 MaaFramework 的开心水族箱挂机小助手，本仓库的活动素材与坐标已集成到该项目中。
