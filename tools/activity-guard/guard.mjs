import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

export const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
export const WORKSPACE = path.dirname(REPO);
export const ROOT = path.join(os.homedir(), '.agent-recall-runtime', 'activity-guard');
const MARKER = '[HAPPYFISH_DAILY_EXECUTION_V1]';
const digest = data => crypto.createHash('sha256').update(data).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const write = (file, data) => { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n'); };
const under = (p, root) => { const rel = path.relative(path.resolve(root), path.resolve(p)); return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel)); };
const identity = id => digest(String(id)).slice(0, 24);
export function paths(id, root = ROOT) {
  const dir = path.join(root, 'runs', identity(id));
  return { dir, state: path.join(dir, 'state.json'), manifest: path.join(dir, 'manifest.json'), receipt: path.join(dir, 'receipt.json') };
}

export function validate(m, context = {}) {
  const errors = [], statuses = [], evidenceHashes = {};
  const now = context.now ?? Date.now(), started = Date.parse(context.started_at);
  const err = (where, reason) => errors.push(`${where}: ${reason}`);
  function evidence(refs, where, observedAt) {
    const t = Date.parse(observedAt);
    if (!Number.isFinite(t) || t < started || t > now + 60000) err(where, '缺少本次运行内的观测时间；旧读数不得复用');
    if (!Array.isArray(refs) || !refs.length) { err(where, '缺少现场截图'); return; }
    for (const ref of refs) {
      if (typeof ref !== 'string' || !path.isAbsolute(ref)) { err(where, '截图必须是绝对路径'); continue; }
      try {
        const b = fs.readFileSync(ref), s = fs.statSync(ref);
        const image = b.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10])) || (b[0] === 255 && b[1] === 216) || (b.toString('ascii', 0, 4) === 'RIFF' && b.toString('ascii', 8, 12) === 'WEBP');
        if (!image || s.mtimeMs < started - 2000) err(where, '证据不是本次截图，不能用技能文档/旧图片代替');
        else evidenceHashes[ref] = digest(b);
      } catch { err(where, `证据文件不存在或不可读: ${ref}`); }
    }
  }
  if (!m || m.version !== 1 || m.run_id !== context.run_id) return { accepted: false, status: 'rejected', errors: ['运行标识不匹配或manifest版本错误'], evidenceHashes };
  if (context.paused) return { accepted: true, status: 'paused', errors: [], evidenceHashes, note: '用户明确暂停，禁止继续游戏输入；不算玩法完成' };
  if (m.external_block) {
    const b = m.external_block;
    if (!['device-unavailable','concurrent-controller','save-conflict'].includes(b.kind) || !b.description) err('external_block', '仅接受具体外部设备/互斥/存档阻塞');
    evidence(b.evidence, 'external_block', b.observed_at);
    return { accepted: !errors.length, status: errors.length ? 'rejected' : 'incomplete', errors, evidenceHashes };
  }
  evidence(m.inventory?.evidence, 'inventory', m.inventory?.observed_at);
  const inventory = m.inventory?.activities;
  if (!Array.isArray(inventory) || !inventory.length) err('inventory', '缺少逐项活动发现结果（含纳入/排除原因）');
  const ids = new Set(), included = new Set();
  for (const a of inventory ?? []) {
    if (!a.id || ids.has(a.id) || typeof a.included !== 'boolean' || !a.reason) err('inventory', '活动id、纳入判断、原因缺失或重复');
    ids.add(a.id);
    if (a.included === true) included.add(a.id);
    else evidence(a.evidence, `excluded:${a.id}`, a.observed_at);
  }
  for (const id of context.expected_ids ?? []) if (!ids.has(id)) err(id, '之前已登记的活动从清单消失，须保留并说明状态');
  if (!Array.isArray(m.activities)) err('activities', '缺少活动验收列表');
  const seen = new Set();
  for (const a of m.activities ?? []) {
    if (!included.has(a.id) || seen.has(a.id)) err(a.id, '活动未纳入或验收行重复');
    seen.add(a.id);
    const e = a.entry, r = a.round;
    if (a.outcome === 'expired') {
      evidence(a.evidence, `${a.id}:expired`, a.observed_at);
      const t = Date.parse(a.play_deadline);
      if (!Number.isFinite(t) || t > now) err(a.id, '玩法截止时间未到或未核实');
      statuses.push('expired'); continue;
    }
    if (!e || e.scope !== 'activity-entry' || !e.resource || !Number.isFinite(e.balance) || e.balance < 0 || !Number.isFinite(e.cost) || e.cost <= 0) err(a.id, '必须现读本活动入口体力/门票余额和单次成本；关内南瓜、主缸通用体力不能代替');
    evidence(e?.evidence, `${a.id}:entry`, e?.observed_at);
    if (!r || !['none','ended','active','stalled'].includes(r.state)) err(a.id, '缺少当前局状态');
    evidence(r?.evidence, `${a.id}:round`, r?.observed_at);
    if (a.outcome === 'exhausted') {
      if (e?.balance >= e?.cost) err(a.id, '入口额度仍可开局，须结束死局后继续下一局');
      if (!['none','ended'].includes(r?.state)) err(a.id, '仍有存档活局/死局；暂时离开不等于结束整轮');
      statuses.push('exhausted');
    } else if (a.outcome === 'blocked') {
      if (e?.balance < e?.cost && ['none','ended'].includes(r?.state)) err(a.id, '免费入口已耗尽且无未结局，应记exhausted；付费续局不属于未完成义务');
      const b = a.block;
      if (!b || !['paid-only','unsafe-reset','unresolved-ui'].includes(b.kind) || !b.description) err(a.id, '缺少具体阻塞；不能引用子技能的停手结论');
      for (const step of ['entry-inspection','round-end-inspection','new-round-inspection']) {
        const attempt = b?.checks?.find(x => x.step === step);
        if (!attempt?.finding) err(a.id, `必须检查 ${step}，不会做不等于无免费路径`);
        evidence(attempt?.evidence, `${a.id}:${step}`, attempt?.observed_at);
      }
      statuses.push('blocked');
    } else err(a.id, '结论只能是exhausted/expired/blocked；暂停须来自用户，不能自签');
  }
  for (const id of included) if (!seen.has(id)) err(id, '已纳入活动漏做/漏验收');
  return { accepted: !errors.length, status: errors.length ? 'rejected' : statuses.includes('blocked') ? 'incomplete' : 'completed', errors, evidenceHashes };
}

