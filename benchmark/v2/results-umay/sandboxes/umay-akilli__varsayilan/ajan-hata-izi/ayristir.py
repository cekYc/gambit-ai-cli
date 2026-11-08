"""Satış CSV'sindeki alanları çözümler."""
from datetime import date


def tutar(metin):
    """Türkçe biçimli tutarı sayıya çevirir: "1.234,56" -> 1234.56, "7.250" -> 7250.0, "7,5" -> 7.5."""
    metin = metin.strip()
    if "," in metin:
        tam, kurus = metin.split(",")
        # kuruş kısmı 1 veya 2 basamak olabilir: "5" -> 50 kuruş, "90" -> 90 kuruş
        kurus = kurus.ljust(2, "0")[:2]
        return float(tam.replace(".", "")) + int(kurus) / 100
    # Virgül yok: nokta varsa binlik ayracıdır (ondalık değil)
    return float(metin.replace(".", ""))


def tarih(metin):
    """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
    g, a, y = metin.strip().split(".")
    return date(int(y), int(a), int(g))
