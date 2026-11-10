import unittest
from datetime import date

from kutuphane import Kitap, KutuphaneServisi, Uye

def servis():
    s = KutuphaneServisi()
    for i in range(1, 8):
        s.kitap_ekle(Kitap(i, f"Kitap {i}", "Yazar"))
    s.uye_ekle(Uye(1, "Ayşe", "standart"))
    s.uye_ekle(Uye(2, "Can", "ogrenci"))
    return s


class KutuphaneTest(unittest.TestCase):
    # Mevcut Testler
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

    # Yeni Özellik Testleri (Ceza ve Sınır)
    def test_kitap_siniri_kontrolu(self):
        s = servis()
        # Öğrenci (Sınır 5): 5 kitap ver
        s.odunc_ver(1, 2, date(2026, 1, 1))
        s.odunc_ver(2, 2, date(2026, 1, 2))
        s.odunc_ver(3, 2, date(2026, 1, 3))
        s.odunc_ver(4, 2, date(2026, 1, 4))
        s.odunc_ver(5, 2, date(2026, 1, 5))
        self.assertEqual(len(s.oduncteki_kitaplar(2)), 5)
        
        # Sınır aşıldı (6. kitap): ValueError fırlatılmalı
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 6))

        # Standart üye (Sınır 3): 3 kitap ver
        s_std = servis()
        s_std.odunc_ver(1, 1, date(2026, 1, 1))
        s_std.odunc_ver(2, 1, date(2026, 1, 2))
        s_std.odunc_ver(3, 1, date(2026, 1, 3))
        
        # Sınır aşıldı (4. kitap): ValueError fırlatılmalı
        with self.assertRaises(ValueError):
            s_std.odunc_ver(4, 1, date(2026, 1, 4))

    def test_ceza_hesaplama_normal(self):
        s = servis()
        # 2026/1/1 - 2026/1/29. Gün farkı = 28. Gecikme = 14. (7*2.5 + 7*5) = 52.5
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 29))
        kayit = next(k for k in s.kayitlar if k.kitap_id == 1)
        self.assertAlmostEqual(kayit.ceza, 52.50, 2)

    def test_ceza_hesaplama_max_limit(self):
        s = servis()
        # Çok fazla gecikme, ceza 150 TL olmalı (34+ gün gecikme)
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 2, 5)) 
        kayit = next(k for k in s.kayitlar if k.kitap_id == 1)
        self.assertAlmostEqual(kayit.ceza, 150.00, 2)

    def test_ceza_hesaplama_ogrenci_indirim(self):
        s = servis()
        # 52.5 TL ceza hesaplandı, öğrenci indirimi (%50): 26.25 TL
        s.odunc_ver(1, 2, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 29))
        kayit = next(k for k in s.kayitlar if k.kitap_id == 1)
        self.assertAlmostEqual(kayit.ceza, 26.25, 2)

    def test_toplam_ceza(self):
        s = servis()
        # Üye 1 (Standart): 52.5 TL ceza
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 29))
        # Üye 2 (Öğrenci): 26.25 TL ceza
        s.odunc_ver(2, 2, date(2026, 1, 1))
        s.iade_al(2, date(2026, 1, 29))
        
        # Toplam: 52.5 + 26.25 = 78.75 TL
        self.assertAlmostEqual(s.toplam_ceza(1), 52.50, 2)
        self.assertAlmostEqual(s.toplam_ceza(2), 26.25, 2)
        self.assertAlmostEqual(s.toplam_ceza(1) + s.toplam_ceza(2), 78.75, 2)


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
    else:
        print("TESTLER BAŞARISIZ")