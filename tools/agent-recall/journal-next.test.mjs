import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeNext } from './journal-next.mjs';
test('同日多次保存只让最新Next参与恢复，保留旧历史和换行', () => {
  const original = '## Next\n旧：等南瓜\n\n## Update\n纠错\n## Next\n新：核实入口重开\n';
  const out = normalizeNext(original);
  assert(out.includes('## Historical next (superseded)\n旧：等南瓜'));
  assert.equal(out.match(/^## Next$/gm).length, 1);
  assert.equal(out.slice(out.indexOf('## Next')), '## Next\n新：核实入口重开\n');
  assert.equal(normalizeNext(out), out);
});
test('新保存前撤下旧Next；不能误处理Next steps或CRLF正文', () => {
  assert.equal(normalizeNext('## Next\r\n旧内容\r\n', true), '## Historical next (superseded)\n旧内容\r\n');
  assert.equal(normalizeNext('## Next steps\n任务', true), '## Next steps\n任务');
});
