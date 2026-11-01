"""Ajan görevleri: birden fazla dosyaya dokunan, keşif + değişiklik + doğrulama gerektiren gerçekçi işler.
Gizli testler ve klasörün son durumu ayrı ayrı ağırlıklandırılır."""

import ast
import json
import re
import sys
import tempfile
from pathlib import Path

from core import Rubric, _run, code, danger, locate, read, run_tests, task, write

AGENT_NOTE = "Araçlarını kullanarak işi bu klasörde kendin yap ve sonucu doğrula. Bitirince kısaca ne yaptığını yaz."


def _setup(files: dict[str, str]):
    def setup(d: Path) -> None:
        for name, text in files.items():
            write(d / name, text)
    return setup


def _project_danger(d: Path, *paths: str) -> str | None:
    """Notlandırıcının çalıştıracağı dosyalarda güvenlik taraması (modelin kendi yardımcı betikleri hariç)."""
    for p in sorted({q for pat in paths for q in d.glob(pat) if q.is_file()}):
        if reason := danger(read(p)):
            return f"{p.relative_to(d).as_posix()}: {reason}"
    return None


def _copy_tree(src: Path, dst: Path, skip=("__pycache__",)) -> None:
    for p in src.rglob("*"):
        if any(s in p.parts for s in skip) or not p.is_file():
            continue
        t = dst / p.relative_to(src)
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(p.read_bytes())


def _run_in_copy(d: Path, cmd: list[str], timeout: float = 60) -> tuple[str, str, bool]:
    with tempfile.TemporaryDirectory(prefix="gb2_", ignore_cleanup_errors=True) as tmp:
        _copy_tree(d, Path(tmp))
        return _run(cmd, Path(tmp), timeout)


# ---------------------------------------------------------------- kütüphane: yeni özellik

LIB_MODELS = code('''
    from dataclasses import dataclass
    from datetime import date


    @dataclass
    class Kitap:
        id: int
        ad: str
        yazar: str


    @dataclass
    class Uye:
        id: int
        ad: str
        tur: str = "standart"  # "standart" ya da "ogrenci"


    @dataclass
    class Odunc:
        kitap_id: int
        uye_id: int
        alinma: date
        iade: date | None = None
''') + "\n"
LIB_SERVICE = code('''
    from .modeller import Odunc


    class KutuphaneServisi:
        def __init__(self):
            self.kitaplar = {}
            self.uyeler = {}
            self.kayitlar = []

        def kitap_ekle(self, kitap):
            self.kitaplar[kitap.id] = kitap

        def uye_ekle(self, uye):
            self.uyeler[uye.id] = uye

        def _aktif(self, kitap_id):
            return next((k for k in self.kayitlar if k.kitap_id == kitap_id and k.iade is None), None)

        def odunc_ver(self, kitap_id, uye_id, tarih):
            """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
            if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
                raise ValueError("kitap ya da üye bulunamadı")
            if self._aktif(kitap_id):
                raise ValueError("kitap zaten ödünçte")
            kayit = Odunc(kitap_id, uye_id, tarih)
            self.kayitlar.append(kayit)
            return kayit

        def iade_al(self, kitap_id, tarih):
            """Kitabın iadesini alır ve ödünç kaydını döndürür. Kitap ödünçte değilse ValueError."""
            kayit = self._aktif(kitap_id)
            if kayit is None:
                raise ValueError("kitap ödünçte değil")
            kayit.iade = tarih
            return kayit

        def oduncteki_kitaplar(self, uye_id):
            return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
''') + "\n"
LIB_INIT = "from .modeller import Kitap, Odunc, Uye\nfrom .servis import KutuphaneServisi\n"
LIB_TESTS = code('''
    import unittest
    from datetime import date

    from kutuphane import Kitap, KutuphaneServisi, Uye


    def servis():
        s = KutuphaneServisi()
        for i in range(1, 8):
            s.kitap_ekle(Kitap(i, f"Kitap {i}", "Yazar"))
        s.uye_ekle(Uye(1, "Ayşe"))
        s.uye_ekle(Uye(2, "Can", "ogrenci"))
        return s


    class KutuphaneTest(unittest.TestCase):
        def test_odunc_ve_iade(self):
            s = servis()
            s.odunc_ver(1, 1, date(2026, 1, 1))
            self.assertEqual(s.oduncteki_kitaplar(1), [1])
            kayit = s.iade_al(1, date(2026, 1, 5))
            self.assertEqual(kayit.iade, date(2026, 1, 5))
            self.assertEqual(s.oduncteki_kitaplar(1), [])

        def test_cift_odunc(self):
            s = servis()
            s.odunc_ver(1, 1, date(2026, 1, 1))
            with self.assertRaises(ValueError):
                s.odunc_ver(1, 2, date(2026, 1, 2))


    if __name__ == "__main__":
        r = unittest.main(exit=False).result
        if r.wasSuccessful():
            print("TÜM TESTLER GEÇTİ")
''') + "\n"
LIB_PRELUDE = code('''
    from datetime import date, timedelta
    K = M

    def servis():
        s = K.KutuphaneServisi()
        for i in range(1, 10):
            s.kitap_ekle(K.Kitap(i, f"Kitap {i}", "Yazar"))
        s.uye_ekle(K.Uye(1, "Ayşe"))
        s.uye_ekle(K.Uye(2, "Can", "ogrenci"))
        return s

    def fee(days, uye=1):
        s = servis()
        s.odunc_ver(3, uye, date(2026, 1, 1))
        k = s.iade_al(3, date(2026, 1, 1) + timedelta(days=days))
        return getattr(k, "ceza", None)

    def close(a, b):
        return isinstance(a, (int, float)) and abs(a - b) < 1e-6

    def raises(f, *a):
        try:
            f(*a)
        except ValueError:
            return True
        except BaseException:
            return False
        return False

    def limit_std():
        s = servis()
        for i in (1, 2, 3):
            s.odunc_ver(i, 1, date(2026, 2, 1))
        ok = raises(s.odunc_ver, 4, 1, date(2026, 2, 2))
        s.iade_al(2, date(2026, 2, 3))
        s.odunc_ver(4, 1, date(2026, 2, 3))
        return ok and s.oduncteki_kitaplar(1) == [1, 3, 4]

    def limit_student():
        s = servis()
        for i in range(1, 6):
            s.odunc_ver(i, 2, date(2026, 2, 1))
        return raises(s.odunc_ver, 6, 2, date(2026, 2, 1)) and len(s.oduncteki_kitaplar(2)) == 5

    def total():
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1)); s.iade_al(1, date(2026, 1, 20))   # 5 gün gecikme: 12.50
        s.odunc_ver(2, 1, date(2026, 1, 1)); s.iade_al(2, date(2026, 1, 10))   # gecikme yok
        s.odunc_ver(1, 1, date(2026, 2, 1)); s.iade_al(1, date(2026, 3, 3))    # 30 gün: 16 gecikme: 17.5 + 45 = 62.5
        s.odunc_ver(5, 2, date(2026, 1, 1)); s.iade_al(5, date(2026, 1, 30))   # başka üye
        s.odunc_ver(6, 1, date(2026, 3, 1))                                     # iade edilmemiş: sayılmaz
        return close(s.toplam_ceza(1), 75.0) and close(s.toplam_ceza(2), 12.5 * 0 + 0.5 * (7 * 2.5 + 8 * 5.0))
''')

