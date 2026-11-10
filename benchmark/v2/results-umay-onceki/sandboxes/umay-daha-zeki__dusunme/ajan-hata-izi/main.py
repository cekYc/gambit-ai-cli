import csv
import rapor

def clean_tutar(tutar_str):
    # Turkish format cleaning: remove periods (thousands separator), replace comma (decimal) with period
    tutar_str = tutar_str.replace('.', '')
    tutar_str = tutar_str.replace(',', '.')
    return tutar_str

with open("veri/satislar.csv", encoding="utf-8") as f:
    satirlar = []
    for r in csv.DictReader(f, delimiter=";"):
        cleaned_tutar = clean_tutar(r["tutar"])
        satirlar.append((r["tarih"], r["urun"], cleaned_tutar))

rapor.yaz(satirlar, "rapor.txt")
print("rapor.txt yazıldı")