class Envanter:
    """Basit stok takibi."""

    def __init__(self, baslangic=None):
        """baslangic: {ürün: adet} sözlüğü. Kopyalanır; dışarıdaki sözlük değişmez."""
        self.stok = dict(baslangic) if baslangic is not None else {}
        self.fiyat = {}

    def ekle(self, urun, adet, fiyat=None):
        """Stoğa adet ekler. adet pozitif bir tam sayı değilse (0, negatif, 2.5, "3") ValueError.
        fiyat verilirse ürünün birim fiyatını günceller."""
        if isinstance(adet, bool) or not isinstance(adet, int) or adet <= 0:
            raise ValueError("adet pozitif bir tam sayı olmalı")
        self.stok[urun] = self.stok.get(urun, 0) + adet
        if fiyat is not None:
            self.fiyat[urun] = fiyat

    def dus(self, urun, adet):
        """Stoktan düşer. Stok yetersizse ya da ürün yoksa ValueError; stok tam sıfıra inebilir."""
        mevcut = self.stok.get(urun, 0)
        if urun not in self.stok or mevcut < adet:
            raise ValueError("yetersiz stok")
        self.stok[urun] -= adet

    def toplam_deger(self):
        """Fiyatı bilinen ürünlerin stok değerleri toplamı, kuruşa (2 ondalık) yuvarlanmış."""
        return round(sum(self.stok[u] * f for u, f in self.fiyat.items()), 2)

    def kritik(self, esik):
        """Stoğu esik değerine EŞİT ya da altında olan ürünlerin adlarını alfabetik sırayla döndürür."""
        return sorted([u for u, a in self.stok.items() if a <= esik])
