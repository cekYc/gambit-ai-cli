"""Kod inceleme görevleri için düzeltilmiş notlandırıcı (yalnızca karşılaştırma için; asıl puanlar değişmez).

Asıl notlandırıcı (gorevler/inceleme.py) bir bildirimi ancak sorunun gömüldüğü satırın ±1 yakınındaysa eşleştirir;
aynı hatayı sonucunun göründüğü satırda (ör. forEach yerine return satırında) bildiren cevap hem "eksik" hem
"yanlış alarm" sayılır. Burada bir bildirim, sorunun bulunduğu fonksiyonun (ya da route'un) satırlarından
herhangi birindeyse eşleşir; sinir_hatasi ve yanlis_kosul türleri birbirinin yerine kabul edilir. Puan kuralları
(satır 0,6 + tür 0,4, yanlış alarm cezası) aynı.

Kullanım: python inceleme_duzeltilmis.py   ->  results-manuel/inceleme_duzeltilmis.json"""
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
from core import Rubric, extract_json  # noqa: E402
from gorevler import inceleme  # noqa: E402

ESDEGER_TUR = {"sinir_hatasi": {"yanlis_kosul"}, "yanlis_kosul": {"sinir_hatasi"}}
GOREVLER = {
    "inceleme-mantik-js": (inceleme.LOGIC_SRC, [
        ("i <= dizi.length; i++", "sinir_hatasi"), ("indexOf(ad) > 0", "yanlis_kosul"), ("urunler.sort(", "yan_etki"),
        ("idler.forEach(async", "async_hata"), ("boyut = 0", "yanlis_varsayilan"),
        ("for (var i = 0; i < isler.length", "kapsam_hatasi"), ("kullanici.adres.sehir", "null_kontrolu")]),
    "inceleme-guvenlik": (inceleme.SEC_SRC, [
        ('app.secret_key = "gizli', "gizli_anahtar"), ("LIKE '%{q}%'", "sql_enjeksiyonu"),
        ("os.path.join(UPLOAD_DIR, ad)", "yol_gecisi"), ("eval(ifade)", "kod_calistirma"), ("hashlib.md5", "zayif_hash"),
        ("random.randint", "zayif_rastgele"), ('@app.delete("/admin', "yetki_eksik")]),
}
BASLANGIC = re.compile(r"^(async function |function |def |@app\.|app\.|module\.exports)")


def araliklar(src: str, issues):
    """Her sorun için kabul edilen satır aralığı: sorunun bulunduğu üst düzey bloğun (fonksiyon/route) satırları."""
    lines = src.split("\n")
    starts = [i for i, ln in enumerate(lines, 1) if BASLANGIC.match(ln)]
    out = []
    for marker, kind in issues:
        line = next(i for i, ln in enumerate(lines, 1) if marker in ln)
        bas = max([s for s in starts if s <= line], default=line)
        if lines[bas - 1].startswith("def ") and bas > 1 and lines[bas - 2].startswith("@app."):
            bas -= 1  # route: dekoratör de bloğa dahil
        son = min([s for s in starts if s > line and not (lines[s - 1].startswith("def ") and lines[s - 2].startswith("@app."))],
                  default=len(lines) + 1) - 1
        out.append((line, kind, bas, son))
    return out


def puanla(task: str, answer: str) -> float:
    src, issues = GOREVLER[task]
    planted = araliklar(src, issues)
    data = extract_json(answer or "")
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), [])
    reports = []
    for x in data if isinstance(data, list) else []:
        if isinstance(x, dict):
            try:
                reports.append((int(x.get("satir", x.get("line", -99))), str(x.get("tur", x.get("type", ""))).strip()))
            except (TypeError, ValueError):
                continue
    r = Rubric()
    used = set()
    for line, kind, bas, son in planted:
        ok_tur = {kind} | ESDEGER_TUR.get(kind, set())
        cands = [j for j, (ln, _) in enumerate(reports) if bas <= ln <= son and j not in used]
        best = next((j for j in cands if reports[j][1] in ok_tur), cands[0] if cands else None)
        if best is None:
            r.add(f"satır {line}", 1, 0)
            continue
        used.add(best)
        r.add(f"satır {line}", 1, 0.6 + 0.4 * (reports[best][1] in ok_tur))
    blok = [(bas, son) for _, _, bas, son in planted]
    false_pos = [rep for j, rep in enumerate(reports) if j not in used and not any(b <= rep[0] <= s for b, s in blok)]
    if false_pos:
        r.gate(f"{len(false_pos)} yanlış alarm", max(0.5, 1 - 0.07 * len(false_pos)))
    return r.score


