"""Gambit Bench v2: yerel modelleri gambit-cli'nin kendi ajan döngüsüyle (ai-cli/ai.py → Chat) zorlu görevlerden geçirir.

  python run.py                         # varsayılan plan: önce düşünme kapalı, sonra otomatik düşünme
  python run.py --plan queen:off        # tek yapılandırma (hazır ayar:mod), virgülle birden fazla
  python run.py --only kod-,sql-        # yalnızca id'si bu öneklerle başlayan görevler
  python run.py --selftest              # notlandırıcıları referans/yanlış çözümlerle sına (model gerekmez)
  python run.py --regrade               # kayıtlı çalıştırmaları güncel notlandırıcılarla yeniden puanla
  python run.py --report                # yalnızca raporu yeniden üret

Her görev gambit'in sistem istemi, araçları (dosya okuma/yazma, PowerShell) ve düşünme modu (off / auto) ile çalışır;
gambit'in onay soruları bir güvenlik kuralıyla (yalnızca görev klasörü) otomatik yanıtlanır. Sonuçlar
results/results.jsonl'e eklenir; yarıda kalan çalıştırma aynı komutla kaldığı yerden sürer."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import types
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT / "ai-cli"))

from openai import APIConnectionError, APIStatusError, OpenAI  # noqa: E402
from rich.console import Console  # noqa: E402

import ai  # noqa: E402  (gambit-cli)
import tools as cli_tools  # noqa: E402
import core  # noqa: E402
import gorevler  # noqa: E402,F401
import grading  # noqa: E402
from core import TASKS, Trace  # noqa: E402

RESULTS = HERE / "results"
DEFAULT_PLAN = "bishop:off,rook:off,queen:off,bishop:auto,queen:auto,king:off"
MAX_TOKENS = {"off": 8192, "auto": 12288}  # tek model çağrısı başına üst sınır (kaçak üretime karşı)
SEED = 42
# Örnekleme ayarları her istekte açıkça gönderilir; yoksa her sunucu kendi varsayılanını kullanır (LM Studio ile
# llama-server'ınki farklı) ve aynı model iki ortamda farklı davranır. Değerler model dosyasının (GGUF)
# general.sampling.* üst verisinden; dosyada olmayanlar için: Qwen3.5 aynı ailenin değerleri, Phi-4-mini-reasoning
# tahmini. min_p 0 ve tekrar cezası yok (1.0) hepsinde.
QWEN_SAMPLING = {"temperature": 1.0, "top_p": 0.95, "top_k": 20}
SAMPLING = {
    "google/gemma-4-26b-a4b-it-qat-q4_0-gguf/gemma-4-26b_q4_0-it.gguf": {"temperature": 1.0, "top_p": 0.95, "top_k": 64},
    "qwen3.8-27b": QWEN_SAMPLING, "qwen3.6-35b-a3b": QWEN_SAMPLING, "qwen3.5-9b": QWEN_SAMPLING,
    "qwen3.5-2b": QWEN_SAMPLING, "phi-4-mini-reasoning": {"temperature": 0.8, "top_p": 0.95, "top_k": 50},
}
SERVER_SAMPLING = False  # --server-sampling: eski koşulardaki gibi sunucunun varsayılanları
MAX_STEPS = 14  # görev başına en fazla model adımı (gambit'te max_steps)
BUDGET = {True: 480, False: 300}  # görev başına süre sınırı (sn): araçlı / araçsız; tüm modellere aynı
# --no-time-limit: yavaş modellerin hızdan değil yetenekten ölçülmesi için süre sınırı yok. Döngüyü adım sınırı,
# CLI'nin tekrar sınırı ve başarısız komutu tekrar çalıştırmaması keser; bu tavan yalnızca bir güvenlik ağı.
NO_LIMIT_CAP = 2 * 3600
NO_LIMIT = False
# --remote: LM Studio yerine uzak (ör. kiralık GPU'daki llama-server) OpenAI uyumlu sunucu; model orada zaten yüklü
REMOTE = ""
READ_TOOLS = {"read_file", "list_dir", "search_files"}


def log(msg: str) -> None:
    print(msg, flush=True)


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def fresh_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
        if path.exists():
            subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", str(path)], capture_output=True)
    path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- gambit sarmalayıcısı

def policy(name: str, args: dict, sandbox: Path) -> str | None:
    """gambit'in onay isteyen araçları için kullanıcı yerine karar: yalnızca görev klasörü içinde izin verilir."""
    if name in ("write_file", "edit_file"):
        path = cli_tools._path(str(args.get("path", "")))
        return None if path.is_relative_to(sandbox.resolve()) else f"klasör dışına yazma: {path}"
    if name in ("run_command", "run_python"):
        # run_python'a giden Python kodu da python -c ile çalıştırılan kodla aynı kurallardan geçer
        cmd = str(args.get("command" if name == "run_command" else "code", ""))
        # koddaki kaçışlı ters bölüler ('\\n') ağ yolu sanılmasın; yalnızca gerçek \\sunucu\paylaşım yolları engellenir
        checked = re.sub(r"\\\\(?![\w.-]+\\[\w$.-]+)", "/", cmd)
        # "~3", "~200ms" gibi yaklaşık değerler ev klasörü sanılmasın; yalnızca ~, ~/ ve ~\ ev yoludur
        checked = re.sub(r"~(?![\\/\s'\"]|$)", "≈", checked)
        if name == "run_python":
            # Python kodundaki "net", "reg", "kill" gibi kelimeler kabuk komutu değildir (ör. "Net satış" yorumu);
            # Python için tehlikeli olan subprocess, os.system, shutil... python_danger'da, yol kuralları aşağıda
            checked = grading.SHELL_DENY.sub("_", checked)
        return grading.shell_safety(checked, sandbox) or grading.python_danger(cmd)
    return None


