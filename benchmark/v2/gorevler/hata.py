"""Hata ayıklama: klasörde hatalı bir modül ve (hataların yalnızca bir kısmını yakalayan) bir test dosyası var.
Model hataları bulup düzeltir; gizli testler her hatayı ayrı ağırlıkla puanlar. Test dosyası değiştirilirse ceza."""

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

from core import Rubric, Trace, _run, code, danger, read, run_tests, task, write


def _sha(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode()).hexdigest()


_baseline: dict[str, set[int]] = {}


def grade_fix(d: Path, trace: Trace, *, lang: str, filename: str, tests: list, prelude: str, visible: tuple[str, str],
              buggy: str, verify_weight: float = 0.6) -> Rubric:
    """Hatalı özgün kodda zaten geçen testler puan maddesi değildir (hiçbir şey yapmamak puan getirmesin); düzeltme
    sonrası bozulurlarsa gerileme cezası (x0,85) uygulanır."""
    r = Rubric()
    vis_name, vis_text = visible
    vis_path = d / vis_name
    if not vis_path.is_file() or _sha(read(vis_path)) != _sha(vis_text):
        r.gate(f"{vis_name} değiştirilmiş/silinmiş", 0.5)
    src = read(d / filename)
    if not src.strip():
        r.add(f"{filename} var", 1, 0)
        r.gate(f"{filename} yok", 0.0)
        return r
    if reason := danger(src, lang):
        r.add("güvenlik", 1, 0)
        r.gate(reason, 0.0)
        return r
    module = Path(filename).stem if lang == "py" else filename
    key = _sha(buggy + prelude + repr(tests))
    if key not in _baseline:
        base_items, _ = run_tests(lang, {filename: buggy}, module, tests, prelude)
        _baseline[key] = {i for i, it in enumerate(base_items) if it.value >= 1}
    items, summary = run_tests(lang, {filename: src}, module, tests, prelude)
    for i, it in enumerate(items):
        if i not in _baseline[key]:
            r.items.append(it)
        elif it.value < 1:
            r.gate(f"gerileme: {it.name}", 0.85)
    # görünen testler (orijinal dosyayla) geçiyor mu
    with tempfile.TemporaryDirectory(prefix="gb2_", ignore_cleanup_errors=True) as tmp:
        write(Path(tmp) / filename, src)
        write(Path(tmp) / vis_name, vis_text)
        cmd = [sys.executable, vis_name] if lang == "py" else [shutil.which("node") or "node", vis_name]
        p_out, p_err, timed = _run(cmd, Path(tmp), 30)
        ok = not timed and ("TÜM TESTLER GEÇTİ" in p_out)
    r.add(f"{vis_name} geçiyor", 1.5, ok)
    r.add("düzeltmeyi kendisi doğruladı", verify_weight, trace.verified_after_write(filename))
    r.note(f"hatalar: {summary[:250]}" if summary else "")
    return r


def _setup(files: dict[str, str]):
    def setup(d: Path) -> None:
        for name, text in files.items():
            write(d / name, text)
    return setup


def _apply(filename: str, text: str):
    def apply(d: Path) -> str:
        write(d / filename, text)
        return "Hatalar düzeltildi, testler geçti."
    return apply


FIX_NOTE = ("Bu klasördeki `{f}` dosyasındaki hataları bul ve düzelt. `{t}` dosyasını DEĞİŞTİRME (onu `{run}` ile "
            "çalıştırabilirsin). Test dosyası hataların hepsini yakalamıyor olabilir: fonksiyonların açıklamalarında "
            "(docstring/yorum) yazan davranış esastır; düzeltmen gizli testlerle de sınanacak. Bitirince ne değiştirdiğini kısaca yaz.")

# ---------------------------------------------------------------- envanter

