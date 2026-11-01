"""Kod inceleme: araçlar kapalı; model satır numaralı koddaki sorunları JSON listesi olarak bildirir. Her gerçek sorun
için doğru satır (±1) 0,6, doğru tür ek 0,4 puan; listede gerçek sorunla eşleşmeyen her bildirim ceza getirir."""

import json
from pathlib import Path

from core import Rubric, code, extract_json, task


def numbered(src: str) -> str:
    return "\n".join(f"{i:>3}| {ln}" for i, ln in enumerate(src.split("\n"), 1))


def make(id_: str, title: str, level: int, lang: str, intro: str, src: str, issues: list[tuple[str, str]],
         types: list[str]) -> None:
    lines = src.split("\n")
    planted = []
    for marker, kind in issues:  # marker: sorunlu satırda geçen benzersiz metin
        hits = [i for i, ln in enumerate(lines, 1) if marker in ln]
        assert len(hits) == 1, (id_, marker, hits)
        planted.append((hits[0], kind))

    def grade(d: Path, answer: str, trace) -> Rubric:
        data = extract_json(answer)
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
        for line, kind in planted:
            cands = [j for j, (ln, _) in enumerate(reports) if abs(ln - line) <= 1 and j not in used]
            best = next((j for j in cands if reports[j][1] == kind), cands[0] if cands else None)
            if best is None:
                r.add(f"satır {line}: {kind}", 1, 0)
                continue
            used.add(best)
            r.add(f"satır {line}: {kind}", 1, 0.6 + 0.4 * (reports[best][1] == kind),
                  "" if reports[best][1] == kind else f"tür {reports[best][1]!r}")
        false_pos = [rep for j, rep in enumerate(reports) if j not in used and not any(abs(rep[0] - ln) <= 1 for ln, _ in planted)]
        if false_pos:
            r.gate(f"{len(false_pos)} yanlış alarm", max(0.5, 1 - 0.07 * len(false_pos)))
        if not reports:
            r.note("JSON liste bulunamadı")
        return r

    def reference(d: Path) -> str:
        return "```json\n" + json.dumps([{"satir": ln, "tur": k} for ln, k in planted], ensure_ascii=False) + "\n```"

    def wrong(d: Path) -> str:
        half = [{"satir": ln, "tur": types[0]} for ln, _ in planted[: len(planted) // 2]] + [{"satir": 1, "tur": types[0]}]
        return "```json\n" + json.dumps(half) + "\n```"

    fence = "python" if lang == "python" else "javascript"
    prompt = (intro + "\n\nİzin verilen türler: " + ", ".join(f"`{t}`" for t in types) + ".\n"
              "Cevabının sonunda YALNIZCA gerçek sorunları içeren tek bir ```json bloğu ver: "
              '[{"satir": satır_numarası, "tur": "tür"}, ...]. Sorun olmayan satırları bildirme; yanlış alarmlar puan kırar.\n\n'
              f"```{fence}\n{numbered(src)}\n```")
    task(id=id_, category="Kod inceleme", title=title, level=level, tools=False, prompt=prompt, grade=grade,
         reference=reference, wrong=wrong)


SEC_SRC = code('''
    import hashlib
    import os
    import random
    import secrets
    import sqlite3

    from flask import Flask, abort, request, session

    app = Flask(__name__)
    app.secret_key = "gizli-anahtar-123"
    UPLOAD_DIR = "/srv/uploads"
    db = sqlite3.connect("app.db", check_same_thread=False)


    def kullanici_bul(ad):
        return db.execute("SELECT * FROM kullanicilar WHERE ad = ?", (ad,)).fetchone()


    @app.get("/ara")
    def ara():
        q = request.args.get("q", "")
        rows = db.execute(f"SELECT ad FROM urunler WHERE ad LIKE '%{q}%'").fetchall()
        return {"sonuc": [r[0] for r in rows]}


    @app.get("/dosya")
    def dosya():
        ad = request.args["ad"]
        with open(os.path.join(UPLOAD_DIR, ad), "rb") as f:
            return f.read()


    @app.post("/hesapla")
    def hesapla():
        ifade = request.form["ifade"]
        return {"sonuc": eval(ifade)}


    @app.post("/kayit")
    def kayit():
        sifre = request.form["sifre"]
        ozet = hashlib.md5(sifre.encode()).hexdigest()
        db.execute("INSERT INTO kullanicilar (ad, sifre) VALUES (?, ?)", (request.form["ad"], ozet))
        return {"ok": True}


    @app.post("/sifre-sifirla")
    def sifirla():
        token = str(random.randint(100000, 999999))
        db.execute("UPDATE kullanicilar SET token = ? WHERE ad = ?", (token, request.form["ad"]))
        return {"gonderildi": True}


    @app.post("/oturum")
    def oturum():
        session["csrf"] = secrets.token_hex(16)
        return {"ok": True}


    @app.delete("/admin/kullanici/<int:uid>")
    def kullanici_sil(uid):
        db.execute("DELETE FROM kullanicilar WHERE id = ?", (uid,))
        return {"silindi": uid}


    @app.get("/profil")
    def profil():
        if "uid" not in session:
            abort(401)
        return {"uid": session["uid"]}
''')

make("inceleme-guvenlik", "Güvenlik açıklarını bulma (Python)", 3, "python",
     "Aşağıdaki Flask uygulamasını güvenlik açısından incele ve gerçek güvenlik açıklarını satır numarasıyla bildir. "
     "Her açığı en belirgin olduğu tek satırla bildir.", SEC_SRC, [
         ('app.secret_key = "gizli', "gizli_anahtar"),
         ("LIKE '%{q}%'", "sql_enjeksiyonu"),
         ("os.path.join(UPLOAD_DIR, ad)", "yol_gecisi"),
         ("eval(ifade)", "kod_calistirma"),
         ("hashlib.md5", "zayif_hash"),
         ("random.randint", "zayif_rastgele"),
         ('@app.delete("/admin', "yetki_eksik"),
     ], ["sql_enjeksiyonu", "yol_gecisi", "gizli_anahtar", "kod_calistirma", "zayif_hash", "zayif_rastgele",
         "yetki_eksik", "xss", "csrf"])

LOGIC_SRC = code('''
    // Sipariş yardımcıları (Node.js)

    function sonNEleman(dizi, n) {
      const sonuc = [];
      for (let i = dizi.length - n; i <= dizi.length; i++) sonuc.push(dizi[i]);
      return sonuc;
    }

    function stoktaVarMi(urunler, ad) {
      return urunler.map((u) => u.ad).indexOf(ad) > 0;
    }

    function enPahalilar(urunler, k = 3) {
      return urunler.sort((a, b) => b.fiyat - a.fiyat).slice(0, k);
    }

    async function fiyatlariGetir(idler, getir) {
      const fiyatlar = {};
      idler.forEach(async (id) => {
        fiyatlar[id] = await getir(id);
      });
      return fiyatlar;
    }

    function sayfala(liste, boyut = 0) {
      const sayfalar = [];
      for (let i = 0; i < liste.length; i += boyut) sayfalar.push(liste.slice(i, i + boyut));
      return sayfalar;
    }

    function zamanlayicilar(isler) {
      for (var i = 0; i < isler.length; i++) {
        setTimeout(() => isler[i].calistir(), 10);
      }
    }

    function sehir(kullanici) {
      // kullanici.adres isteğe bağlıdır (bazı kullanıcılarda hiç yoktur)
      return kullanici.adres.sehir.toUpperCase();
    }

    function toplamTutar(sepet) {
      return sepet.reduce((t, k) => t + k.fiyat * k.adet, 0);
    }

    module.exports = { sonNEleman, stoktaVarMi, enPahalilar, fiyatlariGetir, sayfala, zamanlayicilar, sehir, toplamTutar };
''')

make("inceleme-mantik-js", "Mantık hatalarını bulma (JS)", 3, "js",
     "Aşağıdaki JavaScript modülünü incele ve gerçek hataları (yanlış sonuç, çökme, sonsuz döngü, beklenmeyen yan "
     "etki) satır numarasıyla bildir. Her hatayı en belirgin olduğu tek satırla bildir.", LOGIC_SRC, [
         ("i <= dizi.length; i++", "sinir_hatasi"),
         ("indexOf(ad) > 0", "yanlis_kosul"),
         ("urunler.sort(", "yan_etki"),
         ("idler.forEach(async", "async_hata"),
         ("boyut = 0", "yanlis_varsayilan"),
         ("for (var i = 0; i < isler.length", "kapsam_hatasi"),
         ("kullanici.adres.sehir", "null_kontrolu"),
     ], ["sinir_hatasi", "yanlis_kosul", "yan_etki", "async_hata", "yanlis_varsayilan", "kapsam_hatasi",
         "null_kontrolu", "tip_hatasi"])