def capped_timeout(timeout, deadline: float | None) -> int:
    """Komut süresi görevin kalan süresiyle sınırlanır (gambit zaman aşımında süreç ağacının tamamını kapatır)."""
    timeout = min(max(int(timeout), 1), 600)
    return timeout if deadline is None else max(5, min(timeout, int(deadline - time.perf_counter())))


class _Guard:
    """Akan cevabı süre sınırı aşılınca keser (sunucunun üretmeyi bırakması için bağlantıyı kapatır)."""

    def __init__(self, stream, bench):
        self.stream, self.bench = stream, bench

    def __iter__(self):
        try:
            for chunk in self.stream:
                yield chunk
                if time.perf_counter() > self.bench.deadline:
                    self.bench.timed_out = True
                    break
        finally:
            self.close()

    def close(self):
        try:
            self.stream.close()
        except Exception:
            pass


class _Completions:
    def __init__(self, inner, extra: dict):
        self.inner, self.extra, self.bench = inner, extra, None

    def create(self, **kwargs):
        body = dict(self.extra.get("extra_body", {}))
        if REMOTE and kwargs.get("reasoning_effort") == "none":  # llama-server düşünmeyi şablon değişkeniyle kapatır
            kwargs.pop("reasoning_effort")
            body["chat_template_kwargs"] = {"enable_thinking": False}
        merged = {**self.extra, **kwargs}
        if body:
            merged["extra_body"] = body
        return _Guard(self.inner.create(**merged), self.bench)


