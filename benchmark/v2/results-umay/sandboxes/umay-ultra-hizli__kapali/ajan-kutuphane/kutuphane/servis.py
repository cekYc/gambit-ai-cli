from .modeller import Odunc
from datetime import date
from typing import List

class KutuphaneServisi:
    def __init__(self):
        self.kitaplar = {}
        self.uyeler = {}
        self.kayitlar: List[Odunc] = []

    def kitap_ekle(self, kitap):
        self.kitaplar[kitap.id] = kitap

    def uye_ekle(self, uye):
        self.uyeler[uye.id] = uye

    def _aktif(self, kitap_id):
        return next((k for k in self.kayitlar if k.kitap_id == kitap_id and k.iade is None), None)

    def _uye_siniri_kontrol(self, uye_id):
        uye = self.uyeler.get(uye_id)
        if not uye:
            return 0
        if uye.tur == "ogrenci":
            return 5
        return 3

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError fırlatır ve üye sınırını kontrol eder."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        
        max_sinir = self._uye_siniri_kontrol(uye_id)
        aktif_odunc = len(self.oduncteki_kitaplar(uye_id))
        if aktif_odunc >= max_sinir:
            raise ValueError(f"Üye ({uye_id}) için maksimum ödünç limiti ({max_sinir}) aşıldı.")

        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, gecikme varsa cezayı hesaplar ve kaydı günceller. Ceza hesaplandıktan sonra kayıt döner."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        
        alinma_tarihi = kayit.alinma
        gecikme_gunu = (tarih - alinma_tarihi).days
        
        ceza_miktari = 0.0
        if gecikme_gunu > 14:
            gecikme = gecikme_gunu - 14
            # İlk 7 gün: 2.50 TL, sonraki günler: 5.00 TL
            ceza_ilk_7 = min(7, gecikme) * 2.50
            ceza_sonrasi = max(0, gecikme - 7) * 5.00
            ceza_miktari = ceza_ilk_7 + ceza_sonrasi
        
        # Maksimum ceza 150 TL
        ceza_miktari = min(ceza_miktari, 150.0)

        # Öğrenci indirimi (%50)
        uye = self.uyeler.get(kayit.uye_id)
        if uye and uye.tur == "ogrenci":
            ceza_miktari *= 0.50
        
        # Sonuç 2 ondalığa yuvarlanır
        ceza_miktari = round(ceza_miktari, 2)
        
        kayit.ceza = ceza_miktari
        kayit.iade = tarih
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id) -> float:
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamını döndürür."""
        toplam = sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None)
        return round(toplam, 2)