ENV_BUGGY = code('''
    class Envanter:
        """Basit stok takibi."""

        def __init__(self, baslangic={}):
            """baslangic: {ürün: adet} sözlüğü. Kopyalanır; dışarıdaki sözlük değişmez."""
            self.stok = baslangic
            self.fiyat = {}

        def ekle(self, urun, adet, fiyat=None):
            """Stoğa adet ekler. adet pozitif bir tam sayı değilse (0, negatif, 2.5, "3") ValueError.
            fiyat verilirse ürünün birim fiyatını günceller."""
            if adet < 0:
                raise ValueError("adet pozitif olmalı")
            self.stok[urun] = self.stok.get(urun, 0) + adet
            if fiyat is not None:
                self.fiyat[urun] = fiyat

        def dus(self, urun, adet):
            """Stoktan düşer. Stok yetersizse ya da ürün yoksa ValueError; stok tam sıfıra inebilir."""
            if self.stok.get(urun, 0) > adet:
                self.stok[urun] -= adet
            else:
                raise ValueError("yetersiz stok")

        def toplam_deger(self):
            """Fiyatı bilinen ürünlerin stok değerleri toplamı, kuruşa (2 ondalık) yuvarlanmış."""
            return round(sum(self.stok[u] * f for u, f in self.fiyat.items()), 1)

        def kritik(self, esik):
            """Stoğu esik değerine EŞİT ya da altında olan ürünlerin adlarını alfabetik sırayla döndürür."""
            return [u for u, a in self.stok.items() if a < esik]
''') + "\n"
ENV_FIXED = code('''
    class Envanter:
        """Basit stok takibi."""

        def __init__(self, baslangic=None):
            """baslangic: {ürün: adet} sözlüğü. Kopyalanır; dışarıdaki sözlük değişmez."""
            self.stok = dict(baslangic or {})
            self.fiyat = {}

        def ekle(self, urun, adet, fiyat=None):
            """Stoğa adet ekler. adet pozitif bir tam sayı değilse (0, negatif, 2.5, "3") ValueError.
            fiyat verilirse ürünün birim fiyatını günceller."""
            if not isinstance(adet, int) or isinstance(adet, bool) or adet <= 0:
                raise ValueError("adet pozitif olmalı")
            self.stok[urun] = self.stok.get(urun, 0) + adet
            if fiyat is not None:
                self.fiyat[urun] = fiyat

        def dus(self, urun, adet):
            """Stoktan düşer. Stok yetersizse ya da ürün yoksa ValueError; stok tam sıfıra inebilir."""
            if urun in self.stok and self.stok[urun] >= adet:
                self.stok[urun] -= adet
            else:
                raise ValueError("yetersiz stok")

        def toplam_deger(self):
            """Fiyatı bilinen ürünlerin stok değerleri toplamı, kuruşa (2 ondalık) yuvarlanmış."""
            return round(sum(self.stok.get(u, 0) * f for u, f in self.fiyat.items()), 2)

        def kritik(self, esik):
            """Stoğu esik değerine EŞİT ya da altında olan ürünlerin adlarını alfabetik sırayla döndürür."""
            return sorted(u for u, a in self.stok.items() if a <= esik)
''') + "\n"
ENV_TESTS = code('''
    from envanter import Envanter

    e = Envanter()
    e.ekle("kalem", 10, fiyat=12.35)
    e.ekle("defter", 3, fiyat=40)
    e.dus("kalem", 4)
    assert e.stok["kalem"] == 6, "dus"
    e.dus("defter", 3)
    assert e.stok["defter"] == 0, "stok sıfıra inebilmeli"
    assert e.toplam_deger() == 74.1, "toplam_deger"
    try:
        e.ekle("silgi", -2)
        raise AssertionError("negatif adet kabul edildi")
    except ValueError:
        pass
    print("TÜM TESTLER GEÇTİ")
''') + "\n"
ENV_PRELUDE = code('''
    def raises(f, *a):
        try:
            f(*a)
        except ValueError:
            return True
        except BaseException:
            return False
        return False

    def fresh_default():
        a = M.Envanter(); a.ekle("x", 1)
        b = M.Envanter()
        return b.stok == {}

    def copies_input():
        src = {"a": 5}
        e = M.Envanter(src); e.ekle("a", 1); e.ekle("b", 2)
        return src == {"a": 5} and e.stok == {"a": 6, "b": 2}

    def to_zero():
        e = M.Envanter({"a": 2}); e.dus("a", 2)
        return e.stok["a"] == 0

    def not_enough():
        e = M.Envanter({"a": 2})
        return raises(e.dus, "a", 3) and e.stok["a"] == 2 and raises(e.dus, "yok", 1)

    def value():
        e = M.Envanter()
        e.ekle("a", 3, fiyat=0.1); e.ekle("b", 7, fiyat=19.99); e.ekle("c", 5)
        return e.toplam_deger() == 140.23

    def bad_counts():
        e = M.Envanter()
        return all(raises(e.ekle, "a", v) for v in (0, -1, 2.5, "3")) and e.stok == {}

    def critical():
        e = M.Envanter({"zil": 2, "ayna": 5, "bant": 1, "cam": 9})
        return e.kritik(5) == ["ayna", "bant", "zil"] and e.kritik(0) == []
''')

