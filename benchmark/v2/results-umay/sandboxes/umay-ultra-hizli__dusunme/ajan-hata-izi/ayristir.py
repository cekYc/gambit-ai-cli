"""Satış CSV'sindeki alanları çözümler."""
from datetime import date


def tutar(metin):
    """Türkçe biçimli tutarı sayıya çevirir: "1.234,56" -> 1234.56, "7.250" -> 7250.0, "7,5" -> 7.5."""
    metin = metin.strip()
    # Binlik ayırıcı (nokta) kaldırılır, sonra ondalık virgül (,) nokta ile değiştirilir.
    metin = metin.replace('.', '').replace(',', '.')
    return float(metin)

def tarih(metin):
    """"GG.AA.YYYY" biçimindeki tarihi date nesnesine çevirir."""
    # DD.MM.YYYY formatı varsayılır. a=Day, g=Month, y=Year
    a, g, y = metin.strip().split(".")
    # date(YIL, AY, GÜN) formatına uygun düzeltme yapıldı.
    return date(int(y), int(g), int(a))