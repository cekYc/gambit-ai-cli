"""Sayı yardımcıları."""


def yuvarla(x: float, basamak: int = 2) -> float:
    """Yarımları yukarı yuvarlar."""
    k = 10 ** basamak
    return int(x * k + (0.5 if x >= 0 else -0.5)) / k


def ortalama(*sayilar, bos=0):
    """Sayıların ortalaması; sayı yoksa bos döner."""
    return sum(sayilar) / len(sayilar) if sayilar else bos


async def topla_async(a, b):
    """Asenkron toplama."""
    return a + b


def _gizli():
    pass