class GambitBench(ai.Chat):
    """gambit-cli'nin Chat sınıfının aynısı; yalnızca onaylar kurala göre verilir, okuma araçları görev klasörüyle
    sınırlanır ve süre, token, araç çağrıları kaydedilir."""

    def __init__(self, *args, sandbox: Path, deadline: float, **kwargs):
        super().__init__(*args, **kwargs)
        self.sandbox = sandbox.resolve()
        self.deadline = deadline
        self.t0 = time.perf_counter()
        self.tokens = self.prompt_tokens = self.calls = self.think_calls = 0
        self.events: list[dict] = []
        self.blocked: list[str] = []
        self.timed_out = False
        self.server_error = ""

    def _complete(self):
        if time.perf_counter() > self.deadline:
            self.timed_out = True
            raise KeyboardInterrupt  # Chat.ask bunu "durduruldu" olarak işler
        self.calls += 1
        if self.thinking and self.can_think():
            self.think_calls += 1
        try:
            return super()._complete()
        except APIStatusError as e:
            text = re.sub(r"<[^>]+>|\s+", " ", ai._error_text(e)).strip()
            self.server_error = f"{e.status_code}: {text}"[:300]
            raise
        except APIConnectionError as e:
            self.server_error = f"bağlantı: {type(e).__name__}: {e}"[:300]
            raise

    def _run_tool(self, call):
        self._call = call
        name = call["function"]["name"]
        try:
            args = json.loads(call["function"]["arguments"] or "{}")
            args = args if isinstance(args, dict) else {}
        except ValueError:
            args = {}
        t = round(time.perf_counter() - self.t0, 1)
        if name in READ_TOOLS:
            p = cli_tools._path(str(args.get("path", ".") or "."))
            if not p.is_relative_to(self.sandbox):
                self.blocked.append(f"klasör dışı okuma: {p}")
                result = "Hata: bu ortamda yalnızca çalışma klasörünün içi okunabilir."
                self.events.append({"name": name, "args": args, "result": result, "t": t})
                return result
        originals = {n: cli_tools.TOOLS[n].run for n in ("run_command", "run_python")}
        for n, run in originals.items():
            cli_tools.TOOLS[n].run = (lambda run: lambda *a, timeout=120, **kw:
                                      run(*a, timeout=capped_timeout(timeout, self.deadline), **kw))(run)
        try:
            result = super()._run_tool(call)
        finally:
            for n, run in originals.items():
                cli_tools.TOOLS[n].run = run
        self.events.append({"name": name, "args": _clip_args(args), "result": result[:3000], "t": t})
        return result

    def _approve(self, name):
        try:
            args = json.loads(self._call["function"]["arguments"] or "{}")
        except ValueError:
            args = {}
        if reason := policy(name, args if isinstance(args, dict) else {}, self.sandbox):
            self.blocked.append(reason)
            return f"Bu ortamda izin verilmiyor: {reason}"
        return True

    def _print_stats(self, usage, first):
        if usage:
            self.tokens += usage.completion_tokens or 0
            self.prompt_tokens += usage.prompt_tokens or 0
        super()._print_stats(usage, first)


def _clip_args(args: dict) -> dict:
    return {k: (v if not isinstance(v, str) or len(v) < 6000 else v[:6000] + "…") for k, v in args.items()}


# ---------------------------------------------------------------- LM Studio

