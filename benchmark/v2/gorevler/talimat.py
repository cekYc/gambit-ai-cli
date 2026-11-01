"""Talimat takibi: araçlar kapalı. Kurallar programla tek tek denetlenir; her kural ayrı puan."""

import json
import re
from pathlib import Path

from core import Rubric, code, code_blocks, extract_json, extract_text_answer, task

# ---------------------------------------------------------------- yapılandırılmış çıkarım

EMAIL = code("""
    Konu: Sipariş hk.

    Merhabalar, ben Ayşe Yılmaz. 14 Mart 2026'da verdiğim 2026-0457 numaralı siparişte 3 adet Kahve Kupası
    (tanesi 149,90 TL) ve 1 adet Termos (649,00 TL) vardı. Kupalardan biri kırık geldi; yalnızca o kupanın
    iadesini istiyorum, termos sorunsuz. Bana 0532 412 77 19 numarasından ulaşabilirsiniz.
    Not: Geçen ayki 2026-0311 numaralı siparişim ise hâlâ gelmedi, onu da kontrol eder misiniz?
    Teşekkürler, iyi çalışmalar.
""")
EXTRACT_REF = {
    "musteri_adi": "Ayşe Yılmaz", "siparis_no": "2026-0457", "siparis_tarihi": "2026-03-14",
    "urunler": [{"ad": "Kahve Kupası", "adet": 3, "birim_fiyat": 149.90}, {"ad": "Termos", "adet": 1, "birim_fiyat": 649.00}],
    "siparis_toplami": 1098.70,
    "iade": {"istendi": True, "urun": "Kahve Kupası", "adet": 1, "tutar": 149.90},
    "telefon": "+905324127719",
    "diger_siparisler": ["2026-0311"],
}


def _num(v, want) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and abs(v - want) < 0.005


def grade_extract(d: Path, answer: str, trace) -> Rubric:
    data = extract_json(answer)
    r = Rubric()
    if not isinstance(data, dict):
        return r.add("JSON nesnesi", 1, 0).gate("geçerli JSON yok", 0.0)
    fold = lambda s: str(s or "").strip().casefold()  # noqa: E731
    r.add("musteri_adi", 1, fold(data.get("musteri_adi")) == fold("Ayşe Yılmaz"))
    r.add("siparis_no", 1, str(data.get("siparis_no", "")).strip() == "2026-0457")
    r.add("siparis_tarihi (ISO)", 1, str(data.get("siparis_tarihi", "")).strip() == "2026-03-14")
    items = data.get("urunler") if isinstance(data.get("urunler"), list) else []
    for want in EXTRACT_REF["urunler"]:
        got = next((x for x in items if isinstance(x, dict) and fold(want["ad"]) in fold(x.get("ad"))), None)
        v = 0.0
        if got:
            v = (1 + (got.get("adet") == want["adet"]) + _num(got.get("birim_fiyat"), want["birim_fiyat"])) / 3
        r.add(f"ürün: {want['ad']}", 1.5, v)
    r.add("urunler: fazla kalem yok", 0.5, len(items) == 2)
    r.add("siparis_toplami", 1, _num(data.get("siparis_toplami"), 1098.70))
    iade = data.get("iade") if isinstance(data.get("iade"), dict) else {}
    r.add("iade.istendi", 0.5, iade.get("istendi") is True)
    r.add("iade.urun ve adet", 1, "kupa" in fold(iade.get("urun")) and iade.get("adet") == 1)
    r.add("iade.tutar", 1, _num(iade.get("tutar"), 149.90))
    r.add("telefon (E.164)", 1, str(data.get("telefon", "")).strip() == "+905324127719")
    r.add("diger_siparisler", 1, data.get("diger_siparisler") == ["2026-0311"])
    r.add("yalnızca şemadaki anahtarlar", 0.5, set(data) == set(EXTRACT_REF))
    return r


