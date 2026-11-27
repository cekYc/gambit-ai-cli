"""Bir modeli farklı GPU yük oranlarıyla (bağlam 16k, tek tahmin) yükleyip hızını ölçer ve en hızlı oranı önerir.

  python tune_gpu.py <model-anahtarı ya da hazır ayar> 0.6 0.7 0.8 max
  python tune_gpu.py --context 24576 queen max   # farklı bağlam uzunluğuyla
  python tune_gpu.py --mtp king 0.35              # MTP açık/kapalı karşılaştırması (her oran iki kez ölçülür)
  python tune_gpu.py --fit queen rook              # sığan en yüksek oranı gerçek yüklemeyle bul (hepsi için: --fit all)
  python tune_gpu.py --fit all --apply             # bulunan oranları config.json'a yaz
  python tune_gpu.py --fit knight --keep           # bitince en iyi oranla yüklü bırak
  python tune_gpu.py --fit knight --start 0.5 --quick   # aramaya 0.5'ten başla, kısa promptla dene (yavaş modeller)
  python tune_gpu.py --fit all --vision --apply    # görsel modu (görsel ekli sanal model) ayrıca ölç, "vision"a yaz

--fit: LM Studio tahmininden başlar; her oranda modeli yükler, uzun bir prompt işletir ve nvidia-smi'de en az
--reserve MiB (varsayılan 500: ekran kartı ekranı da çiziyorsa masaüstü ve tarayıcı için pay) boş kalıyor mu bakar.
Sığdığı sürece 0,05 artırır, sığmazsa azaltır; en iyi oranda üretim ve prompt işleme hızını ölçer.

Yükleme RAM bekçisiyle yapılır (ai-cli/lmstudio.py): bellek tükenirse o oran atlanır.

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
    v = ai.lmstudio.vram()
    if v is None:
        sys.exit("nvidia-smi çalışmıyor (sürücü güncellendiyse bilgisayarı yeniden başlat); VRAM ölçülemez.")
    return (v[1] - v[0]) // ai.lmstudio.MIB


def measure(client: OpenAI, model: str, prompt: str, max_tokens: int) -> dict:
    # Başına benzersiz bir etiket: LM Studio aynı promptu önbellekten işleyip prompt hızını şişirmesin
    prompt = f"[ölçüm {time.time_ns()}]\n{prompt}"
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


def _step(ratio: str) -> int:
    return {"off": 0, "max": 20}.get(ratio, round(float(ratio) * 20))


QUICK = ("Aşağıdaki metin yalnızca dolgu.\n\n" + "Yerel modeller çevrimdışı çalışır. " * 120
         + "\n\nBu metinde kaç cümle var? Tek sayıyla cevap ver.")


def fit(cfg: dict, client: OpenAI, name: str, context: str, reserve_mib: int, start_ratio: str | None = None,
        quick: bool = False, vision: bool = False) -> dict:
    """Hazır ayar için 16k (ya da verilen) bağlamda VRAM'e pay bırakarak sığan en yüksek GPU oranı ve hızı."""
    lm = ai.lmstudio
    p = cfg["presets"][name]
    if not p.get("_disk"):
        return {"preset": name, "error": "model diskte yok"}
    v = lm.vision_of(p)
    if vision and not v:
        return {"preset": name, "vision": True, "error": "görsel eki yok"}
    key = v["model"] if vision else p["model"]
    base = lm.set_arg(lm.preset_args(p, vision=vision), lm.CONTEXT_FLAGS, context)
    lm.unload_all(cfg)
    time.sleep(2)
    free0 = lm.vram()[0]
    reserve = reserve_mib * lm.MIB
    advice = lm.advise(cfg, key, base, free0 - reserve, None)
    # LM Studio tahmini görsel ekini ve op offload tamponunu sayıyor; sanal modellerde gerçeğin altında kalabilir
    start = _step(start_ratio) if start_ratio else _step(advice.gpu) if advice else _step(str(p.get("gpu", 0.3)))
    probe = QUICK if quick else LONG
    tried: dict[int, dict] = {}

    def attempt(step: int) -> bool:
        lm.unload_all(cfg)
        time.sleep(1)
        args = lm.set_arg(base, ("--gpu",), lm._ratio(step))
        t0 = time.perf_counter()
        res = lm.guarded_load(cfg, key, args)
        row = {"gpu": lm._ratio(step), "load_s": round(time.perf_counter() - t0, 1), "ok": False}
        if res.ok:
            try:
                measure(client, key, probe, 8)  # hesap tamponları da ayrılsın: boş VRAM uzun prompttan sonra ölçülür
                row["free_mib"] = lm.vram()[0] // lm.MIB
                row["ok"] = row["free_mib"] >= reserve_mib
            except Exception as e:  # noqa: BLE001
                row["error"] = f"{type(e).__name__}: {e}"[:200]
        else:
            row["error"] = res.message[:200]
            row["guard"] = res.guard_tripped
        tried[step] = row
        state = (f"boş VRAM {row['free_mib']} MiB" if "free_mib" in row else row.get("error", ""))
        print(f"  {name} gpu={row['gpu']:>4}: {'sığıyor' if row['ok'] else 'sığmıyor'} · {state}", flush=True)
        return row["ok"]

    best = None
    if attempt(start):
        best = start
        while best < 20 and attempt(best + 1):
            best += 1
    else:
        step = start - 1
        while step >= 0 and best is None:
            if attempt(step):
                best = step
            elif tried[step].get("guard"):
                break  # RAM yetmiyor: GPU oranını düşürmek RAM'e daha çok yükler
            step -= 1
    if best is None:
        lm.unload_all(cfg)
        return {"preset": name, "model": key, "error": "hiçbir oranda sığmadı", "tried": list(tried.values())}
    if next(reversed(tried)) != best:  # son yüklenen en iyi oran değilse onu yeniden yükle
        attempt(best)
    measure(client, key, "Merhaba", 8)
    gen = measure(client, key, SHORT, 300)
    long = measure(client, key, probe, 8)
    ram = lm.mem_available()
    return {"preset": name, "vision": vision, "model": key, "context": int(context), "gpu": lm._ratio(best),
            "free_vram_mib": lm.vram()[0] // lm.MIB, "free_ram_gib": round(ram / lm.GIB, 1) if ram else None,
            "gen_tps": round(gen["gen_tps"], 1),
            "prompt_tps": round(long["prompt_tokens"] / long["ttft"], 1) if long["ttft"] else 0.0,
            "tried": list(tried.values())}