def grade_library(d: Path, trace) -> Rubric:
    r = Rubric()
    if reason := _project_danger(d, "kutuphane/**/*.py", "test_kutuphane.py"):
        return r.add("güvenlik", 1, 0).gate(reason, 0.0)
    files = {str(p.relative_to(d).as_posix()): read(p) for p in (d / "kutuphane").rglob("*.py")} if (d / "kutuphane").is_dir() else {}
    if not files:
        return r.add("kutuphane paketi", 1, 0).gate("kutuphane paketi yok", 0.0)
    items, summary = run_tests("py", files, "kutuphane", [
        (1, "close(fee(14), 0) and close(fee(3), 0)", "14 güne kadar ceza yok"),
        (1.5, "close(fee(15), 2.5) and close(fee(21), 17.5)", "ilk 7 gün 2,50"),
        (1.5, "close(fee(22), 22.5) and close(fee(30), 62.5)", "sonraki günler 5,00"),
        (1, "close(fee(60), 150) and close(fee(400), 150)", "150 TL sınırı"),
        (1.5, "close(fee(21, 2), 8.75) and close(fee(100, 2), 75)", "öğrenci indirimi (sınırdan sonra)"),
        (1.5, "total()", "toplam_ceza"),
        (1.5, "limit_std()", "standart üye sınırı 3"),
        (1, "limit_student()", "öğrenci sınırı 5"),
        (0.5, "K.Odunc(1, 1, date(2026, 1, 1)).ceza == 0.0", "ceza alanı varsayılanı"),
    ], LIB_PRELUDE)
    r.extend(items)
    r.note(f"hatalar: {summary[:200]}" if summary else "")
    if not any(it.value for it in items[:-1]):
        r.gate("istenen özelliklerin hiçbiri çalışmıyor", 0.1)
    with tempfile.TemporaryDirectory(prefix="gb2_", ignore_cleanup_errors=True) as tmp:
        _copy_tree(d / "kutuphane", Path(tmp) / "kutuphane")
        write(Path(tmp) / "test_kutuphane.py", LIB_TESTS)
        out, err, _ = _run([sys.executable, "test_kutuphane.py"], Path(tmp), 60)
    r.add("eski testler hâlâ geçiyor", 1.5, "TÜM TESTLER GEÇTİ" in out)
    test_text = read(d / "test_kutuphane.py")
    new_tests = len(re.findall(r"^\s*def test_\w+", test_text, re.M)) - 2
    out2, _, _ = _run_in_copy(d, [sys.executable, "test_kutuphane.py"])
    r.add("yeni testler eklenmiş ve geçiyor", 1, (min(new_tests, 3) / 3) * (1.0 if "TÜM TESTLER GEÇTİ" in out2 else 0.3))
    r.add("kendisi doğruladı", 0.5, trace.verified_after_write())
    return r


def ref_library(d: Path) -> str:
    write(d / "kutuphane/modeller.py", LIB_MODELS.replace("    iade: date | None = None",
                                                          "    iade: date | None = None\n    ceza: float = 0.0"))
    svc = LIB_SERVICE.replace(code('''
        if self._aktif(kitap_id):
                    raise ValueError("kitap zaten ödünçte")
    '''), code('''
        if self._aktif(kitap_id):
                    raise ValueError("kitap zaten ödünçte")
                sinir = 5 if self.uyeler[uye_id].tur == "ogrenci" else 3
                if len(self.oduncteki_kitaplar(uye_id)) >= sinir:
                    raise ValueError("ödünç sınırı")
    ''')).replace(code('''
        kayit.iade = tarih
                return kayit
    '''), code('''
        kayit.iade = tarih
                gec = max(0, (tarih - kayit.alinma).days - 14)
                ceza = min(150.0, min(gec, 7) * 2.5 + max(0, gec - 7) * 5.0)
                if self.uyeler[kayit.uye_id].tur == "ogrenci":
                    ceza *= 0.5
                kayit.ceza = round(ceza, 2)
                return kayit

            def toplam_ceza(self, uye_id):
                return round(sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None), 2)
    '''))
    assert "toplam_ceza" in svc and "sinir" in svc
    write(d / "kutuphane/servis.py", svc)
    tests = LIB_TESTS.replace('if __name__ == "__main__":', code('''
        class CezaTest(unittest.TestCase):
            def test_ceza_yok(self):
                s = servis(); s.odunc_ver(1, 1, date(2026, 1, 1))
                self.assertEqual(s.iade_al(1, date(2026, 1, 15)).ceza, 0)

            def test_ceza(self):
                s = servis(); s.odunc_ver(1, 1, date(2026, 1, 1))
                self.assertEqual(s.iade_al(1, date(2026, 1, 31)).ceza, 62.5)

            def test_sinir(self):
                s = servis()
                for i in (1, 2, 3):
                    s.odunc_ver(i, 1, date(2026, 1, 1))
                with self.assertRaises(ValueError):
                    s.odunc_ver(4, 1, date(2026, 1, 1))


        if __name__ == "__main__":
    '''))
    assert "CezaTest" in tests
    write(d / "test_kutuphane.py", tests)
    return "Özellik eklendi, testler geçti."


