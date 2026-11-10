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
    ceza: float = 0.0
    iade: date | None = None
    iade: date | None = None