def apply_fits(fits: list[dict]) -> None:
    """Bulunan oranları config.json'daki hazır ayarlara yazar (dosya ham okunur; çözümlenmiş alanlar eklenmez)."""
    path = HERE.parent / "ai-cli" / "config.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    for f in fits:
        if "gpu" in f and f["preset"] in raw["presets"]:
            g = f["gpu"]
            g = float(g) if g[0].isdigit() else g
            preset = raw["presets"][f["preset"]]
            day = time.strftime("%Y-%m-%d")
            if f.get("vision"):
                preset.setdefault("vision", {}).update(gpu=g, measured=day)
            else:
                preset.update(gpu=g, context=f["context"], measured=day)
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("config.json güncellendi: " + ", ".join(f"{f['preset']}{' (görsel)' if f.get('vision') else ''}={f['gpu']}"
                                                  for f in fits if "gpu" in f))


def main_fit(argv: list[str], context: str) -> int:
    names = [a for a in argv if not a.startswith("--")]
    reserve = int(argv[argv.index("--reserve") + 1]) if "--reserve" in argv else 500
    start = argv[argv.index("--start") + 1] if "--start" in argv else None
    names = [n for n in names if not n.isdigit() and n != start]
    cfg = ai.load_config()
    vision = "--vision" in argv
    if names == ["all"]:
        # "fit": false: ayarı GPU oranıyla değil sanal modelle yapılan taş (knight: uzman tensörleri bölünür)
        names = [n for n, p in cfg["presets"].items()
                 if p.get("_disk") and p.get("fit", True) and (not vision or ai.lmstudio.vision_of(p))]
    if ai.lmstudio.vram() is None:
        sys.exit("nvidia-smi çalışmıyor (sürücü güncellendiyse bilgisayarı yeniden başlat); VRAM ölçülemez.")
    client = OpenAI(base_url=cfg["base_url"], api_key="lm-studio", timeout=1800, max_retries=0)
    fits = []
    for name in names:
        print(f"=== {name}", flush=True)
        f = fit(cfg, client, name, context, reserve, start_ratio=start, quick="--quick" in argv, vision=vision)
        fits.append(f)
        if "--apply" in argv and "gpu" in f:
            apply_fits([f])  # her modelden sonra yaz: ölçüm yarıda kesilse de bulunanlar kalsın
        print(f"=== {name}: " + (f"gpu={f['gpu']} · üretim {f['gen_tps']} tok/s · prompt {f['prompt_tps']} tok/s · boş VRAM "
                                f"{f['free_vram_mib']} MiB · boş RAM {f['free_ram_gib']} GiB" if "gpu" in f
                                else f["error"]), flush=True)
        if name != names[-1] or "--keep" not in argv:
            ai.lmstudio.unload_all(cfg)
    out = HERE / "results" / "tuning"
    out.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M")
    (out / f"fit_{stamp}.json").write_text(json.dumps(fits, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if "--fit" in argv:
        rest = [a for a in argv if a != "--fit"]
        context = rest[rest.index("--context") + 1] if "--context" in rest else CONTEXT
        if "--context" in rest:
            i = rest.index("--context")
            rest = rest[:i] + rest[i + 2:]
        return main_fit(rest, context)
    context, mtp_modes = CONTEXT, [None]
    while argv[:1] in (["--context"], ["--mtp"]):
        if argv[0] == "--mtp":
            mtp_modes, argv = [False, True], argv[1:]
        elif len(argv) > 1:
            context, argv = argv[1], argv[2:]
    if len(argv) < 2:
        print(__doc__)
        return 1
    key, ratios = argv[0], argv[1:]
    cfg = ai.load_config()
    if key in cfg["presets"]:  # hazır ayar adı verildiyse diskteki model anahtarı
        key = cfg["presets"][key]["model"] or sys.exit(f"{argv[0]}: model diskte yok")
    client = OpenAI(base_url=cfg["base_url"], api_key="lm-studio", timeout=1800, max_retries=0)
    rows = []
    for ratio, mtp in ((r, m) for r in ratios for m in mtp_modes):
        lms(cfg, "unload", "--all")
        idle = vram_mib()
        start = time.perf_counter()
        load_args = ["-c", context, "--parallel", "1", "--gpu", ratio]
        if mtp is not None:
            load_args.append("--speculative-draft-mtp" if mtp else "--no-speculative-draft-mtp")
        res = ai.lmstudio.guarded_load(cfg, key, load_args)
        load_s = time.perf_counter() - start
        tag = f"gpu={ratio:>4}" + ("" if mtp is None else f" mtp={'açık' if mtp else 'kapalı'}")
        if not res.ok:
            rows.append({"gpu": ratio, "mtp": mtp, "error": res.message[-200:]})
            print(f"{tag}: yüklenemedi: {res.message}", flush=True)
            continue
        model = next((m["id"] for m in ai.server_models(cfg["base_url"]) or [] if m.get("state") == "loaded"), key)
        try:
            measure(client, model, "Merhaba", 8)  # ısınma
            gen = measure(client, model, SHORT, 400)
            long = measure(client, model, LONG, 8)
        except Exception as e:
            rows.append({"gpu": ratio, "mtp": mtp, "error": f"{type(e).__name__}: {e}"[:200]})
            print(f"{tag}: ölçüm hatası {e}", flush=True)
            continue
        row = {"gpu": ratio, "mtp": mtp, "load_s": round(load_s, 1), "vram_mib": vram_mib() - idle,
               "gen_tps": round(gen["gen_tps"], 1), "gen_tokens": gen["tokens"],
               "prompt_tps": round(long["prompt_tokens"] / long["ttft"], 1) if long["ttft"] else 0.0,
               "prompt_tokens": long["prompt_tokens"]}
        rows.append(row)
        print(f"{tag}: yükleme {row['load_s']:5.1f} sn · VRAM +{row['vram_mib']} MiB · üretim "
              f"{row['gen_tps']:5.1f} tok/s · prompt işleme {row['prompt_tps']:6.1f} tok/s", flush=True)
    lms(cfg, "unload", "--all")
    ok = [r for r in rows if "gen_tps" in r]
    if ok:
        best = max(ok, key=lambda r: r["gen_tps"])
        mtp_note = "" if best.get("mtp") is None else f", MTP {'açık' if best['mtp'] else 'kapalı'}"
        print(f"\nEn hızlı üretim: gpu={best['gpu']}{mtp_note} ({best['gen_tps']} tok/s)", flush=True)
    out = HERE / "results" / "tuning"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{key.replace('/', '_')}_{context}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