task(
    id="ajan-kutuphane", category="Ajan", title="Projeye gecikme cezası özelliği ekleme", level=3,
    prompt=code("""
        Bu klasördeki `kutuphane` paketine (Python) yeni özellikler ekle:
        1. `Odunc` kaydına `ceza: float = 0.0` alanı ekle. `iade_al(kitap_id, tarih)` iade sırasında cezayı hesaplayıp
           kayda yazsın (dönüş değeri yine kayıt olsun).
        2. Ceza kuralları: ödünç süresi 14 gün (gün sayısı = iade tarihi − alınma tarihi). 14 günü aşan her gün
           gecikmedir. Gecikmenin ilk 7 günü için günlük 2,50 TL, sonraki günler için günlük 5,00 TL. Ceza en fazla
           150 TL olur. Üye türü "ogrenci" ise ceza (150 TL sınırı uygulandıktan sonra) %50 indirimlidir. Sonuç 2
           ondalığa yuvarlanır.
        3. `KutuphaneServisi.toplam_ceza(uye_id) -> float`: üyenin iade edilmiş tüm ödünçlerinin cezaları toplamı.
        4. Aynı anda ödünçte tutulabilecek kitap sınırı: "standart" üye 3, "ogrenci" 5. Sınır aşılırsa `odunc_ver`
           ValueError fırlatsın.
        Mevcut `test_kutuphane.py` testleri geçmeye devam etmeli (`python test_kutuphane.py`); yeni özellikler için
        bu dosyaya testler ekle.
    """) + "\n" + AGENT_NOTE,
    setup=_setup({"kutuphane/__init__.py": LIB_INIT, "kutuphane/modeller.py": LIB_MODELS,
                  "kutuphane/servis.py": LIB_SERVICE, "test_kutuphane.py": LIB_TESTS}),
    grade=lambda d, a, t: grade_library(d, t), reference=ref_library,
    wrong=lambda d: (ref_library(d), write(d / "kutuphane/servis.py", read(d / "kutuphane/servis.py")
                     .replace("ceza *= 0.5", "ceza *= 1").replace(">= sinir", "> sinir")), "")[-1],
)

# ---------------------------------------------------------------- yeniden adlandırma

REN_HESAP = code('''
    """KDV hesapları."""


    def hesapKdv(tutar, oran=0.20):
        """Tutarın KDV'sini döndürür (kuruşa yuvarlanmış)."""
        return round(tutar * oran, 2)


    def hesapKdvDahil(tutar, oran=0.20):
        """KDV dahil tutarı döndürür."""
        return round(tutar + hesapKdv(tutar, oran), 2)


    def toplam_tutar(kalemler):
        """[(fiyat, adet, kdv_orani), ...] listesinin KDV dahil toplamı."""
        return round(sum(f * a + hesapKdv(f * a, o) for f, a, o in kalemler), 2)
''') + "\n"
REN_INIT = "from .hesap import hesapKdv, hesapKdvDahil, toplam_tutar\n"
REN_RAPOR = code('''
    from fatura.hesap import hesapKdv as kdv
    from fatura.hesap import hesapKdvDahil


    def satir(ad, tutar, oran=0.20):
        return f"{ad:<10} {tutar:>10.2f} KDV {kdv(tutar, oran):>8.2f} TOPLAM {hesapKdvDahil(tutar, oran):>10.2f}"
''') + "\n"
REN_APP = code('''
    import fatura
    from fatura.rapor import satir

    print(satir("Kalem", 125.0))
    print(satir("Kitap", 300.0, 0.10))
    print("KDV:", fatura.hesapKdv(1000))
    print("Toplam:", fatura.toplam_tutar([(100, 2, 0.2), (50, 1, 0.1)]))
''') + "\n"
REN_TEST = code('''
    import unittest

    from fatura import hesapKdv, hesapKdvDahil, toplam_tutar


    class HesapTest(unittest.TestCase):
        def test_kdv(self):
            self.assertEqual(hesapKdv(100), 20.0)
            self.assertEqual(hesapKdv(100, 0.10), 10.0)

        def test_dahil(self):
            self.assertEqual(hesapKdvDahil(100), 120.0)

        def test_toplam(self):
            self.assertEqual(toplam_tutar([(100, 2, 0.2), (50, 1, 0.1)]), 295.0)


    if __name__ == "__main__":
        unittest.main()
''') + "\n"
REN_README = code('''
    # fatura

    KDV hesaplama yardımcıları.

    ```python
    from fatura import hesapKdv
    hesapKdv(100)        # 20.0
    hesapKdvDahil(100)   # 120.0
    ```

    `hesapKdv(tutar, oran=0.20)` tutarın KDV'sini döndürür.
''') + "\n"
REN_FILES = {"fatura/__init__.py": REN_INIT, "fatura/hesap.py": REN_HESAP, "fatura/rapor.py": REN_RAPOR,
             "uygulama.py": REN_APP, "tests/__init__.py": "", "tests/test_hesap.py": REN_TEST, "README.md": REN_README}
