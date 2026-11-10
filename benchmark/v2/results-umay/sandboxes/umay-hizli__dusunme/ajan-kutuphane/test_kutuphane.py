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

    def test_odunc_siniri_standart(self):
        s = servis()
        for kitap_id in range(1, 4):
            s.odunc_ver(kitap_id, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 2))

    def test_odunc_siniri_ogrenci(self):
        s = servis()
        for kitap_id in range(1, 6):
            s.odunc_ver(kitap_id, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 2))

    def test_ceza_yok_14_gun_icinde(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 15))  # 14 gün, cezasız
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_hesaplama(self):
        s = servis()
        # 15 gün = 1 gün gecikme -> 2.50 TL
        s.odunc_ver(1, 1, date(2026, 1, 1))
        k = s.iade_al(1, date(2026, 1, 16))
        self.assertEqual(k.ceza, 2.50)
        # 21 gün = 7 gün gecikme -> 7 * 2.50 = 17.50 TL
        s.odunc_ver(2, 1, date(2026, 1, 1))
        k = s.iade_al(2, date(2026, 1, 22))
        self.assertEqual(k.ceza, 17.50)
        # 22 gün = 8 gün gecikme -> 17.50 + 5.00 = 22.50 TL
        s.odunc_ver(3, 1, date(2026, 1, 1))
        k = s.iade_al(3, date(2026, 1, 23))
        self.assertEqual(k.ceza, 22.50)
        # 50 gün = 36 gün gecikme -> 17.50 + 29*5 = 162.50 -> 150 TL kısıtı
        s.odunc_ver(4, 1, date(2026, 1, 1))
        k = s.iade_al(4, date(2026, 2, 20))
        self.assertEqual(k.ceza, 150.0)
        # Öğrenci: 150 TL kısıtı uygulandıktan sonra %50 indirim -> 75.00 TL
        s.odunc_ver(5, 2, date(2026, 1, 1))
        k = s.iade_al(5, date(2026, 2, 20))
        self.assertEqual(k.ceza, 75.0)

    def test_toplam_ceza(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 16))  # 2.50 TL
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.iade_al(2, date(2026, 1, 22))  # 17.50 TL
        self.assertEqual(s.toplam_ceza(1), 20.0)
        self.assertEqual(s.toplam_ceza(2), 0.0)
        # İade edilmemiş kayıt sayılmamalı
        s.odunc_ver(3, 1, date(2026, 1, 1))
        self.assertEqual(s.toplam_ceza(1), 20.0)


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
