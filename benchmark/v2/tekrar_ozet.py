"""Tekrar turlarının özeti: her seed'in ağırlıklı puanı, ortalama ± standart sapma ve kategori ortalamaları.
Kullanım: python tekrar_ozet.py <hazır_ayar> <mod>   (results-tekrar/<hazır_ayar>-<mod>-s*-p*/results.jsonl)"""
import glob
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import core  # noqa: E402
import gorevler  # noqa: E402,F401

CATS = ["Kod yazma", "Hata ayıklama", "Kod okuma", "SQL", "Terminal", "Ajan", "Mantık", "Talimat", "Kod inceleme"]
catmap = {t.id: t.category for t in core.TASKS}


def wavg(rs):
    return 100 * sum(r["weight"] * r["score"] for r in rs) / sum(r["weight"] for r in rs)


def load(preset, mode):
    seeds = {}
    for f in glob.glob(str(HERE / f"results-tekrar/{preset}-{mode}-s*-p*/results.jsonl")):
        seed = int(re.search(r"-s(\d+)-p", f)[1])
        seeds.setdefault(seed, []).extend(json.loads(l) for l in open(f, encoding="utf-8") if l.strip())
    return dict(sorted(seeds.items()))


if __name__ == "__main__":
    seeds = load(sys.argv[1], sys.argv[2])
    tot = []
    for seed, rs in seeds.items():
        assert len({r["task"] for r in rs}) == len(rs), f"seed {seed}: yinelenen görev"
        tot.append(wavg(rs))
        print(f"seed {seed}: {len(rs)} görev, {tot[-1]:.1f}")
    print(f"ortalama {statistics.mean(tot):.1f} ± {statistics.stdev(tot):.1f} (min {min(tot):.1f}, maks {max(tot):.1f})")
    for c in CATS:
        vals = [wavg([r for r in rs if catmap[r["task"]] == c]) for rs in seeds.values()]
        print(f"  {c:14} {statistics.mean(vals):5.1f}  ({' / '.join(f'{v:.0f}' for v in vals)})")
