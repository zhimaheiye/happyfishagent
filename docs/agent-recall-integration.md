# AgentRecall 本机接入（2026-10-27）

**2026-11-02 加固**：日常活动先读 [执行契约](activity-execution-contract.md)。Qoder增加PreToolUse规则防误写及Stop收工验收，原记忆加载钩子保留。`tools/activity-guard/install.mjs`安装/更新本机基线，执行任务不得调用安装器；新发现进入observations，不当轮改有效技能。

MCP入口现经 `tools/agent-recall/proxy.mjs` 转发原5个工具，版本仍3.5.2。兼容层修复同日多次session_end追加多个`## Next`而上游恢复取第一段的问题：旧段改成历史标题，正文保留并先备份；最新段仍叫`## Next`。桥接同样处理。此处不是上游升级，也没有改变工具schema；后续升级须重新验证是否仍需兼容层。

选用项目：[Goldentrii/AgentRecall-X](https://github.com/Goldentrii/AgentRecall-X)。本机固定安装 `agent-recall-mcp@3.5.2` 与 `agent-recall-cli@3.5.2`，不需要克隆源码，不在上游源码中填写记忆。

## 目录与客户端

- 程序：`C:\Users\Administrator\.agent-recall-runtime\node_modules\`；保留package-lock固定依赖。
- 记忆根：`C:\Users\Administrator\.agent-recall\`；本项目固定 `projects\happyfish-activities\`，包含纠正台账、知识房间、日志。
- Qoder：`C:\Users\Administrator\.qoder-cn\settings.json` 中新增 `agent-recall` stdio MCP；原有MaaMCP和其它服务器保留。
- WorkBuddy：现有 `C:\Users\Administrator\.workbuddy\mcp.json` 同步新增同一MCP，复用同一记忆目录；这里没有声称安装其专用自动钩子。
- 配置备份和本次安装清单：`.agent-recall-runtime\happyfish-installation.json`，其中记录实际备份目录；不将含其它服务凭据的配置备份提交仓库。

MCP是让Agent读写记忆的接口；文件目录是存储；工作区规则和生命周期钩子负责促使Agent主动加载。记忆仍需核对来源与范围，不能覆盖当前用户指令、系统规则或资源边界。

## 自动加载与压缩

Qoder用户级hooks新增 `SessionStart`、`UserPromptSubmit`、`PreCompact`、`PostCompact`，调用本仓库 `tools/agent-recall/bridge.mjs hook`。脚本只在本工作区及其子目录生效；其它项目无输出。启动、用户输入、压缩后从纠正台账直接重新读取完整规则和证据，避免只靠模型主动检索；压缩前留事件检查点。用户输入经凭据脱敏后暂存在 `integration/qoder/input-inbox.jsonl`，仅为未审核来源，不会自动提升成规则；不自动把助手输出当事实。

运行日志：`C:\Users\Administrator\.agent-recall\projects\happyfish-activities\integration\qoder\hooks.jsonl`。配置文件有记录不等于应用已加载：以实际hook日志和任务回读为准。原有运行中的会话可能需要新会话/重载；不擅自退出正在执行的客户端。参考：[Qoder Hooks](https://docs.qoder.com/qoder/hooks)。

## 后续Agent必须执行

1. 开工、继续工作或压缩后：`session_start(project="happyfish-activities",mode="full",verbose=true)`；再读工作区入口和目标子技能。只收到自动hook时也要核对适用范围。
2. 用户明确纠正：`check` 的 `human_correction` 必须为 `{rule,why,applies_when}`，带中文原话、证据和范围；`rule`完整且不超过100字符。确认激活并读回；普通`remember`不是永久纠正接口，不能传不存在的`type`参数。
3. 普通知识：`remember(content,context="decision",project="happyfish-activities")`。进度写日期和证据，不当永久授权。检索只给摘要时继续读源文件正文，不把脚本读全文但只打印切片当作自己已读全文。
4. 收尾：`session_end`保存真实结果、未处理项与下一步；有免费玩法未完成且无有效阻塞，不报全部完成。记忆遵守情况只能依据实际执行证据记录，不能因为读到规则就标记已遵守。
5. 仓库规范、截图、流程仍是可审阅的源资料；AgentRecall保存紧凑规则和可追溯索引，避免复制所有流水或另造冲突知识库。

## 当前会话无MCP时的备用入口

`node "D:/开心水族箱活动经验/happyfishagent/tools/agent-recall/bridge.mjs" list`

将参数写入UTF-8 JSON文件，再运行：

`node "D:/开心水族箱活动经验/happyfishagent/tools/agent-recall/bridge.mjs" call session_start "D:/开心水族箱活动经验/tmp/memory-input.json"`

示例参数：`{"project":"happyfish-activities","mode":"full","verbose":true}`。不能因旧会话工具列表未刷新就绕过记忆或要求用户人工整理。

## 验证范围

`tools/agent-recall/verify.mjs`验证真实MCP握手、工具schema、7条纠正激活、中文检索、全新进程持久化、启动/压缩后/用户输入hook模拟和项目隔离。结果位于记忆项目 `integration/installation-verification.json`。后续真实Qoder任务的启动/用户输入hook需另以日志核验；没有人为制造整次长对话压缩，不声称该端到端链已验证。

首轮实际Qoder会话为 `3c103046-1c54-42bc-bb5a-b1c227591645`（“项目知识整理（AgentRecall）”）。已在其hook日志核对到真实 `SessionStart` 和 `UserPromptSubmit`，初始化事件确认仅加载文件读写工具与agent-recall MCP，没有MaaMCP、Bash或其它设备工具。日志在 `.agent-recall-runtime/qoder-knowledge-migration.jsonl`；整理结果见 `docs/agent-recall-migration-report.md`。`tools/agent-recall/verify-migration.mjs`在独立新进程中核对五个场景的规则检索及实际工具范围，结果另存 `integration/migration-verification.json`。

完整整理提示词见 [agent-recall-bootstrap-prompt.md](agent-recall-bootstrap-prompt.md)，最终有效结果以 [agent-recall-acceptance.md](agent-recall-acceptance.md) 为准。本次离线安装与整理不操作模拟器、MFA及实际定时任务。
