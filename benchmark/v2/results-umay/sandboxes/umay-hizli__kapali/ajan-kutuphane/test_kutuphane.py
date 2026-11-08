import unittest
from datetime import date

from kutuphane import Kitap, KutuphaneServisi, Odunc, Uye


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
        kayit = s.iade_al(1, date(2026, 1, 14))
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_14_gun_sinir(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # 15 gün sonra = 1 geciken gün
        kayit = s.iade_al(1, date(2026, 1, 15))
        self.assertEqual(kayit.ceza, 2.50)

    def test_ceza_ilk_7_gun(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # 21 gün sonra = 7 geciken gün -> 7 * 2.50 = 17.50
        kayit = s.iade_al(1, date(2026, 1, 22))
        self.assertEqual(kayit.ceza, 17.50)

    def test_ceza_sonraki_gunler(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # 22 gün sonra = 8 geciken gün -> 7*2.50 + 1*5.00 = 22.50
        kayit = s.iade_al(1, date(2026, 1, 23))
        self.assertEqual(kayit.ceza, 22.50)

    def test_ceza_sinir_150(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # Çok gecikme: 150 TL üst sınırı
        kayit = s.iade_al(1, date(2026, 2, 1))
        self.assertEqual(kayit.ceza, 150.0)

    def test_ogrenci_ceza_indirimi(self):
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))
        # 22 gün sonra = 8 geciken gün -> 22.50 TL, ogrenci %50 indirimli -> 11.25 TL
        kayit = s.iade_al(1, date(2026, 1, 23))
        self.assertEqual(kayit.ceza, 11.25)

    def test_toplam_ceza(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 23))  # 22.50 TL
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.iade_al(2, date(2026, 1, 23))  # 22.50 TL
        self.assertEqual(s.toplam_ceza(1), 45.00)

    def test_odunc_siniri_standart(self):
        s = servis()
        for kitap_id in range(1, 4):
            s.odunc_ver(kitap_id, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 1))

    def test_odunc_siniri_ogrenci(self):
        s = servis()
        for kitap_id in range(1, 6):
            s.odunc_ver(kitap_id, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 1))

    def test_odunc_siniri_ogrenci_bosaltinca(self):
        s = servis()
        for kitap_id in range(1, 6):
            s.odunc_ver(kitap_id, 2, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 2))
        # İade sonrası tekrar ödünç alınabilmeli
        s.odunc_ver(6, 2, date(2026, 1, 3))


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")