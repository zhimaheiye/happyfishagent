import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { pathToFileURL, fileURLToPath } from 'node:url';
const runtime = path.join(os.homedir(), '.agent-recall-runtime');
const sdk = path.join(runtime, 'node_modules/@modelcontextprotocol/sdk/dist/esm/client');
const { Client } = await import(pathToFileURL(path.join(sdk, 'index.js')).href);
const { StdioClientTransport } = await import(pathToFileURL(path.join(sdk, 'stdio.js')).href);
const proxy = fileURLToPath(new URL('./proxy.mjs', import.meta.url));
const client = new Client({ name: 'happyfish-offline-acceptance', version: '1.0.0' });
await client.connect(new StdioClientTransport({ command: process.execPath, args: [proxy], stderr: 'pipe' }));
const trajectory = '2026-11-02执行加固已落地，用户会自行发起下一次活动执行。开工按docs/activity-execution-contract.md和本轮manifest核实活动入口额度及整轮状态；喵喵屋旧暂离收工/等南瓜规定作废，重开路径与发放须现场核实。日常不得自改技能，观察写observations。任务新版正文已准备但尚未通过Qoder原生调度接口应用；本次未操作游戏，用户并发用机后只用后台方式。';
try {
  const listed = await client.listTools(); assert.deepEqual(listed.tools.map(t => t.name).sort(), ['check','recall','remember','session_end','session_start']);
  const saved = await client.callTool({ name: 'session_end', arguments: { project: 'happyfish-activities', summary: '用户授权本次离线加固：修订用户规则优先级、入口额度与整轮验收、观察与规程分离；修正喵喵屋错误技能及旧剩5证据。Qoder PreToolUse/Stop保护和兼容层已安装，WorkBuddy技能副本同步。程序回归通过；真实Qoder CLI离线Stop拦截验证通过，未触碰游戏。兼容层保留历史并修复同日session_end多段Next被取第一段的问题。', trajectory } });
  assert(!saved.isError);
} finally { await client.close(); }
// Fresh server process, rather than a cached same-client response.
const fresh = new Client({ name: 'happyfish-fresh-acceptance', version: '1.0.0' });
await fresh.connect(new StdioClientTransport({ command: process.execPath, args: [proxy], stderr: 'pipe' }));
try {
  const result = await fresh.callTool({ name: 'session_start', arguments: { project: 'happyfish-activities', mode: 'full', verbose: true } });
  assert(!result.isError);
  const content = result.content.filter(c => c.type === 'text').map(c => c.text).join('\n');
  const start = content.indexOf('\n{\n'), end = content.lastIndexOf('\n}');
  const context = JSON.parse(content.slice(start + 1, end + 2));
  // Upstream trims the final Chinese full stop; compare all substantive text.
  assert.equal(context.resume.last_trajectory.replace(/。$/, ''), trajectory.replace(/。$/, ''), '新进程未加载最新Next');
  assert(!content.includes('就收手，剩 5 点体力没用'), '旧错误数字仍作为纠正证据加载');
  const report = { at: new Date().toISOString(), fiveToolsUnchanged: true, freshProcess: true, latestTrajectoryLoaded: true, staleEvidenceRemoved: true, trajectory };
  fs.writeFileSync(path.join(runtime, 'activity-guard/proxy-verification.json'), JSON.stringify(report, null, 2)); console.log(JSON.stringify(report, null, 2));
} finally { await fresh.close(); }
