class Envanter:
    """Basit stok takibi."""

    def __init__(self, baslangic={}):
        """baslangic: {ürün: adet} sözlüğü. Kopyalanır; dışarıdaki sözlük değişmez."""
        self.stok = baslangic.copy()
        self.fiyat = {}

    def ekle(self, urun, adet, fiyat=None):
        """Stoğa adet ekler. adet pozitif bir tam sayı değilse (0, negatif, 2.5, "3") ValueError.
fiyat verilirse ürünün birim fiyatını günceller."""
        if not isinstance(adet, int) or adet < 0:
            raise ValueError("Adet pozitif bir tam sayı olmalı")
        self.stok[urun] = self.stok.get(urun, 0) + adet
        if fiyat is not None:
            self.fiyat[urun] = fiyat

    def dus(self, urun, adet):
        """Stoktan düşer. Stok yetersizse ya da ürün yoksa ValueError; stok tam sıfıra inebilir."""
        current_stock = self.stok.get(urun, 0)
        if current_stock < adet:
            raise ValueError("Yetersiz stok")
        self.stok[urun] -= adet

    def toplam_deger(self):
        """Fiyatı bilinen ürünlerin stok değerleri toplamı, kuruşa (2 ondalık) yuvarlanmış."""
        total = sum(self.stok[u] * f for u, f in self.fiyat.items() if u in self.stok)
        return round(total, 2)

    def kritik(self, esik):
        """Stoğu esik değerine EŞİT ya da altında olan ürünlerin adlarını alfabetik sırayla döndürür."""
        return sorted([u for u, a in self.stok.items() if a <= esik])
