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

    def test_ceza_hesaplama_yok(self):
        """14 gün içinde iade - ceza 0"""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 15))  # 14 gün
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_ilk_7_gun(self):
        """15-21 gün arası: günlük 2.50 TL"""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 16))  # 15 gün = 1 gecikme
        self.assertEqual(kayit.ceza, 2.5)
        s2 = servis()
        s2.odunc_ver(2, 1, date(2026, 1, 1))
        kayit2 = s2.iade_al(2, date(2026, 1, 22))  # 21 gün = 7 gecikme
        self.assertEqual(kayit2.ceza, 17.5)  # 7 * 2.5

    def test_ceza_7_sonra(self):
        """22+ gün: ilk 7 gün 2.5, sonrası 5.0 TL"""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 23))  # 22 gün = 8 gecikme
        self.assertEqual(kayit.ceza, 22.5)  # 7*2.5 + 1*5 = 17.5 + 5
        s2 = servis()
        s2.odunc_ver(2, 1, date(2026, 1, 1))
        kayit2 = s2.iade_al(2, date(2026, 2, 1))  # 31 gün = 17 gecikme
        self.assertEqual(kayit2.ceza, 67.5)  # 7*2.5 + 10*5 = 17.5 + 50

    def test_ceza_maksimum_150(self):
        """Ceza en fazla 150 TL"""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 6, 1))  # çok uzun süre
        self.assertEqual(kayit.ceza, 150.0)

    def test_ogrenci_indirimi(self):
        """Öğrenci üyelerde %50 indirim (150 sınırından sonra)"""
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))  # öğrenci
        kayit = s.iade_al(1, date(2026, 6, 1))
        self.assertEqual(kayit.ceza, 75.0)  # 150 * 0.5
        s2 = servis()
        s2.odunc_ver(2, 2, date(2026, 1, 1))
        kayit2 = s2.iade_al(2, date(2026, 1, 23))  # 22 gün = 8 gecikme
        self.assertEqual(kayit2.ceza, 11.25)  # 22.5 * 0.5

    def test_toplam_ceza(self):
        """Üyenin iade edilmiş ödünçlerin cezaları toplamı"""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 16))  # 2.5
        s.odunc_ver(2, 1, date(2026, 2, 1))
        s.iade_al(2, date(2026, 2, 23))  # 22.5
        # kitap 3 hala ödünçte
        s.odunc_ver(3, 1, date(2026, 3, 1))
        self.assertEqual(s.toplam_ceza(1), 25.0)

    def test_odunc_limiti_standart(self):
        """Standart üye max 3 kitap"""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 1))

    def test_odunc_limiti_ogrenci(self):
        """Öğrenci üye max 5 kitap"""
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))
        s.odunc_ver(2, 2, date(2026, 1, 1))
        s.odunc_ver(3, 2, date(2026, 1, 1))
        s.odunc_ver(4, 2, date(2026, 1, 1))
        s.odunc_ver(5, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 1))

    def test_iade_sonrasi_yeni_odunc(self):
        """İade edilen kitap limit sayılmamalı"""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 5))
        # artık 2 aktif, 3. kitap alınabilir
        s.odunc_ver(4, 1, date(2026, 1, 6))
        self.assertEqual(len(s.oduncteki_kitaplar(1)), 3)


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")