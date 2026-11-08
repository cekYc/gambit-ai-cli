"""Gambit Bench v2'nin 39 görevini Umay CLI ajanıyla (Umay API, uzak model) koşturur ve aynı notlandırıcılarla puanlar.

  python umay_kos.py                          # Umay Akıllı, düşünme açık, tüm görevler
  python umay_kos.py --only kod-,sql-         # yalnızca bu öneklerle başlayan görevler
  python umay_kos.py --model umay-hizli       # başka model
  python umay_kos.py --no-thinking            # düşünme kapalı (enable_thinking: false)
  python umay_kos.py --server-default-thinking  # düşünme alanı gönderilmez, Umay karar verir
  python umay_kos.py --report                 # yalnızca raporu yeniden üret
  python umay_kos.py --umay "C:\\yol\\Umay-CLI" # Umay CLI klasörü (varsayılan: UMAY_CLI_DIR)

Gambit koşucusuyla (run.py) aynı olanlar: görevler, kurulum, notlandırma, onay kuralı (yalnızca görev klasörü),
okumanın görev klasörüyle sınırlanması, görev başına 14 model adımı ve süre sınırı (araçlı 8 dk, araçsız 5 dk).
Farklı olanlar: ajan döngüsü ve sistem istemi Umay CLI'nindir; araçlar metin protokolüyle çağrılır (Umay API
yerleşik araç çağrısını kullanmıyor); örnekleme ve çıktı sınırı Umay sunucusunun varsayılanlarıdır.

API anahtarı UMAY_API_KEY ortam değişkeninden okunur; yoksa gizli olarak sorulur ve hiçbir dosyaya yazılmaz.
Sonuçlar results-umay/ altına yazılır; yarıda kalan koşu aynı komutla kaldığı yerden sürer."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import core  # noqa: E402
import gorevler  # noqa: E402,F401
import run  # noqa: E402  (onay kuralı, notlandırma, süre sınırları: Gambit koşucusuyla aynı)
from core import TASKS, Trace  # noqa: E402

RESULTS = HERE / "results-umay"
DRIVER = HERE / "umay_ajan.mjs"
DEFAULT_UMAY = os.environ.get("UMAY_CLI_DIR", r"C:\Users\erayc\OneDrive\Desktop\aaa")


def log(msg: str) -> None:
    print(msg, flush=True)


def attempt(task: core.Task, umay: Path, model: str, mode: str, key: str, base_url: str) -> dict:
    label = f"{model}__{mode}"
    sandbox = RESULTS / "sandboxes" / label / task.id
    run.fresh_dir(sandbox)
    task.setup(sandbox)
    budget = run.BUDGET[task.tools]
    env = {**os.environ, "UMAY_API_KEY": key, "UMAY_SETTINGS": str(RESULTS / "ayarlar.json"), "NO_COLOR": "1"}
    started = time.perf_counter()
    log_lines: list[str] = []
    proc = subprocess.Popen(["node", str(DRIVER), "--umay", str(umay)], cwd=sandbox, env=env, text=True,
                            encoding="utf-8", errors="replace", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    reader = threading.Thread(target=lambda: log_lines.extend(proc.stderr), daemon=True)
    reader.start()
    proc.stdin.write(json.dumps({"type": "start", "prompt": task.prompt, "cwd": str(sandbox), "tools": task.tools,
                                 "budget": budget, "maxSteps": run.MAX_STEPS, "model": model,
                                 "thinking": {"dusunme": True, "kapali": False}.get(mode), "baseURL": base_url}, ensure_ascii=False) + "\n")
    proc.stdin.flush()
    done: dict = {}
    previous = os.getcwd()
    os.chdir(sandbox)  # onay kuralı göreli yolları run.py'deki gibi görev klasörüne göre çözer
    try:
        for line in proc.stdout:
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if msg.get("type") == "approve":
                args = msg.get("args") if isinstance(msg.get("args"), dict) else {}
                reason = run.policy(msg["name"], args, sandbox)
                if reason:
                    log(f"      engellendi: {reason[:100]}")
                proc.stdin.write(json.dumps({"type": "approval", "id": msg["id"], "ok": not reason}) + "\n")
                proc.stdin.flush()
            elif msg.get("type") == "done":
                done = msg
                break
    finally:
        os.chdir(previous)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
        reader.join(timeout=5)
    wall = time.perf_counter() - started
    final = done.get("final", "")
    trace = Trace(events=done.get("events", []), final=final)
    score, detail, items = run.grade_safely(task, sandbox, final, trace)
    crash = done.get("crash", "") or ("" if done else f"sürücü yanıt vermedi (çıkış kodu {proc.returncode})")
    notes = []
    if done.get("timedOut"):
        notes.append("süre sınırı")
    if done.get("serverError"):
        notes.append(f"sunucu: {done['serverError'][:120]}")
    if crash:
        notes.append(f"çökme: {crash[:120]}")
    if done.get("blocked"):
        notes.append("engellenen: " + " | ".join(b[:60] for b in done["blocked"][:2]))
    calls = int(done.get("calls", 0))
    result = {
        "preset": model, "model_id": model, "mode": mode, "task": task.id, "category": task.category,
        "level": task.level, "weight": task.weight, "score": round(score, 4), "detail": detail,
        "notes": "; ".join(notes), "items": items, "wall": round(wall, 1), "tokens": int(done.get("tokens") or 0), "prompt_tokens": int(done.get("promptTokens") or 0),
        "calls": calls, "think_calls": calls if mode == "dusunme" else 0, "tool_calls": len(trace.events),
        "timed_out": bool(done.get("timedOut")), "server_error": done.get("serverError", ""), "crash": crash,
        "time": datetime.now().isoformat(timespec="seconds"), "time_limit": budget, "seed": None,
        "sampling": "sunucu", "host": "umay-api", "agent": "umay-cli",
    }
    folder = RESULTS / "responses" / label
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{task.id}.json").write_text(json.dumps({
        "result": result, "final": final, "events": trace.events, "messages": done.get("messages", []),
    }, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (folder / f"{task.id}.log").write_text("".join(log_lines), encoding="utf-8")
    return result


def run_task(task, umay, model, mode, key, base_url) -> dict:
    for n in range(3):
        res = attempt(task, umay, model, mode, key, base_url)
        error = res["server_error"]
        # Anahtar hatası tekrarla düzelmez; kota, bakım ve bağlantı sorunları için bekleyip yeniden dene
        if not error or "kabul edilmedi" in error or n == 2:
            return res
        wait = 60 if "kota" in error or "sınır" in error else 20
        log(f"    sunucu sorunu ({error[:90]}); {wait} sn sonra görev yeniden denenecek")
        time.sleep(wait)
    return res


def compare() -> None:
    """Umay sonucunu Gambit'in yerel model koşularıyla (results/, run.py'nin varsayılan çıktısı) aynı tabloda gösterir."""
    import rapor
    rows = []
    for folder in (HERE / "results", RESULTS):
        rows += rapor.load(folder)
    configs = [c for c in rapor.summarize(rows) if c["done"] == c["total"]]
    if not configs:
        return
    log("\nKarşılaştırma (39 görevin tamamını bitirmiş yapılandırmalar):")
    for c in configs:
        log(f"  {c['label']:42} {rapor.fmt(c['score']):>6}  (zor görevler {rapor.fmt(c['hard'])}, {rapor.fmt(c['minutes'], 0)} dk)")


def main() -> int:
    global RESULTS
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--umay", default=DEFAULT_UMAY, help="Umay CLI klasörü")
    ap.add_argument("--model", default="umay-akilli")
    ap.add_argument("--no-thinking", action="store_true", help="enable_thinking: false gönderir")
    ap.add_argument("--server-default-thinking", action="store_true", help="düşünme alanı göndermez, Umay karar verir")
    ap.add_argument("--only", default="", help="virgülle ayrılmış görev id önekleri")
    ap.add_argument("--base-url", default=os.environ.get("UMAY_BASE_URL", ""))
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", default=str(RESULTS), help="sonuç klasörü")
    a = ap.parse_args()
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    RESULTS = Path(a.out)
    import rapor
    rapor.MODES.update(dusunme="düşünme açık", kapali="düşünme kapalı",
                       varsayilan="düşünme alanı gönderilmedi")
    if a.report:
        rapor.build(RESULTS)
        compare()
        return 0
    umay = Path(a.umay)
    if not (umay / "src" / "client.mjs").is_file() or not (umay / "node_modules").is_dir():
        log(f"Umay CLI bulunamadı veya paketleri kurulu değil: {umay} (--umay ile klasörü ver, orada npm ci çalıştır)")
        return 1
    key = os.environ.get("UMAY_API_KEY", "").strip()
    if not key and not a.base_url.startswith("http://127.0.0.1"):
        key = getpass.getpass("Umay API anahtarı (gizli): ").strip()
    if not key:
        key = "yerel-deneme"
    mode = "kapali" if a.no_thinking else "varsayilan" if a.server_default_thinking else "dusunme"
    prefixes = [p for p in a.only.split(",") if p]
    tasks = [t for t in TASKS if not prefixes or any(t.id.startswith(p) for p in prefixes)]
    done = {(r["preset"], r["mode"], r["task"]) for r in run.load_jsonl(RESULTS / "results.jsonl")
            if not r.get("server_error") and not r.get("crash")}
    todo = [t for t in tasks if (a.model, mode, t.id) not in done]
    RESULTS.mkdir(parents=True, exist_ok=True)
    log(f"{a.model} · {mode} · {len(todo)}/{len(tasks)} görev çalıştırılacak · sonuçlar: {RESULTS}")
    run.append_jsonl(RESULTS / "configs.jsonl", {"preset": a.model, "model_id": a.model, "mode": mode,
                                                 "status": "başladı", "agent": "umay-cli",
                                                 "time": datetime.now().isoformat(timespec="seconds")})
    started = time.perf_counter()
    for i, task in enumerate(todo, 1):
        log(f"  [{i}/{len(todo)}] {task.id} ({task.category}, seviye {task.level})")
        res = run_task(task, umay, a.model, mode, key, a.base_url)
        run.append_jsonl(RESULTS / "results.jsonl", res)
        extra = f" · {res['notes']}" if res["notes"] else ""
        log(f"      puan {100 * res['score']:.0f} · {res['wall']:.0f} sn · {res['calls']} adım · {res['tool_calls']} araç{extra}")
        rapor.build(RESULTS)
    run.append_jsonl(RESULTS / "configs.jsonl", {"preset": a.model, "mode": mode, "status": "bitti",
                                                 "minutes": round((time.perf_counter() - started) / 60, 1),
                                                 "time": datetime.now().isoformat(timespec="seconds")})
    rapor.build(RESULTS)
    for c in rapor.summarize(rapor.load(RESULTS)):
        log(f"\n{c['label']}: {rapor.fmt(c['score'])} puan ({c['done']}/{c['total']} görev)")
    compare()
    log(f"\nRapor: {RESULTS / 'RAPOR.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
