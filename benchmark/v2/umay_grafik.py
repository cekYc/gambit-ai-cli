"""Umay CLI'nin docs/ klasöründeki iki kıyaslama grafiğini results-umay sonuçlarından üretir.

  python umay_grafik.py                       # Umay CLI klasörü: UMAY_CLI_DIR ya da varsayılan
  python umay_grafik.py --docs C:\\yol\\docs   # başka bir klasöre yaz

kiyaslama-genel.svg: 39 görevi bitmiş tüm Umay yapılandırmaları ve Qwen3.8 27B, genel puan çubukları.
kiyaslama.svg: en yüksek puanlı Umay yapılandırması ve Qwen3.8 27B, kategori puanları (radar).
Qwen3.8 27B değerleri Gambit Bench raporundan alınır (yerel, süre sınırı yok)."""

from __future__ import annotations

import argparse
import math
import os
import sys
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rapor  # noqa: E402
from core import CATEGORIES  # noqa: E402

DEFAULT_DOCS = Path(os.environ.get("UMAY_CLI_DIR", r"C:\Users\erayc\OneDrive\Desktop\aaa")) / "docs"
NAMES = {"umay-akilli": "Umay Akıllı", "umay-hizli": "Umay Hızlı", "umay-ultra-hizli": "Umay Ultra Hızlı",
         "umay-daha-zeki": "Umay Daha Zeki"}
COLORS = {"umay-akilli": "#e30a17", "umay-hizli": "#f87171", "umay-ultra-hizli": "#f59e0b",
          "umay-daha-zeki": "#a855f7"}
MODE_NAMES = {"dusunme": "düşünme açık", "varsayilan": "otomatik", "kapali": "düşünme kapalı"}
MODE_FIELDS = {"dusunme": "enable_thinking: true", "varsayilan": "düşünme alanı yok, Umay karar verir",
               "kapali": "enable_thinking: false"}
QWEN = {"name": "Qwen3.8 27B · düşünme kapalı", "short": "Qwen3.8 27B", "sub": "yerel · Gambit CLI · süre sınırı yok",
        "legend": "yerel · Gambit CLI · düşünme kapalı", "limit": "Süre sınırı yok", "color": "#a1a1aa",
        "dash": True, "score": 84.3, "minutes": 872, "full": 17, "zero": 0,
        "cats": dict(zip(CATEGORIES, [77, 97, 89, 88, 78, 75, 100, 77, 81]))}
MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
WORDS = {2: "iki", 3: "üç", 4: "dört", 5: "beş", 6: "altı", 7: "yedi", 8: "sekiz", 9: "dokuz", 10: "on",
         11: "on bir", 12: "on iki", 13: "on üç", 14: "on dört"}
FONT = "Segoe UI, Helvetica, Arial, sans-serif"


def num(v: float, digits: int = 1) -> str:
    q = Decimal(1).scaleb(-digits)
    return str(Decimal(str(v)).quantize(q, rounding=ROUND_HALF_UP)).replace(".", ",")


def text(x, y, s, size, fill="#9ca3af", weight=None, anchor=None) -> str:
    extra = (f' font-weight="{weight}"' if weight else "") + (f' text-anchor="{anchor}"' if anchor else "")
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}"{extra}>{escape(s, quote=False)}</text>'


def configs() -> list[dict]:
    """39 görevi bitmiş Umay yapılandırmaları ve Qwen, genel puana göre sıralı."""
    rows = rapor.load(HERE / "results-umay")
    out = []
    for c in rapor.summarize(rows):
        if c["done"] != c["total"] or c["preset"] not in NAMES:
            continue
        rs = [r for r in rows if r["preset"] == c["preset"] and r["mode"] == c["mode"]]
        unlimited = all(r.get("time_limit", 0) > 600 for r in rs)
        name = NAMES[c["preset"]]
        out.append({
            "name": f"{name} · {MODE_NAMES.get(c['mode'], c['mode'])}", "short": name,
            "sub": f"uzak API · Umay CLI · {MODE_FIELDS.get(c['mode'], c['mode'])}",
            "legend": f"uzak API · Umay CLI · {MODE_NAMES.get(c['mode'], c['mode'])}",
            "limit": "Süre sınırı yok" if unlimited else "Görev başına 5–8 dk sınırı", "unlimited": unlimited,
            "color": COLORS[c["preset"]], "dash": False, "score": c["score"], "minutes": c["minutes"],
            "full": c["full"], "zero": c["zero"], "cats": c["cats"],
            "days": {r["time"][:10] for r in rs if r.get("time")},
        })
    return sorted(out + [QWEN], key=lambda c: -c["score"])


