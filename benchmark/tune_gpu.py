"""Bir modeli farklı GPU yük oranlarıyla (bağlam 16k, tek tahmin) yükleyip hızını ölçer ve en hızlı oranı önerir.

  python tune_gpu.py <model-anahtarı> 0.6 0.7 0.8 max
  python tune_gpu.py --context 24576 <model-anahtarı> max   # farklı bağlam uzunluğuyla

Her oran için: yükleme süresi, VRAM kullanımı, üretim hızı (tok/s) ve uzun prompt işleme hızı (tok/s).
Sonuçlar results/tuning/<model>.json dosyasına yazılır. Bitince yüklü model kalmaz."""

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parent / "ai-cli"))

import ai  # noqa: E402
from openai import OpenAI  # noqa: E402

CONTEXT = "16384"
SHORT = "Python'da bir metindeki kelimelerin sıklığını sayan, açıklamalı bir fonksiyon yaz."
LONG = ("Aşağıdaki metin yalnızca dolgu, okumana gerek yok.\n\n"
        + "Yerel modeller internet bağlantısı olmadan çalışır ve verileri bilgisayardan çıkmaz. " * 260
        + "\n\nBu metinde kaç kez 'yerel' kelimesi geçiyor? Tek sayıyla cevap ver.")


def lms(cfg: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([ai.lms_path(cfg), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def vram_mib() -> int:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout
    return int(out.strip().splitlines()[0])


def measure(client: OpenAI, model: str, prompt: str, max_tokens: int) -> dict:
    kwargs = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens,
              "stream": True, "stream_options": {"include_usage": True}, "temperature": 0, "reasoning_effort": "none"}
    try:
        stream = client.chat.completions.create(**kwargs)
    except Exception:
        kwargs.pop("reasoning_effort")  # düşünme desteği olmayan model parametreyi reddederse
        stream = client.chat.completions.create(**kwargs)
    start = time.perf_counter()
    first = usage = None
    for chunk in stream:
        usage = chunk.usage or usage
        if chunk.choices and first is None:
            delta = chunk.choices[0].delta
            if delta.content or getattr(delta, "reasoning_content", None):
                first = time.perf_counter()
    end = time.perf_counter()
    ttft = (first or end) - start
    return {"ttft": ttft, "prompt_tokens": usage.prompt_tokens if usage else 0,
            "tokens": usage.completion_tokens if usage else 0, "gen_tps": (usage.completion_tokens - 1) / (end - first)
            if usage and first and end > first else 0.0}


def main() -> int:
    argv = sys.argv[1:]
    context = CONTEXT
    if argv[:1] == ["--context"] and len(argv) > 1:
        context, argv = argv[1], argv[2:]
    if len(argv) < 2:
        print(__doc__)
        return 1
    key, ratios = argv[0], argv[1:]
    cfg = ai.load_config()
    client = OpenAI(base_url=cfg["base_url"], api_key="lm-studio", timeout=1800, max_retries=0)
    rows = []
    for ratio in ratios:
        lms(cfg, "unload", "--all")
        idle = vram_mib()
        start = time.perf_counter()
        r = lms(cfg, "load", key, "-c", context, "--parallel", "1", "--gpu", ratio, "-y")
        load_s = time.perf_counter() - start
        if r.returncode != 0:
            rows.append({"gpu": ratio, "error": (r.stderr or r.stdout).strip()[-200:]})
            print(f"gpu={ratio}: yüklenemedi", flush=True)
            continue
        model = next((m["id"] for m in ai.server_models(cfg["base_url"]) or [] if m.get("state") == "loaded"), key)
        try:
            measure(client, model, "Merhaba", 8)  # ısınma
            gen = measure(client, model, SHORT, 400)
            long = measure(client, model, LONG, 8)
        except Exception as e:
            rows.append({"gpu": ratio, "error": f"{type(e).__name__}: {e}"[:200]})
            print(f"gpu={ratio}: ölçüm hatası {e}", flush=True)
            continue
        row = {"gpu": ratio, "load_s": round(load_s, 1), "vram_mib": vram_mib() - idle,
               "gen_tps": round(gen["gen_tps"], 1), "gen_tokens": gen["tokens"],
               "prompt_tps": round(long["prompt_tokens"] / long["ttft"], 1) if long["ttft"] else 0.0,
               "prompt_tokens": long["prompt_tokens"]}
        rows.append(row)
        print(f"gpu={ratio:>4}: yükleme {row['load_s']:5.1f} sn · VRAM +{row['vram_mib']} MiB · üretim "
              f"{row['gen_tps']:5.1f} tok/s · prompt işleme {row['prompt_tps']:6.1f} tok/s", flush=True)
    lms(cfg, "unload", "--all")
    ok = [r for r in rows if "gen_tps" in r]
    if ok:
        best = max(ok, key=lambda r: r["gen_tps"])
        print(f"\nEn hızlı üretim: gpu={best['gpu']} ({best['gen_tps']} tok/s)", flush=True)
    out = HERE / "results" / "tuning"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{key.replace('/', '_')}_{context}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
