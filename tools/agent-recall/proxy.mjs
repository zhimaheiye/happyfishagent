import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { connect, RUNTIME } from './bridge.mjs';
import { normalizeProjectNext, restoreProjectNext } from './journal-next.mjs';

// Keep the upstream schemas/tools unchanged. No custom authorization is inferred.
const sdk = path.join(RUNTIME, 'node_modules', '@modelcontextprotocol/sdk/dist/esm');
const { Server } = await import(pathToFileURL(path.join(sdk, 'server/index.js')).href);
const { StdioServerTransport } = await import(pathToFileURL(path.join(sdk, 'server/stdio.js')).href);
const { ListToolsRequestSchema, CallToolRequestSchema } = await import(pathToFileURL(path.join(sdk, 'types.js')).href);
const { client } = await connect();
const server = new Server({ name: 'happyfish-agent-recall', version: '1.0.0' }, { capabilities: { tools: {} } });
server.setRequestHandler(ListToolsRequestSchema, () => client.listTools());
server.setRequestHandler(CallToolRequestSchema, async request => {
  const { name, arguments: args = {} } = request.params;
  const target = args.project === 'happyfish-activities';
  if (target && name === 'session_start') normalizeProjectNext();
  // Demote old trajectories before the upstream call builds the new journal/handoff.
  const changes = target && name === 'session_end' && args.trajectory ? normalizeProjectNext({ retireAll: true }) : [];
  try {
    const result = await client.callTool({ name, arguments: args });
    if (result.isError) restoreProjectNext(changes);
    return result;
  } catch (e) { restoreProjectNext(changes); throw e; }
});
const transport = new StdioServerTransport();
server.onclose = () => { client.close().catch(() => {}); };
await server.connect(transport);
