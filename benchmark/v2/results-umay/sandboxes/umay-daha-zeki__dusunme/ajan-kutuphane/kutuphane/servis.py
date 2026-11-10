from .modeller import Odunc, Uye
from datetime import date


class KutuphaneServisi:
    def __init__(self):
        self.kitaplar = {}
        self.uyeler = {}
        self.kayitlar = []

    def kitap_ekle(self, kitap):
        self.kitaplar[kitap.id] = kitap

    def uye_ekle(self, uye):
        self.uyeler[uye.id] = uye

    def _aktif(self, kitap_id):
        return next((k for k in self.kayitlar if k.kitap_id == kitap_id and k.iade is None), None)

    def _aktif_odunc_sayisi(self, uye_id):
        return sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def odunc_ver(self, kitap_id, uye_id, tarih: date):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError fırlatır.
        Ayrıca, üye kitap sınırını aşarsa ValueError fırlatır."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")

        uye = self.uyeler[uye_id]
        uye_tipi = uye.tur
        max_limit = 5 if uye_tipi == "ogrenci" else 3

        aktif_sayi = self._aktif_odunc_sayisi(uye_id)
        if aktif_sayi >= max_limit:
            raise ValueError(f"Üye türü ({uye_tipi}) için maksimum ödünç sınırı ({max_limit}) aşıldı.")

        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih: date) -> Odunc:
        """Kitabın iadesini alır, gecikme varsa cezayı hesaplar ve kaydı günceller. Iade edilen kaydı döndürür."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")

        alinma_tarihi = kayit.alinma
        gecikme_gunu = (tarih - alinma_tarihi).days - 14
        
        if gecikme_gunu <= 0:
            kayit.ceza = 0.0
        else:
            # Ceza hesaplaması
            ceza = 0.0
            # İlk 7 gün: 2.50 TL
            ceza += min(7, gecikme_gunu) * 2.50
            # Sonraki günler: 5.00 TL
            kalan_gecikme = max(0, gecikme_gunu - 7)
            ceza += kalan_gecikme * 5.00
            
            # Maksimum ceza ve öğrenci indirimi
            ceza = min(ceza, 150.0)
            
            uye = self.uyeler[kayit.uye_id]
            if uye.tur == "ogrenci":
                ceza *= 0.50
            
            kayit.ceza = round(ceza, 2)
        
        kayit.iade = tarih
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id) -> float:
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamını hesaplar."""
        toplam = sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None)
        return round(toplam, 2)
