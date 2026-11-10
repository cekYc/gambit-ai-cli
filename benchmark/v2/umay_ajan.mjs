// Gambit Bench v2 için Umay CLI ajan sürücüsü: bir görevi Umay CLI'nin kendi ajan döngüsüyle (chat + yerel araçlar)
// görev klasöründe çalıştırır. umay_kos.py ile stdin/stdout üzerinden JSON satırlarıyla konuşur:
//   ← {"type":"start", prompt, cwd, tools, budget, maxSteps, model, thinking, baseURL}
//   → {"type":"approve", id, name, args}   ← {"type":"approval", id, ok}
//   → {"type":"done", final, events, messages, calls, timedOut, serverError, crash, blocked, emptyRetries, tokens, promptTokens}
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
// Sunucu hatası, model hiçbir şey üretmeden geldiyse aynı istek görevi baştan başlatmadan yeniden gönderilir:
//  - boş akış: 200 ve olay akışı başlığı gelip model çıktısı gelmeden bağlantı kapanırsa (yeni modellerde ilk token
//    ~2 dakikayı geçince böyle oluyor, 9 Kasım 2026);
//  - kopan bağlantı: aynı durumda bağlantı düzgün kapanmak yerine koparsa (SDK bunu "Failed to process successful
//    response" diye bildiriyor, CLI "Yanıt işlenemedi" diyor);
//  - hata olayı: model çıktısından önce {"error": ...} gelirse (Umay'ın arka ucu sağlayıcıya ulaşamayınca, ör. "Tüm
//    API anahtarları denendi fakat yanıt alınamadı").
// Model çıktısı başlamış akışlar (sonradan kesilse de) olduğu gibi geçer.
let calls = 0, emptyRetries = 0, emptyGaveUp = false;
const EMPTY_RETRIES = 5;
const isStream = response => response.ok && response.body && /event-stream/i.test(response.headers.get('content-type') ?? '');
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  if (!String(url).includes('/chat/completions')) return realFetch(url, init);
  calls++;
  const response = await realFetch(url, init);
  if (!isStream(response)) return response;
  return new Response(retrying(url, init, response),
    { status: response.status, statusText: response.statusText, headers: response.headers });
};

// Tam "data:" olaylarına sırayla bakar: model çıktısı (metin, düşünce, araç çağrısı ya da bitiş nedeni) gelmişse
// 'data', ondan önce hata olayı gelmişse 'error', henüz ikisi de yoksa 'wait'. Rol ya da kullanım bilgisi gibi
// içeriksiz olaylar model çıktısı sayılmaz.
function firstEvent(text) {
  const end = text.lastIndexOf('\n');
  for (const raw of text.slice(0, Math.max(end, 0)).split('\n')) {
    const line = raw.replace(/\r$/, '');
    if (!line.startsWith('data:')) continue;
    const body = line.slice(5).trim();
    if (!body || body === '[DONE]') continue;
    let json;
    try {
      json = JSON.parse(body);
    } catch {
      return 'data';
    }
    if (!json || typeof json !== 'object') return 'data';
    if (json.error && !json.choices) return 'error';
    for (const choice of json.choices ?? []) {
      const d = choice.delta ?? choice.message ?? {};
      if (d.content || d.reasoning_content || d.reasoning || d.tool_calls?.length || choice.finish_reason) return 'data';
    }
  }
  return 'wait';
}

function errorText(text) {
  for (const line of text.split('\n')) {
    try {
      const { error } = JSON.parse(line.replace(/^data:/, '').trim());
      if (error) return typeof error === 'string' ? error : error.message ?? JSON.stringify(error);
    } catch { /* satır JSON değil */ }
  }
  return text.trim();
}

// Hatanın kendisi ve alttaki nedenleri: "TypeError: terminated / SocketError: other side closed" gibi.
function describe(error) {
  const parts = [];
  for (let e = error, depth = 0; e && depth < 3; e = e.cause, depth++) parts.push(`${e.name ?? 'Error'}: ${e.message ?? e}`);
  return parts.join(' / ');
}