export function init(id, options = {}) {
  if (!id) throw new Error('需要run/session id');
  const p = paths(id, options.root);
  if (fs.existsSync(p.state)) return read(p.state);
  const started_at = options.started_at ?? new Date().toISOString();
  const state = { run_id: id, started_at, rejections: 0, expected_ids: [], paused: false, initial_prompt: options.prompt ?? '', user_prompts: [] };
  write(p.state, state);
  write(p.manifest, { version: 1, run_id: id, inventory: { observed_at: '', evidence: [], activities: [] }, activities: [] });
  return state;
}

function protectedPaths(root) {
  const file = path.join(root, 'protected.json');
  return fs.existsSync(file) ? read(file).files : null;
}
function integrity(root) {
  const files = protectedPaths(root);
  if (!files) return ['缺少受保护文件基线，不能把保护未安装当通过'];
  return Object.entries(files).flatMap(([p, sha]) => {
    try { return digest(fs.readFileSync(p)) === sha ? [] : [`受保护规则被修改: ${p}`]; }
    catch { return [`受保护规则丢失: ${p}`]; }
  });
}
export function preflight(input, root = ROOT) {
  const problems = integrity(root);
  if (problems.length) return problems;
  let name = input.tool_name ?? '', args = input.tool_input ?? {};
  if (name === 'mcp_call') { name = args.toolName ?? ''; args = args.arguments ?? {}; }
  const files = Object.keys(protectedPaths(root) ?? {});
  const writeTool = /(?:^|__)(?:Write|Edit|MultiEdit|replace|apply_patch)$/i.test(name);
  const target = args.file_path ?? args.path ?? args.file ?? args.target;
  if (writeTool && (typeof target !== 'string' || files.some(p => path.resolve(p).toLowerCase() === path.resolve(input.cwd, target).toLowerCase()) || /(?:^|[\\/])SKILL\.md$/i.test(target))) {
    return ['日常执行不得改写技能/用户规则。新发现写assets/<活动>/observations/<run>.md；有效规程在离线审核时更新。'];
  }
  const command = args.command ?? args.cmd ?? '';
  if (/Bash|exec|run|shell/i.test(name) && typeof command === 'string') {
    if (/(?:write|set-content|add-content|out-file|replace|unlink|remove-item|\brm\b|\bmv\b|\bcp\b|copy-item|apply_patch|sed\s+-i|>|open\([^\n]*['"](?:w|a))/.test(command.toLowerCase()) && /SKILL\.md|AGENTS\.md|user-policy|activity-guard|settings\.json|corrections[\\/]/i.test(command)) {
      return ['命令可能修改执行期受保护规则；日常阶段只能写观察记录，不能修改规则或保护器。'];
    }
  }
  return [];
}

export async function handleHook(input, options = {}) {
  const root = options.root ?? ROOT, workspace = options.workspace ?? WORKSPACE;
  if (!input.cwd || !under(input.cwd, workspace) || !input.session_id) return { code: 0 };
  const p = paths(input.session_id, root), event = input.hook_event_name;
  const prompt = typeof input.prompt === 'string' ? input.prompt.trim() : '';
  // Only an actual execution prompt activates this guard. Quoted audit documents do not.
  if (event === 'UserPromptSubmit' && (prompt.startsWith(MARKER) || /^你是《开心水族箱》项目的[「“"]04[:：]00\s*全天档/.test(prompt))) init(input.session_id, { root, prompt });
  if (!fs.existsSync(p.state)) return { code: 0 };
  fs.appendFileSync(path.join(p.dir, 'events.jsonl'), JSON.stringify({ at: new Date().toISOString(), event, session_id: input.session_id, tool: input.tool_name ?? null }) + '\n');
  const state = read(p.state);
  if (event === 'UserPromptSubmit' && prompt && prompt !== state.initial_prompt) {
    state.user_prompts.push(prompt);
    // Direct, short pause/resume commands only; do not infer consent from task text.
    if (/^(?:请|现在|先|这里可以)?(?:暂停|停手|停止操作|停止游戏|不要操作游戏|不用操作)[。！!\s]*$/.test(prompt)) state.paused = true;
    if (/^(?:请|现在)?(?:继续|继续执行|恢复执行)[。！!\s]*$/.test(prompt)) { state.paused = false; state.rejections = 0; }
    write(p.state, state);
  }
  if (['SessionStart','UserPromptSubmit','PostCompact'].includes(event)) return { code: 0, output: { hookSpecificOutput: { hookEventName: event, additionalContext: `活动执行验收已启用，run_id=${state.run_id}。先读 ${path.join(REPO, 'docs/activity-execution-contract.md')}。本轮清单填写 ${p.manifest}，收工前运行 node "${fileURLToPath(import.meta.url)}" check "${p.manifest}"。不得写技能/用户规则；新发现进observations。未通过验收不算完成。用户暂停优先，不能为通过检查盲点或付费。` } } };
  if (event === 'PreToolUse') {
    const errors = preflight(input, root);
    let name = input.tool_name ?? '', args = input.tool_input ?? {};
    if (name === 'mcp_call') { name = args.toolName ?? ''; args = args.arguments ?? {}; }
    if (state.paused && /(?:tap|click|swipe|drag|input|post_task|run_task)/i.test(name + ' ' + (args.command ?? args.cmd ?? ''))) errors.push('用户已暂停，禁止继续游戏输入；可读取证据或整理报告。');
    if (/check$/.test(name) && args.human_correction) {
      const why = args.human_correction.why ?? '';
      const quote = /用户原话[：:]\s*[「“]([^」”]{10,})[」”]/.exec(why)?.[1];
      if (!quote || !state.user_prompts.some(s => s.includes(quote))) errors.push('纠正必须引用本执行会话后续用户的原话：why含 用户原话：「逐字原句」。助手复盘/技能推断不得伪装成人类纠正；普通发现写观察。');
    }
    return errors.length ? { code: 2, error: errors.join('\n') } : { code: 0 };
  }
  if (event !== 'Stop') return { code: 0 };
  let result;
  try { result = validate(read(p.manifest), state); }
  catch (e) { result = { accepted: false, status: 'rejected', errors: [`清单读取失败: ${e.message}`] }; }
  if (!state.paused) {
    result.errors.push(...integrity(root));
    if (result.errors.length) { result.accepted = false; result.status = 'rejected'; }
  }
  result.at = new Date().toISOString(); result.run_id = state.run_id;
  try { state.expected_ids = [...new Set([...state.expected_ids, ...read(p.manifest).inventory.activities.map(a => a.id).filter(Boolean)])]; } catch { /* malformed manifests are already rejected */ }
  if (!result.accepted) {
    state.rejections++;
    if (state.rejections > 2) {
      result.status = 'incomplete'; result.accepted = false;
      result.note = '连续两次返工后仍未通过，终止自动重试；本轮未完成，不得记成功';
      write(p.receipt, result); write(p.state, state);
      return { code: 0, output: { continue: false, stopReason: result.note, systemMessage: `活动验收失败，本轮未完成。详见 ${p.receipt}` } };
    }
    write(p.receipt, result); write(p.state, state);
    return { code: 2, error: `活动收工验收拒绝（${state.rejections}/2）：\n${result.errors.join('\n')}\n修正 ${p.manifest} 并补做已授权工作。真实阻塞填blocked及三项现场检查；用户暂停立即停输入。禁止改规则迁就结果。` };
  }
  state.expected_ids = read(p.manifest).inventory?.activities?.map(a => a.id) ?? [];
  write(p.receipt, result); write(p.state, state);
  return { code: 0, output: { systemMessage: `活动验收：${result.status === 'completed' ? '通过' : result.status === 'paused' ? '用户暂停（未完成）' : '存在已登记阻塞（未完成）'}。${p.receipt}` } };
}

async function main() {
  const [cmd, arg] = process.argv.slice(2);
  if (cmd === 'hook') {
    let raw = ''; for await (const chunk of process.stdin) raw += chunk;
    const result = await handleHook(JSON.parse(raw));
    if (result.output) console.log(JSON.stringify(result.output));
    if (result.error) console.error(result.error);
    process.exitCode = result.code; return;
  }
  if (cmd === 'begin') { const s = init(arg); console.log(JSON.stringify({ ...s, ...paths(arg) }, null, 2)); return; }
  if (cmd === 'check') {
    const m = read(arg), p = paths(m.run_id), state = read(p.state);
    const result = validate(m, state);
    result.errors.push(...integrity(ROOT));
    if (result.errors.length) { result.accepted = false; result.status = 'rejected'; }
    const ids = m.inventory?.activities?.map(a => a.id).filter(Boolean) ?? [];
    state.expected_ids = [...new Set([...state.expected_ids, ...ids])]; write(p.state, state);
    result.at = new Date().toISOString(); result.run_id = m.run_id;
    write(p.receipt, result); console.log(JSON.stringify(result, null, 2)); process.exitCode = result.accepted ? 0 : 2; return;
  }
  throw new Error('Usage: guard.mjs hook | begin <session-or-run-id> | check <manifest.json>');
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main().catch(e => { console.error(e.stack); process.exitCode = 2; });