REN_CHECK = code('''
    import json, warnings
    res = {}
    import fatura
    from fatura import hesap
    res["yeni"] = hasattr(fatura, "kdv_hesapla") and hesap.kdv_hesapla(250) == 50.0 and hesap.kdv_hesapla(100, 0.1) == 10.0
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            v = fatura.hesapKdv(100)
        except Exception:
            v = None
    res["eski_uyari"] = v == 20.0 and any(issubclass(x.category, DeprecationWarning) for x in w)
    res["eski_var"] = v == 20.0
    res["dahil"] = getattr(fatura, "hesapKdvDahil", None) is not None and fatura.hesapKdvDahil(100) == 120.0
    print(json.dumps(res))
''')


def grade_rename(d: Path, trace) -> Rubric:
    r = Rubric()
    if reason := _project_danger(d, "fatura/**/*.py", "tests/**/*.py", "uygulama.py"):
        return r.add("güvenlik", 1, 0).gate(reason, 0.0)
    out, err, _ = _run_in_copy(d, [sys.executable, "-c", REN_CHECK])
    try:
        res = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        res = {}
        r.note("kontrol betiği çalışmadı: " + (err or out)[-200:])
    r.add("kdv_hesapla tanımlı ve dışa aktarılmış", 1.5, res.get("yeni", False))
    if not res.get("yeni"):
        r.gate("yeniden adlandırma yapılmamış (kdv_hesapla yok)", 0.15)
    r.add("hesapKdv geriye uyumlu + DeprecationWarning", 1.5, 1.0 if res.get("eski_uyari") else (0.4 if res.get("eski_var") else 0))
    r.add("hesapKdvDahil adı değişmemiş", 1.5, res.get("dahil", False))
    leftovers = []
    for p in d.rglob("*.py"):
        rel = p.relative_to(d).as_posix()
        if "__pycache__" in rel or rel.startswith("_"):
            continue
        n = len(re.findall(r"\bhesapKdv\b", read(p)))
        if rel == "fatura/hesap.py":
            n = max(0, n - 2)  # uyumluluk tanımı (def + uyarı metni)
        elif rel == "fatura/__init__.py":
            n = max(0, n - 1)
        if n:
            leftovers.append(f"{rel}:{n}")
    r.add("eski ad başka yerde kullanılmıyor", 2, max(0.0, 1 - 0.25 * len(leftovers)), ", ".join(leftovers))
    readme = read(d / "README.md")
    r.add("README güncellenmiş", 0.5, "kdv_hesapla" in readme and not re.search(r"\bhesapKdv\(100\)", readme))
    out, err, _ = _run_in_copy(d, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."])
    ran = re.search(r"Ran (\d+) test", err)
    r.add("testler geçiyor", 1.5, bool(ran) and "OK" in err.splitlines()[-1] if err.strip() else False)
    r.add("test sayısı azalmamış", 0.5, bool(ran) and int(ran.group(1)) >= 3)
    app_out, _, _ = _run_in_copy(d, [sys.executable, "uygulama.py"])
    want_out = _orig_app_output()
    r.add("uygulama.py çıktısı aynı", 1, app_out.replace("\r\n", "\n").strip() == want_out.strip())
    r.add("kendisi doğruladı", 0.5, trace.verified_after_write())
    return r


_app_cache: list[str] = []


def _orig_app_output() -> str:
    if not _app_cache:
        with tempfile.TemporaryDirectory(prefix="gb2_", ignore_cleanup_errors=True) as tmp:
            for n, t in REN_FILES.items():
                write(Path(tmp) / n, t)
            out, _, _ = _run([sys.executable, "uygulama.py"], Path(tmp), 30)
        _app_cache.append(out.replace("\r\n", "\n"))
    return _app_cache[0]


def ref_rename(d: Path) -> str:
    write(d / "fatura/hesap.py", code('''
        """KDV hesapları."""
        import warnings


        def kdv_hesapla(tutar, oran=0.20):
            """Tutarın KDV'sini döndürür (kuruşa yuvarlanmış)."""
            return round(tutar * oran, 2)


        def hesapKdv(tutar, oran=0.20):
            warnings.warn("hesapKdv yerine kdv_hesapla kullanın", DeprecationWarning, stacklevel=2)
            return kdv_hesapla(tutar, oran)


        def hesapKdvDahil(tutar, oran=0.20):
            """KDV dahil tutarı döndürür."""
            return round(tutar + kdv_hesapla(tutar, oran), 2)


        def toplam_tutar(kalemler):
            """[(fiyat, adet, kdv_orani), ...] listesinin KDV dahil toplamı."""
            return round(sum(f * a + kdv_hesapla(f * a, o) for f, a, o in kalemler), 2)
    ''') + "\n")
    write(d / "fatura/__init__.py", "from .hesap import hesapKdv, hesapKdvDahil, kdv_hesapla, toplam_tutar\n")
    for name in ("fatura/rapor.py", "uygulama.py", "tests/test_hesap.py", "README.md"):
        write(d / name, re.sub(r"\bhesapKdv\b", "kdv_hesapla", read(d / name)))
    return "Yeniden adlandırıldı."


task(
    id="ajan-yeniden-adlandir", category="Ajan", title="Kod tabanında güvenli yeniden adlandırma", level=3,
    prompt=code("""
        Bu klasördeki Python projesinde `hesapKdv` fonksiyonunun adını her yerde `kdv_hesapla` olarak değiştir:
        tanım, tüm çağrılar ve importlar (takma adla import edilenler dahil), testler ve README. Adında `hesapKdv`
        geçen BAŞKA isimlere (ör. `hesapKdvDahil`) dokunma. Geriye uyumluluk için `fatura/hesap.py` içinde
        `hesapKdv` adı kalsın: yeni fonksiyonu çağırsın ve `DeprecationWarning` uyarısı versin; `fatura` paketi hem
        eski hem yeni adı dışa aktarsın. Testler `python -m unittest discover -s tests -t .` ile çalışır ve geçmeli;
        `python uygulama.py` çıktısı değişmemeli.
    """) + "\n" + AGENT_NOTE,
    setup=_setup(REN_FILES), grade=lambda d, a, t: grade_rename(d, t), reference=ref_rename,
    wrong=lambda d: (ref_rename(d), write(d / "fatura/hesap.py", read(d / "fatura/hesap.py").replace("hesapKdvDahil", "kdv_hesaplaDahil")),
                     write(d / "fatura/__init__.py", "from .hesap import kdv_hesapla, toplam_tutar\n"), "")[-1],
)

# ---------------------------------------------------------------- dağınık veri temizleme

ORDERS_RAW = [
    '{"id": 1, "musteri": "Ayşe", "tutar": 1234.5, "tarih": "2025-03-01", "durum": "tamamlandı"}',
    '{"id": 2, "musteri": "Mehmet", "tutar": "1.234,50 TL", "tarih": "05.03.2025", "durum": "TAMAMLANDI"}',
    '{"id": 3, "musteri": "Zeynep", "tutar": "₺99,90", "tarih": "2025-03-17", "durum": "iptal"}',
    '{"id": 4, "musteri": "Ayşe", "tutar": "2.500 TL", "tarih": "2 Nisan 2025", "durum": "tamamlandı"}',
    '{"id": 5, "musteri": "Can", "tutar": "15.75", "tarih": "2025/04/09", "durum": "kargoda"}',
    '{"id": 6, "musteri": "Mehmet", "tutar": 300, "tarih": "2025-04-30", "durum": "İPTAL"}',
    "{bozuk satır",
    "",
    '{"id": 7, "musteri": "Zeynep", "tutar": "1.000,00", "tarih": "01.05.2025", "durum": "tamamlandı"}',
    '{"id": 8, "musteri": "Can", "tarih": "2025-05-02", "durum": "tamamlandı"}',
    '{"id": 2, "musteri": "Mehmet", "tutar": "2.000,25 TL", "tarih": "06.03.2025", "durum": "tamamlandı"}',
    '{"id": 9, "musteri": " Ayşe ", "tutar": "450,5", "tarih": "15 Mayıs 2025", "durum": "Tamamlandı"}',
    '{"id": 10, "musteri": "Deniz", "tutar": "abc", "tarih": "2025-05-20", "durum": "tamamlandı"}',
    '{"id": 11, "musteri": "Deniz", "tutar": 80, "tarih": "2025-13-01", "durum": "tamamlandı"}',
    '[1, 2, 3]',
    '{"id": 12, "musteri": "Elif", "tutar": "12.345,678", "tarih": "2025-06-01", "durum": "tamamlandı"}',
    '{"id": 13, "musteri": "Elif", "tutar": 1e3, "tarih": "30 Haziran 2025", "durum": "kargoda"}',
    '{"id": 14, "musteri": "Can", "tutar": "3,5", "tarih": "2025-06-15", "durum": "iptal"}',
    '{"id": 15, "musteri": "Burak", "tutar": "7.5", "tarih": "2025-06-20", "durum": "tamamlandı"} ',
    "   ",
    '{"id": 4, "musteri": "Ayşe", "tutar": "2.600 TL", "tarih": "3 Nisan 2025", "durum": "tamamlandı"}',
]
# Geçerli ve tekil (aynı id'nin son geçerli kaydı): beklenen özet elle hesaplandı
ORDERS_EXPECTED = {
    "gecerli_kayit": 12,
    "hatali_satir": 5,
    "iptal_sayisi": 3,
    "toplam_tutar": 1234.5 + 2000.25 + 2600 + 15.75 + 1000 + 450.5 + 12345.678 + 1000 + 7.5,
    "aylik": {"2025-03": 1234.5 + 2000.25, "2025-04": 2600 + 15.75, "2025-05": 1000 + 450.5,
              "2025-06": 12345.678 + 1000 + 7.5},
    "en_cok_harcayan": "Elif",
}


def grade_orders(d: Path, trace) -> Rubric:
    r = Rubric()
    f, factor, where = locate(d, "ozet.json")
    try:
        got = json.loads(read(f)) if f else None
        assert isinstance(got, dict)
    except (ValueError, AssertionError):
        return r.add("ozet.json okunabilir", 1, 0).gate("ozet.json yok ya da geçersiz JSON", 0.0)
    if where:
        r.gate(where, factor)
    exp = ORDERS_EXPECTED

    def num(key, w):
        v = got.get(key)
        ok = isinstance(v, (int, float)) and not isinstance(v, bool) and abs(v - round(exp[key], 2)) < 0.006
        near = isinstance(v, (int, float)) and abs(v - exp[key]) / max(abs(exp[key]), 1) < 0.02
        r.add(key, w, 1.0 if ok else (0.4 if near else 0.0), "" if ok else f"beklenen {round(exp[key], 2)}, bulunan {v!r}")

    num("gecerli_kayit", 1.5)
    num("hatali_satir", 1.5)
    num("iptal_sayisi", 1)
    num("toplam_tutar", 2)
    months = got.get("aylik") if isinstance(got.get("aylik"), dict) else {}
    for m, v in exp["aylik"].items():
        gv = months.get(m)
        ok = isinstance(gv, (int, float)) and abs(gv - round(v, 2)) < 0.006
        r.add(f"aylik[{m}]", 0.75, ok, "" if ok else f"beklenen {round(v, 2)}, bulunan {gv!r}")
    r.add("aylik: fazla ay yok", 0.5, set(months) == set(exp["aylik"]))
    r.add("en_cok_harcayan", 1, str(got.get("en_cok_harcayan", "")).strip() == exp["en_cok_harcayan"])
    return r


def ref_orders(d: Path) -> str:
    out = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in ORDERS_EXPECTED.items()}
    out["aylik"] = {k: round(v, 2) for k, v in ORDERS_EXPECTED["aylik"].items()}
    write(d / "ozet.json", json.dumps(out, ensure_ascii=False, indent=2))
    return "ozet.json yazıldı."