def lms(cfg: dict, *args: str, timeout: float = 600) -> subprocess.CompletedProcess:
    try:
        return subprocess.run([ai.lms_path(cfg), *args], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(e.cmd, 1, "", "zaman aşımı")


def loaded(cfg: dict) -> list[dict] | None:
    models = ai.server_models(cfg["base_url"])
    return None if models is None else [m for m in models if m.get("state") == "loaded"]


def ensure_server(cfg: dict) -> bool:
    if loaded(cfg) is not None:
        return True
    lms(cfg, "server", "start", timeout=120)
    for _ in range(30):
        if loaded(cfg) is not None:
            return True
        time.sleep(2)
    return False


def load_preset(cfg: dict, preset: str) -> tuple[str, int | None]:
    p = cfg["presets"][preset]
    last = ""
    for attempt in range(3):
        ensure_server(cfg)
        lms(cfg, "unload", "--all", timeout=120)
        time.sleep(3 + 5 * attempt)
        r = lms(cfg, "load", p["model"], *p.get("args", []), "-y")
        info = next((m for m in loaded(cfg) or [] if m["id"] == p["model"]), None)
        if r.returncode == 0 and info:
            return info["id"], info.get("loaded_context_length")
        last = (r.stderr or r.stdout).strip()[-300:]
        log(f"    yükleme denemesi {attempt + 1} başarısız: {last}")
    raise RuntimeError(f"{preset} yüklenemedi: {last}")


def model_ready(cfg: dict, model_id: str) -> bool:
    return any(m["id"] == model_id for m in loaded(cfg) or [])


def supports_thinking(client: OpenAI, model: str) -> bool:
    try:
        r = client.chat.completions.create(model=model, max_tokens=512, seed=SEED,
                                           messages=[{"role": "user", "content": "2+2 kaç eder? Tek kelimeyle cevap ver."}])
    except Exception as e:  # sessizce "desteklemiyor" demesin: otomatik mod koşusu boşuna atlanır
        log(f"    düşünme desteği sınanamadı: {type(e).__name__}: {str(e)[:150]}")
        return False
    msg = r.choices[0].message
    return bool((getattr(msg, "reasoning_content", None) or "").strip()) or "<think>" in (msg.content or "")


def keep_awake() -> None:
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED


# ---------------------------------------------------------------- görev çalıştırma

def grade_safely(task: core.Task, sandbox: Path, final: str, trace: Trace) -> tuple[float, str, list]:
    try:
        rub = task.grade(sandbox, final, trace)
        return rub.score, rub.detail(), rub.to_json()
    except Exception as e:
        return 0.0, f"notlandırıcı hatası: {type(e).__name__}: {e}"[:300], [["notlandırıcı", 1, 0, traceback.format_exc()[-400:]]]


def run_dir(model_id: str, mode: str) -> str:
    """Cevap ve sandbox klasörünün adı. Hazır ayar adı değil model kimliği: adlar yeniden atanınca
    (eski knight bugün bishop) yeni modelin koşusu eskisinin kayıtlarını ezmesin."""
    name = re.sub(r"\.gguf$", "", model_id.rstrip("/").rsplit("/", 1)[-1])
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name) + f"__{mode}"


def attempt(client, cfg: dict, preset: str, model_id: str, ctx: int | None, mode: str, task: core.Task) -> dict:
    sandbox = RESULTS / "sandboxes" / run_dir(model_id, mode) / task.id
    fresh_dir(sandbox)
    task.setup(sandbox)
    # Hep düşünen modeller (thinking: "always") kapalı modda da düşünür: otomatik moddaki çıktı payını alır
    always = cfg["presets"].get(preset, {}).get("thinking") == "always"
    extra = {"max_tokens": MAX_TOKENS["auto" if always else mode], "seed": SEED}
    if not SERVER_SAMPLING:
        sp = SAMPLING.get(model_id, QWEN_SAMPLING)
        extra.update(temperature=sp["temperature"], top_p=sp["top_p"],
                     extra_body={"top_k": sp["top_k"], "min_p": 0.0, "repeat_penalty": 1.0})
    completions = _Completions(client.chat.completions, extra)
    capped = types.SimpleNamespace(chat=types.SimpleNamespace(completions=completions))
    args = argparse.Namespace(no_tools=not task.tools, think=False if mode == "off" else None, show_think=False,
                              yes=False, auto_think=mode == "auto")
    buf = io.StringIO()
    ai.console = Console(file=buf, width=150, force_terminal=False, color_system=None, highlight=False, soft_wrap=True)
    previous = os.getcwd()
    os.chdir(sandbox)
    started = time.perf_counter()
    crash = ""
    try:
        chat = GambitBench(capped, {**cfg, "max_steps": MAX_STEPS}, cfg["base_url"], args, sandbox=sandbox,
                           deadline=started + (NO_LIMIT_CAP if NO_LIMIT else BUDGET[task.tools]))
        completions.bench = chat
        chat.model, chat.ctx = model_id, ctx
        chat.messages[0]["content"] = chat.system_prompt()  # gerçek CLI'daki gibi: mod adı (knight, queen...) istemde
        try:
            chat.ask(task.prompt)
        except Exception as e:
            crash = f"{type(e).__name__}: {e}"[:300]
    finally:
        os.chdir(previous)
    wall = time.perf_counter() - started
    final = next((m.get("content") or "" for m in reversed(chat.messages) if m["role"] == "assistant"), "")
    trace = Trace(events=chat.events, final=final)
    score, detail, items = grade_safely(task, sandbox, final, trace)
    notes = []
    if chat.timed_out:
        notes.append("süre sınırı")
    if chat.server_error:
        notes.append(f"sunucu: {chat.server_error[:120]}")
    if crash:
        notes.append(f"çökme: {crash[:120]}")
    if chat.blocked:
        notes.append("engellenen: " + " | ".join(b[:60] for b in chat.blocked[:2]))
    if mode == "auto" and chat.think_calls:
        notes.append(f"düşünme {chat.think_calls}/{chat.calls} adımda açık")
    result = {
        "preset": preset, "model_id": model_id, "mode": mode, "task": task.id, "category": task.category,
        "level": task.level, "weight": task.weight, "score": round(score, 4), "detail": detail,
        "notes": "; ".join(notes), "items": items, "wall": round(wall, 1), "tokens": chat.tokens,
        "prompt_tokens": chat.prompt_tokens, "calls": chat.calls, "think_calls": chat.think_calls,
        "tool_calls": len(chat.events), "timed_out": chat.timed_out, "server_error": chat.server_error,
        "crash": crash, "time": datetime.now().isoformat(timespec="seconds"),
        "time_limit": NO_LIMIT_CAP if NO_LIMIT else BUDGET[task.tools], "seed": SEED,
        "sampling": "sunucu" if SERVER_SAMPLING else "sabit",
        **({"host": "uzak"} if REMOTE else {}),
    }
    folder = RESULTS / "responses" / run_dir(model_id, mode)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{task.id}.json").write_text(json.dumps({
        "result": result, "final": final, "events": chat.events, "messages": chat.messages,
    }, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (folder / f"{task.id}.log").write_text(buf.getvalue(), encoding="utf-8")
    return result


