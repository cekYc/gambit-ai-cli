// Gambit Bench v2 için Umay CLI ajan sürücüsü: bir görevi Umay CLI'nin kendi ajan döngüsüyle (chat + yerel araçlar)
// görev klasöründe çalıştırır. umay_kos.py ile stdin/stdout üzerinden JSON satırlarıyla konuşur:
//   ← {"type":"start", prompt, cwd, tools, budget, maxSteps, model, thinking, baseURL}
//   → {"type":"approve", id, name, args}   ← {"type":"approval", id, ok}
//   → {"type":"done", final, events, messages, calls, timedOut, serverError, crash, blocked, tokens, promptTokens}
// Ekran çıktısı (düşünce, yanıt, araç olayları) stderr'e yazılır; koşucu bunu .log dosyasına kaydeder.
import { createInterface } from 'node:readline';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const umayDir = process.argv[process.argv.indexOf('--umay') + 1];
if (!umayDir || process.argv.indexOf('--umay') < 0) { console.error('--umay <Umay CLI klasörü> gerekli'); process.exit(2); }
const load = file => import(pathToFileURL(path.join(umayDir, 'src', file)).href);
const { chat, friendlyError } = await load('client.mjs');
const { ToolRuntime } = await load('tools.mjs');

const READ_TOOLS = new Set(['read_file', 'list_dir', 'search_files']);
const send = obj => process.stdout.write(JSON.stringify(obj) + '\n');
const say = text => process.stderr.write(text);

const input = createInterface({ input: process.stdin });
const lines = input[Symbol.asyncIterator]();
const start = JSON.parse((await lines.next()).value);
const pending = new Map();
(async () => {
  for await (const line of lines) {
    const msg = JSON.parse(line);
    if (msg.type === 'approval') pending.get(msg.id)?.(msg.ok);
  }
})();

// Model çağrısı sayısı: Umay API'ye giden her sohbet isteği bir adımdır.
let calls = 0;
const realFetch = globalThis.fetch;
globalThis.fetch = (url, init) => {
  if (String(url).includes('/chat/completions')) calls++;
  return realFetch(url, init);
};

const sandbox = path.resolve(start.cwd);
const inside = file => {
  const rel = path.relative(sandbox.toLowerCase(), path.resolve(sandbox, file).toLowerCase());
  return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel));
};
const began = Date.now();
const deadline = began + start.budget * 1000;
const events = [];
const blocked = [];
let visible = '';
let approvals = 0;

class BenchRuntime extends ToolRuntime {
  // Gambit koşucusuyla aynı kurallar: okuma yalnızca görev klasöründe, komut süresi görevin kalan süresiyle sınırlı.
  definitions(signal) {
    const tools = super.definitions(signal);
    for (const [name, definition] of Object.entries(tools)) {
      const execute = definition.execute;
      definition.execute = async (args = {}, ...rest) => {
        const t = Math.round((Date.now() - began) / 100) / 10;
        visible = '';
        if (READ_TOOLS.has(name) && !inside(String(args.path ?? '.') || '.')) {
          const result = 'Hata: bu ortamda yalnızca çalışma klasörünün içi okunabilir.';
          blocked.push(`klasör dışı okuma: ${args.path}`);
          events.push({ name, args, result, t });
          return result;
        }
        if (['run_command', 'run_python'].includes(name)) {
          const left = Math.floor((deadline - Date.now()) / 1000);
          args = { ...args, timeout: Math.max(5, Math.min(Math.max(Number(args.timeout) || 120, 1), 600, left)) };
        }
        const result = String(await execute(args, ...rest));
        events.push({ name, args: clip(args), result: result.slice(0, 3000), t });
        return result;
      };
    }
    return tools;
  }
}

function clip(args) {
  return Object.fromEntries(Object.entries(args).map(([k, v]) => [k, typeof v === 'string' && v.length >= 6000 ? v.slice(0, 6000) + '…' : v]));
}

const runtime = start.tools ? new BenchRuntime({
  cwd: sandbox,
  onEvent: event => say(event.type === 'start' ? `\n⚙ ${event.name} ${JSON.stringify(event.args).slice(0, 300)}\n`
    : `✓ ${String(event.result).split('\n')[0].slice(0, 300)}\n`),
  confirm: ({ name, args }) => new Promise(resolve => {
    const id = ++approvals;
    pending.set(id, ok => { pending.delete(id); if (!ok) blocked.push(`${name} reddedildi`); resolve(ok); });
    send({ type: 'approve', id, name, args });
  }),
}) : undefined;

const abort = new AbortController();
const timer = setTimeout(() => abort.abort(new DOMException('Süre sınırı', 'TimeoutError')), start.budget * 1000);
let final = '', messages = [], usage = {}, timedOut = false, serverError = '', crash = '';
try {
  if (runtime) await runtime.start();
  const result = await chat({
    apiKey: process.env.UMAY_API_KEY, baseURL: start.baseURL || undefined, model: start.model,
    thinking: start.thinking, stream: true, timeout: start.budget * 1000 + 60_000, signal: abort.signal,
    runtime, toolMode: 'text', maxSteps: start.maxSteps,
    messages: [{ role: 'user', content: start.prompt }],
    onText: text => { visible += text; say(text); },
    onReasoning: text => say(text),
  });
  final = result.text;
  messages = result.messages;
  usage = result.usage ?? {};
} catch (error) {
  final = visible;
  if (abort.signal.aborted) timedOut = true;
  else if (error?.statusCode || /fetch|network|ECONN|socket|ENOTFOUND/i.test(error?.message ?? '')) serverError = friendlyError(error, process.env.UMAY_API_KEY ?? '');
  else crash = `${error?.name}: ${error?.message}`.slice(0, 300);
} finally {
  clearTimeout(timer);
  await runtime?.close();
}
send({ type: 'done', final, events, messages, calls, timedOut, serverError, crash, blocked,
  tokens: usage.outputTokens ?? 0, promptTokens: usage.inputTokens ?? 0 });
process.exit(0);
