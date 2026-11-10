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

    def _uyenin_aktif_odunc_sayisi(self, uye_id):
        return sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def _maks_odunc_limiti(self, uye_id):
        uye = self.uyeler.get(uye_id)
        if uye is None:
            return 0
        return 5 if uye.tur == "ogrenci" else 3

    def _ceza_hesapla(self, alinma, iade, uye_tur):
        gun_sayisi = (iade - alinma).days
        gecikme = max(0, gun_sayisi - 14)
        if gecikme == 0:
            return 0.0
        if gecikme <= 7:
            ceza = gecikme * 2.5
        else:
            ceza = 7 * 2.5 + (gecikme - 7) * 5.0
        ceza = min(ceza, 150.0)
        if uye_tur == "ogrenci":
            ceza *= 0.5
        return round(ceza, 2)

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        if self._uyenin_aktif_odunc_sayisi(uye_id) >= self._maks_odunc_limiti(uye_id):
            raise ValueError("ödünç limiti aşıldı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplayıp kayda yazar ve ödünç kaydını döndürür."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        uye = self.uyeler.get(kayit.uye_id)
        uye_tur = uye.tur if uye else "standart"
        kayit.ceza = self._ceza_hesapla(kayit.alinma, tarih, uye_tur)
        kayit.iade = tarih
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id):
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamı."""
        return sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None)