def date_line(cs: list[dict]) -> str:
    days = sorted({d for c in cs for d in c.get("days", ())})
    if not days:
        return ""
    a, b = (datetime.fromisoformat(d) for d in (days[0], days[-1]))
    if a.date() == b.date():
        return f"{a.day} {MONTHS[a.month - 1]} {a.year}"
    if (a.month, a.year) == (b.month, b.year):
        return f"{a.day}–{b.day} {MONTHS[a.month - 1]} {a.year}"
    return f"{a.day} {MONTHS[a.month - 1]} – {b.day} {MONTHS[b.month - 1]} {b.year}"


def bars(cs: list[dict]) -> str:
    n, umay = len(cs), sum(c is not QWEN for c in cs)
    bottom = 96 + 70 * n - 10
    height = bottom + 94
    x0, scale = 360, 3.4
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="{height}" viewBox="0 0 820 {height}" '
           f'role="img" aria-label="Gambit Bench v2 genel puanları: {WORDS.get(umay, umay)} Umay yapılandırması ve Qwen3.8 27B">',
           "<title>Gambit Bench v2 genel puanları</title>",
           f'<rect width="820" height="{height}" rx="14" fill="#0e0e11"/>', f'<g font-family="{FONT}">',
           text(32, 44, "Gambit Bench v2 · genel puan", 20, "#f4f4f5", 700),
           text(32, 68, "39 görev, zorluk ağırlıklı, 0–100 · her yapılandırma bir kez koşturuldu", 13)]
    for v in (0, 25, 50, 75, 100):
        x = f"{x0 + scale * v:.1f}"
        out.append(f'<line x1="{x}" y1="96" x2="{x}" y2="{bottom}" stroke="#2a2a31" stroke-width="1"/>')
        out.append(text(x, 90, str(v), 10, "#6b7280", anchor="middle"))
    for i, c in enumerate(cs):
        y = 104 + 70 * i
        w = scale * c["score"]
        dash = ' stroke-dasharray="5 3"' if c["dash"] else ""
        minutes = f"süre {num(c['minutes'], 0)} dk" + (" (süre sınırı yok)" if c.get("unlimited") else "")
        out += [text(32, y + 13, c["name"], 14, "#f4f4f5", 700), text(32, y + 31, c["sub"], 12),
                f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="18" rx="4" fill="{c["color"]}" fill-opacity="0.75" '
                f'stroke="{c["color"]}"{dash}/>',
                text(f"{x0 + w + 10:.1f}", y + 15, num(c["score"]), 17, c["color"], 700),
                text(x0, y + 36, f"{minutes} · tam puan {c['full']} görev · sıfır puan {c['zero']} görev", 12)]
    out += [text(32, bottom + 52, "Bu grafik kesin bir sıralama değildir.", 12, "#d4d4d8", 700),
            text(32, bottom + 72, "Donanım, çalışma ortamı (yerel / uzak API), kullanılan CLI, süre sınırları ve model "
                                  f"ayarları farklı sonuçlar verebilir. {date_line(cs)}.", 11),
            "</g>", "</svg>"]
    return "\n".join(out) + "\n"


