"""Metin yardımcıları."""
import re

AYIRICI = "-"


def kisalt(metin: str, uzunluk: int = 20, son: str = "…") -> str:
    """Metni verilen uzunluğa kısaltır.

    Ayrıntılı açıklama.
    """
    return metin if len(metin) <= uzunluk else metin[: uzunluk - len(son)] + son


def kelime_say(metin):
    """Metindeki kelime sayısını döndürür."""
    return len(_kelimeler(metin))


def _kelimeler(metin):
    """İç yardımcı."""
    return re.findall(r"\w+", metin)


def baslik(metin: str, *, kucuk_kelimeler=("ve", "ile")) -> str:
    """Her kelimenin ilk harfini büyütür (bağlaçlar hariç)."""
    return " ".join(k if k in kucuk_kelimeler else k.capitalize() for k in metin.split())


class Sablon:
    """Basit metin şablonu."""

    def __init__(self, metin):
        self.metin = metin

    def doldur(self, **degerler) -> str:
        """Şablondaki {ad} alanlarını doldurur."""
        return self.metin.format(**degerler)

    def _ham(self):
        return self.metin
