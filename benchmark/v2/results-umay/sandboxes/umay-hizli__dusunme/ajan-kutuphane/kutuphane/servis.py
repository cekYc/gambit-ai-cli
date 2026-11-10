from .modeller import Odunc, Uye


CEZA_GUNLUK_ILK = 2.50
CEZA_GUNLUK_SONRA = 5.00
CEZA_MAX = 150.0
ODUNC_SURESI = 14
ODUNC_LIMITI = {"standart": 3, "ogrenci": 5}


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

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        uye = self.uyeler[uye_id]
        limit = ODUNC_LIMITI.get(uye.tur, ODUNC_LIMITI["standart"])
        if self._aktif_sayisi(uye_id) >= limit:
            raise ValueError("ödünç kitap sınırı aşıldı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def _ceza_hesapla(self, kayit: Odunc, uye: Uye) -> float:
        geciken = (kayit.iade - kayit.alinma).days - ODUNC_SURESI
        if geciken <= 0:
            return 0.0
        ilk = min(geciken, 7) * CEZA_GUNLUK_ILK
        sonra = max(0, geciken - 7) * CEZA_GUNLUK_SONRA
        ceza = min(ilk + sonra, CEZA_MAX)
        if uye.tur == "ogrenci":
            ceza *= 0.5
        return round(ceza, 2)

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplayıp kayda yazar ve ödünç kaydını döndürür.
        Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        kayit.ceza = self._ceza_hesapla(kayit, self.uyeler[kayit.uye_id])
        return kayit

    def toplam_ceza(self, uye_id) -> float:
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamı."""
        return round(
            sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None),
            2,
        )

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
