from .modeller import Odunc


class KutuphaneServisi:
    GUNLUK_CEZA_BASLANGIC = 2.50
    GUNLUK_CEZA_SONRA = 5.00
    CEZA_SINIR = 150.0
    OGRENCI_INDIRIM = 0.50
    ODUNC_SURESI = 14

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

    def _gun_sayisi(self, alinma, iade):
        return (iade - alinma).days

    def _ceza_hesapla(self, alinma, iade, uye_tur):
        gun = self._gun_sayisi(alinma, iade)
        gecikme = max(0, gun - self.ODUNC_SURESI)
        if gecikme == 0:
            return 0.0
        ilki = min(gecikme, 7) * self.GUNLUK_CEZA_BASLANGIC
        sonraki = max(0, gecikme - 7) * self.GUNLUK_CEZA_SONRA
        ceza = ilki + sonraki
        ceza = min(ceza, self.CEZA_SINIR)
        if uye_tur == "ogrenci":
            ceza *= self.OGRENCI_INDIRIM
        return round(ceza, 2)

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        uye = self.uyeler[uye_id]
        aktif_sayisi = sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
        sinir = 5 if uye.tur == "ogrenci" else 3
        if aktif_sayisi >= sinir:
            raise ValueError("üye ödünçte tutabileceği kitap sınırına ulaştı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplayıp kayda yazar ve ödünç kaydını döndürür. Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        uye = self.uyeler[kayit.uye_id]
        kayit.ceza = self._ceza_hesapla(kayit.alinma, tarih, uye.tur)
        return kayit

    def toplam_ceza(self, uye_id):
        """Üyenin iade edilmiş tüm ödünçlerinin cezalarının toplamını döndürür."""
        return round(sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None), 2)

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
