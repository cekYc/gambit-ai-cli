from .modeller import Odunc, Uye


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

    def _maks_odunc(self, uye: Uye) -> int:
        return 5 if uye.tur == "ogrenci" else 3

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        uye = self.uyeler[uye_id]
        if self._aktif_sayisi(uye_id) >= self._maks_odunc(uye):
            raise ValueError("üye ödünç kitap sınırına ulaştı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    @staticmethod
    def _ceza_hesapla(kayit: Odunc, uye: Uye, tarih: date) -> float:
        gecikme = (tarih - kayit.alinma).days - 14
        if gecikme <= 0:
            return 0.0
        ilk = min(gecikme, 7) * 2.50
        sonraki = max(gecikme - 7, 0) * 5.00
        ceza = ilk + sonraki
        if ceza > 150:
            ceza = 150.0
        if uye.tur == "ogrenci":
            ceza *= 0.5
        return round(ceza, 2)

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplayıp kayda yazar ve ödünç kaydını döndürür.
        Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        uye = self.uyeler[kayit.uye_id]
        kayit.iade = tarih
        kayit.ceza = self._ceza_hesapla(kayit, uye, tarih)
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id) -> float:
        return round(
            sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None),
            2,
        )