task(
    id="talimat-cikarim", category="Talimat", title="E-postadan yapılandırılmış veri", level=2, tools=False,
    prompt=code("""
        Aşağıdaki müşteri e-postasından bilgileri çıkar ve YALNIZCA bir ```json bloğu ver (başka açıklama yazma).
        Şema (tam olarak bu anahtarlar):
        {"musteri_adi": metin, "siparis_no": metin (bu e-postanın konusu olan sipariş), "siparis_tarihi": "YYYY-AA-GG",
         "urunler": [{"ad": metin, "adet": tam sayı, "birim_fiyat": sayı}], "siparis_toplami": sayı (tüm ürünler),
         "iade": {"istendi": true/false, "urun": metin, "adet": tam sayı, "tutar": sayı},
         "telefon": "+90..." biçiminde boşluksuz E.164, "diger_siparisler": [e-postada geçen diğer sipariş numaraları]}
        Sayılar JSON sayısı olsun (metin değil, nokta ondalık ayırıcı).

        E-posta:
        ---
    """) + "\n" + EMAIL + "\n---",
    grade=grade_extract,
    reference=lambda d: "```json\n" + json.dumps(EXTRACT_REF, ensure_ascii=False) + "\n```",
    wrong=lambda d: "```json\n" + json.dumps({**EXTRACT_REF, "siparis_tarihi": "14.03.2026", "telefon": "0532 412 77 19",
                                              "siparis_toplami": 1748.6}, ensure_ascii=False) + "\n```",
)

# ---------------------------------------------------------------- kısıtlı metin

BANNED = ("harika", "mükemmel", "devrim")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")


def _words(s: str) -> list[str]:
    return re.findall(r"[\wçğıöşüÇĞİÖŞÜâîû'’-]+", s)


def grade_constrained(d: Path, answer: str, trace) -> Rubric:
    r = Rubric()
    text = (answer or "").strip()
    if code_blocks(text):
        r.gate("kod bloğu kullanılmış", 0.9)
        text = extract_text_answer(text).strip()
    lines = text.split("\n")
    r.add("başlık: ## ile başlar, Gambit içerir", 1, bool(lines) and lines[0].startswith("## ") and "Gambit" in lines[0])
    blocks = [b.strip() for b in re.split(r"\n\s*\n", "\n".join(lines[1:])) if b.strip()]
    kinds = ["liste" if all(ln.strip().startswith("- ") for ln in b.split("\n")) else "paragraf" for b in blocks]
    r.add("yapı: paragraf, paragraf, liste, paragraf", 1.5, kinds == ["paragraf", "paragraf", "liste", "paragraf"])
    paras = [b for b, k in zip(blocks, kinds) if k == "paragraf"]
    r.add("tam 3 paragraf", 1, len(paras) == 3)
    lists = [b for b, k in zip(blocks, kinds) if k == "liste"]
    items = lists[0].split("\n") if len(lists) == 1 else []
    r.add("liste tam 4 madde", 1, len(items) == 4)
    r.add("maddeler en fazla 8 kelime", 1, bool(items) and all(len(_words(i[2:])) <= 8 for i in items))
    n = len(_words(text))
    if n < 80:
        r.gate("metin çok kısa", n / 80)
    r.add("toplam 110-160 kelime", 1.5, 110 <= n <= 160 or (1 - min(abs(n - 110), abs(n - 160)) / 40 if 70 <= n <= 200 else 0),
          f"{n} kelime")
    low = text.casefold()
    req = ["çevrimdışı", "gizlilik", "terminal"]
    r.add("zorunlu kelimeler", 1.5, sum(w in low for w in req) / 3)
    r.add("yasaklı kelime yok", 1, not any(re.search(rf"\b{w}", low) for w in BANNED))
    sentences = [lines[0]] if lines else []
    for b, k in zip(blocks, kinds):
        if k == "liste":
            sentences += [ln.strip()[2:] for ln in b.split("\n")]
        else:
            sentences += [s for s in re.split(r"(?<=[.!?…])\s+", " ".join(b.split("\n"))) if s.strip()]
    longest = max((len(_words(s)) for s in sentences), default=0)
    r.add("cümleler en fazla 22 kelime", 1, longest <= 22, f"en uzun {longest}")
    r.add("soru işaretiyle biter", 1, text.rstrip().endswith("?"))
    r.add("emoji ve ünlem yok", 1, not EMOJI.search(text) and "!" not in text)
    return r