task(
    id="hata-envanter", category="Hata ayıklama", title="Stok modülü (5 hata)", level=2,
    prompt=FIX_NOTE.format(f="envanter.py", t="test_envanter.py", run="python test_envanter.py"),
    setup=_setup({"envanter.py": ENV_BUGGY, "test_envanter.py": ENV_TESTS}),
    grade=lambda d, a, t: grade_fix(d, t, lang="py", filename="envanter.py", prelude=ENV_PRELUDE,
                                    visible=("test_envanter.py", ENV_TESTS), buggy=ENV_BUGGY, tests=[
        (1.5, "fresh_default()", "değişken varsayılan argüman"),
        (1, "copies_input()", "başlangıç sözlüğü kopyalanır"),
        (1.5, "to_zero()", "stok sıfıra inebilir"),
        (1, "not_enough()", "yetersiz stok / olmayan ürün"),
        (1.5, "value()", "2 ondalık yuvarlama"),
        (1.5, "bad_counts()", "0 / kesirli / metin adet reddedilir"),
        (1.5, "critical()", "kritik: eşit dahil, alfabetik"),
    ]),
    reference=_apply("envanter.py", ENV_FIXED),
    wrong=_apply("envanter.py", ENV_BUGGY.replace("> adet:", ">= adet:").replace("), 1)", "), 2)")),
)

# ---------------------------------------------------------------- tarih

DATE_BUGGY = code('''
    from datetime import date, timedelta


    def artik_yil(y):
        """Miladi takvimde artık yıl mı: 4'e bölünen yıllar; ancak 100'e bölünüp 400'e bölünmeyenler değil."""
        return y % 4 == 0 and y % 100 != 0


    def ay_sonu(y, m):
        """y yılının m. ayının (1-12) son günü."""
        gunler = [31, 29 if artik_yil(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return gunler[m]


    def ay_ekle(d, n):
        """d tarihine n ay ekler (n negatif olabilir). Gün yeni ayda yoksa ayın son gününe çekilir:
        31 Ocak 2024 + 1 ay = 29 Şubat 2024."""
        m = d.month + n
        y = d.year + m // 12
        m = m % 12
        return date(y, m, min(d.day, ay_sonu(y, m)))


    def is_gunu_say(bas, bit):
        """bas ve bit DAHİL aradaki hafta içi (Pzt-Cum) günlerin sayısı; bas > bit ise 0."""
        gun = 0
        d = bas
        while d < bit:
            if d.weekday() < 5:
                gun += 1
            d += timedelta(days=1)
        return gun
''') + "\n"
DATE_FIXED = code('''
    from datetime import date, timedelta


    def artik_yil(y):
        """Miladi takvimde artık yıl mı: 4'e bölünen yıllar; ancak 100'e bölünüp 400'e bölünmeyenler değil."""
        return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


    def ay_sonu(y, m):
        """y yılının m. ayının (1-12) son günü."""
        gunler = [31, 29 if artik_yil(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return gunler[m - 1]


    def ay_ekle(d, n):
        """d tarihine n ay ekler (n negatif olabilir). Gün yeni ayda yoksa ayın son gününe çekilir:
        31 Ocak 2024 + 1 ay = 29 Şubat 2024."""
        y, m0 = divmod(d.year * 12 + d.month - 1 + n, 12)
        m = m0 + 1
        return date(y, m, min(d.day, ay_sonu(y, m)))


    def is_gunu_say(bas, bit):
        """bas ve bit DAHİL aradaki hafta içi (Pzt-Cum) günlerin sayısı; bas > bit ise 0."""
        gun = 0
        d = bas
        while d <= bit:
            if d.weekday() < 5:
                gun += 1
            d += timedelta(days=1)
        return gun
''') + "\n"
DATE_TESTS = code('''
    import unittest
    from datetime import date

    from tarih import artik_yil, ay_ekle, is_gunu_say


    class TarihTest(unittest.TestCase):
        def test_artik(self):
            self.assertTrue(artik_yil(2024))
            self.assertFalse(artik_yil(2023))

        def test_ay_ekle(self):
            self.assertEqual(ay_ekle(date(2024, 1, 31), 1), date(2024, 2, 29))
            self.assertEqual(ay_ekle(date(2024, 3, 15), 2), date(2024, 5, 15))

        def test_is_gunu(self):
            self.assertEqual(is_gunu_say(date(2026, 3, 2), date(2026, 3, 6)), 5)  # Pzt-Cum


    if __name__ == "__main__":
        r = unittest.main(exit=False).result
        if r.wasSuccessful():
            print("TÜM TESTLER GEÇTİ")
''') + "\n"
DATE_PRELUDE = "from datetime import date"