task(
    id="ajan-veri-temizle", category="Ajan", title="Dağınık JSONL verisini temizleyip özetleme", level=3,
    prompt=code("""
        Bu klasördeki `siparisler.jsonl` dosyası dağınık: her satır bir sipariş olmalı ama bazı satırlar bozuk.
        Kurallar:
        - Boş ya da yalnız boşluk içeren satırlar yok sayılır (hatalı sayılmaz).
        - Geçerli kayıt: JSON nesnesidir; id, musteri, tutar, tarih, durum alanlarının hepsi vardır; tutar ve tarih
          aşağıdaki kurallarla çözümlenebilir. Diğer her satır HATALIDIR.
        - Aynı id birden fazla geçerli kayıtta geçiyorsa dosyadaki SON geçerli kayıt kullanılır.
        - tutar sayı ya da metin olabilir. Metinde `₺`, `TL` ve boşluklar atılır; hem `.` hem `,` varsa `.` binlik,
          `,` ondalık ayırıcıdır; yalnız `,` varsa ondalık ayırıcıdır; yalnız `.` varsa ve noktadan sonra tam 3 rakam
          varsa binlik ayırıcı, değilse ondalık ayırıcıdır.
        - tarih biçimleri: `YYYY-MM-DD`, `YYYY/MM/DD`, `GG.AA.YYYY` ya da Türkçe ay adıyla `G Ay YYYY` (ör. `2 Nisan 2025`).
          Gerçek bir takvim tarihi olmalı.
        - durum büyük/küçük harf duyarsızdır (Türkçe: `İPTAL` = `iptal`); musteri adının baş/son boşlukları atılır.
        Sonuçta bu klasöre `ozet.json` yaz (2 ondalığa yuvarlanmış sayılarla):
        `{"gecerli_kayit": tekil geçerli kayıt sayısı, "hatali_satir": hatalı satır sayısı,
          "iptal_sayisi": durumu iptal olan tekil geçerli kayıt sayısı,
          "toplam_tutar": iptal OLMAYAN tekil geçerli kayıtların tutar toplamı,
          "aylik": {"YYYY-AA": o ayın iptal olmayan tutar toplamı, ...},
          "en_cok_harcayan": iptal olmayan kayıtlarda toplam tutarı en yüksek müşteri}`
    """) + "\n" + AGENT_NOTE,
    setup=_setup({"siparisler.jsonl": "\n".join(ORDERS_RAW) + "\n"}),
    grade=lambda d, a, t: grade_orders(d, t), reference=ref_orders,
    wrong=lambda d: (write(d / "ozet.json", json.dumps({"gecerli_kayit": 15, "hatali_satir": 5, "iptal_sayisi": 3,
                                                         "toplam_tutar": 20653.68, "aylik": {"2025-03": 3234.5},
                                                         "en_cok_harcayan": "Elif"})), "")[-1],
)

