from __future__ import annotations

from collections import defaultdict
from heapq import heappush, heappop
from typing import Dict, List


class DonguHatasi(ValueError):
    """Bagimlilik dagarinda dongu bulunmasi durumunda firlatilir.

    ``dongu`` ozelligi, donguyu olusturan paketlerin listesidir: her paket
    listede kendisinden sonraki pakete bagimlidir, sondaki paket ilkine;
    liste dongudeki alfabetik olarak en kucuk paketle baslar.
    """

    def __init__(self, dongu: List[str]) -> None:
        self.dongu = dongu
        super().__init__(f"DonguHatasi: {' -> '.join(dongu)} -> {dongu[0]}")


def _donguyu_bul(start: str, dagitarim: Dict[str, List[str]]) -> List[str]:
    """start'dan baslayip geri donen ilk donguyu dondurur."""

    baslangic_dugumu = min(dagitarim.keys())
    visited: set[str] = set()
    stack: List[str] = [start]
    parent: Dict[str, str] = {}
    in_stack: set[str] = {start}

    while stack:
        node = stack[-1]
        if node not in visited:
            visited.add(node)
        komsular = dagitarim.get(node, [])
        ileriye_gitti = False
        for komsu in komsular:
            if komsu == baslangic_dugumu:
                dongu = [komsu]
                cur = node
                while cur != komsu:
                    dongu.append(cur)
                    cur = parent[cur]
                dongu.reverse()
                return dongu
            if komsu not in visited and komsu not in in_stack:
                parent[komsu] = node
                stack.append(komsu)
                in_stack.add(komsu)
                ileriye_gitti = True
                break
        if not ileriye_gitti:
            stack.pop()
            in_stack.discard(node)

    return [start]


def kurulum_sirasi(deps: Dict[str, List[str]]) -> List[str]:
    """Paketleri topolojik sirada dondurur.

    ``deps[p]``, p'nin kurulmasindan once kurulmasi gereken paketleri verir.
    Ayni bagimlilik iki kez yazilabilir. Birden fazla paket kurulabilir
    oldugunda alfabetik en kucuk once gelir. Dongu varsa DonguHatasi firlatir.
    """

    paketler: set[str] = set(deps.keys())
    for bagimliliklar in deps.values():
        paketler.update(bagimliliklar)

    if not paketler:
        return []

    dagitarim: Dict[str, List[str]] = defaultdict(list)
    giris_derecesi: Dict[str, int] = {p: 0 for p in paketler}

    for paket, bagimliliklar in deps.items():
        for bagimlilik in set(bagimliliklar):
            dagitarim[bagimlilik].append(paket)
            giris_derecesi[paket] += 1

    for komsu_listesi in dagitarim.values():
        komsu_listesi.sort()

    kuyruk: List[str] = []
    for paket in paketler:
        if giris_derecesi[paket] == 0:
            heappush(kuyruk, paket)

    sirali: List[str] = []
    islenmis: set[str] = set()

    while kuyruk:
        paket = heappop(kuyruk)
        if paket in islenmis:
            continue
        islenmis.add(paket)
        sirali.append(paket)

        for komsu in dagitarim.get(paket, []):
            if komsu in islenmis:
                continue
            giris_derecesi[komsu] -= 1
            if giris_derecesi[komsu] == 0:
                heappush(kuyruk, komsu)

    if len(sirali) != len(paketler):
        islenmemis = paketler - islenmis
        dagitarim_kisalti: Dict[str, List[str]] = {}
        for dugum in islenmemis:
            dagitarim_kisalti[dugum] = [
                k for k in dagitarim.get(dugum, []) if k in islenmemis
            ]

        baslangic = min(islenmemis)
        dongu = _donguyu_bul(baslangic, dagitarim_kisalti)
        raise DonguHatasi(dongu)

    return sirali
