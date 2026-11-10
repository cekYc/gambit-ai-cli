import csv

import rapor

with open("veri/satislar.csv", encoding="utf-8") as f:
    satirlar = [(r["tarih"], r["urun"], r["tutar"]) for r in csv.DictReader(f, delimiter=";")]
rapor.yaz(satirlar, "rapor.txt")
print("rapor.txt yazıldı")
