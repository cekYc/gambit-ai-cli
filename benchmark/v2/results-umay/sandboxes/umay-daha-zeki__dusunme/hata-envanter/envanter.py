class Envanter:
    """Basit stok takibi."""

    def __init__(self, baslangic={}):
        """baslangic: {ürün: adet} sözlüğü. Kopyalanır; dışarıdaki sözlük değişmez."""
        self.stok = baslangic.copy()
        self.fiyat = {}

    def ekle(self, urun, adet, fiyat=None):
        """Stoğa adet ekler. adet pozitif bir tam sayı değilse (0, negatif, 2.5, "3") ValueError.
fiyat verilirse ürünün birim fiyatını günceller."""
        if not isinstance(adet, int) or adet <= 0:
            raise ValueError("Adet pozitif bir tam sayı olmalıdır.")
        
        self.stok[urun] = self.stok.get(urun, 0) + adet
        if fiyat is not None:
            self.fiyat[urun] = fiyat

    def dus(self, urun, adet):
        """Stoktan düşer. Stok yetersizse ya da ürün yoksa ValueError; stok tam sıfıra inebilir."""
        current_stock = self.stok.get(urun, 0)
        if current_stock == 0 and adet > 0:
             raise ValueError(f"Ürün '{urun}' stoğumuzda bulunmamaktadır.")
        if current_stock < adet:
            raise ValueError("Yetersiz stok")
        
        self.stok[urun] -= adet

    def toplam_deger(self):
        """Fiyatı bilinen ürünlerin stok değerleri toplamı, kuruşa (2 ondalık) yuvarlanmış."""
        # Fiyatı bilinen ürünleri filtrele ve toplamı 2 ondalık hassasiyette yuvarla
        toplam = sum(self.stok[u] * f for u, f in self.fiyat.items())
        return round(toplam, 2)

    def kritik(self, esik):
        """Stoğu esik değerine EŞİT ya da altında olan ürünlerin adlarını alfabetik sırayla döndürür."""
        kritik_urunler = [u for u, a in self.stok.items() if a <= esik]
        return sorted(kritik_urunler)
