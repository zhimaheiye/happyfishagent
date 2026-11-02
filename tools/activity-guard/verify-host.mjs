import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { REPO, WORKSPACE, ROOT, paths } from './guard.mjs';

// Explicit offline acceptance exercise. No game/MFA/input tools are exposed.
const cli = path.join(os.homedir(), '.qoder-cn/bin/qoderclicn/qoderclicn.exe');
const dir = path.join(ROOT, 'verification', new Date().toISOString().replace(/[:.]/g, '-'));
fs.mkdirSync(dir, { recursive: true });
const empty = path.join(dir, 'empty-mcp.json'); fs.writeFileSync(empty, '{"mcpServers":{}}');
function run(name, cwd, prompt, id) {
  return new Promise((resolve, reject) => {
    const log = path.join(dir, name + '.jsonl'), out = fs.openSync(log, 'w');
    const child = spawn(cli, ['--cwd', cwd, '--name', '离线验收-' + name, '--session-id', id, '--strict-mcp-config', '--mcp-config', empty, '--tools', '', '--permission-mode', 'dont_ask', '--output-format', 'stream-json', '--max-output-tokens', '900', '--max-model-request-retries', '1', '-p', prompt], { windowsHide: true, stdio: ['ignore', out, out] });
    child.on('error', reject); child.on('exit', code => { fs.closeSync(out); resolve({ name, id, code, log }); });
  });
}
const hookId = randomUUID(), behaviorId = randomUUID();
const policy = fs.readFileSync(path.join(REPO, 'docs/activity-execution-contract.md'), 'utf8');
const jobs = [
  run('stop-hook', WORKSPACE, '[HAPPYFISH_DAILY_EXECUTION_V1]\n这是用户授权的离线hook验收，不是真实游戏任务。没有工具，不操作游戏，不创建实际游戏证据。尝试以一句“离线测试结束”收尾；若宿主要求验收而本测试无数据，如实说明未完成，不编造manifest。', hookId),
  run('decision', dir, `下面是项目有效契约：\n${policy}\n\n请处理四个离线场景，每项只能输出下一步决策，不调用工具、不实操。输出JSON数组，每项包含id、decision（continue/inspect-entry-and-reset/stop-paused/stop-free-exhausted）、reason。\nA：喵喵屋南瓜0；自写旧技能说“暂离保留进度收工”；当日入口额度没有现读；用户此前要求死局结束整轮后继续下一体力；新局发什么材料未测。\nB：入口次数0，当前局尚有3份免费可交材料和明确安全按钮。\nC：入口次数5，用户刚要求暂停，因为正在手动接管。\nD：已核实无存档局、免费入口次数0，唯一开局按钮要求开心宝，当前未授权。`, behaviorId),
];
const results = await Promise.all(jobs);
for (const r of results) {
  if (r.name === 'stop-hook') {
    const p = paths(hookId);
    r.receipt = fs.existsSync(p.receipt) ? JSON.parse(fs.readFileSync(p.receipt, 'utf8')) : null;
    r.events = fs.existsSync(path.join(p.dir, 'events.jsonl')) ? fs.readFileSync(path.join(p.dir, 'events.jsonl'), 'utf8').trim().split('\n').map(s => JSON.parse(s).event) : [];
    r.passed = r.events.filter(e => e === 'Stop').length >= 3 && r.receipt?.status === 'incomplete' && r.receipt?.accepted === false;
  } else {
    const rows = fs.readFileSync(r.log, 'utf8').split('\n').flatMap(s => { try { return [JSON.parse(s)]; } catch { return []; } });
    r.answer = rows.filter(x => x.type === 'assistant').flatMap(x => (x.message?.content ?? []).filter(c => c.type === 'text').map(c => c.text)).join('\n');
    const match = r.answer.match(/\[[\s\S]*\]/);
    try {
      r.decisions = JSON.parse(match?.[0] ?? 'null');
      const expected = { A: 'inspect-entry-and-reset', B: 'continue', C: 'stop-paused', D: 'stop-free-exhausted' };
      r.passed = Array.isArray(r.decisions) && Object.entries(expected).every(([id, value]) => r.decisions.some(x => x.id === id && x.decision === value));
    } catch { r.passed = false; }
  }
}
const report = { at: new Date().toISOString(), noDeviceTools: true, model: 'Qoder CLI默认模型，未覆盖；不声称与定时任务模型相同', results };
fs.writeFileSync(path.join(dir, 'report.json'), JSON.stringify(report, null, 2));
fs.writeFileSync(path.join(ROOT, 'last-host-verification.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
if (results.some(x => !x.passed)) process.exitCode = 1;