CONSTRAINED_REF = code("""
    ## Gambit ile yerel yapay zekâ terminalinizde

    Gambit, bilgisayarınızda çalışan yerel modellerle konuşan bir terminal asistanıdır. Tamamen çevrimdışı çalışır
    ve verileriniz makinenizden dışarı çıkmaz. Bu yüzden gizlilik konusunda içiniz rahat olur.

    Asistan dosyaları okur, arar ve sizin onayınızla düzenler. Komutları çalıştırmadan önce size gösterir ve
    izninizi bekler. Böylece kontrol her zaman sizde kalır.

    - Yerel modellerle hızlı ve güvenli yanıtlar
    - Dosya okuma, arama ve onaylı düzenleme
    - PowerShell komutlarını onayla çalıştırma
    - Görevin zorluğuna göre otomatik düşünme

    Satranç taşı adlarıyla modeller arasında kolayca geçiş yapabilirsiniz. Hafif işler için hızlı bir model,
    zor sorular için daha güçlü bir model seçebilirsiniz. Kurulum internet gerektirmez ve birkaç dakika sürer.
    Siz de günlük işlerinizi terminalde yerel bir asistanla yapmayı denemek ister misiniz?
""")

task(
    id="talimat-kisitli-metin", category="Talimat", title="Çok kısıtlı tanıtım metni", level=3, tools=False,
    prompt=code("""
        Gambit CLI (yerel modellerle çalışan terminal asistanı) için kısa bir Türkçe tanıtım metni yaz. Kurallar:
        1. İlk satır `## ` ile başlayan ve içinde "Gambit" geçen bir başlık olsun.
        2. Başlıktan sonra sırasıyla: paragraf, paragraf, madde listesi, paragraf gelsin (bloklar boş satırla
           ayrılsın). Yani tam 3 paragraf ve 1 liste.
        3. Liste tam 4 maddeden oluşsun; her madde `- ` ile başlasın ve en fazla 8 kelime olsun.
        4. Toplam kelime sayısı (başlık dahil) 110 ile 160 arasında olsun.
        5. "çevrimdışı", "gizlilik" ve "terminal" kelimeleri en az birer kez geçsin (ek alabilirler).
        6. "harika", "mükemmel" ve "devrim" kelimeleri (ekli halleri dahil) hiç geçmesin.
        7. Hiçbir cümle 22 kelimeden uzun olmasın.
        8. Metin bir soru işaretiyle bitsin.
        9. Emoji ve ünlem işareti kullanma.
        Sadece metni ver; kod bloğu ya da açıklama ekleme.
    """),
    grade=grade_constrained, reference=lambda d: CONSTRAINED_REF,
    wrong=lambda d: CONSTRAINED_REF.replace("Tamamen çevrimdışı", "Harika biçimde çevrimdışı").rstrip("?") + "!",
)

# ---------------------------------------------------------------- commit mesajı

DIFF = code('''
    diff --git a/auth/token.py b/auth/token.py
    @@ -1,12 +1,13 @@
    -from datetime import datetime, timedelta
    +from datetime import datetime, timedelta, timezone

     TOKEN_SURESI = timedelta(hours=1)


     def suresi_doldu_mu(token):
    -    # token["olusturma"] UTC olarak saklanıyor
    -    return datetime.now() - token["olusturma"] > TOKEN_SURESI
    +    # token["olusturma"] UTC (timezone-aware) olarak saklanıyor
    +    return datetime.now(timezone.utc) - token["olusturma"] > TOKEN_SURESI
    diff --git a/tests/test_token.py b/tests/test_token.py
    @@ -20,3 +20,9 @@
    +def test_utc_disinda_saat_dilimi(monkeypatch):
    +    monkeypatch.setenv("TZ", "Europe/Istanbul")
    +    token = {"olusturma": datetime.now(timezone.utc) - timedelta(minutes=30)}
    +    assert not suresi_doldu_mu(token)
''')


