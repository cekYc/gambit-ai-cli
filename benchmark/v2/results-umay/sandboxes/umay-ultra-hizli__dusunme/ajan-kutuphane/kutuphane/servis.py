from .modeller import Odunc
from datetime import date, timedelta


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
        uye = self.uyeler.get(uye_id)
        if uye is None:
            raise ValueError("üye bulunamadı")
        
        uye_tur = uye.tur
        max_limit = 5 if uye_tur == "ogrenci" else 3
        
        aktif_kitaplar = self.oduncteki_kitaplar(uye_id)
        if len(aktif_kitaplar) >= max_limit:
            raise ValueError(f"Üye türü '{uye_tur}' için maksimum ödünç sayısı ({max_limit}) aşıldı.")

        if kitap_id not in self.kitaplar:
            raise ValueError("kitap bulunamadı")

        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplar ve ödünç kaydını döndürür."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        
        uye = self.uyeler.get(kayit.uye_id)
        if uye is None:
             raise ValueError("üye bulunamadı")

        ceza = self._ceza_hesapla(kayit, uye.tur, tarih)
        kayit.ceza = ceza
        kayit.iade = tarih
        return kayit

    def _ceza_hesapla(self, kayit: Odunc, uye_tur: str, iade_tarihi: date) -> float:
        """Gecikmeyi hesaplar ve cezayı kurallara göre döndürür."""
        alis_tarihi = kayit.alinma
        gecikme = (iade_tarihi - alis_tarihi).days - 14

        if gecikme <= 0:
            return 0.0

        # Ceza kuralları: ilk 7 gün 2.50 TL, sonrası 5.00 TL
        gecikme_7_gun = min(gecikme, 7)
        gecikme_sonrasi = max(0, gecikme - 7)
        
        ceza_brut = (gecikme_7_gun * 2.50) + (gecikme_sonrasi * 5.00)
        
        # Ceza sınırı: 150 TL
        ceza_max = 150.0
        ceza_uyelik_indirim = 0.5 if uye_tur == "ogrenci" else 0.0
        
        ceza_uyelikli = ceza_brut * (1 - ceza_uyelik_indirim)
        ceza_nihai = min(ceza_max, ceza_uyelikli)
        
        return round(ceza_nihai, 2)
        """Kitabın iadesini alır ve ödünç kaydını döndürür. Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
