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

    # --- Yeni özellik testleri ---

    def test_ceza_yok_14_gun_icinde(self):
        """14 gün içinde iade edilirse ceza 0."""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 15))  # 14 gün
        self.assertEqual(kayit.ceza, 0.0)

    def test_ceza_ilk_7_gun_gecikme(self):
        """14 günün üzerindeki ilk 7 gün: günlük 2.50 TL."""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 20))  # 19 gün = 5 gün gecikme
        self.assertEqual(kayit.ceza, 12.50)  # 5 * 2.5

    def test_ceza_7_gunden_fazla_gecikme(self):
        """İlk 7 gün 2.50, sonrası 5.00 TL."""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 1, 28))  # 27 gün = 13 gün gecikme
        # 7 * 2.5 + 6 * 5 = 17.5 + 30 = 47.5
        self.assertEqual(kayit.ceza, 47.50)

    def test_ceza_max_150_tl(self):
        """Ceza en fazla 150 TL."""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        # Çok uzun süre: 100 gün = 86 gün gecikme
        # 7 * 2.5 + 79 * 5 = 17.5 + 395 = 412.5 -> 150'e kesilmeli
        kayit = s.iade_al(1, date(2026, 4, 10))
        self.assertEqual(kayit.ceza, 150.0)

    def test_ceza_ogrenci_indirim(self):
        """Öğrenci üye %50 indirim alır (150 TL sınırı sonrası)."""
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))  # Can öğrenci
        kayit = s.iade_al(1, date(2026, 1, 28))  # 27 gün = 13 gün gecikme
        # Normal: 47.50, Öğrenci: 23.75
        self.assertEqual(kayit.ceza, 23.75)

    def test_ceza_ogrenci_max_sinir(self):
        """Öğrenci için max 150 TL sınırından sonra %50 = 75 TL."""
        s = servis()
        s.odunc_ver(1, 2, date(2026, 1, 1))
        kayit = s.iade_al(1, date(2026, 4, 10))  # Çok uzun süre
        self.assertEqual(kayit.ceza, 75.0)

    def test_toplam_ceza(self):
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamı."""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 20))  # 12.50
        s.odunc_ver(2, 1, date(2026, 2, 1))
        s.iade_al(2, date(2026, 2, 20))  # 12.50
        # 3. kitap iade edilmemiş
        s.odunc_ver(3, 1, date(2026, 3, 1))
        self.assertEqual(s.toplam_ceza(1), 25.0)

    def test_odunc_limiti_standart(self):
        """Standart üye en fazla 3 kitap alabilir."""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(4, 1, date(2026, 1, 1))

    def test_odunc_limiti_ogrenci(self):
        """Öğrenci üye en fazla 5 kitap alabilir."""
        s = servis()
        for i in range(1, 6):
            s.odunc_ver(i, 2, date(2026, 1, 1))
        with self.assertRaises(ValueError):
            s.odunc_ver(6, 2, date(2026, 1, 1))

    def test_iade_sonra_yeni_odunc(self):
        """İade edilen kitap limiti boşaltır."""
        s = servis()
        s.odunc_ver(1, 1, date(2026, 1, 1))
        s.odunc_ver(2, 1, date(2026, 1, 1))
        s.odunc_ver(3, 1, date(2026, 1, 1))
        s.iade_al(1, date(2026, 1, 10))
        # Artık 4. kitap alınabilir
        s.odunc_ver(4, 1, date(2026, 1, 11))
        self.assertEqual(len(s.oduncteki_kitaplar(1)), 3)


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")