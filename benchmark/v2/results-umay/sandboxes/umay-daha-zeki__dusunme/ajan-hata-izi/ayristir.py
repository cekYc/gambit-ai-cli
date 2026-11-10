"""Satış CSV'sindeki alanları çözümler."""
from datetime import date

def tutar(metin):
    """Türkçe biçimli tutarı sayıya çevirir: "1.234,56" -> 1234.56, "7.250" -> 7250.0, "7,5" -> 7.5."""
    metin = metin.strip()
    # Binlik ayırıcı ('.') kaldırılır, ardından ondalık ayırıcı (',') '.' olarak değiştirilir.
    metin = metin.replace('.', '') 
    if ',' in metin:
        metin = metin.replace(',', '.')
    return float(metin)

def tarih(metin):
    """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
    # CSV formatı: Gün.Ay.Yıl (a=Gün, g=Ay, y=Yıl)
    a, g, y = metin.strip().split(".")
    # date() constructor: date(Yıl, Ay, Gün)
    return date(int(y), int(g), int(a))