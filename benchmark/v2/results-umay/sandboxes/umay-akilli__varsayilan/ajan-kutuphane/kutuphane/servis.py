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

    def _uygun_mu(self, uye_id):
        """Üyenin ödünç alabileceği kitap sayısı sınırını kontrol eder."""
        uye = self.uyeler.get(uye_id)
        if not uye:
            return False
        limit = 5 if uye.tur == "ogrenci" else 3
        aktif_sayisi = sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
        return aktif_sayisi < limit

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        if not self._uygun_mu(uye_id):
            raise ValueError("ödünç limiti aşıldı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def _hesapla_ceza(self, alinma: date, iade: date, uye_tur: str) -> float:
        """Ceza hesaplar."""
        gun_sayisi = (iade - alinma).days
        if gun_sayisi <= 14:
            return 0.0
        gecikme = gun_sayisi - 14
        if gecikme <= 7:
            ceza = gecikme * 2.5
        else:
            ceza = 7 * 2.5 + (gecikme - 7) * 5.0
        if ceza > 150.0:
            ceza = 150.0
        if uye_tur == "ogrenci":
            ceza = ceza * 0.5
        return round(ceza, 2)

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplayıp kayda yazar ve ödünç kaydını döndürür."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        uye = self.uyeler[kayit.uye_id]
        kayit.ceza = self._hesapla_ceza(kayit.alinma, tarih, uye.tur)
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id) -> float:
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamı."""
        return round(sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None), 2)