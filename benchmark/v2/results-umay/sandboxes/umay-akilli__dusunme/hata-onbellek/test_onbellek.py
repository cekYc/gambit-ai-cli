from onbellek import onbellekle

cagri = []


@onbellekle()
def kare(x):
    """Karesini alır."""
    cagri.append(x)
    return x * x


assert kare(3) == 9 and kare(3) == 9 and cagri == [3], "temel önbellek"
assert kare.bilgi() == {"isabet": 1, "iska": 1}, "bilgi"


@onbellekle()
def us(x, n=2):
    return x ** n


assert us(2, n=3) == 8 and us(2, n=4) == 16, "isimli argümanlar"
assert kare.__name__ == "kare", "fonksiyon adı korunmalı"
print("TÜM TESTLER GEÇTİ")