task(
    id="hata-tarih", category="Hata ayıklama", title="Tarih yardımcıları (4 hata)", level=3,
    prompt=FIX_NOTE.format(f="tarih.py", t="test_tarih.py", run="python test_tarih.py"),
    setup=_setup({"tarih.py": DATE_BUGGY, "test_tarih.py": DATE_TESTS}),
    grade=lambda d, a, t: grade_fix(d, t, lang="py", filename="tarih.py", prelude=DATE_PRELUDE,
                                    visible=("test_tarih.py", DATE_TESTS), buggy=DATE_BUGGY, tests=[
        (1.5, "M.artik_yil(2000) and not M.artik_yil(1900) and M.artik_yil(2024) and not M.artik_yil(2025)", "400 kuralı"),
        (1, "M.ay_sonu(2026, 12) == 31 and M.ay_sonu(2026, 1) == 31 and M.ay_sonu(2026, 4) == 30", "ay_sonu indeksi"),
        (1, "M.ay_sonu(2000, 2) == 29 and M.ay_sonu(1900, 2) == 28", "Şubat sonu"),
        (1, "M.ay_ekle(date(2024, 1, 31), 1) == date(2024, 2, 29) and M.ay_ekle(date(2023, 1, 31), 1) == date(2023, 2, 28)"),
        (1.5, "M.ay_ekle(date(2025, 11, 30), 1) == date(2025, 12, 30) and M.ay_ekle(date(2025, 12, 15), 1) == date(2026, 1, 15)",
         "Aralık geçişi"),
        (1.5, "M.ay_ekle(date(2026, 3, 31), -1) == date(2026, 2, 28) and M.ay_ekle(date(2026, 1, 10), -13) == date(2024, 12, 10)",
         "negatif ay"),
        (0.5, "M.ay_ekle(date(2026, 5, 5), 0) == date(2026, 5, 5) and M.ay_ekle(date(2024, 2, 29), 12) == date(2025, 2, 28)"),
        (1.5, "M.is_gunu_say(date(2026, 3, 2), date(2026, 3, 6)) == 5 and M.is_gunu_say(date(2026, 3, 6), date(2026, 3, 6)) == 1",
         "uç günler dahil"),
        (1, "M.is_gunu_say(date(2026, 3, 1), date(2026, 3, 31)) == 22 and M.is_gunu_say(date(2026, 3, 7), date(2026, 3, 8)) == 0"),
        (0.5, "M.is_gunu_say(date(2026, 3, 9), date(2026, 3, 2)) == 0", "bas > bit"),
    ]),
    reference=_apply("tarih.py", DATE_FIXED),
    wrong=_apply("tarih.py", DATE_BUGGY.replace("gunler[m]", "gunler[m - 1]").replace("while d < bit", "while d <= bit")),
)

# ---------------------------------------------------------------- async JS