# ---------------------------------------------------------------- hata izi sürme

TRACE_PARSER = code('''
    """Satış CSV'sindeki alanları çözümler."""
    from datetime import date


    def tutar(metin):
        """Türkçe biçimli tutarı sayıya çevirir: "1.234,56" -> 1234.56, "7.250" -> 7250.0, "7,5" -> 7.5."""
        metin = metin.strip()
        if "," in metin:
            tam, kurus = metin.split(",")
            return float(tam.replace(".", "")) + float(kurus) / 100
        return float(metin)


    def tarih(metin):
        """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
        a, g, y = metin.strip().split(".")
        return date(int(y), int(a), int(g))
''') + "\n"
TRACE_FIXED = code('''
    """Satış CSV'sindeki alanları çözümler."""
    from datetime import date


    def tutar(metin):
        """Türkçe biçimli tutarı sayıya çevirir: "1.234,56" -> 1234.56, "7.250" -> 7250.0, "7,5" -> 7.5."""
        metin = metin.strip()
        if "," in metin:
            tam, kurus = metin.split(",")
            return float(tam.replace(".", "") + "." + kurus)
        return float(metin.replace(".", ""))


    def tarih(metin):
        """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
        g, a, y = metin.strip().split(".")
        return date(int(y), int(a), int(g))
''') + "\n"
TRACE_REPORT = code('''
    from collections import defaultdict

    import ayristir


    def ozet(satirlar):
        """satirlar: (tarih_metni, urun, tutar_metni). Aylık toplamlar ve genel toplam."""
        aylik = defaultdict(float)
        for t, _, tt in satirlar:
            d = ayristir.tarih(t)
            aylik[f"{d.year}-{d.month:02d}"] += ayristir.tutar(tt)
        return dict(sorted(aylik.items())), round(sum(aylik.values()), 2)


    def yaz(satirlar, yol):
        aylik, genel = ozet(satirlar)
        with open(yol, "w", encoding="utf-8") as f:
            for ay, t in aylik.items():
                f.write(f"{ay}: {t:.2f}\\n")
            f.write(f"GENEL: {genel:.2f}\\n")
''') + "\n"
TRACE_MAIN = code('''
    import csv

    import rapor

    with open("veri/satislar.csv", encoding="utf-8") as f:
        satirlar = [(r["tarih"], r["urun"], r["tutar"]) for r in csv.DictReader(f, delimiter=";")]
    rapor.yaz(satirlar, "rapor.txt")
    print("rapor.txt yazıldı")
''') + "\n"
TRACE_ROWS = [("03.01.2026", "Laptop", "32.500"), ("11.01.2026", "Mouse", "450"), ("09.01.2026", "Kablo", "89,90"),
              ("02.02.2026", "Monitör", "7.250,50"), ("12.02.2026", "Kalem", "25"), ("10.03.2026", "Kulaklık", "1.800"),
              ("01.03.2026", "Klavye", "1.199,99"), ("05.03.2026", "Pil", "7,5")]