def radar(best: dict, other: dict) -> str:
    cx, cy, r = 300, 318, 200
    angle = [math.radians(-90 + 40 * i) for i in range(len(CATEGORIES))]

    def pt(i, v):
        return f"{cx + r * v / 100 * math.cos(angle[i]):.1f},{cy + r * v / 100 * math.sin(angle[i]):.1f}"

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="620" viewBox="0 0 820 620" role="img" '
           f'aria-label="Gambit Bench v2 kategori puanları: {best["short"]} ve {other["short"]}">',
           f"<title>Gambit Bench v2: {best['short']} ve {other['short']} kategori puanları</title>",
           '<rect width="820" height="620" rx="14" fill="#0e0e11"/>', f'<g font-family="{FONT}">',
           text(32, 44, "Gambit Bench v2 · kategori puanları", 20, "#f4f4f5", 700),
           text(32, 68, "39 görev, 9 kategori, aynı gizli testler ve puanlama · 0–100, zorluk ağırlıklı", 13)]
    for v in (25, 50, 75, 100):
        out.append(f'<polygon points="{" ".join(pt(i, v) for i in range(len(CATEGORIES)))}" fill="none" '
                   'stroke="#2e2e36" stroke-width="1"/>')
        out.append(text(f"{cx + 5:.1f}", f"{cy - r * v / 100 + 4:.1f}", str(v), 10, "#6b7280"))
    for i, name in enumerate(CATEGORIES):
        x2, y2 = pt(i, 100).split(",")
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="#2e2e36" stroke-width="1"/>')
        c = math.cos(angle[i])
        anchor = "middle" if abs(c) < 0.1 else "start" if c > 0 else "end"
        out.append(text(f"{cx + 226 * c:.1f}", f"{cy + 226 * math.sin(angle[i]) + 4:.1f}", name, 13, "#d4d4d8",
                        anchor=anchor))
    series = [other, best]
    for s in series:
        dash = ' stroke-dasharray="6 4"' if s["dash"] else ""
        opacity, width = ("0.16", "2") if s["dash"] else ("0.22", "2.5")
        pts = " ".join(pt(i, s["cats"][c] or 0) for i, c in enumerate(CATEGORIES))
        out.append(f'<polygon points="{pts}" fill="{s["color"]}" fill-opacity="{opacity}" stroke="{s["color"]}" '
                   f'stroke-width="{width}"{dash}/>')
    for s in series:
        for i, c in enumerate(CATEGORIES):
            x, y = pt(i, s["cats"][c] or 0).split(",")
            out.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{s["color"]}"/>')
    for k, s in enumerate([best, other]):
        y = 104 + 186 * k
        dash = ' stroke-dasharray="4 3"' if s["dash"] else ""
        out += [f'<rect x="590" y="{y}" width="16" height="16" rx="3" fill="{s["color"]}" fill-opacity="0.3" '
                f'stroke="{s["color"]}" stroke-width="2"{dash}/>',
                text(616, y + 13, s["short"], 14, "#f4f4f5", 700), text(616, y + 32, s["legend"], 12),
                text(616, y + 66, num(s["score"]), 30, s["color"], 700),
                text(616, y + 90, f"Süre: {num(s['minutes'], 0)} dk", 12),
                text(616, y + 107, f"Tam puan: {s['full']} görev", 12),
                text(616, y + 124, f"Sıfır puan: {s['zero']} görev", 12), text(616, y + 141, s["limit"], 12)]
    out += [text(590, 488, "Genel puan: 39 görev, zorluk ağırlıklı", 11, "#6b7280"),
            text(32, 578, "Bu grafik kesin bir sıralama değildir.", 12, "#d4d4d8", 700),
            text(32, 598, "Donanım, çalışma ortamı (yerel / uzak API), kullanılan CLI, süre sınırları ve model ayarları "
                          f"farklı sonuçlar verebilir. Tek koşu, {date_line([best])}.", 11),
            "</g>", "</svg>"]
    return "\n".join(out) + "\n"


def main() -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", default=str(DEFAULT_DOCS), help="SVG'lerin yazılacağı klasör")
    a = ap.parse_args()
    docs = Path(a.docs)
    cs = configs()
    best = next(c for c in cs if c is not QWEN)
    (docs / "kiyaslama-genel.svg").write_text(bars(cs), encoding="utf-8", newline="\n")
    (docs / "kiyaslama.svg").write_text(radar(best, QWEN), encoding="utf-8", newline="\n")
    for c in cs:
        print(f"  {c['name']:42} {num(c['score']):>5}")
    print(f"Yazıldı: {docs / 'kiyaslama-genel.svg'}, {docs / 'kiyaslama.svg'} (radar: {best['name']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
