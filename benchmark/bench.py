"""Yerel modelleri (LM Studio) düşünme kapalı ve açık olarak kodlama ve terminal görevlerinden geçirir.

  python bench.py                    # knight ve queen; düşünme kapalı ve açık
  python bench.py --models king      # başka hazır ayarlar (ai-cli/config.json'daki adlarla)
  python bench.py --modes off        # sadece düşünme kapalı
  python bench.py --only kod-,sql-   # sadece id'si bu öneklerle başlayan görevler
  python bench.py --no-load          # LM Studio'da şu an yüklü modelle çalış (hızlı deneme)
  python bench.py --selftest         # notlandırıcıları referans çözümlerle sına (model gerekmez)
  python bench.py --regrade          # kayıtlı cevapları güncel notlandırıcıyla yeniden puanla

Sonuçlar results/results.jsonl dosyasına eklenir; yarıda kesilen çalıştırma aynı komutla kaldığı yerden sürer.
Model cevapları results/responses, terminal ve ajan görevlerinin çalışma klasörleri results/sandboxes altında kalır."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import types
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parent / "ai-cli"))

import ai  # noqa: E402
import tools as cli_tools  # noqa: E402
from openai import OpenAI  # noqa: E402

import grading  # noqa: E402
from tasks import CATEGORIES, TASKS, Task, make_sql_db  # noqa: E402

RESULTS = HERE / "results"
RESULTS_FILE = RESULTS / "results.jsonl"
CONFIGS_FILE = RESULTS / "configs.jsonl"
MAX_TOKENS = {"off": 3072, "on": 8192, "auto": 8192}  # auto: CLI'ın otomatik düşünme modu
SEED = 42
AGENT_MAX_STEPS = 12
AGENT_TIME_BUDGET = 900  # saniye; aşıldıktan sonra yeni model çağrısı yapılmaz
SYSTEM = "Sen deneyimli bir yazılım geliştiricisin. Görevi dikkatle çöz ve cevabını tam olarak istenen biçimde ver."

_expected: dict[str, str] = {}
LAST_EXEC: dict = {}  # son notlandırmada komut/sorgu hatası: {"error": metin, "failed": çıkış kodu sıfırdan farklı mı}
FEEDBACK = False  # --feedback: SQL/terminal görevlerinde hata modele gösterilir ve bir kez daha denenir


def expected_output(task: Task) -> str:
    if task.id not in _expected:
        _expected[task.id] = grading.run_snippet(task.snippet, task.lang)
    return _expected[task.id]


def set_results_dir(path: Path) -> None:
    global RESULTS, RESULTS_FILE, CONFIGS_FILE
    RESULTS = path.resolve()
    RESULTS_FILE = RESULTS / "results.jsonl"
    CONFIGS_FILE = RESULTS / "configs.jsonl"


def fresh_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------------------------------------------------------------- notlandırma

def grade_answer(task: Task, answer: str, sandbox: Path) -> tuple[float, str, str]:
    """(puan, açıklama, cevaptan çıkarılan kod/komut). Komut ya da sorgu çalışırken hata verdiyse
    LAST_EXEC'e yazılır (geri bildirimli denemede modele gösterilmek üzere)."""
    LAST_EXEC.clear()
    name = re.escape(task.entry)
    if task.kind == "python":
        src = grading.extract_code(answer, "python", rf"^\s*(?:def|class)\s+{name}\b|^{name}\s*=", longest=True)
        return *grading.grade_python(src, task.tests, task.prelude, task.forbid), src
    if task.kind == "js":
        defines = (rf"function\s+{name}\b|\b(?:const|let|var)\s+{name}\s*=|\b{name}\s*:\s*(?:async\s+)?(?:function\b|\()"
                   rf"|exports\.{name}\s*=|^\s*(?:async\s+)?{name}\s*\([^)]*\)\s*\{{")
        src = grading.extract_code(answer, "js", defines, longest=True)
        return *grading.grade_js(src, task.tests, task.prelude, task.entry), src
    if task.kind == "output":
        return *grading.grade_output(answer, expected_output(task)), grading.extract_code(answer, "text")
    if task.kind == "sql":
        src = grading.extract_code(answer, "sql")
        score, detail = grading.grade_sql(src, task.reference, make_sql_db)
        if detail.startswith("SQL hatası"):
            LAST_EXEC.update(error=detail, failed=True)
        return score, detail, src
    if task.kind == "shell":
        cmd = grading.extract_code(answer, "powershell")
        fresh_dir(sandbox)
        task.setup(sandbox)
        if not cmd.strip():
            return 0.0, "cevapta komut yok", cmd
        if reason := grading.shell_safety(cmd, sandbox):
            return 0.0, f"çalıştırılmadı ({reason})", cmd
        rc, out, err, timed_out = grading.run_powershell(cmd, sandbox)
        if timed_out:
            return 0.0, "zaman aşımı", cmd
        if rc != 0 or err.strip():
            LAST_EXEC.update(error=f"çıkış kodu: {rc}\n{out.strip()}\n[stderr]\n{err.strip()}"[-1500:], failed=rc != 0)
        score, detail = task.check(sandbox, out)
        if score < 1 and err.strip():
            detail += f"; hata: {err.strip()[-200:]}"
        return score, detail, cmd
    raise ValueError(task.kind)