def remote_wait(cfg: dict, model_id: str, minutes: int = 20) -> bool:
    """Uzak sunucu (ya da SSH tüneli) geri gelene kadar bekler; yerelde LM Studio'ya hiç dokunmaz."""
    for _ in range(minutes * 6):
        if model_ready(cfg, model_id):
            return True
        time.sleep(10)
    return False


def run_task(client, cfg: dict, preset: str, model_id: str, ctx, mode: str, task: core.Task) -> dict:
    for n in range(3):
        if REMOTE and not model_ready(cfg, model_id):
            log(f"    uzak sunucuya ulaşılamıyor; geri gelmesi bekleniyor…")
            if not remote_wait(cfg, model_id):
                raise RuntimeError("uzak sunucu 20 dakikadır yanıt vermiyor")
        elif not model_ready(cfg, model_id):
            log(f"    model yüklü değil; yeniden yükleniyor…")
            model_id, ctx = load_preset(cfg, preset)
        res = attempt(client, cfg, preset, model_id, ctx, mode, task)
        broken = res["server_error"] and ("bağlantı" in res["server_error"] or not model_ready(cfg, model_id)
                                          or any(w in res["server_error"].lower() for w in ("crash", "unload", "not loaded", "exit code")))
        if not broken or n == 2:
            return res
        log(f"    sunucu/model sorunu ({res['server_error'][:100]}); görev yeniden denenecek")
        if not REMOTE:
            ensure_server(cfg)
        time.sleep(10)
    return res


