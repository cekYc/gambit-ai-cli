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

    def odunc_ver(self, kitap_id, uye_id, tarih):
        """Kitabı üyeye verir. Kitap/üye yoksa ya da kitap zaten ödünçteyse ValueError. Kitap sınırı kontrolü yapar."""
        if kitap_id not in self.kitaplar or uye_id not in self.uyeler:
            raise ValueError("kitap ya da üye bulunamadı")
        if self._aktif(kitap_id):
            raise ValueError("kitap zaten ödünçte")

        # Kitap Sınırı Kontrolü
        aktif_odunc = [k for k in self.kayitlar if k.uye_id == uye_id and k.iade is None]
        uye = self.uyeler[uye_id]
        sinir = 5 if uye.tur == "ogrenci" else 3
        if len(aktif_odunc) >= sinir:
            raise ValueError(f"Üye türü {uye.tur} için maksimum {sinir} kitap ödünç alınabilir. Sınır aşıldı.")

        kayit = Odunc(kitap_id, uye_id, tarih)
        self.kayitlar.append(kayit)
        return kayit

    def _hesapla_ceza(self, alinma_tarihi, iade_tarihi, uye_tur):
        # Ödünç süresi 14 gündür
        sure_gun = (iade_tarihi - alinma_tarihi).days
        gecikme = max(0, sure_gun - 14)

        if gecikme == 0:
            return 0.0

        # Ceza Hesaplama Kuralları
        # İlk 7 gün: 2.50 TL, Sonraki günler: 5.00 TL
        ceza = 0.0
        gecikme_ilk_7 = min(gecikme, 7)
        ceza += gecikme_ilk_7 * 2.50

        gecikme_sonraki = max(0, gecikme - 7)
        ceza += gecikme_sonraki * 5.00

        # Maksimum ceza 150 TL
        ceza = min(ceza, 150.0)

        # Öğrenci indirimi (%50)
        if uye_tur == "ogrenci":
            ceza *= 0.5

        return round(ceza, 2)

    def iade_al(self, kitap_id, iade_tarih):
        """Kitabın iadesini alır, cezayı hesaplar ve kaydı günceller. Kitap ödünçte değilse ValueError."""
        kayit = self._aktif(kitap_id)
        if kayit is None:
            raise ValueError("kitap ödünçte değil")

        # Ceza Hesaplama ve Kayda Yazma
        ceza = self._hesapla_ceza(kayit.alinma, iade_tarih, self.uyeler[kayit.uye_id].tur)
        kayit.ceza = ceza

        # İade tarihi güncelleme
        kayit.iade = iade_tarih
        return kayit

    def oduncteki_kitaplar(self, uye_id):
        return sorted(k.kitap_id for k in self.kayitlar if k.uye_id == uye_id and k.iade is None)

    def toplam_ceza(self, uye_id) -> float:
        """Üyenin iade edilmiş tüm ödünçlerinin cezaları toplamını hesaplar."""
        toplam = sum(k.ceza for k in self.kayitlar if k.uye_id == uye_id and k.iade is not None)
        return round(toplam, 2)