import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { validate, init, paths, handleHook, preflight } from './guard.mjs';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'happyfish-guard-test-'));
// Real 1x1 PNG, isolated fixtures only. No device interaction.
const shot = path.join(dir, 'current.png');
fs.writeFileSync(shot, Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/bWQAAAAASUVORK5CYII=', 'base64'));
const time = new Date().toISOString(), started_at = new Date(Date.now() - 1000).toISOString();
const context = { run_id: 'test-run', started_at };
const ev = () => ({ observed_at: time, evidence: [shot] });
function good() { return { version: 1, run_id: 'test-run', inventory: { ...ev(), activities: [{ id: 'cat-house', included: true, reason: '免费活动' }] }, activities: [{ id: 'cat-house', entry: { ...ev(), scope: 'activity-entry', resource: '本活动体力', balance: 0, cost: 1 }, round: { ...ev(), state: 'ended' }, outcome: 'exhausted' }] }; }
test('实际事故：关内南瓜0，但入口仍5、仅暂离，不得通过', () => {
  const m = good(); m.activities[0].entry.balance = 5; m.activities[0].round.state = 'stalled'; m.activities[0].pumpkins = 0;
  const r = validate(m, context); assert.equal(r.accepted, false); assert(r.errors.some(x => x.includes('仍可开局'))); assert(r.errors.some(x => x.includes('暂时离开')));
});
test('没有读取入口，不能拿缺失值当0', () => { const m = good(); delete m.activities[0].entry; assert.equal(validate(m, context).accepted, false); });
test('主缸体力不是本活动入口额度', () => { const m = good(); m.activities[0].entry.scope = 'main-tank'; assert.equal(validate(m, context).accepted, false); });
test('入口额度0仍有活局时不能收工', () => { const m = good(); m.activities[0].round.state = 'active'; assert.equal(validate(m, context).accepted, false); });
test('已耗尽且结束整轮可以完成', () => assert.equal(validate(good(), context).status, 'completed'));
test('已用尽免费局后仅剩付费续局，不应留成blocked欠账', () => { const m = good(); m.activities[0].outcome = 'blocked'; assert(validate(m, context).errors.some(x => x.includes('付费续局不属于'))); });
test('排除也需要证据；纳入活动不得丢失', () => {
  const m = good(); m.inventory.activities.push({ id: 'other', included: true, reason: '有效期内' }); assert.equal(validate(m, context).accepted, false);
  assert.equal(validate(good(), { ...context, expected_ids: ['old-known'] }).accepted, false);
});
test('旧读数、文档伪装截图、缺失截图、旧轮次都拒绝', () => {
  const m = good(); m.activities[0].entry.observed_at = '2026-10-31T04:00:00+08:00'; assert.equal(validate(m, context).accepted, false);
  m.activities[0].entry = { ...good().activities[0].entry, evidence: [path.join(dir, 'SKILL.md')] }; fs.writeFileSync(m.activities[0].entry.evidence[0], '已打空'); assert.equal(validate(m, context).accepted, false);
  m.activities[0].entry.evidence = [path.join(dir, 'missing.png')]; assert.equal(validate(m, context).accepted, false);
  assert.equal(validate(good(), { ...context, run_id: 'next-day' }).accepted, false);
});
test('只说南瓜0是阻塞不够；三项现场核实后仍只算未完成', () => {
  const m = good(), a = m.activities[0]; a.entry.balance = 5; a.round.state = 'stalled'; a.outcome = 'blocked'; a.block = { kind: 'unsafe-reset', description: '南瓜0，技能说停手' };
  assert.equal(validate(m, context).accepted, false);
  a.block.description = '检查帮助、退出弹窗与入口后仍不能确认安全结束路径'; a.block.checks = ['entry-inspection','round-end-inspection','new-round-inspection'].map(step => ({ step, finding: '本轮页面已核实，重开含义尚不能安全确定', ...ev() }));
  assert.equal(validate(m, context).status, 'incomplete');
});
test('真实外部阻塞允许未完成；用户暂停不要求继续操作补证据', () => {
  const m = { version: 1, run_id: 'test-run', external_block: { kind: 'save-conflict', description: '服务器存档冲突', ...ev() } };
  assert.equal(validate(m, context).status, 'incomplete'); assert.equal(validate({ version: 1, run_id: 'test-run' }, { ...context, paused: true }).status, 'paused');
});
test('仍在有效期不能标expired', () => { const m = good(); m.activities[0] = { id: 'cat-house', outcome: 'expired', ...ev(), play_deadline: new Date(Date.now()+3600000).toISOString() }; assert.equal(validate(m, context).accepted, false); });
test('hook只激活真正执行请求，不误拦其它项目/只读调查', async () => {
  const root = path.join(dir, 'inactive'); const opts = { root, workspace: dir };
  await handleHook({ cwd: dir, session_id: 'audit', hook_event_name: 'UserPromptSubmit', prompt: '研究“04:00 全天档”错误，不操作' }, opts);
  assert.equal(fs.existsSync(paths('audit', root).state), false);
  assert.equal((await handleHook({ cwd: os.tmpdir(), session_id: 'outside', hook_event_name: 'Stop' }, opts)).code, 0);
});
test('缺清单Stop真实拒绝两次，第三次明确未完成退出；新轮不继承计数', async () => {
  const root = path.join(dir, 'active'), opts = { root, workspace: dir };
  fs.mkdirSync(root, { recursive: true }); fs.writeFileSync(path.join(root, 'protected.json'), '{"files":{}}');
  const input = { cwd: dir, session_id: 'hook-run', hook_event_name: 'UserPromptSubmit', prompt: '[HAPPYFISH_DAILY_EXECUTION_V1]\n测试' };
  assert.equal((await handleHook(input, opts)).code, 0);
  input.hook_event_name = 'Stop';
  assert.equal((await handleHook(input, opts)).code, 2); assert.equal((await handleHook(input, opts)).code, 2);
  const last = await handleHook(input, opts); assert.equal(last.code, 0); assert.equal(last.output.continue, false);
  assert.equal(JSON.parse(fs.readFileSync(paths('hook-run', root).receipt)).status, 'incomplete');
  assert.equal(init('other-run', { root }).rejections, 0);
});
test('直接编辑和shell写技能被拒；读取通过；绕过写后完整性检查拒绝', () => {
  const root = path.join(dir, 'protected'); fs.mkdirSync(root, { recursive: true });
  const file = path.join(root, 'SKILL.md'); fs.writeFileSync(file, '用户要求继续');
  fs.writeFileSync(path.join(root, 'protected.json'), JSON.stringify({ files: { [file]: crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex') } }));
  assert(preflight({ cwd: root, tool_name: 'Edit', tool_input: { file_path: file } }, root).length);
  assert(preflight({ cwd: root, tool_name: 'Bash', tool_input: { command: 'Set-Content SKILL.md "停手"' } }, root).length);
  assert.equal(preflight({ cwd: root, tool_name: 'Read', tool_input: { file_path: file } }, root).length, 0);
  fs.writeFileSync(file, '停手'); assert(preflight({ cwd: root, tool_name: 'Read', tool_input: { file_path: file } }, root).length);
});
test('模型复盘不能冒充用户纠正；当前用户逐字原话可保存', async () => {
  const root = path.join(dir, 'correction'), opts = { root, workspace: dir }; fs.mkdirSync(root, { recursive: true }); fs.writeFileSync(path.join(root, 'protected.json'), '{"files":{}}'); init('correction-run', { root });
  const base = { cwd: dir, session_id: 'correction-run' };
  const input = { ...base, hook_event_name: 'PreToolUse', tool_name: 'mcp_call', tool_input: { toolName: 'mcp__agent_recall__check', arguments: { human_correction: { why: '我认为不该继续，决定以后停止' } } } };
  assert.equal((await handleHook(input, opts)).code, 2);
  await handleHook({ ...base, hook_event_name: 'UserPromptSubmit', prompt: '剩余免费体力继续用，不要停在原地等我。' }, opts);
  input.tool_input.arguments.human_correction.why = '用户原话：「剩余免费体力继续用，不要停在原地等我。」'; assert.equal((await handleHook(input, opts)).code, 0);
});