def write_status(**kw) -> None:
    try:
        (RESULTS / "durum.json").write_text(json.dumps({**kw, "guncelleme": datetime.now().isoformat(timespec="seconds")},
                                                       ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        pass


def build_report() -> None:
    try:
        import rapor
        rapor.build(RESULTS)
    except Exception as e:
        log(f"(rapor üretilemedi: {type(e).__name__}: {e})")


def run_plan(plan: list[tuple[str, str]], tasks: list[core.Task]) -> int:
    cfg = ai.load_config()
    if REMOTE:
        cfg["base_url"] = REMOTE
    key_file = HERE / "uzak_anahtar.txt"  # git'e girmez; anahtar sohbete yazılmasın diye dosyadan okunur
    key = (os.environ.get("GAMBIT_REMOTE_KEY") or (key_file.read_text(encoding="utf-8").strip()
                                                     if key_file.is_file() else "")) if REMOTE else cfg.get("api_key")
    client = OpenAI(base_url=cfg["base_url"], api_key=key or "lm-studio", timeout=900, max_retries=0)
    keep_awake()
    if REMOTE:
        try:
            log(f"uzak sunucu: {REMOTE} · modeller: {[m.id for m in client.models.list().data]}")
        except Exception as e:
            log(f"Uzak sunucuya bağlanılamadı ({REMOTE}): {type(e).__name__}: {str(e)[:200]}")
            return 1
    elif not ensure_server(cfg):
        log("LM Studio sunucusu başlatılamadı.")
        return 1
    results_file = RESULTS / "results.jsonl"
    # Model kimliğiyle eşlenir: hazır ayar adları değişebilir (eski knight bugün bishop), modelin sonucu ise aynı kalır
    done = {(r.get("model_id"), r["mode"], r["task"]) for r in load_jsonl(results_file)}
    current = None
    model_id = ctx = None
    total_started = time.perf_counter()
    completed = False
    try:
        for ci, (preset, mode) in enumerate(plan, 1):
            todo = [t for t in tasks if (cfg["presets"].get(preset, {}).get("model"), mode, t.id) not in done]
            if not todo:
                continue
            if not cfg["presets"].get(preset, {}).get("model"):
                log(f"!!! bilinmeyen ya da boş hazır ayar: {preset}")
                continue
            if current != preset:
                log(f"\n=== {preset} yükleniyor…")
                try:
                    t0 = time.perf_counter()
                    if REMOTE:  # uzakta tek model zaten yüklü; kayıtlar yerel koşularla eşleşsin diye aynı kimlik
                        pargs = cfg["presets"][preset].get("args", [])
                        model_id = cfg["presets"][preset]["model"]
                        ctx = int(pargs[pargs.index("-c") + 1]) if "-c" in pargs else None
                    else:
                        model_id, ctx = load_preset(cfg, preset)
                    log(f"=== {preset} hazır ({time.perf_counter() - t0:.0f} sn, bağlam {ctx})")
                    current = preset
                except RuntimeError as e:
                    log(f"!!! {e}")
                    append_jsonl(RESULTS / "configs.jsonl", {"preset": preset, "mode": mode, "status": "yüklenemedi",
                                                             "reason": str(e)[:300]})
                    current = None
                    continue
            thinking = supports_thinking(client, model_id) and cfg["presets"][preset].get("thinking", True)
            if mode == "auto" and not thinking:
                log(f"--- {preset}/auto atlandı: model düşünmeyi desteklemiyor")
                continue
            append_jsonl(RESULTS / "configs.jsonl", {"preset": preset, "model_id": model_id, "mode": mode, "ctx": ctx,
                                                     "thinking_supported": thinking, "status": "başladı",
                                                     "time": datetime.now().isoformat(timespec="seconds")})
            log(f"--- {preset}/{mode}: {len(todo)} görev")
            started = time.perf_counter()
            for i, task in enumerate(todo, 1):
                write_status(yapilandirma=f"{preset}/{mode}", sira=f"{ci}/{len(plan)}", gorev=task.id,
                             ilerleme=f"{i}/{len(todo)}", baslangic=datetime.now().isoformat(timespec="seconds"))
                try:
                    r = run_task(client, cfg, preset, model_id, ctx, mode, task)
                except Exception as e:  # çalıştırıcının kendisinde beklenmeyen hata: görevi sıfırla, devam et
                    log(f"    beklenmeyen hata: {type(e).__name__}: {e}")
                    r = {"preset": preset, "model_id": model_id, "mode": mode, "task": task.id, "category": task.category,
                         "level": task.level, "weight": task.weight, "score": 0.0, "detail": f"çalıştırıcı hatası: {e}"[:300],
                         "notes": "", "items": [], "wall": 0.0, "tokens": 0, "prompt_tokens": 0, "calls": 0,
                         "think_calls": 0, "tool_calls": 0, "timed_out": False, "server_error": "", "crash": str(e)[:200],
                         "time": datetime.now().isoformat(timespec="seconds")}
                append_jsonl(results_file, r)
                log(f"[{preset}/{mode} {i}/{len(todo)}] {task.id:24} {100 * r['score']:5.1f} (x{task.weight:g}) "
                    f"{r['wall']:6.1f} sn {r['tokens']:6} tok {r['tool_calls']:3} araç  {r['detail'][:80]}"
                    + (f"  [{r['notes'][:80]}]" if r["notes"] else ""))
            append_jsonl(RESULTS / "configs.jsonl", {"preset": preset, "mode": mode, "status": "bitti",
                                                     "minutes": round((time.perf_counter() - started) / 60, 1),
                                                     "time": datetime.now().isoformat(timespec="seconds")})
            log(f"--- {preset}/{mode} bitti: {(time.perf_counter() - started) / 60:.1f} dk")
            build_report()
        completed = True
        log("\nTüm sonuçlar güncel notlandırıcılarla yeniden puanlanıyor…")
        regrade()
    finally:
        if not REMOTE:
            log("\nLM Studio'daki modeller boşaltılıyor…")
            lms(cfg, "unload", "--all", timeout=120)
        build_report()
        write_status(yapilandirma="bitti" if completed else "durdu",
                     toplam_dk=round((time.perf_counter() - total_started) / 60, 1))
    # yalnızca plan sonuna kadar gidildiyse; çökmede yazılmaz (calistir.ps1 yeniden başlatır)
    (RESULTS / "BITTI.txt").write_text(datetime.now().isoformat(timespec="seconds") + "\n", encoding="utf-8")
    return 0


# ---------------------------------------------------------------- öz-sınama ve yeniden puanlama

def _fake_trace(d: Path) -> Trace:
    events = [{"name": "write_file", "args": {"path": str(p)}, "result": "yazıldı"} for p in d.rglob("*") if p.is_file()]
    events.append({"name": "run_command", "args": {"command": "python -m py_compile x.py"}, "result": "çıkış kodu: 0"})
    return Trace(events=events)


def selftest(tasks: list[core.Task]) -> int:
    root = Path(tempfile.mkdtemp(prefix="gb2_selftest_"))
    failures = 0
    rows = []
    for t in tasks:
        d = root / t.id
        try:
            fresh_dir(d); t.setup(d)
            empty = t.grade(d, "", Trace()).score
            fresh_dir(d); t.setup(d)
            ans = t.reference(d) if t.reference else ""
            rub = t.grade(d, ans, _fake_trace(d))
            good, gdetail = rub.score, rub.detail()
            wrong = None
            if t.wrong:
                fresh_dir(d); t.setup(d)
                ans = t.wrong(d)
                wrong = t.grade(d, ans or "", _fake_trace(d)).score
        except Exception:
            failures += 1
            log(f"HATA {t.id}: {traceback.format_exc()[-800:]}")
            continue
        ok = good >= 0.999 and empty <= 0.35 and (wrong is None or 0.03 < wrong < 0.97)
        failures += not ok
        rows.append(t.id)
        log(f"{'OK  ' if ok else 'HATA'} {t.id:24} seviye={t.level} referans={good:.2f} boş={empty:.2f} "
            f"yanlış={'-' if wrong is None else format(wrong, '.2f')}  {'' if good >= 0.999 else gdetail[:200]}")
    shutil.rmtree(root, ignore_errors=True)
    cats = {}
    for t in tasks:
        cats[t.category] = cats.get(t.category, 0) + 1
    log(f"\n{len(tasks)} görev, toplam ağırlık {sum(t.weight for t in tasks):g} "
        f"({', '.join(f'{c}: {n}' for c, n in cats.items())}); {failures} hata")
    return 1 if failures else 0


def regrade() -> int:
    by_id = {t.id: t for t in TASKS}
    path = RESULTS / "results.jsonl"
    results = load_jsonl(path)
    changed = 0
    for r in results:
        t = by_id.get(r["task"])
        if not t:
            continue
        # önce model kimliğine göre klasör; yoksa eski düzen (hazır ayar adı), ama yalnızca kayıt aynı modele aitse
        for folder in (run_dir(r.get("model_id") or "", r["mode"]), f"{r['preset']}__{r['mode']}"):
            saved = RESULTS / "responses" / folder / f"{r['task']}.json"
            data = json.loads(saved.read_text(encoding="utf-8")) if saved.is_file() else None
            if data and data.get("result", {}).get("model_id") == r.get("model_id"):
                break
        else:
            continue
        sandbox = RESULTS / "sandboxes" / folder / t.id
        score, detail, items = grade_safely(t, sandbox, data.get("final", ""), Trace(events=data.get("events", []),
                                                                                       final=data.get("final", "")))
        if abs(round(score, 4) - r["score"]) > 1e-6:
            changed += 1
            log(f"{r['preset']}/{r['mode']} {t.id}: {100 * r['score']:.1f} → {100 * score:.1f}  {detail[:100]}")
        r.update(score=round(score, 4), detail=detail, items=items, weight=t.weight, level=t.level)
    tmp = path.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results), encoding="utf-8")
    tmp.replace(path)
    log(f"{len(results)} sonuç tarandı, {changed} puan değişti")
    build_report()
    return 0


