"""Bağımlılık kurulum sırası hesaplama modülü (sadece standart kitaplık)."""

from __future__ import annotations

import heapq


class DonguHatasi(ValueError):
    """Bağımlılık grafiğinde bir döngü bulunduğunda fırlatılan istisna."""

    def __init__(self, dongu: list[str], mesaj: str | None = None) -> None:
        self.dongu = list(dongu)
        if mesaj is None:
            zincir = " -> ".join(self.dongu)
            mesaj = f"Bağımlılık döngüsü tespit edildi: {zincir} -> {self.dongu[0]}"
        super().__init__(mesaj)


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """deps içindeki tüm paketleri bağımlılık sırasına göre döndürür.

    ``deps[p]``, p'den önce kurulması gereken paketleri listeler. Aynı
    bağımlılık birden fazla yazılmış olabilir. Her paket kendi
    bağımlılarından sonra gelir; eşlikerde alfabetik olarak en küçük
    önce seçilir (Kahn algoritması + min-heap). Döngü varsa
    ``DonguHatasi`` fırlatılır ve ``dongu`` özniteliği döngüyü
    (alfabetik en küçük paketten başlayarak) içerir.
    """
    # 1. Tüm paketleri topla (anahtar olarak ve yalnızca bağımlılık olarak geçenler).
    tum_paketler: set[str] = set(deps.keys())
    for bagimlilikler in deps.values():
        tum_paketler.update(bagimlilikler)

    # Ön-şart ve başarımlı kenarları, tekilleştirerek tut.
    once: dict[str, set[str]] = {p: set() for p in tum_paketler}
    sonra: dict[str, set[str]] = {p: set() for p in tum_paketler}

    for paket, bagimlilikler in deps.items():
        for bagimlilik in set(bagimlilikler):
            once[paket].add(bagimlilik)
            sonra[bagimlilik].add(paket)

    # 2. Kahn algoritması: her adımda ön şartı kalmayan alfabetik en küçük paket.
    hazir: list[str] = [p for p in tum_paketler if not once[p]]
    heapq.heapify(hazir)

    sirali: list[str] = []
    while hazir:
        paket = heapq.heappop(hazir)
        sirali.append(paket)
        for gosteren in sonra[paket]:
            once[gosteren].discard(paket)
            if not once[gosteren]:
                heapq.heappush(hazir, gosteren)

    if len(sirali) == len(tum_paketler):
        return sirali

    # 3. Döngü var: henüz sıraya alınamayan paketlerin her birinin
    #    (sıraya alınmamış) en az bir ön şartı vardır.
    kalan: set[str] = tum_paketler - set(sirali)

    # Ön şart kenarlarını izleyerek bir döngü bul.
    imlec = min(kalan)
    indice: dict[str, int] = {}
    yol: list[str] = []
    while imlec not in indice:
        indice[imlec] = len(yol)
        yol.append(imlec)
        once_kalan = once[imlec] & kalan
        imlec = min(once_kalan)

    dongu = yol[indice[imlec]:]
    en_kucuk = min(dongu)
    bas = dongu.index(en_kucuk)
    dongu = dongu[bas:] + dongu[:bas]

    raise DonguHatasi(dongu)
