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

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")
        uye = self.uyeler[uye_id]
        aktif_sayisi = sum(1 for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)
        limit = 5 if uye.tur == "ogrenci" else 3
        if aktif_sayisi >= limit:
            raise ValueError("üyenin ödünçte tutabileceği kitap sayısı sınırına ulaşıldı")
        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def iade_al(self, kitap_id, tarih):
        """Kitabın iadesini alır, cezayı hesaplayıp kayda yazar ve ödünç kaydını döndürür.
        Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")
        kayit.iade = tarih
        kayit.ceza = self._hesapla_ceza(kayit, tarih)
        return kayit

    def _hesapla_ceza(self, kayit, tarih):
        geciken = (tarih - kayit.alinma).days - 14
        if geciken <= 0:
            return 0.0
        sure_1 = min(geciken, 7)
        sure_2 = max(0, geciken - 7)
        ceza = sure_1 * 2.50 + sure_2 * 5.00
        if ceza > 150.0:
            ceza = 150.0
        uye = self.uyeler[kayit.uye_id]
        if uye.tur == "ogrenci":
            ceza *= 0.5
        return round(ceza, 2)

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id):
        """Üyenin iade edilmiş tüm ödünçlerinin cezalarının toplamını döndürür."""
        return round(
            sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None),
            2,
        )