def main() -> int:
    global RESULTS, NO_LIMIT, REMOTE, SEED, SERVER_SAMPLING
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", default=DEFAULT_PLAN, help="hazır_ayar:mod listesi (mod: off | auto)")
    ap.add_argument("--only", default="", help="yalnızca id'si bu öneklerle başlayan görevler (virgülle)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--regrade", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", default=str(HERE / "results"), help="sonuç klasörü")
    ap.add_argument("--no-time-limit", action="store_true",
                    help=f"görev süre sınırını kaldır (güvenlik tavanı {NO_LIMIT_CAP // 3600} saat)")
    ap.add_argument("--remote", default="", help="uzak OpenAI uyumlu sunucu adresi (…/v1); anahtar GAMBIT_REMOTE_KEY'de")
    ap.add_argument("--seed", type=int, default=SEED, help="örnekleme tohumu; tekrar turlarında farklı ver")
    ap.add_argument("--server-sampling", action="store_true",
                    help="örnekleme ayarlarını gönderme, sunucunun varsayılanlarını kullan (eski koşular böyleydi)")
    args = ap.parse_args()
    RESULTS = Path(args.out).resolve()
    NO_LIMIT = args.no_time_limit
    REMOTE, SEED = args.remote.rstrip("/"), args.seed
    SERVER_SAMPLING = args.server_sampling
    RESULTS.mkdir(parents=True, exist_ok=True)
    prefixes = tuple(p for p in args.only.split(",") if p)
    tasks = [t for t in TASKS if not prefixes or t.id.startswith(prefixes)]
    if args.selftest:
        return selftest(tasks)
    if args.regrade:
        return regrade()
    if args.report:
        build_report()
        return 0
    plan = []
    for item in args.plan.split(","):
        preset, _, mode = item.strip().partition(":")
        if mode not in MAX_TOKENS:
            log(f"geçersiz plan öğesi: {item}")
            return 1
        plan.append((preset, mode))
    log(f"Gambit Bench v2 · {len(tasks)} görev · plan: {', '.join(f'{p}/{m}' for p, m in plan)} · "
        f"{datetime.now():%Y-%m-%d %H:%M}" + (" · süre sınırı yok" if NO_LIMIT else "")
        + (f" · uzak: {REMOTE}" if REMOTE else "") + (f" · seed {SEED}" if SEED != 42 else "")
        + (" · sunucunun örnekleme ayarları" if SERVER_SAMPLING else ""))
    return run_plan(plan, tasks)


if __name__ == "__main__":
    sys.exit(main())
