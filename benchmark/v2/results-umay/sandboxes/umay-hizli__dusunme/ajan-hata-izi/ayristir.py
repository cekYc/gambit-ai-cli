"""Satış CSV'sindeki alanları çözümler."""
from datetime import date


def tutar(metin):
    """Türkçe biçimli tutarı sayıya çevirir: "1.234,56" -> 1234.56, "7.250" -> 7250.0, "7,5" -> 7.5."""
    metin = metin.strip()
    if "," in metin:
        tam, kurus = metin.split(",")
        return float(tam.replace(".", "")) + float(kurus.ljust(2, "0")[:2]) / 100
    return float(metin.replace(".", ""))


def tarih(metin):
    """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
    a, g, y = metin.strip().split(".")
    return date(int(y), int(g), int(a))
