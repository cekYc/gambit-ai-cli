"""Gambit Bench v2 raporu: results/results.jsonl → RAPOR.md, rapor.html, sonuclar.csv.

  python rapor.py [--out results]

Genel puan zorluk ağırlıklıdır: Σ(ağırlık × görev puanı) / Σ ağırlık (ağırlık = seviye: kolay 1, orta 2, zor 3,
çok zor 4). Kategori puanları da kendi içinde aynı şekilde ağırlıklıdır."""

from __future__ import annotations

import csv
import html
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import core  # noqa: E402
import gorevler  # noqa: E402,F401
from core import CATEGORIES, LEVELS, TASKS  # noqa: E402

LABELS = {  # hazır ayar → model (raporda okunabilirlik için)
    "knight": "Qwen3.5 9B", "rook": "Qwen3-Coder 30B-A3B", "queen": "Gemma 4 26B-A4B",
    "bishop": "Gemma 4 12B Coder", "king": "Qwen3.8 27B",
}
ORDER = ["knight", "rook", "queen", "bishop", "king"]
MODES = {"off": "kapalı", "auto": "otomatik"}


def load(results: Path) -> list[dict]:
    path = results / "results.jsonl"
    if not path.is_file():
        return []
    rows = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        rows[(r["preset"], r["mode"], r["task"])] = r  # aynı görev iki kez varsa sonuncusu
    return list(rows.values())


def wmean(rows: list[dict]) -> float | None:
    w = sum(r["weight"] for r in rows)
    return 100 * sum(r["weight"] * r["score"] for r in rows) / w if w else None


def summarize(rows: list[dict]) -> list[dict]:
    configs = {}
    for r in rows:
        configs.setdefault((r["preset"], r["mode"]), []).append(r)
    out = []
    for (preset, mode), rs in configs.items():
        cats = {c: wmean([r for r in rs if r["category"] == c]) for c in CATEGORIES}
        hard = [r for r in rs if r["level"] >= 3]
        out.append({
            "preset": preset, "mode": mode, "label": f"{preset} · {MODES.get(mode, mode)}",
            "model": LABELS.get(preset, preset), "done": len(rs), "total": len(TASKS),
            "score": wmean(rs), "plain": 100 * sum(r["score"] for r in rs) / len(rs), "hard": wmean(hard),
            "cats": cats, "minutes": sum(r["wall"] for r in rs) / 60, "tokens": sum(r["tokens"] for r in rs),
            "think": sum(r.get("think_calls", 0) for r in rs), "calls": sum(r.get("calls", 0) for r in rs),
            "timeouts": sum(bool(r.get("timed_out")) for r in rs),
            "errors": sum(bool(r.get("server_error") or r.get("crash")) for r in rs),
            "full": sum(r["score"] >= 0.999 for r in rs), "zero": sum(r["score"] <= 0.001 for r in rs),
        })
    out.sort(key=lambda c: (-(c["score"] or 0), ORDER.index(c["preset"]) if c["preset"] in ORDER else 9))
    return out


def fmt(v, digits=1) -> str:
    return "–" if v is None else f"{v:.{digits}f}".replace(".", ",")


def partial_note(partial: list[dict]) -> str:
    return ("Yarım kalan ve sıralamaya alınmayan yapılandırmalar: "
            + ", ".join(f"{c['label']} ({c['done']}/{c['total']} görev)" for c in partial) + ".") if partial else ""