JS_BUGGY = code('''
    // Yardımcı işlemler

    // Her öğe için fn'i SIRAYLA çağırır (bir çağrı bitmeden sonrakine geçmez); sonuçları aynı sırada döndürür.
    async function siraylaIsle(ogeler, fn) {
      const sonuclar = [];
      ogeler.forEach(async (oge) => {
        sonuclar.push(await fn(oge));
      });
      return sonuclar;
    }

    // fn'i (deneme numarasıyla: 0, 1, 2...) en fazla `deneme` kez çağırır; ilk başarılı sonucu döndürür.
    // Hepsi başarısız olursa SON hatayı fırlatır.
    async function tekrarDene(fn, deneme = 3) {
      let sonHata;
      for (let i = 0; i <= deneme; i++) {
        try {
          return await fn(i);
        } catch (e) {
          sonHata = e;
        }
      }
    }

    // Her değerin kaç kez geçtiğini { deger: adet } nesnesi olarak döndürür.
    function say(dizi) {
      const sayac = {};
      for (const x of dizi) sayac[x] = sayac[x]++ || 1;
      return sayac;
    }

    // Sayıların ortalaması; boş dizide 0.
    function ortalama(dizi) {
      return dizi.reduce((a, b) => a + b) / dizi.length;
    }

    // anahtarFn(oge) sonucuna göre gruplar: { anahtar: [ogeler...] }; öğelerin sırası korunur.
    function grupla(dizi, anahtarFn) {
      return dizi.reduce((acc, oge) => {
        const k = anahtarFn(oge);
        (acc[k] = acc[k] || []).push(oge);
        return acc;
      }, {});
    }

    module.exports = { siraylaIsle, tekrarDene, say, ortalama, grupla };
''') + "\n"
JS_FIXED = (JS_BUGGY
            .replace("ogeler.forEach(async (oge) => {\n    sonuclar.push(await fn(oge));\n  });",
                     "for (const oge of ogeler) {\n    sonuclar.push(await fn(oge));\n  }")
            .replace("i <= deneme; i++", "i < deneme; i++")
            .replace("      sonHata = e;\n    }\n  }\n}", "      sonHata = e;\n    }\n  }\n  throw sonHata;\n}")
            .replace("sayac[x] = sayac[x]++ || 1;", "sayac[x] = (sayac[x] || 0) + 1;")
            .replace("return dizi.reduce((a, b) => a + b) / dizi.length;",
                     "return dizi.length ? dizi.reduce((a, b) => a + b, 0) / dizi.length : 0;"))
JS_TESTS = code('''
    const assert = require("assert");
    const { siraylaIsle, say, ortalama } = require("./islem.js");

    (async () => {
      assert.deepStrictEqual(say(["a", "b", "a"]), { a: 2, b: 1 });
      assert.strictEqual(ortalama([2, 4]), 3);
      const r = await siraylaIsle([1, 2, 3], async (x) => x * 10);
      assert.deepStrictEqual(r, [10, 20, 30]);
      console.log("TÜM TESTLER GEÇTİ");
    })().catch((e) => { console.error(e.message); process.exitCode = 1; });
''') + "\n"
JS_PRELUDE = code('''
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    async function sequential() {
      let active = 0, maxActive = 0;
      const r = await M.siraylaIsle([30, 5, 15], async (ms) => {
        active++; maxActive = Math.max(maxActive, active); await wait(ms); active--; return ms * 2;
      });
      return JSON.stringify(r) === "[60,10,30]" && maxActive === 1;
    }
    async function retryCount() {
      let calls = 0;
      try { await M.tekrarDene(async () => { calls++; throw new Error("e" + calls); }, 3); } catch (e) {
        return calls === 3 && e.message === "e3";
      }
      return false;
    }
    async function retrySuccess() {
      const seen = [];
      const v = await M.tekrarDene(async (i) => { seen.push(i); if (i < 2) throw new Error("x"); return "ok" + i; }, 5);
      return v === "ok2" && JSON.stringify(seen) === "[0,1,2]";
    }
    async function retryDefault() {
      let calls = 0;
      try { await M.tekrarDene(() => { calls++; throw new Error("y"); }); } catch (e) { return calls === 3; }
      return false;
    }
''')

