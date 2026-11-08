from __future__ import annotations
import heapq
from collections import defaultdict


class DonguHatasi(ValueError):
    """Bağımlılık grafiğinde döngü bulunduğunda fırlatılır."""
    def __init__(self, dongu: list[str]):
        super().__init__("Bağımlılık döngüsü bulundu: " + " -> ".join(dongu) + " -> " + dongu[0])
        self.dongu = dongu


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """
    Bağımlılık sözlüğünden topological sıralama döndürür.
    
    Args:
        deps: {paket: [bağımlılıklar]} sözlüğü. Bağımlılıklar tekrar edebilir.
    
    Returns:
        Kurulum sırası (her paket kendi bağımlılıklarından sonra gelir).
        Aynı anda kurulabilecek paketler alfabetik sırayla yerleştirilir.
    
    Raises:
        DonguHatasi: Grafikte döngü varsa, döngü alfabetik en küçük paketle başlar.
    """
    # Tüm düğümleri topla (anahtarlar + bağımlılıklar)
    tum_dugumler: set[str] = set(deps.keys())
    for bagimlilar in deps.values():
        tum_dugumler.update(bagimlilar)
    
    # Komşuluk listesi (reverse: bagimli -> paket) ve giriş dereceleri
    komsular: dict[str, list[str]] = defaultdict(list)
    giris_derecesi: dict[str, int] = {dugum: 0 for dugum in tum_dugumler}
    
    # Kenarları ekle (tekrar eden bağımlılıkları tekilleştir)
    for paket, bagimlilar in deps.items():
        for bagimli in set(bagimlilar):
            komsular[bagimli].append(paket)
            giris_derecesi[paket] += 1
    
    # Komşuları alfabetik sırala (deterministik işlem için)
    for k in komsular:
        komsular[k].sort()
    
    # Giriş derecesi 0 olanları min-heap'e ekle
    heap: list[str] = [dugum for dugum, d in giris_derecesi.items() if d == 0]
    heapq.heapify(heap)
    
    sonuc: list[str] = []
    
    while heap:
        dugum = heapq.heappop(heap)
        sonuc.append(dugum)
        
        for komsu in komsular[dugum]:
            giris_derecesi[komsu] -= 1
            if giris_derecesi[komsu] == 0:
                heapq.heappush(heap, komsu)
    
    # Döngü kontrolü
    if len(sonuc) != len(tum_dugumler):
        kalan = {d for d in tum_dugumler if d not in sonuc}
        # Bağımlılık yönünde graf oluştur (paket -> bağımlılıklar)
        bagimlilik_grafi: dict[str, list[str]] = defaultdict(list)
        for paket, bagimlilar in deps.items():
            for bagimli in set(bagimlilar):
                if bagimli in kalan and paket in kalan:
                    bagimlilik_grafi[paket].append(bagimli)
        for k in bagimlilik_grafi:
            bagimlilik_grafi[k].sort()
        dongu = _dongu_bul(kalan, bagimlilik_grafi)
        raise DonguHatasi(dongu)
    
    return sonuc


def _dongu_bul(dugumler: set[str], komsular: dict[str, list[str]]) -> list[str]:
    """Verilen alt grafikte bir döngü bulur, alfabetik en küçüğüyle başlatır.
    komsular: u -> [v] şeklinde, u v'ye bağımlı (u depends on v)."""
    renk: dict[str, int] = {}
    ebeveyn: dict[str, str] = {}
    dongu_yolu: list[str] = []
    
    def dfs(u: str) -> bool:
        nonlocal dongu_yolu
        renk[u] = 1
        for v in komsular.get(u, []):
            if v not in dugumler:
                continue
            if renk.get(v, 0) == 0:
                ebeveyn[v] = u
                if dfs(v):
                    return True
            elif renk.get(v) == 1:
                # Döngü bulundu: u -> ... -> v -> u
                # v'yi başlangıç olarak al, u'dan v'ye ebeveyn zinciriyle git
                dongu_yolu = [v]
                cur = u
                while cur != v:
                    dongu_yolu.append(cur)
                    cur = ebeveyn[cur]
                dongu_yolu.reverse()  # v'den başla
                return True
        renk[u] = 2
        return False
    
    for dugum in sorted(dugumler):
        if renk.get(dugum, 0) == 0:
            ebeveyn[dugum] = ""
            if dfs(dugum):
                break
    
    if dongu_yolu:
        min_idx = min(range(len(dongu_yolu)), key=lambda i: dongu_yolu[i])
        dongu_yolu = dongu_yolu[min_idx:] + dongu_yolu[:min_idx]
    
    return dongu_yolu
