import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { REPO, WORKSPACE, ROOT } from './guard.mjs';

const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const backup = path.join(ROOT, 'backups', stamp);
fs.mkdirSync(backup, { recursive: true });
const configPath = path.join(os.homedir(), '.qoder-cn', 'settings.json');
const before = fs.readFileSync(configPath, 'utf8');
const config = JSON.parse(before.replace(/^\uFEFF/, ''));
const untouched = structuredClone(config); delete untouched.hooks; delete untouched.mcpServers?.['agent-recall'];
const proxy = path.join(REPO, 'tools/agent-recall/proxy.mjs');
if (!config.mcpServers?.['agent-recall']) throw new Error('先安装原AgentRecall');
config.mcpServers['agent-recall'].args = [proxy];
const script = fileURLToPath(new URL('./guard.mjs', import.meta.url)).replaceAll('\\', '/');
const command = `"${process.execPath.replaceAll('\\', '/')}" "${script}" hook`;
config.hooks ??= {};
for (const event of ['SessionStart','UserPromptSubmit','PostCompact','PreToolUse','Stop']) {
  config.hooks[event] ??= [];
  if (!config.hooks[event].some(g => g.hooks?.some(h => h.command === command))) config.hooks[event].push({ hooks: [{ type: 'command', command, timeout: 15 }] });
}
const afterUntouched = structuredClone(config); delete afterUntouched.hooks; delete afterUntouched.mcpServers?.['agent-recall'];
assert.deepEqual(afterUntouched, untouched);
assert.equal(fs.readFileSync(configPath, 'utf8'), before, '配置被并发修改');
fs.copyFileSync(configPath, path.join(backup, 'qoder-settings.json'));
fs.writeFileSync(configPath + '.activity-guard.tmp', JSON.stringify(config, null, 2) + '\n');
fs.renameSync(configPath + '.activity-guard.tmp', configPath);

const files = {};
function add(file) { if (fs.existsSync(file)) files[file] = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
function skills(dir) {
  if (!fs.existsSync(dir)) return;
  for (const d of fs.readdirSync(dir, { withFileTypes: true })) {
    if (d.isDirectory() && !['sessions','experiments','assets','.git','node_modules'].includes(d.name)) skills(path.join(dir, d.name));
    else if (d.isFile() && d.name === 'SKILL.md') add(path.join(dir, d.name));
  }
}
for (const relative of ['AGENTS.md','docs/activity-execution-contract.md','docs/agent-recall-integration.md','tools/activity-guard/guard.mjs','tools/activity-guard/install.mjs','tools/activity-guard/user-policy.json','tools/agent-recall/bridge.mjs','tools/agent-recall/proxy.mjs','tools/agent-recall/journal-next.mjs']) add(path.join(REPO, relative));
add(path.join(WORKSPACE, 'AGENTS.md'));
const skillDir = path.join(REPO, 'happyfish-activity-automation');
skills(skillDir);
for (const name of ['activity-module-reuse.md','activity-authorization-resource-flow.md','agent-work-modes-maa-boundary.md']) add(path.join(skillDir, 'references', name));
skills(path.join(os.homedir(), '.workbuddy', 'skills', 'happyfish-activity-automation'));
add(path.join(os.homedir(), '.workbuddy', 'skills', 'docs', 'activity-execution-contract.md'));
const baseline = path.join(ROOT, 'protected.json');
if (fs.existsSync(baseline)) fs.copyFileSync(baseline, path.join(backup, 'protected.json'));
fs.writeFileSync(baseline, JSON.stringify({ installed_at: new Date().toISOString(), files }, null, 2) + '\n');
const result = { installed_at: new Date().toISOString(), configPath, backup, protectedFiles: Object.keys(files).length, hooks: ['SessionStart','UserPromptSubmit','PostCompact','PreToolUse','Stop'], limits: ['Qoder实际定时宿主仍需下次运行检查hook日志；CLI离线测试单独记录', '同账户任意代码执行不是不可绕过的权限隔离'] };
for (const file of [path.join(os.homedir(), '.workbuddy', 'mcp.json'), path.join(os.homedir(), '.agent-recall-runtime', 'happyfish-mcp.json')]) {
  if (!fs.existsSync(file)) continue;
  const original = fs.readFileSync(file, 'utf8'), other = JSON.parse(original.replace(/^\uFEFF/, ''));
  if (!other.mcpServers?.['agent-recall']) continue;
  fs.copyFileSync(file, path.join(backup, file.includes('.workbuddy') ? 'workbuddy-mcp.json' : 'happyfish-mcp.json'));
  other.mcpServers['agent-recall'].args = [proxy];
  assert.equal(fs.readFileSync(file, 'utf8'), original, 'MCP配置并发修改');
  fs.writeFileSync(file + '.activity-guard.tmp', JSON.stringify(other, null, 2) + '\n');
  fs.renameSync(file + '.activity-guard.tmp', file);
}
fs.writeFileSync(path.join(ROOT, 'installation.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
