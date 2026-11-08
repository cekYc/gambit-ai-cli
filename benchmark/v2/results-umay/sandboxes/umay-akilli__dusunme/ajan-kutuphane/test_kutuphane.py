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

    def test_ceza_yok_14_gun_icinde(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 14))  # 13 gün fark
        self.assertEqual(kayit.ceza, 0.0)
        s.odunc_ver(2, 1, date(2026, 1, 1))
        kayit = s.iade_al(2, date(2026, 1, 15))  # 14 gün fark
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_ilk_7_gun_gecikme(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # 15. gün = 1 gün gecikme -> 2.50 TL
        kayit = s.iade_al(1, date(2026, 1, 16))
        self.assertEqual(kayit.ceza, 2.50)
        # 21. gün = 7 gün gecikme -> 7 * 2.5 = 17.50 TL
        s.odunc_ver(2, 1, date(2026, 1, 1))
        kayit = s.iade_al(2, date(2026, 1, 22))
        self.assertEqual(kayit.ceza, 17.50)

    def test_ceza_7_gun_sonra_5_tl(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # 22. gün = 8 gün gecikme -> 7*2.5 + 1*5 = 22.50
        kayit = s.iade_al(1, date(2026, 1, 23))
        self.assertEqual(kayit.ceza, 22.50)

    def test_ceza_max_150_tl(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # Çok uzun gecikme -> max 150 TL
        kayit = s.iade_al(1, date(2026, 6, 1))
        self.assertEqual(kayit.ceza, 150.0)

    def test_ogrenci_ceza_50_indirim(self):
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))  # Can öğrenci
        # 22. gün = 8 gün gecikme -> normal 22.50, öğrenci 11.25
        kayit = s.iade_al(1, date(2026, 1, 23))
        self.assertEqual(kayit.ceza, 11.25)
        # Max ceza da öğrencide 75 TL
        s.odunc_ver(2, 2, date(2026, 1, 1))
        kayit = s.iade_al(2, date(2026, 6, 1))
        self.assertEqual(kayit.ceza, 75.0)

    def test_standart_uye_kitap_siniri_3(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 1))

    def test_ogrenci_uye_kitap_siniri_5(self):
        s = servis()
        for i in range(1, 6):
            s.odunc_ver(i, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 1))

    def test_toplam_ceza(self):
        s = servis()
        # Ayşe (standart) - 2 kitap iade, cezalar: 2.50 + 17.50 = 20.00
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 16))  # 2.50
        s.iade_al(2, date(2026, 1, 22))  # 17.50
        self.assertEqual(s.toplam_ceza(1), 20.00)
        # Can (ogrenci) - 1 kitap iade, ceza: 11.25
        s.odunc_ver(3, 2, date(2026, 1, 1))
        s.iade_al(3, date(2026, 1, 23))  # 11.25
        self.assertEqual(s.toplam_ceza(2), 11.25)
        # İade edilmemiş kitaplar dahil edilmez
        s.odunc_ver(4, 1, date(2026, 1, 1))
        self.assertEqual(s.toplam_ceza(1), 20.00)


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
