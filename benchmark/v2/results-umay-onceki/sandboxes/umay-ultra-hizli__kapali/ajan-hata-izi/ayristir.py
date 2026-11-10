"""Satış CSV'sindeki alanları çözümler."""
from datetime import date


def tutar(metin):
    """Türkçe biçimli tutarı sayıya çevirir: "32.500" -> 32500, "7.250,50" -> 7250.50, "7,5" -> 7.5."""
    metin = metin.strip()
    # Türkçe ondalık ayrağı "," ve binler Ayrıracı "."
    if "," in metin:
        # Önce binler ayracı "." varsa kaldır
        metin = metin.replace(".", "")
        # Sonra "" ile ayır (ondalık kısım)
        tam, kurus = metin.split(",", 1)
        # Tam kısma tekrar binler ayracı ekle (boş olursa eklemez)
        if tam:
            tam = tam.replace(".", "")
        # Kurus 2 haneli değil de 1 haneli ("7,5") olabilir
        if len(kurus) == 1:
            kurus += "0"
        return float(tam) + float(kurus) / 100
    return float(metin)


def tarih(metin):
    """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
    a, g, y = metin.strip().split(".")
    return date(int(y), int(g), int(a))
