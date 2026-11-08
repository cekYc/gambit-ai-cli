from .modeller import Odunc


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

    def _aktif_sayisi(self, uye_id):
        return sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def _odunc_limiti(self, uye_id):
        return 5 if self.uyeler[uye_id].tur == "ogrenci" else 3

    def _ceza_hesapla(self, alinma, iade, uye_tur):
        geciken = (iade - alinma).days - 14
        if geciken <= 0:
            return 0.0
        sure = min(geciken, 7)
        fazlasi = max(geciken - 7, 0)
        ceza = sure * 2.50 + fazlasi * 5.00
        if ceza > 150:
            ceza = 150
        if uye_tur == "ogrenci":
            ceza *= 0.5
        return round(ceza, 2)

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        if self._aktif_sayisi(uye_id) >= self._odunc_limiti(uye_id):
            raise ValueError("ödünç kitap sınırına ulaşıldı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplar ve ödünç kaydını döndürür. Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        uye_tur = self.uyeler[kayit.uye_id].tur
        kayit.ceza = self._ceza_hesapla(kayit.alinma, tarih, uye_tur)
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id):
        return round(sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None), 2)