task(
    id="hata-async-js", category="Hata ayıklama", title="Async JS yardımcıları (4 hata)", level=3,
    prompt=FIX_NOTE.format(f="islem.js", t="test.js", run="node test.js"),
    setup=_setup({"islem.js": JS_BUGGY, "test.js": JS_TESTS}),
    grade=lambda d, a, t: grade_fix(d, t, lang="js", filename="islem.js", prelude=JS_PRELUDE,
                                    visible=("test.js", JS_TESTS), buggy=JS_BUGGY, tests=[
        (2, "sequential()", "siraylaIsle sırayla ve sonuçlu"),
        (0.5, '(async () => JSON.stringify(await M.siraylaIsle([], async (x) => x)) === "[]")()'),
        (1.5, "retryCount()", "tekrarDene: tam deneme sayısı + son hata"),
        (1, "retrySuccess()", "tekrarDene: ilk başarı"),
        (0.5, "retryDefault()", "varsayılan 3 deneme"),
        (1.5, 'JSON.stringify(M.say(["x", "y", "x", "x", 3, "3"])) === JSON.stringify({ 3: 2, x: 3, y: 1 })', "say"),
        (1, 'M.ortalama([]) === 0 && M.ortalama([1, 2, 3, 4]) === 2.5', "ortalama"),
        (1, 'JSON.stringify(M.grupla([1, 2, 3, 4, 5], (x) => (x % 2 ? "tek" : "cift"))) === '
            '\'{"tek":[1,3,5],"cift":[2,4]}\'', "grupla bozulmamış"),
    ]),
    reference=_apply("islem.js", JS_FIXED),
    wrong=_apply("islem.js", JS_BUGGY.replace("sayac[x] = sayac[x]++ || 1;", "sayac[x] = (sayac[x] || 0) + 1;")),
)

# ---------------------------------------------------------------- önbellek dekoratörü

