import unittest
from datetime import date
from kutuphane.modeller import Kitap, Uye, Odunc
from kutuphane.servis import KutuphaneServisi

class TestKutuphane(unittest.TestCase):
    def setUp(self):
        self.servis = KutuphaneServisi()
        # Kitaplar
        k1 = Kitap(id=1, ad="Sefiller", yazar="Victor Hugo")
        k2 = Kitap(id=2, ad="1984", yazar="George Orwell")
        self.servis.kitap_ekle(k1)
        self.servis.kitap_ekle(k2)
        # Üyeler
        u_std = Uye(id=101, ad="Ali", tur="standart")
        u_ogrenci = Uye(id=201, ad="Ayşe", tur="ogrenci")
        self.servis.uye_ekle(u_std)
        self.servis.uye_ekle(u_ogrenci)

    def test_temel_odunc_verme(self):
        tarih = date(2026, 10, 1)
        kayit = self.servis.odunc_ver(1, 101, tarih)
        self.assertEqual(kayit.kitap_id, 1)
        self.assertIsNone(kayit.iade)

    def test_kitap_zaten_oduncte(self):
        tarih = date(2026, 10, 1)
        self.servis.odunc_ver(1, 101, tarih)
        with self.assertRaisesRegex(ValueError, "kitap zaten ödünçte"):
            self.servis.odunc_ver(1, 101, tarih)

    def test_iade_alma(self):
        tarih_alinma = date(2026, 10, 1)
        tarih_iade = date(2026, 10, 15)
        self.servis.odunc_ver(2, 101, tarih_alinma)
        kayit = self.servis.iade_al(2, tarih_iade)
        self.assertEqual(kayit.iade, tarih_iade)

    def test_ceza_hesaplama_normal(self):
        # 15 gün gecikme (14+1). Gecikme 1 gün. Ceza = 1 * 2.50 = 2.50 TL
        tarih_alinma = date(2026, 10, 1)
        tarih_iade = date(2026, 10, 15) 
        self.servis.odunc_ver(2, 101, tarih_alinma)
        kayit = self.servis.iade_al(2, tarih_iade)
        self.assertAlmostEqual(kayit.ceza, 2.50)

    def test_ceza_hesaplama_cok_gecikme_satinir_sonrasi(self):
        # Gecikme = 21 gün (14+7). İlk 7 gün (7*2.5=17.5), Sonraki 14 gün (14*5=70). Toplam = 87.5 TL
        tarih_alinma = date(2026, 10, 1)
        tarih_iade = date(2026, 10, 22) # 21 gün gecikme
        self.servis.odunc_ver(2, 101, tarih_alinma)
        kayit = self.servis.iade_al(2, tarih_iade)
        self.assertAlmostEqual(kayit.ceza, 87.50)

    def test_ceza_maksimum_sinir(self):
        # Maksimum ceza 150 TL olmalı. 30 gün gecikme (16+14) 150 TL'yi aşar.
        tarih_alinma = date(2026, 10, 1)
        tarih_iade = date(2026, 11, 10) # 40 gün gecikme
        self.servis.odunc_ver(2, 101, tarih_alinma)
        kayit = self.servis.iade_al(2, tarih_iade)
        self.assertEqual(kayit.ceza, 150.00)

    def test_ceza_ogrenci_indirim(self):
        # Normal ceza 87.5 TL idi, %50 indirim -> 43.75 TL olmalı
        tarih_alinma = date(2026, 10, 1)
        tarih_iade = date(2026, 10, 22) # 21 gün gecikme
        self.servis.odunc_ver(2, 201, tarih_alinma)
        kayit = self.servis.iade_al(2, tarih_iade)
        self.assertAlmostEqual(kayit.ceza, 43.75)

    def test_toplam_ceza(self):
        # Standart üye (101): 2.50 TL ceza ödedi
        tarih_alinma_std = date(2026, 10, 1)
        tarih_iade_std = date(2026, 10, 15)
        self.servis.odunc_ver(1, 101, tarih_alinma_std)
        self.servis.iade_al(1, tarih_iade_std)
        
        # Öğrenci üye (201): 43.75 TL ceza ödedi
        tarih_alinma_ogrenci = date(2026, 10, 1)
        tarih_iade_ogrenci = date(2026, 10, 22)
        self.servis.odunc_ver(2, 201, tarih_alinma_ogrenci)
        self.servis.iade_al(2, tarih_iade_ogrenci)
        
        toplam_std = self.servis.toplam_ceza(101)
        self.assertAlmostEqual(toplam_std, 2.50)
        
        toplam_ogrenci = self.servis.toplam_ceza(201)
        self.assertAlmostEqual(toplam_ogrenci, 43.75)

    def test_uye_siniri_ogrenci(self):
        # Öğrenci (201) limiti 5
        tarih = date(2026, 10, 1)
        for i in range(1, 6): # 5 başarılı ödünç
            self.servis.odunc_ver(1, 201, tarih) 
        
        with self.assertRaisesRegex(ValueError, "maksimum ödünç limiti.*5 aşıldı"):
            self.servis.odunc_ver(2, 201, tarih) # 6. ödünç

    def test_uye_siniri_standart(self):
        # Standart (101) limiti 3
        tarih = date(2026, 10, 1)
        for i in range(1, 4): # 3 başarılı ödünç
            self.servis.odunc_ver(1, 101, tarih) 
        
        with self.assertRaisesRegex(ValueError, "maksimum ödünç limiti.*3 aşıldı"):
            self.servis.odunc_ver(2, 101, tarih) # 4. ödünç

if __name__ == '__main__':
    unittest.main()
