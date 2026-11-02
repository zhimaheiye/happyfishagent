import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

// AgentRecall 3.5.2 readers take the FIRST ## Next, while session_end appends.
// Preserve history but expose only the latest section under the active heading.
export function normalizeNext(text, retireAll = false) {
  const matches = [...text.matchAll(/^## Next[ \t]*\r?$/gm)];
  const retire = retireAll ? matches : matches.slice(0, -1);
  let out = text;
  for (const match of retire.reverse()) out = out.slice(0, match.index) + '## Historical next (superseded)' + out.slice(match.index + match[0].length);
  return out;
}
export function normalizeProjectNext({ retireAll = false } = {}) {
  const project = path.join(os.homedir(), '.agent-recall', 'projects', 'happyfish-activities');
  const journal = path.join(project, 'journal');
  const backup = path.join(os.homedir(), '.agent-recall-runtime', 'backups', 'journal-next', new Date().toISOString().replace(/[:.]/g, '-'));
  const changed = [];
  if (!fs.existsSync(journal)) return changed;
  const files = fs.readdirSync(journal).filter(n => n.endsWith('.md')).sort();
  // Do not retire past days when preparing a new session_end. They remain historical resumes.
  const today = new Date().toISOString().slice(0, 10);
  for (const name of files) {
    const file = path.join(journal, name), original = fs.readFileSync(file, 'utf8');
    const next = normalizeNext(original, retireAll && name.startsWith(today));
    if (next === original) continue;
    fs.mkdirSync(backup, { recursive: true }); fs.writeFileSync(path.join(backup, name), original);
    fs.writeFileSync(file, next); changed.push({ file, original, next });
  }
  return changed;
}
export function restoreProjectNext(changes) {
  for (const { file, original, next } of changes) if (fs.readFileSync(file, 'utf8') === next) fs.writeFileSync(file, original);
}
