"""KDV hesapları."""

# DeprecationWarning uyarısı için eski fonksiyonu koruyoruz
def hesapKdv(tutar, oran=0.20):
    """Tutarın KDV'sini döndürür (eski fonksiyon)."""
    import warnings
    warnings.warn("hesapKdv kullanımdan kaldırıldı. Lütfen kdv_hesapla kullanın.", DeprecationWarning)
    return round(tutar * oran, 2)


def kdv_hesapla(tutar, oran=0.20):
    """Tutarın KDV'sini döndürür (yeni fonksiyon)."""
    return round(tutar * oran, 2)


def hesapKdvDahil(tutar, oran=0.20):
    """KDV dahil tutarı döndürür (eski fonksiyon)."""
    import warnings
    warnings.warn("hesapKdvDahil kullanımdan kaldırıldı. Lütfen kdv_hesaplaDahil kullanın.", DeprecationWarning)
    return round(tutar + hesapKdv(tutar, oran), 2)


def kdv_hesaplaDahil(tutar, oran=0.20):
    """KDV dahil tutarı döndürür (yeni fonksiyon)."""
    return round(tutar + kdv_hesapla(tutar, oran), 2)


def toplam_tutar(kalemler):
    """[(fiyat, adet, kdv_orani), ...] listesinin KDV dahil toplamı."""
    return round(sum(f * a + kdv_hesapla(f * a, o) for f, a, o in kalemler), 2)