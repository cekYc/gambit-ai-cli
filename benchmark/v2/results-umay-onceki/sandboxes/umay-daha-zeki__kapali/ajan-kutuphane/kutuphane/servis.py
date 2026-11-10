from .modeller import Odunc
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

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError fırlatır."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        
        # 4. Aynı anda ödünçte tutulabilecek kitap sınırı kontrolü
        uye_tur = self.uyeler[uye_id].tur
        max_limit = 3 if uye_tur == "standart" else 5
        aktif_odunc_sayisi = len([k for k in self.kayitlar if k.uye_id == uye_id and k.iade is None])
        
        if aktif_odunc_sayisi >= max_limit:
            raise ValueError(f"Üye türü '{uye_tur}' için maksimum ödünç sınırı ({max_limit}) aşıldı.")
        
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def _ceza_hesapla(self, alinma_tarihi: date, iade_tarihi: date, uye_tur: str) -> float:
        # Ceza kuralları: Ödünç süresi 14 gün
        gecikme_gunu = (iade_tarihi - alinma_tarihi).days - 14
        
        if gecikme_gunu <= 0:
            return 0.0

        # Gecikme: İlk 7 gün 2,50 TL, sonrası 5,00 TL
        ceza = 0.0
        if gecikme_gunu <= 7:
            ceza = gecikme_gunu * 2.50
        else:
            ceza = 7 * 2.50 + (gecikme_gunu - 7) * 5.00
        
        # Maksimum ceza 150 TL
        ceza = min(ceza, 150.0)
        
        # Öğrenci indirimi (%50)
        if uye_tur == "ogrenci":
            ceza *= 0.50
        
        # Sonuç 2 ondalığa yuvarlanır
        return round(ceza, 2)

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplar/kaydeder ve ödünç kaydını döndürür. Kitap ödünçte değilse ValueError fırlatır."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        
        uye_tur = self.uyeler[kayit.uye_id].tur
        ceza = self._ceza_hesapla(kayit.alinma, tarih, uye_tur)
        
        kayit.iade = tarih
        kayit.ceza = ceza # 1. Odunc kaydına ceza ekleniyor
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    # 3. Üyenin toplam cezası
    def toplam_ceza(self, uye_id) -> float:
        toplam = sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None)
        return round(toplam, 2)