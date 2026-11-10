from .modeller import Odunc, Uye


ODUNC_SURESI = 14
CEZA_GUNLUK_ILK = 2.50
CEZA_GUNLUK_SONRA = 5.00
CEZA_MAKSIMUM = 150.0
OGRENCI_INDIRIMI = 0.5
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

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        uye = self.uyeler[uye_id]
        aktif_sayisi = sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
        limit = ODUNC_LIMITI.get(uye.tur, ODUNC_LIMITI["standart"])
        if aktif_sayisi >= limit:
            raise ValueError("ödünç limitine ulaşıldı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def _ceza_hesapla(self, kayit, tarih):
        gun = (tarih - kayit.alinma).days
        gecikme = gun - ODUNC_SURESI
        if gecikme <= 0:
            return 0.0
        sure1 = min(gecikme, 7)
        sure2 = max(gecikme - 7, 0)
        ceza = sure1 * CEZA_GUNLUK_ILK + sure2 * CEZA_GUNLUK_SONRA
        ceza = min(ceza, CEZA_MAKSIMUM)
        uye = self.uyeler.get(kayit.uye_id)
        if uye is not None and uye.tur == "ogrenci":
            ceza *= OGRENCI_INDIRIMI
        return round(ceza, 2)

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplayıp kayda yazar ve kaydı döndürür. Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        kayit.ceza = self._ceza_hesapla(kayit, tarih)
        return kayit

    def toplam_ceza(self, uye_id):
        """Üyenin iade edilmiş tüm ödünçlerinin cezalarının toplamı."""
        return round(sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None), 2)

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
