from fatura.hesap import hesapKdv as kdv
from fatura.hesap import hesapKdvDahil


def satir(ad, tutar, oran=0.20):
    return f"{ad:<10} {tutar:>10.2f} KDV {kdv(tutar, oran):>8.2f} TOPLAM {hesapKdvDahil(tutar, oran):>10.2f}"
