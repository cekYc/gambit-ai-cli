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


class KutuphaneCezaTest(unittest.TestCase):
    def setUp(self):
        self.s = servis()

    def test_ceza_yok_14_gun_ici(self):
        s = self.s
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 14))
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_yok_tam_14_gun(self):
        s = self.s
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 15))
        self.assertEqual(kayit.ceza, 0.0)

    def test_ilk_7_gecikme_gunu(self):
        s = self.s
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 20))  # 5 gun gecikme -> 5 * 2.50 = 12.50
        self.assertEqual(kayit.ceza, 12.50)

    def test_gecikme_ust_sinir(self):
        s = self.s
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 2, 1))  # 17 gun gecikme -> 17.50 + 50 = 67.50
        self.assertEqual(kayit.ceza, 67.50)

    def test_ceza_maksimum_150(self):
        s = self.s
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 6, 1))  # cok gecikme -> sinir 150
        self.assertEqual(kayit.ceza, 150.0)

    def test_ogrenci_yuzde_50_indirim(self):
        s = self.s
        s.odunc_ver(1, 2, date(2026, 1, 1))  # ogrenci uye
        kayit = s.iade_al(1, date(2026, 1, 20))  # 12.50 * %50 = 6.25
        self.assertEqual(kayit.ceza, 6.25)

    def test_toplam_ceza(self):
        s = self.s
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 20))  # 12.50
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.iade_al(2, date(2026, 1, 20))  # 12.50
        self.assertEqual(s.toplam_ceza(1), 25.00)

    def test_sinir_standart_3(self):
        s = self.s
        for kitap in (1, 2, 3):
            s.odunc_ver(kitap, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 2))

    def test_sinir_ogrenci_5(self):
        s = self.s
        for kitap in range(1, 6):
            s.odunc_ver(kitap, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 2))


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
