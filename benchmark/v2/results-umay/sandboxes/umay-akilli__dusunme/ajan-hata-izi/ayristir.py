"""Satış CSV'sindeki alanları çözümler."""
from datetime import date


def tutar(metin):
    """Türkçe biçimli tutarı sayıya çevirir: "1.234,56" -> 1234.56, "7.250" -> 7250.0, "7,5" -> 7.5."""
    metin = metin.strip()
    if "," in metin:
        tam, kurus = metin.split(",")
        tam = float(tam.replace(".", ""))
        # Tek basamaklı kuruş ondalık (5 -> 0.5), iki basamaklı kuruş (05 -> 0.05)
        kurus_val = float(kurus) / (10 if len(kurus) == 1 else 100)
        return tam + kurus_val
    # Nokta varsa binlik ayırıcıdır (örn. "32.500" -> 32500)
    return float(metin.replace(".", ""))


def tarih(metin):
    """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
    g, a, y = metin.strip().split(".")
    return date(int(y), int(a), int(g))
