"""Kör karşılaştırma: bir görevde birkaç yapılandırmanın çıktısını model adı ve puan olmadan, rastgele harflerle
gösterir; eşleşme ayrı dosyaya yazılır ve ancak `--ac` ile açılır.
Kullanım: python kor.py <görev> <yapılandırma,...>   |   python kor.py <görev> --ac"""
import json
import random
import sys
from pathlib import Path

import incele

ESLESME = Path(__file__).parent / "results-manuel" / "kor_eslesme.json"
ATLA = ("test", "veri", "dosyalar", "__pycache__", "paket/")


def goster(task: str, confs: list[str]) -> None:
    eslesme = json.loads(ESLESME.read_text(encoding="utf-8")) if ESLESME.exists() else {}
    if sorted(eslesme.get(task, {}).values()) == sorted(confs):  # aynı görev yeniden gösterilirse harfler değişmez
        harfler = [h for h, c in sorted(eslesme[task].items(), key=lambda hc: confs.index(hc[1]))]
    else:
        harfler = random.SystemRandom().sample("ABCDEFGH"[:len(confs)], len(confs))
    eslesme[task] = dict(zip(harfler, confs))
    ESLESME.parent.mkdir(exist_ok=True)
    ESLESME.write_text(json.dumps(eslesme, ensure_ascii=False, indent=1), encoding="utf-8")
    t = next(x for x in incele.core.TASKS if x.id == task)
    print(f"=== GÖREV {task}\n{t.prompt[:1500]}\n")
    for h, c in sorted(zip(harfler, confs)):
        p = incele.bul(c, task)
        d = json.load(open(p, encoding="utf-8"))
        print(f"################ {h} ################\n--- son cevap ---\n{(d['final'] or '(boş)')[:900]}")
        sb = incele.sandbox(p, task)
        if sb.exists() and t.tools:
            for f in sorted(sb.rglob("*")):
                rel = f.relative_to(sb).as_posix()
                if f.is_file() and f.suffix in (".py", ".js", ".md", ".txt") and not rel.startswith(ATLA) and f.stat().st_size < 20000:
                    print(f"--- dosya {rel} ---\n{f.read_text(encoding='utf-8', errors='replace')[:1800]}")


if __name__ == "__main__":
    if sys.argv[2] == "--ac":
        print(json.loads(ESLESME.read_text(encoding="utf-8"))[sys.argv[1]])
    else:
        goster(sys.argv[1], sys.argv[2].split(","))