def write_md(path: Path, configs: list[dict], rows: list[dict], partial: list[dict] = ()) -> None:
    by = {(r["preset"], r["mode"], r["task"]): r for r in rows}
    total_w = sum(t.weight for t in TASKS)
    lines = [
        "# Gambit Bench v2 sonuçları", "",
        f"_Güncelleme: {datetime.now():%Y-%m-%d %H:%M} · {len(TASKS)} görev · toplam ağırlık {total_w:g} · "
        "her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._", "",
        "**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.", "",
        "## Sıralama", "",
        "| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(configs, 1):
        lines.append(f"| {i} | **{c['label']}** | {c['model']} | **{fmt(c['score'])}** | {fmt(c['plain'])} | {fmt(c['hard'])} | "
                     f"{c['full']} / {c['zero']} | {fmt(c['minutes'], 0)} | {fmt(c['tokens'] / 1000)} | "
                     f"{c['think']}/{c['calls']} | {c['timeouts']} | {c['done']}/{c['total']} |")
    if partial:
        lines += ["", f"_{partial_note(partial)}_"]
    lines += ["", "## Kategoriler (kategori içinde ağırlıklı)", "",
              "| Yapılandırma | " + " | ".join(CATEGORIES) + " |", "|---|" + "---|" * len(CATEGORIES)]
    for c in configs:
        lines.append(f"| {c['label']} | " + " | ".join(fmt(c["cats"][k], 0) for k in CATEGORIES) + " |")
    lines += ["", "## Görevler", "",
              "| Görev | Kategori | Seviye (ağırlık) | " + " | ".join(c["label"] for c in configs) + " |",
              "|---|---|---|" + "---|" * len(configs)]
    for t in TASKS:
        cells = [fmt(100 * by[(c["preset"], c["mode"], t.id)]["score"], 0) if (c["preset"], c["mode"], t.id) in by else "–"
                 for c in configs]
        lines.append(f"| {t.id} — {t.title} | {t.category} | {LEVELS[t.level]} (×{t.weight:g}) | " + " | ".join(cells) + " |")
    lines += ["", "## Notlar", "",
              "- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu,"
              " biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi"
              " durumlar çarpan cezası alır.",
              "- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.",
              "- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).",
              "- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<yapılandırma>/<görev>.json` ve `.log`.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["yapilandirma", "hazir_ayar", "mod", "gorev", "kategori", "seviye", "agirlik", "puan", "sure_sn",
                    "token", "arac_cagrisi", "dusunulen_adim", "sure_asimi", "not"])
        for r in sorted(rows, key=lambda r: (r["preset"], r["mode"], r["task"])):
            w.writerow([f"{r['preset']}_{r['mode']}", r["preset"], r["mode"], r["task"], r["category"], r["level"],
                        r["weight"], f"{100 * r['score']:.1f}".replace(".", ","), r["wall"], r["tokens"], r["tool_calls"],
                        r.get("think_calls", 0), int(bool(r.get("timed_out"))), (r["detail"] + " " + r.get("notes", ""))[:300]])


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#e4e1d8;--card:#ffffff;--accent:#2f5d8a;--bar:#2f5d8a22}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#161615;--fg:#ecebe6;--muted:#a3a29b;
--line:#2f2e2b;--card:#1e1e1c;--accent:#7fb0e0;--bar:#7fb0e033}}
:root[data-theme="dark"]{--bg:#161615;--fg:#ecebe6;--muted:#a3a29b;--line:#2f2e2b;--card:#1e1e1c;--accent:#7fb0e0;--bar:#7fb0e033}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1200px;margin:0 auto;padding:24px 16px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:32px 0 10px}
.muted{color:var(--muted)}.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{padding:7px 10px;border-bottom:1px solid var(--line);
text-align:right;white-space:nowrap}th{font-weight:600;color:var(--muted);font-size:12px;position:sticky;top:0;background:var(--card)}
td:first-child,th:first-child,td.l,th.l{text-align:left}tr:last-child td{border-bottom:0}
.bar{position:relative}.bar span{position:absolute;left:0;top:4px;bottom:4px;background:var(--bar);border-radius:4px}
.bar b{position:relative}.cell{border-radius:4px;padding:2px 6px;display:inline-block;min-width:38px;text-align:center}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:8px 0;color:var(--muted);font-size:12px}
"""


def heat(v: float | None) -> str:
    if v is None:
        return "<span class='cell muted'>–</span>"
    hue = 10 + 110 * (v / 100)  # kırmızı → yeşil
    return f"<span class='cell' style='background:hsl({hue:.0f} 60% 50% / .28)'>{v:.0f}</span>"


def write_html(path: Path, configs: list[dict], rows: list[dict], partial: list[dict] = ()) -> None:
    by = {(r["preset"], r["mode"], r["task"]): r for r in rows}
    e = html.escape
    out = [f"<!doctype html><html lang='tr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
           f"<title>Gambit Bench v2</title><style>{CSS}</style></head><body><main>",
           "<h1>Gambit Bench v2</h1>",
           f"<p class='muted'>{len(TASKS)} görev · {len(CATEGORIES)} kategori · toplam ağırlık {sum(t.weight for t in TASKS):g} · "
           f"güncelleme {datetime.now():%Y-%m-%d %H:%M}. Her görev gambit-cli'nin ajan döngüsüyle çalıştırıldı; puanlar kısmi "
           "(rubrik) ve genel puan zorluk ağırlıklı (kolay ×1 … çok zor ×4).</p>",
           "<h2>Sıralama</h2><div class='wrap'><table><tr><th class='l'>#</th><th class='l'>Yapılandırma</th><th class='l'>Model</th>"
           "<th class='l' style='min-width:220px'>Genel (ağırlıklı)</th><th>Basit ort.</th><th>Zor+ görevler</th><th>Tam / sıfır</th>"
           "<th>Süre (dk)</th><th>Token (bin)</th><th>Düşünülen adım</th><th>Süre aşımı</th><th>Görev</th></tr>"]
    for i, c in enumerate(configs, 1):
        s = c["score"] or 0
        out.append(f"<tr><td class='l'>{i}</td><td class='l'><b>{e(c['label'])}</b></td><td class='l muted'>{e(c['model'])}</td>"
                   f"<td class='l bar'><span style='width:{s:.1f}%'></span><b>{fmt(c['score'])}</b></td>"
                   f"<td>{fmt(c['plain'])}</td><td>{fmt(c['hard'])}</td><td>{c['full']} / {c['zero']}</td>"
                   f"<td>{fmt(c['minutes'], 0)}</td><td>{fmt(c['tokens'] / 1000)}</td><td>{c['think']}/{c['calls']}</td>"
                   f"<td>{c['timeouts']}</td><td>{c['done']}/{c['total']}</td></tr>")
    out.append("</table></div>" + (f"<p class='muted'>{e(partial_note(partial))}</p>" if partial else ""))
    out.append("<h2>Kategoriler</h2><div class='wrap'><table><tr><th class='l'>Yapılandırma</th>"
               + "".join(f"<th>{e(k)}</th>" for k in CATEGORIES) + "</tr>")
    for c in configs:
        out.append(f"<tr><td class='l'>{e(c['label'])}</td>" + "".join(f"<td>{heat(c['cats'][k])}</td>" for k in CATEGORIES) + "</tr>")
    out.append("</table></div><h2>Görevler</h2><div class='wrap'><table><tr><th class='l'>Görev</th><th class='l'>Kategori</th>"
               "<th>Seviye</th>" + "".join(f"<th>{e(c['label'])}</th>" for c in configs) + "</tr>")
    for t in TASKS:
        cells = []
        for c in configs:
            r = by.get((c["preset"], c["mode"], t.id))
            tip = e((r["detail"] + (" | " + r["notes"] if r.get("notes") else ""))[:400]) if r else ""
            cells.append(f"<td title='{tip}'>{heat(100 * r['score'] if r else None)}</td>")
        out.append(f"<tr><td class='l'>{e(t.id)}<div class='muted' style='font-size:12px'>{e(t.title)}</div></td>"
                   f"<td class='l muted'>{e(t.category)}</td><td>{e(LEVELS[t.level])} ×{t.weight:g}</td>" + "".join(cells) + "</tr>")
    out.append("</table></div><p class='muted'>Hücrenin üzerine gelince notlandırıcının notu görünür. Ham veriler: "
               "results.jsonl, sonuclar.csv; görev dökümleri: responses/.</p></main></body></html>")
    path.write_text("".join(out), encoding="utf-8")


def build(results: Path) -> list[dict]:
    rows = load(results)
    configs = summarize(rows)
    if not rows:
        return configs
    # Yarım kalan yapılandırmalar farklı görev kümesiyle ortalama alacağı için sıralamaya girmez
    complete = [c for c in configs if c["done"] == c["total"]]
    partial = [c for c in configs if c["done"] < c["total"]]
    write_md(results / "RAPOR.md", complete, rows, partial)
    write_html(results / "rapor.html", complete, rows, partial)
    write_csv(results / "sonuclar.csv", rows)
    return configs


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "results"))
    a = ap.parse_args()
    for c in build(Path(a.out)):
        print(f"{c['label']:22} {fmt(c['score']):>6}  ({c['done']}/{c['total']} görev, {fmt(c['minutes'], 0)} dk)")
