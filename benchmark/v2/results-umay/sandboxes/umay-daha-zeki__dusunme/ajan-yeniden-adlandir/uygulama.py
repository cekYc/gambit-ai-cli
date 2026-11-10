import fatura
from fatura.rapor import satir

print(satir("Kalem", 125.0))
print(satir("Kitap", 300.0, 0.10))
print("KDV:", fatura.kdv_hesapla(1000))
print("Toplam:", fatura.toplam_tutar([(100, 2, 0.2), (50, 1, 0.1)]))