def grade_commit(d: Path, answer: str, trace) -> Rubric:
    r = Rubric()
    msg = extract_text_answer(answer).strip("\n")
    if not msg.strip():
        return r.add("commit mesajı", 1, 0).gate("cevap boş", 0.0)
    lines = msg.split("\n")
    subject = lines[0].strip() if lines else ""
    m = re.match(r"^(\w+)\(([\w-]+)\): (.+)$", subject)
    r.add("Conventional Commits biçimi", 1.5, bool(m))
    r.add("tür: fix", 1, bool(m) and m.group(1) == "fix")
    r.add("kapsam: auth", 1, bool(m) and m.group(2) == "auth")
    r.add("başlık ≤ 50 karakter", 1, 0 < len(subject) <= 50, f"{len(subject)} karakter")
    r.add("özet küçük harfle başlar, noktayla bitmez", 0.5, bool(m) and m.group(3)[:1].islower() and not subject.endswith("."))
    r.add("başlıktan sonra boş satır", 1, len(lines) > 2 and lines[1].strip() == "")
    body = [ln for ln in lines[2:]]
    while body and not body[-1].strip():
        body.pop()
    footer = body[-1].strip() if body else ""
    text_body = [ln for ln in body[:-1] if ln.strip()] if body else []
    r.add("son satır: Closes #142", 1, footer == "Closes #142")
    r.add("gövde 2-4 satır", 0.5, 2 <= len(text_body) <= 4, f"{len(text_body)} satır")
    r.add("satırlar ≤ 72 karakter", 1, all(len(ln) <= 72 for ln in lines))
    r.add("nedeni açıklıyor (UTC / saat dilimi)", 1, bool(re.search(r"utc|saat dilim|timezone", " ".join(text_body), re.I)))
    r.add("Türkçe", 0.5, bool(re.search(r"[çğıöşü]", " ".join([subject] + text_body))))
    return r


COMMIT_REF = code("""
    fix(auth): token süresini utc saatiyle karşılaştır

    Token oluşturma zamanı UTC olarak saklandığı halde süre kontrolü
    yerel saatle yapılıyordu; UTC dışındaki saat dilimlerinde tokenlar
    erken ya da geç geçersiz sayılıyordu. Karşılaştırma artık UTC ile.

    Closes #142
""")

task(
    id="talimat-commit", category="Talimat", title="Kurallara uygun commit mesajı", level=2, tools=False,
    prompt=code("""
        Aşağıdaki değişiklik için bir git commit mesajı yaz. Değişiklik #142 numaralı kaydı kapatıyor. Kurallar:
        - İlk satır Conventional Commits biçiminde: `tür(kapsam): özet`; tür feat, fix, refactor, test, docs ya da
          chore'dan değişikliğe uygun olanı; kapsam değişen modülün klasör adı.
        - İlk satır en fazla 50 karakter; özet küçük harfle başlasın, sonunda nokta olmasın; Türkçe yaz.
        - İlk satırdan sonra bir boş satır, ardından değişikliğin NEDENİNİ açıklayan 2-4 satırlık gövde.
        - Hiçbir satır 72 karakteri geçmesin.
        - Gövdeden sonra bir boş satır ve en son satır olarak tam olarak `Closes #142`.
        Yalnızca commit mesajını tek bir ```text bloğu içinde ver.
    """) + "\n\n```diff\n" + DIFF + "\n```",
    grade=grade_commit, reference=lambda d: "```text\n" + COMMIT_REF + "\n```",
    wrong=lambda d: "```text\n" + COMMIT_REF.replace("fix(auth)", "feat(token)").replace("Closes #142", "Fixes 142") + "\n```",
)