CACHE_BUGGY = code('''
    import time

    _onbellek = {}


    def onbellekle(ttl=None, saat=time.monotonic):
        """Fonksiyon sonuçlarını argümanlarına göre önbelleğe alan dekoratör.

        - Aynı argümanlarla (konumsal ve isimli; isimli argümanların yazılış sırası önemsiz) yapılan çağrılar
          fonksiyonu yeniden çalıştırmaz.
        - ttl (saniye) verilirse kayıt eklendiği andan ttl saniye geçtikten SONRA geçersiz olur (tam ttl anında
          hâlâ geçerlidir); geçersiz kayıt için fonksiyon yeniden çalıştırılır.
        - Her dekore edilen fonksiyonun önbelleği ayrıdır.
        - Hashlenemeyen argümanlarla (ör. liste) yapılan çağrılar önbelleğe alınmadan doğrudan çalıştırılır.
        - Sarılan fonksiyon adını ve docstring'ini korur. `temizle()` yalnızca kendi önbelleğini boşaltır;
          `bilgi()` {"isabet": n, "iska": m} döndürür (iska: fonksiyonun gerçekten çalıştırıldığı çağrılar).
        """
        def dekorator(f):
            isabet = iska = 0

            def sarmal(*args, **kwargs):
                nonlocal isabet, iska
                anahtar = args
                if anahtar in _onbellek:
                    deger, zaman = _onbellek[anahtar]
                    if ttl is None or saat() - zaman > ttl:
                        isabet += 1
                        return deger
                iska += 1
                deger = f(*args, **kwargs)
                _onbellek[anahtar] = (deger, saat())
                return deger

            sarmal.temizle = lambda: _onbellek.clear()
            sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
            return sarmal
        return dekorator
''') + "\n"
CACHE_FIXED = code('''
    import functools
    import time


    def onbellekle(ttl=None, saat=time.monotonic):
        """Fonksiyon sonuçlarını argümanlarına göre önbelleğe alan dekoratör (ayrıntılar özgün dosyada)."""
        def dekorator(f):
            cache = {}
            isabet = iska = 0

            @functools.wraps(f)
            def sarmal(*args, **kwargs):
                nonlocal isabet, iska
                anahtar = (args, tuple(sorted(kwargs.items())))
                try:
                    hash(anahtar)
                except TypeError:
                    iska += 1
                    return f(*args, **kwargs)
                if anahtar in cache:
                    deger, zaman = cache[anahtar]
                    if ttl is None or saat() - zaman <= ttl:
                        isabet += 1
                        return deger
                iska += 1
                deger = f(*args, **kwargs)
                cache[anahtar] = (deger, saat())
                return deger

            sarmal.temizle = cache.clear
            sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
            return sarmal
        return dekorator
''') + "\n"
CACHE_TESTS = code('''
    from onbellek import onbellekle

    cagri = []


    @onbellekle()
    def kare(x):
        """Karesini alır."""
        cagri.append(x)
        return x * x


    assert kare(3) == 9 and kare(3) == 9 and cagri == [3], "temel önbellek"
    assert kare.bilgi() == {"isabet": 1, "iska": 1}, "bilgi"


    @onbellekle()
    def us(x, n=2):
        return x ** n


    assert us(2, n=3) == 8 and us(2, n=4) == 16, "isimli argümanlar"
    assert kare.__name__ == "kare", "fonksiyon adı korunmalı"
    print("TÜM TESTLER GEÇTİ")
''') + "\n"
CACHE_PRELUDE = code('''
    class Saat:
        def __init__(self):
            self.t = 100.0
        def __call__(self):
            return self.t

    def kwargs_order():
        calls = []
        @M.onbellekle()
        def f(a, b=0, c=0):
            calls.append(1); return a + b * 10 + c * 100
        return f(1, b=2, c=3) == 321 and f(1, c=3, b=2) == 321 and len(calls) == 1 and f(1, b=3, c=2) == 231

    def separate():
        @M.onbellekle()
        def a(x): return "a"
        @M.onbellekle()
        def b(x): return "b"
        return a(1) == "a" and b(1) == "b"

    def ttl_ok():
        s = Saat(); calls = []
        @M.onbellekle(ttl=10, saat=s)
        def f(x):
            calls.append(x); return len(calls)
        r1 = f(1); s.t += 5; r2 = f(1); s.t += 5; r3 = f(1); s.t += 0.5; r4 = f(1)
        return (r1, r2, r3, r4) == (1, 1, 1, 2)

    def unhashable():
        calls = []
        @M.onbellekle()
        def f(xs):
            calls.append(1); return sum(xs)
        return f([1, 2]) == 3 and f([1, 2]) == 3 and len(calls) == 2

    def wraps_ok():
        @M.onbellekle(ttl=5)
        def topla(a, b):
            """İki sayıyı toplar."""
            return a + b
        return topla.__name__ == "topla" and topla.__doc__ == "İki sayıyı toplar." and topla(2, 3) == 5

    def clear_own():
        ca, cb = [], []
        @M.onbellekle()
        def a(x):
            ca.append(x); return x
        @M.onbellekle()
        def b(x):
            cb.append(x); return x
        a(1); b(1); a.temizle(); a(1); b(1)
        return len(ca) == 2 and len(cb) == 1

    def info():
        @M.onbellekle()
        def f(x): return x
        f(1); f(1); f(2); f([3]); f(1)
        return f.bilgi() == {"isabet": 2, "iska": 3}
''')

task(
    id="hata-onbellek", category="Hata ayıklama", title="Önbellek dekoratörü (6 hata)", level=4,
    prompt=FIX_NOTE.format(f="onbellek.py", t="test_onbellek.py", run="python test_onbellek.py"),
    setup=_setup({"onbellek.py": CACHE_BUGGY, "test_onbellek.py": CACHE_TESTS}),
    grade=lambda d, a, t: grade_fix(d, t, lang="py", filename="onbellek.py", prelude=CACHE_PRELUDE,
                                    visible=("test_onbellek.py", CACHE_TESTS), buggy=CACHE_BUGGY, tests=[
        (1.5, "kwargs_order()", "isimli argümanlar anahtarda (sıra önemsiz)"),
        (1.5, "separate()", "fonksiyon başına ayrı önbellek"),
        (2, "ttl_ok()", "ttl: tam sınırda geçerli, sonra yenilenir"),
        (1.5, "unhashable()", "hashlenemeyen argüman"),
        (1, "wraps_ok()", "ad ve docstring korunur"),
        (1, "clear_own()", "temizle yalnız kendi önbelleğini"),
        (1, "info()", "bilgi sayaçları"),
    ]),
    reference=_apply("onbellek.py", CACHE_FIXED),
    wrong=_apply("onbellek.py", CACHE_BUGGY.replace("anahtar = args", "anahtar = (args, tuple(sorted(kwargs.items())))")),
)