TRACE_CSV = "tarih;urun;tutar\n" + "".join(f"{a};{b};{c}\n" for a, b, c in TRACE_ROWS)
TRACE_EXPECTED = "2026-01: 33039.90\n2026-02: 7275.50\n2026-03: 3007.49\nGENEL: 43322.89\n"


def grade_trace(d: Path, trace) -> Rubric:
    r = Rubric()
    if reason := _project_danger(d, "ayristir.py", "rapor.py", "main.py"):
        return r.add("güvenlik", 1, 0).gate(reason, 0.0)
    if read(d / "veri/satislar.csv").replace("\r\n", "\n") != TRACE_CSV:
        r.gate("veri dosyası değiştirilmiş", 0.4)
    src = read(d / "ayristir.py")
    items, summary = run_tests("py", {"ayristir.py": src}, "ayristir", [
        (1.5, 'M.tutar("32.500") == 32500 and M.tutar("1.800") == 1800', "virgülsüz binlik ayırıcı"),
        (1, 'M.tutar("7,5") == 7.5 and M.tutar("89,90") == 89.9 and M.tutar(" 0,05 ") == 0.05', "kuruş basamakları"),
        (0.5, 'M.tutar("1.234,56") == 1234.56 and M.tutar("250") == 250.0 and M.tutar("12.345.678,9") == 12345678.9'),
        (1.5, "M.tarih('03.01.2026') == __import__('datetime').date(2026, 1, 3)", "gün/ay sırası"),
        (1, "M.tarih('28.02.2026').month == 2 and M.tarih('31.12.2025').day == 31", "tarih kenar durumları"),
    ])
    r.extend(items)
    r.note(f"hatalar: {summary[:200]}" if summary else "")
    rapor = read(d / "rapor.txt").replace("\r\n", "\n")
    r.add("rapor.txt yeniden üretilmiş ve doğru", 2, rapor.strip() == TRACE_EXPECTED.strip())
    with tempfile.TemporaryDirectory(prefix="gb2_", ignore_cleanup_errors=True) as tmp:
        _copy_tree(d, Path(tmp))
        write(Path(tmp) / "veri/satislar.csv", "tarih;urun;tutar\n05.11.2025;X;1.000,50\n30.11.2025;Y;99,5\n01.12.2025;Z;10\n")
        (Path(tmp) / "rapor.txt").unlink(missing_ok=True)
        _run([sys.executable, "main.py"], Path(tmp), 30)
        other = read(Path(tmp) / "rapor.txt").replace("\r\n", "\n")
    r.add("başka veriyle de doğru (sonuç gömülmemiş)", 1.5, other.strip() == "2025-11: 1100.00\n2025-12: 10.00\nGENEL: 1110.00")
    r.add("kendisi doğruladı", 0.5, trace.verified_after_write())
    return r


def ref_trace(d: Path) -> str:
    write(d / "ayristir.py", TRACE_FIXED)
    write(d / "rapor.txt", TRACE_EXPECTED)
    return "Düzeltildi."


task(
    id="ajan-hata-izi", category="Ajan", title="Hatanın kaynağını bulup düzeltme", level=3,
    prompt=code("""
        Bu klasördeki küçük proje `python main.py` ile `veri/satislar.csv` dosyasından aylık satış raporu (`rapor.txt`)
        üretiyor. Kullanıcı şikâyeti: "Raporda bazı ayların toplamı çok düşük çıkıyor ve satışlar yanlış aylara
        yazılıyor gibi; genel toplam da tutmuyor." Hatanın kaynağını bul ve düzelt (veri dosyasını değiştirme,
        sonuçları elle yazma), sonra `python main.py` ile `rapor.txt`'yi yeniden üret ve doğru olduğunu kontrol et.
    """) + "\n" + AGENT_NOTE,
    setup=_setup({"ayristir.py": TRACE_PARSER, "rapor.py": TRACE_REPORT, "main.py": TRACE_MAIN, "veri/satislar.csv": TRACE_CSV}),
    grade=lambda d, a, t: grade_trace(d, t), reference=ref_trace,
    wrong=lambda d: (ref_trace(d), write(d / "ayristir.py", TRACE_FIXED.replace("g, a, y = metin", "a, g, y = metin")),
                     write(d / "rapor.txt", "2026-01: 33039.90\n"), "")[-1],
)

# ---------------------------------------------------------------- API belgesi

