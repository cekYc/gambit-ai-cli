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

    def test_ceza_guncel_gecikme(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 20))  # 19 gün, 5 gün gecikme
        self.assertEqual(kayit.ceza, 12.50)

    def test_ceza_ilk_7_sonra(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 23))  # 22 gün, 8 gün gecikme -> 7*2.50 + 1*5.00 = 22.50
        self.assertEqual(kayit.ceza, 22.50)

    def test_ceza_maksimum_sinir(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 6, 1))  # çok büyük gecikme, sınır 150 TL
        self.assertEqual(kayit.ceza, 150.0)

    def test_ceza_ogrenci_indirimi(self):
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))  # üye 2 öğrenci
        kayit = s.iade_al(1, date(2026, 1, 23))  # 22 gün, 8 gün gecikme -> 22.50 TL, %50 indirim = 11.25
        self.assertEqual(kayit.ceza, 11.25)

    def test_toplam_ceza(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 20))  # 12.50 TL
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.iade_al(2, date(2026, 1, 23))  # 22.50 TL
        self.assertEqual(s.toplam_ceza(1), 35.0)

    def test_odunc_limiti_standart(self):
        s = servis()
        for kitap_id in range(1, 4):
            s.odunc_ver(kitap_id, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 1))

    def test_odunc_limiti_ogrenci(self):
        s = servis()
        for kitap_id in range(1, 6):
            s.odunc_ver(kitap_id, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 1))


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