# ---------------------------------------------------------------- model çağrıları

def ask_once(client: OpenAI, model: str, mode: str, prompt: str, thinking_supported: bool,
             history: list[dict] | None = None, think: bool | None = None) -> dict:
    kwargs = {
        "model": model, "stream": True, "stream_options": {"include_usage": True},
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}, *(history or [])],
        "max_tokens": MAX_TOKENS[mode], "seed": SEED,
    }
    if think is None:
        think = mode == "on" or (mode == "auto" and ai.analysis_question(prompt))
    if thinking_supported and not think:
        kwargs["reasoning_effort"] = "none"
    start = time.perf_counter()
    first = usage = finish = None
    content, reasoning = [], []
    for chunk in client.chat.completions.create(**kwargs):
        usage = chunk.usage or usage
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        delta = choice.delta
        thought = getattr(delta, "reasoning_content", None) or getattr(delta, "reasoning", None)
        if thought:
            reasoning.append(thought)
            first = first or time.perf_counter()
        if delta.content:
            content.append(delta.content)
            first = first or time.perf_counter()
        finish = choice.finish_reason or finish
    end = time.perf_counter()
    text, thought = "".join(content), "".join(reasoning)
    if m := re.match(r"\s*<think>(.*?)</think>(.*)$", text, re.S):  # düşünce içerikte etiketle geldiyse ayır
        thought, text = thought + m.group(1), m.group(2)
    return {
        "answer": text.strip() or thought.strip(),  # CLI'daki gibi: içerik boşsa düşünce cevap sayılır
        "content": text, "reasoning": thought,
        "tokens": usage.completion_tokens if usage else 0,
        "wall": end - start, "ttft": (first - start) if first else None, "gen": (end - first) if first else None,
        "truncated": finish == "length",
    }


class CappedCompletions:
    """CLI'ın her model çağrısına benchmark'ın token sınırını ve seed'ini ekler."""

    def __init__(self, inner, extra: dict):
        self.inner, self.extra = inner, extra

    def create(self, **kwargs):
        return self.inner.create(**{**self.extra, **kwargs})


def agent_policy(name: str, args: dict, sandbox: Path) -> str | None:
    """Ajanın yazma ve komut isteklerini kullanıcı yerine değerlendirir; izin yoksa nedenini döndürür."""
    if name in ("write_file", "edit_file"):
        path = cli_tools._path(str(args.get("path", "")))
        return None if path.is_relative_to(sandbox.resolve()) else f"klasör dışına yazma: {path}"
    if name == "run_command":
        cmd = str(args.get("command", ""))
        return grading.shell_safety(cmd, sandbox) or grading.python_danger(cmd)
    return None