DOC_FILES = {
    "paket/__init__.py": '"""Örnek paket."""\n',
    "paket/metin.py": code('''
        """Metin yardımcıları."""
        import re

        AYIRICI = "-"


        def kisalt(metin: str, uzunluk: int = 20, son: str = "…") -> str:
            """Metni verilen uzunluğa kısaltır.

            Ayrıntılı açıklama.
            """
            return metin if len(metin) <= uzunluk else metin[: uzunluk - len(son)] + son


        def kelime_say(metin):
            """Metindeki kelime sayısını döndürür."""
            return len(_kelimeler(metin))


        def _kelimeler(metin):
            """İç yardımcı."""
            return re.findall(r"\\w+", metin)


        def baslik(metin: str, *, kucuk_kelimeler=("ve", "ile")) -> str:
            """Her kelimenin ilk harfini büyütür (bağlaçlar hariç)."""
            return " ".join(k if k in kucuk_kelimeler else k.capitalize() for k in metin.split())


        class Sablon:
            """Basit metin şablonu."""

            def __init__(self, metin):
                self.metin = metin

            def doldur(self, **degerler) -> str:
                """Şablondaki {ad} alanlarını doldurur."""
                return self.metin.format(**degerler)

            def _ham(self):
                return self.metin
    ''') + "\n",
    "paket/sayi.py": code('''
        """Sayı yardımcıları."""


        def yuvarla(x: float, basamak: int = 2) -> float:
            """Yarımları yukarı yuvarlar."""
            k = 10 ** basamak
            return int(x * k + (0.5 if x >= 0 else -0.5)) / k


        def ortalama(*sayilar, bos=0):
            """Sayıların ortalaması; sayı yoksa bos döner."""
            return sum(sayilar) / len(sayilar) if sayilar else bos


        async def topla_async(a, b):
            """Asenkron toplama."""
            return a + b


        def _gizli():
            pass
    ''') + "\n",
    "paket/_ic.py": code('''
        """İç modül; belgelenmez."""


        def ic_fonksiyon(x):
            """Belgelenmemeli."""
            return x
    ''') + "\n",
}
DOC_EXPECTED = {
    "paket.metin": [("kisalt(metin: str, uzunluk: int = 20, son: str = \"…\") -> str", "Metni verilen uzunluğa kısaltır."),
                    ("kelime_say(metin)", "Metindeki kelime sayısını döndürür."),
                    ("baslik(metin: str, *, kucuk_kelimeler=(\"ve\", \"ile\")) -> str", "Her kelimenin ilk harfini büyütür (bağlaçlar hariç)."),
                    ("class Sablon", "Basit metin şablonu."),
                    ("Sablon.doldur(self, **degerler) -> str", "Şablondaki {ad} alanlarını doldurur.")],
    "paket.sayi": [("yuvarla(x: float, basamak: int = 2) -> float", "Yarımları yukarı yuvarlar."),
                   ("ortalama(*sayilar, bos=0)", "Sayıların ortalaması; sayı yoksa bos döner."),
                   ("async topla_async(a, b)", "Asenkron toplama.")],
}


def _nows(s: str) -> str:
    return re.sub(r"\s+", "", s).replace("'", '"')


def grade_doc(d: Path, trace) -> Rubric:
    r = Rubric()
    f, factor, where = locate(d, "API.md")
    text = read(f) if f else ""
    if not text.strip():
        return r.add("API.md var", 1, 0).gate("API.md yok", 0.0)
    if where:
        r.gate(where, factor)
    lines = text.splitlines()
    found = 0
    for mod in DOC_EXPECTED:
        r.add(f"## {mod} başlığı", 0.75, any(re.match(rf"^##\s+`?{re.escape(mod)}`?\s*$", ln.strip()) for ln in lines))
    for mod, entries in DOC_EXPECTED.items():
        for sig, doc in entries:
            hit = next((ln for ln in lines if _nows(f"`{sig}`") in _nows(ln)), None)
            found += hit is not None
            r.add(f"{sig[:40]}", 1, hit is not None)
            r.add(f"{sig[:25]} açıklaması", 0.5, bool(hit) and _nows(doc) in _nows(hit))
    bad = [n for n in ("_kelimeler", "_ham", "_gizli", "ic_fonksiyon", "paket._ic", "AYIRICI")
           if re.search(rf"(?<![\w.]){re.escape(n)}\b", text)]
    # Uydurma ya da eksik bir belge de iç öğe içermez; bu madde yalnızca belgelenen gerçek öğeler oranında sayılır.
    coverage = found / sum(len(e) for e in DOC_EXPECTED.values())
    r.add("özel/iç öğeler yok", 1.5, max(0.0, 1 - 0.34 * len(bad)) * coverage, ", ".join(bad))
    order_ok = True
    for mod, entries in DOC_EXPECTED.items():
        idx = [next((i for i, ln in enumerate(lines) if _nows(f"`{s}`") in _nows(ln)), -1) for s, _ in entries]
        order_ok &= all(i >= 0 for i in idx) and idx == sorted(idx)
    r.add("tanım sırası korunmuş", 0.5, order_ok)
    return r


def ref_doc(d: Path) -> str:
    out = ["# API", ""]
    for mod, entries in DOC_EXPECTED.items():
        out += [f"## {mod}", ""] + [f"- `{s}` — {doc}" for s, doc in entries] + [""]
    write(d / "API.md", "\n".join(out))
    return "API.md yazıldı."


task(
    id="ajan-api-belgesi", category="Ajan", title="Kaynaktan API belgesi çıkarma", level=2,
    prompt=code("""
        `paket` klasöründeki Python modüllerini oku ve bu klasörde `API.md` dosyası oluştur. Kurallar:
        - Adı `_` ile başlayan modüller (ör. `_ic.py`), fonksiyonlar, sınıflar ve metotlar ile modül düzeyindeki
          sabitler belgelenmez; `__init__` metotları da yazılmaz. `__init__.py` dosyası boşsa atla.
        - Her modül için `## paket.modul_adi` biçiminde bir başlık (ör. `## paket.metin`).
        - Başlığın altında her genel öğe kaynaktaki sırayla bir madde: `` - `imza` — açıklama ``. imza, tanımdaki
          ad ve parametre listesidir (tip ipuçları, varsayılanlar ve dönüş tipi dahil, `def` ve sondaki `:` olmadan;
          ör. `kisalt(metin: str, uzunluk: int = 20, son: str = "…") -> str`). async fonksiyonların imzası `async `
          ile başlar. Sınıflar `class Ad` olarak, genel metotları ise sınıftan hemen sonra `Sinif.metot(self, ...)`
          biçiminde ayrı maddeler olarak yazılır. açıklama, docstring'in yalnızca ilk satırıdır.
    """) + "\n" + AGENT_NOTE,
    setup=_setup(DOC_FILES), grade=lambda d, a, t: grade_doc(d, t), reference=ref_doc,
    wrong=lambda d: (write(d / "API.md", "## paket.metin\n- `kisalt(metin, uzunluk, son)` — Metni kısaltır.\n- `_kelimeler(metin)`\n"), "")[-1],
)
