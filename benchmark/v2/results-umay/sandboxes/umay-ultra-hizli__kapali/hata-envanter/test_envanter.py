from envanter import Envanter

e = Envanter()
e.ekle("kalem", 10, fiyat=12.35)
e.ekle("defter", 3, fiyat=40)
e.dus("kalem", 4)
assert e.stok["kalem"] == 6, "dus"
e.dus("defter", 3)
assert e.stok["defter"] == 0, "stok sıfıra inebilmeli"
assert e.toplam_deger() == 74.1, "toplam_deger"
try:
    e.ekle("silgi", -2)
    raise AssertionError("negatif adet kabul edildi")
except ValueError:
    pass
print("TÜM TESTLER GEÇTİ")