class BenchChat(ai.Chat):
    """CLI'ın ajan döngüsünün aynısı; onaylar güvenlik kuralıyla verilir, süre ve token sayılır."""

    def __init__(self, *args, sandbox: Path, **kwargs):
        super().__init__(*args, **kwargs)
        self.sandbox = sandbox
        self.started = time.perf_counter()
        self.tokens = 0
        self.tool_calls = 0
        self.blocked: list[str] = []
        self.timed_out = False

    def _complete(self):
        if time.perf_counter() - self.started > AGENT_TIME_BUDGET:
            self.timed_out = True
            raise KeyboardInterrupt  # Chat.ask bunu "durduruldu" olarak işler
        return super()._complete()

    def _run_tool(self, call):
        self._call = call
        self.tool_calls += 1
        return super()._run_tool(call)

    def _approve(self, name):
        try:
            args = json.loads(self._call["function"]["arguments"] or "{}")
        except ValueError:
            args = {}
        if reason := agent_policy(name, args, self.sandbox):
            self.blocked.append(reason)
            return f"Bu ortamda izin verilmiyor: {reason}"
        return True

    def _print_stats(self, usage, first):
        if usage:
            self.tokens += usage.completion_tokens
        super()._print_stats(usage, first)


def run_agent(client: OpenAI, cfg: dict, model: str, ctx: int | None, mode: str, task: Task, sandbox: Path,
              thinking_supported: bool) -> dict:
    fresh_dir(sandbox)
    task.setup(sandbox)
    extra = {"max_tokens": MAX_TOKENS[mode], "seed": SEED}
    capped = types.SimpleNamespace(chat=types.SimpleNamespace(completions=CappedCompletions(client.chat.completions, extra)))
    args = argparse.Namespace(no_tools=False, think=mode == "on" or not thinking_supported, show_think=False, yes=False,
                              auto_think=mode == "auto" and thinking_supported)
    previous = os.getcwd()
    os.chdir(sandbox)
    try:
        chat = BenchChat(capped, {**cfg, "max_steps": AGENT_MAX_STEPS}, cfg["base_url"], args, sandbox=sandbox)
        chat.model, chat.ctx = model, ctx
        start = time.perf_counter()
        chat.ask(task.prompt)
        wall = time.perf_counter() - start
    finally:
        os.chdir(previous)
    final = next((m.get("content") or "" for m in reversed(chat.messages) if m["role"] == "assistant"), "")
    score, detail = task.check(sandbox, final)
    if chat.escalations:
        detail += "; komut başarısız olunca düşünme otomatik açıldı"
    if chat.timed_out:
        detail += "; süre sınırına ulaşıldı"
    if chat.blocked:
        detail += "; engellenen istekler: " + " | ".join(chat.blocked[:3])
    return {"score": score, "detail": detail, "tokens": chat.tokens, "wall": wall, "tool_calls": chat.tool_calls,
            "answer": final, "transcript": chat.messages}


def save_response(key: str, mode: str, task: Task, result: dict, extra: dict) -> None:
    folder = RESULTS / "responses" / f"{key}__{mode}"
    folder.mkdir(parents=True, exist_ok=True)
    if "transcript" in extra:
        (folder / f"{task.id}.json").write_text(json.dumps(extra["transcript"], ensure_ascii=False, indent=1),
                                                encoding="utf-8")
        return
    parts = [f"# {task.id} · puan {result['score']:.2f}", f"**Not:** {result['detail']}", "## Prompt", task.prompt]
    if extra.get("reasoning"):
        parts += ["## Düşünme", extra["reasoning"]]
    parts += ["## Cevap", extra.get("content") or "(boş)"]
    if extra.get("extracted"):
        parts += ["## Notlandırılan kod/komut", f"```\n{extra['extracted']}\n```"]
    (folder / f"{task.id}.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")


