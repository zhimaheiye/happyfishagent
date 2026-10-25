# 新活动默认：Agent 决策，复用 Maa 模块，逐步录制

2026-10-25 用户明确：Maa 指复用截图、OCR、模板识别、点击等有用模块；无需把活动编成 Pipeline 在 MFA 操作。**以后所有已授权的新活动默认采用本方式，不等用户再次说“使用混合模式”。** 此规则只确定工作方式，不扩大活动/资源授权、不新增定时任务、不代跑 MAA 已覆盖任务。

## 工作循环

1. 核对当前授权、设备和执行互斥；从真实当前页面开始。
2. 新活动先读帮助/规则、起止时间、免费额度、最终兑换边界；从第一步录制。
3. Agent 判断新状态、玩法语义、资源选择和异常。确定性识别复用 Maa OCR/模板匹配；点击/滑动通过 Recorder 记录前后图、坐标、结果、原因与资源变化。
4. 一次命令只提交一个游戏动作；看实际后继页面再决定下一步。API 成功和整屏稳定都不能代替业务验收。失败先看当前图，不自动重发。
5. 已知界面复用验证过的识别函数/规则，逐次确认当前免费次数及付费邻居；新变体交回 Agent。无需为复用模块强行生成 Pipeline。
6. 每局结束复盘 NEW/VARIANT/REPEATED/CANDIDATE_MAA/SAFETY_AI，把稳定重复判断下沉为可复用规则。只在局间验证/更新，不在一局消耗途中热改自动玩法。
7. session 保存完整原始证据；交付时将操作/分支表、关键图、OCR 与验证过的模板归档到可追踪目录。旧 flow→Pipeline 编译器仍是可选导出能力。

## 通用单步入口

```powershell
python happyfish-activity-automation/scripts/record_action.py --event <slug> init
python happyfish-activity-automation/scripts/activity_console.py --event <slug>
```

默认后端 `adb-maa-vision`：ADB 截图/点击 + MaaFramework CPU OCR，Agent 逐条输入 JSON。没有活动自动循环，不接 MFA 队列，不执行业务 Pipeline。用 `--ocr-model-dir` 选择模型目录；用 `--command '<JSON>'` 执行一次。本机 Maa MCP 试验发生原生异常且点击接口不兼容；当前入口仅提供已验证的 ADB + Maa OCR 通道，不保留未验证的 MCP 启动分支。

本机验证环境：Python3.13、maafw5.10.2、numpy2.2.6、opencv-python4.12.0.88、Pillow12.2.0。OCR模型默认只读引用 `D:/happyfishgame/assets/resource/model/ocr`，其它机器必须传实际目录；不把模型或游戏开发仓库当可修改对象。

```json
{"op":"read"}
{"op":"tap_text","expect":"出发救援","safety":"confirmed_safe","reason":"已核实当前免费体力且用户已授权","read_after":true}
{"op":"tap","point":[100,200],"expect":"页面唯一特征","safety":"readonly","reason":"阅读帮助","read_after":true}
{"op":"swipe","points":[[800,500],[400,500]],"duration":700,"safety":"nav","reason":"查看下一页"}
```

`expect` 是 OCR 原文字面子串且必须唯一命中；同名控件可用 `roi`（x/y/宽/高）缩小范围。`tap_text` 点击实时识别框中心；普通 `tap` 的 expect 只证明页面特征，不自动证明给定落点安全。safety/reason 仍由 Agent 自报，不是自动经济语义拦截。

除 Recorder flow/trace/截图/差分，还留 `decisions.jsonl` 和 `ocr/`，写明实际后端。Maa OCR 只负责图像分析；不能把 Agent 每步决策写成“纯 Maa 自动完成”。

每次 Maa OCR 会在 `vision/` 保存唯一时间戳的源图及 JSON，`read_after` 的 `image` 指向这张真实识别图，`recorder_image` 保留更早的动作后图。`vision/frame.png` 只是会覆盖的预览，不能单独当交付证据。动作已执行但后续 OCR 失败时，仍返回 `executed:true` 并附 `ocr_error`，必须先读图，不能重发动作。

已知检修浮层出现时，后台标题命中不能放行。Agent 看清表盘位置后，用 `modal_expect:"在指针进入绿色区域时点击"` 明确操作浮层。存档冲突默认拒绝输入；只有用户明确同意加载服务器存档，才可发 `tap_text/expect:确定/server_reload_authorized:true`。这些标志仍由调用 Agent 负责绑定真实授权，不是自动理解用户授权的经济闸门。

录制结束后可归档：

```powershell
python happyfish-activity-automation/scripts/archive_activity_session.py <session目录> assets/<slug>/evidence/<session编号>
```

目标必须是新目录。工具去除原生日志，PNG 转无损 WebP 并校验每个像素，保留源文件哈希/映射，重写图片链接，生成 `actions.md`。活动子技能仍需补充页面语义、未点控件、分支、资源账和未验证范围。

## 本机已取证的接口限制

- Maa MCP 默认 MuMu 专用截图曾触发原生 OpenCV 分配异常，不为恢复此通道反复重连/重启模拟器。
- Maa MCP click 使用 touch_down/up，AdbShell-only 不支持此接口，返回失败后必须先检查画面。
- 当前 Python 包缺 MaaDbgControlUnit 原生库；默认识别后端采用普通 ADB 控制器初始化、明确 Encode 截图配置、CPU 推理，并把 Recorder 截图显式交给 post_recognition。
- Tasker 未初始化会返回无 TaskDetail；这属于调用失败，不能当成“目标不存在”。

## 当前案例

2026-10-25「嘎嘎队立大功」已经实机使用 Maa OCR 唯一命中门禁、识别框中心点击和 Recorder 留证。`known_prepare` 是该活动专用的有界步骤：Maa OCR 免费额度 + OpenCV 未开包模板，最多4次；每次独立录制，并要求额度恰好减1。C区3普通+1加锁、D区2普通+2加锁均走过；D区新文案曾安全停手，经修正后继续。**它不是其它新活动可直接套用的玩法循环**。

`known_repair` 仅是候选模块：静态扳手模板实测因旋转未命中，零点击交回 Agent，不能标为已自动检修。已增加浮层排除，但新门禁不等于完整识别状态机通过。当前整轮探索仍由 Agent 判断路线、小游戏、费用和异常；未实现无人值守自动玩完新活动。完整玩法、资源、分支和验证范围见 [活动子技能](../activities/dudu-rescue/SKILL.md)。
