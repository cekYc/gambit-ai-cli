import unittest
from datetime import date
from kutuphane.modeller import Kitap, Uye, Odunc
from kutuphane.servis import KutuphaneServisi

class TestKutuphane(unittest.TestCase):
    def setUp(self):
        self.servis = KutuphaneServisi()
        # Test verileri
        kitap1 = Kitap(1, "Kitap A", "Yazar X")
        kitap2 = Kitap(2, "Kitap B", "Yazar Y")
        self.servis.kitap_ekle(kitap1)
        self.servis.kitap_ekle(kitap2)
        
        uye_std = Uye(101, "Ali", "standart")
        uye_ogrenci = Uye(102, "Ayşe", "ogrenci")
        self.servis.uye_ekle(uye_std)
        self.servis.uye_ekle(uye_ogrenci)

    def test_odunc_ver_basit(self):
        # Başarılı ödünç verme testi
        tarih = date(2026, 1, 1)
        kayit = self.servis.odunc_ver(1, 101, tarih)
        self.assertEqual(kayit.kitap_id, 1)
        self.assertIsNone(kayit.iade)
        self.assertEqual(kayit.ceza, 0.0)

    def test_odunc_ver_hata_kontrol(self):
        # Kitap/Üye yoksa hata
        with self.assertRaises(ValueError): self.servis.odunc_ver(99, 101, date(2026, 1, 1))
        # Kitap zaten ödünçteyse hata
        self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        with self.assertRaises(ValueError): self.servis.odunc_ver(1, 101, date(2026, 1, 1))

    def test_odunc_satin_sinir_standart(self):
        # Standart (3) sınırını aşma testi
        self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        self.servis.odunc_ver(2, 101, date(2026, 1, 2))
        # Üçüncüsünü verelim
        self.servis.kitap_ekle(Kitap(3, "Kitap C", "Yazar Z"))
        self.servis.odunc_ver(3, 101, date(2026, 1, 3))
        # Dördüncüyü vermeye çalışalım (ValueError bekleniyor)
        with self.assertRaisesRegex(ValueError, "Maksimum ödünç sınırı \(3\) aşıldı."): 
            self.servis.odunc_ver(1, 102, date(2026, 1, 4)) # Öğrenci testi için geçici olarak 102 kullanıldı, 101 ile devam edelim
        
        # Not: Test için 101'in sınırı 3. 1, 2, 3 verildi. Dördüncü deneme hata vermelidir.
        with self.assertRaisesRegex(ValueError, "Maksimum ödünç sınırı \(3\) aşıldı."): 
             self.servis.odunc_ver(1, 101, date(2026, 1, 4))

    def test_odunc_satin_sinir_ogrenci(self):
        # Öğrenci (5) sınırını aşma testi
        self.servis.odunc_ver(1, 102, date(2026, 1, 1))
        self.servis.odunc_ver(2, 102, date(2026, 1, 2))
        self.servis.kitap_ekle(Kitap(3, "Kitap C", "Yazar Z")); self.servis.odunc_ver(3, 102, date(2026, 1, 3))
        self.servis.kitap_ekle(Kitap(4, "Kitap D", "Yazar W")); self.servis.odunc_ver(4, 102, date(2026, 1, 4))
        # Beşinciyi verelim
        self.servis.kitap_ekle(Kitap(5, "Kitap E", "Yazar V")); self.servis.odunc_ver(5, 102, date(2026, 1, 5))
        # Altıncıyı vermeye çalışalım (ValueError bekleniyor)
        with self.assertRaisesRegex(ValueError, "Maksimum ödünç sınırı \(5\) aşıldı."): 
             self.servis.odunc_ver(1, 102, date(2026, 1, 6))

    def test_iade_ve_ceza_hesaplama(self):
        # 1. Normal iade (Ceza 0 TL)
        alinma_tarih = date(2026, 1, 1)
        iade_tarih_normal = date(2026, 1, 15) # 14 gün sonra
        kayit = self.servis.odunc_ver(1, 101, alinma_tarih)
        self.servis.iade_al(1, iade_tarih_normal)
        self.assertEqual(kayit.ceza, 0.0)
        
        # 2. Hafif gecikme (7 gün aşmamış, öğrenci değil) -> 7 gün * 2.5 = 17.5 TL
        alinma_tarih = date(2026, 1, 1)
        iade_tarih_hafif = date(2026, 1, 21) # 20 gün. Gecikme: 6 gün (20-14). 6*2.5=15.0 TL
        kayit_std = self.servis.odunc_ver(2, 101, alinma_tarih)
        self.servis.iade_al(2, iade_tarih_hafif)
        self.assertAlmostEqual(kayit_std.ceza, 15.00)

        # 3. Orta gecikme (7 günü aşmış, öğrenci değil) -> 7*2.5 + (13-7)*5 = 17.5 + 30 = 47.5 TL
        alinma_tarih = date(2026, 1, 1)
        iade_tarih_orta = date(2026, 1, 28) # 27 gün. Gecikme: 13 gün. (7*2.5) + (6*5) = 17.5 + 30 = 47.5 TL
        kayit_std_orta = self.servis.odunc_ver(1, 101, alinma_tarih)
        self.servis.iade_al(1, iade_tarih_orta)
        self.assertAlmostEqual(kayit_std_orta.ceza, 47.50)

        # 4. Maksimum ceza testi (150 TL sınırı)
        # Ceza 150 TL'ye ulaşmak için yaklaşık 52 gün gerekir: 7*2.5 + (G-7)*5 = 150 => 17.5 + 5G - 35 = 150 => 5G = 167.5 => G = 33.5
        # 34 gün gecikme -> (7*2.5) + (27*5) = 17.5 + 135 = 152.5 TL. Sınır 150 TL olmalı.
        alinma_tarih = date(2026, 1, 1)
        iade_tarih_max = date(2026, 1, 35) # 34 gün. Gecikme: 20 gün. (7*2.5) + (13*5) = 17.5 + 65 = 82.5 TL. (Hata kontrolü: 150 TL'ye ulaşmak için gereken gün sayısını kontrol edelim. 150 / 7.5 = 20 gecikme gününe denk geliyor olmalı.)
        # 7+20 = 27 gün. 28. gün iade. Gecikme 14 gün.
        # 7 gün (17.5) + 18 gün (90) = 107.5 TL
        # 7 gün + X gün * 5 TL = 150 - 17.5 = 132.5. X = 132.5 / 5 = 26.
        # Toplam gecikme: 7 + 26 = 33 gün. İade tarihi: 14 + 33 = 47. gün.
        alinma_tarih = date(2026, 1, 1)
        iade_tarih_max = date(2026, 1, 47) # 46 gün gecikme. Gecikme 32 gün. (7*2.5) + (25*5) = 17.5 + 125 = 142.5 TL
        # 48. gün gecikme 34 gün. 17.5 + 27*5 = 152.5 TL. Maksimum 150 TL olmalı.
        kayit_max = self.servis.odunc_ver(1, 101, alinma_tarih)
        self.servis.iade_al(1, date(2026, 1, 48))
        self.assertAlmostEqual(kayit_max.ceza, 150.00)

        # 5. Öğrenci indirimi testi (Maksimum ceza üzerinden test)
        alinma_tarih = date(2026, 1, 1)
        iade_tarih_max_ogrenci = date(2026, 1, 48) # Orijinal ceza 150 TL
        kayit_ogrenci = self.servis.odunc_ver(2, 102, alinma_tarih)
        self.servis.iade_al(2, iade_tarih_max_ogrenci)
        # 150 * 0.5 = 75.0 TL
        self.assertAlmostEqual(kayit_ogrenci.ceza, 75.00)

    def test_toplam_ceza(self):
        # 101 (Standart): 15.00 + 47.50 = 62.50 TL
        self.servis.odunc_ver(1, 101, date(2026, 1, 1)); self.servis.iade_al(1, date(2026, 1, 21)) # 15.00 TL
        self.servis.odunc_ver(2, 101, date(2026, 1, 1)); self.servis.iade_al(2, date(2026, 1, 28)) # 47.50 TL
        self.assertAlmostEqual(self.servis.toplam_ceza(101), 62.50)

        # 102 (Öğrenci): 75.00 TL
        self.servis.odunc_ver(1, 102, date(2026, 1, 1)); self.servis.iade_al(1, date(2026, 1, 48)) # 75.00 TL
        self.assertAlmostEqual(self.servis.toplam_ceza(102), 75.00)
        
    def test_oduncteki_kitaplar(self):
        self.servis.odunc_ver(1, 101, date(2026, 1, 1))
        self.servis.odunc_ver(2, 101, date(2026, 1, 2))
        self.servis.iade_al(1, date(2026, 1, 15))
        
        aktif = self.servis.oduncteki_kitaplar(101)
        self.assertEqual(aktif, [2])

if __name__ == '__main__':
    unittest.main()
