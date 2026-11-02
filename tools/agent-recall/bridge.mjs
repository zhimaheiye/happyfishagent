import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { normalizeProjectNext, restoreProjectNext } from './journal-next.mjs';

export const PROJECT = 'happyfish-activities';
export const WORKSPACE = 'D:\\开心水族箱活动经验';
export const RUNTIME = path.join(os.homedir(), '.agent-recall-runtime');
export const MEMORY = path.join(os.homedir(), '.agent-recall');
export const core = await import(pathToFileURL(path.join(RUNTIME, 'node_modules', 'agent-recall-core', 'dist', 'index.js')).href);
const integration = path.join(MEMORY, 'projects', PROJECT, 'integration', 'qoder');

export async function connect() {
  const sdk = path.join(RUNTIME, 'node_modules', '@modelcontextprotocol', 'sdk', 'dist', 'esm', 'client');
  const { Client } = await import(pathToFileURL(path.join(sdk, 'index.js')).href);
  const { StdioClientTransport } = await import(pathToFileURL(path.join(sdk, 'stdio.js')).href);
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [path.join(RUNTIME, 'node_modules', 'agent-recall-mcp', 'dist', 'index.js')],
    env: { ...process.env, AGENT_RECALL_ROOT: MEMORY },
    stderr: 'pipe',
  });
  const client = new Client({ name: 'happyfish-memory-bridge', version: '1.0.0' });
  await client.connect(transport);
  return { client, transport };
}

function inWorkspace(cwd) {
  if (!cwd) return false;
  const root = path.resolve(WORKSPACE).toLowerCase();
  const target = path.resolve(cwd).toLowerCase();
  return target === root || target.startsWith(root + path.sep);
}

async function hook() {
  let raw = '';
  for await (const chunk of process.stdin) raw += chunk;
  const input = JSON.parse(raw || '{}');
  if (!inWorkspace(input.cwd)) return;
  fs.mkdirSync(integration, { recursive: true });
  const event = input.hook_event_name;
  if (['SessionStart', 'PostCompact'].includes(event)) normalizeProjectNext();
  const log = { at: new Date().toISOString(), event, session: input.session_id, cwd: input.cwd };
  // Keep user input as evidence, not as automatically authorized rules.
  // Redact credentials before persistence; never promote assistant output here.
  if (event === 'UserPromptSubmit' && typeof input.prompt === 'string') {
    const prompt = core.scrubSecretContent(input.prompt).content;
    const hash = crypto.createHash('sha256').update(prompt).digest('hex');
    fs.appendFileSync(path.join(integration, 'input-inbox.jsonl'), JSON.stringify({ ...log, hash, source: 'user_prompt_unreviewed', prompt }) + '\n');
    log.prompt_hash = hash;
  }
  fs.appendFileSync(path.join(integration, 'hooks.jsonl'), JSON.stringify(log) + '\n');
  if (!['SessionStart', 'UserPromptSubmit', 'PostCompact'].includes(event)) return;
  const rules = core.readActiveCorrections(PROJECT);
  const context = [
    `本项目使用 AgentRecall，project 固定为 ${PROJECT}，不得用 auto 创建分叉。`,
    '下面是已记录且可追溯的项目规则；来源和适用范围须与当前用户要求核对，当前明确指令及更高层规则优先。',
    ...rules.map(r => `[${r.id}] ${r.rule}\n证据：${r.context}`),
    '开始工作或上下文压缩后调用 agent-recall.session_start(project, mode="full", verbose=true)，并读取工作区 AGENTS.md。',
    '用户纠正/持续授权立即调用 check(goal, project, human_correction:{rule,why,applies_when})；确认激活，不能只说记住了。',
    '普通事实用 remember(content,context="decision",project)；当前状态带核实时间和来源，不升级为永久授权。',
    '结束/交接前调用 session_end；不得把 Agent 自己的推断当作用户规则，也不得虚报已执行或记忆有效。',
    `本轮用户原文备份在 ${path.join(integration, 'input-inbox.jsonl')}，仅供查证，未审核内容不能自动成为规则。`,
  ].join('\n\n');
  // No summarization or per-rule truncation: explicit rules survive compaction.
  process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: event, additionalContext: context } }));
}

async function main() {
  const [command, name, file] = process.argv.slice(2);
  if (command === 'hook') return hook();
  const { client } = await connect();
  try {
    if (command === 'list') console.log(JSON.stringify(await client.listTools(), null, 2));
    else if (command === 'call') {
      const input = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
      if (name === 'session_start') normalizeProjectNext();
      const changes = name === 'session_end' && input.trajectory ? normalizeProjectNext({ retireAll: true }) : [];
      let result;
      try { result = await client.callTool({ name, arguments: { project: PROJECT, ...input } }); }
      catch (e) { restoreProjectNext(changes); throw e; }
      if (result.isError) restoreProjectNext(changes);
      console.log(JSON.stringify(result, null, 2));
      if (result.isError) process.exitCode = 1;
    } else throw new Error('Usage: node bridge.mjs list | call TOOL INPUT.json | hook');
  } finally { await client.close(); }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main();
}