def retry_with_feedback(client: OpenAI, model: str, mode: str, task: Task, sandbox: Path, thinking_supported: bool,
                        first: dict, result: dict, extra: dict) -> None:
    """CLI'daki gibi: komut/sorgu hata verince hata modele gösterilir ve bir kez daha dener. Otomatik modda,
    CLI'daki kuralla aynı şekilde, hata bir başarısızlıksa (sıfır olmayan çıkış kodu, SQL hatası) düşünme açılır."""
    what = "komut" if task.kind == "shell" else "sorgu"
    feedback = (f"Bu {what} çalıştırılınca şu sonuç alındı:\n```\n{LAST_EXEC['error']}\n```\n"
                f"Hatayı düzelt ve düzeltilmiş {what}u ilk istekteki biçimde ver.")
    escalate = mode == "auto" and LAST_EXEC.get("failed", False)
    think = mode == "on" or escalate
    history = [{"role": "assistant", "content": first["content"] or first["answer"]}, {"role": "user", "content": feedback}]
    second = ask_once(client, model, mode, task.prompt, thinking_supported, history=history, think=think)
    score, detail, extracted = grade_answer(task, second["answer"], sandbox)
    notes = ["2. deneme"] + (["düşünme otomatik açıldı"] if escalate else [])
    if second["truncated"]:
        detail += "; token sınırında kesildi"
    result.update(score=score, detail=f"{', '.join(notes)}: {detail}", tokens=result["tokens"] + second["tokens"],
                  wall=result["wall"] + second["wall"], gen=(result.get("gen") or 0) + (second["gen"] or 0),
                  reasoning_chars=result["reasoning_chars"] + len(second["reasoning"]),
                  truncated=result["truncated"] or second["truncated"], retried=True)
    extra.update(reasoning=extra["reasoning"] + "\n\n--- 2. deneme ---\n\n" + second["reasoning"],
                 content=extra["content"] + f"\n\n--- Geri bildirim ---\n\n{feedback}\n\n--- 2. deneme ---\n\n"
                 + second["content"], extracted=extracted)


def run_task(client: OpenAI, cfg: dict, key: str, model: str, ctx: int | None, mode: str, task: Task,
             thinking_supported: bool) -> dict:
    sandbox = RESULTS / "sandboxes" / f"{key}__{mode}" / task.id
    result = {"model": key, "model_id": model, "mode": mode, "task": task.id, "category": task.category,
              "title": task.title, "time": datetime.now().isoformat(timespec="seconds")}
    extra: dict = {}
    try:
        if task.kind == "agent":
            out = run_agent(client, cfg, model, ctx, mode, task, sandbox, thinking_supported)
            extra = {"transcript": out.pop("transcript")}
            out.pop("answer")
            result.update(out)
        else:
            out = ask_once(client, model, mode, task.prompt, thinking_supported)
            score, detail, extracted = grade_answer(task, out["answer"], sandbox)
            if out["truncated"]:
                detail += "; token sınırında kesildi"
            extra = {"reasoning": out["reasoning"], "content": out["content"], "extracted": extracted}
            result.update(score=score, detail=detail, tokens=out["tokens"], wall=out["wall"], ttft=out["ttft"],
                          gen=out["gen"], reasoning_chars=len(out["reasoning"]), truncated=out["truncated"])
            if FEEDBACK and task.kind in ("shell", "sql") and score < 1 and LAST_EXEC.get("error"):
                retry_with_feedback(client, model, mode, task, sandbox, thinking_supported, out, result, extra)
    except Exception as e:  # sunucu hatası vb.; görev sıfır alır, çalıştırma sürer
        result.update(score=0.0, detail=f"çalıştırma hatası: {type(e).__name__}: {e}"[:300], tokens=0, wall=0.0)
    save_response(key, mode, task, result, extra)
    return result


# ---------------------------------------------------------------- LM Studio

