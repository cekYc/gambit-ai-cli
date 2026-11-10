"""Satış CSV'sindeki alanları çözümler."""
from datetime import date


def tutar(metin):
    """Türkçe biçimli tutarı sayıya çevirir.
    "1.234,56" -> 1234.56 (bin ayracı + onlar)
    "7.250" -> 7250.0 (sadece bin ayracı)
    "7,5" -> 7.5 (ondalık)
    "32500" -> 32500 (sıfı ayracı yok)
    """
    metin = metin.strip()
    if "," in metin:
        # Onlıklı format: "1.234,56"
        tam, kurus = metin.split(",")
        return float(tam.replace(".", "")) + float(kurus) / 100
    elif "." in metin:
        # Bin ayracı olan, onlıksız: "32.500" -> 32500.0
        return float(metin.replace(".", ""))
    else:
        # Sadece sayı: "25" -> 25.0
        return float(metin)


def tarih(metin):
    """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
    g, a, y = metin.strip().split(".")
    return date(int(y), int(a), int(g))