function retrying(url, init, first) {
  let reader = first.body.getReader(), decoder = new TextDecoder(), text = '', pending = [], decided = false, tries = 0;
  let began = Date.now();
  const flush = controller => { for (const chunk of pending) controller.enqueue(chunk); pending = []; decided = true; };
  return new ReadableStream({
    async pull(controller) {
      for (;;) {
        let value, done, dropped;
        try {
          ({ value, done } = await reader.read());
        } catch (error) {
          // Model çıktısı başladıktan sonra kopan ya da bizim iptal ettiğimiz akışın hatası olduğu gibi geçer.
          if (decided || init?.signal?.aborted) throw error;
          dropped = error;
          done = true;
        }
        if (decided) {
          if (done) controller.close(); else controller.enqueue(value);
          return;
        }
        let verdict = 'empty';
        if (!done) {
          pending.push(value);
          text += decoder.decode(value, { stream: true });
          verdict = firstEvent(text);
          if (verdict === 'wait') continue;
          if (verdict === 'data') { flush(controller); return; }
        }
        // Boş akış, kopan bağlantı ya da ilk olayı hata olan akış: yeniden dene; deneme hakkı bittiyse geleni olduğu
        // gibi geçir (CLI hatayı gösterir, sürücü sunucu hatası olarak kaydeder ve koşucu görevi yeniden dener).
        if (tries >= EMPTY_RETRIES) {
          emptyGaveUp = true;
          flush(controller);
          if (dropped) controller.error(dropped);
          else if (done) controller.close();
          return;
        }
        if (!done) await reader.cancel().catch(() => {});
        tries++;
        emptyRetries++;
        const seconds = Math.round((Date.now() - began) / 1000);
        const what = verdict === 'error'
          ? `sunucu ${seconds} sn sonra hata döndürdü: ${errorText(text).slice(0, 200)}`
          : dropped
            ? `bağlantı ${seconds} sn sonra model yanıtı gelmeden koptu (${describe(dropped).slice(0, 200)})`
            : `sunucu ${seconds} sn sonra hiç veri göndermeden kapattı${text.trim() ? ` (gelen: ${JSON.stringify(text.trim().slice(0, 200))})` : ''}`;
        say(`\n⟳ ${what}; istek yeniden gönderiliyor (${tries}/${EMPTY_RETRIES})\n`);
        began = Date.now();
        const next = await realFetch(url, init);
        if (!isStream(next)) {
          await next.body?.cancel();
          say(`⟳ yeniden deneme HTTP ${next.status} döndü\n`);
          emptyGaveUp = true;
          flush(controller);
          controller.close();
          return;
        }
        reader = next.body.getReader();
        decoder = new TextDecoder();
        text = '';
        pending = [];
      }
    },
    cancel(reason) { return reader.cancel(reason); },
  });
}

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
  const key = process.env.UMAY_API_KEY ?? '';
  const status = error?.statusCode ? ` ${error.statusCode}` : '';
  const raw = `${error?.name ?? 'Error'}${status}: ${error?.message ?? error}${error?.cause ? ` (${describe(error.cause)})` : ''}`;
  if (abort.signal.aborted) timedOut = true;
  else if (emptyGaveUp) serverError = `sunucu ${EMPTY_RETRIES + 1} denemede de model yanıtı göndermedi (boş akış, kopan bağlantı ya da hata olayı)`;
  // HTTP ya da bağlantı hatası: CLI'nin kullanıcıya gösterdiği mesajın yanında ham hata da kaydedilir
  else if (error?.statusCode || /fetch|network|ECONN|socket|ENOTFOUND/i.test(error?.message ?? '')) {
    serverError = `${friendlyError(error, key)} [${key ? raw.replaceAll(key, '[gizli]') : raw}]`.slice(0, 400);
  }
  // Model çıktısı başladıktan sonra gelen kesilme (ör. Umay sunucusunun zaman sınırı: "context deadline exceeded")
  // önceki koşulardaki kesilen yanıtlar gibi sonuçtur: çökme olarak kaydedilir ve yeniden denenmez.
  else crash = `${error?.name}: ${error?.message}`.slice(0, 300);
} finally {
  clearTimeout(timer);
  await runtime?.close();
}
send({ type: 'done', final, events, messages, calls, timedOut, serverError, crash, blocked, emptyRetries,
  tokens: usage.outputTokens ?? 0, promptTokens: usage.inputTokens ?? 0 });
process.exit(0);
