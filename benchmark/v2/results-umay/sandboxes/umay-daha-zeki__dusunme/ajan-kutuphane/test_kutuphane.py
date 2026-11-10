import unittest
from datetime import date
from kutuphane import Kitap, KutuphaneServisi, Uye


def servis():
    s = KutuphaneServisi()
    # Kitaplar
    for i in range(1, 8):
        s.kitap_ekle(Kitap(i, f"Kitap {i}", "Yazar"))
    # Üyeler
    s.uye_ekle(Uye(1, "Ayşe", "standart"))
    s.uye_ekle(Uye(2, "Can", "ogrenci"))
    s.uye_ekle(Uye(3, "Deniz", "standart"))
    return s


class KutuphaneTest(unittest.TestCase):
    # Mevcut Testler
    def test_odunc_ve_iade(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        self.assertEqual(s.oduncteki_kitaplar(1), [1])
        # 4 gün gecikme (14 gün grace + 4 gün = 18. 18-14=4 gecikme günü)
        kayit = s.iade_al(1, date(2026, 1, 5))
        self.assertEqual(kayit.iade, date(2026, 1, 5))
        self.assertEqual(s.oduncteki_kitaplar(1), [])

    def test_cift_odunc(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # Aynı kitap iki farklı üyeye verilemez
        with self.assertRaises(ValueError):
            s.odunc_ver(1, 2, date(2026, 1, 2))

    # Yeni Testler - Üye Sınırı
    def test_odunc_siniri_ogrenci(self):
        s = servis()
        # Öğrenci (2) için max 5 kitap
        for i in range(1, 7):
            with self.assertRaises(ValueError):
                s.odunc_ver(i, 2, date(2026, 1, 1))
        # 5. kitap başarılı olmalı
        s.odunc_ver(1, 2, date(2026, 1, 1))
        s.odunc_ver(2, 2, date(2026, 1, 1))
        s.odunc_ver(3, 2, date(2026, 1, 1))
        s.odunc_ver(4, 2, date(2026, 1, 1))
        s.odunc_ver(5, 2, date(2026, 1, 1))
        self.assertEqual(len(s.oduncteki_kitaplar(2)), 5)

    def test_odunc_siniri_standart(self):
        s = servis()
        # Standart (1) için max 3 kitap
        for i in range(1, 5):
            with self.assertRaises(ValueError):
                s.odunc_ver(i, 1, date(2026, 1, 1))
        # 3. kitap başarılı olmalı
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        self.assertEqual(len(s.oduncteki_kitaplar(1)), 3)

    # Yeni Testler - Ceza Hesaplama
    def test_ceza_gecikmesiz(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # 14 gün içinde iade (15. gün iade)
        s.iade_al(1, date(2026, 1, 15))
        kayit = next(k for k in s.kayitlar if k.kitap_id == 1)
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_kis_gunler(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # 14+7=21 gün sonra iade (22. gün iade)
        # İlk 7 gün (7*2.5=17.5) + 1 gün (5.0) = 22.5 TL
        s.iade_al(1, date(2026, 1, 22))
        kayit = next(k for k in s.kayitlar if k.kitap_id == 1)
        self.assertAlmostEqual(kayit.ceza, 22.50)

    def test_ceza_max_limit(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # Ceza 150 TL'yi aşacak kadar gecikme (Örn: 7 gün * 2.5 + X gün * 5 > 150)
        # 17.5 + 5X = 150 -> 5X = 132.5 -> X = 26.5
        # Toplam gecikme: 7 + 27 = 34 gün. Toplam gün: 14+34 = 48.
        # İade tarihi: 2026, 1, 1 + 48 gün = 2026, 2, 18
        s.iade_al(1, date(2026, 2, 18))
        kayit = next(k for k in s.kayitlar if k.kitap_id == 1)
        self.assertEqual(kayit.ceza, 150.00)

    def test_ceza_ogrenci_indirimi(self):
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))
        # Normal ceza 22.5 TL idi. Öğrenci indirimi %50.
        s.iade_al(1, date(2026, 1, 22))
        kayit = next(k for k in s.kayitlar if k.kitap_id == 1)
        self.assertAlmostEqual(kayit.ceza, 11.25)

    # Yeni Testler - Toplam Ceza
    def test_toplam_ceza(self):
        s = servis()
        # Üye 1 (Standart)
        s.odunc_ver(1, 1, date(2026, 1, 1)); s.iade_al(1, date(2026, 1, 22)) # Ceza: 22.50 TL
        s.odunc_ver(2, 1, date(2026, 1, 1)); s.iade_al(2, date(2026, 2, 18)) # Ceza: 150.00 TL
        self.assertAlmostEqual(s.toplam_ceza(1), 172.50)
        # Üye 2 (Öğrenci)
        s.odunc_ver(3, 2, date(2026, 1, 1)); s.iade_al(3, date(2026, 1, 22)) # Ceza: 11.25 TL
        self.assertAlmostEqual(s.toplam_ceza(2), 11.25)

if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
