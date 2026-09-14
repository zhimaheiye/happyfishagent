# 通用自动化流程（Windows + MuMu + maa-mcp）

跟具体活动无关，跨活动复用。

## 一、环境

| 项目 | 值 |
|---|---|
| 模拟器 | MuMu Player，分辨率 **1280×720** |
| adb | `D:\MuMuPlayer\nx_device\15.0\shell\adb.exe`（MuMu 自带） |
| 设备 | `127.0.0.1:7555` |
| 截图中转目录 | `C:\Users\Administrator\.workbuddy\_vgtmp`（**必须是 ASCII 路径**） |
| Python（带 Pillow 的隔离 venv） | `C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe` |

**坑**：
- ⚠️ adb **不认中文路径** → pull 目标必须是纯 ASCII 目录。
- ⚠️ adb daemon 可能每次调用重启 → `connect` 与后续操作必须写在**同一条命令**里。
- ⚠️ 截图疑似缓存帧时，**换一个区域**重截一次即可确认。

## 二、双通道连接

### 通道 1：maa-mcp（首选）

```
find_adb_device_list()                      # 返回设备名，形如 127.0.0.1:7555-D:/MuMuPlayer/nx_main/adb.exe
connect_adb_device(device_name=...)         # 返回 controller_id
screencap(controller_id)                    # 全屏截图；带 region=[x,y,w,h] 可局部截
ocr(controller_id)                          # 全屏文字 + 坐标
swipe(controller_id, start_x, start_y, end_x, end_y, duration=1500)
click(controller_id, x, y)
wait(controller_id, ms)
```

批量加载工具：`ToolSearch(tool_names=["mcp__maa-mcp__screencap", "mcp__maa-mcp__swipe", ...])`，再用 `DeferExecuteTool` 调用。

### 通道 2：adb 兜底（MCP 返回空 / `false` / 没注册时）

```bash
ADB="D:/MuMuPlayer/nx_device/15.0/shell/adb.exe"; DEV="127.0.0.1:7555"
"$ADB" connect $DEV && "$ADB" -s $DEV shell "screencap -p /sdcard/_s.png" \
  && "$ADB" -s $DEV pull /sdcard/_s.png "C:/Users/Administrator/.workbuddy/_vgtmp/s.png"

# 拖拽（慢拖 1500ms）
"$ADB" -s $DEV shell "input swipe 1183 268 427 409 1500"
# 点击
"$ADB" -s $DEV shell "input tap 640 410"
```

> 实测教训：maa-mcp 的 `screencap` 会间歇性返回空、`swipe` 会返回 `false`。**一旦出现，立刻切 adb 兜底，不要反复重试 MCP。**

## 三、读界面纪律

1. 全屏缩略图**只用来定位**；判读图标、角标、文字**必须放大 2~3 倍**（`scripts/zoom.py`）。
2. 中文按钮、小图标（尤其**付费/广告角标**）放大后再下结论。
3. 棋盘类玩法：用像素法找网格线（纯色行列扫描取峰值），推出行列数与格心公式，比目测准。
4. OCR 拿文字坐标用于校核，不代替看图。
5. **悬停类信息无法验证** → 不写进档案。

## 四、操作纪律

- **一次一个动作**：拖拽/点击后立刻截图，确认有变化再继续。
- 关闭类按钮（X / 取消）点之前重新截图确认。
- 拖拽不生效 → 先查起点是否压在卡片上（放大重算），再查落点是否落在空格。
- 计数类验证最可靠：完成日程 N/10、体力、货币数字，**变化即证据**。

## 五、红线

| 标识 | 含义 | 处置 |
|---|---|---|
| 蓝色 ▶ 圆标 | 看广告 | 本机不可用，**不点** |
| 开心宝图标 / 数字 | 付费货币 | **绝不点**，宁可放弃该奖励 |
| X / 取消 | 关闭弹窗 | 点前必须重新截图确认 |

拿不准含义的按钮 → 先放大读文字；读不清就停下来问人。
