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

    def test_ceza_hesaplama(self):
        s = servis()
        # 14 gün içinde iade -> ceza yok
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 15))
        self.assertEqual(kayit.ceza, 0.0)

        # 1 gün gecikme (15. gün) -> 2.50 TL
        s.odunc_ver(2, 1, date(2026, 1, 1))
        kayit = s.iade_al(2, date(2026, 1, 16))
        self.assertEqual(kayit.ceza, 2.5)

        # 7 gün gecikme -> 7 * 2.5 = 17.50 TL
        s.odunc_ver(3, 1, date(2026, 1, 1))
        kayit = s.iade_al(3, date(2026, 1, 22))
        self.assertEqual(kayit.ceza, 17.5)

        # 8 gün gecikme -> 7*2.5 + 1*5 = 22.50 TL
        s.odunc_ver(4, 1, date(2026, 1, 1))
        kayit = s.iade_al(4, date(2026, 1, 23))
        self.assertEqual(kayit.ceza, 22.5)

        # Çok gecikme -> 150 TL sınırı
        s.odunc_ver(5, 1, date(2026, 1, 1))
        kayit = s.iade_al(5, date(2026, 7, 1))
        self.assertEqual(kayit.ceza, 150.0)

    def test_ogrenci_indirimi(self):
        s = servis()
        # Öğrenci 10 gün gecikme -> normalde 7*2.5 + 3*5 = 32.50, indirimli 16.25
        s.odunc_ver(1, 2, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 25))
        self.assertEqual(kayit.ceza, 16.25)

        # Öğrenci çok gecikme -> 150 TL sınırı sonra %50 = 75.0
        s.odunc_ver(2, 2, date(2026, 1, 1))
        kayit = s.iade_al(2, date(2026, 7, 1))
        self.assertEqual(kayit.ceza, 75.0)

    def test_toplam_ceza(self):
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 16))  # 2.50
        s.odunc_ver(2, 1, date(2026, 2, 1))
        s.iade_al(2, date(2026, 2, 16))  # 2.50
        self.assertEqual(s.toplam_ceza(1), 5.0)

    def test_odunc_limiti_standart(self):
        s = servis()
        # Standart üye max 3 kitap
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 1))

    def test_odunc_limiti_ogrenci(self):
        s = servis()
        # Öğrenci max 5 kitap
        s.odunc_ver(1, 2, date(2026, 1, 1))
        s.odunc_ver(2, 2, date(2026, 1, 1))
        s.odunc_ver(3, 2, date(2026, 1, 1))
        s.odunc_ver(4, 2, date(2026, 1, 1))
        s.odunc_ver(5, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 1))


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