# Sonuçlarda her model sabit bir anahtarla tutulur; CLI'daki hazır ayar adları değişse de eski sonuçlarla eşleşir
RESULT_KEYS = {
    "qwen3.5-9b": "9b",
    "google/gemma-4-26b-a4b-it-qat-q4_0-gguf/gemma-4-26b_q4_0-it.gguf": "gemma",
    "qwen3-coder-30b-a3b-instruct": "coder30",
    "gemma-4-12b-coder-fable5-composer2.5-v1": "gemma12",
    "qwen3.8-27b": "27b",
    "qwen3.5-4b": "4b",
    "qwen2.5-coder-3b-instruct-128k": "coder",
}


def result_key(cfg: dict, preset: str) -> str:
    model = cfg["presets"].get(preset, {}).get("model", preset)
    return RESULT_KEYS.get(model, preset)


def lms(cfg: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([ai.lms_path(cfg), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def loaded_models(cfg: dict) -> list[dict]:
    return [m for m in (ai.server_models(cfg["base_url"]) or []) if m.get("state") == "loaded"]


def load_preset(cfg: dict, key: str) -> tuple[str, int | None, float]:
    preset = cfg["presets"][key]
    start = time.perf_counter()
    lms(cfg, "unload", "--all")
    r = lms(cfg, "load", preset["model"], *preset.get("args", []))
    loaded = loaded_models(cfg)
    info = next((m for m in loaded if m["id"] == preset["model"]), None)
    if r.returncode != 0 or not info:
        raise RuntimeError(f"{key} yüklenemedi: {(r.stderr or r.stdout).strip()[-300:]}")
    return info["id"], info.get("loaded_context_length"), time.perf_counter() - start


def restore(cfg: dict, model_ids: list[str]) -> None:
    lms(cfg, "unload", "--all")
    for model_id in model_ids:
        preset = next((p for p in cfg["presets"].values() if p["model"] == model_id), None)
        lms(cfg, "load", model_id, *(preset.get("args", []) if preset else []))


def keep_awake() -> None:
    """Çalıştırma sürdükçe Windows'un boşta uykuya geçmesini engeller; süreç bitince kendiliğinden kalkar."""
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED


def supports_thinking(client: OpenAI, model: str) -> bool:
    r = client.chat.completions.create(model=model, max_tokens=512, seed=SEED,
                                       messages=[{"role": "user", "content": "2+2 kaç eder? Tek kelimeyle cevap ver."}])
    msg = r.choices[0].message
    return bool((getattr(msg, "reasoning_content", None) or "").strip()) or "<think>" in (msg.content or "")


# ---------------------------------------------------------------- çalıştırma

def summarize(results: list[dict]) -> None:
    configs: dict[tuple, dict] = {}
    for r in results:
        configs.setdefault((r["model"], r["mode"]), {}).setdefault(r["category"], []).append(r["score"])
    print(f"\n{'model/düşünme':16}" + "".join(f"{c[:10]:>12}" for c in CATEGORIES) + f"{'GENEL':>9}")
    for (model, mode), cats in configs.items():
        means = [100 * sum(cats[c]) / len(cats[c]) if c in cats else None for c in CATEGORIES]
        known = [m for m in means if m is not None]
        print(f"{model + '/' + mode:16}" + "".join(f"{m:12.0f}" if m is not None else f"{'-':>12}" for m in means)
              + f"{sum(known) / len(known):9.1f}")


def parse_saved(md: str) -> tuple[str, str]:
    """save_response'un yazdığı dosyadan (cevap içeriği, düşünme) geri okur."""
    def section(title: str, until: str) -> str:
        head = f"\n\n## {title}\n\n"
        start = md.find(head)
        if start < 0:
            return ""
        start += len(head)
        end = md.find(f"\n\n## {until}\n\n", start)
        return md[start:end] if end >= 0 else md[start:].rstrip("\n")
    content = section("Cevap", "Notlandırılan kod/komut")
    return ("" if content == "(boş)" else content), section("Düşünme", "Cevap")


def regrade() -> int:
    """Tek adımlı görevleri kayıtlı cevaplardan güncel notlandırıcıyla yeniden puanlar (modele tekrar sormadan)."""
    by_id = {t.id: t for t in TASKS}
    results = load_jsonl(RESULTS_FILE)
    changed = 0
    for r in results:
        task = by_id.get(r["task"])
        if not task or task.kind == "agent" or r.get("detail", "").startswith("çalıştırma hatası"):
            continue
        saved = RESULTS / "responses" / f"{r['model']}__{r['mode']}" / f"{task.id}.md"
        if not saved.is_file():
            continue
        content, reasoning = parse_saved(saved.read_text(encoding="utf-8"))
        sandbox = RESULTS / "sandboxes" / f"{r['model']}__{r['mode']}" / task.id
        score, detail, extracted = grade_answer(task, content.strip() or reasoning.strip(), sandbox)
        if r.get("truncated"):
            detail += "; token sınırında kesildi"
        if abs(score - r["score"]) > 1e-9:
            changed += 1
            print(f"{r['model']}/{r['mode']} {task.id}: {r['score']:.2f} → {score:.2f}  {detail[:100]}", flush=True)
        r.update(score=score, detail=detail)
        save_response(r["model"], r["mode"], task, r, {"reasoning": reasoning, "content": content, "extracted": extracted})
    tmp = RESULTS_FILE.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results), encoding="utf-8")
    tmp.replace(RESULTS_FILE)
    print(f"{len(results)} sonuç tarandı, {changed} puan değişti")
    summarize(results)
    return 0


def selftest() -> int:
    """Her görevin notlandırıcısını referans çözümle (tam puan beklenir) ve yanlış bir cevapla dener."""
    failures = 0
    root = RESULTS / "_selftest"
    for t in TASKS:
        d = root / t.id
        if t.kind == "agent":
            fresh_dir(d)
            t.setup(d)
            bad, _ = t.check(d, "")
            fresh_dir(d)
            t.setup(d)
            t.apply_reference(d)
            good, detail = t.check(d, "")
        elif t.kind == "shell":
            fresh_dir(d)
            t.setup(d)
            bad, _ = t.check(d, "")
            good, detail, _ = grade_answer(t, f"```powershell\n{t.reference}\n```", d)
        elif t.kind == "output":
            good, detail, _ = grade_answer(t, f"```text\n{expected_output(t)}\n```", d)
            bad = grade_answer(t, "```text\nyanlış\n```", d)[0]
            detail = f"beklenen çıktı: {expected_output(t).strip()!r}"
        elif t.kind == "sql":
            good, detail, _ = grade_answer(t, f"```sql\n{t.reference}\n```", d)
            bad = grade_answer(t, "```sql\nSELECT 1\n```", d)[0]
        else:
            fence = "python" if t.kind == "python" else "javascript"
            good, detail, _ = grade_answer(t, f"```{fence}\n{t.reference}\n```", d)
            bad = grade_answer(t, f"```{fence}\n{t.buggy}\n```", d)[0] if t.buggy else 0.0
        ok = good == 1.0 and bad < 1.0
        failures += not ok
        print(f"{'OK  ' if ok else 'HATA'} {t.id:20} referans={good:.2f} yanlış={bad:.2f}  {detail[:150]}", flush=True)
    shutil.rmtree(root, ignore_errors=True)
    print(f"\n{len(TASKS)} görev ({', '.join(f'{c}: {sum(t.category == c for t in TASKS)}' for c in CATEGORIES)}), "
          f"{failures} hata")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default="knight,queen", help="ai-cli/config.json'daki hazır ayar adları")
    ap.add_argument("--modes", default="off,on", help="off: düşünme kapalı, on: açık")
    ap.add_argument("--only", default="", help="sadece id'si bu öneklerle başlayan görevler (virgülle)")
    ap.add_argument("--no-load", action="store_true", help="modeli yükleme; LM Studio'da yüklü olanı kullan")
    ap.add_argument("--selftest", action="store_true", help="notlandırıcıları referans çözümlerle sına")
    ap.add_argument("--regrade", action="store_true", help="kayıtlı cevapları güncel notlandırıcıyla yeniden puanla")
    ap.add_argument("--feedback", action="store_true",
                    help="SQL/terminal görevlerinde hata modele gösterilir ve bir kez daha dener (CLI'daki gibi)")
    ap.add_argument("--out", default=str(RESULTS), help="sonuç klasörü (varsayılan: results)")
    args = ap.parse_args()
    set_results_dir(Path(args.out))
    global FEEDBACK
    FEEDBACK = args.feedback
    if args.selftest:
        return selftest()
    if args.regrade:
        return regrade()

    cfg = ai.load_config()
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg.get("api_key") or "lm-studio", timeout=3600, max_retries=0)
    prefixes = tuple(p for p in args.only.split(",") if p)
    tasks = [t for t in TASKS if not prefixes or t.id.startswith(prefixes)]
    modes = [m for m in args.modes.split(",") if m in MAX_TOKENS]
    done = {(r["model"], r["mode"], r["task"]) for r in load_jsonl(RESULTS_FILE)}
    initial = [m["id"] for m in loaded_models(cfg)]
    if args.no_load:
        if not initial:
            print("LM Studio'da yüklü model yok.")
            return 1
        keys = [next((k for k, p in cfg["presets"].items() if p["model"] == initial[0]), initial[0])]
    else:
        keys = [k for k in args.models.split(",") if k]
        if unknown := [k for k in keys if k not in cfg["presets"]]:
            print(f"Bilinmeyen hazır ayar: {', '.join(unknown)}")
            return 1

    keep_awake()
    try:
        for preset in keys:
            key = result_key(cfg, preset)
            pending = [(mode, t) for mode in modes for t in tasks if (key, mode, t.id) not in done]
            if not pending:
                continue
            if args.no_load:
                info = loaded_models(cfg)[0]
                model, ctx, load_s = info["id"], info.get("loaded_context_length"), 0.0
            else:
                print(f"\n=== {key} yükleniyor…", flush=True)
                try:
                    model, ctx, load_s = load_preset(cfg, preset)
                except RuntimeError as e:
                    print(e, flush=True)
                    continue
            thinking = supports_thinking(client, model)
            print(f"=== {key}: {model} (bağlam {ctx}, yükleme {load_s:.0f} sn, düşünme desteği: "
                  f"{'var' if thinking else 'yok'})", flush=True)
            for mode in modes:
                todo = [t for m, t in pending if m == mode]
                if not todo:
                    continue
                if mode == "on" and not thinking:
                    append_jsonl(CONFIGS_FILE, {"model": key, "model_id": model, "mode": mode, "skipped": True,
                                                "reason": "model düşünme modunu desteklemiyor"})
                    print(f"--- {key}/on atlandı: model düşünme modunu desteklemiyor", flush=True)
                    continue
                append_jsonl(CONFIGS_FILE, {"model": key, "model_id": model, "mode": mode, "ctx": ctx,
                                            "thinking_supported": thinking, "load_s": round(load_s, 1),
                                            "started": datetime.now().isoformat(timespec="seconds")})
                print(f"--- {key}/{mode}: {len(todo)} görev", flush=True)
                started = time.perf_counter()
                for i, task in enumerate(todo, 1):
                    r = run_task(client, cfg, key, model, ctx, mode, task, thinking)
                    append_jsonl(RESULTS_FILE, r)
                    print(f"[{key}/{mode} {i}/{len(todo)}] {task.id:20} puan={r['score']:.2f} {r['wall']:6.1f} sn "
                          f"{r['tokens']:5} token  {r['detail'][:90]}", flush=True)
                print(f"--- {key}/{mode} bitti: {(time.perf_counter() - started) / 60:.1f} dk", flush=True)
    finally:
        if not args.no_load:  # başlangıçta yüklü model yoksa hepsini boşaltır
            print("\nLM Studio başlangıçtaki durumuna döndürülüyor…", flush=True)
            restore(cfg, initial)
    summarize(load_jsonl(RESULTS_FILE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
