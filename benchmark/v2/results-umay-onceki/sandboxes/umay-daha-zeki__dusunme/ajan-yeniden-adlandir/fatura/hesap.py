import warnings

"""KDV hesapları."""

def kdv_hesapla(tutar, oran=0.20):
    """Tutarın KDV'sini döndürür (kuruşa yuvarlanmış)."""
    return round(tutar * oran, 2)

def hesapKdv(tutar, oran=0.20):
    warnings.warn("hesapKdv fonksiyonu kullanımdan kaldırılmıştır. Lütfen kdv_hesapla kullanın.", DeprecationWarning)
    return kdv_hesapla(tutar, oran)

def hesapKdvDahil(tutar, oran=0.20):
    """KDV dahil tutarı döndürür."""
    return round(tutar + kdv_hesapla(tutar, oran), 2)

def toplam_tutar(kalemler):
    """[(fiyat, adet, kdv_orani), ...] listesinin KDV dahil toplamı."""
    return round(sum(f * a + kdv_hesapla(f * a, o) for f, a, o in kalemler), 2)