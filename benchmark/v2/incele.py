"""Elle puanlama için bir yapılandırmanın bir görevdeki koşusunu gösterir: görev istemi, otomatik puan ve notu,
modelin son cevabı ve görev klasörüne yazdığı dosyalar.
Kullanım: python incele.py <yapılandırma> <görev> [--istem] [--dosya-siniri N]
Yapılandırmalar panodaki güvenilir skorların kaynağı olan koşular (KAYNAK)."""
import argparse
import glob
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import core  # noqa: E402
import gorevler  # noqa: E402,F401

G = "google/gemma-4-26b-a4b-it-qat-q4_0-gguf/gemma-4-26b_q4_0-it.gguf"
# yapılandırma -> (model kimliği, mod, öncelik sırasıyla aranacak sonuç klasörleri)
KAYNAK = {
    "king-oto": ("qwen3.8-27b", "auto", ["results-uzak-king"]),
    "king-kapali": ("qwen3.8-27b", "off", ["results-uzak-king", "results-sinirsiz", "results-v3"]),
    "queen-oto": (G, "auto", ["results-sinirsiz", "results-v3"]),
    "queen-kapali": (G, "off", ["results-tekrar/queen-off-s42-p*"]),
    "rook-oto": ("qwen3.6-35b-a3b", "auto", ["results-uzak-rook"]),
    "rook-kapali": ("qwen3.6-35b-a3b", "off", ["results-uzak-rook"]),
    "bishop-oto": ("qwen3.5-9b", "auto", ["results-uzak-bishop"]),
    "bishop-kapali": ("qwen3.5-9b", "off", ["results-tekrar/bishop-off-s42-p*"]),
}


def bul(conf: str, task: str) -> Path | None:
    mid, mode, klasorler = KAYNAK[conf]
    for k in klasorler:
        for p in sorted(glob.glob(str(HERE / k / "responses" / "*" / f"{task}.json"))):
            r = json.load(open(p, encoding="utf-8"))["result"]
            if r["model_id"] == mid and r["mode"] == mode:
                return Path(p)
    return None


def sandbox(p: Path, task: str) -> Path:
    return p.parent.parent.parent / "sandboxes" / p.parent.name / task


def goster(conf: str, task: str, istem: bool, siniri: int) -> None:
    t = next(x for x in core.TASKS if x.id == task)
    if istem:
        print(f"=== GÖREV {task} ({t.category}, seviye {t.level}, ağırlık {t.weight})\n{t.prompt}\n")
    p = bul(conf, task)
    if not p:
        print(f"=== {conf}: koşu bulunamadı")
        return
    d = json.load(open(p, encoding="utf-8"))
    r = d["result"]
    print(f"=== {conf} | otomatik puan {100 * r['score']:.1f} | {r['calls']} adım, {r['tool_calls']} araç")
    print(f"notlandırıcı: {r['detail'][:400]}")
    print(f"--- son cevap ---\n{(d['final'] or '(boş)')[:siniri]}")
    sb = sandbox(p, task)
    if sb.exists() and t.tools:
        for f in sorted(sb.rglob("*")):
            if f.is_file() and f.stat().st_size < 20000 and f.suffix in (".py", ".js", ".sql", ".txt", ".md", ".json", ".csv", ".ini"):
                print(f"--- dosya {f.relative_to(sb)} ---\n{f.read_text(encoding='utf-8', errors='replace')[:siniri]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("conf")
    ap.add_argument("task")
    ap.add_argument("--istem", action="store_true")
    ap.add_argument("--dosya-siniri", type=int, default=2500)
    a = ap.parse_args()
    for c in a.conf.split(","):
        goster(c, a.task, a.istem, a.dosya_siniri)
        a.istem = False
