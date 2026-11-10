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

    def _limit(self, uye: Uye) -> int:
        return 5 if uye.tur == "ogrenci" else 3

    def _aktif_sayisi(self, uye_id: int) -> int:
        return sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        uye = self.uyeler[uye_id]
        if self._aktif_sayisi(uye_id) >= self._limit(uye):
            raise ValueError("ödünç sınırı aşıldı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplar ve ödünç kaydını döndürür. Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        kayit.ceza = self._ceza_hesapla(kayit)
        return kayit

    def _ceza_hesapla(self, kayit: Odunc) -> float:
        if kayit.iade is None:
            return 0.0
        gun_sayisi = (kayit.iade - kayit.alinma).days
        gecikme = gun_sayisi - 14
        if gecikme <= 0:
            return 0.0
        if gecikme <= 7:
            ceza = gecikme * 2.5
        else:
            ceza = 7 * 2.5 + (gecikme - 7) * 5.0
        if ceza > 150:
            ceza = 150.0
        uye = self.uyeler.get(kayit.uye_id)
        if uye and uye.tur == "ogrenci":
            ceza *= 0.5
        return round(ceza, 2)

    def toplam_ceza(self, uye_id: int) -> float:
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamı."""
        return round(sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None), 2)

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
