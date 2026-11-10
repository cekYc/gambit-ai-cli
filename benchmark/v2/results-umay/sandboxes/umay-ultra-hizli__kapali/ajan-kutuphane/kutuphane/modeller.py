from dataclasses import dataclass
from datetime import date


@dataclass
class Kitap:
    id: int
    ad: str
    yazar: str


@dataclass
class Uye:
    id: int
    ad: str
    tur: str = "standart"  # "standart" ya da "ogrenci"


@dataclass
class Odunc:
    kitap_id: int
    uye_id: int
    alinma: date
    iade: date | None = None
    ceza: float = 0.0
    uye_id: int
    alinma: date
    iade: date | None = None
