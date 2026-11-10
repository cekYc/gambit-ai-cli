from datetime import date
from kutuphane.modeller import Kitap, Uye, Odunc
from kutuphane.servis import KutuphaneServisi
import unittest

class TestKutuphane(unittest.TestCase):

    def setUp(self):
        self.servis = KutuphaneServisi()
        self.kitap1 = Kitap(1, "Sefiller", "Victor Hugo")
        self.kitap2 = Kitap(2, "1984", "George Orwell")
        self.uye_std = Uye(101, "Ayşe", "standart")
        self.uye_ogrenci = Uye(102, "Can", "ogrenci")
        
        self.servis.kitap_ekle(self.kitap1)
        self.servis.kitap_ekle(self.kitap2)
        self.servis.uye_ekle(self.uye_std)
        self.servis.uye_ekle(self.uye_ogrenci)

    # Mevcut fonksiyonların temel testleri (varsayımsal)
    def test_odunc_ver_basarili(self):
        odunc = self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        self.assertIsNotNone(odunc)
        self.assertEqual(len(self.servis.oduncteki_kitaplar(101)), 1)

    def test_odunc_ver_kitap_bulunamadi(self):
        with self.assertRaises(ValueError):
            self.servis.odunc_ver(99, 101, date(2026, 1, 1))

    # Yeni Özellik 2 ve 3 Testleri: Ceza Hesaplama
    def test_ceza_hesaplama_normal(self):
        # 14 gün + 15 gün gecikme (15 gün = 7*2.5 + 8*5) -> 17.5 + 40 = 57.5 TL
        odunc = self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        iade_tarihi = date(2026, 1, 16) # 15 gün gecikme
        self.servis.iade_al(1, iade_tarihi)
        kayit = next(k for k in self.servis.kayitlar if k.kitap_id == 1)
        self.assertAlmostEqual(kayit.ceza, 57.50, 2)

    def test_ceza_hesaplama_maksimum(self):
        # 150 TL sınırını test etmeli
        odunc = self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        # 150 TL ceza için yeterli gecikme
        iade_tarihi = date(2026, 2, 20) 
        self.servis.iade_al(1, iade_tarihi)
        kayit = next(k for k in self.servis.kayitlar if k.kitap_id == 1)
        self.assertEqual(kayit.ceza, 150.00)

    def test_ceza_hesaplama_ogrenci_indirimli(self):
        # Normal ceza 57.50 TL iken, öğrenci %50 indirimli olmalı (28.75 TL)
        odunc = self.servis.odunc_ver(1, 102, date(2026, 1, 1))
        iade_tarihi = date(2026, 1, 16) # 15 gün gecikme
        self.servis.iade_al(1, iade_tarihi)
        kayit = next(k for k in self.servis.kayitlar if k.kitap_id == 1)
        self.assertAlmostEqual(kayit.ceza, 28.75, 2)

    def test_toplam_ceza(self):
        # Ayşe (101) için ceza kaydı 57.50 TL
        odunc1 = self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        self.servis.iade_al(1, date(2026, 1, 16))
        
        # İkinci bir ceza kaydı (Örnek: 100 TL - maksimuma yakın bir değer)
        odunc2 = self.servis.odunc_ver(2, 101, date(2026, 1, 1))
        # Maksimum ceza 150 TL olduğu için, ikinci kayıt 100 TL varsayalım
        # Not: Gerçek test için 150 TL'yi kullanmalıyız, ama basitlik için bunu bırakıyorum.
        self.servis.iade_al(2, date(2026, 2, 20))

        # Beklenen toplam: 57.50 + 150.00 = 207.50 TL
        self.assertAlmostEqual(self.servis.toplam_ceza(101), 207.50, 2)

    # Yeni Özellik 4 Testleri: Kitap Sınırı
    def test_kitap_siniri_standart(self):
        # Standart üye 3 kitap sınırı var
        for i in range(3): 
            self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        
        with self.assertRaisesRegex(ValueError, "maksimum 3 kitap ödünç alınabilir"):
            self.servis.odunc_ver(2, 101, date(2026, 1, 1))

    def test_kitap_siniri_ogrenci(self):
        # Öğrenci üye 5 kitap sınırı var
        for i in range(5): 
            self.servis.odunc_ver(1, 102, date(2026, 1, 1))
        
        with self.assertRaisesRegex(ValueError, "maksimum 5 kitap ödünç alınabilir"):
            self.servis.odunc_ver(2, 102, date(2026, 1, 1))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)