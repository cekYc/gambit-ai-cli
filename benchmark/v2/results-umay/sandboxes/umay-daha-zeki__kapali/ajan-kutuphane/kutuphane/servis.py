from .modeller import Odunc, Uye
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

    def _ceza_hesapla(self, odunc: Odunc, uye: Uye, iade_tarihi: date) -> float:
        gecikme = (iade_tarihi - odunc.alinma).days - 14
        if gecikme <= 0:
            return 0.0

        # Ceza kuralı: İlk 7 gün 2.50 TL, sonrası 5.00 TL
        ceza = 0.0
        if gecikme > 0:
            ilk_7_gun_ceza = min(gecikme, 7) * 2.50
            sonraki_gun_ceza = max(0, gecikme - 7) * 5.00
            ceza = ilk_7_gun_ceza + sonraki_gun_ceza

        # Maksimum ceza 150 TL
        ceza = min(ceza, 150.0)

        # Öğrenci indirimi (%50)
        if uye.tur == "ogrenci":
            ceza *= 0.50

        return round(ceza, 2)

    def odunc_ver(self, kitap_id, uye_id, tarih):
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")

        # Üye kitap sınırı kontrolü
        aktif_odunc = [k for k in self.kayitlar if k.uye_id == uye_id and k.iade is None]
        satin_siniri = 5 if self.uyeler[uye_id].tur == "ogrenci" else 3
        if len(aktif_odunc) >= satin_siniri:
            raise ValueError(f"Üye türünüz ({self.uyeler[uye_id].tur}) için maksimum {satin_siniri} kitap ödünç alınabilir.")

        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")

        uye = self.uyeler[kayit.uye_id]
        ceza = self._ceza_hesapla(kayit, uye, tarih)

        kayit.iade = tarih
        kayit.ceza = ceza
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id) -> float:
        toplam = 0.0
        for kayit in self.kayitlar:
            if kayit.uye_id == uye_id and kayit.iade is not None:
                toplam += kayit.ceza
        return round(toplam, 2)