def koşular(model_id, mode, kosu_listesi):
    """Bir yapılandırmanın inceleme görevlerindeki koşuları (her biri {görev: (eski, yeni)}). Her koşu, öncelik
    sırasıyla aranacak klasör kalıplarının listesi: bir görevin cevabı ilk eşleşen klasörden alınır."""
    out = []
    for kaliplar in kosu_listesi:
        row = {}
        for task in GOREVLER:
            for k in kaliplar:
                for p in sorted(glob.glob(str(HERE / k / "responses" / "*" / f"{task}.json"))):
                    js = json.load(open(p, encoding="utf-8"))
                    if js["result"]["model_id"] == model_id and js["result"]["mode"] == mode:
                        row[task] = (js["result"]["score"], puanla(task, js["final"]))
                        break
                if task in row:
                    break
        if len(row) == len(GOREVLER):
            out.append(row)
    return out


G = "google/gemma-4-26b-a4b-it-qat-q4_0-gguf/gemma-4-26b_q4_0-it.gguf"
# panodaki güvenilir skorların kaynağı olan koşular (build_v2_main.py GUVENILIR ile aynı)
TEKRAR = lambda ad: [[f"results-tekrar/{ad}-s{s}-p*"] for s in (42, 43, 44)]  # noqa: E731
YAPILANDIRMA = [
    ("king · otomatik", "king_auto_gv", "qwen3.8-27b", "auto", [["results-uzak-king"]]),
    ("king · kapalı", "king_off_gv", "qwen3.8-27b", "off", [["results-uzak-king", "results-sinirsiz", "results-v3"]]),
    ("queen · otomatik", "queen_auto_gv", G, "auto", [["results-sinirsiz", "results-v3"], ["results-uzak-queen-oto"]]),
    ("queen · kapalı", "queen_off_gv", G, "off", TEKRAR("queen-off")),
    ("rook · otomatik", "rook_auto_gv", "qwen3.6-35b-a3b", "auto", [["results-uzak-rook"]]),
    ("rook · kapalı", "rook_off_gv", "qwen3.6-35b-a3b", "off", [["results-uzak-rook"]]),
    ("bishop · otomatik", "bishop_auto_gv", "qwen3.5-9b", "auto", [["results-uzak-bishop"]]),
    ("bishop · kapalı", "bishop_off_gv", "qwen3.5-9b", "off", TEKRAR("bishop-off")),
    ("pawn · kapalı", "pawn_off_gv", "qwen3.5-2b", "off", [["results-v3"]]),
    ("knight · kapalı", "knight_off_gv", "phi-4-mini-reasoning", "off", [["results-v3"]]),
]

if __name__ == "__main__":
    gv = {}
    for r in json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else []:
        if r["kod"].endswith("_gv"):
            gv.setdefault(r["kod"], []).append(r)
    W = {t.id: t.weight for t in core.TASKS}
    toplam_w = sum(W.values())
    satirlar = []
    for ad, kod, mid, mode, klasorler in YAPILANDIRMA:
        runs = koşular(mid, mode, klasorler)
        if not runs:
            print("koşu yok:", ad)
            continue
        ort = {t: (statistics.mean(r[t][0] for r in runs) * 100, statistics.mean(r[t][1] for r in runs) * 100) for t in GOREVLER}
        rs = gv.get(kod, [])
        genel = sum(x["agirlik"] * x["puan"] for x in rs) / sum(x["agirlik"] for x in rs) if rs else None
        fark = sum(W[t] * (ort[t][1] - ort[t][0]) for t in GOREVLER) / toplam_w
        satirlar.append(dict(yapilandirma=ad, kosu=len(runs),
                             mantik_eski=round(ort["inceleme-mantik-js"][0], 1), mantik_yeni=round(ort["inceleme-mantik-js"][1], 1),
                             guvenlik_eski=round(ort["inceleme-guvenlik"][0], 1), guvenlik_yeni=round(ort["inceleme-guvenlik"][1], 1),
                             genel_eski=round(genel, 1) if genel is not None else None,
                             genel_yeni=round(genel + fark, 1) if genel is not None else None))
        print(satirlar[-1])
    (HERE / "results-manuel" / "inceleme_duzeltilmis.json").write_text(json.dumps(satirlar, ensure_ascii=False, indent=1), encoding="utf-8")
