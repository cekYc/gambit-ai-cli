class Envanter:
    """Basit stok takibi."""

    def __init__(self, baslangic={}):
        """baslangic: {ürün: adet} sözlüğü. Kopyalanır; dışarıdaki sözlük değişmez."""
        self.stok = baslangic.copy()
        self.fiyat = {}

    def ekle(self, urun, adet, fiyat=None):
        """Stoğa adet ekler. adet pozitif bir tam sayı olmalıdır. Fiyat verilirse ürünün birim fiyatını günceller."""
        if not isinstance(adet, int) or adet <= 0:
            raise ValueError("Adet pozitif bir tam sayı olmalıdır.")
        
        self.stok[urun] = self.stok.get(urun, 0) + adet
        if fiyat is not None:
            self.fiyat[urun] = fiyat

    def dus(self, urun, adet):
        """Stoktan düşer. Stok yetersizse ya da ürün yoksa ValueError; stok tam sıfıra inebilir."""
        if self.stok.get(urun, 0) >= adet:
            self.stok[urun] -= adet
        else:
            raise ValueError("Yetersiz stok veya ürün bulunamadı.")

    def toplam_deger(self):
        """Fiyatı bilinen ürünlerin stok değerleri toplamı, kuruşa (2 ondalık) yuvarlanmış olarak döner."""
        toplam = 0
        for u, f in self.fiyat.items():
            if u in self.stok:
                toplam += self.stok[u] * f
        return round(toplam, 2)

    def kritik(self, esik):
        """Stoğu esik değerine EŞİT ya da altında olan ürünlerin adlarını alfabetik sırayla döndürür."""
        kritik_urunler = [u for u, a in self.stok.items() if a <= esik]
        return sorted(kritik_urunler)
