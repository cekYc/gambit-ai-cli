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

    def test_ceza_yok(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 15))  # tam 14 gün, gecikme yok
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_hesaplama(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 16))  # 1 gün gecikme
        self.assertEqual(kayit.ceza, 2.50)

    def test_ceza_ilk_7_gun(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 21))  # 6 gün gecikme
        self.assertEqual(kayit.ceza, 15.00)

    def test_ceza_sonraki_gunler(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 23))  # 8 gün gecikme: 7*2.5 + 1*5
        self.assertEqual(kayit.ceza, 22.50)

    def test_ceza_ust_sinir(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 2, 18))  # 34 gün gecikme -> 150 TL üst sınır
        self.assertEqual(kayit.ceza, 150.0)

    def test_ogrenci_ceza_indirimi(self):
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))  # Can ogrenci
        kayit = s.iade_al(1, date(2026, 2, 18))  # 34 gün gecikme -> 150 -> %50 = 75
        self.assertEqual(kayit.ceza, 75.0)

    def test_toplam_ceza(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 16))  # 2.50
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.iade_al(2, date(2026, 1, 21))  # 15.00
        self.assertEqual(s.toplam_ceza(1), 17.50)

    def test_odunc_siniri_standart(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 1))

    def test_odunc_siniri_ogrenci(self):
        s = servis()
        for i in range(1, 6):
            s.odunc_ver(i, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 1))


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
